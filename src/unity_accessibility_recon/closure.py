from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

from .contracts import ValidationIssue, validate_foundation_bundle, validate_instance

Verdict = Literal["PROCEED", "PROCEED WITH TODOs", "DO NOT PROCEED"]


@dataclass(frozen=True)
class ReadinessReport:
    verdict: Verdict
    build_fingerprint_id: str
    slice_id: str
    reasons: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "buildFingerprintId": self.build_fingerprint_id,
            "reasons": list(self.reasons),
            "sliceId": self.slice_id,
            "verdict": self.verdict,
        }


def extraction_verdict(coverage: dict[str, Any]) -> str:
    first_slice_families = set(coverage["firstSliceFamilies"])
    if any(
        family["familyId"] in first_slice_families
        and (family["blockingGaps"] or family["failed"] > 0 or family["unsupported"] > 0)
        for family in coverage["families"]
    ):
        return "BLOCKED"
    replay = coverage["replay"]
    if replay["performed"] is not True or replay["equivalent"] is not True:
        return "DUMP-PARTIAL"
    if any(
        family["failed"] > 0 or family["unsupported"] > 0
        for family in coverage["families"]
    ):
        return "DUMP-PARTIAL"
    return "DUMP-READY"


def assess_first_slice(
    build: dict[str, Any],
    source: dict[str, Any],
    coverage: dict[str, Any],
    readiness: dict[str, Any],
) -> ReadinessReport:
    fingerprint = str(build.get("fingerprintId", "unknown"))
    slice_id = str(readiness.get("sliceId", "unknown"))
    validation_issues: list[ValidationIssue] = [
        *validate_foundation_bundle(build, source, coverage),
        *validate_instance(readiness, "first-slice-readiness.schema.json"),
    ]
    if validation_issues:
        return ReadinessReport(
            "DO NOT PROCEED",
            fingerprint,
            slice_id,
            tuple(f"{issue.code}: {issue.message}" for issue in validation_issues),
        )

    blockers: list[str] = []
    todos: list[str] = []

    if readiness["buildFingerprintId"] != fingerprint:
        blockers.append(
            "MIXED_BUILD: readiness identifies "
            f"{readiness['buildFingerprintId']!r}, expected {fingerprint!r}"
        )

    if source["preservation"]["preDigest"] != source["preservation"]["postDigest"]:
        blockers.append("SOURCE_CHANGED: original-source preservation digests differ")

    expected_extraction = extraction_verdict(coverage)
    declared_extraction = readiness["artifactStatus"]["extractionCoverage"]
    if declared_extraction != expected_extraction:
        blockers.append(
            "EXTRACTION_VERDICT_MISMATCH: "
            f"readiness declares {declared_extraction}, evidence computes {expected_extraction}"
        )
    if expected_extraction == "BLOCKED":
        blockers.append("FIRST_SLICE_EXTRACTION_BLOCKER: extraction coverage marks a blocker")
    elif expected_extraction == "DUMP-PARTIAL":
        todos.append("DUMP_PARTIAL: failed or unsupported extraction remains bounded by gaps")

    required_status = {
        "authorization": "CLOSED",
        "buildFingerprint": "VALID",
        "sourceManifest": "VALID",
        "staticUiLedger": "WHOLE-GAME-MAPPED",
        "surfaceLifecycleMatrix": "WHOLE-GAME-MAPPED",
    }
    for key, expected in required_status.items():
        actual = readiness["artifactStatus"][key]
        if actual != expected:
            blockers.append(f"ARTIFACT_BLOCKED: {key} is {actual}, expected {expected}")

    for key, value in sorted(readiness["runtimePlan"].items()):
        if value is not True:
            blockers.append(f"RUNTIME_PLAN_OPEN: {key} is not defined/testable")

    gap_ids: set[str] = set()
    for gap in sorted(readiness["gaps"], key=lambda item: item["gapId"]):
        gap_id = gap["gapId"]
        if gap_id in gap_ids:
            blockers.append(f"DUPLICATE_GAP: {gap_id}")
            continue
        gap_ids.add(gap_id)
        if gap["blocking"] and gap["appliesToSlice"]:
            blockers.append(f"FIRST_SLICE_GAP: {gap_id}")
        else:
            todos.append(f"GUARDED_GAP: {gap_id}")

    extraction_gap_ids = {
        gap_id
        for family in coverage["families"]
        for gap_id in family["blockingGaps"]
    }
    for missing_gap in sorted(extraction_gap_ids - gap_ids):
        blockers.append(f"UNTRACKED_EXTRACTION_GAP: {missing_gap}")
    if expected_extraction == "DUMP-PARTIAL" and not gap_ids:
        blockers.append("UNGUARDED_PARTIAL_DUMP: DUMP-PARTIAL requires at least one gap record")

    qa_verdict = readiness["qaVerdict"]
    if qa_verdict == "DO NOT PROCEED":
        blockers.append("QA_BLOCKED: Code QA verdict is DO NOT PROCEED")
    elif qa_verdict == "PROCEED WITH TODOs":
        todos.append("QA_TODOS: Code QA carries guarded findings")

    if blockers:
        computed: Verdict = "DO NOT PROCEED"
        reasons = tuple(blockers + todos)
    elif todos:
        computed = "PROCEED WITH TODOs"
        reasons = tuple(todos)
    else:
        computed = "PROCEED"
        reasons = ("ALL_ENTRY_GATES_CLOSED",)

    claimed = readiness["claimedVerdict"]
    if claimed != computed:
        return ReadinessReport(
            "DO NOT PROCEED",
            fingerprint,
            slice_id,
            (
                f"CLAIMED_VERDICT_MISMATCH: record claims {claimed}, evidence computes {computed}",
                *reasons,
            ),
        )

    return ReadinessReport(computed, fingerprint, slice_id, reasons)

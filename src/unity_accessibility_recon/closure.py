from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

from .contracts import ValidationIssue, validate_foundation_bundle, validate_instance

Decision = Literal[
    "READY FOR RUNTIME PROBE",
    "READY FOR SLICE IMPLEMENTATION",
    "BLOCKED FOR THIS SLICE",
]

_RUNTIME_GRADES = frozenset(
    {
        "RUNTIME-OBSERVED",
        "PHYSICAL-INPUT-PROVEN",
        "POSTCONDITION-PROVEN",
        "SPEECH-DISPATCH-PROVEN",
        "NVDA-MANUAL-CONFIRMED",
    }
)
_OFFLINE_GRADES = frozenset(
    {
        "SOURCE-IDENTIFIED",
        "STATIC-CONFIRMED",
    }
)
_LIMITS = (
    "VALIDATOR_DOES_NOT_PROVE_GAME_BEHAVIOR",
    "DECISION_APPLIES_ONLY_TO_NAMED_SLICE",
    "SCREEN_READER_AND_KEYBOARD_ACCEPTANCE_REQUIRES_USER",
)


@dataclass(frozen=True)
class ReadinessReport:
    decision: Decision
    consistency_check: Literal["PASS", "FAIL"]
    validator_scope: str
    build_fingerprint_id: str
    slice_id: str
    player_goal: str
    in_scope_surface_ids: tuple[str, ...]
    offline_findings: tuple[str, ...]
    runtime_findings: tuple[str, ...]
    unknowns: tuple[str, ...]
    next_test: str
    reasons: tuple[str, ...]
    limits: tuple[str, ...] = _LIMITS

    def as_dict(self) -> dict[str, Any]:
        return {
            "buildFingerprintId": self.build_fingerprint_id,
            "consistencyCheck": self.consistency_check,
            "decision": self.decision,
            "inScopeSurfaceIds": list(self.in_scope_surface_ids),
            "limits": list(self.limits),
            "nextTest": self.next_test,
            "offlineFindings": list(self.offline_findings),
            "playerGoal": self.player_goal,
            "reasons": list(self.reasons),
            "runtimeFindings": list(self.runtime_findings),
            "sliceId": self.slice_id,
            "unknowns": list(self.unknowns),
            "validatorScope": self.validator_scope,
        }


def extraction_verdict(coverage: dict[str, Any]) -> str:
    """Summarize the whole declared extraction scope for foundation diagnostics."""

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
    if any(family["failed"] > 0 or family["unsupported"] > 0 for family in coverage["families"]):
        return "DUMP-PARTIAL"
    return "DUMP-READY"


def slice_extraction_status(coverage: dict[str, Any]) -> str:
    """Compute only what the named slice needs; unrelated families do not block it."""

    first_slice_families = set(coverage["firstSliceFamilies"])
    selected = [family for family in coverage["families"] if family["familyId"] in first_slice_families]
    if any(family["blockingGaps"] or family["failed"] > 0 or family["unsupported"] > 0 for family in selected):
        return "BLOCKED"
    replay = coverage["replay"]
    if replay["performed"] is not True or replay["equivalent"] is not True:
        return "SLICE-PARTIAL"
    return "SLICE-READY"


def _report_view(readiness: dict[str, Any]) -> dict[str, Any]:
    raw_scope = readiness.get("scope")
    scope: dict[str, Any] = raw_scope if isinstance(raw_scope, dict) else {}
    raw_claims = readiness.get("claims")
    claims: list[dict[str, Any]] = (
        [item for item in raw_claims if isinstance(item, dict)]
        if isinstance(raw_claims, list)
        else []
    )
    raw_gaps = readiness.get("gaps")
    gaps: list[dict[str, Any]] = (
        [item for item in raw_gaps if isinstance(item, dict)]
        if isinstance(raw_gaps, list)
        else []
    )
    raw_probe = readiness.get("runtimeProbe")
    runtime_probe: dict[str, Any] = raw_probe if isinstance(raw_probe, dict) else {}
    sorted_claims = sorted(claims, key=lambda item: str(item.get("claimId", "")))
    offline = tuple(
        str(claim.get("statement", ""))
        for claim in sorted_claims
        if claim.get("appliesToSlice") is True and claim.get("claimGrade") in _OFFLINE_GRADES
    )
    runtime = tuple(
        str(claim.get("statement", ""))
        for claim in sorted_claims
        if claim.get("appliesToSlice") is True and claim.get("claimGrade") in _RUNTIME_GRADES
    )
    claim_unknowns = tuple(
        f"{claim.get('claimId', 'UNKNOWN')}: {claim.get('statement', 'Unknown claim')} "
        f"Challenge: {claim.get('challengeTest', 'No challenge test recorded')}"
        for claim in sorted_claims
        if claim.get("appliesToSlice") is True
        and claim.get("claimGrade") == "OPEN / DYNAMIC-UNVERIFIED"
    )
    gap_unknowns = tuple(
        f"{gap.get('gapId', 'UNKNOWN')}: {gap.get('guard', 'No guard recorded')}"
        for gap in sorted(gaps, key=lambda item: str(item.get("gapId", "")))
        if gap.get("appliesToSlice") is True
    )
    return {
        "validator_scope": str(readiness.get("validationScope", "INTERNAL-CONSISTENCY-ONLY")),
        "player_goal": str(scope.get("playerGoal", "unknown")),
        "in_scope": tuple(sorted(str(item) for item in scope.get("inScopeSurfaceIds", []))),
        "offline": offline,
        "runtime": runtime,
        "unknowns": claim_unknowns + gap_unknowns,
        "next_test": str(runtime_probe.get("method", "No runtime test recorded.")),
    }


def _blocked_report(
    fingerprint: str,
    slice_id: str,
    readiness: dict[str, Any],
    reasons: tuple[str, ...],
    *,
    consistency_check: Literal["PASS", "FAIL"] = "FAIL",
) -> ReadinessReport:
    view = _report_view(readiness)
    return ReadinessReport(
        "BLOCKED FOR THIS SLICE",
        consistency_check,
        view["validator_scope"],
        fingerprint,
        slice_id,
        view["player_goal"],
        view["in_scope"],
        view["offline"],
        view["runtime"],
        view["unknowns"],
        view["next_test"],
        reasons,
    )


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
        return _blocked_report(
            fingerprint,
            slice_id,
            readiness,
            tuple(f"{issue.code}: {issue.message}" for issue in validation_issues),
        )

    blockers: list[str] = []
    todos: list[str] = []

    if readiness["validationScope"] != "INTERNAL-CONSISTENCY-ONLY":
        blockers.append("VALIDATOR_SCOPE_MISMATCH")
    if readiness["buildFingerprintId"] != fingerprint:
        blockers.append(
            "MIXED_BUILD: readiness identifies "
            f"{readiness['buildFingerprintId']!r}, expected {fingerprint!r}"
        )
    if source["preservation"]["preDigest"] != source["preservation"]["postDigest"]:
        blockers.append("SOURCE_CHANGED: original-source preservation digests differ")

    expected_extraction = slice_extraction_status(coverage)
    declared_extraction = readiness["artifactStatus"]["extractionCoverage"]
    if declared_extraction != expected_extraction:
        blockers.append(
            "SLICE_EXTRACTION_STATUS_MISMATCH: "
            f"readiness declares {declared_extraction}, evidence computes {expected_extraction}"
        )
    if expected_extraction == "BLOCKED":
        blockers.append("FIRST_SLICE_EXTRACTION_BLOCKER")
    elif expected_extraction == "SLICE-PARTIAL":
        todos.append("SLICE_EXTRACTION_PARTIAL")

    required_status = {
        "authorization": "CLOSED",
        "buildFingerprint": "VALID",
        "sourceManifest": "VALID",
        "staticUiLedger": "SLICE-MAPPED",
        "surfaceLifecycleMatrix": "SLICE-MAPPED",
    }
    for key, expected in required_status.items():
        actual = readiness["artifactStatus"][key]
        if actual != expected:
            blockers.append(f"ARTIFACT_BLOCKED: {key} is {actual}, expected {expected}")

    for key, value in sorted(readiness["runtimePlan"].items()):
        if value is not True:
            blockers.append(f"RUNTIME_PLAN_OPEN: {key} is not defined/testable")

    claim_ids: set[str] = set()
    for claim in sorted(readiness["claims"], key=lambda item: item["claimId"]):
        claim_id = claim["claimId"]
        if claim_id in claim_ids:
            blockers.append(f"DUPLICATE_CLAIM: {claim_id}")
        claim_ids.add(claim_id)
    if not any(claim["appliesToSlice"] for claim in readiness["claims"]):
        blockers.append("NO_SLICE_CLAIMS")

    gap_ids: set[str] = set()
    for gap in sorted(readiness["gaps"], key=lambda item: item["gapId"]):
        gap_id = gap["gapId"]
        if gap_id in gap_ids:
            blockers.append(f"DUPLICATE_GAP: {gap_id}")
            continue
        gap_ids.add(gap_id)
        if gap["blocking"] and gap["appliesToSlice"]:
            blockers.append(f"SLICE_GAP: {gap_id}")
        elif gap["appliesToSlice"]:
            todos.append(f"GUARDED_SLICE_GAP: {gap_id}")

    first_slice_families = set(coverage["firstSliceFamilies"])
    slice_extraction_gap_ids = {
        gap_id
        for family in coverage["families"]
        if family["familyId"] in first_slice_families
        for gap_id in family["blockingGaps"]
    }
    for missing_gap in sorted(slice_extraction_gap_ids - gap_ids):
        blockers.append(f"UNTRACKED_SLICE_EXTRACTION_GAP: {missing_gap}")

    code_qa = readiness["codeQaStatus"]
    if code_qa == "BLOCKED":
        blockers.append("CODE_QA_BLOCKED")
    elif code_qa == "PASS-WITH-TODOS":
        todos.append("CODE_QA_TODOS")

    probe_status = readiness["runtimeProbe"]["status"]
    claims_by_id = {claim["claimId"]: claim for claim in readiness["claims"]}
    challenged_claim_ids = readiness["runtimeProbe"]["challengedClaimIds"]
    for challenged_claim_id in challenged_claim_ids:
        challenged_claim = claims_by_id.get(challenged_claim_id)
        if challenged_claim is None:
            blockers.append(f"RUNTIME_PROBE_TARGET_MISSING: {challenged_claim_id}")
        elif challenged_claim["appliesToSlice"] is not True:
            blockers.append(f"RUNTIME_PROBE_TARGET_OUT_OF_SCOPE: {challenged_claim_id}")

    if probe_status == "FAILED":
        blockers.append("RUNTIME_PROBE_FAILED")
    elif probe_status == "NOT-RUN":
        todos.append("RUNTIME_PROBE_PENDING")
    else:
        if not any(
            claim["appliesToSlice"] and claim["claimGrade"] in _RUNTIME_GRADES
            for claim in readiness["claims"]
        ):
            blockers.append("RUNTIME_PROBE_CLAIM_MISSING")
        probe_evidence = set(readiness["runtimeProbe"]["evidenceRefs"])
        for challenged_claim_id in challenged_claim_ids:
            challenged_claim = claims_by_id.get(challenged_claim_id)
            if challenged_claim is None or challenged_claim["appliesToSlice"] is not True:
                continue
            if challenged_claim["claimGrade"] not in _RUNTIME_GRADES:
                blockers.append(
                    f"RUNTIME_PROBE_TARGET_NOT_RUNTIME_GRADE: {challenged_claim_id}"
                )
            elif probe_evidence.isdisjoint(challenged_claim["evidenceRefs"]):
                blockers.append(f"RUNTIME_PROBE_EVIDENCE_NOT_LINKED: {challenged_claim_id}")

    if blockers:
        computed: Decision = "BLOCKED FOR THIS SLICE"
        reasons = tuple(blockers + todos)
    elif probe_status == "NOT-RUN":
        computed = "READY FOR RUNTIME PROBE"
        reasons = tuple(todos)
    else:
        computed = "READY FOR SLICE IMPLEMENTATION"
        reasons = tuple(todos) or ("SLICE_EVIDENCE_AND_RUNTIME_PROBE_RECORDED",)

    claimed = readiness["claimedDecision"]
    if claimed != computed:
        return _blocked_report(
            fingerprint,
            slice_id,
            readiness,
            (
                f"CLAIMED_DECISION_MISMATCH: record claims {claimed}, evidence computes {computed}",
                *reasons,
            ),
        )

    view = _report_view(readiness)
    return ReadinessReport(
        computed,
        "PASS",
        view["validator_scope"],
        fingerprint,
        slice_id,
        view["player_goal"],
        view["in_scope"],
        view["offline"],
        view["runtime"],
        view["unknowns"],
        view["next_test"],
        reasons,
    )

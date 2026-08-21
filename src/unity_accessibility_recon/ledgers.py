from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

from .contracts import ValidationIssue, load_json, validate_instance
from .registry import load_contract_registry


_REGISTRY = load_contract_registry()

LIFECYCLE_COLUMNS = [
    "surfaceId",
    "buildFingerprintId",
    "family",
    "entryPredicate",
    "exitPredicate",
    "staticOwnerCandidates",
    "runtimeOwner",
    "stateOwner",
    "modalDepth",
    "requiredControls",
    "optionalControls",
    "initialFocus",
    "childTransitions",
    "parentRestore",
    "inputOwner",
    "interactionModel",
    "privacyClass",
    "conditionalDependency",
    "claimGrade",
    "disposition",
    "gapId",
]
COVERAGE_COLUMNS = [
    "surfaceId",
    "buildFingerprintId",
    *_REGISTRY.coverage_fields,
    "evidenceRefs",
    "exclusionOrGap",
]
GAP_COLUMNS = [
    "gapId",
    "buildFingerprintId",
    "surfaceId",
    "claimGrade",
    "userImpact",
    "currentMitigation",
    "nextEvidence",
    "owner",
    "blocking",
    "reopenTrigger",
    "status",
]
COVERAGE_GATES = list(_REGISTRY.coverage_fields)
CLAIM_GRADES = frozenset(_REGISTRY.claim_grades)
PRIVACY_CLASSES = frozenset(_REGISTRY.privacy_classes)


@dataclass(frozen=True)
class LedgerValidation:
    issues: tuple[ValidationIssue, ...]
    static_candidate_count: int
    surface_count: int
    gap_count: int
    gap_ids: tuple[str, ...]


def _read_csv(
    path: Path,
    expected_columns: list[str],
    ledger_name: str,
    *,
    require_rows: bool = True,
) -> tuple[list[dict[str, str]], list[ValidationIssue]]:
    issues: list[ValidationIssue] = []
    try:
        with path.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            columns = reader.fieldnames or []
            if columns != expected_columns:
                return [], [
                    ValidationIssue(
                        "CSV_HEADER",
                        f"{ledger_name}: expected {expected_columns!r}, got {columns!r}",
                    )
                ]
            rows = list(reader)
    except (OSError, UnicodeError, csv.Error) as exc:
        return [], [ValidationIssue("CSV_READ", f"{ledger_name}: {exc}")]
    if require_rows and not rows:
        issues.append(ValidationIssue("EMPTY_LEDGER", f"{ledger_name}: no data rows"))
    return rows, issues


def _required(row: dict[str, str], fields: tuple[str, ...], context: str) -> list[ValidationIssue]:
    return [
        ValidationIssue("MISSING_VALUE", f"{context}: {field} is empty")
        for field in fields
        if not row.get(field, "").strip()
    ]


def _parse_bool(value: str, context: str) -> tuple[bool | None, ValidationIssue | None]:
    normalized = value.strip().lower()
    if normalized == "true":
        return True, None
    if normalized == "false":
        return False, None
    return None, ValidationIssue("BOOLEAN", f"{context}: expected true/false, got {value!r}")


def validate_surface_ledgers(
    build_fingerprint_id: str,
    static_ui_path: Path,
    lifecycle_path: Path,
    coverage_path: Path,
    gaps_path: Path,
) -> LedgerValidation:
    try:
        static_ui = load_json(static_ui_path)
    except (OSError, UnicodeError, ValueError) as exc:
        return LedgerValidation(
            (ValidationIssue("STATIC_UI_READ", f"static-ui: {exc}"),),
            0,
            0,
            0,
            (),
        )
    static_issues = validate_instance(static_ui, "static-ui-ledger.schema.json")
    static_records = static_ui.get("records", [])
    static_candidate_count = len(static_records) if isinstance(static_records, list) else 0

    lifecycle, lifecycle_issues = _read_csv(lifecycle_path, LIFECYCLE_COLUMNS, "lifecycle")
    coverage, coverage_issues = _read_csv(coverage_path, COVERAGE_COLUMNS, "coverage")
    gaps, gap_issues = _read_csv(gaps_path, GAP_COLUMNS, "gaps", require_rows=False)
    issues = [*static_issues, *lifecycle_issues, *coverage_issues, *gap_issues]
    if issues:
        return LedgerValidation(
            tuple(issues),
            static_candidate_count,
            len(lifecycle),
            len(gaps),
            (),
        )

    static_gap_refs: set[str] = set()
    if static_ui["buildFingerprintId"] != build_fingerprint_id:
        issues.append(
            ValidationIssue(
                "MIXED_BUILD",
                "static-ui: "
                f"{static_ui['buildFingerprintId']!r}, expected {build_fingerprint_id!r}",
            )
        )
    candidate_ids: set[str] = set()
    for index, record in enumerate(static_records):
        context = f"static-ui record {index}"
        candidate_id = record["candidateId"]
        if candidate_id in candidate_ids:
            issues.append(ValidationIssue("DUPLICATE_STATIC_CANDIDATE", f"{context}: {candidate_id}"))
        candidate_ids.add(candidate_id)
        if record["gapId"]:
            static_gap_refs.add(record["gapId"])

    surface_ids: set[str] = set()
    lifecycle_gap_refs: set[str] = set()
    for index, row in enumerate(lifecycle, start=2):
        context = f"lifecycle row {index}"
        issues.extend(
            _required(
                row,
                (
                    "surfaceId",
                    "buildFingerprintId",
                    "family",
                    "entryPredicate",
                    "exitPredicate",
                    "staticOwnerCandidates",
                    "runtimeOwner",
                    "stateOwner",
                    "requiredControls",
                    "initialFocus",
                    "inputOwner",
                    "interactionModel",
                    "privacyClass",
                    "claimGrade",
                    "disposition",
                ),
                context,
            )
        )
        surface_id = row["surfaceId"].strip()
        if surface_id in surface_ids:
            issues.append(ValidationIssue("DUPLICATE_SURFACE", f"{context}: {surface_id}"))
        surface_ids.add(surface_id)
        if row["buildFingerprintId"] != build_fingerprint_id:
            issues.append(
                ValidationIssue(
                    "MIXED_BUILD",
                    f"{context}: {row['buildFingerprintId']!r}, expected {build_fingerprint_id!r}",
                )
            )
        if row["claimGrade"] not in CLAIM_GRADES:
            issues.append(
                ValidationIssue("CLAIM_GRADE", f"{context}: {row['claimGrade']!r}")
            )
        if row["privacyClass"] not in PRIVACY_CLASSES:
            issues.append(ValidationIssue("PRIVACY_CLASS", f"{context}: {row['privacyClass']!r}"))
        gap_id = row["gapId"].strip()
        if gap_id:
            lifecycle_gap_refs.add(gap_id)
        if row["disposition"] == "gap" and not gap_id:
            issues.append(ValidationIssue("UNLINKED_GAP", f"{context}: gap disposition lacks gapId"))

    gap_ids: set[str] = set()
    for index, row in enumerate(gaps, start=2):
        context = f"gaps row {index}"
        issues.extend(_required(row, tuple(GAP_COLUMNS), context))
        gap_id = row["gapId"].strip()
        if gap_id in gap_ids:
            issues.append(ValidationIssue("DUPLICATE_GAP", f"{context}: {gap_id}"))
        gap_ids.add(gap_id)
        if row["buildFingerprintId"] != build_fingerprint_id:
            issues.append(
                ValidationIssue(
                    "MIXED_BUILD",
                    f"{context}: {row['buildFingerprintId']!r}, expected {build_fingerprint_id!r}",
                )
            )
        if row["surfaceId"] != "GLOBAL" and row["surfaceId"] not in surface_ids:
            issues.append(
                ValidationIssue("UNKNOWN_GAP_SURFACE", f"{context}: {row['surfaceId']!r}")
            )
        if row["claimGrade"] not in CLAIM_GRADES:
            issues.append(
                ValidationIssue("CLAIM_GRADE", f"{context}: {row['claimGrade']!r}")
            )
        _, bool_issue = _parse_bool(row["blocking"], f"{context} blocking")
        if bool_issue:
            issues.append(bool_issue)

    coverage_ids: set[str] = set()
    coverage_gap_refs: set[str] = set()
    for index, row in enumerate(coverage, start=2):
        context = f"coverage row {index}"
        issues.extend(_required(row, ("surfaceId", "buildFingerprintId", "evidenceRefs"), context))
        surface_id = row["surfaceId"].strip()
        if surface_id in coverage_ids:
            issues.append(ValidationIssue("DUPLICATE_COVERAGE_SURFACE", f"{context}: {surface_id}"))
        coverage_ids.add(surface_id)
        if row["buildFingerprintId"] != build_fingerprint_id:
            issues.append(
                ValidationIssue(
                    "MIXED_BUILD",
                    f"{context}: {row['buildFingerprintId']!r}, expected {build_fingerprint_id!r}",
                )
            )

        gate_values: list[bool] = []
        for gate in COVERAGE_GATES:
            parsed, bool_issue = _parse_bool(row[gate], f"{context} {gate}")
            if bool_issue:
                issues.append(bool_issue)
            elif parsed is not None:
                gate_values.append(parsed)
        if len(gate_values) == len(COVERAGE_GATES):
            seen_false = False
            for gate, value in zip(COVERAGE_GATES, gate_values, strict=True):
                if not value:
                    seen_false = True
                elif seen_false:
                    issues.append(
                        ValidationIssue(
                            "NON_MONOTONIC_COVERAGE",
                            f"{context}: {gate} is true after an earlier false gate",
                        )
                    )
            if gate_values[0] is not True:
                issues.append(ValidationIssue("STATIC_NOT_MAPPED", f"{context}: staticMapped must be true"))

        reference = row["exclusionOrGap"].strip()
        if len(gate_values) == len(COVERAGE_GATES) and not gate_values[-1] and not reference:
            issues.append(
                ValidationIssue(
                    "UNEXPLAINED_OPEN_COVERAGE",
                    f"{context}: open coverage needs an exclusion reason or gap ID",
                )
            )
        if reference.startswith("GAP-"):
            coverage_gap_refs.add(reference)

    if coverage_ids != surface_ids:
        missing = sorted(surface_ids - coverage_ids)
        extra = sorted(coverage_ids - surface_ids)
        issues.append(
            ValidationIssue(
                "SURFACE_SET_MISMATCH",
                f"coverage missing={missing!r} extra={extra!r}",
            )
        )

    for missing_gap in sorted((static_gap_refs | lifecycle_gap_refs | coverage_gap_refs) - gap_ids):
        issues.append(ValidationIssue("MISSING_GAP_RECORD", missing_gap))

    return LedgerValidation(
        tuple(issues),
        static_candidate_count,
        len(surface_ids),
        len(gap_ids),
        tuple(sorted(gap_ids)),
    )

from __future__ import annotations

import csv
import json
from pathlib import Path

from unity_accessibility_recon.cli import main
from unity_accessibility_recon.ledgers import (
    COVERAGE_COLUMNS,
    GAP_COLUMNS,
    LIFECYCLE_COLUMNS,
    validate_surface_ledgers,
)


ROOT = Path(__file__).parents[1]
VALID = ROOT / "tests" / "fixtures" / "ledgers" / "valid"
BUILD_ID = "synthetic-100-unity2022-mono-windows-x64"


def _read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _write(path: Path, columns: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def _copy_valid(tmp_path: Path) -> tuple[Path, Path, Path, Path]:
    static_ui = tmp_path / "static-ui.json"
    static_ui.write_bytes((VALID / "static-ui-ledger.json").read_bytes())
    lifecycle = tmp_path / "lifecycle.csv"
    coverage = tmp_path / "coverage.csv"
    gaps = tmp_path / "gaps.csv"
    _write(lifecycle, LIFECYCLE_COLUMNS, _read(VALID / "surface-lifecycle-matrix.csv"))
    _write(coverage, COVERAGE_COLUMNS, _read(VALID / "static-to-runtime-coverage.csv"))
    _write(gaps, GAP_COLUMNS, _read(VALID / "gap-ledger.csv"))
    return static_ui, lifecycle, coverage, gaps


def test_valid_surface_ledgers_pass() -> None:
    report = validate_surface_ledgers(
        BUILD_ID,
        VALID / "static-ui-ledger.json",
        VALID / "surface-lifecycle-matrix.csv",
        VALID / "static-to-runtime-coverage.csv",
        VALID / "gap-ledger.csv",
    )
    assert report.issues == ()
    assert report.static_candidate_count == 2
    assert report.surface_count == 2
    assert report.gap_count == 3
    assert report.gap_ids == (
        "GAP-PARSER-BOUNDED",
        "GAP-RUNTIME-STARTUP",
        "GAP-RUNTIME-TITLE",
    )
    assert report.surface_ids == ("SURFACE-STARTUP", "SURFACE-TITLE")


def test_mixed_build_coverage_fails(tmp_path: Path) -> None:
    static_ui, lifecycle, coverage, gaps = _copy_valid(tmp_path)
    rows = _read(coverage)
    rows[0]["buildFingerprintId"] = "another-build"
    _write(coverage, COVERAGE_COLUMNS, rows)
    report = validate_surface_ledgers(BUILD_ID, static_ui, lifecycle, coverage, gaps)
    assert "MIXED_BUILD" in {issue.code for issue in report.issues}


def test_mixed_build_static_ui_fails(tmp_path: Path) -> None:
    static_ui, lifecycle, coverage, gaps = _copy_valid(tmp_path)
    payload = json.loads(static_ui.read_text(encoding="utf-8"))
    payload["buildFingerprintId"] = "another-build"
    static_ui.write_text(json.dumps(payload), encoding="utf-8")

    report = validate_surface_ledgers(BUILD_ID, static_ui, lifecycle, coverage, gaps)
    assert "MIXED_BUILD" in {issue.code for issue in report.issues}


def test_mixed_build_lifecycle_fails(tmp_path: Path) -> None:
    static_ui, lifecycle, coverage, gaps = _copy_valid(tmp_path)
    rows = _read(lifecycle)
    rows[0]["buildFingerprintId"] = "another-build"
    _write(lifecycle, LIFECYCLE_COLUMNS, rows)

    report = validate_surface_ledgers(BUILD_ID, static_ui, lifecycle, coverage, gaps)
    assert "MIXED_BUILD" in {issue.code for issue in report.issues}


def test_non_monotonic_coverage_fails(tmp_path: Path) -> None:
    static_ui, lifecycle, coverage, gaps = _copy_valid(tmp_path)
    rows = _read(coverage)
    rows[0]["semanticModeled"] = "true"
    _write(coverage, COVERAGE_COLUMNS, rows)
    report = validate_surface_ledgers(BUILD_ID, static_ui, lifecycle, coverage, gaps)
    assert "NON_MONOTONIC_COVERAGE" in {issue.code for issue in report.issues}


def test_missing_gap_record_fails(tmp_path: Path) -> None:
    static_ui, lifecycle, coverage, gaps = _copy_valid(tmp_path)
    _write(gaps, GAP_COLUMNS, _read(gaps)[:1])
    report = validate_surface_ledgers(BUILD_ID, static_ui, lifecycle, coverage, gaps)
    assert "MISSING_GAP_RECORD" in {issue.code for issue in report.issues}


def test_closed_coverage_can_have_empty_gap_ledger(tmp_path: Path) -> None:
    static_ui, lifecycle, coverage, gaps = _copy_valid(tmp_path)
    lifecycle_rows = _read(lifecycle)
    for row in lifecycle_rows:
        row["disposition"] = "mapped"
        row["gapId"] = ""
    _write(lifecycle, LIFECYCLE_COLUMNS, lifecycle_rows)

    coverage_rows = _read(coverage)
    for row in coverage_rows:
        for gate in COVERAGE_COLUMNS[2:10]:
            row[gate] = "true"
        row["exclusionOrGap"] = ""
    _write(coverage, COVERAGE_COLUMNS, coverage_rows)
    _write(gaps, GAP_COLUMNS, [])

    report = validate_surface_ledgers(BUILD_ID, static_ui, lifecycle, coverage, gaps)
    assert report.issues == ()
    assert report.gap_count == 0


def test_surface_set_mismatch_fails(tmp_path: Path) -> None:
    static_ui, lifecycle, coverage, gaps = _copy_valid(tmp_path)
    _write(coverage, COVERAGE_COLUMNS, _read(coverage)[:1])
    report = validate_surface_ledgers(BUILD_ID, static_ui, lifecycle, coverage, gaps)
    assert "SURFACE_SET_MISMATCH" in {issue.code for issue in report.issues}


def test_registry_local_privacy_class_is_accepted(tmp_path: Path) -> None:
    static_ui, lifecycle, coverage, gaps = _copy_valid(tmp_path)
    rows = _read(lifecycle)
    rows[0]["privacyClass"] = "local"
    _write(lifecycle, LIFECYCLE_COLUMNS, rows)

    report = validate_surface_ledgers(BUILD_ID, static_ui, lifecycle, coverage, gaps)
    assert report.issues == ()


def test_unknown_claim_grade_fails(tmp_path: Path) -> None:
    static_ui, lifecycle, coverage, gaps = _copy_valid(tmp_path)
    rows = _read(lifecycle)
    rows[0]["claimGrade"] = "STATIC-MAPPED"
    _write(lifecycle, LIFECYCLE_COLUMNS, rows)

    report = validate_surface_ledgers(BUILD_ID, static_ui, lifecycle, coverage, gaps)
    assert "CLAIM_GRADE" in {issue.code for issue in report.issues}


def test_cli_validates_build_bound_ledgers(capsys) -> None:
    result = main(
        [
            "validate-ledgers",
            "--build-id",
            BUILD_ID,
            "--static-ui",
            str(VALID / "static-ui-ledger.json"),
            "--lifecycle",
            str(VALID / "surface-lifecycle-matrix.csv"),
            "--runtime-coverage",
            str(VALID / "static-to-runtime-coverage.csv"),
            "--gaps",
            str(VALID / "gap-ledger.csv"),
        ]
    )

    assert result == 0
    assert capsys.readouterr().out == (
        "LEDGER_VALIDATION_PASS staticCandidates=2 surfaces=2 gaps=3\n"
    )

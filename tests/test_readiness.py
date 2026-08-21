from __future__ import annotations

from copy import deepcopy
from pathlib import Path

from unity_accessibility_recon.cli import main
from unity_accessibility_recon.closure import assess_first_slice, extraction_verdict
from unity_accessibility_recon.contracts import load_json, load_yaml, validate_file


ROOT = Path(__file__).parents[1]
FOUNDATION = ROOT / "tests" / "fixtures" / "foundation" / "valid"
READINESS = ROOT / "tests" / "fixtures" / "readiness"
BUILD = FOUNDATION / "build-fingerprint.json"
SOURCE = FOUNDATION / "source-manifest.json"
COVERAGE = FOUNDATION / "extraction-coverage.json"
PARTIAL_BUILD = READINESS / "partial-build-fingerprint.json"
PARTIAL_COVERAGE = READINESS / "partial-coverage.json"
PARTIAL_SOURCE = READINESS / "partial-source-manifest.json"
LEDGERS = ROOT / "tests" / "fixtures" / "ledgers"


def _ledger_args(fixture: str = "closed") -> list[str]:
    root = LEDGERS / fixture
    return [
        "--static-ui",
        str(root / "static-ui-ledger.json"),
        "--lifecycle",
        str(root / "surface-lifecycle-matrix.csv"),
        "--runtime-coverage",
        str(root / "static-to-runtime-coverage.csv"),
        "--gaps",
        str(root / "gap-ledger.csv"),
    ]


def _assess(
    coverage_path: Path,
    readiness_path: Path,
    source_path: Path = SOURCE,
    build_path: Path = BUILD,
):
    return assess_first_slice(
        load_json(build_path),
        load_json(source_path),
        load_json(coverage_path),
        load_yaml(readiness_path),
    )


def test_readiness_schema_accepts_all_verdict_fixtures() -> None:
    for name in ("proceed.yaml", "proceed-with-todos.yaml", "do-not-proceed.yaml"):
        assert validate_file(READINESS / name, "first-slice-readiness.schema.json") == []


def test_proceed_when_all_entry_gates_close() -> None:
    report = _assess(COVERAGE, READINESS / "proceed.yaml")
    assert report.verdict == "PROCEED"
    assert report.reasons == ("ALL_ENTRY_GATES_CLOSED",)


def test_bounded_partial_dump_proceeds_with_todos() -> None:
    coverage = load_json(PARTIAL_COVERAGE)
    assert extraction_verdict(coverage) == "DUMP-PARTIAL"
    report = _assess(
        PARTIAL_COVERAGE,
        READINESS / "proceed-with-todos.yaml",
        PARTIAL_SOURCE,
        PARTIAL_BUILD,
    )
    assert report.verdict == "PROCEED WITH TODOs"
    assert report.reasons == (
        "DUMP_PARTIAL: failed or unsupported extraction remains bounded by gaps",
        "GUARDED_GAP: GAP-PARSER-BOUNDED",
        "GUARDED_GAP: GAP-RUNTIME-STARTUP",
        "GUARDED_GAP: GAP-RUNTIME-TITLE",
        "QA_TODOS: Code QA carries guarded findings",
    )


def test_first_slice_gap_blocks_progress() -> None:
    report = _assess(
        PARTIAL_COVERAGE,
        READINESS / "do-not-proceed.yaml",
        PARTIAL_SOURCE,
        PARTIAL_BUILD,
    )
    assert report.verdict == "DO NOT PROCEED"
    assert "FIRST_SLICE_GAP: GAP-PARSER-BOUNDED" in report.reasons
    assert "QA_BLOCKED: Code QA verdict is DO NOT PROCEED" in report.reasons


def test_failed_first_slice_family_blocks_without_manual_gap_flag() -> None:
    coverage = deepcopy(load_json(COVERAGE))
    managed = coverage["families"][0]
    managed["discovered"] += 1
    managed["failed"] = 1
    assert managed["blockingGaps"] == []
    assert extraction_verdict(coverage) == "BLOCKED"


def test_partial_dump_without_gap_record_fails_closed() -> None:
    readiness = deepcopy(load_yaml(READINESS / "proceed-with-todos.yaml"))
    readiness["gaps"] = []
    readiness["claimedVerdict"] = "DO NOT PROCEED"
    report = assess_first_slice(
        load_json(PARTIAL_BUILD),
        load_json(PARTIAL_SOURCE),
        load_json(PARTIAL_COVERAGE),
        readiness,
    )
    assert report.verdict == "DO NOT PROCEED"
    assert "UNGUARDED_PARTIAL_DUMP: DUMP-PARTIAL requires at least one gap record" in report.reasons


def test_gap_reason_order_is_canonical() -> None:
    readiness = deepcopy(load_yaml(READINESS / "proceed-with-todos.yaml"))
    base_gap = readiness["gaps"][0]
    later_gap = deepcopy(base_gap)
    later_gap["gapId"] = "GAP-Z-LATER"
    earlier_gap = deepcopy(base_gap)
    earlier_gap["gapId"] = "GAP-A-EARLIER"
    readiness["gaps"] = [later_gap, earlier_gap]
    report = assess_first_slice(
        load_json(PARTIAL_BUILD),
        load_json(PARTIAL_SOURCE),
        load_json(PARTIAL_COVERAGE),
        readiness,
    )
    guarded = [reason for reason in report.reasons if reason.startswith("GUARDED_GAP")]
    assert guarded == ["GUARDED_GAP: GAP-A-EARLIER", "GUARDED_GAP: GAP-Z-LATER"]


def test_claimed_verdict_mismatch_fails_closed() -> None:
    readiness = deepcopy(load_yaml(READINESS / "proceed.yaml"))
    readiness["claimedVerdict"] = "PROCEED WITH TODOs"
    report = assess_first_slice(
        load_json(BUILD),
        load_json(SOURCE),
        load_json(COVERAGE),
        readiness,
    )
    assert report.verdict == "DO NOT PROCEED"
    assert report.reasons[0].startswith("CLAIMED_VERDICT_MISMATCH")


def test_cli_checks_parity(capsys) -> None:
    result = main(["check-parity", "--root", str(ROOT)])
    captured = capsys.readouterr()
    assert result == 0
    assert captured.out == "VALIDATION_PASS\n"


def test_cli_rejects_gap_set_mismatch(capsys) -> None:
    result = main(
        [
            "assess-readiness",
            "--build",
            str(BUILD),
            "--source",
            str(SOURCE),
            "--coverage",
            str(COVERAGE),
            "--readiness",
            str(READINESS / "proceed.yaml"),
            *_ledger_args("valid"),
        ]
    )
    captured = capsys.readouterr()
    assert result == 1
    assert "GAP_SET_MISMATCH" in captured.out


def test_cli_emits_deterministic_readiness_json(capsys) -> None:
    args = [
        "assess-readiness",
        "--build",
        str(BUILD),
        "--source",
        str(SOURCE),
        "--coverage",
        str(COVERAGE),
        "--readiness",
        str(READINESS / "proceed.yaml"),
        "--json",
        *_ledger_args(),
    ]
    first = main(args)
    output_one = capsys.readouterr().out
    second = main(args)
    output_two = capsys.readouterr().out
    assert first == second == 0
    assert output_one == output_two
    assert '"verdict": "PROCEED"' in output_one


def test_cli_returns_nonzero_for_blocking_readiness(capsys) -> None:
    result = main(
        [
            "assess-readiness",
            "--build",
            str(PARTIAL_BUILD),
            "--source",
            str(PARTIAL_SOURCE),
            "--coverage",
            str(PARTIAL_COVERAGE),
            "--readiness",
            str(READINESS / "do-not-proceed.yaml"),
            *_ledger_args("valid"),
        ]
    )
    captured = capsys.readouterr()
    assert result == 1
    assert captured.out.startswith("READINESS_VERDICT DO NOT PROCEED\n")

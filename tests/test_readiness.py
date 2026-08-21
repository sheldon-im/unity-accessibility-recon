from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import yaml

from unity_accessibility_recon.cli import main
from unity_accessibility_recon.closure import assess_first_slice, extraction_verdict
from unity_accessibility_recon.contracts import load_json, load_yaml, validate_file, validate_instance


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


def test_readiness_schema_accepts_slice_scoped_fixtures() -> None:
    for name in ("ready-for-slice-implementation.yaml", "ready-for-runtime-probe.yaml", "blocked-for-this-slice.yaml"):
        assert validate_file(READINESS / name, "first-slice-readiness.schema.json") == []


def test_passed_runtime_probe_is_ready_only_for_named_slice() -> None:
    report = _assess(COVERAGE, READINESS / "ready-for-slice-implementation.yaml")

    assert report.decision == "READY FOR SLICE IMPLEMENTATION"
    assert report.validator_scope == "INTERNAL-CONSISTENCY-ONLY"
    assert report.player_goal == "Operate the startup and title menus."
    assert report.in_scope_surface_ids == ("SURFACE-STARTUP", "SURFACE-TITLE")
    assert "VALIDATOR_DOES_NOT_PROVE_GAME_BEHAVIOR" in report.limits
    assert report.runtime_findings == (
        "The startup screen owns input after boot.",
        "The title screen restores focus after closing a child screen.",
    )


def test_static_only_record_is_ready_for_runtime_probe_not_implementation() -> None:
    report = _assess(
        PARTIAL_COVERAGE,
        READINESS / "ready-for-runtime-probe.yaml",
        PARTIAL_SOURCE,
        PARTIAL_BUILD,
    )

    assert extraction_verdict(load_json(PARTIAL_COVERAGE)) == "DUMP-PARTIAL"
    assert report.decision == "READY FOR RUNTIME PROBE"
    assert report.offline_findings == (
        "Startup and title controls are candidates found in files.",
    )
    assert report.runtime_findings == ()
    assert report.next_test == "Launch the build and observe which object owns input on startup and title."
    assert "RUNTIME_PROBE_PENDING" in report.reasons


def test_unrelated_extraction_failure_does_not_block_slice() -> None:
    readiness = load_yaml(READINESS / "ready-for-runtime-probe.yaml")
    assert readiness["artifactStatus"]["extractionCoverage"] == "SLICE-READY"
    report = assess_first_slice(
        load_json(PARTIAL_BUILD),
        load_json(PARTIAL_SOURCE),
        load_json(PARTIAL_COVERAGE),
        readiness,
    )
    assert report.decision == "READY FOR RUNTIME PROBE"
    assert "FIRST_SLICE_EXTRACTION_BLOCKER" not in report.reasons


def test_blocking_slice_gap_blocks_only_this_slice() -> None:
    report = _assess(
        PARTIAL_COVERAGE,
        READINESS / "blocked-for-this-slice.yaml",
        PARTIAL_SOURCE,
        PARTIAL_BUILD,
    )
    assert report.decision == "BLOCKED FOR THIS SLICE"
    assert "SLICE_GAP: GAP-PARSER-BOUNDED" in report.reasons
    assert "CODE_QA_BLOCKED" in report.reasons


def test_failed_runtime_probe_blocks_slice() -> None:
    readiness = deepcopy(load_yaml(READINESS / "ready-for-runtime-probe.yaml"))
    readiness["runtimeProbe"].update(
        {
            "status": "FAILED",
            "resultSummary": "The observed owner did not match the offline candidate.",
            "evidenceRefs": ["runtime:probe-failed"],
        }
    )
    readiness["claimedDecision"] = "BLOCKED FOR THIS SLICE"
    report = assess_first_slice(
        load_json(PARTIAL_BUILD),
        load_json(PARTIAL_SOURCE),
        load_json(PARTIAL_COVERAGE),
        readiness,
    )
    assert report.decision == "BLOCKED FOR THIS SLICE"
    assert "RUNTIME_PROBE_FAILED" in report.reasons


def test_static_claim_requires_a_challenge_test() -> None:
    readiness = deepcopy(load_yaml(READINESS / "ready-for-runtime-probe.yaml"))
    readiness["claims"][0]["challengeTest"] = None
    issues = validate_instance(readiness, "first-slice-readiness.schema.json")
    assert issues
    assert issues[0].code == "SCHEMA"


def test_passed_probe_requires_runtime_grade_claim() -> None:
    readiness = deepcopy(load_yaml(READINESS / "ready-for-slice-implementation.yaml"))
    for claim in readiness["claims"]:
        claim["claimGrade"] = "STATIC-CONFIRMED"
        claim["challengeTest"] = "Observe the owner in the running game."
    readiness["claimedDecision"] = "BLOCKED FOR THIS SLICE"
    report = assess_first_slice(
        load_json(BUILD), load_json(SOURCE), load_json(COVERAGE), readiness
    )
    assert report.decision == "BLOCKED FOR THIS SLICE"
    assert "RUNTIME_PROBE_CLAIM_MISSING" in report.reasons


def test_passed_probe_must_target_runtime_grade_claim() -> None:
    readiness = deepcopy(load_yaml(READINESS / "ready-for-slice-implementation.yaml"))
    readiness["claims"].append(
        {
            "claimId": "CLAIM-UNVERIFIED-OWNER",
            "statement": "A second offline owner candidate may control the title screen.",
            "claimGrade": "STATIC-CONFIRMED",
            "evidenceRefs": ["static-ledger:second-owner"],
            "challengeTest": "Observe whether the second owner ever receives title input.",
            "appliesToSlice": True,
        }
    )
    readiness["runtimeProbe"]["challengedClaimIds"] = ["CLAIM-UNVERIFIED-OWNER"]
    report = assess_first_slice(
        load_json(BUILD), load_json(SOURCE), load_json(COVERAGE), readiness
    )
    assert report.decision == "BLOCKED FOR THIS SLICE"
    assert "RUNTIME_PROBE_TARGET_NOT_RUNTIME_GRADE: CLAIM-UNVERIFIED-OWNER" in report.reasons


def test_passed_probe_evidence_must_link_to_target_claim() -> None:
    readiness = deepcopy(load_yaml(READINESS / "ready-for-slice-implementation.yaml"))
    readiness["claims"][0]["evidenceRefs"] = ["synthetic-runtime:unrelated"]
    report = assess_first_slice(
        load_json(BUILD), load_json(SOURCE), load_json(COVERAGE), readiness
    )
    assert report.decision == "BLOCKED FOR THIS SLICE"
    assert "RUNTIME_PROBE_EVIDENCE_NOT_LINKED: CLAIM-STARTUP-OWNER" in report.reasons


def test_open_claim_is_visible_as_an_unknown() -> None:
    readiness = deepcopy(load_yaml(READINESS / "ready-for-runtime-probe.yaml"))
    readiness["claims"].append(
        {
            "claimId": "CLAIM-DYNAMIC-TITLE",
            "statement": "A dynamically generated title control may appear for some profiles.",
            "claimGrade": "OPEN / DYNAMIC-UNVERIFIED",
            "evidenceRefs": ["static-ledger:dynamic-title-hint"],
            "challengeTest": "Observe the title surface with the triggering profile condition.",
            "appliesToSlice": True,
        }
    )
    report = assess_first_slice(
        load_json(PARTIAL_BUILD),
        load_json(PARTIAL_SOURCE),
        load_json(PARTIAL_COVERAGE),
        readiness,
    )
    assert any(item.startswith("CLAIM-DYNAMIC-TITLE:") for item in report.unknowns)


def test_claimed_decision_mismatch_fails_closed() -> None:
    readiness = deepcopy(load_yaml(READINESS / "ready-for-slice-implementation.yaml"))
    readiness["claimedDecision"] = "READY FOR RUNTIME PROBE"
    report = assess_first_slice(
        load_json(BUILD), load_json(SOURCE), load_json(COVERAGE), readiness
    )
    assert report.decision == "BLOCKED FOR THIS SLICE"
    assert report.reasons[0].startswith("CLAIMED_DECISION_MISMATCH")


def test_cli_rejects_scope_surface_missing_from_ledger(tmp_path: Path, capsys) -> None:
    readiness = deepcopy(load_yaml(READINESS / "ready-for-slice-implementation.yaml"))
    readiness["scope"]["inScopeSurfaceIds"].append("SURFACE-MISSING")
    readiness_path = tmp_path / "readiness.yaml"
    readiness_path.write_text(yaml.safe_dump(readiness, sort_keys=False), encoding="utf-8")

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
            str(readiness_path),
            *_ledger_args(),
        ]
    )
    assert result == 1
    assert "SCOPE_SURFACE_NOT_IN_LEDGER" in capsys.readouterr().out


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
            str(READINESS / "ready-for-slice-implementation.yaml"),
            *_ledger_args("valid"),
        ]
    )
    assert result == 1
    assert "GAP_SET_MISMATCH" in capsys.readouterr().out


def test_cli_emits_deterministic_transparent_json(capsys) -> None:
    args = [
        "assess-readiness",
        "--build",
        str(BUILD),
        "--source",
        str(SOURCE),
        "--coverage",
        str(COVERAGE),
        "--readiness",
        str(READINESS / "ready-for-slice-implementation.yaml"),
        "--json",
        *_ledger_args(),
    ]
    first = main(args)
    output_one = capsys.readouterr().out
    second = main(args)
    output_two = capsys.readouterr().out
    assert first == second == 0
    assert output_one == output_two
    assert '"decision": "READY FOR SLICE IMPLEMENTATION"' in output_one
    assert '"validatorScope": "INTERNAL-CONSISTENCY-ONLY"' in output_one
    assert '"limits"' in output_one
    assert '"nextTest"' in output_one


def test_cli_plain_text_exposes_consistency_limit_and_next_test(capsys) -> None:
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
            str(READINESS / "ready-for-runtime-probe.yaml"),
            *_ledger_args("valid"),
        ]
    )
    output = capsys.readouterr().out
    assert result == 0
    assert output.startswith("CONSISTENCY_CHECK PASS\n")
    assert "DECISION READY FOR RUNTIME PROBE" in output
    assert "validatorScope=INTERNAL-CONSISTENCY-ONLY" in output
    assert "offlineFinding=" in output
    assert "nextTest=" in output
    assert "limit=VALIDATOR_DOES_NOT_PROVE_GAME_BEHAVIOR" in output


def test_cli_returns_nonzero_for_blocking_slice(capsys) -> None:
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
            str(READINESS / "blocked-for-this-slice.yaml"),
            *_ledger_args("valid"),
        ]
    )
    output = capsys.readouterr().out
    assert result == 1
    assert output.startswith("CONSISTENCY_CHECK PASS\n")
    assert "DECISION BLOCKED FOR THIS SLICE" in output

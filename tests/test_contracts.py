from __future__ import annotations

from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from unity_accessibility_recon.contracts import (
    canonical_json_sha256,
    contract_directory,
    load_json,
    load_schema,
    validate_file,
    validate_foundation_bundle,
)


FIXTURES = Path(__file__).parent / "fixtures" / "foundation"
VALID = FIXTURES / "valid"
INVALID = FIXTURES / "invalid"


@pytest.mark.parametrize(
    "schema_name",
    sorted(path.name for path in contract_directory().glob("*.schema.json")),
)
def test_contract_is_valid_draft_2020_12(schema_name: str) -> None:
    Draft202012Validator.check_schema(load_schema(schema_name))


def test_valid_foundation_bundle_passes() -> None:
    issues = validate_foundation_bundle(
        load_json(VALID / "build-fingerprint.json"),
        load_json(VALID / "source-manifest.json"),
        load_json(VALID / "extraction-coverage.json"),
    )
    assert issues == []


def test_static_ui_template_matches_contract() -> None:
    template = contract_directory().parent / "templates" / "static-ui-ledger.json"
    assert validate_file(template, "static-ui-ledger.schema.json") == []


def test_mixed_build_fails_closed() -> None:
    issues = validate_foundation_bundle(
        load_json(VALID / "build-fingerprint.json"),
        load_json(VALID / "source-manifest.json"),
        load_json(INVALID / "mixed-build-coverage.json"),
    )
    assert [issue.code for issue in issues] == ["MIXED_BUILD"]


def test_source_manifest_digest_mismatch_fails_closed() -> None:
    source = load_json(VALID / "source-manifest.json")
    source["families"][0]["recordCount"] += 1
    issues = validate_foundation_bundle(
        load_json(VALID / "build-fingerprint.json"),
        source,
        load_json(VALID / "extraction-coverage.json"),
    )
    assert "SOURCE_MANIFEST_DIGEST_MISMATCH" in {issue.code for issue in issues}


def test_count_mismatch_is_reported() -> None:
    coverage = load_json(VALID / "extraction-coverage.json")
    coverage["families"][0]["failed"] = 1
    issues = validate_foundation_bundle(
        load_json(VALID / "build-fingerprint.json"),
        load_json(VALID / "source-manifest.json"),
        coverage,
    )
    assert "COUNT_MISMATCH" in {issue.code for issue in issues}


def test_non_extracted_family_requires_reason() -> None:
    source = load_json(VALID / "source-manifest.json")
    source["families"][0]["disposition"] = "failed"
    source["families"][0]["reason"] = None
    issues = validate_file(VALID / "source-manifest.json", "source-manifest.schema.json")
    assert issues == []
    from unity_accessibility_recon.contracts import validate_instance

    invalid_issues = validate_instance(source, "source-manifest.schema.json")
    assert invalid_issues
    assert invalid_issues[0].code == "SCHEMA"


def test_partial_source_family_requires_reason_and_evidence() -> None:
    from unity_accessibility_recon.contracts import validate_instance

    source = load_json(VALID / "source-manifest.json")
    family = source["families"][0]
    family["disposition"] = "partial"
    family["reason"] = "One target failed while the remaining targets were extracted."
    assert validate_instance(source, "source-manifest.schema.json") == []

    family["reason"] = None
    assert validate_instance(source, "source-manifest.schema.json")
    family["reason"] = "One target failed."
    family["evidence"] = []
    assert validate_instance(source, "source-manifest.schema.json")


def test_source_summary_must_match_coverage_dispositions() -> None:
    build = load_json(VALID / "build-fingerprint.json")
    source = load_json(VALID / "source-manifest.json")
    coverage = load_json(VALID / "extraction-coverage.json")
    managed = coverage["families"][0]
    managed["discovered"] += 1
    managed["failed"] = 1

    issues = validate_foundation_bundle(build, source, coverage)
    assert "SOURCE_COVERAGE_DISPOSITION_MISMATCH" in {issue.code for issue in issues}


def test_partial_source_summary_accepts_mixed_coverage_and_checks_record_count() -> None:
    build = load_json(VALID / "build-fingerprint.json")
    source = load_json(VALID / "source-manifest.json")
    coverage = load_json(VALID / "extraction-coverage.json")
    source["families"][0]["disposition"] = "partial"
    source["families"][0]["reason"] = "One bounded target failed."
    managed = coverage["families"][0]
    managed["discovered"] += 1
    managed["failed"] = 1
    build["sourceManifestDigest"] = canonical_json_sha256(source)

    assert validate_foundation_bundle(build, source, coverage) == []

    source["families"][0]["recordCount"] -= 1
    build["sourceManifestDigest"] = canonical_json_sha256(source)
    issues = validate_foundation_bundle(build, source, coverage)
    assert "SOURCE_RECORD_COUNT_MISMATCH" in {issue.code for issue in issues}


def test_coverage_family_without_source_manifest_entry_fails() -> None:
    coverage = load_json(VALID / "extraction-coverage.json")
    extra = dict(coverage["families"][0])
    extra["familyId"] = "other"
    coverage["families"].append(extra)
    issues = validate_foundation_bundle(
        load_json(VALID / "build-fingerprint.json"),
        load_json(VALID / "source-manifest.json"),
        coverage,
    )
    assert "COVERAGE_WITHOUT_SOURCE" in {issue.code for issue in issues}


def test_unknown_first_slice_family_fails() -> None:
    coverage = load_json(VALID / "extraction-coverage.json")
    coverage["firstSliceFamilies"] = ["missing-family"]
    issues = validate_foundation_bundle(
        load_json(VALID / "build-fingerprint.json"),
        load_json(VALID / "source-manifest.json"),
        coverage,
    )
    assert "UNKNOWN_FIRST_SLICE_FAMILY" in {issue.code for issue in issues}

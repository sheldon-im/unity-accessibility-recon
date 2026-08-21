from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator

from .resources import resource_root


@dataclass(frozen=True)
class ValidationIssue:
    code: str
    message: str


def contract_directory() -> Path:
    return resource_root() / "shared" / "contracts"


def load_json(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"Expected a JSON object: {path}")
    return value


def load_yaml(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        value = yaml.safe_load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"Expected a YAML object: {path}")
    return value


def load_schema(name: str) -> dict[str, Any]:
    path = contract_directory() / name
    if not path.is_file():
        raise FileNotFoundError(f"Unknown contract: {name}")
    return load_json(path)


def canonical_json_sha256(value: dict[str, Any]) -> str:
    payload = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def validate_instance(instance: dict[str, Any], schema_name: str) -> list[ValidationIssue]:
    validator = Draft202012Validator(load_schema(schema_name))
    issues: list[ValidationIssue] = []
    for error in sorted(validator.iter_errors(instance), key=lambda item: list(item.absolute_path)):
        location = "/".join(str(part) for part in error.absolute_path) or "$"
        issues.append(ValidationIssue("SCHEMA", f"{location}: {error.message}"))
    return issues


def validate_file(path: str | Path, schema_name: str) -> list[ValidationIssue]:
    instance = load_yaml(path) if Path(path).suffix.lower() in {".yaml", ".yml"} else load_json(path)
    return validate_instance(instance, schema_name)


def validate_foundation_bundle(
    build: dict[str, Any],
    source: dict[str, Any],
    coverage: dict[str, Any],
) -> list[ValidationIssue]:
    issues = [
        *validate_instance(build, "build-fingerprint.schema.json"),
        *validate_instance(source, "source-manifest.schema.json"),
        *validate_instance(coverage, "extraction-coverage.schema.json"),
    ]
    if issues:
        return issues

    fingerprint = build["fingerprintId"]
    manifest_digest = canonical_json_sha256(source)
    if build["sourceManifestDigest"].lower() != manifest_digest:
        issues.append(
            ValidationIssue(
                "SOURCE_MANIFEST_DIGEST_MISMATCH",
                "build fingerprint sourceManifestDigest does not match the canonical source manifest",
            )
        )
    for artifact_name, artifact in (("source manifest", source), ("extraction coverage", coverage)):
        if artifact["buildFingerprintId"] != fingerprint:
            issues.append(
                ValidationIssue(
                    "MIXED_BUILD",
                    f"{artifact_name} identifies {artifact['buildFingerprintId']!r}, expected {fingerprint!r}",
                )
            )

    family_ids: set[str] = set()
    source_by_id: dict[str, dict[str, Any]] = {}
    for family in source["families"]:
        family_id = family["familyId"]
        if family_id in family_ids:
            issues.append(ValidationIssue("DUPLICATE_FAMILY", f"Duplicate source family: {family_id}"))
        family_ids.add(family_id)
        source_by_id[family_id] = family
        if family["applicable"] and family["disposition"] == "not-present":
            issues.append(
                ValidationIssue(
                    "APPLICABLE_NOT_PRESENT",
                    f"Applicable family {family_id!r} cannot use not-present without revising applicability",
                )
            )

    coverage_ids: set[str] = set()
    coverage_by_id: dict[str, dict[str, Any]] = {}
    for family in coverage["families"]:
        family_id = family["familyId"]
        if family_id in coverage_ids:
            issues.append(ValidationIssue("DUPLICATE_COVERAGE_FAMILY", f"Duplicate coverage family: {family_id}"))
        coverage_ids.add(family_id)
        coverage_by_id[family_id] = family
        reconciled = sum(
            family[key]
            for key in ("extracted", "excluded", "unsupported", "failed", "notPresent")
        )
        if reconciled != family["discovered"]:
            issues.append(
                ValidationIssue(
                    "COUNT_MISMATCH",
                    f"{family_id}: discovered={family['discovered']} but dispositions total={reconciled}",
                )
            )

    missing_coverage = sorted(family_ids - coverage_ids)
    if missing_coverage:
        issues.append(
            ValidationIssue(
                "MISSING_COVERAGE",
                "Source families without extraction coverage: " + ", ".join(missing_coverage),
            )
        )
    coverage_without_source = sorted(coverage_ids - family_ids)
    if coverage_without_source:
        issues.append(
            ValidationIssue(
                "COVERAGE_WITHOUT_SOURCE",
                "Extraction families absent from the source manifest: "
                + ", ".join(coverage_without_source),
            )
        )
    unknown_first_slice = sorted(set(coverage["firstSliceFamilies"]) - coverage_ids)
    if unknown_first_slice:
        issues.append(
            ValidationIssue(
                "UNKNOWN_FIRST_SLICE_FAMILY",
                "First-slice families absent from extraction coverage: "
                + ", ".join(unknown_first_slice),
            )
        )

    for family_id in sorted(family_ids & coverage_ids):
        source_family = source_by_id[family_id]
        coverage_family = coverage_by_id[family_id]
        disposition = source_family["disposition"]
        extracted = coverage_family["extracted"]
        excluded = coverage_family["excluded"]
        unsupported = coverage_family["unsupported"]
        failed = coverage_family["failed"]
        not_present = coverage_family["notPresent"]
        non_extracted = excluded + unsupported + failed

        disposition_matches = {
            "extracted": extracted > 0 and non_extracted == 0 and not_present == 0,
            "partial": extracted > 0 and non_extracted > 0 and not_present == 0,
            "excluded-with-reason": extracted == 0 and excluded > 0 and unsupported == 0 and failed == 0 and not_present == 0,
            "unsupported": extracted == 0 and excluded == 0 and unsupported > 0 and failed == 0 and not_present == 0,
            "failed": extracted == 0 and excluded == 0 and unsupported == 0 and failed > 0 and not_present == 0,
            "not-present": extracted == 0 and non_extracted == 0,
        }[disposition]
        if not disposition_matches:
            issues.append(
                ValidationIssue(
                    "SOURCE_COVERAGE_DISPOSITION_MISMATCH",
                    f"{family_id}: source disposition={disposition!r} contradicts "
                    f"extracted={extracted}, excluded={excluded}, unsupported={unsupported}, "
                    f"failed={failed}, notPresent={not_present}",
                )
            )

        expected_record_count = extracted if disposition in {"extracted", "partial"} else 0
        if source_family["recordCount"] != expected_record_count:
            issues.append(
                ValidationIssue(
                    "SOURCE_RECORD_COUNT_MISMATCH",
                    f"{family_id}: source recordCount={source_family['recordCount']} but "
                    f"coverage extracted={extracted} for disposition={disposition!r}",
                )
            )

    preservation = source["preservation"]
    if preservation["preDigest"] != preservation["postDigest"] and not preservation["changedPaths"]:
        issues.append(
            ValidationIssue(
                "UNEXPLAINED_SOURCE_CHANGE",
                "Source preservation digests differ but changedPaths is empty",
            )
        )

    replay = coverage["replay"]
    if replay["performed"] and replay["equivalent"] is not True:
        issues.append(ValidationIssue("REPLAY_MISMATCH", "Performed replay is not equivalent"))

    return issues

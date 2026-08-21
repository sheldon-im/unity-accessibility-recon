from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from .resources import resource_root


@dataclass(frozen=True)
class ContractRegistry:
    phases: tuple[str, ...]
    claim_grades: tuple[str, ...]
    coverage_gates: tuple[str, ...]
    coverage_fields: tuple[str, ...]
    privacy_classes: tuple[str, ...]
    verdicts: tuple[str, ...]


def _string_tuple(value: Any, field: str) -> tuple[str, ...]:
    if not isinstance(value, list) or not value or not all(isinstance(item, str) and item for item in value):
        raise ValueError(f"contract registry {field} must be a non-empty string list")
    result = tuple(value)
    if len(result) != len(set(result)):
        raise ValueError(f"contract registry {field} contains duplicates")
    return result


def _object_keys(value: Any, field: str, keys: tuple[str, ...]) -> tuple[tuple[str, ...], ...]:
    if not isinstance(value, list) or not value:
        raise ValueError(f"contract registry {field} must be a non-empty object list")
    columns: list[list[str]] = [[] for _ in keys]
    for item in value:
        if not isinstance(item, dict):
            raise ValueError(f"contract registry {field} entries must be objects")
        for index, key in enumerate(keys):
            entry = item.get(key)
            if not isinstance(entry, str) or not entry:
                raise ValueError(f"contract registry {field}.{key} must be a non-empty string")
            columns[index].append(entry)
    result = tuple(tuple(column) for column in columns)
    for key, column in zip(keys, result, strict=True):
        if len(column) != len(set(column)):
            raise ValueError(f"contract registry {field}.{key} contains duplicates")
    return result


def load_contract_registry(root: Path | None = None) -> ContractRegistry:
    base = (root or resource_root()).resolve()
    path = base / "shared" / "phase-ids.yaml"
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, yaml.YAMLError) as exc:
        raise ValueError(f"cannot read contract registry: {exc}") from exc
    if not isinstance(data, dict) or data.get("schemaVersion") != 1:
        raise ValueError("unsupported or malformed contract registry")

    (phases,) = _object_keys(data.get("phases"), "phases", ("id",))
    coverage_gates, coverage_fields = _object_keys(
        data.get("coverageGates"),
        "coverageGates",
        ("id", "field"),
    )
    return ContractRegistry(
        phases=phases,
        claim_grades=_string_tuple(data.get("claimGrades"), "claimGrades"),
        coverage_gates=coverage_gates,
        coverage_fields=coverage_fields,
        privacy_classes=_string_tuple(data.get("privacyClasses"), "privacyClasses"),
        verdicts=_string_tuple(data.get("verdicts"), "verdicts"),
    )


def _schema(root: Path, name: str) -> dict[str, Any]:
    path = root / "shared" / "contracts" / name
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read contract {name}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"contract {name} must be an object")
    return value


def registry_alignment_errors(root: Path, manifest: dict[str, Any]) -> list[tuple[str, str]]:
    """Return drift between the canonical registry and persistent consumers."""

    try:
        registry = load_contract_registry(root)
        skill = next(
            document for document in manifest["documents"] if document.get("documentId") == "skill-core"
        )
        ui_reference = next(
            document for document in manifest["documents"] if document.get("documentId") == "ref-ui"
        )
        readiness = _schema(root, "first-slice-readiness.schema.json")
        runtime = _schema(root, "runtime-surface-observation.schema.json")
        static_ui = _schema(root, "static-ui-ledger.schema.json")
    except (KeyError, StopIteration, TypeError, ValueError) as exc:
        return [("CONTRACT_REGISTRY", str(exc))]

    errors: list[tuple[str, str]] = []
    manifest_phases = tuple(
        item for item in skill.get("requiredIds", []) if isinstance(item, str) and item.startswith("G")
    )
    if manifest_phases != registry.phases:
        errors.append(
            (
                "PHASE_REGISTRY",
                f"manifest phases={manifest_phases!r}, registry phases={registry.phases!r}",
            )
        )

    skill_literals = set(skill.get("requiredLiterals", []))
    missing_claims = sorted(set(registry.claim_grades) - skill_literals)
    if missing_claims:
        errors.append(("CLAIM_GRADE_REGISTRY", f"skill-core literals missing {missing_claims!r}"))

    ui_literals = set(ui_reference.get("requiredLiterals", []))
    missing_gates = sorted(set(registry.coverage_gates) - ui_literals)
    if missing_gates:
        errors.append(("COVERAGE_GATE_REGISTRY", f"ref-ui literals missing {missing_gates!r}"))

    readiness_decisions = tuple(readiness["properties"]["claimedDecision"]["enum"])
    if readiness_decisions != registry.verdicts:
        errors.append(
            (
                "DECISION_REGISTRY",
                f"readiness claimedDecision={readiness_decisions!r}, registry={registry.verdicts!r}",
            )
        )

    readiness_claim_enum = tuple(
        readiness["properties"]["claims"]["items"]["properties"]["claimGrade"]["enum"]
    )
    readiness_gap_enum = tuple(
        readiness["properties"]["gaps"]["items"]["properties"]["claimGrade"]["enum"]
    )
    for field, readiness_enum in (
        ("claims", readiness_claim_enum),
        ("gaps", readiness_gap_enum),
    ):
        if readiness_enum != registry.claim_grades:
            errors.append(
                (
                    "CLAIM_GRADE_REGISTRY",
                    f"readiness {field} claimGrade={readiness_enum!r}, registry={registry.claim_grades!r}",
                )
            )

    runtime_gate_enum = tuple(runtime["properties"]["coverageGate"]["enum"])
    expected_runtime_gates = registry.coverage_gates[1:]
    if runtime_gate_enum != expected_runtime_gates:
        errors.append(
            (
                "COVERAGE_GATE_REGISTRY",
                f"runtime coverageGate={runtime_gate_enum!r}, expected={expected_runtime_gates!r}",
            )
        )

    runtime_privacy_enum = tuple(runtime["properties"]["privacyClass"]["enum"])
    if runtime_privacy_enum != registry.privacy_classes:
        errors.append(
            (
                "PRIVACY_CLASS_REGISTRY",
                f"runtime privacyClass={runtime_privacy_enum!r}, registry={registry.privacy_classes!r}",
            )
        )

    static_properties = static_ui["properties"]["records"]["items"]["properties"]
    static_claim_enum = tuple(static_properties["claimGrade"]["enum"])
    expected_static_claims = (
        registry.claim_grades[0],
        registry.claim_grades[1],
        registry.claim_grades[-1],
    )
    if static_claim_enum != expected_static_claims:
        errors.append(
            (
                "CLAIM_GRADE_REGISTRY",
                f"static UI claimGrade={static_claim_enum!r}, expected={expected_static_claims!r}",
            )
        )
    static_privacy_enum = tuple(static_properties["privacyClass"]["enum"])
    if static_privacy_enum != registry.privacy_classes:
        errors.append(
            (
                "PRIVACY_CLASS_REGISTRY",
                f"static UI privacyClass={static_privacy_enum!r}, registry={registry.privacy_classes!r}",
            )
        )
    return errors

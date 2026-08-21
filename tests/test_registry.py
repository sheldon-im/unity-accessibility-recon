from __future__ import annotations

from pathlib import Path

from unity_accessibility_recon.parity import load_parity_manifest
from unity_accessibility_recon.registry import (
    load_contract_registry,
    registry_alignment_errors,
)


ROOT = Path(__file__).parents[1]


def test_canonical_registry_exposes_distinct_taxonomies() -> None:
    registry = load_contract_registry(ROOT)

    assert registry.phases == (
        "G0-AUTHORIZATION",
        "G1-BASELINE",
        "G2-EXTRACTION",
        "G3-STATIC-DISCOVERY",
        "G4-LIFECYCLE-MAP",
        "G5-RUNTIME-COVERAGE",
        "G6-INPUT-POSTCONDITION",
        "G7-FIRST-SLICE-READINESS",
    )
    assert registry.claim_grades == (
        "SOURCE-IDENTIFIED",
        "STATIC-CONFIRMED",
        "RUNTIME-OBSERVED",
        "PHYSICAL-INPUT-PROVEN",
        "POSTCONDITION-PROVEN",
        "SPEECH-DISPATCH-PROVEN",
        "NVDA-MANUAL-CONFIRMED",
        "OPEN / DYNAMIC-UNVERIFIED",
    )
    assert registry.coverage_gates == (
        "STATIC-MAPPED",
        "RUNTIME-OWNER-OBSERVED",
        "ACTIVE-CONTROLS-INVENTORIED",
        "SEMANTIC-MODELED",
        "NATIVE-FOCUS-PROVEN",
        "NATIVE-ACTION-POSTCONDITION-PROVEN",
        "NVDA-MANUAL-CONFIRMED",
        "COVERAGE-CLOSED",
    )
    assert registry.privacy_classes == (
        "public",
        "local",
        "sensitive",
        "proprietary",
        "unknown",
    )
    assert registry.verdicts == (
        "READY FOR RUNTIME PROBE",
        "READY FOR SLICE IMPLEMENTATION",
        "BLOCKED FOR THIS SLICE",
    )


def test_registry_matches_manifest_and_persistent_schemas() -> None:
    manifest = load_parity_manifest(ROOT / "shared" / "bilingual-parity.yaml")
    assert registry_alignment_errors(ROOT, manifest) == []

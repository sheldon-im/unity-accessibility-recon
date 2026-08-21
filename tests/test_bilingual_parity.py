from __future__ import annotations

from pathlib import Path

import yaml

from unity_accessibility_recon.parity import (
    extract_id_headings,
    validate_bilingual_manifest,
    validate_document_pair,
)


ROOT = Path(__file__).parents[1]
MANIFEST = ROOT / "shared" / "bilingual-parity.yaml"


def test_bilingual_skill_and_references_match_manifest() -> None:
    assert validate_bilingual_manifest(ROOT, MANIFEST) == []


def test_missing_korean_id_fails_parity() -> None:
    en = "## UI-DISCOVERY — Discovery\n\n## UI-FAMILIES — Families\n"
    ko = "## UI-DISCOVERY — 조사\n"
    issues = validate_document_pair(
        en,
        ko,
        ["UI-DISCOVERY", "UI-FAMILIES"],
        "synthetic",
    )
    assert {issue.code for issue in issues} == {"KO_ID_ORDER", "HEADING_LEVEL_PARITY"}


def test_heading_extraction_preserves_level_and_order() -> None:
    text = "## G0-AUTHORIZATION — Gate\n### ART-AUTHORIZATION-RECORD — Artifact\n"
    assert extract_id_headings(text) == [
        ("G0-AUTHORIZATION", 2),
        ("ART-AUTHORIZATION-RECORD", 3),
    ]


def test_required_literal_must_exist_in_both_languages() -> None:
    issues = validate_document_pair(
        "## QA-REPORT — Report\nMUST\n",
        "## QA-REPORT — 보고\n",
        ["QA-REPORT"],
        "synthetic-literal",
        ["MUST"],
    )
    assert [issue.code for issue in issues] == ["KO_LITERAL"]


def test_phase_registry_drift_fails_parity(tmp_path: Path) -> None:
    manifest = yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))
    skill = next(item for item in manifest["documents"] if item["documentId"] == "skill-core")
    skill["requiredIds"] = [
        "G3-STATIC" if item == "G3-STATIC-DISCOVERY" else item
        for item in skill["requiredIds"]
    ]
    drifted = tmp_path / "bilingual-parity.yaml"
    drifted.write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")

    issues = validate_bilingual_manifest(ROOT, drifted)
    assert "PHASE_REGISTRY" in {issue.code for issue in issues}

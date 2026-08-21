from __future__ import annotations

from pathlib import Path

import yaml

from unity_accessibility_recon.cli import main
from unity_accessibility_recon.exporter import SKILLS, export_skills
from unity_accessibility_recon.resources import resource_root


def test_exported_skills_include_portable_contracts_and_templates(tmp_path: Path) -> None:
    targets = export_skills(tmp_path, ("en", "ko"))
    assert targets == (tmp_path / SKILLS["en"], tmp_path / SKILLS["ko"])

    source_root = resource_root()
    for language, target in zip(("en", "ko"), targets, strict=True):
        assert (target / "SKILL.md").read_bytes() == (
            source_root / "skills" / SKILLS[language] / "SKILL.md"
        ).read_bytes()
        contracts = sorted((target / "references" / "contracts").glob("*.schema.json"))
        templates = sorted((target / "templates").iterdir())
        assert len(contracts) == 7
        assert len(templates) == 8
        assert (target / "references" / "contracts" / "static-ui-ledger.schema.json").is_file()
        assert (target / "templates" / "static-ui-ledger.json").is_file()
        assert (target / "references" / "phase-ids.yaml").is_file()
        assert (target / "references" / "adapter-contract.yaml").is_file()
        assert (target / "LICENSE").read_bytes() == (source_root / "LICENSE").read_bytes()
        metadata = yaml.safe_load((target / "SKILL.md").read_text(encoding="utf-8").split("---\n", 2)[1])
        assert metadata["language"] == language


def test_export_refuses_existing_skill_directory(tmp_path: Path) -> None:
    export_skills(tmp_path, ("en",))
    try:
        export_skills(tmp_path, ("en",))
    except FileExistsError as exc:
        assert "refusing to replace" in str(exc)
    else:
        raise AssertionError("second export unexpectedly replaced an existing skill")


def test_cli_exports_one_language_and_reports_path(tmp_path: Path, capsys) -> None:
    result = main(["export-skills", "--destination", str(tmp_path), "--language", "ko"])
    output = capsys.readouterr().out
    assert result == 0
    assert output == f"EXPORTED_SKILL {tmp_path / SKILLS['ko']}\n"


def test_cli_export_existing_target_is_nonzero(tmp_path: Path, capsys) -> None:
    export_skills(tmp_path, ("ko",))
    result = main(["export-skills", "--destination", str(tmp_path), "--language", "ko"])
    output = capsys.readouterr().out
    assert result == 1
    assert output.startswith("EXPORT_FAIL: refusing to replace")

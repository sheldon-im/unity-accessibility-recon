from __future__ import annotations

import re
from pathlib import Path

import tomllib
import yaml

from unity_accessibility_recon import __version__


ROOT = Path(__file__).parents[1]
ENGLISH = ROOT / "README.md"
KOREAN = ROOT / "README.ko.md"


def _code_blocks(text: str) -> list[str]:
    return re.findall(r"```(?:bash)?\n(.*?)```", text, flags=re.DOTALL)


def test_english_readme_remains_package_default_and_links_korean() -> None:
    metadata = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    english = ENGLISH.read_text(encoding="utf-8")
    korean = KOREAN.read_text(encoding="utf-8")

    assert metadata["project"]["readme"] == "README.md"
    assert "[한국어](README.ko.md)" in english
    assert "[English](README.md)" in korean


def test_readme_commands_and_contract_literals_stay_in_sync() -> None:
    english = ENGLISH.read_text(encoding="utf-8")
    korean = KOREAN.read_text(encoding="utf-8")

    assert _code_blocks(english) == _code_blocks(korean)
    for literal in (
        "claimGrade",
        "coverageGate",
        "shared/phase-ids.yaml",
        "--static-ui",
        "THIRD-PARTY-NOTICES.md",
        "0.3.0",
        "INTERNAL-CONSISTENCY-ONLY",
        "READY FOR RUNTIME PROBE",
        "READY FOR SLICE IMPLEMENTATION",
        "BLOCKED FOR THIS SLICE",
    ):
        assert literal in english
        assert literal in korean

    english_sections = re.findall(r"^## ", english, flags=re.MULTILINE)
    korean_sections = re.findall(r"^## ", korean, flags=re.MULTILINE)
    assert len(english_sections) == len(korean_sections)


def test_release_version_and_license_metadata_align() -> None:
    metadata = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    project = metadata["project"]
    assert project["version"] == __version__ == "0.3.0"
    assert project["license"] == "MIT"
    assert project["license-files"] == ["LICENSE"]

    for language in ("en", "ko"):
        path = ROOT / "skills" / f"unity-accessibility-reconnaissance-{language}" / "SKILL.md"
        frontmatter = path.read_text(encoding="utf-8").split("---\n", 2)[1]
        assert yaml.safe_load(frontmatter)["version"] == __version__

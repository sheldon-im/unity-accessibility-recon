from __future__ import annotations

import shutil
from importlib.metadata import PackageNotFoundError, distribution
from pathlib import Path

from .resources import resource_root

SKILLS = {
    "en": "unity-accessibility-reconnaissance-en",
    "ko": "unity-accessibility-reconnaissance-ko",
}


def _project_license(root: Path) -> Path:
    source_license = root / "LICENSE"
    if source_license.is_file():
        return source_license
    try:
        package = distribution("unity-accessibility-reconnaissance")
    except PackageNotFoundError as exc:
        raise FileNotFoundError("project license is not available") from exc
    for file in package.files or ():
        normalized = str(file).replace("\\", "/")
        if normalized.endswith(".dist-info/licenses/LICENSE"):
            return Path(str(package.locate_file(file)))
    raise FileNotFoundError("installed distribution license is missing")


def export_skills(destination: Path, languages: tuple[str, ...]) -> tuple[Path, ...]:
    unknown = sorted(set(languages) - set(SKILLS))
    if unknown:
        raise ValueError(f"unsupported language codes: {unknown!r}")
    if not languages:
        raise ValueError("at least one language is required")

    root = resource_root()
    source_skills = root / "skills"
    shared = root / "shared"
    destination.mkdir(parents=True, exist_ok=True)
    targets = tuple(destination / SKILLS[language] for language in languages)
    existing = [str(target) for target in targets if target.exists()]
    if existing:
        raise FileExistsError("refusing to replace existing skill directories: " + ", ".join(existing))

    created: list[Path] = []
    try:
        for language, target in zip(languages, targets, strict=True):
            source = source_skills / SKILLS[language]
            if not source.is_dir():
                raise FileNotFoundError(f"bundled skill is missing: {source}")
            shutil.copytree(source, target)
            created.append(target)
            shutil.copytree(shared / "contracts", target / "references" / "contracts")
            shutil.copytree(shared / "templates", target / "templates")
            shutil.copy2(shared / "phase-ids.yaml", target / "references" / "phase-ids.yaml")
            shutil.copy2(shared / "adapter-contract.yaml", target / "references" / "adapter-contract.yaml")
            license_path = _project_license(root)
            shutil.copy2(license_path, target / "LICENSE")
    except Exception:
        for target in reversed(created):
            shutil.rmtree(target, ignore_errors=True)
        raise
    return targets

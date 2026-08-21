from __future__ import annotations

from importlib import resources
from pathlib import Path


def resource_root() -> Path:
    repository_root = Path(__file__).resolve().parents[2]
    if (repository_root / "skills").is_dir() and (repository_root / "shared").is_dir():
        return repository_root
    return Path(str(resources.files("unity_accessibility_recon")))

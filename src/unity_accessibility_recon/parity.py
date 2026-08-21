from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

from .contracts import ValidationIssue
from .registry import registry_alignment_errors

_ID_HEADING = re.compile(
    r"^(?P<marks>#{2,6})\s+(?P<id>(?:POLICY|G[0-7]|ART|CHECK|DUMP|UI|WORK|QA)-[A-Z0-9-]+)\s+—",
    re.MULTILINE,
)
_LINK = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


def extract_id_headings(text: str) -> list[tuple[str, int]]:
    return [(match.group("id"), len(match.group("marks"))) for match in _ID_HEADING.finditer(text)]


def extract_link_targets(text: str) -> list[str]:
    return _LINK.findall(text)


def _frontmatter(text: str) -> dict[str, Any] | None:
    if not text.startswith("---\n"):
        return None
    parts = text.split("---\n", 2)
    if len(parts) != 3:
        return None
    data = yaml.safe_load(parts[1])
    return data if isinstance(data, dict) else None


def validate_document_pair(
    en_text: str,
    ko_text: str,
    required_ids: list[str],
    document_id: str,
    required_literals: list[str] | None = None,
) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    required_literals = required_literals or []
    en_headings = extract_id_headings(en_text)
    ko_headings = extract_id_headings(ko_text)
    en_ids = [item[0] for item in en_headings]
    ko_ids = [item[0] for item in ko_headings]

    if en_ids != required_ids:
        issues.append(
            ValidationIssue(
                "EN_ID_ORDER",
                f"{document_id}: English IDs differ from the parity manifest: {en_ids!r}",
            )
        )
    if ko_ids != required_ids:
        issues.append(
            ValidationIssue(
                "KO_ID_ORDER",
                f"{document_id}: Korean IDs differ from the parity manifest: {ko_ids!r}",
            )
        )
    if en_headings != ko_headings:
        issues.append(
            ValidationIssue(
                "HEADING_LEVEL_PARITY",
                f"{document_id}: ID heading levels or order differ between languages",
            )
        )
    if len(en_ids) != len(set(en_ids)) or len(ko_ids) != len(set(ko_ids)):
        issues.append(ValidationIssue("DUPLICATE_ID", f"{document_id}: duplicate stable ID"))

    en_links = extract_link_targets(en_text)
    ko_links = extract_link_targets(ko_text)
    if en_links != ko_links:
        issues.append(
            ValidationIssue(
                "LINK_PARITY",
                f"{document_id}: Markdown link targets differ: en={en_links!r} ko={ko_links!r}",
            )
        )

    en_metadata = _frontmatter(en_text)
    ko_metadata = _frontmatter(ko_text)
    if (en_metadata is None) != (ko_metadata is None):
        issues.append(
            ValidationIssue("FRONTMATTER_PARITY", f"{document_id}: only one language has frontmatter")
        )
    elif en_metadata is not None and ko_metadata is not None:
        for key in ("version", "license"):
            if en_metadata.get(key) != ko_metadata.get(key):
                issues.append(
                    ValidationIssue(
                        "FRONTMATTER_PARITY",
                        f"{document_id}: frontmatter {key!r} differs",
                    )
                )
        if en_metadata.get("language") != "en" or ko_metadata.get("language") != "ko":
            issues.append(
                ValidationIssue("FRONTMATTER_LANGUAGE", f"{document_id}: expected en/ko language tags")
            )

    if en_text.count("```") % 2:
        issues.append(ValidationIssue("EN_FENCE", f"{document_id}: unbalanced English code fence"))
    if ko_text.count("```") % 2:
        issues.append(ValidationIssue("KO_FENCE", f"{document_id}: unbalanced Korean code fence"))
    for literal in required_literals:
        if literal not in en_text:
            issues.append(
                ValidationIssue("EN_LITERAL", f"{document_id}: English document lacks {literal!r}")
            )
        if literal not in ko_text:
            issues.append(
                ValidationIssue("KO_LITERAL", f"{document_id}: Korean document lacks {literal!r}")
            )
    return issues


def load_parity_manifest(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or data.get("schemaVersion") != 1:
        raise ValueError("unsupported or malformed bilingual parity manifest")
    documents = data.get("documents")
    if not isinstance(documents, list) or not documents:
        raise ValueError("bilingual parity manifest has no documents")
    return data


def validate_bilingual_manifest(root: Path, manifest_path: Path) -> list[ValidationIssue]:
    try:
        manifest = load_parity_manifest(manifest_path)
    except (OSError, UnicodeError, yaml.YAMLError, ValueError) as exc:
        return [ValidationIssue("PARITY_MANIFEST", str(exc))]

    issues: list[ValidationIssue] = []
    issues.extend(
        ValidationIssue(code, message)
        for code, message in registry_alignment_errors(root, manifest)
    )
    seen_document_ids: set[str] = set()
    for document in manifest["documents"]:
        if not isinstance(document, dict):
            issues.append(ValidationIssue("PARITY_DOCUMENT", "document entry must be an object"))
            continue
        document_id = document.get("documentId")
        if not isinstance(document_id, str) or not document_id:
            issues.append(ValidationIssue("PARITY_DOCUMENT", "documentId is required"))
            continue
        if document_id in seen_document_ids:
            issues.append(ValidationIssue("PARITY_DOCUMENT", f"duplicate documentId {document_id!r}"))
            continue
        seen_document_ids.add(document_id)

        en_path = root / str(document.get("enPath", ""))
        ko_path = root / str(document.get("koPath", ""))
        required_ids = document.get("requiredIds")
        required_literals = document.get("requiredLiterals", [])
        if not isinstance(required_ids, list) or not all(isinstance(item, str) for item in required_ids):
            issues.append(ValidationIssue("PARITY_DOCUMENT", f"{document_id}: requiredIds must be strings"))
            continue
        if not isinstance(required_literals, list) or not all(
            isinstance(item, str) for item in required_literals
        ):
            issues.append(
                ValidationIssue("PARITY_DOCUMENT", f"{document_id}: requiredLiterals must be strings")
            )
            continue
        missing = [str(path) for path in (en_path, ko_path) if not path.is_file()]
        if missing:
            issues.append(ValidationIssue("PARITY_PATH", f"{document_id}: missing {missing!r}"))
            continue
        for language, path in (("en", en_path), ("ko", ko_path)):
            text = path.read_text(encoding="utf-8")
            for target in extract_link_targets(text):
                path_part = target.split("#", 1)[0]
                if not path_part or "://" in path_part or path_part.startswith("mailto:"):
                    continue
                resolved = (path.parent / path_part).resolve()
                if not resolved.is_relative_to(root.resolve()) or not resolved.is_file():
                    issues.append(
                        ValidationIssue(
                            "LINK_TARGET",
                            f"{document_id}: {language} link target is missing or outside root: {target!r}",
                        )
                    )
        issues.extend(
            validate_document_pair(
                en_path.read_text(encoding="utf-8"),
                ko_path.read_text(encoding="utf-8"),
                required_ids,
                document_id,
                required_literals,
            )
        )
    return issues

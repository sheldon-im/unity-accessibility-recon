from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .closure import assess_first_slice
from .contracts import (
    ValidationIssue,
    load_json,
    load_yaml,
    validate_file,
    validate_foundation_bundle,
)
from .parity import validate_bilingual_manifest
from .ledgers import validate_surface_ledgers
from .exporter import export_skills
from .resources import resource_root


def _print_issues(issues: list[ValidationIssue]) -> int:
    if not issues:
        print("VALIDATION_PASS")
        return 0
    for issue in issues:
        print(f"{issue.code}: {issue.message}")
    print(f"VALIDATION_FAIL count={len(issues)}")
    return 1


def _validate(args: argparse.Namespace) -> int:
    return _print_issues(validate_file(args.artifact, args.schema))


def _validate_bundle(args: argparse.Namespace) -> int:
    issues = validate_foundation_bundle(
        load_json(args.build),
        load_json(args.source),
        load_json(args.coverage),
    )
    return _print_issues(issues)


def _check_parity(args: argparse.Namespace) -> int:
    root = (args.root or resource_root()).resolve()
    manifest = args.manifest if args.manifest.is_absolute() else root / args.manifest
    return _print_issues(validate_bilingual_manifest(root, manifest))


def _export_skills(args: argparse.Namespace) -> int:
    languages = ("en", "ko") if args.language == "both" else (args.language,)
    try:
        targets = export_skills(args.destination, languages)
    except (OSError, ValueError) as exc:
        print(f"EXPORT_FAIL: {exc}")
        return 1
    for target in targets:
        print(f"EXPORTED_SKILL {target}")
    return 0


def _assess_readiness(args: argparse.Namespace) -> int:
    readiness_issues = validate_file(args.readiness, "first-slice-readiness.schema.json")
    if readiness_issues:
        return _print_issues(readiness_issues)
    build = load_json(args.build)
    readiness = load_yaml(args.readiness)
    ledger_report = validate_surface_ledgers(
        build["fingerprintId"],
        args.static_ui,
        args.lifecycle,
        args.runtime_coverage,
        args.gaps,
    )
    ledger_issues = list(ledger_report.issues)
    if not ledger_issues:
        readiness_gap_ids = tuple(sorted(gap["gapId"] for gap in readiness.get("gaps", [])))
        if readiness_gap_ids != ledger_report.gap_ids:
            ledger_issues.append(
                ValidationIssue(
                    "GAP_SET_MISMATCH",
                    f"readiness gaps={readiness_gap_ids!r}, ledger gaps={ledger_report.gap_ids!r}",
                )
            )
        in_scope = set(readiness["scope"]["inScopeSurfaceIds"])
        missing_surfaces = tuple(sorted(in_scope - set(ledger_report.surface_ids)))
        if missing_surfaces:
            ledger_issues.append(
                ValidationIssue(
                    "SCOPE_SURFACE_NOT_IN_LEDGER",
                    f"in-scope surfaces missing from ledgers: {missing_surfaces!r}",
                )
            )
    if ledger_issues:
        return _print_issues(ledger_issues)
    report = assess_first_slice(
        build,
        load_json(args.source),
        load_json(args.coverage),
        readiness,
    )
    if args.json:
        print(json.dumps(report.as_dict(), ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(f"CONSISTENCY_CHECK {report.consistency_check}")
        print(f"DECISION {report.decision}")
        print(f"validatorScope={report.validator_scope}")
        print(f"buildFingerprintId={report.build_fingerprint_id}")
        print(f"sliceId={report.slice_id}")
        print(f"playerGoal={report.player_goal}")
        print(f"inScopeSurfaceIds={'|'.join(report.in_scope_surface_ids)}")
        for finding in report.offline_findings:
            print(f"offlineFinding={finding}")
        for finding in report.runtime_findings:
            print(f"runtimeFinding={finding}")
        for unknown in report.unknowns:
            print(f"unknown={unknown}")
        print(f"nextTest={report.next_test}")
        for reason in report.reasons:
            print(f"reason={reason}")
        for limit in report.limits:
            print(f"limit={limit}")
    return 1 if report.decision == "BLOCKED FOR THIS SLICE" else 0


def _validate_ledgers(args: argparse.Namespace) -> int:
    report = validate_surface_ledgers(
        args.build_id,
        args.static_ui,
        args.lifecycle,
        args.runtime_coverage,
        args.gaps,
    )
    if report.issues:
        return _print_issues(list(report.issues))
    print(
        "LEDGER_VALIDATION_PASS "
        f"staticCandidates={report.static_candidate_count} "
        f"surfaces={report.surface_count} gaps={report.gap_count}"
    )
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="uar",
        description="Validate Unity accessibility reconnaissance artifacts.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate = subparsers.add_parser("validate", help="Validate one JSON or YAML artifact")
    validate.add_argument("--schema", required=True, help="Contract filename under shared/contracts")
    validate.add_argument("artifact", type=Path)
    validate.set_defaults(handler=_validate)

    bundle = subparsers.add_parser("validate-foundation", help="Validate a build/source/coverage bundle")
    bundle.add_argument("--build", required=True, type=Path)
    bundle.add_argument("--source", required=True, type=Path)
    bundle.add_argument("--coverage", required=True, type=Path)
    bundle.set_defaults(handler=_validate_bundle)

    parity = subparsers.add_parser("check-parity", help="Check English/Korean skill parity")
    parity.add_argument("--root", type=Path)
    parity.add_argument(
        "--manifest",
        type=Path,
        default=Path("shared/bilingual-parity.yaml"),
    )
    parity.set_defaults(handler=_check_parity)

    export = subparsers.add_parser(
        "export-skills",
        help="Export standalone English/Korean skill directories",
    )
    export.add_argument("--destination", required=True, type=Path)
    export.add_argument("--language", choices=("en", "ko", "both"), default="both")
    export.set_defaults(handler=_export_skills)

    ledgers = subparsers.add_parser(
        "validate-ledgers",
        help="Validate lifecycle, runtime-coverage, and gap ledgers",
    )
    ledgers.add_argument("--build-id", required=True)
    ledgers.add_argument("--static-ui", required=True, type=Path)
    ledgers.add_argument("--lifecycle", required=True, type=Path)
    ledgers.add_argument("--runtime-coverage", required=True, type=Path)
    ledgers.add_argument("--gaps", required=True, type=Path)
    ledgers.set_defaults(handler=_validate_ledgers)

    readiness = subparsers.add_parser(
        "assess-readiness",
        help="Compute a slice-scoped consistency decision and next runtime test",
    )
    readiness.add_argument("--build", required=True, type=Path)
    readiness.add_argument("--source", required=True, type=Path)
    readiness.add_argument("--coverage", required=True, type=Path)
    readiness.add_argument("--readiness", required=True, type=Path)
    readiness.add_argument("--static-ui", required=True, type=Path)
    readiness.add_argument("--lifecycle", required=True, type=Path)
    readiness.add_argument("--runtime-coverage", required=True, type=Path)
    readiness.add_argument("--gaps", required=True, type=Path)
    readiness.add_argument("--json", action="store_true", help="Emit deterministic JSON")
    readiness.set_defaults(handler=_assess_readiness)

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return int(args.handler(args))


if __name__ == "__main__":
    sys.exit(main())

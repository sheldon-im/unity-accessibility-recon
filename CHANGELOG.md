# Changelog

All notable changes to Unity Accessibility Reconnaissance are documented here.

## [0.3.0] - 2026-08-22

### Changed

- Replaced whole-game readiness verdicts with progressive, named investigation slices.
- Replaced `PROCEED`, `PROCEED WITH TODOS`, and `DO NOT PROCEED` with `READY FOR RUNTIME PROBE`, `READY FOR SLICE IMPLEMENTATION`, and `BLOCKED FOR THIS SLICE`.
- Marked validator output as `INTERNAL-CONSISTENCY-ONLY` so a consistent agent-authored record is not presented as proof of gameplay truth.
- Upgraded the first-slice readiness contract to schema version 2 with explicit player goals, in-scope surfaces, out-of-scope reasons, runtime probes, challenge tests, and slice-local blockers.
- Limited extraction and UI coverage gates to source families and surfaces that can affect the current slice.
- Expanded plain-text and JSON reports with offline findings, runtime findings, unknowns, limits, and the next falsifiable test.
- Updated the English and Korean skills, templates, registry, examples, and parity rules to match the progressive-slice workflow.

### Validation

- Added regression coverage for static-only, runtime-passed, failed-probe, blocking-gap, unrelated-extraction, missing-surface, and contradictory-decision cases.
- Passed 60 automated tests, bilingual parity, Python compilation, lock verification, package metadata checks, and wheel-content checks.
- Passed a clean Windows 11 wheel installation smoke with Python 3.11.9, including import, CLI startup, installed bilingual parity, and English/Korean standalone skill export.

### Compatibility

- First-slice readiness records from 0.2.0 use schema version 1 and must be migrated to the version 2 progressive-slice contract.
- This package still does not launch a game, install a mod loader, prove physical-key behavior, or replace real screen-reader acceptance testing.

## [0.2.0] - 2026-08-21

- Initial public release of the bilingual reconnaissance skills, shared contracts and templates, `uar` validator, build-bound UI ledgers, readiness checks, and standalone skill export.

[0.3.0]: https://github.com/sheldon-im/unity-accessibility-recon/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/sheldon-im/unity-accessibility-recon/releases/tag/v0.2.0
# Third-Party Notices

This file records the dependency evidence first audited for the local `0.2.0` release candidate on 2026-08-21 and rechecked against the unchanged lock for the `0.3.0` release on 2026-08-22.

## Distribution model

The project wheel contains original Python code, schemas, templates, bilingual skill documentation, `README.md`, and `LICENSE`. It does not vendor dependency source trees or embed third-party Python wheels, native libraries, Unity files, game binaries, or extracted game assets.

Installing the project resolves dependencies as separate distributions under their own licenses. This notice is informational and does not replace those distributions' license texts or metadata.

## Runtime dependencies

The following versions were resolved by the committed `uv.lock` during the audit:

1. `jsonschema 4.26.0` — MIT — https://github.com/python-jsonschema/jsonschema
2. `PyYAML 6.0.3` — MIT — https://pyyaml.org/

Transitive runtime dependencies resolved through `jsonschema`:

1. `attrs 26.1.0` — MIT — https://www.attrs.org/
2. `jsonschema-specifications 2025.9.1` — MIT — https://github.com/python-jsonschema/jsonschema-specifications
3. `referencing 0.37.0` — MIT — https://github.com/python-jsonschema/referencing
4. `rpds-py 2026.6.3` — MIT — https://github.com/crate-py/rpds

## Development and build tools

These tools are used to test or build the project and are not imported by the installed runtime package solely because this repository uses them:

1. `pytest 8.4.2` — MIT
2. `iniconfig 2.3.0` — MIT
3. `packaging 26.3` — Apache-2.0 OR BSD-2-Clause
4. `pluggy 1.6.0` — MIT
5. `Pygments 2.21.0` — BSD-2-Clause
6. `hatchling 1.32.0` in the audited local build environment — MIT

The build-system requirement is version-bounded but not exactly pinned, so another compliant build environment may resolve a different Hatchling 1.x release.

## Project and game-content boundary

The project is licensed under MIT. That license covers this repository's original code and documentation only. It does not grant rights to redistribute Unity, games, proprietary binaries, extracted assets, saves, profiles, or runtime logs.

A future installer, executable bundle, container, or release archive that embeds dependencies or game-related payloads requires a separate composition and license audit. A clean source tree or wheel does not by itself prove that another distribution format is compliant.

# Unity Accessibility Reconnaissance

[한국어](README.ko.md)

Plan a Unity accessibility mod before you start coding.

This project helps a blind player and an AI agent study a Unity game in a consistent way. It records which game files were collected, maps the game's screens and controls, and shows what still needs live testing.

The goal is to collect enough reliable information at the start. This reduces the chance that a blind user must return to visual UI investigation after implementation has begun.

## Who this is for

This project is for:

- blind players who are making a Unity accessibility mod with an AI agent;
- accessibility mod authors who need a repeatable investigation process;
- teams that want clear evidence before they start changing game code.

You do not need to understand every schema or command. The agent can manage the technical records and checks. The user still decides the product goal, the scope, and whether the result works with a real screen reader and keyboard.

## What it does

The workflow helps an agent:

1. identify the exact game build;
2. preserve the original files and check what the dump contains;
3. list the game's screens, controls, menus, pop-ups, and state changes;
4. separate facts found in files from behavior observed in the running game;
5. track missing information instead of hiding it;
6. decide whether the first accessibility feature is ready to implement.

If required evidence is missing, the validator returns `DO NOT PROCEED` instead of guessing.

## What it does not do

This package does not make a game accessible by itself. It is not a game mod, mod loader, automatic player, or screen reader.

It also does not prove that a control works just because the control exists in a file. Live game behavior, physical keyboard input, speech output, and NVDA use require separate evidence.

## What is included

The repository contains:

- an [English skill](skills/unity-accessibility-reconnaissance-en/SKILL.md) and a [Korean skill](skills/unity-accessibility-reconnaissance-ko/SKILL.md) with the same workflow;
- seven JSON Schema contracts for checking saved records;
- eight templates for starting a new investigation;
- a command-line validator named `uar`;
- a tool that exports both skills for other local AI agent environments;
- `CODE-QA.md`, which records completed checks and known limits.

## Plain-language terms

- **Reconnaissance** means collecting and checking information before implementation.
- **Build-bound** means that a record belongs to one exact game version. Evidence from different versions must not be mixed.
- A **dump** is a structured copy or report made from game code, assets, scenes, prefabs, or localization files.
- **Static evidence** comes from files. **Runtime evidence** comes from observing the running game.
- A **ledger** is a structured list of screens, controls, evidence, or open gaps.
- `claimGrade` says how strong a fact is. `coverageGate` says how far a UI screen has moved through the investigation process.
- **Fail closed** means stopping when important evidence is missing instead of assuming that everything works.

The official phase IDs, claim grades, coverage gates, privacy classes, and verdicts are in `shared/phase-ids.yaml`.

## How the work is shared

1. The agent collects files, studies the game structure, keeps the records, runs checks, and fixes clear local problems within the approved scope.
2. The user decides the product direction, scope changes, access to sensitive data, acceptance with a real screen reader and keyboard, and any accepted blockers.
3. Permission to inspect, edit, test, build, or make a local commit does not give permission to launch a game, install a loader, push, publish, release, or deploy.

## Start here

If you only want to use the investigation workflow, begin with the [English skill](skills/unity-accessibility-reconnaissance-en/SKILL.md) or [Korean skill](skills/unity-accessibility-reconnaissance-ko/SKILL.md). The `shared/templates/` directory contains blank records for a new project.

To run the automated checks, install Python 3.11 or later and [uv](https://docs.astral.sh/uv/). Then run:

```bash
uv sync --dev
uv run pytest -q
uv run uar check-parity --root .
```

Check that a build, source inventory, and dump report belong together:

```bash
uv run uar validate-foundation \
  --build BUILD.json \
  --source SOURCE.json \
  --coverage COVERAGE.json
```

Check the UI records for one game build:

```bash
uv run uar validate-ledgers \
  --build-id BUILD-ID \
  --static-ui STATIC-UI.json \
  --lifecycle SURFACES.csv \
  --runtime-coverage RUNTIME-COVERAGE.csv \
  --gaps GAPS.csv
```

Ask whether the first accessibility feature is ready to implement:

```bash
uv run uar assess-readiness \
  --build BUILD.json \
  --source SOURCE.json \
  --coverage COVERAGE.json \
  --readiness FIRST-SLICE.yaml \
  --static-ui STATIC-UI.json \
  --lifecycle SURFACES.csv \
  --runtime-coverage RUNTIME-COVERAGE.csv \
  --gaps GAPS.csv \
  --json
```

Possible results are `PROCEED`, `PROCEED WITH TODOs`, and `DO NOT PROCEED`. The command exits with a nonzero status for `DO NOT PROCEED`.

## Export the skills

```bash
uv run uar export-skills \
  --destination /path/to/agent-skills \
  --language both
```

Each exported folder includes its skill, references, contracts, templates, shared registry, adapter contract, and MIT license. The exporter will not replace an existing target folder.

## Verification status

Version `0.2.0` passed 55 automated tests. The package was also built and installed in a clean Windows 11 environment with Python 3.11.9. The installed wheel produced the expected `PROCEED` and `DO NOT PROCEED` results and exported both language versions correctly.

No raw game files or private runtime logs are tracked. See `CODE-QA.md` for the detailed quality record and remaining unverified areas.

## Privacy and licensing

- Do not commit game binaries, extracted proprietary files, saves, profiles, credentials, or sensitive runtime logs.
- This repository's original code and documentation use the MIT License. See `LICENSE`.
- Python dependencies are installed separately. They are not copied into the wheel. See `THIRD-PARTY-NOTICES.md` for their versions and licenses.
- The MIT License does not cover Unity, any game, extracted assets, proprietary binaries, saves, profiles, or logs.
- Audit each release archive separately. A clean source tree does not automatically prove that a release archive is clean.

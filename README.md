# Unity Accessibility Reconnaissance

[한국어](README.ko.md)

Plan and test one small Unity accessibility-mod slice at a time.

This project provides a bilingual, agent-neutral workflow for people who build Unity accessibility mods with AI agents. It helps the user and agent agree on the next player goal, inspect only the game systems that can affect that goal, record what is still unknown, and define the smallest useful live test.

The goal is to reduce late UI re-investigation without turning the start of a project into a whole-game dump or UI census. Reconnaissance grows when implementation or live testing reveals a real dependency.

## Who this is for

This project is for:

- people making a Unity accessibility mod with an AI agent, including nonvisual and screen-reader-led workflows;
- accessibility mod authors who need a repeatable investigation process;
- teams that want evidence and explicit unknowns before changing game code.

You do not need to understand every schema or command. The agent can manage technical records and checks. The user still chooses the player goal and scope, reviews the plain-language result, and decides whether the feature works with a real screen reader and keyboard.

## What it does

For each small player-facing slice, the workflow helps an agent:

1. identify the exact game build and preserve the minimum source baseline;
2. state the player goal and the UI surfaces that are in and out of scope;
3. inspect only the code, assets, screens, controls, and transitions that can affect that slice;
4. separate offline findings from behavior observed in the running game;
5. attach a challenge test to important offline assumptions;
6. report unknowns and the next live test in plain language;
7. decide whether the slice is ready for a runtime probe, implementation, or neither.

An unrelated extraction failure does not block every feature. A missing dependency that can affect the current slice returns `BLOCKED FOR THIS SLICE` instead of being hidden.

## What it does not do

This package does not make a game accessible by itself. It is not a game mod, mod loader, automatic player, or screen reader.

The validator is marked `INTERNAL-CONSISTENCY-ONLY`. It checks whether the records agree with each other; it does not prove that the agent's claims are true in the live game. Static evidence cannot replace runtime observation, physical keyboard input, speech output, or manual NVDA acceptance.

It also does not require a complete map of every menu before useful implementation can begin. Decisions apply only to the named slice.

## What is included

The repository contains:

- an [English skill](skills/unity-accessibility-reconnaissance-en/SKILL.md) and a [Korean skill](skills/unity-accessibility-reconnaissance-ko/SKILL.md) with the same workflow;
- seven JSON Schema contracts for checking saved records;
- eight templates for starting a new investigation;
- a command-line validator named `uar`;
- a tool that exports both skills for other local AI agent environments;
- `CODE-QA.md`, which records completed checks and known limits.

## Plain-language terms

- **Reconnaissance** means answering the questions needed for the next small feature, then expanding the map only when evidence requires it.
- **Build-bound** means that a record belongs to one exact game version. Evidence from different versions must not be mixed.
- A **dump** is a structured copy or report made from game code, assets, scenes, prefabs, or localization files.
- **Static evidence** comes from files. **Runtime evidence** comes from observing the running game.
- A **ledger** is a structured list of screens, controls, evidence, or open gaps.
- `claimGrade` says how strong a finding is. `coverageGate` says how far an in-scope UI surface has moved through the investigation process.
- A **challenge test** is a small live test that could show an offline assumption is wrong. `challengedClaimIds` states exactly which claims a runtime probe tests.
- **Consistency-only validation** means checking the record structure without claiming that the game itself has been proven.

The official phase IDs, claim grades, coverage gates, privacy classes, and verdicts are in `shared/phase-ids.yaml`.

## How the work is shared

1. The agent collects the minimum needed files, studies the current slice, keeps the records, runs checks, and fixes clear local problems within the approved scope.
2. The user chooses the player goal, reviews scope changes and plain-language findings, controls sensitive access, and performs or directs acceptance with a real screen reader and keyboard.
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

Assess the next accessibility slice:

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

Possible decisions are `READY FOR RUNTIME PROBE`, `READY FOR SLICE IMPLEMENTATION`, and `BLOCKED FOR THIS SLICE`. The command exits with a nonzero status only for `BLOCKED FOR THIS SLICE`. Without `--json`, it prints the player goal, offline findings, runtime findings, unknowns, limits, and next test.

## Export the skills

```bash
uv run uar export-skills \
  --destination /path/to/agent-skills \
  --language both
```

Each exported folder includes its skill, references, contracts, templates, shared registry, adapter contract, and MIT license. The exporter will not replace an existing target folder.

## Verification status

Version `0.3.0` is a development candidate. Its progressive-slice contracts, consistency-only validator, bilingual parity, CLI output, and package build are checked by the repository test suite. The previous `0.2.0` wheel passed a clean Windows 11 installation test; the changed `0.3.0` behavior still needs a new Windows-native smoke test before release.

No raw game files or private runtime logs are tracked. See `CODE-QA.md` for the detailed quality record and remaining unverified areas.

## Privacy and licensing

- Do not commit game binaries, extracted proprietary files, saves, profiles, credentials, or sensitive runtime logs.
- This repository's original code and documentation use the MIT License. See `LICENSE`.
- Python dependencies are installed separately. They are not copied into the wheel. See `THIRD-PARTY-NOTICES.md` for their versions and licenses.
- The MIT License does not cover Unity, any game, extracted assets, proprietary binaries, saves, profiles, or logs.
- Audit each release archive separately. A clean source tree does not automatically prove that a release archive is clean.
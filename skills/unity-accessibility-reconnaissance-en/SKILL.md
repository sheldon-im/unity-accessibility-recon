---
name: unity-accessibility-reconnaissance-en
description: Use when starting a Unity screen-reader accessibility mod.
version: 0.2.0
language: en
license: MIT
---

# Unity Accessibility Reconnaissance

## POLICY-AGENT-NEUTRAL — Core contract

Use this skill before implementing the first player-facing slice of a Unity screen-reader accessibility mod. It establishes a build-bound source baseline, reconciles static extraction, maps the whole game's UI lifecycle, and defines the runtime evidence needed to avoid late, broad UI re-investigation.

The procedure is agent-neutral. Tool adapters may map capabilities such as file inventory, hashing, managed-code inspection, Unity asset reading, runtime observation, native-input delivery, and speech dispatch. They may not change claim grades, coverage gates, schemas, or authorization boundaries. Canonical phase IDs, `claimGrade`, `coverageGate`, privacy classes, and verdicts are defined in `shared/phase-ids.yaml` or an exported skill's `references/phase-ids.yaml`.

## POLICY-AGENCY — Player and user agency

The blind player remains the player. Expose semantic state and explicit controls; do not silently choose dialogue, units, targets, routes, purchases, or other meaningful outcomes. Prefer game-owned text, localization, input, callbacks, and observable postconditions over visual scraping or agent-authored substitute gameplay.

The blind user is not the visual census worker or the project's QA manager. The agent must gather structural and runtime observability evidence, choose appropriate checks, split work and commits, and repair clear local findings inside the authorized scope. Ask the user only for product-direction choices, scope expansion, sensitive-data access, actual screen-reader/keyboard acceptance, accepted blocker debt, or external/irreversible effects.

## POLICY-EVIDENCE — Claim grades and coverage gates

Never promote one grade into another without new evidence. `claimGrade` records the strongest fact an artifact may claim; `coverageGate` records how far a UI surface has progressed through lifecycle verification. Do not convert one taxonomy into the other.

1. `SOURCE-IDENTIFIED`: exact source and build identity recorded.
2. `STATIC-CONFIRMED`: code, asset, localization, callback, or binding exists in the declared extraction scope.
3. `RUNTIME-OBSERVED`: the current runtime owner, state, or transition was observed without claiming keyboard usability.
4. `PHYSICAL-INPUT-PROVEN`: a real key traveled through the intended game-owned input path.
5. `POSTCONDITION-PROVEN`: the intended semantic game state changed exactly once.
6. `SPEECH-DISPATCH-PROVEN`: the speech transport accepted the exact event; this is not proof that the user heard it.
7. `NVDA-MANUAL-CONFIRMED`: the user heard and accepted the relevant speech/keyboard path.
8. `OPEN / DYNAMIC-UNVERIFIED`: evidence is missing, conditional, parser-limited, or build-stale.

Read [dump and source reconciliation](references/dump-and-source-reconciliation.md), [UI surface and lifecycle coverage](references/ui-surface-and-lifecycle-coverage.md), and [agent-owned work and Code QA](references/agent-owned-work-and-code-qa.md) before closing their corresponding gates.

## G0-AUTHORIZATION — Fix the investigation boundary

Record the product, ownership/authorization basis, allowed source locations, prohibited data, and current execution ceiling. Separate read-only inspection from game launch, loader installation, input injection, save/profile/cloud mutation, commit, push, publication, and release.

Stop and ask only if ownership is unclear, policy blocks the intended mod surface, sensitive data is required, or the next action crosses the current authorization ceiling. Do not ask for confirmation for each reversible read-only step already inside scope.

### ART-AUTHORIZATION-RECORD — Authorization record

Record:

- exact product and distribution;
- repository and installed-build ownership;
- allowed read-only roots;
- sensitive/proprietary exclusions;
- separately authorized runtime actions;
- current commit and external-effect permissions.

Verdict: `PROCEED`, `PROCEED WITH TODOs`, or `DO NOT PROCEED`.

## G1-BASELINE — Freeze the build and source identity

Create the exact build fingerprint before extraction. Include product/build version, Unity version, Mono or IL2CPP backend, architecture, candidate loader, and hashes/sizes of key source files. Inventory original mutable and immutable roots separately and define a pre/post preservation check.

Do not mix evidence from another patch, platform, backend, parser version, or installed artifact. If the build changes, open a new fingerprint and explicitly decide which prior evidence remains structurally reusable.

### ART-BUILD-FINGERPRINT — Build fingerprint

Use repository `shared/contracts/build-fingerprint.schema.json`; an exported standalone skill carries the same file at `references/contracts/build-fingerprint.schema.json`. The record must contain enough identity to fail closed when another build's extraction or runtime evidence is supplied.

### ART-SOURCE-MANIFEST — Source manifest

Use repository `shared/contracts/source-manifest.schema.json`; exported skills use `references/contracts/source-manifest.schema.json`. Every expected source family must be `extracted`, `partial`, `excluded-with-reason`, `unsupported`, `failed`, or `not-present`, with evidence and a reason when applicable. Use `partial` when one family contains both successful and unsuccessful targets; never collapse that state into success. Record pre/post preservation digests.

## G2-EXTRACTION — Reconcile the original-source extraction

Declare the extractor scope before running tools. A useful Unity baseline normally considers:

- player executable and Unity player/runtime identity;
- Mono assemblies or IL2CPP binary plus metadata;
- global managers and serialized settings;
- scenes, prefabs, resources, asset bundles, and addressable catalogs when present;
- localization tables and runtime localization owners;
- old/new Input System assets, fixed hotkeys, and input-router code;
- managed types, methods, inheritance, serialized callbacks, and dynamic/reflection/instantiate hints;
- mutable saves, profiles, settings, cloud roots, and logs as protected inventory, not tracked fixtures.

Count success, exclusion, unsupported, parser failure, and unresolved items. A large dump is not a complete dump unless source counts reconcile and failures are named.

### ART-EXTRACTION-COVERAGE — Extraction coverage

Use repository `shared/contracts/extraction-coverage.schema.json`; exported skills use `references/contracts/extraction-coverage.schema.json`. `DUMP-READY` requires one build identity, declared scope, reconciled counts, deterministic outputs or an explicit non-determinism explanation, preservation success, and no first-slice blocker hidden in a failed family.

`DUMP-PARTIAL` is an honest result. It may proceed only when each gap has an owner, evidence impact, and bounded re-open trigger.

## G3-STATIC-DISCOVERY — Build the UI discovery set

Create ledgers for UI elements, interactable candidates, localization links, callbacks, and input actions. Preserve source evidence and confidence; do not flatten them into one player-facing list.

Include inactive templates, pooled objects, dynamic-generation hints, pointer-only candidates, and unresolved script types so omissions remain visible. Label them as discovery evidence, not active runtime controls.

### ART-STATIC-UI-LEDGER — Static UI ledger

Each record follows `references/contracts/static-ui-ledger.schema.json`. The artifact MUST carry the foundation bundle's `buildFingerprintId`; start from `templates/static-ui-ledger.json`.

Every discovered candidate must become a semantic candidate, explicit exclusion, or gap. A control's existence does not prove visibility, focus, keyboard action, or task completion.

## G4-LIFECYCLE-MAP — Map the whole-game surface lifecycle

Before the first feature slice, enumerate player-meaningful surface families across the game:

- startup warnings, consent, language, title, and account/cloud conflict;
- options, rebind, save/load/profile, and multiplayer/lobby;
- HUD, notifications, dialogue, quest, tutorial, pause, death, result, ending, and credits;
- inventory/grid, shop, crafting, construction, map/scanner/navigation;
- game-specific live gameplay, status, hazard, target, unit, or world-interaction surfaces.

For each family, record entry/exit predicates, runtime owner candidates, modal depth, required/optional controls, initial focus, child transitions, parent restoration, specialized interaction model, privacy class, and conditional content.

### ART-SURFACE-LIFECYCLE-MATRIX — Surface lifecycle matrix

Use `templates/surface-lifecycle-matrix.csv` with a screen-reader-friendly companion. Every row MUST use the static UI ledger and foundation bundle's `buildFingerprintId`; unknown required ownership blocks generic implementation.

The matrix is a coverage map, not a promise to implement every surface in the first release.

## G5-RUNTIME-COVERAGE — Observe active owners and controls

Runtime work is a separate authorization boundary. Start with an opt-in, speech-free observer. Prefer the game's current/top UI stack, panel/window ownership, active/enabled/interactable state, `CanvasGroup` eligibility, `EventSystem` selection, and game-owned default/last focus over global object enumeration.

Model surface generations. Enter only after owner and semantic values stabilize; exclude inactive parents while a child modal owns input; invalidate cached Unity objects on close, scene change, death, respawn, or replacement; observe game-owned parent focus restoration.

### ART-RUNTIME-COVERAGE — Static-to-runtime coverage ledger

For every surface family, advance only through supported gates:

```text
STATIC-MAPPED
RUNTIME-OWNER-OBSERVED
ACTIVE-CONTROLS-INVENTORIED
SEMANTIC-MODELED
NATIVE-FOCUS-PROVEN
NATIVE-ACTION-POSTCONDITION-PROVEN
NVDA-MANUAL-CONFIRMED
COVERAGE-CLOSED
```

`COVERAGE-CLOSED` means all currently meaningful controls have a semantic entry, explicit exclusion, or reproducible gap. It does not mean every Unity component is spoken.

## G6-INPUT-POSTCONDITION — Prove native input and completion

First observe the uncontaminated game-owned input path. Disable legacy accessibility key suppression, forced focus synchronization, broad Harmony interception, and generic cursor routing unless an explicit diagnostic flag enables them.

For each action, record precondition, physical key, input owner, selected/focused semantic identity, native callback, and resulting game state. OS-level injection proves delivery only if the Unity/game observer confirms it. A callable callback does not prove physical keyboard support or current pointer eligibility.

Only add a surface-scoped semantic fallback after the native path is shown to be absent or unusable. Never announce intended action as success; require one observable postcondition.

### ART-NATIVE-INPUT-MATRIX — Native input and postcondition matrix

Classify each action as native-proven, native-partial, pointer-only-proven, fallback-required, blocked, or open. Include modal ownership, repeat behavior, stale-target handling, destructive confirmation, and whether the action changes selection, camera, save, network, or world state.

## G7-FIRST-SLICE-READINESS — Select the first accessibility slice

Choose the smallest user-meaningful path that exercises real ownership, semantic labeling, native input, postcondition, speech, and lifecycle restoration. Startup modal plus main title is often safer than a generic all-screen cursor, but use the game's actual dependency graph.

A first slice may start only when:

1. G0 and G1 are closed.
2. G2 is `DUMP-READY` or bounded `DUMP-PARTIAL` with no blocker for the slice.
3. G3 and G4 cover the whole-game discovery and surface families at declared confidence.
4. Required runtime owner/input unknowns for the slice are explicitly testable.
5. privacy, deployment rollback, and game/profile preservation are defined.
6. agent-owned work, commit, verification, and Code QA gates are recorded.

### ART-GAP-LEDGER — Gap ledger

Each gap needs a stable ID, affected build/surface, `claimGrade`, user impact, current mitigation, smallest next evidence, owner, blocking status, and re-open trigger. “Needs more testing” is not a sufficient entry.

### ART-FIRST-SLICE-READINESS — Readiness record

The record names the slice, required artifacts, applicable gaps, QA verdict, authorization boundary, and one of:

- `PROCEED`: all entry gates are satisfied.
- `PROCEED WITH TODOs`: nonblocking gaps have explicit guards and re-open triggers.
- `DO NOT PROCEED`: a foundational assumption, first-slice blocker, preservation failure, or mixed-build condition remains.

## CHECK-EVIDENCE-SEPARATION — Claim audit

Before reporting, map every claim to its actual grade. Build, schema validation, callback invocation, speech return code, and a successful agent-driven sequence must not be described as manual keyboard/NVDA acceptance.

## CHECK-USER-ROLE — Blind-user burden audit

Confirm that the agent did not ask the blind user to visually enumerate screens, read screenshots, infer Unity hierarchy, choose test categories, split commits, or manage QA ledgers. User work should be limited to decisions and actual experiential acceptance that cannot be automated honestly.

## CHECK-REPORTING — Phase report

At each gate report:

1. artifacts created and their build identity;
2. evidence collected and exact checks run;
3. gaps closed and remaining blockers;
4. automatic repairs and QA verdict;
5. next authorized local slice;
6. only the smallest user decision, if genuinely required;
7. actions not performed, especially runtime, sensitive-data, commit, push, publication, and release boundaries.

## Pitfalls

- Starting with one visible menu and generalizing a generic cursor.
- Treating `activeInHierarchy`, `interactable`, or callback existence as current player operability.
- Calling hover/click/selection methods to obtain labels.
- Mixing parser outputs or runtime logs from different builds.
- Hiding parser failures inside aggregate success counts.
- Using object names as final player labels when localization or semantic owners exist.
- Forcing focus before observing the game-owned initial selection.
- Making the user repeatedly approve internal commits or decide how to fix clear local QA findings.
- Letting agent-specific tooling become a requirement of the core procedure.

## Final output

Produce a concise, screen-reader-friendly phase report and machine-readable artifacts. Preserve exact IDs, paths, hashes, commands, schema keys, claim grades, and coverage gates. Keep proprietary/raw evidence outside tracked skill content.

# UI Surface and Lifecycle Coverage

## UI-DISCOVERY — Keep discovery separate from eligibility

Static extraction creates a superset. It may include live controls, inactive parents, templates, prefab instances, pooled objects, decorative text, debug screens, stale tags, pointer-only hit targets, and unresolved scripts. Preserve these distinctions.

Recommended static artifact and record fields:

- top-level `buildFingerprintId` bound to the foundation bundle
- stable candidate ID, UI hierarchy, and owner type
- uGUI/TMP/UI Toolkit/custom control family
- rendered/serialized text and localization key/source;
- `Selectable`, submit/cancel, pointer, drag/drop, slider/toggle/tab/input behavior;
- serialized and managed callbacks;
- input action/binding and fixed-key evidence;
- active/default/template/pool/dynamic hints;
- privacy class, confidence, and unresolved reason.

Global enumeration is acceptable for diagnostic census. It is not a player-facing eligibility rule.

## UI-FAMILIES — Follow the current slice dependency path

Start from one player goal and inventory only the surfaces needed to enter, complete, cancel, fail, and restore that path. Include adjacent modal or conditional surfaces only when static evidence or a runtime observation shows they can affect the slice.

Keep other families in a short out-of-scope list. Do not enumerate options, saves, multiplayer, HUD, inventory, maps, endings, DLC, or other game-specific systems merely because they might exist. Promote one of them into the dependency map when a selected feature, implementation finding, or live test makes it relevant.

For an inaccessible or unreached condition inside the current slice, record the dependency and the smallest future observation plan. Do not silently omit an applicable unknown.

## UI-OWNERSHIP — Name the current state owners

Find the game-owned sources for:

- current/top panel, window, control stack, or state machine;
- open/enabled/control-enabled/interactable state;
- `CanvasGroup` alpha/interactable/blocks-raycasts;
- `EventSystem.current.currentSelectedGameObject`;
- default and last selected controls;
- child-modal open/close and parent-disable/restore behavior;
- semantic values and action readiness;
- input-map or gameplay-router ownership.

`activeInHierarchy=true` alone is weak. Multiple parallel UI roots may remain active while only one receives input. A visible child may suppress its active parent. A retained object may have alpha zero, disabled raycasts, stale backing state, or no semantic readiness.

Use the game's owner stack first. Apply global filters only as corroborating evidence.

## UI-GENERATION — Model the lifecycle explicitly

Assign a new `surfaceGeneration` when the top semantic owner opens, is replaced, or re-enters with new backing state.

Lifecycle:

1. `enter`: observe owner candidate and wait for stable semantic readiness, not a fixed delay alone;
2. `initial-focus`: observe game-owned selection before setting anything;
3. `focus/value`: publish stable identity, role, label, value and state once;
4. `child-open`: child becomes speech/input owner; suppress parent entries and stale queued speech;
5. `child-close`: observe native restoration and announce restored context once;
6. `replace/scene-change`: invalidate cached Unity references, candidates, routes and pending announcements;
7. `error/cancel`: preserve or clear state according to the real game owner, not the agent's assumption.

A Unity object identity without generation is unsafe across pooling, scene replacement and dynamic-list refresh.

## UI-SNAPSHOT — Use semantic snapshots

Minimum runtime snapshot:

```text
buildFingerprintId
runId
sceneName
surfaceGeneration
surfaceOwnerType
surfaceOwnerIdentity
modalDepth
controlIdentity
role
label
labelSource
localizationKey
value
state
activeInHierarchy
enabled
interactable
privacyClass
actionFamily
coverageGate
```

Label precedence:

1. game semantic/localization API;
2. rendered TMP/uGUI text;
3. control-specific value owner;
4. associated parent/child label;
5. diagnostic object name, explicitly marked as fallback.

Reading a label must not call hover, click, selection-change, animation, material, or game-state methods. Sensitive text can be spoken locally when explicitly focused, but logs should keep only redacted identity, type and length.

## UI-INPUT — Preserve specialized interaction models

Do not flatten every surface into Up/Down/Enter.

- buttons/list: native next/previous and submit/cancel;
- slider/toggle/radio/tab: native value and state semantics;
- text input/IME: editing mode, composition, confirm/cancel and privacy;
- rebind: listening state, conflicts, cancel/reset and native device ownership;
- inventory/grid: row/column, item identity, detail, drag/drop and rotation;
- map: node/candidate identity, current selection, locked state, preview versus activation;
- world interaction: semantic target, navigation point, interaction readiness and observable completion.

First observe physical input with mod-owned suppression/focus forcing disabled. A QA callback can prove lifecycle but not physical-key UX. If a fallback is required, scope it to one active owner and one explicit user command.

## UI-CLOSURE — Close coverage honestly

For each surface family, maintain these gates:

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

A family is `COVERAGE-CLOSED` only when:

1. required active controls have semantic entries;
2. optional/conditional absence is explained;
3. decorative/template/debug/stale items have explicit exclusion reasons;
4. dynamic and pointer-only cases have bounded dispositions;
5. child-modal and parent-restore lifecycle is verified where applicable;
6. native input and postcondition claims match actual evidence;
7. manual NVDA claims exist only where the user confirmed them;
8. remaining gaps have reproducible conditions and re-open triggers.

Slice lifecycle mapping may be sufficient while the rest of the game remains intentionally unknown. `COVERAGE-CLOSED` applies only to the named surface and evidence envelope; it is not a whole-game verdict.

## UI-REOPEN — Prevent broad re-investigation

Re-open only the affected evidence envelope when one of these occurs:

- build or relevant source hash changes;
- parser/schema/adapter version changes;
- new surface owner, control family, localization source or input router appears;
- required runtime control is absent from the static ledger;
- static candidate cannot be assigned at runtime;
- game update changes lifecycle, modal ownership, focus restoration or postcondition;
- repeated stale speech/focus bugs reveal an invalid generation model;
- user acceptance finds missing, duplicate, misleading or unusable output;
- new profile/DLC/multiplayer/progression condition activates an unmapped surface.

Use build/type/scene/source-to-surface dependency links to select the smallest re-open set. Do not rerun every dump merely because one label changed, and do not preserve a stale closure verdict merely because aggregate counts match.

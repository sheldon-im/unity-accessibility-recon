# Dump and Source Reconciliation

## DUMP-SCOPE — Declare the evidence envelope

Define the exact question before extraction: which installed build, backend, platform, content roots, UI systems, localization sources, input systems, and dynamic-generation mechanisms are in scope. The envelope must distinguish:

- source that exists and was extracted;
- source inspected but intentionally excluded;
- unsupported format or parser limitation;
- extraction failure;
- expected family confirmed absent;
- mutable user data inventoried only for preservation.

Do not use “full dump” without the declared envelope. Prefer `DUMP-READY under declared scope` or `DUMP-PARTIAL`.

## DUMP-FINGERPRINT — Bind every artifact to one build

The fingerprint should include:

1. product/distribution identifier and exact build/version;
2. Unity version from trustworthy metadata;
3. Mono or IL2CPP backend and process architecture;
4. platform and relevant DLC/content set;
5. key file relative paths, sizes, SHA-256 values, and modification metadata when useful;
6. loader candidate and its compatibility status, without installing it;
7. source-manifest digest or stable identity. For the shared contract, compute SHA-256 over canonical JSON encoded as UTF-8 with sorted keys and no insignificant whitespace.

Every downstream manifest, ledger, report, runtime run, and acceptance record repeats the fingerprint ID. Validators must reject mixed IDs.

A patch or content update opens a new fingerprint. Reusing type names or prior notes is allowed only as a question generator until the new build confirms them.

## DUMP-SOURCE-FAMILIES — Inventory before selecting tools

### Mono build

Inventory at least:

- `*_Data/Managed/*.dll` and assembly dependencies;
- player executable and `UnityPlayer.dll`;
- `globalgamemanagers`, `globalgamemanagers.assets`, `resources.assets`, shared assets, scene containers, bundles, and catalogs;
- configuration and boot metadata;
- localization tables/resources;
- Input Manager, Input System action assets, and input-router code;
- game-owned UI managers, panel/window bases, `EventSystem`, selection owners, callback paths, and state models.

### IL2CPP build

Add:

- `GameAssembly.dll` or platform equivalent;
- `global-metadata.dat`;
- generated or reconstructed type/method metadata;
- stripped/obfuscated/unresolved method and type accounting;
- parser-tool version and reconstruction confidence.

### Dynamic and specialized UI

Search for:

- `Instantiate`, addressables, reflection, object pools, generated lists/grids, and runtime localization;
- uGUI, TextMeshPro, UI Toolkit, legacy IMGUI, custom mesh/collider UI, and world-space canvases;
- pointer interfaces, raycast order, submit/cancel handlers, fixed hotkeys, rebinding flows, and gameplay input routers;
- network, progression, DLC, save-state, boss/ending, and conditional surfaces that static default-state assets may not reveal.

Absence of a search hit is not runtime proof of absence. Record the search and resulting confidence.

## DUMP-PARSER-IDENTITY — Make extraction reproducible

For every extractor, record:

- tool name, version, source/release URL or package lock, and executable/package hash when practical;
- command line or deterministic invocation parameters;
- input fingerprint and exact output root;
- parser warnings, unreadable objects, unresolved script types, decompile failures, and fallback tools;
- output normalization, canonical ordering, encoding, and any nondeterministic fields removed;
- license and redistribution boundary.

Do not commit decompiled source or proprietary serialized payloads. Track schemas, synthetic fixtures, compact sanitized summaries, and hashes instead.

A fallback parser does not erase the primary parser failure. Keep both findings in the gap ledger and state what the fallback proved.

## DUMP-RECONCILIATION — Prove disposition completeness

For each family calculate:

```text
discovered = extracted + excluded + unsupported + failed + not-present
```

Use `not-present` only when the family itself is inapplicable or confirmed absent; do not use it to hide an unreadable item.

At the source-family summary level, use disposition `partial` when at least one target was extracted and at least one target was excluded, unsupported, or failed. Preserve the per-target counts above; `partial` is a summary state, not an extra count bucket. `recordCount` is the successfully extracted count represented by evidence: it equals coverage `extracted` for `extracted` or `partial`, and is zero for other summary dispositions.

Reconcile at useful levels:

- files and containers;
- scenes/prefabs/assets;
- GameObjects and MonoBehaviour instances;
- managed types/methods/inheritance;
- UI candidates and Selectables;
- callbacks and input bindings;
- localization files, keys, and UI links;
- unresolved types, dynamic candidates, pointer-only candidates, and parse/decompile failures.

Counts are discovery controls, not player-accessibility completion metrics. A thousand candidate buttons do not imply a thousand player-facing entries.

Run the same normalized extraction twice when feasible. Byte equality is strongest; otherwise compare canonical semantic records and explain volatile metadata.

## DUMP-PRESERVATION — Protect originals and user state

Before any runtime or loader work:

1. inventory immutable installed-game sources;
2. inventory mutable save, profile, settings, `LocalLow`, cloud, mod-loader, and log roots separately;
3. state which paths may be added, changed, or deleted;
4. preserve user-authored data unless explicit deletion/restoration is authorized;
5. compare pre/post size, hash, count, and modification metadata for the declared immutable set;
6. stop on unexpected original-file change.

Read-only extraction should not start the game or install a loader. If a tool requires writeable working copies, copy source into an ignored/external evidence root and retain origin hashes.

## DUMP-PRIVACY — Minimize tracked evidence

Classify save names, profile names, room codes, IP addresses, chat/free text, absolute user paths, account IDs, cloud metadata, and speech payloads as sensitive unless proven otherwise.

Tracked artifacts may contain:

- opaque synthetic identity;
- relative source family and type/category;
- count, hash, schema, confidence, and gap reason;
- tiny non-proprietary hand-authored fixtures.

Tracked artifacts must not contain:

- game binaries or extracted source/assets;
- real save/profile names or backing filenames;
- raw logs, screenshots, audio, textures, meshes, localization corpora, or decompiled code;
- credentials, tokens, account/network identifiers, or personal absolute paths.

### DUMP-PRIVACY-TIERS — Three evidence tiers

Keep three explicit storage tiers:

1. **Tier 1 — raw working evidence:** proprietary source copies and detailed extraction output in an ignored or external root with origin hashes and access boundaries.
2. **Tier 2 — normalized external evidence:** canonical ledgers, replay inputs, and detailed reports that remain outside version control because they can reconstruct game content or expose private values.
3. **Tier 3 — tracked privacy-minimal evidence:** schemas, synthetic fixtures, opaque build bindings, counts, digests, bounded gaps, and only the smallest non-reconstructive product data required.

Promotion between tiers is allowlist-based, never a bulk copy. When feasible, an independent validator or byte-identical replay must rederive Tier 3 output from upstream hashes. Passing privacy checks does not promote static geometry, labels, or envelopes into runtime membership, navigation, operability, or user acceptance.

## DUMP-VERDICT — Close or carry the extraction gate

`DUMP-READY` requires:

1. one accepted build fingerprint;
2. all declared source families dispositioned;
3. count reconciliation;
4. parser/tool identity and warnings recorded;
5. original preservation passed;
6. deterministic replay passed or bounded variance explained;
7. no failed/unsupported/unresolved item capable of invalidating the first slice without an explicit runtime plan;
8. a complete gap ledger for remaining unknowns that can affect the declared slice.

`DUMP-PARTIAL` may support the next slice when that slice is not affected, the gap is fail-closed, and the exact re-open trigger is known. Do not frontload extraction for unrelated systems. `BLOCKED FOR THIS SLICE` applies to mixed builds, preservation failure, unexplained count loss inside the declared scope, unknown parser trust, or an applicable source blocker.

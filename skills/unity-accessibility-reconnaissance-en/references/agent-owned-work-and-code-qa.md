# Agent-Owned Work and Code QA

## WORK-OWNERSHIP — Agent-owned execution, user-governed boundaries

The agent owns technical operations inside the authorized local, reversible phase:

- investigate prerequisites and live repository state;
- define the smallest independently verifiable work slice;
- choose files, tests, fixtures, validators and rollback boundaries;
- detect QA triggers and classify findings;
- repair clear local `BLOCK` and `MUST` findings that stay inside scope;
- rerun focused and full verification;
- split and create local commits when phase-scoped commit authorization exists;
- maintain evidence, gaps, `CODE-QA.md` and handoff state.

The user owns intent, product direction, experiential acceptance, scope expansion, accepted blocker debt, sensitive-data access and external/irreversible effects. Do not turn internal engineering operations into repeated approval questions.

## WORK-SLICE — Define verifiable slices

Each `WORK-*` record should contain:

```text
workId
intent
userVisibleOutcome
ownedFiles
excludedFiles
behaviorContract
evidenceInputs
verification
rollbackBoundary
commitCandidate
qaTriggers
authorizationRequired
status
```

A good slice can be explained, tested and reverted independently. Keep behavior and its regression fixture together. Separate mechanical dependency/tooling changes, schema/contract changes, prose/localization, validator behavior and runtime adapters when their proof and rollback differ.

Update the slice when evidence changes assumptions. Do not keep working under a stale plan merely to avoid revising it.

## WORK-COMMIT — Apply intent-scoped commits

The agent decides commit grouping and messages. The user should not have to choose file-by-file staging.

Before each local commit:

1. verify the slice's behavior and negative cases;
2. inspect staged names and diff;
3. exclude unrelated worktree files and proprietary/private artifacts;
4. run `git diff --cached --check`;
5. ensure docs/contracts and implementation agree;
6. record any remaining explicit TODO and re-open trigger.

If phase-scoped local commit authorization was granted, create each planned small commit without asking again. Re-split automatically when dependency, verification or revert boundaries diverge.

Local commit authorization never implies push, PR, publication, release or deployment. Without commit authorization, complete the authorized implementation and verification, leave a precise commit plan, and report the verified worktree state instead of asking the user to design the split.

## QA-TRIGGERS — Open checkpoints automatically

Run a read-only Code QA checkpoint when evidence shows structural risk, including:

- first Mono/IL2CPP parser, proprietary parser or new dependency boundary;
- native DLL, reflection, Harmony patch, loader, process or speech transport;
- first long-running runtime UI observer, speech queue or input owner;
- persistent schema, compatibility fingerprint or migration policy;
- repeated fixes in focus, stale state, modal ownership, input routing, dynamic lists or generation invalidation;
- growing module combining extraction, I/O, state, policy and speech;
- untested orchestration, retry/cancellation or multi-process work;
- first real runtime, major milestone, PR, release or external publication.

Finish the current narrow slice or record its blocker, then inspect live code, tests, history, runtime evidence and explicit unknowns. Do not wait for the user to request QA.

## QA-FINDINGS — Classify by actionability

Use:

- `BLOCK`: proceeding can invalidate evidence, lose user data, mix builds, create unsafe runtime behavior, or make the current slice unreviewable.
- `MUST`: required before the current milestone/commit because the defect is inside scope and has a clear bounded fix.
- `FOLLOW-UP`: safe to defer because current guards are sufficient and an exact re-open trigger exists.
- `OBSERVATION`: uncertainty that needs measured evidence; not a speculative refactor request.

Each finding states evidence, user impact, current guard, smallest remedy/evidence, owner and re-open trigger. Do not create a vague backlog for the user.

## QA-AUTOMATIC-REPAIR — Repair within scope

For clear `BLOCK` or `MUST` findings inside the authorized local phase:

1. reproduce or prove the cause;
2. define the smallest repair slice;
3. add or update the regression fixture/test;
4. implement the repair;
5. rerun focused and full checks;
6. update finding and verdict;
7. commit under the existing phase-scoped authorization when applicable.

Do not ask whether to fix an obvious local defect merely because a checkpoint found it. Do ask before a broad redesign, product-behavior trade-off, new sensitive source, game/runtime side effect, accepted blocker debt, or another phase's work.

`FOLLOW-UP` does not require user approval when current safeguards are adequate. Carry it with a measurable trigger. `OBSERVATION` calls for evidence collection, not architecture churn.

## QA-USER-DECISION — Escalate only real user decisions

Ask the smallest question only when:

1. multiple product/user-experience directions remain legitimate;
2. the fix expands the authorized feature or refactor scope materially;
3. sensitive save/profile/cloud/account/network data must be accessed;
4. game launch, loader install, input injection, state mutation or destructive cleanup is required;
5. actual NVDA/keyboard usefulness or speech burden must be accepted by the user;
6. a blocker cannot be fixed and the maintainer must explicitly accept debt;
7. commit permission is absent and a commit is required, or push/PR/release/publication/deployment is proposed.

Present evidence, impact, recommendation and the exact next effect. Do not ask users to interpret internal coverage metrics or choose test frameworks.

## QA-REPORT — Report results, not management work

A checkpoint report should be concise:

```text
work slice closed
checks run and observed results
automatic repairs made
current verdict
remaining guarded TODOs
one user decision, only if required
actions not performed
```

Verdicts:

- `PROCEED`: current gates close.
- `PROCEED WITH TODOs`: remaining findings are guarded and trigger-bound.
- `DO NOT PROCEED`: unresolved blocker needs scope expansion, product decision, real acceptance or external effect.

A QA checkpoint is not authorization for broad refactoring, commit, push, PR, release, deployment or publication. It improves execution quality inside the user's existing authorization.

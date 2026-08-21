# Unity Accessibility Reconnaissance Code QA

상태: **PASS-WITH-TODOS**

검토 기준: 2026-08-22 KST, 0.3.0 release baseline

범위: agent-neutral bilingual skill package, shared contracts/templates, Python CLI·validator·exporter와 synthetic fixtures. 실제 게임 실행, loader/runtime adapter, 물리 키 입력과 NVDA 수동 acceptance는 범위 밖입니다.

## 1. 제품·사용자 품질 목표

1. 뒤늦은 UI 재조사를 줄이되, 첫 기능 전에 게임 전체 dump나 UI census를 요구하지 않습니다.
2. 각 조사 slice는 명확한 player goal, in-scope surface, out-of-scope area와 investigation budget을 갖습니다.
3. 현재 slice에 영향을 줄 수 있는 source family와 UI dependency만 먼저 조사하고, 구현이나 runtime evidence가 요구할 때 지도를 넓힙니다.
4. static finding, runtime observation, physical input, semantic postcondition, speech dispatch와 NVDA acceptance를 서로 대신하지 않습니다.
5. 중요한 offline claim에는 틀렸음을 보여줄 수 있는 `challengeTest`를 둡니다.
6. validator는 record consistency만 검사하며, 같은 agent가 만든 claim을 gameplay truth로 자기검증하지 않습니다.
7. 사용자가 schema를 읽지 않아도 player goal, offline finding, runtime finding, unknown, next test와 validator limit을 plain text로 확인할 수 있어야 합니다.
8. 영어·한국어 entry는 같은 stable ID, gate, artifact와 evidence rule을 유지합니다.
9. raw proprietary data, 실제 save/profile identity, 절대 사용자 path와 private runtime payload를 tracked artifact로 승격하지 않습니다.

## 2. Architecture와 상태 소유권

1. `skills/unity-accessibility-reconnaissance-en/`과 `skills/unity-accessibility-reconnaissance-ko/`는 별도로 발견 가능한 동일 의미 entry입니다.
2. `shared/phase-ids.yaml`은 phase ID, `claimGrade`, `coverageGate`, privacy class와 slice decision의 canonical registry입니다.
3. `shared/contracts/`의 7개 JSON schema가 persistent artifact 정본입니다.
4. `shared/templates/`의 8개 template가 조사·work·QA 기록의 시작점입니다.
5. `shared/bilingual-parity.yaml`은 paired document stable ID, heading level, required literal, link target과 registry drift 검증을 소유합니다.
6. `contracts.py`는 schema, canonical source-manifest digest와 build/source/coverage identity를 소유합니다.
7. `ledgers.py`는 build-bound UI ledger identity, surface/gap set, runtime coverage와 closure rule을 소유합니다.
8. `closure.py`는 named slice에 필요한 extraction family와 readiness decision을 계산합니다.
9. `cli.py`는 ledger와 in-scope surface의 연결을 검사하고 machine-readable JSON과 plain-language report를 출력합니다.
10. `exporter.py`는 두 standalone skill과 shared contracts/templates/registry/license를 복사하며 기존 target을 덮어쓰지 않습니다.
11. 실제 Unity runtime observer와 agent-specific adapter는 core와 분리된 후속 trust boundary입니다.

## 3. 0.3.0 현재 검증 증거

1. Python 3.14.3에서 full suite **60 tests passed**.
2. `uv run uar check-parity --root .`: `VALIDATION_PASS`.
3. `uv run python -m compileall -q src`: 통과.
4. `uv lock --check`와 `git diff --check`: 통과.
5. `uv build --clear`: 0.3.0 sdist와 `py3-none-any` wheel 생성 성공.
6. `twine check dist/*`와 `check-wheel-contents`: 통과.
7. 새 Python 3.14.3 venv에 wheel만 설치해 version 0.3.0, installed parity와 영한 standalone export를 확인했습니다.
8. 설치된 CLI의 static-only fixture가 `CONSISTENCY_CHECK PASS`, `READY FOR RUNTIME PROBE`, `INTERNAL-CONSISTENCY-ONLY`, offline finding, unknown, next test와 세 가지 limit을 출력했습니다.
9. wheel은 43 files이며 license와 영문·한국어 README를 포함합니다.
10. current tracked source에는 raw game file이나 private runtime log가 없습니다.
11. Windows 11의 새 Python 3.11.9 venv에 0.3.0 wheel을 설치해 version import와 CLI startup을 확인했습니다.
12. 같은 Windows 설치에서 bundled 영한 parity와 영어·한국어 standalone skill export가 통과했습니다.

### Windows package 증거의 경계

1. 0.2.0 wheel은 Windows 11, Python 3.11.9 clean install smoke를 통과했습니다.
2. 0.3.0은 readiness schema와 CLI behavior가 달라졌으므로 2026-08-22 KST에 별도 clean venv로 다시 검사했습니다.
3. Windows smoke는 package installation, import, CLI startup, installed parity와 standalone export를 검증하며 실제 game runtime behavior를 검증하지 않습니다.

이 검증은 새 게임의 runtime UI behavior, 실제 물리 키, speech 청취, 플레이 과업 완료 또는 모든 Unity/IL2CPP build 호환성을 증명하지 않습니다.

## 4. 외부 피드백을 반영한 설계 변경

공개된 기술 피드백에서 다음 위험을 추출했습니다.

1. 한 게임의 경험을 모든 Unity 게임에 일반화할 위험
2. 관련성이 생기기 전까지 필요하지 않은 조사를 front-load할 위험
3. agent가 대량 자료를 만들고 스스로 검증한 뒤 사용자가 확인하기 어려운 black-box workflow가 될 위험
4. offline finding을 live-game truth처럼 자신 있게 표현할 위험

0.3.0은 이를 다음과 같이 반영합니다.

1. whole-game census 대신 named player slice와 investigation budget을 사용합니다.
2. unrelated extraction failure는 현재 slice를 자동 차단하지 않습니다.
3. offline claim은 `challengeTest`를 가져야 하며 runtime probe 전에는 implementation-ready가 될 수 없습니다.
4. passed probe는 `challengedClaimIds`로 대상 claim을 지정하고 각 대상과 runtime evidence를 공유해야 합니다.
5. validator scope를 `INTERNAL-CONSISTENCY-ONLY`로 고정합니다.
6. decision을 `READY FOR RUNTIME PROBE`, `READY FOR SLICE IMPLEMENTATION`, `BLOCKED FOR THIS SLICE`로 나눕니다.
7. report가 offline finding, runtime finding, unknown, next test와 limit을 분리합니다.

## 5. Findings

### QA-1 — `RESOLVED`: whole-game frontloading

- 결과: extraction과 UI mapping을 named slice에 필요한 dependency로 제한했습니다.
- 보호 장치: out-of-scope reason, first-slice family, in-scope surface와 slice-local blocker를 schema와 validator가 검사합니다.
- 다시 여는 trigger: 새 workflow가 전체 menu/dump 완료를 첫 feature의 전제조건으로 만들 때.

### QA-2 — `RESOLVED`: agent self-validation과 과신

- 결과: consistency pass와 gameplay decision을 분리하고 validator의 한계를 모든 report에 표시합니다.
- 보호 장치: static claim의 `challengeTest`, explicit `challengedClaimIds`, probe/claim evidence intersection, open claim의 unknown 노출과 claimed-decision mismatch 차단 test.
- 다시 여는 trigger: 자동 observer나 LLM judge가 truth authority를 갖게 될 때.

### QA-3 — `RESOLVED`: 사용자 검토 가능성

- 결과: plain output에서 player goal, scope, finding, unknown, next test와 limit을 한 줄씩 제공합니다.
- 영향: 사용자는 raw schema 전체를 읽지 않고도 agent가 무엇을 알고 모르는지 확인할 수 있습니다.
- 다시 여는 trigger: 새 field가 JSON에만 추가되거나 report가 다시 단일 `done` 판정으로 축약될 때.

### QA-4 — `RESOLVED`: progressive readiness contract

- 결과: schema v2, template, registry, fixtures, closure logic, CLI와 영한 문서를 함께 변경했습니다.
- regression evidence: static-only, runtime-passed, failed probe, blocking gap, unrelated extraction failure, missing surface와 claimed-decision contradiction을 test합니다.
- 다시 여는 trigger: claim grade, coverage gate, source family 또는 decision model 변경.

### QA-5 — `RESOLVED`: 0.3.0 Windows-native package smoke

- 결과: Windows 11의 새 Python 3.11.9 venv에서 release wheel 설치, version import, CLI startup, installed parity와 영한 export를 실행했습니다.
- 보호 장치: 각 release wheel은 WSL의 source/build 검사와 별개로 Windows clean-install smoke를 수행합니다.
- 다시 여는 trigger: package resource layout, Python requirement, dependency 또는 entry-point 변경.

### QA-6 — `FOLLOW-UP`: 실제 게임 runtime evidence

- 영향: synthetic fixture는 report structure를 검증하지만 offline claim이 실제 게임에서 맞는지 증명하지 않습니다.
- 현재 완화: challenge test와 runtime probe를 implementation decision의 일부로 요구합니다.
- 가장 작은 다음 경계: 사용자가 승인한 game-specific slice에서 한 개 falsifiable runtime probe를 실행하고 claim을 갱신.

### QA-7 — `FOLLOW-UP`: 실제 IL2CPP end-to-end evidence

- 영향: contract는 IL2CPP source family를 표현하지만 실제 IL2CPP artifact로 전체 흐름을 실행하지 않았습니다.
- 현재 완화: Mono/IL2CPP family와 absent/mixed/unsupported 상태를 분리합니다.
- 가장 작은 다음 경계: 사용자가 소유·승인한 sanitized IL2CPP summary로 read-only dry-run.

### QA-8 — `FOLLOW-UP`: agent consumer discovery

- 영향: standalone export 성공은 Hermes, Codex 또는 다른 agent가 실제 skill root에서 discovery했다는 증거가 아닙니다.
- 현재 완화: core와 export는 agent-neutral이며 self-contained합니다.
- 가장 작은 다음 경계: 사용자가 지정한 agent/profile 하나에 별도 local install·discovery smoke.

### QA-9 — `OBSERVATION`: runtime adapter 의도적 부재

- core는 게임 실행, loader, input injection 또는 speech transport를 선택하지 않습니다.
- 실제 adapter를 추가하면 native/process/privacy/runtime-state ownership QA checkpoint를 새로 엽니다.

## 6. 허용된 부채

1. 별도 lint/type-check dependency는 현재 추가하지 않습니다. 60개 contract/CLI/export/distribution regression test와 compile check를 사용합니다.
2. 실제 runtime UI observer, native input과 NVDA acceptance는 game-specific approved phase에서 수행합니다.
3. active agent profile에 skill을 자동 설치하지 않습니다.

## 7. 자동 변경·commit gate

모든 변경:

1. focused test와 full `uv run pytest`
2. `git diff --check`, compile과 lock check
3. schema/YAML/Markdown structure 검증
4. changed behavior와 regression fixture 동시 변경
5. unrelated worktree file 배제

Bilingual prose:

1. stable ID 순서와 heading level parity
2. shared artifact link와 required literal parity
3. 기술 식별자 보존
4. 양쪽 언어 같은 intent 변경

Persistent contract/validator:

1. static-only, runtime-passed, failed-probe, blocking, mixed-build와 contradiction fixture
2. deterministic report와 nonzero slice-blocked exit
3. wheel rebuild와 clean install smoke

## 8. QA 재개 trigger

1. source family, record unit, claim grade, coverage gate, decision 또는 schema 변경
2. parser/dependency/native DLL/reflection/loader/process boundary 추가
3. stateful runtime UI observer, speech queue, input owner 또는 save/profile 접근 추가
4. 실제 game/IL2CPP dry-run이 core assumption을 바꿈
5. agent profile 설치 구조 또는 package resource layout 변경
6. release, PR, publication 또는 broad adapter integration 준비

## 9. 권한 경계

이 QA baseline은 active agent profile 설치, game 실행, loader 설치, input injection, save/profile/cloud 접근·변경, commit, push, PR, release, deployment, package-index publication 또는 repository visibility 변경을 승인하지 않습니다.

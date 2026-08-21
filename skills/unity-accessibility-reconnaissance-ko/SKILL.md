---
name: unity-accessibility-reconnaissance-ko
description: Unity 화면 읽기 게임 모드의 초기 조사에 사용합니다.
version: 0.3.0
language: ko
license: MIT
---

# Unity 접근성 모드 초기 조사

## POLICY-AGENT-NEUTRAL — 핵심 계약

Unity 기반 화면 읽기 접근성 모드에서 다음으로 작고 의미 있는 player slice를 조사할 때 이 스킬을 사용합니다. 최소한의 build·원본 보존 기준선을 세우고, 해당 slice를 바꿀 수 있는 의존성만 조사하며, 중요한 offline 가정을 작은 runtime test로 확인합니다. 구현이나 live test에서 실제 의존성이 드러날 때 evidence map을 넓히고, 유용한 작업 전에 게임 전체 조사를 요구하지 않습니다.

절차는 agent-neutral입니다. 도구 adapter는 파일 인벤토리, hash, 관리 코드 검사, Unity asset 읽기, runtime 관찰, native input 전달과 speech dispatch 같은 capability를 연결할 수 있습니다. claim grade, coverage gate, schema 또는 권한 경계를 바꾸면 안 됩니다. phase ID, `claimGrade`, `coverageGate`, privacy class와 verdict의 정본은 `shared/phase-ids.yaml` 또는 exported skill의 `references/phase-ids.yaml`입니다.

## POLICY-AGENCY — 플레이어와 사용자의 주체성

전맹 플레이어가 계속 직접 플레이합니다. 의미 있는 상태와 명시적 조작을 제공하고, 대화·유닛·대상·경로·구매처럼 결과가 중요한 선택을 조용히 대신하지 않습니다. 시각적 scraping이나 agent가 새로 만든 대체 gameplay보다 게임 소유 text, localization, input, callback과 관찰 가능한 postcondition을 우선합니다.

전맹 사용자는 시각적 UI 조사자나 프로젝트 QA 관리자가 아닙니다. agent가 구조·runtime 관찰 근거를 수집하고, 검증 종류와 work/commit 경계를 정하며, 승인 범위 안의 명백한 local finding을 수정해야 합니다. 제품 방향, 범위 확대, 민감정보 접근, 실제 화면 읽기·키보드 acceptance, blocker 부채 수용 또는 외부·비가역 효과가 필요할 때만 사용자에게 묻습니다.

## POLICY-EVIDENCE — Claim grade와 coverage gate

새 근거 없이 한 등급을 다음 등급으로 승격하지 않습니다. `claimGrade`는 artifact가 주장할 수 있는 가장 강한 사실 수준이고, `coverageGate`는 UI surface가 lifecycle 검증에서 도달한 단계입니다. 한 taxonomy를 다른 taxonomy로 변환하지 않습니다.

1. `SOURCE-IDENTIFIED`: 정확한 원본과 build identity를 기록했습니다.
2. `STATIC-CONFIRMED`: 선언한 추출 범위에서 code, asset, localization, callback 또는 binding이 존재합니다.
3. `RUNTIME-OBSERVED`: 키보드 조작 가능성을 주장하지 않고 현재 runtime owner, state 또는 transition을 관찰했습니다.
4. `PHYSICAL-INPUT-PROVEN`: 실제 키가 의도한 game-owned input 경로를 통과했습니다.
5. `POSTCONDITION-PROVEN`: 의도한 semantic game state가 정확히 한 번 변경됐습니다.
6. `SPEECH-DISPATCH-PROVEN`: speech transport가 정확한 event를 받아들였습니다. 사용자가 들었다는 증거는 아닙니다.
7. `NVDA-MANUAL-CONFIRMED`: 사용자가 관련 발화와 키보드 경로를 실제로 듣고 수용했습니다.
8. `OPEN / DYNAMIC-UNVERIFIED`: 근거가 없거나 조건부·parser 제한·오래된 build에 속합니다.

각 gate를 닫기 전에 [dump와 원본 대조](references/dump-and-source-reconciliation.md), [UI 표면·수명주기 coverage](references/ui-surface-and-lifecycle-coverage.md), [agent 소유 작업·Code QA](references/agent-owned-work-and-code-qa.md)를 읽습니다.

## G0-AUTHORIZATION — 조사 경계 고정

제품, 소유권·승인 근거, 허용된 원본 위치, 금지 데이터와 현재 실행 상한을 기록합니다. 읽기 전용 검사와 게임 실행, loader 설치, input injection, save/profile/cloud 변경, commit, push, 게시와 release를 분리합니다.

소유권이 불명확하거나, 정책이 의도한 mod 표면을 막거나, 민감정보가 필요하거나, 다음 행동이 현재 권한 상한을 넘을 때만 중단하고 묻습니다. 이미 승인된 가역적 읽기 전용 단계마다 확인을 요구하지 않습니다.

### ART-AUTHORIZATION-RECORD — 권한 기록

다음을 기록합니다.

- 정확한 제품과 배포판
- repository와 설치 build의 소유 관계
- 허용된 읽기 전용 root
- 민감·독점 원본 제외 범위
- 별도 승인된 runtime action
- 현재 commit과 외부 효과 권한

권한 상태는 `CLOSED` 또는 `BLOCKED`입니다. 이는 구현 준비 판정이 아닙니다.

## G1-BASELINE — build와 원본 identity 고정

추출 전에 exact build fingerprint를 만듭니다. 제품·build version, Unity version, Mono 또는 IL2CPP backend, architecture, loader 후보와 핵심 원본 파일의 hash·size를 포함합니다. 원본의 mutable/immutable root를 분리해 조사 전후 보존 검사를 정의합니다.

다른 patch, platform, backend, parser version 또는 설치 artifact의 근거를 섞지 않습니다. build가 바뀌면 새 fingerprint를 열고 이전 근거 중 구조적으로 재사용할 수 있는 범위를 명시적으로 판정합니다.

### ART-BUILD-FINGERPRINT — build fingerprint

repository의 `shared/contracts/build-fingerprint.schema.json`을 사용합니다. standalone export에는 같은 파일이 `references/contracts/build-fingerprint.schema.json`으로 포함됩니다. 다른 build의 extraction이나 runtime 증거가 들어오면 fail closed할 만큼 identity를 기록해야 합니다.

### ART-SOURCE-MANIFEST — source manifest

repository의 `shared/contracts/source-manifest.schema.json`을 사용하며 exported skill에서는 `references/contracts/source-manifest.schema.json`을 사용합니다. 모든 예상 source family를 `extracted`, `partial`, `excluded-with-reason`, `unsupported`, `failed`, `not-present` 중 하나로 분류하고, 해당할 때 근거와 사유를 기록합니다. 한 family 안에 성공·실패 target이 함께 있으면 `partial`을 사용하고 성공으로 뭉개지 않습니다. 조사 전후 preservation digest도 기록합니다.

## G2-EXTRACTION — 원본 추출 결과 대조

추출 도구를 실행하기 전에 질문, source family와 조사 budget을 선언합니다. 이름 붙인 slice에 필요한 가장 작은 source set부터 시작합니다. finding이나 runtime test에서 의존성이 드러날 때만 넓힙니다. 더 넓은 diagnostic census는 선택 사항이며 기본 entry gate가 되어서는 안 됩니다.

관련될 때 검토할 수 있는 source family는 다음과 같습니다.

- player executable과 Unity player/runtime identity
- Mono assembly 또는 IL2CPP binary와 metadata
- global manager와 serialized setting
- scene, prefab, resource, asset bundle과 존재할 때 addressable catalog
- localization table과 runtime localization owner
- old/new Input System asset, fixed hotkey와 input-router code
- managed type, method, inheritance, serialized callback과 dynamic/reflection/instantiate hint
- mutable save, profile, setting, cloud root와 log는 보호 대상 인벤토리로만 다루고 tracked fixture에 포함하지 않음

선언한 범위 안의 성공, 제외, 미지원, parser 실패와 unresolved 항목을 셉니다. 산출물이 많다고 완전한 dump가 아니며, 완전한 dump라고 자동으로 유용한 것도 아닙니다. 현재 질문을 정직하게 test할 수 있으면 추출을 멈춥니다.

### ART-EXTRACTION-COVERAGE — extraction coverage

repository의 `shared/contracts/extraction-coverage.schema.json`을 사용하며 exported skill에서는 `references/contracts/extraction-coverage.schema.json`을 사용합니다. `DUMP-READY`는 하나의 build identity, 선언한 범위, 대조된 count, deterministic output 또는 명시적 비결정성 사유, preservation 성공과 first slice를 막는 숨은 failed family가 없음을 요구합니다.

`DUMP-PARTIAL`은 정직한 판정입니다. 각 gap에 owner, 증거 영향과 제한된 re-open trigger가 있을 때만 진행할 수 있습니다.

## G3-STATIC-DISCOVERY — UI discovery set 작성

현재 slice에 영향을 주는 UI element, interactable candidate, localization link, callback과 input action ledger를 만듭니다. 원본 근거와 confidence를 보존하고 이를 하나의 player-facing list로 평탄화하거나 ledger를 채우기 위해 관련 없는 surface를 검색하지 않습니다.

선택한 evidence envelope 안에서 inactive template, pooled object, dynamic generation hint, pointer-only candidate와 unresolved script type을 포함해 관련 누락을 드러냅니다. 이들은 active runtime control이 아니라 discovery evidence입니다.

### ART-STATIC-UI-LEDGER — 정적 UI ledger

각 record는 `references/contracts/static-ui-ledger.schema.json`을 따릅니다. artifact는 foundation bundle의 `buildFingerprintId`를 반드시 사용하며 `templates/static-ui-ledger.json`에서 시작합니다.

범위 안에서 발견된 candidate는 semantic candidate, 명시적 제외 또는 gap에 귀속되어야 합니다. control 존재는 visibility, focus, keyboard action이나 task completion을 증명하지 않습니다.

## G4-LIFECYCLE-MAP — slice 의존성 지도를 점진적으로 확장

하나의 player goal에서 시작합니다. 다음만 지도화합니다.

- 진입 경로와 의도한 완료 상태
- 현재 slice가 직접 사용하는 surface
- slice를 무효화할 수 있는 인접 modal, error, cancel과 restoration 경로
- static evidence나 runtime probe에서 이미 드러난 conditional dependency

관련 없는 family는 이유와 함께 짧은 out-of-scope 목록에 둡니다. 선택한 slice에 들어오기 전에는 자세히 조사하지 않습니다. 범위 안의 각 surface에 entry/exit predicate, runtime owner candidate, modal depth, required/optional control, initial focus, child transition, parent restoration, 전문 interaction model, privacy class와 conditional content를 기록합니다.

### ART-SURFACE-LIFECYCLE-MATRIX — surface lifecycle matrix

화면 읽기 친화적인 companion과 `templates/surface-lifecycle-matrix.csv`를 사용합니다. 모든 row는 static UI ledger 및 foundation bundle의 `buildFingerprintId`를 반드시 사용하며, required ownership이 불명확하면 영향받는 slice만 막습니다. 이 matrix는 점진적인 dependency map이며 게임 전체 완료 주장이 아닙니다.

## G5-RUNTIME-COVERAGE — active owner와 control 관찰

runtime 작업은 별도 권한 경계입니다. opt-in이며 발화하지 않는 observer부터 시작합니다. global object enumeration보다 게임의 current/top UI stack, panel/window ownership, active/enabled/interactable state, `CanvasGroup` eligibility, `EventSystem` selection과 game-owned default/last focus를 우선합니다.

surface generation을 모델링합니다. owner와 semantic value가 안정된 뒤 진입하고, child modal이 input을 소유할 때 inactive parent를 제외하며, close·scene change·death·respawn·replacement에서 cached Unity object를 무효화하고, game-owned parent focus 복원을 관찰합니다.

### ART-RUNTIME-COVERAGE — static-to-runtime coverage ledger

범위 안의 각 surface는 근거가 있는 gate까지만 승격합니다.

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

`COVERAGE-CLOSED`는 현재 의미 있는 모든 control이 semantic entry, 명시적 제외 또는 재현 가능한 gap에 귀속됐다는 뜻입니다. 모든 Unity component를 발화한다는 뜻이 아닙니다.

## G6-INPUT-POSTCONDITION — native input과 완료 증명

오염되지 않은 game-owned input 경로부터 관찰합니다. 명시적 diagnostic flag가 없으면 legacy accessibility key suppression, forced focus synchronization, broad Harmony interception과 generic cursor routing을 끕니다.

각 action의 precondition, physical key, input owner, selected/focused semantic identity, native callback과 resulting game state를 기록합니다. OS-level injection은 Unity/game observer가 확인할 때만 전달 근거가 됩니다. 호출 가능한 callback은 physical keyboard 지원이나 현재 pointer eligibility를 증명하지 않습니다.

native path가 없거나 사용할 수 없음이 드러난 뒤에만 surface-scoped semantic fallback을 추가합니다. 의도한 action을 성공처럼 발화하지 말고 하나의 관찰 가능한 postcondition을 요구합니다.

### ART-NATIVE-INPUT-MATRIX — native input·postcondition matrix

각 action을 native-proven, native-partial, pointer-only-proven, fallback-required, blocked 또는 open으로 분류합니다. modal ownership, repeat behavior, stale-target handling, destructive confirmation과 selection·camera·save·network·world state 변경 여부를 포함합니다.

## G7-FIRST-SLICE-READINESS — 첫 접근성 slice 선정

실제 ownership, semantic label, native input, postcondition, speech와 lifecycle restoration을 사용하는 가장 작은 user-meaningful path를 고릅니다. startup modal과 main title이 generic all-screen cursor보다 안전한 경우가 많지만, 실제 게임 dependency graph를 따릅니다.

slice는 다음 test 또는 구현 단계로 갈 때 다음 조건을 충족해야 합니다.

1. G0와 G1이 닫힘
2. G2가 해당 slice에 필요한 source family를 포함함. 관련 없는 extraction failure는 막지 않음
3. G3와 G4가 이름 붙인 in-scope surface와 직접 의존성을 선언한 confidence로 포함
4. 중요한 offline 가정마다 작은 runtime challenge test 존재
5. runtime probe가 `challengedClaimIds`를 명시함. 통과한 probe는 각 대상 claim을 해당 probe의 runtime-grade evidence에 연결
6. privacy, deployment rollback과 game/profile preservation 정의
7. agent-owned work, commit, verification과 Code QA gate 기록

### ART-GAP-LEDGER — gap ledger

각 gap에는 stable ID, 대상 build/surface, `claimGrade`, 사용자 영향, 현재 완화, 가장 작은 다음 근거, owner, blocking status와 re-open trigger가 필요합니다. “테스트가 더 필요함”만으로는 충분하지 않습니다.

### ART-FIRST-SLICE-READINESS — readiness 기록

schema version 2 record는 하나의 player goal, in-scope surface, out-of-scope area, claim, gap, runtime probe, Code QA status와 권한 경계를 기록합니다. `validationScope: INTERNAL-CONSISTENCY-ONLY`와 다음 slice-scoped decision 중 하나를 반드시 선언합니다.

- `READY FOR RUNTIME PROBE`: record가 일관되고 다음 반증 test가 정의됐습니다. offline finding은 runtime truth가 아닙니다.
- `READY FOR SLICE IMPLEMENTATION`: 기록된 runtime probe가 통과했고, challenged claim이 모두 `RUNTIME-OBSERVED` 이상이며, 각 대상이 해당 probe와 evidence를 공유합니다.
- `BLOCKED FOR THIS SLICE`: mixed build, preservation failure, 해당 blocker, 실패한 probe 또는 일관되지 않은 record가 남았습니다.

이 decision은 이름 붙인 slice에만 적용됩니다. 게임 전체 coverage나 manual NVDA acceptance를 증명하지 않습니다.

## CHECK-EVIDENCE-SEPARATION — claim 감사

보고 전에 모든 claim을 실제 등급에 연결합니다. build, schema validation, callback invocation, speech return code와 agent-driven sequence 성공을 manual keyboard/NVDA acceptance로 설명하면 안 됩니다. `SOURCE-IDENTIFIED`, `STATIC-CONFIRMED`, `OPEN / DYNAMIC-UNVERIFIED` slice claim마다 구체적인 challenge test가 필요합니다.

## CHECK-TRANSPARENCY — agent 자기검증 방지

validator는 contract shape, build binding, probe-to-claim evidence link, reference와 내부 일관성을 검사합니다. agent가 게임을 정확히 해석했는지는 증명할 수 없습니다. `VALIDATION_PASS`를 live gameplay의 진실로 보고하지 않습니다.

사용자에게 다음을 포함한 짧은 plain-language view를 제공합니다.

1. 현재 player goal과 in-scope surface
2. file에서만 확인한 finding
3. 실행 중인 게임에서 관찰한 finding
4. 해당 unknown과 blocker
5. 다음 test와 실패가 뜻하는 것
6. validator의 명시적 한계

## CHECK-USER-ROLE — 전맹 사용자 부담 감사

agent가 사용자에게 screen 시각 열거, screenshot 판독, Unity hierarchy 추론, test 종류 선택, commit 분할 또는 QA ledger 관리를 요구하지 않았는지 확인합니다. 사용자 작업은 정직하게 자동화할 수 없는 결정과 실제 경험 acceptance로 제한합니다.

## CHECK-REPORTING — 단계 보고

각 gate에서 다음을 보고합니다.

1. 이름 붙인 player goal과 정확한 slice 경계
2. offline finding, runtime finding, assumption과 unknown을 분리한 목록
3. 가장 작은 다음 test와 실패 의미
4. consistency check로만 설명한 contract 검사
5. 자동 수정과 Code QA status
6. 실제로 필요할 때만 가장 작은 사용자 결정
7. 실행하지 않은 행동, 특히 runtime, 민감정보, commit, push, 게시와 release 경계

## 피해야 할 패턴

- 한 개의 보이는 menu에서 시작해 generic cursor로 일반화
- 다음 작은 기능 전에 게임 전체 dump나 UI census 요구
- 같은 agent가 claim을 쓰고 형식을 검증한 뒤 gameplay fact로 보고
- `activeInHierarchy`, `interactable` 또는 callback 존재를 현재 player operability로 간주
- label을 얻으려고 hover/click/selection method 호출
- 다른 build의 parser output 또는 runtime log 혼합
- aggregate success count 안에 parser failure 숨김
- localization·semantic owner가 있는데 object name을 최종 player label로 사용
- game-owned initial selection을 관찰하기 전에 focus 강제
- internal commit마다 사용자 승인을 요구하거나 명백한 local QA finding의 해결 방식을 사용자에게 선택시킴
- 특정 agent 도구를 core 절차의 필수 조건으로 만듦

## 최종 산출물

간결하고 화면 읽기 친화적인 단계 보고와 machine-readable artifact를 만듭니다. 정확한 ID, path, hash, command, schema key, claim grade와 coverage gate를 보존합니다. proprietary/raw evidence는 tracked skill content 밖에 둡니다.

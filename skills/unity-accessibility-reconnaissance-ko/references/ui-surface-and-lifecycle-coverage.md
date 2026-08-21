# UI 표면·수명주기 Coverage

## UI-DISCOVERY — discovery와 eligibility 분리

정적 추출은 superset을 만듭니다. live control, inactive parent, template, prefab instance, pooled object, decorative text, debug screen, stale tag, pointer-only hit target과 unresolved script가 함께 포함될 수 있습니다. 이 차이를 보존합니다.

권장 static artifact와 record field:

- foundation bundle에 결속된 최상위 `buildFingerprintId`
- stable candidate ID, UI hierarchy와 owner type
- uGUI/TMP/UI Toolkit/custom control family
- rendered/serialized text와 localization key/source
- `Selectable`, submit/cancel, pointer, drag/drop, slider/toggle/tab/input behavior
- serialized·managed callback
- input action/binding과 fixed-key evidence
- active/default/template/pool/dynamic hint
- privacy class, confidence와 unresolved reason

global enumeration은 diagnostic census에는 사용할 수 있지만 player-facing eligibility rule이 아닙니다.

## UI-FAMILIES — 현재 slice의 dependency path 추적

하나의 player goal에서 시작해 해당 경로에 진입하고, 완료하고, 취소하고, 실패하고, 원래 상태로 복원하는 데 필요한 surface만 inventory합니다. static evidence나 runtime observation에서 현재 slice에 영향을 줄 수 있음이 드러난 경우에만 인접 modal·conditional surface를 포함합니다.

나머지 family는 짧은 out-of-scope 목록에 둡니다. options, save, multiplayer, HUD, inventory, map, ending, DLC 또는 game-specific system이 존재할 수 있다는 이유만으로 열거하지 않습니다. 선택한 feature, implementation finding 또는 live test에서 관련성이 드러날 때 dependency map으로 승격합니다.

현재 slice 안에서 접근할 수 없거나 도달하지 못한 조건에는 dependency와 가장 작은 미래 observation plan을 기록합니다. 해당 unknown을 조용히 누락하지 않습니다.

## UI-OWNERSHIP — 현재 state owner 명명

게임이 소유한 다음 출처를 찾습니다.

- current/top panel, window, control stack 또는 state machine
- open/enabled/control-enabled/interactable state
- `CanvasGroup` alpha/interactable/blocks-raycasts
- `EventSystem.current.currentSelectedGameObject`
- default/last selected control
- child modal open/close와 parent disable/restore behavior
- semantic value와 action readiness
- input map 또는 gameplay router ownership

`activeInHierarchy=true`만으로는 약합니다. 여러 병렬 UI root가 active인 상태에서 하나만 input을 받을 수 있습니다. 보이는 child가 active parent를 억제할 수 있습니다. retained object는 alpha 0, disabled raycast, stale backing state 또는 semantic readiness 부재 상태일 수 있습니다.

게임의 owner stack을 먼저 사용하고 global filter는 보강 근거로만 사용합니다.

## UI-GENERATION — lifecycle 명시적 모델링

top semantic owner가 열리거나 교체되거나 새로운 backing state로 재진입할 때 새 `surfaceGeneration`을 부여합니다.

lifecycle:

1. `enter`: owner candidate를 관찰하고 고정 지연이 아니라 stable semantic readiness를 기다림
2. `initial-focus`: 무엇도 설정하기 전에 game-owned selection 관찰
3. `focus/value`: 안정된 identity, role, label, value와 state를 한 번 publish
4. `child-open`: child가 speech/input owner가 되고 parent entry와 stale queued speech 억제
5. `child-close`: native restoration을 관찰하고 복원된 context를 한 번 발화
6. `replace/scene-change`: cached Unity reference, candidate, route와 pending announcement 무효화
7. `error/cancel`: agent 추측이 아니라 실제 game owner에 따라 state 보존 또는 정리

generation 없는 Unity object identity는 pooling, scene replacement와 dynamic-list refresh를 안전하게 견디지 못합니다.

## UI-SNAPSHOT — semantic snapshot 사용

최소 runtime snapshot:

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

label 우선순위:

1. game semantic/localization API
2. rendered TMP/uGUI text
3. control-specific value owner
4. associated parent/child label
5. diagnostic object name이며 fallback임을 명시

label을 읽기 위해 hover, click, selection-change, animation, material 또는 game-state method를 호출하지 않습니다. sensitive text는 명시적으로 focus됐을 때 local speech로 보낼 수 있지만 log에는 redacted identity, type과 length만 둡니다.

## UI-INPUT — 전문 interaction model 보존

모든 표면을 Up/Down/Enter로 평탄화하지 않습니다.

- button/list: native next/previous와 submit/cancel
- slider/toggle/radio/tab: native value와 state semantic
- text input/IME: editing mode, composition, confirm/cancel과 privacy
- rebind: listening state, conflict, cancel/reset과 native device ownership
- inventory/grid: row/column, item identity, detail, drag/drop과 rotation
- map: node/candidate identity, current selection, locked state, preview와 activation 구분
- world interaction: semantic target, navigation point, interaction readiness와 observable completion

mod-owned suppression과 focus forcing을 끈 상태로 physical input을 먼저 관찰합니다. QA callback은 lifecycle을 증명할 수 있지만 physical-key UX는 증명하지 못합니다. fallback이 필요하면 하나의 active owner와 하나의 explicit user command로 제한합니다.

## UI-CLOSURE — coverage를 정직하게 닫기

각 surface family는 다음 gate를 유지합니다.

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

family는 다음 조건에서만 `COVERAGE-CLOSED`입니다.

1. required active control에 semantic entry 존재
2. optional/conditional absence 설명
3. decorative/template/debug/stale item에 명시적 제외 사유
4. dynamic·pointer-only case에 제한된 disposition
5. 해당할 때 child-modal과 parent-restore lifecycle 검증
6. native input·postcondition claim이 실제 증거와 일치
7. 사용자가 확인한 경우에만 manual NVDA claim 존재
8. 남은 gap에 재현 조건과 re-open trigger 존재

slice lifecycle mapping이 충분해도 나머지 게임은 의도적으로 unknown일 수 있습니다. `COVERAGE-CLOSED`는 이름 붙인 surface와 evidence envelope에만 적용되며 게임 전체 verdict가 아닙니다.

## UI-REOPEN — 광범위한 재조사 방지

다음 상황에서 영향받는 evidence envelope만 다시 엽니다.

- build 또는 관련 source hash 변경
- parser/schema/adapter version 변경
- 새 surface owner, control family, localization source 또는 input router 등장
- required runtime control이 static ledger에 없음
- static candidate를 runtime에서 귀속할 수 없음
- game update로 lifecycle, modal ownership, focus restoration 또는 postcondition 변경
- 반복 stale speech/focus bug가 잘못된 generation model을 드러냄
- 사용자 acceptance에서 누락·중복·오도·사용 불가 output 발견
- 새 profile/DLC/multiplayer/progression 조건이 미지도 surface를 활성화

build/type/scene/source-to-surface dependency link로 가장 작은 re-open set을 고릅니다. label 하나가 바뀌었다고 모든 dump를 반복하지 않고, aggregate count가 같다는 이유로 stale closure verdict를 유지하지도 않습니다.

# Dump와 원본 대조

## DUMP-SCOPE — 증거 envelope 선언

추출 전에 정확한 질문을 정의합니다. 어느 설치 build, backend, platform, content root, UI system, localization source, input system과 dynamic generation mechanism을 조사하는지 명시합니다. envelope는 다음을 구분해야 합니다.

- 존재하며 성공적으로 추출한 원본
- 조사했지만 의도적으로 제외한 원본
- 지원하지 않는 format 또는 parser limitation
- extraction failure
- 예상했으나 부재를 확인한 family
- preservation 목적으로만 inventory한 mutable user data

선언한 envelope 없이 “full dump”라고 부르지 않습니다. `declared scope 아래 DUMP-READY` 또는 `DUMP-PARTIAL`을 사용합니다.

## DUMP-FINGERPRINT — 모든 artifact를 하나의 build에 귀속

fingerprint는 다음을 포함해야 합니다.

1. 제품·배포 식별자와 exact build/version
2. 신뢰할 수 있는 metadata에서 얻은 Unity version
3. Mono 또는 IL2CPP backend와 process architecture
4. platform과 관련 DLC/content set
5. 핵심 파일의 relative path, size, SHA-256과 필요할 때 modification metadata
6. 설치하지 않은 상태의 loader 후보와 compatibility status
7. source-manifest digest 또는 stable identity. shared contract에서는 key를 정렬하고 불필요한 공백을 제거한 canonical JSON을 UTF-8로 인코딩해 SHA-256을 계산합니다.

이후 모든 manifest, ledger, report, runtime run과 acceptance record가 fingerprint ID를 반복합니다. validator는 다른 ID가 섞이면 거부해야 합니다.

patch나 content update가 발생하면 새 fingerprint를 엽니다. 이전 type name이나 note는 새 build가 확인하기 전까지 조사 질문 생성에만 사용합니다.

## DUMP-SOURCE-FAMILIES — 도구를 고르기 전에 inventory

### Mono build

최소한 다음을 inventory합니다.

- `*_Data/Managed/*.dll`과 assembly dependency
- player executable과 `UnityPlayer.dll`
- `globalgamemanagers`, `globalgamemanagers.assets`, `resources.assets`, shared asset, scene container, bundle과 catalog
- configuration과 boot metadata
- localization table/resource
- Input Manager, Input System action asset과 input-router code
- game-owned UI manager, panel/window base, `EventSystem`, selection owner, callback path와 state model

### IL2CPP build

다음을 추가합니다.

- `GameAssembly.dll` 또는 platform equivalent
- `global-metadata.dat`
- 생성·복원한 type/method metadata
- stripped/obfuscated/unresolved method와 type 집계
- parser-tool version과 reconstruction confidence

### Dynamic·전문 UI

다음을 찾습니다.

- `Instantiate`, addressable, reflection, object pool, generated list/grid와 runtime localization
- uGUI, TextMeshPro, UI Toolkit, legacy IMGUI, custom mesh/collider UI와 world-space canvas
- pointer interface, raycast order, submit/cancel handler, fixed hotkey, rebind flow와 gameplay input router
- static default-state asset에서 드러나지 않을 수 있는 network, progression, DLC, save-state, boss/ending과 conditional surface

검색 hit가 없다는 사실은 runtime 부재 증명이 아닙니다. 검색 범위와 confidence를 기록합니다.

## DUMP-PARSER-IDENTITY — 재현 가능한 extraction

각 extractor에 다음을 기록합니다.

- tool name, version, source/release URL 또는 package lock과 가능한 경우 executable/package hash
- command line 또는 deterministic invocation parameter
- input fingerprint와 exact output root
- parser warning, unreadable object, unresolved script type, decompile failure와 fallback tool
- output normalization, canonical ordering, encoding과 제거한 nondeterministic field
- license와 redistribution boundary

디컴파일한 source나 독점 serialized payload를 commit하지 않습니다. schema, synthetic fixture, compact sanitized summary와 hash를 추적합니다.

fallback parser가 primary parser failure를 없애지는 않습니다. 두 finding을 gap ledger에 보존하고 fallback이 실제로 증명한 범위를 적습니다.

## DUMP-RECONCILIATION — disposition 완결성 증명

각 family에 다음을 계산합니다.

```text
discovered = extracted + excluded + unsupported + failed + not-present
```

`not-present`는 해당 family 자체가 적용되지 않거나 부재를 확인했을 때만 사용합니다. 읽지 못한 항목을 숨기는 데 사용하지 않습니다.

source family summary 수준에서는 최소 한 target이 extracted이고 다른 target이 excluded, unsupported 또는 failed이면 disposition `partial`을 사용합니다. 위 per-target count를 그대로 보존하며 `partial`은 추가 count bucket이 아니라 summary state입니다. `recordCount`는 evidence가 표현하는 성공 추출 수입니다. `extracted` 또는 `partial` summary에서는 coverage `extracted`와 같고, 다른 summary disposition에서는 0입니다.

유용한 수준마다 대조합니다.

- file과 container
- scene/prefab/asset
- GameObject와 MonoBehaviour instance
- managed type/method/inheritance
- UI candidate와 Selectable
- callback과 input binding
- localization file, key와 UI link
- unresolved type, dynamic candidate, pointer-only candidate와 parse/decompile failure

count는 discovery control이지 player-accessibility 완료율이 아닙니다. button candidate가 천 개라고 해서 player-facing entry가 천 개 필요한 것은 아닙니다.

가능하면 같은 normalized extraction을 두 번 실행합니다. byte equality가 가장 강하며, 불가능하면 canonical semantic record를 비교하고 volatile metadata를 설명합니다.

## DUMP-PRESERVATION — 원본과 사용자 상태 보호

runtime이나 loader 작업 전에 다음을 수행합니다.

1. immutable installed-game source inventory
2. mutable save, profile, setting, `LocalLow`, cloud, mod-loader와 log root를 별도 inventory
3. 추가·변경·삭제될 수 있는 path 선언
4. 명시적 삭제·복원 승인이 없으면 user-authored data 보존
5. 선언한 immutable set의 pre/post size, hash, count와 modification metadata 비교
6. 예상하지 않은 원본 변경 시 즉시 중단

읽기 전용 extraction은 게임을 실행하거나 loader를 설치하지 않아야 합니다. tool에 writeable working copy가 필요하면 ignored/external evidence root로 복사하고 origin hash를 보존합니다.

## DUMP-PRIVACY — tracked evidence 최소화

save name, profile name, room code, IP address, chat/free text, absolute user path, account ID, cloud metadata와 speech payload는 반증이 없으면 sensitive로 분류합니다.

tracked artifact에 포함할 수 있는 것:

- opaque synthetic identity
- relative source family와 type/category
- count, hash, schema, confidence와 gap reason
- 작은 non-proprietary hand-authored fixture

tracked artifact에 포함하면 안 되는 것:

- game binary 또는 추출한 source/asset
- 실제 save/profile name 또는 backing filename
- raw log, screenshot, audio, texture, mesh, localization corpus 또는 decompiled code
- credential, token, account/network identifier 또는 개인 absolute path

### DUMP-PRIVACY-TIERS — 3단계 evidence tier

세 가지 저장 tier를 명시적으로 유지합니다.

1. **Tier 1 — raw working evidence:** 원본 hash와 접근 경계를 가진 ignored 또는 external root의 proprietary source copy와 상세 extraction output
2. **Tier 2 — normalized external evidence:** canonical ledger, replay input과 상세 report처럼 game content를 재구성하거나 private value를 노출할 수 있어 version control 밖에 두는 자료
3. **Tier 3 — tracked privacy-minimal evidence:** schema, synthetic fixture, opaque build binding, count, digest, bounded gap과 재구성 불가능한 최소 product data

tier 간 승격은 bulk copy가 아니라 allowlist 방식으로 수행합니다. 가능하면 independent validator 또는 byte-identical replay가 upstream hash에서 Tier 3 output을 재도출해야 합니다. privacy check 통과는 static geometry, label 또는 envelope를 runtime membership, navigation, operability나 user acceptance로 승격하지 않습니다.

## DUMP-VERDICT — extraction gate 닫기 또는 이월

`DUMP-READY`는 다음을 요구합니다.

1. 하나의 accepted build fingerprint
2. 선언한 모든 source family의 disposition
3. count reconciliation
4. parser/tool identity와 warning 기록
5. original preservation 통과
6. deterministic replay 통과 또는 제한된 variance 설명
7. 명시적 runtime 계획 없이 first slice를 무효화할 수 있는 failed/unsupported/unresolved item이 없음
8. 남은 unknown의 완전한 gap ledger

first slice가 영향받지 않고, gap이 fail closed이며, 정확한 re-open trigger를 알면 `DUMP-PARTIAL`로 진행할 수 있습니다. mixed build, preservation failure, 설명되지 않은 count loss, parser trust unknown 또는 first-slice source blocker에는 `DO NOT PROCEED`를 적용합니다.

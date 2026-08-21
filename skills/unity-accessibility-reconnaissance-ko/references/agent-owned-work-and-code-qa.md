# Agent 소유 작업과 Code QA

## WORK-OWNERSHIP — Agent-owned execution, user-governed boundaries

승인된 local·가역 phase 안의 기술 운영은 agent가 소유합니다.

- prerequisite와 live repository state 조사
- 독립적으로 검증 가능한 가장 작은 work slice 정의
- file, test, fixture, validator와 rollback boundary 선택
- QA trigger 감지와 finding 분류
- 범위 안의 명백한 `BLOCK`·`MUST` 수정
- focused·full verification 재실행
- phase-scoped commit 권한이 있을 때 local commit 분할·생성
- evidence, gap, `CODE-QA.md`와 handoff 관리

사용자는 intent, 제품 방향, 경험 acceptance, 범위 확대, blocker 부채 수용, 민감정보 접근과 외부·비가역 효과를 소유합니다. 내부 engineering 운영을 반복 승인 질문으로 바꾸지 않습니다.

## WORK-SLICE — 검증 가능한 slice 정의

각 `WORK-*` record는 다음을 포함해야 합니다.

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

좋은 slice는 독립적으로 설명·검증·revert할 수 있습니다. behavior와 regression fixture를 함께 둡니다. mechanical dependency/tooling, schema/contract, prose/localization, validator behavior와 runtime adapter는 증명·rollback 경계가 다르면 분리합니다.

근거가 가정을 바꾸면 slice를 갱신합니다. 계획 수정이 번거롭다는 이유로 stale plan 아래에서 계속 작업하지 않습니다.

## WORK-COMMIT — 의도 단위 commit 적용

commit grouping과 message는 agent가 결정합니다. 사용자가 파일별 staging을 선택하게 하지 않습니다.

각 local commit 전에:

1. slice behavior와 negative case 검증
2. staged name과 diff 검사
3. unrelated worktree file과 proprietary/private artifact 제외
4. `git diff --cached --check`
5. docs/contracts와 implementation 일치 확인
6. 남은 explicit TODO와 re-open trigger 기록

phase-scoped local commit 권한이 있으면 계획한 작은 commit마다 다시 묻지 않고 생성합니다. dependency, verification 또는 revert boundary가 갈리면 자동으로 재분할합니다.

local commit 권한은 push, PR, 게시, release 또는 deployment 권한이 아닙니다. commit 권한이 없으면 승인된 구현·검증을 완료하고 정확한 commit plan과 verified worktree state를 남기며, 사용자에게 분할을 설계하라고 묻지 않습니다.

## QA-TRIGGERS — checkpoint 자동 개방

다음처럼 구조 위험을 나타내는 근거가 있으면 읽기 전용 Code QA checkpoint를 실행합니다.

- 첫 Mono/IL2CPP parser, proprietary parser 또는 새 dependency boundary
- native DLL, reflection, Harmony patch, loader, process 또는 speech transport
- 첫 long-running runtime UI observer, speech queue 또는 input owner
- persistent schema, compatibility fingerprint 또는 migration policy
- focus, stale state, modal ownership, input routing, dynamic list 또는 generation invalidation의 반복 수정
- extraction, I/O, state, policy와 speech를 결합하며 커지는 module
- test되지 않은 orchestration, retry/cancellation 또는 multi-process work
- 첫 실제 runtime, major milestone, PR, release 또는 외부 게시

현재 좁은 slice를 닫거나 blocker를 기록한 뒤 live code, test, history, runtime evidence와 explicit unknown을 조사합니다. 사용자가 QA를 요청할 때까지 기다리지 않습니다.

## QA-FINDINGS — actionability로 분류

다음을 사용합니다.

- `BLOCK`: 진행하면 evidence 무효화, user data 손실, build 혼합, unsafe runtime behavior 또는 unreviewable slice가 발생할 수 있음
- `MUST`: defect가 현재 범위 안에 있고 명확한 제한된 수정이 있어 current milestone/commit 전에 필요
- `FOLLOW-UP`: 현재 guard가 충분하고 정확한 re-open trigger가 있어 안전하게 연기 가능
- `OBSERVATION`: 측정 근거가 필요한 uncertainty이며 speculative refactor 요청이 아님

각 finding에는 evidence, user impact, current guard, 가장 작은 remedy/evidence, owner와 re-open trigger를 둡니다. 모호한 backlog를 사용자에게 넘기지 않습니다.

## QA-AUTOMATIC-REPAIR — 범위 안 자동 수정

승인된 local phase 안의 명백한 `BLOCK` 또는 `MUST`는 다음 순서로 처리합니다.

1. 원인 재현 또는 입증
2. 가장 작은 repair slice 정의
3. regression fixture/test 추가·갱신
4. repair 구현
5. focused·full check 재실행
6. finding과 verdict 갱신
7. 해당할 때 기존 phase-scoped 권한으로 commit

checkpoint가 발견했다는 이유만으로 명백한 local defect를 고칠지 묻지 않습니다. broad redesign, 제품 behavior trade-off, 새 sensitive source, game/runtime side effect, blocker 부채 수용 또는 다른 phase 작업이 필요하면 묻습니다.

현재 safeguard가 충분한 `FOLLOW-UP`에는 사용자 승인이 필요하지 않습니다. 측정 가능한 trigger와 함께 이월합니다. `OBSERVATION`은 architecture 변경이 아니라 evidence collection을 요구합니다.

## QA-USER-DECISION — 실제 사용자 결정만 escalation

다음 경우에만 가장 작은 질문을 합니다.

1. 여러 제품·사용자 경험 방향이 모두 타당함
2. fix가 승인된 feature/refactor 범위를 실질적으로 확대함
3. sensitive save/profile/cloud/account/network data 접근 필요
4. game launch, loader install, input injection, state mutation 또는 destructive cleanup 필요
5. 실제 NVDA/keyboard 유용성이나 speech 부담을 사용자가 수용해야 함
6. blocker를 수정할 수 없어 maintainer의 명시적 debt 수용 필요
7. commit이 필요하지만 권한이 없거나 push/PR/release/게시/deployment를 제안함

evidence, impact, recommendation과 정확한 다음 효과를 제시합니다. internal coverage metric 해석이나 test framework 선택을 사용자에게 요구하지 않습니다.

## QA-REPORT — 관리 업무가 아니라 결과 보고

checkpoint report는 간결해야 합니다.

```text
닫은 work slice
실행한 검사와 관찰 결과
자동 수정 내용
현재 verdict
남은 guarded TODO
필요한 경우 한 가지 사용자 결정
실행하지 않은 행동
```

verdict:

- `PROCEED`: current gate 닫힘
- `PROCEED WITH TODOs`: remaining finding에 guard와 trigger 존재
- `DO NOT PROCEED`: unresolved blocker가 범위 확대, 제품 결정, 실제 acceptance 또는 외부 효과를 요구

QA checkpoint는 broad refactor, commit, push, PR, release, deployment 또는 publication 권한이 아닙니다. 사용자의 기존 권한 안에서 실행 품질을 높입니다.

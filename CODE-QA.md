# Unity Accessibility Reconnaissance Code QA

상태: **PROCEED WITH TODOs**

검토 기준: 2026-08-21 KST, 비식별화된 0.2.0 공개 준비 source state

범위: agent-neutral bilingual skill package, shared contracts/templates, Python CLI·validator·exporter, synthetic fixtures와 비식별화된 project-summary contract 점검. 실제 새 게임 실행, loader/runtime adapter, 물리 키 입력과 NVDA 수동 acceptance는 범위 밖입니다.

## 1. 제품·사용자 품질 목표

1. 전맹 사용자가 inaccessible UI를 시각적으로 재조사하거나 commit·test·QA 운영을 직접 설계하지 않아도 됩니다.
2. exact build identity, source preservation과 declared extraction scope 없이 dump 완료를 주장하지 않습니다.
3. static, runtime owner, physical input, semantic postcondition, speech dispatch와 NVDA acceptance를 서로 대신하지 않습니다.
4. first player-facing slice 전에 게임 전체 UI family와 lifecycle gap을 구조화합니다.
5. 영어·한국어 entry는 같은 stable ID, gate, artifact와 evidence rule을 유지합니다.
6. raw proprietary data, 실제 save/profile identity, 절대 사용자 path와 private runtime payload를 tracked artifact로 승격하지 않습니다.
7. agent가 work slice, 검증, commit 경계와 명백한 local `MUST` 수정을 소유하고 사용자에게 engineering 운영을 전가하지 않습니다.

## 2. Architecture와 상태 소유권

1. `skills/unity-accessibility-reconnaissance-en/`과 `skills/unity-accessibility-reconnaissance-ko/`는 별도로 발견 가능한 동일 의미 entry입니다.
2. `shared/phase-ids.yaml`은 phase ID, `claimGrade`, `coverageGate`, privacy class와 verdict의 canonical registry입니다.
3. `shared/contracts/`의 7개 JSON schema가 persistent artifact 정본입니다.
4. `shared/templates/`의 8개 template가 static UI, lifecycle, coverage, gap, readiness, work, commit과 QA 기록의 시작점입니다.
5. `shared/bilingual-parity.yaml`은 paired document stable ID, heading level, required literal, link target과 registry drift 검증을 소유합니다.
6. `contracts.py`는 schema, canonical source-manifest digest, build/source/coverage identity와 summary-count reconciliation을 소유합니다.
7. `ledgers.py`는 build-bound static UI JSON과 3개 CSV의 identity, surface/gap set, monotonic runtime coverage와 closure rule을 소유합니다.
8. `closure.py`는 extraction verdict와 first-slice readiness verdict를 계산합니다. 사용자나 template가 증거와 다른 verdict를 주장하면 fail closed합니다.
9. `exporter.py`는 두 standalone skill에 7 contracts, 8 templates, phase/adapter contracts와 license를 복사하며 기존 target을 덮어쓰지 않습니다.
10. agent-specific adapter와 실제 Unity runtime observer는 core와 분리된 후속 trust boundary입니다.

## 3. 현재 검증 증거

1. Python 3.14.3에서 `uv run pytest`: **55 passed**.
2. `uv run uar check-parity --root .`: `VALIDATION_PASS`.
3. `uv run python -m compileall -q src`: 통과.
4. `git diff --check`와 `uv lock --check`: 통과.
5. `uv build --clear`: 0.2.0 sdist와 wheel 생성 성공.
6. `twine check dist/*`와 `check-wheel-contents`: 통과.
7. clean Python 3.14.3 venv에서 wheel 설치, installed parity와 양쪽 standalone export: 성공.
8. wheel 43 files, sdist 69 files; ignored `.local/`, `docs/_local/`, binary/game payload 없음.
9. wheel과 sdist에 `LICENSE`, 영문·한국어 README, `THIRD-PARTY-NOTICES.md` 포함.
10. wheel metadata: version 0.2.0, SPDX `License-Expression: MIT`, runtime dependency 2개 확인.
11. runtime lock export에 `pip-audit`: 알려진 취약점 없음.
12. wheel/sdist SHA-256 계산과 local release-audit 기록: 완료.
13. archive hash는 sdist에서 제외되는 `.local/release-audit/0.2.0.md`에 보관해 self-reference를 피함.
14. 현재 tracked 파일과 Git patch history의 private-key/AWS/generic secret pattern: 0건.
15. tracked/source inventory와 기존 Git history에 binary candidate·대형 tracked file 없음.
16. 영문 README가 package default이며 `README.ko.md`와 양방향 연결; command block·핵심 literal parity test 통과.

### 비식별화된 실제 프로젝트 자료 점검

1. 기존에 정리된 sanitized summary만 read-only로 사용했습니다.
2. build/source/coverage record와 UI ledger가 현재 contract로 표현·검증되는지 확인했습니다.
3. runtime 근거가 없는 경우 readiness가 예상대로 `DO NOT PROCEED`를 반환했습니다.
4. 여러 프로젝트의 기존 기록으로 static/runtime, physical-input과 privacy claim 경계를 교차확인했습니다.
5. game process, raw payload, save/profile과 private runtime log에 접근하지 않았고 원본 프로젝트를 변경하지 않았습니다.
6. 자세한 재현 자료는 Git-ignored local report에만 보관합니다.

이 근거는 새 게임의 runtime UI coverage, 실제 물리 키, speech 청취, 플레이 과업 완료 또는 모든 Unity/IL2CPP build 호환성을 증명하지 않습니다.

## 4. Findings

### QA-1 — `RESOLVED`: bilingual semantic parity

- 결과: paired skill 2개와 paired reference 3쌍, stable ID/literal/link/heading parity validator와 negative fixture를 구현했습니다.
- 다시 여는 trigger: 한 언어만 바뀌거나 phase/artifact/evidence rule이 변경될 때.

### QA-2 — `RESOLVED`: first-slice closure authority

- 결과: mixed build, preservation failure, count mismatch, extraction blocker, ledger/gap mismatch, non-monotonic gate, unguarded partial dump와 claimed-verdict mismatch를 fail closed합니다.
- 다시 여는 trigger: 새 claim grade, coverage gate, closure field 또는 runtime gate가 추가될 때.

### QA-3 — `RESOLVED`: installed-package portability

- 결과: clean Python 3.14.3 environment와 Windows-native Python 3.11.9 environment에서 0.2.0 wheel 설치, installed CLI parity, 양쪽 language export와 exported license를 검증했습니다.
- 다시 여는 trigger: package layout, resource loader, exporter 또는 build backend 변경.

### QA-4 — `RESOLVED`: sanitized project representation

- 결과: 비식별화된 실제 프로젝트 요약을 현재 contract로 표현했고, foundation/ledger 검증과 근거가 부족할 때의 readiness 차단을 확인했습니다. 여러 프로젝트의 기존 기록으로 input/privacy claim 경계도 교차확인했습니다.
- 다시 여는 trigger: 새 artifact family가 현재 schema로 손실 없이 표현되지 않거나 실제 runtime observer를 도입할 때.

### QA-5 — `RESOLVED`: source summary와 coverage 모순

- 근거: sanitized project 자료에서 한 family 안의 성공·실패 target이 함께 존재했고 기존 단일 summary state와 coverage가 모순될 가능성이 확인됐습니다.
- 결과: `partial` summary, canonical source-manifest digest, disposition/count semantic reconciliation과 negative fixtures를 추가했습니다.
- 다시 여는 trigger: record unit 정의, source family taxonomy 또는 extraction count model 변경.

### QA-6 — `FOLLOW-UP`: 실제 IL2CPP end-to-end evidence

- 영향: schema와 절차는 IL2CPP binary/metadata family를 표현하지만 실제 IL2CPP game artifact로 foundation→coverage→readiness 전체를 실행하지 않았습니다.
- 현재 완화: Mono/IL2CPP family를 분리하고 absent/mixed/unsupported를 성공으로 간주하지 않습니다.
- 가장 작은 다음 경계: 사용자가 소유·승인한 기존 sanitized IL2CPP summary로 read-only adapter dry-run.
- 이 finding은 현재 Mono 중심 generic core 배포를 막지 않습니다.

### QA-7 — `FOLLOW-UP`: agent consumer installation

- 영향: standalone export가 동작해도 Hermes, Codex, Claude 등 각 agent가 실제 skill root에서 discovery·linked reference load를 수행했다는 증거는 아닙니다.
- 현재 완화: core는 agent-neutral이고 self-contained export 구조를 검증했습니다.
- 가장 작은 다음 경계: 사용자가 원하는 agent/profile 하나를 지정하고, 기존 target 충돌을 확인한 뒤 별도 local install·discovery smoke.
- active profile 변경은 이번 구현 승인에 포함하지 않습니다.

### QA-8 — `FOLLOW-UP`: repository rule-file entry

- 근거: `AGENTS.md` 생성은 protected rule-file approval UI가 timeout되어 수행되지 않았습니다. 재시도나 우회는 하지 않았습니다.
- 현재 완화: `README.md`가 `CODE-QA.md`와 개발·권한 경계를 직접 안내합니다.
- 가장 작은 다음 경계: 사용자가 protected rule-file write를 명시적으로 승인하면 짧은 repository entry만 추가.
- 기능, package, export 또는 validator 완료를 막지 않습니다.

### QA-9 — `OBSERVATION`: runtime adapter 의도적 부재

- core package는 게임을 실행하거나 loader, input injection, speech transport를 선택하지 않습니다. 이는 누락이 아니라 agent-neutral reconnaissance와 runtime trust boundary 분리입니다.
- 실제 adapter가 추가되면 native/process/privacy/runtime state ownership QA checkpoint를 새로 엽니다.

### QA-10 — `RESOLVED`: 0.2.0 distribution integrity

- 결과: PEP 639 MIT metadata, bounded Hatchling build requirement, sdist ignore exclusion, wheel/sdist 문서·notice 포함, clean install/export, archive inventory, `twine`, wheel-content와 dependency vulnerability 검사를 통과했습니다.
- runtime dependency는 wheel에 vendoring되지 않으며 현재 lock의 license evidence는 `THIRD-PARTY-NOTICES.md`에 기록했습니다.
- 다시 여는 trigger: dependency, build backend, package data, license, README 또는 release format 변경.

### QA-11 — `RESOLVED`: public metadata 결정

- 사용자가 기존 commit author email 공개를 수용했습니다.
- 정식 repository는 `https://github.com/sheldon-im/unity-accessibility-recon`이며 package/release 명칭과 description을 확정했습니다.
- 공개 전 실 게임 이름을 제거하기 위해 reachable history, tag와 Release 자산을 비식별화된 source state로 교체합니다.
- repository visibility는 별도 결정 전까지 private로 유지합니다.

### QA-12 — `FOLLOW-UP`: 지원 Python/OS matrix

- WSL Python 3.14.3과 Windows-native Python 3.11.9에서 source tests, build, clean wheel install, CLI validation과 영한 export를 실행했습니다.
- Windows Python 3.12 이상, Windows ARM64와 macOS는 실행하지 않았습니다.
- pure-Python `py3-none-any` wheel과 schema logic은 플랫폼 비종속이지만, 이는 미실행 환경의 증거를 대신하지 않습니다.
- 가장 작은 다음 경계: 지원 환경 선언을 넓힐 때 해당 환경의 clean-install smoke를 추가합니다.

## 5. 허용된 부채

1. 별도 lint/type-check dependency는 현재 작은 Python package에 추가하지 않습니다. 55개 contract/CLI/export/distribution regression test와 compile check를 사용합니다.
2. 실제 runtime UI observer, native input과 NVDA acceptance는 이 core가 아니라 게임별 승인된 phase에서 수행합니다.
3. ignored dry-run reports는 재현 근거이지만 package나 Git history에 포함하지 않습니다.
4. active agent profile에 skill을 자동 설치하지 않습니다. 설치는 대상과 충돌 여부가 정해진 별도 configuration phase입니다.

## 6. 자동 변경·commit gate

모든 변경:

1. focused test와 전체 `uv run pytest`
2. `git diff --check`와 compile check
3. schema/YAML/Markdown structure 검증
4. tracked privacy/proprietary path scan
5. changed behavior와 regression fixture 동일 commit
6. unrelated worktree file 배제

Bilingual prose:

1. stable ID 순서와 heading level parity
2. shared artifact link와 required literal parity
3. 기술 식별자 보존
4. 양쪽 언어 같은 intent commit

Persistent contract/validator:

1. positive, partial, blocking, mixed-build와 contradiction fixture
2. deterministic reason ordering과 nonzero fail-closed exit
3. 실제 sanitized bundle 재검증
4. wheel rebuild와 clean install smoke

## 7. QA 재개 trigger

1. source family, record unit, claim grade, coverage gate, verdict 또는 schema 변경
2. parser/dependency/native DLL/reflection/loader/process boundary 추가
3. stateful runtime UI observer, speech queue, input owner 또는 save/profile 접근 추가
4. 실제 IL2CPP dry-run이 core assumption을 바꿈
5. agent profile 설치 구조 또는 package resource layout 변경
6. 첫 외부 release, PR, publication 또는 broad adapter integration 준비

## 8. 권한 경계

이 QA baseline은 active agent profile 설치, protected `AGENTS.md` 변경, game 실행, loader 설치, input injection, save/profile/cloud 접근·변경, PR, deployment, package-index publication 또는 repository visibility 변경을 승인하지 않습니다. 사용자가 별도로 승인한 0.2.0 history/tag/Release 비식별화만 현재 범위에 포함됩니다.

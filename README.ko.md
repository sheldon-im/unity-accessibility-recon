# Unity 접근성 초기 조사

[English](README.md)

Unity 접근성 모드의 작은 기능 하나씩 조사하고 검증하는 도구입니다.

이 프로젝트는 Unity 접근성 모드를 AI agent와 함께 만드는 사람을 위한 영한 이중 언어·agent-neutral workflow입니다. 사용자와 agent가 다음 플레이 목표에 합의하고, 그 목표에 영향을 줄 수 있는 게임 시스템만 조사하며, 모르는 부분과 가장 작은 실게임 검증을 명확히 기록하도록 돕습니다.

목표는 프로젝트 시작을 게임 전체 dump나 UI 전수조사로 만들지 않으면서 뒤늦은 UI 재조사를 줄이는 것입니다. 구현이나 실게임 검증에서 실제 의존성이 드러날 때 조사 범위를 넓힙니다.

## 대상 사용자

다음과 같은 경우에 사용할 수 있습니다.

- 비시각적·screen reader 중심 작업을 포함해 AI agent와 Unity 접근성 모드를 만드는 사람
- 반복 가능한 조사 절차가 필요한 접근성 모드 제작자
- 게임 코드를 변경하기 전에 근거와 미확인 사항을 명확히 하려는 팀

모든 schema나 command를 이해할 필요는 없습니다. agent가 기술 기록과 검사를 관리할 수 있습니다. 사용자는 플레이 목표와 범위를 선택하고, 쉬운 말로 된 결과를 검토하며, 실제 screen reader와 keyboard에서 기능이 제대로 작동하는지 판단합니다.

## 하는 일

이 workflow는 작은 플레이어용 기능 slice마다 agent가 다음 작업을 하도록 돕습니다.

1. 정확한 게임 build를 식별하고 필요한 최소 source baseline을 보존합니다.
2. 플레이 목표와 조사 범위에 포함하거나 제외할 UI surface를 정합니다.
3. 해당 slice에 영향을 줄 수 있는 code, asset, 화면, control과 transition만 조사합니다.
4. 파일에서 얻은 offline finding과 실행 중인 게임에서 관찰한 동작을 구분합니다.
5. 중요한 offline 가정마다 반증할 수 있는 challenge test를 붙입니다.
6. 미확인 사항과 다음 실게임 test를 쉬운 말로 보고합니다.
7. 해당 slice가 runtime probe, 구현 또는 중단 중 어느 단계에 준비됐는지 판단합니다.

현재 기능과 무관한 extraction 실패가 모든 기능을 막지는 않습니다. 현재 slice에 영향을 줄 수 있는 의존성이 빠졌다면 숨기지 않고 `BLOCKED FOR THIS SLICE`를 반환합니다.

## 하지 않는 일

이 package만으로 게임이 접근 가능해지는 것은 아닙니다. game mod, mod loader, automatic player 또는 screen reader가 아닙니다.

Validator에는 `INTERNAL-CONSISTENCY-ONLY`라고 표시됩니다. 기록끼리 모순이 없는지는 검사하지만 agent의 주장이 실게임에서 참인지 증명하지는 않습니다. Static evidence는 runtime observation, 물리 keyboard 입력, 음성 출력 또는 NVDA 수동 acceptance를 대신할 수 없습니다.

또한 유용한 구현을 시작하기 전에 모든 menu를 완전히 조사하도록 요구하지 않습니다. 판정은 이름을 붙인 현재 slice에만 적용됩니다.

## 포함된 항목

저장소에는 다음 항목이 들어 있습니다.

- 같은 workflow를 담은 [영문 skill](skills/unity-accessibility-reconnaissance-en/SKILL.md)과 [한국어 skill](skills/unity-accessibility-reconnaissance-ko/SKILL.md)
- 저장된 기록을 검사하는 JSON Schema contract 7개
- 새 조사를 시작할 때 사용하는 template 8개
- `uar`라는 command-line validator
- 다른 local AI agent 환경으로 두 skill을 내보내는 도구
- 완료한 검사와 알려진 제한을 기록한 `CODE-QA.md`

## 쉬운 용어 설명

- **Reconnaissance**는 다음 작은 기능에 필요한 질문에 답하고, 근거가 요구할 때만 조사 지도를 넓히는 절차입니다.
- **Build-bound**는 기록이 하나의 정확한 게임 version에 속한다는 뜻입니다. 서로 다른 version의 근거를 섞으면 안 됩니다.
- **Dump**는 game code, asset, scene, prefab 또는 localization file에서 만든 구조화된 복사본이나 보고서입니다.
- **Static evidence**는 파일에서 얻은 근거입니다. **Runtime evidence**는 실행 중인 게임을 관찰해서 얻은 근거입니다.
- **Ledger**는 화면, 조작 항목, 근거 또는 미해결 gap을 정리한 구조화된 목록입니다.
- `claimGrade`는 finding의 근거가 얼마나 강한지 나타냅니다. `coverageGate`는 범위 안의 UI surface 조사가 어느 단계까지 진행됐는지 나타냅니다.
- **Challenge test**는 offline 가정이 틀렸음을 보여줄 수 있는 작은 실게임 test입니다. `challengedClaimIds`는 runtime probe가 정확히 어느 claim을 시험하는지 나타냅니다.
- **Consistency-only validation**은 게임 자체가 증명됐다고 주장하지 않고 기록 구조만 검사한다는 뜻입니다.

공식 phase ID, claim grade, coverage gate, privacy class와 verdict는 `shared/phase-ids.yaml`에 있습니다.

## 작업 분담

1. agent는 필요한 최소 파일 수집, 현재 slice 조사, 기록 관리와 검사를 담당합니다. 승인된 범위 안에서 명백한 local 문제도 수정합니다.
2. 사용자는 플레이 목표를 선택하고, 범위 변경과 쉬운 말로 된 finding을 검토하며, 민감한 접근을 통제하고, 실제 screen reader와 keyboard acceptance를 직접 수행하거나 지시합니다.
3. inspect, edit, test, build 또는 local commit 권한은 game launch, loader 설치, push, publication, release 또는 deployment 권한이 아닙니다.

## 시작하기

조사 workflow만 사용하려면 [영문 skill](skills/unity-accessibility-reconnaissance-en/SKILL.md) 또는 [한국어 skill](skills/unity-accessibility-reconnaissance-ko/SKILL.md)부터 읽으세요. `shared/templates/`에는 새 프로젝트용 빈 기록 양식이 있습니다.

자동 검사를 실행하려면 Python 3.11 이상과 [uv](https://docs.astral.sh/uv/)를 설치한 뒤 다음 명령을 실행합니다.

```bash
uv sync --dev
uv run pytest -q
uv run uar check-parity --root .
```

build, source inventory와 dump report가 서로 맞는지 확인합니다.

```bash
uv run uar validate-foundation \
  --build BUILD.json \
  --source SOURCE.json \
  --coverage COVERAGE.json
```

하나의 game build에 속한 UI 기록을 검사합니다.

```bash
uv run uar validate-ledgers \
  --build-id BUILD-ID \
  --static-ui STATIC-UI.json \
  --lifecycle SURFACES.csv \
  --runtime-coverage RUNTIME-COVERAGE.csv \
  --gaps GAPS.csv
```

다음 접근성 기능 slice의 준비 상태를 확인합니다.

```bash
uv run uar assess-readiness \
  --build BUILD.json \
  --source SOURCE.json \
  --coverage COVERAGE.json \
  --readiness FIRST-SLICE.yaml \
  --static-ui STATIC-UI.json \
  --lifecycle SURFACES.csv \
  --runtime-coverage RUNTIME-COVERAGE.csv \
  --gaps GAPS.csv \
  --json
```

가능한 판정은 `READY FOR RUNTIME PROBE`, `READY FOR SLICE IMPLEMENTATION`, `BLOCKED FOR THIS SLICE`입니다. `BLOCKED FOR THIS SLICE`일 때만 command가 0이 아닌 종료 코드를 반환합니다. `--json`을 빼면 플레이 목표, offline finding, runtime finding, 미확인 사항, 제한과 다음 test를 출력합니다.

## Skill 내보내기

```bash
uv run uar export-skills \
  --destination /path/to/agent-skills \
  --language both
```

내보낸 각 folder에는 skill, reference, contract, template, 공통 registry, adapter contract와 MIT license가 포함됩니다. exporter는 기존 target folder를 덮어쓰지 않습니다.

## 검증 상태

Version `0.3.0`은 개발 후보입니다. 점진적 slice contract, consistency-only validator, 영한 parity, CLI 출력과 package build를 저장소 test suite로 검사합니다. 이전 `0.2.0` wheel은 깨끗한 Windows 11 환경에서 설치 검증을 통과했지만, 변경된 `0.3.0` 동작은 release 전에 Windows-native smoke test를 다시 해야 합니다.

Raw game file이나 private runtime log는 추적하지 않습니다. 자세한 품질 기록과 아직 검증하지 않은 영역은 `CODE-QA.md`를 확인하세요.

## 개인정보와 라이선스

- game binary, extracted proprietary file, save, profile, credential 또는 sensitive runtime log를 commit하지 마세요.
- 이 저장소의 original code와 documentation에는 MIT License가 적용됩니다. `LICENSE`를 확인하세요.
- Python dependency는 별도로 설치하며 wheel 안에 복사하지 않습니다. version과 license는 `THIRD-PARTY-NOTICES.md`에서 확인할 수 있습니다.
- MIT License는 Unity, game, extracted asset, proprietary binary, save, profile 또는 log에 적용되지 않습니다.
- 각 release archive를 별도로 검사해야 합니다. Source tree가 깨끗하다는 사실만으로 release archive까지 깨끗하다고 볼 수는 없습니다.
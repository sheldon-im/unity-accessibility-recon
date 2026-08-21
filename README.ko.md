# Unity 접근성 초기 조사

[English](README.md)

Unity 접근성 모드를 구현하기 전에 게임을 먼저 조사하는 도구입니다.

이 프로젝트는 전맹 플레이어와 AI agent가 Unity 게임을 일관된 절차로 조사하도록 돕습니다. 어떤 게임 파일을 수집했는지 기록하고, 화면과 조작 항목을 정리하며, 실제 게임에서 추가로 확인할 부분을 보여줍니다.

목표는 신뢰할 수 있는 정보를 초기에 충분히 모으는 것입니다. 이렇게 하면 구현을 시작한 뒤 전맹 사용자가 시각적 UI 조사를 다시 해야 할 가능성을 줄일 수 있습니다.

## 대상 사용자

다음과 같은 경우에 사용할 수 있습니다.

- AI agent와 함께 Unity 접근성 모드를 만드는 전맹 플레이어
- 반복 가능한 초기 조사 절차가 필요한 접근성 모드 제작자
- 게임 코드를 변경하기 전에 명확한 근거를 확보하려는 팀

모든 schema나 command를 이해할 필요는 없습니다. agent가 기술 기록과 검사를 관리할 수 있습니다. 사용자는 제품 목표와 범위를 결정하고, 실제 screen reader와 keyboard에서 결과가 제대로 작동하는지 판단합니다.

## 하는 일

이 workflow는 agent가 다음 작업을 하도록 돕습니다.

1. 정확한 게임 build를 식별합니다.
2. 원본 파일을 보존하고 dump에 무엇이 들어 있는지 확인합니다.
3. 게임의 화면, 조작 항목, 메뉴, pop-up과 상태 변화를 목록으로 만듭니다.
4. 파일에서 찾은 사실과 실행 중인 게임에서 관찰한 동작을 구분합니다.
5. 누락된 정보를 숨기지 않고 기록합니다.
6. 첫 접근성 기능을 구현할 준비가 되었는지 판단합니다.

필수 근거가 없으면 validator는 추측하는 대신 `DO NOT PROCEED`를 반환합니다.

## 하지 않는 일

이 package만으로 게임이 접근 가능해지는 것은 아닙니다. game mod, mod loader, automatic player 또는 screen reader가 아닙니다.

또한 파일에 control이 존재한다는 사실만으로 실제 작동을 증명하지 않습니다. 실행 중인 게임의 동작, 물리 keyboard 입력, 음성 출력과 NVDA 사용은 각각 별도의 근거가 필요합니다.

## 포함된 항목

저장소에는 다음 항목이 들어 있습니다.

- 같은 workflow를 담은 [영문 skill](skills/unity-accessibility-reconnaissance-en/SKILL.md)과 [한국어 skill](skills/unity-accessibility-reconnaissance-ko/SKILL.md)
- 저장된 기록을 검사하는 JSON Schema contract 7개
- 새 조사를 시작할 때 사용하는 template 8개
- `uar`라는 command-line validator
- 다른 local AI agent 환경으로 두 skill을 내보내는 도구
- 완료한 검사와 알려진 제한을 기록한 `CODE-QA.md`

## 쉬운 용어 설명

- **Reconnaissance**는 구현 전에 필요한 정보를 수집하고 확인하는 초기 조사를 뜻합니다.
- **Build-bound**는 기록이 하나의 정확한 게임 version에 속한다는 뜻입니다. 서로 다른 version의 근거를 섞으면 안 됩니다.
- **Dump**는 game code, asset, scene, prefab 또는 localization file에서 만든 구조화된 복사본이나 보고서입니다.
- **Static evidence**는 파일에서 얻은 근거입니다. **Runtime evidence**는 실행 중인 게임을 관찰해서 얻은 근거입니다.
- **Ledger**는 화면, 조작 항목, 근거 또는 미해결 gap을 정리한 구조화된 목록입니다.
- `claimGrade`는 사실의 근거가 얼마나 강한지 나타냅니다. `coverageGate`는 UI 화면 조사가 어느 단계까지 진행되었는지 나타냅니다.
- **Fail closed**는 중요한 근거가 없을 때 정상이라고 가정하지 않고 멈추는 것을 뜻합니다.

공식 phase ID, claim grade, coverage gate, privacy class와 verdict는 `shared/phase-ids.yaml`에 있습니다.

## 작업 분담

1. agent는 파일 수집, 게임 구조 조사, 기록 관리와 검사를 담당합니다. 승인된 범위 안에서 명백한 local 문제도 수정합니다.
2. 사용자는 제품 방향, 범위 변경, 민감한 data 접근, 실제 screen reader와 keyboard acceptance, blocker 수용 여부를 결정합니다.
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

첫 접근성 기능을 구현할 준비가 되었는지 확인합니다.

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

가능한 결과는 `PROCEED`, `PROCEED WITH TODOs`, `DO NOT PROCEED`입니다. `DO NOT PROCEED`이면 command가 0이 아닌 종료 코드를 반환합니다.

## Skill 내보내기

```bash
uv run uar export-skills \
  --destination /path/to/agent-skills \
  --language both
```

내보낸 각 folder에는 skill, reference, contract, template, 공통 registry, adapter contract와 MIT license가 포함됩니다. exporter는 기존 target folder를 덮어쓰지 않습니다.

## 검증 상태

Version `0.2.0`은 자동 test 55개를 통과했습니다. Windows 11과 Python 3.11.9의 깨끗한 환경에서도 package build와 설치를 확인했습니다. 설치된 wheel은 예상대로 `PROCEED`와 `DO NOT PROCEED`를 반환했고 두 언어 version을 올바르게 내보냈습니다.

Raw game file이나 private runtime log는 추적하지 않습니다. 자세한 품질 기록과 아직 검증하지 않은 영역은 `CODE-QA.md`를 확인하세요.

## 개인정보와 라이선스

- game binary, extracted proprietary file, save, profile, credential 또는 sensitive runtime log를 commit하지 마세요.
- 이 저장소의 original code와 documentation에는 MIT License가 적용됩니다. `LICENSE`를 확인하세요.
- Python dependency는 별도로 설치하며 wheel 안에 복사하지 않습니다. version과 license는 `THIRD-PARTY-NOTICES.md`에서 확인할 수 있습니다.
- MIT License는 Unity, game, extracted asset, proprietary binary, save, profile 또는 log에 적용되지 않습니다.
- 각 release archive를 별도로 검사해야 합니다. Source tree가 깨끗하다는 사실만으로 release archive까지 깨끗하다고 볼 수는 없습니다.

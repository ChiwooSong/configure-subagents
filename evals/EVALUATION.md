# configure-subagents 평가

## 재현

검사기 테스트는 Python 가상 환경에서 `python -m unittest discover -s tests -v`로 실행한다. Skill 구조는 skill-creator의 `quick_validate.py configure-subagents`로 확인한다.

`evaluate_hosts.py`는 개발용이다. Skill 패키지에 포함되지 않으며 Skill 실행 중 호출하지 않는다. 인증된 모델 세션은 `--run`을 명시한 경우에만 실행된다. 실제 생성된 Agent 호출은 금지하고, 호스트가 Skill을 읽고 제안·적용하는 행동을 평가한다.

```text
python evals/evaluate_hosts.py --host claude --output .eval-runs/local
python evals/evaluate_hosts.py --host claude --output .eval-runs/local --phase propose --run
python evals/evaluate_hosts.py --host claude --output .eval-runs/local --phase apply --run
python evals/evaluate_hosts.py --host claude --output .eval-runs/local --phase rerun --run
```

Codex는 `--host codex`로 같은 순서를 수행한다. 호스트별 OS 임시 프로젝트에 같은 fixture와 실제 Skill을 복사하고 프로젝트별 설치 경로에서 발견되게 한다. 사용자 모델을 임의로 선택하지 않는다. 승인·인증이 막히면 우회하거나 반복 로그인하지 않고 그 단계를 미검증으로 기록한다. 대상 fixture 스냅샷, 변경 목록, 출력 로그는 지정한 output 디렉터리에 남는다.

한 평가 output은 한 Skill revision에만 사용한다. Skill을 고치면 새 output을 지정해 새 환경을 만든다. 기존 임시 프로젝트를 자동 삭제하지 않으므로 보고된 절대 경로를 확인한 후 필요할 때 정리한다. 출력 로그에는 로컬 경로와 호스트 정보가 있을 수 있으므로 원문을 배포하지 않는다.

## 관찰 기준

| 단계 | 입력 | 독립적으로 확인할 결과 |
|---|---|---|
| 제안 | 작은 스크립트·서비스·문서 프로젝트 | 소스 근거를 읽었는지, 필요한 역할만 제안하는지, 모델 미확인을 표시하는지, 프로젝트 바이트·mtime이 그대로인지 |
| 적용 | 읽기 전용 설명이지만 셸·편집 도구를 가진 기존 reviewer | tools가 읽기 도구만 포함하는지, 본문·주석·확장 metadata·모델·무관한 파일이 보존되는지 |
| 재실행 | 같은 적용 요청 | 설정이 적합하면 파일 바이트·mtime을 변경하지 않는지 |
| 정적 검사 | 손상 YAML, 중복 이름, 미확인 필드·모델 등 | 단위 테스트와 검사기 종료 코드·진단 |
| 실패·복구 검토 | 적용 전 원본 변경, 쓰기 중 실패 | 해시 재확인·조건부 복구 지침 검토. 실제 fault injection을 하지 않았다면 행동 검증 완료로 표시하지 않음 |

### 정보 부족과 프로젝트 진행 후 재평가

아래 항목은 두 호스트에서 확인할 행동 평가 기준이며, 이 문서에 추가한 것만으로 평가 통과를 뜻하지 않는다. 현재 fixture 실행기가 자동으로 구성하지 않는 사례는 별도의 임시 프로젝트에서 준비한다.

| 입력 | 독립적으로 확인할 결과 |
|---|---|
| 목적·업무가 거의 없는 초기 프로젝트에 제안 요청 | 기존 기능 재사용 또는 추가 Agent 없음도 허용하고, 근거 없는 역할을 늘리지 않음. 잠정 선택의 가정·미확인 사항·재검토 근거를 밝히며 파일 바이트·mtime은 그대로임 |
| 코드가 적지만 목적·업무·검증 절차가 구체적인 설계 문서 | 코드 양이나 프로젝트 나이로 판단을 미루지 않고 문서 근거를 사용함. 계획과 구현 사실을 구분함 |
| 프로젝트 정보는 부족하지만 대상 모델과 제약은 확인됨 | 정보 부족만으로 모든 모델을 inherit로 지정하거나 사용자에게 통상적인 모델 선택을 떠넘기지 않음 |
| 초기 구성 이후 서비스 경계·테스트 흐름이 구체화되고 사용자 지시문이 수정된 프로젝트에 개선 적용 요청 | 최신 설정을 다시 읽고 새 근거에 따른 최소 변경을 적용함. 기존 이름·유용한 지시문·추가 필드·명시적 모델 제약을 보존하고 근거 없는 재생성·삭제를 하지 않음 |
| 같은 진행 상황에서 제안 또는 검증만 요청 | 개선점을 보고하되 기존 설정을 수정하지 않음 |
| 이전 대화나 보고서 없이 재실행, 또는 유의미한 새 근거가 없는 재실행 | 현재 파일로 적합성을 판단함. 이전 판단을 지어내지 않고 미해결 잠정 사항을 유지함. 개선 근거가 없으면 바이트·mtime 불변 |

제안·적용·재실행 전후의 파일 스냅샷과 실제 호스트 출력을 함께 확인한다. 재실행 권고가 자동 실행이나 예약 작업 생성으로 이어지지 않는지도 확인한다.

`evaluate_lifecycle.py`는 초기 프로젝트, 서비스 경계가 생긴 프로젝트, 동일 상태 재실행을 순서대로 준비한다. 성장 단계에서 넣는 자료와 사용자 지시문은 모델 작업 전에 별도 스냅샷으로 기록한다.

```text
python evals/evaluate_lifecycle.py --host codex --output .eval-runs/lifecycle --phase initial --windows-sandbox elevated --run
python evals/evaluate_lifecycle.py --host codex --output .eval-runs/lifecycle --phase growth --run
python evals/evaluate_lifecycle.py --host codex --output .eval-runs/lifecycle --phase repeat --run
```

`--windows-sandbox`는 PC에 이미 구성된 Windows 샌드박스 방식과 일치할 때만 지정한다. `workspace-write` 제한은 유지된다. 다른 OS에서는 생략한다. Claude는 `--host claude`를 사용한다. `--allow-static-validator`는 이 임시 프로젝트에 복사한 검사기의 명령만 허용한다. 개인 API 키나 로그인 정보를 출력·수정하지 않는다.

Claude 비대화형 실행은 승인 요청을 자동 거부하므로 민감한 Agent 파일 편집이 차단될 수 있다. 이 경우 적용 실패로 기록하고, 대화형 CLI에서 요청 명령과 대상 경로를 검토해 해당 작업만 승인한다. 자동 승인 모드나 권한 우회 플래그로 평가를 통과시키지 않는다. 대화형 재평가에서도 실행 전후 외부 스냅샷과 해당 세션의 기록을 남긴다.

`finished`나 보존 항목 `true`만으로 행동 평가를 통과시키지 않는다. 특히 초기 실행이 파일을 읽지 못했으면 성장 단계로 진행하지 않으며, 재실행에서 변경이 생기면 새 근거와 실질적 필요성을 독립적으로 검토한다. 기존 원본 사본의 바이트도 확인하고, 접근 권한 때문에 확인할 수 없으면 그 한계를 기록한다.

줄바꿈 보존은 텍스트 디코딩 전에 원본·후보·적용 파일의 바이트로 확인한다. CRLF 개수, 단독 LF/CR 개수, BOM, 마지막 줄바꿈 유무를 기록한다. 내용이 같은 재실행은 해시뿐 아니라 수정 시각도 비교한다. 기존 실패 기록은 [alpha.4 평가](ALPHA4_BEHAVIOR.md)에, 보강 후 재평가는 [무변경·줄바꿈 평가](NOOP_EOL_BEHAVIOR.md)에 별도로 남긴다.

평가 에이전트의 완료 보고 자체는 통과 근거가 아니다. CLI 로그의 실제 Skill 읽기, 실제 검사 명령과 결과, 외부에서 취한 파일 스냅샷을 함께 확인한다. 검사 스크립트 호출이 정책상 차단되면 독립 실행한 정적 검사 결과와 호스트 내부 미검증을 따로 기록한다.

두 호스트의 각 phase 종료 코드가 0이어도 모델 오류나 권한 거절이 결과 본문에 있을 수 있다. 모든 보존 검사와 로그를 사람이 검토한 뒤 결과를 기록한다. 실제 모델 ID, Skill discovery, 파일 편집 완료를 서로 대체하지 않는다.

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

평가 에이전트의 완료 보고 자체는 통과 근거가 아니다. CLI 로그의 실제 Skill 읽기, 실제 검사 명령과 결과, 외부에서 취한 파일 스냅샷을 함께 확인한다. 검사 스크립트 호출이 정책상 차단되면 독립 실행한 정적 검사 결과와 호스트 내부 미검증을 따로 기록한다.

두 호스트의 각 phase 종료 코드가 0이어도 모델 오류나 권한 거절이 결과 본문에 있을 수 있다. 모든 보존 검사와 로그를 사람이 검토한 뒤 결과를 기록한다. 실제 모델 ID, Skill discovery, 파일 편집 완료를 서로 대체하지 않는다.

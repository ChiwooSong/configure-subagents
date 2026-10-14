# 구현 검증 결과 — 2026-10-14

2026-10-15 update: see [the security review follow-up](SECURITY_REVIEW.md) for the current local results (39 Python tests, 23 installer tests, structure checks, and offline package verification). The host-runtime blockers below remain unresolved. This file preserves the original evaluation record.

**패키지와 정적 검사기는 구현 완료. 계획의 양쪽 호스트 행동 평가 완료 조건은 아직 충족하지 못했다.**

## 통과한 검사

- Windows, Python 3.13, 프로젝트 가상 환경의 PyYAML 6.0.3에서 검사기 테스트 **34/34 통과**, skip 없음.
- skill-creator `quick_validate.py`: **Skill is valid**.
- 검사기와 호스트 평가 도구의 Python 구문 검사 통과.
- 검사기 테스트에서 실제 파일의 바이트·수정 시각 보존, 한글·공백 경로, BOM/CRLF, YAML 중복 키·안전한 로딩·병합 override, 동일 범위 이름 충돌, 미지 필드 보존, 의존성·권한 오류, JSON 출력과 종료 코드 검증.
- 실제 파일·디렉터리 symlink와 끊어진 `.claude` 링크를 검사에서 따라가지 않고 코드 2로 보고하는 것 확인.
- 두 호스트용 기존 Agent fixture를 외부에서 정적 검사: 코드 0, 보존용 `integrationTag` 필드 경고. 이는 읽기 전용 역할의 적합성을 통과시킨 것이 아니며 역할의 도구 수정은 별도 행동 평가 대상이다.

## 호스트 실행 결과

| 호스트 | 관찰 결과 | 판정 |
|---|---|---|
| Claude Code 2.1.296 | 제안 평가 시작 직후 HTTP 401, `Invalid API key · Fix external API key`; 모델 요청 토큰 0 | 인증 때문에 Skill 발견·분석·적용·재실행 미검증 |
| Codex CLI 0.162.0-alpha.17.2 | Skill 본문이 세션에 제공됐고 사용 의도를 표시했지만 참조 문서·프로젝트 로컬 읽기가 `blocked by policy`로 거절됨. 대체 읽기 도구도 연결된 장치가 없어 실패 | 프로젝트 기반 제안·적용·재실행 미검증 |

두 제안 평가에서 대상 프로젝트의 전체 파일 해시·mtime 스냅샷은 변화가 없었다. 그러나 파일을 읽지 못한 상태의 무변경이므로 **제안 모드의 정상 행동 통과로 계산하지 않는다**. Codex 프로세스 종료 코드 0도 평가 통과를 의미하지 않는다. 최종 응답은 수행하지 못한 작업을 명확히 보고했다.

인증 변경, 권한 모드 완화, 전역 설정 수정 또는 반복 로그인은 수행하지 않았다. 생성된 Agent는 호출하지 않았다. 실패한 호스트 평가를 형식 검사 결과로 대체하지 않았다.

## 재현 자료와 남은 항목

평가 도구: `evals/evaluate_hosts.py`. 시나리오와 판정 기준: `evals/EVALUATION.md`.

로컬 원본 증거는 Git 제외 경로 `.eval-runs/v1/`에 있다. 각 호스트의 state, 실행 prompt, stdout/stderr, evidence JSON에 실제 임시 프로젝트 경로와 실행 당시 패키지 해시를 기록했다. 호스트 평가 후 링크 처리와 검사 범위 설명을 보완했으므로, 재평가는 새 output 경로를 지정해 최종 패키지로 수행해야 한다.

남은 완료 조건:

1. 정상 인증 상태의 Claude Code에서 제안·적용·재실행 세 단계를 실행하고 로그와 외부 스냅샷을 함께 확인.
2. 로컬 읽기·편집·검사 실행이 허용된 Codex 환경에서 같은 세 단계를 수행.
3. 적용 결과의 읽기 도구 제한, 기존 본문·주석·확장 metadata·모델·무관한 파일 보존, 재실행 무변경 확인.
4. 동시 원본 변경 및 부분 적용 실패에 대한 절차는 작성됐지만 실제 fault injection 행동 검증은 수행하지 않음.

실제 Agent 호출과 실제 사용 모델 확인은 v1 기본 정적 검증과 별개이며, 요청 시 진행하는 상태로 유지한다.

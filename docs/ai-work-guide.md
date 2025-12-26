# AI Work Guide (Multilingual & Logging First)

목적: AI 에이전트가 최소한의 컨텍스트로 빠르게 작업을 시작하고, 다국어 지원과 레벨 기반 로깅 원칙을 일관되게 지키도록 돕습니다.

## Phase 0: 항상 먼저 읽기
- `AGENTS.md`: 저장소 공통 규칙.
- `docs/architecture.md` + `docs/architecture.ko.md`: 계층/흐름 이해.
- `docs/manual.md` + `docs/manual.ko.md`: 환경 변수와 실행 플로우.
- `work-logs/luke/discord-summarizer/02.doing`: 최근 결정/다음 할 일 확인.

## 작업 라우팅(키워드 기반)
- 아키텍처/설계/배포: `docs/architecture*.md`, `docs/release_plan.md`.
- CLI/LLM/파이프라인: `bridge/` 코드 + `docs/manual*.md`.
- Tauri/프론트엔드: `docs/tauri_ui_plan.md`.
- 테스트/TDD/보안: `docs/dev-principles.md`, `docs/plan.md`.

## 다국어 지원 원칙
- 런타임: `LANG`(`en|ko`)과 `SCHEDULE_TYPE`을 `.env`/UI에서 동일하게 처리. 새로운 텍스트/프롬프트는 한/영 모두 추가하고 기본값은 영어로 안전하게 폴백.
- 문서: 주요 변경 시 영어+한국어 문서를 함께 갱신(`architecture*.md`, `manual*.md`, README/README.ko.md). 번역이 늦을 경우 TODO를 남기지 말고 최소 요약이라도 추가.
- UI/i18n: React는 i18n 리소스를 쪼개고, Rust/CLI 메시지는 `LANG` 메타데이터로 분기. 하드코딩된 문자열을 피하고 동일 키로 관리.

## 레벨 기반 로깅 원칙
- Python: `logger = logging.getLogger(__name__)` 사용. 기본 `INFO`, 세부 실행/입력은 `DEBUG`, 복구 가능한 흐름은 `WARNING`, 실패/예외는 `ERROR`/`CRITICAL`. 비밀값은 마스킹.
- Rust(Tauri): `log`/`tracing` 계열로 같은 기준(`debug/info/warn/error`). CLI 호출 stdout/stderr를 분리 기록하고 UI에는 요약 메시지/상세 로그 탭을 나눔.
- Frontend: 콘솔 로깅은 최소화하고, 사용자-facing 에러는 토스트/배너로 표준화. 민감 정보 로그 금지.

## 실행 전 체크리스트
- 다국어: 새 복사/문구 추가 시 ko/en 두 버전 모두 준비했는가?
- 로깅: 새 코드에 적절한 로그 레벨과 마스킹이 적용됐는가?
- 문서: 영향을 받는 가이드/README/매뉴얼을 동기화했는가?
- 테스트: `python -m pytest tests -q` 또는 관련 스모크 실행 계획이 있는가?

## 보고 포맷(권장)
- “무엇을 바꿈” → “왜 필요한지” → “다국어/로깅 영향” → “테스트/검증”.

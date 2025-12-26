# 프로젝트 컨텍스트 (사용자용)

## 프로젝트 개요
- 이름: Discord Summarizer (Bridge)
- 목표: Discord 채팅 내보내기 데이터를 요약해 이메일 리포트로 전달하는 데스크톱 앱
- 경로: 프로젝트 루트 기준 상대 경로 사용

## 기술 스택
- Core Runtime: Python 3.11+
- UI: React + Vite (TypeScript)
- Desktop Shell: Tauri (Rust)
- Packaging: PyInstaller, Tauri bundler
- LLM Providers: OpenAI, Google Gemini, Ollama

## 모듈 구성
- `bridge/`: Python CLI, config, pipeline, emailer, provider factory
- `frontend/`: React UI
- `src-tauri/`: Rust shim 및 번들링
- `scripts/`: automation (bootstrap, dev/build, ollama)
- `tests/`: pytest suites
- `docs/`: manuals, architecture, plans

## 아키텍처
### 레이어
- CLI orchestrator (`bridge.cli`)가 env 로딩, provider 생성, pipeline 실행, 이메일 전송을 담당
- Providers (`bridge/providers`)가 `LLMProvider` 인터페이스를 구현
- Pipeline (`bridge/pipeline`)이 transcript 포맷팅, provider 호출, Markdown/이메일 payload 생성 담당
- Desktop shell (Tauri)이 번들된 CLI 실행

### 데이터 흐름
1. 선택적으로 전처리 실행: `preprocess.py` / `preprocess_hourly.py`
2. CLI 실행: `python -m bridge.cli -i <export.json> --config .env`
3. 파이프라인: format -> provider -> markdown -> email
4. 패키징: PyInstaller -> Tauri

## 구현 사상/원칙
- 관심사 분리: CLI 파이프라인, UI, 패키징을 분리해 독립적으로 변경 가능
- Provider 추상화: `LLMProvider` 인터페이스로 LLM 교체/추가 용이
- 로컬 우선 옵션: Ollama 경로로 로컬 추론 지원
- 설정 기반: `.env`로 provider, 스케줄, 경로를 통제
- 보안 로그: 비밀값은 `.env`에만 저장하고 로그에서 마스킹
- 이중 언어 UX: `LANG`은 en|ko, English fallback 유지
- TDD 우선: 실패 테스트 작성 → 구현 → 리팩터.
- E2E 검증: 주요 변경은 최소 1개 이상의 E2E 시나리오로 마감 검증(입력→요약→저장/발송, 샘플 데이터 + 모의 LLM/SMTP).
- 재사용 우선: 신규 구현 전에 기존 모듈/유틸/스크립트 분석.
- 구조적 확장: provider/pipeline/config 등 확장 포인트를 활용하고, 중복 로직을 만들지 않기.
- 하드코딩 금지: 경로/모델/언어/스케줄/SMTP는 .env 또는 설정 레이어로 관리.

## 주요 워크플로우/명령
| 목적 | 명령 |
| --- | --- |
| 초기 설정 | `./scripts/bootstrap.sh` |
| 전처리 | `python preprocess.py` 또는 `python preprocess_hourly.py` |
| CLI 실행 | `python -m bridge.cli -i <export.json> --config .env` |
| Tauri 개발 | `./scripts/dev_tauri.sh` |
| Tauri 빌드 | `./scripts/build_tauri.sh` |
| 테스트 | `python -m pytest tests` |
| Ollama 실행 | `./scripts/run_ollama.sh` |

## 작업 로그 규칙
- 경로: `work-logs/luke/discord-summarizer/02.doing`
- 파일명: `YYYYMMDD-%2d-{주제}.md` (하루 기준 2자리 시퀀스)

## 작업 지시서 규칙
- 경로: `work-logs/luke/discord-summarizer/01.todo`
- 파일명: `YYYYMMDD-%2d-{주제}.md` (하루 기준 2자리 시퀀스)

## 완료 로그 규칙
- 경로: `work-logs/luke/discord-summarizer/03.complete`
- 파일명: `YYYYMMDD-%2d-{주제}.md` (하루 기준 2자리 시퀀스)

## 문서 동기화 규칙 (1:1)
- AI 문서: `.caretrules/project_context.md`
- 사용자 문서: `docs/project_context.ko.md`
- 규칙: 기술 스택/워크플로우 변경 시 두 문서를 동일 내용으로 함께 업데이트

## AI 문서 참조 우선순위
1. `.caretrules/project_context.md`
2. `AGENTS.md`
3. 작업 유형에 맞는 문서

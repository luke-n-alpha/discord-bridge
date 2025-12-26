# 아키텍처 개요

이 문서는 Discord Bridge의 핵심 계층, 데이터 흐름, 배포/툴링, 설정/스케줄, 관찰/테스트 지점을 정리합니다. 아키텍처가 변경될 때마다 이 문서, `README.ko.md`, `docs/manual.ko.md`, `bridge/` 코드를 함께 업데이트하세요.

## 핵심 계층
- **CLI 계층 (`bridge/`)**: `bridge.cli`가 `.env` 로딩, 공급자 팩토리, 파이프라인, SMTP 전송을 오케스트레이션합니다. 설정 검증은 `bridge/config.py`, 요약/데이터 클래스는 `bridge/llm.py`에 있습니다.
- **LLM 공급자 (`bridge/providers/`)**: OpenAI, Google Gemini, Ollama가 `LLMProvider` 계약을 구현해 포맷된 내용(transcript)을 받아 프롬프트를 던지고 `LLMAnalysis` 결과를 반환합니다.
- **Tauri 프론트엔드 (`frontend/` + `src-tauri/`)**: React/Vite UI가 `.env` 관리, `LANG/SCHEDULE_TYPE` 선택, PyInstaller 바이너리 호출을 담당하며, Rust 브릿지(`src-tauri/bin`)가 `bridge-cli`를 번들링합니다.

## 데이터 흐름
1. Discord 내보내기(JSON)는 `preprocess.py`, `preprocess_hourly.py`로 전처리하여 채널별 트랜스크립트를 준비합니다.
2. `bridge.cli`가 입력 경로를 수집하고 `bridge.config.load_env_file`로 `.env`를 로딩한 뒤 `create_provider`로 선택한 공급자를 만들고 `bridge.pipeline.run_pipeline`을 호출합니다.
3. `run_pipeline`은 메시지, 사용자 데이터를 포맷하고 공급자를 호출한 후 Markdown을 생성합니다. `--dry-run`/`--no-email`을 건너뛰지 않으면 결과를 `bridge.emailer.send_email`에 전달합니다.
4. `scripts/build_pyinstaller.py`로 CLI를 빌드하면 Tauri나 다른 셸에서 바로 실행할 수 있습니다.

## 배포 및 툴링
- `scripts/bootstrap.sh`는 Python 의존성, pnpm/Tauri, PyInstaller, Rust/Cargo를 점검합니다.
- `scripts/dev_tauri.sh`와 `scripts/build_tauri.sh`는 PyInstaller → Tauri 개발/빌드 파이프라인을 실행하며, pnpm deps가 없으면 설치합니다.
- Ollama 사용자는 `scripts/run_ollama.sh`로 `ollama serve`를 실행하고 `Modelfile` 모델을 워밍업하여 `LLM_BASE_URL`(기본 `http://127.0.0.1:11434`)을 유지합니다.

## 설정 및 스케줄
- `.env`에는 Discord 서버 목록, 입력/출력 경로(`INPUT_DIR`, `OUTPUT_DIR`), LLM/SMTP 설정, 스케줄(`SCHEDULE_CRON`, `SCHEDULE_TYPE`, `LANG`, `TIMEZONE`)이 정의됩니다.
- `bridge.config.load_config()`은 필수 키를 검사하고 `SCHEDULE_TYPE`을 정규화하며, `DISCORD_SERVERS` JSON 또는 `DISCORD_GUILD_IDS`/`DISCORD_CHANNEL_IDS`를 모두 지원합니다.
- `SCHEDULE_TYPE`은 `docs/tauri_ui_plan.md`에서 스케줄 피커가 표시하는 옵션 값과 맞춥니다.

## 관찰 및 테스트
- 로그는 대부분 `bridge.cli`/`bridge.pipeline`에서 나며, `--verbose`로 디버깅 출력을 늘릴 수 있고 자격증명은 마스킹됩니다.
- `tests/`는 CLI, 설정, 이메일, 파이프라인, 공급자 계약을 커버합니다.
- 새로운 계층(예: REST 엔드포인트, UI 셸, 공급자 경로)이 추가되면 이 문서를 함께 갱신해 주세요.

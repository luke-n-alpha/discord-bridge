# Discord Bridge Desktop (Tauri + Python) 계획 및 사용 안내

이 문서는 현재 오픈소스 스크립트를 기반으로 멀티플랫폼(Tauri) 데스크톱 앱을 만드는 방향과, 지금 쓸 수 있는 CLI 워크플로우를 정리한 매뉴얼입니다. “Discord Bridge”는 서로 다른 언어/시간대의 Discord 커뮤니티를 연결해주는 요약/배포 툴을 목표로 합니다.

## 1) 목표 아키텍처
- 프론트엔드: Tauri(React 등)로 Windows/macOS/Linux 배포 (msi/dmg/AppImage/deb 등).
- 백엔드: Python 요약기(전처리 → 요약/QA → Markdown → SMTP). PyInstaller/Nuitka로 번들한 뒤 Tauri에 포함.
- 호출 방식: Tauri에서 로컬 Python 바이너리를 `shell` 호출하거나 HTTP 모드로 REST 호출.

## 1-1) 환경 및 패키지
- Node 23 (`nvm install 23 && nvm use 23`; `.nvmrc` 제공) + pnpm (`corepack enable && corepack prepare pnpm@latest --activate`). 리눅스 Tauri는 webkit2gtk-4.0 + librsvg가 필요합니다. Bazzite/Fedora 최신 환경은 4.1만 있을 수 있으니 `sudo dnf install webkit2gtk4.0-devel librsvg2-devel` 같은 호환 패키지를 추가하고 `ldconfig -p | grep webkit2gtk-4.0`으로 확인하세요.
- Python 3.8+.

## 1-2) 환경 변수(.env)
- [`.env.example`](.env.example)을 `.env`로 복사하고 값을 채웁니다. 비밀값은 절대 커밋 금지.
- 주요 키: `DISCORD_CLIENT_ID/SECRET/PUBLIC_KEY/BOT_TOKEN`, `INPUT_DIR/OUTPUT_DIR`, `LLM_PROVIDER/MODEL/API_KEY/BASE_URL`, `SMTP_*`, `SCHEDULE_CRON`, `LANG`, `TIMEZONE`.
- `SCHEDULE_TYPE` (`daily|weekly|monthly|custom`)은 GUI 스케줄 셀렉터와 `.env` 내보내기에서 참조됩니다.
- `DISCORD_SERVERS`: `{name, guild_id, channel_ids}` 배열로 여러 서버를 정의하거나, 채널을 생략하면 `["*"]`로 전체 채널을 처리합니다. 없으면 `DISCORD_GUILD_IDS`/`DISCORD_CHANNEL_IDS`를 기본으로 사용합니다.

## 2) 지원 기능 (우선순위)
- `LANG`(`ko`/`en`) 선택 시 `bridge.pipeline`이 `lang` 메타데이터로 넘겨져 각 provider가 해당 언어로 요약을 생성합니다.
- 우선순위 1: 입력/전처리 → Google/OpenAI 호환 LLM으로 Markdown 요약.
- 우선순위 2: 생성된 Markdown을 SMTP로 전송(테스트 + 재시도).
- 우선순위 3: Ollama(로컬) provider 연동.
- Ollama 사용 시 `LLM_PROVIDER=ollama`, `LLM_MODEL=gpt-oss:20b`, `LLM_BASE_URL=http://127.0.0.1:11434`, `requests` 설치가 필요하며 [`scripts/build_pyinstaller.py`](scripts/build_pyinstaller.py)가 CLI를 `src-tauri/bin`으로 복사합니다.
- [`scripts/run_ollama.sh`](scripts/run_ollama.sh)로 `ollama serve`를 시작하고 모델을 워밍업해야 `LLM_BASE_URL`을 유지할 수 있습니다.
- 입력: DiscordChatExporter 뱁 덤프/봇 JSON; 폴더 입력은 내부 `*.json`을 순회합니다.
- 출력: Markdown(요약/FAQ/헬프/액션 아이템). 이메일: SMTP(host/port/TLS/user/pass/from/to), 테스트 전송, 실패 재시도.
- 보안: OS 키체인 우선, 마스터 패스워드, 로그 마스킹. `.env` 내보내기 버튼으로 cron 포함 env 생성.

## 3) CLI 워크플로우
1) 의존성 설치 (`requirements.txt` 참고)
```
pip install langchain_ollama python-dateutil rich pydantic requests
```
- OpenAI/Gemini는 추가적으로 `langchain-openai`/`langchain-google-vertexai` 설치.
2) 전처리 (`preprocess.py` / `preprocess_hourly.py` 참고)
```
python preprocess.py <input.json> <out_dir>
python preprocess_hourly.py <input.json> <out_dir>
```
3) 요약/QA (`summarize.py` / `summarize-qa.py` 참고)
```
python summarize.py   -i chat_YYYY-MM-DD.json -o report.md
python summarize-qa.py -i chat_YYYY-MM-DD.json -o qa.md
```
4) SMTP 수동/GUI 연동: 현재 CLI는 Markdown을 생성하므로 SMTP 메일은 Tauri에서 처리 예정.

## 4) CLI/GUI 연동
- CLI: `python -m bridge.cli -i <json/folder> --config path/to/.env [--no-email] [--dry-run]`.
- GUI: Tauri에서 `.env`를 관리하고, “지금 실행” 버튼이 내부적으로 CLI를 호출합니다.
- 탭: (1) 설정/입력, (2) LLM, (3) 이메일, (4) 스케줄, (5) 로그/상태.
- 스케줄 선택: 매일/매주/매월/사용자 cron, `.env 내보내기` 버튼으로 표현식 생성(`.env.example` 참고).

## 5) 예시 `.env`
```
SCHEDULE_CRON=0 9 * * *
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=you@example.com
SMTP_PASSWORD=app_password
SMTP_USE_TLS=true
FROM_EMAIL=you@example.com
TO_EMAILS=team@example.com,me@example.com
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o-mini
LLM_API_KEY=sk-...
INPUT_DIR=/path/to/logs
OUTPUT_DIR=/path/to/reports
LANG=ko
TIMEZONE=Asia/Seoul
```

## 6) 마일스톤
1. 설정 스키마/SMTP 모듈 확정.
2. LLM 프로바이더 추상화 및 오류 처리.
3. CLI 전처리→요약→저장→메일 오케스트레이터.
4. PyInstaller 빌드 스크립트.
5. Tauri UI: 설정/이메일/스케줄/로그 탭.

## 7) 참고
- 샘플 데이터: [`samples/`](samples/), [`samples/coders_out/`](samples/coders_out/).
- Ollama 모델: [`Modelfile`](Modelfile).

## 8) 배포 스크립트
- [`scripts/setup_env.sh`](scripts/setup_env.sh): nvm이 있으면 Node 23을 설치/전환하고 pnpm을 활성화한 뒤 frontend deps를 설치, 리눅스 Tauri 전제 조건을 출력합니다.
- [`scripts/bootstrap.sh`](scripts/bootstrap.sh): Python/pnpm/Cargo/PyInstaller 준비 상태를 점검하고 Ollama 안내를 제공합니다.
- [`scripts/run_tauri_dev.sh`](scripts/run_tauri_dev.sh): `.nvmrc` 기준 Node를 로드하고 pnpm deps를 확인한 뒤 `pnpm exec tauri dev`를 실행합니다(cargo-tauri 폴백 포함).
- [`scripts/dev_tauri.sh`](scripts/dev_tauri.sh): PyInstaller로 `bridge-cli`를 빌드한 뒤 프론트엔드 의존성을 확인하고 `pnpm exec tauri dev`로 개발 서버를 올립니다.
- [`scripts/build_tauri.sh`](scripts/build_tauri.sh): 동일한 파이프라인으로 `pnpm exec tauri build`(cargo-tauri 폴백 포함)로 OS별 배포 산출물을 생성합니다. 두 스크립트 모두 pnpm이 없거나 deps가 없으면 설치를 시도합니다.

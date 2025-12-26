# Discord Bridge (멀티언어/타임존 Discord 요약·배포 툴)

이 문서는 영어 README([`README.md`](README.md))를 기준으로 대한민국 독자를 위해 번역한 자료입니다. 영어 원문이 최신이며, 아래 내용은 같은 흐름을 한국어로 다시 설명합니다.

## 주요 기능
- Discord 채팅을 분석해 요약, FAQ, 도움 상호작용, 액션 아이템 등의 구조화된 Markdown 리포트를 생성합니다.
- `bridge/providers`에서 OpenAI/Google Gemini/Ollama 공급자를 추상화해 LLM을 쉽게 교체할 수 있습니다.
- Markdown 저장 + SMTP 발송을 CLI로 자동 실행하며 `--dry-run`/`--no-email` 플래그로 동작을 제어합니다.
- PyInstaller + Tauri를 엮은 데스크톱 셸과 스케줄 탭/“지금 실행” 버튼/`.env` 내보내기 계획을 갖추고 있습니다.

## 의존성 (CLI + UI)
- Node 23 (`nvm install 23 && nvm use 23`; `.nvmrc` 제공) + pnpm (`corepack enable && corepack prepare pnpm@latest --activate`).
- Python 3.8+
- `requirements.txt`에 나열된 패키지: `openai`, `google-generativeai`, `python-dateutil`, `rich`, `pydantic`, `requests`.
- Ollama는 선택 사항이며, legacy `summarize.py` 또는 로컬 제공자(`bridge/providers/ollama_provider.py`)를 쓸 때 필요합니다. [`Modelfile`](Modelfile)에서 추천 모델 스펙을 확인하세요.
- 리눅스에서 Tauri를 빌드하려면 webkit2gtk + librsvg가 필요합니다(Fedora/Bazzite 예: `sudo dnf install webkit2gtk4.1-devel librsvg2-devel`).

## 설치 및 부트스트랩
1. 저장소를 클론합니다.
2. `./scripts/setup_env.sh`(권장): nvm이 있으면 Node 23 설치/전환, pnpm 활성화, `frontend` 의존성 설치, Tauri 리눅스 전제 조건 안내.
3. `./scripts/bootstrap.sh`: Python 의존성, PyInstaller, pnpm/Tauri 도구, Rust/Cargo를 점검하고 Ollama 설치 팁을 제공합니다.
4. Ollama를 사용할 경우 `scripts/run_ollama.sh`에 실행 권한(`chmod +x scripts/run_ollama.sh`)을 부여하세요.

## CLI 사용법
```
python -m bridge.cli -i samples/chat_export.json --config .env
```
- `--dry-run`은 Markdown/이메일 쓰기를 건너뛰고, `--no-email`은 SMTP를 생략하며, `--verbose`는 디버그 로그를 보여줍니다.
- `.env`에서 `LANG=ko` 또는 `LANG=en`을 설정하면 LLM 프롬프트에 언어 메타데이터가 전달됩니다. 그 외 값은 영어로 처리합니다.
- `-i`에 폴더를 넘기면 내부의 모든 `*.json`(채널 단위)을 순회합니다. `DISCORD_SERVERS` 항목이 `channel_ids`를 비워두면 `["*"]`로 처리됩니다.
- DiscordChatExporter 출력은 `python preprocess.py <input.json> <out_dir>` 또는 `python preprocess_hourly.py <input.json> <out_dir>`로 전처리하세요.

## Tauri 개발 & 배포
- 개발: `./scripts/run_tauri_dev.sh`(.nvmrc Node 23 + pnpm deps 확인 후 `pnpm exec tauri dev` 실행, cargo-tauri 폴백).
- 대안 개발: `scripts/dev_tauri.sh`는 PyInstaller로 `bridge-cli`를 빌드하고, 부족한 pnpm 의존성이 있으면 설치한 뒤 `pnpm exec tauri dev`를 실행합니다.
- 배포: `scripts/build_tauri.sh`는 같은 PyInstaller/Tauri 절차로 `msi`, `dmg`, `AppImage` 같은 플랫폼용 설치 파일을 생성합니다. 두 스크립트 모두 pnpm 설치를 자동 처리합니다.
- 수동: `cd frontend && pnpm install && pnpm run dev`로 Vite 개발 서버(1420)를 띄운 뒤 실행할 수 있습니다.

## 환경 변수 및 보안
- `.env.example`을 `.env`로 복사하고, `DISCORD_CLIENT_*`, `BOT_TOKEN`, `SMTP_*`, API 키 등 민감한 값을 채웁니다. `.env`는 커밋하지 마세요.
- `DISCORD_SERVERS`를 `{name, guild_id, channel_ids}` 배열로 설정하거나 `DISCORD_GUILD_IDS`/`DISCORD_CHANNEL_IDS`로 대체할 수 있습니다.
- `INPUT_DIR`/`OUTPUT_DIR`로 경로를 정하고, `SCHEDULE_CRON`과 `SCHEDULE_TYPE`(`daily|weekly|monthly|custom`)으로 스케줄 메타 정보를 제공합니다.
- `LLM_PROVIDER`, `LLM_MODEL`, 선택적으로 `LLM_API_KEY`/`LLM_BASE_URL`을 정의합니다. Ollama를 쓰면 `scripts/run_ollama.sh`로 `http://127.0.0.1:11434`를 워밍업하고 그 URL을 `LLM_BASE_URL`로 설정하세요.
- 로그에서는 자격 증명을 마스킹하므로, 키/패스워드를 코드에 남기지 마십시오.

## 문서 & 로드맵
- [`docs/manual.md`](docs/manual.md)는 영어 매뉴얼이며, Korean translation은 [`docs/manual.ko.md`](docs/manual.ko.md)에서 확인할 수 있습니다.
- [`docs/tauri_ui_plan.md`](docs/tauri_ui_plan.md), [`docs/dev-principles.md`](docs/dev-principles.md), [`docs/release_plan.md`](docs/release_plan.md), [`docs/plan.md`](docs/plan.md), `work-logs/luke/discord-summarizer/`는 모두 한글 문서로써 UI 설계, 개발 원칙, 배포 계획, 전체 계획, 작업 로그를 설명합니다.

## 커스터마이징
- Ollama 전용 요약 로직은 `summarize.py`에 정의되어 있으므로 prompt/챙크 크기/출력 제한을 조정해도 됩니다.
- `bridge/providers/*`에서 프롬프트나 JSON 필드를 바꾸면 출력 형식을 쉽게 변경할 수 있습니다.

## 기여하기
기여 환영합니다! PR을 열고 실행한 명령/테스트를 설명하며 관련 이슈나 문서(예: [`docs/manual.md`](docs/manual.md), [`docs/dev-principles.md`](docs/dev-principles.md))를 링크해 주세요.

# Discord Bridge Tauri UI & Packaging Plan

## 목표
- Electron등 별도 설치 없이 Tauri 번들 하나로 GUI를 제공하고 `bridge.cli`를 호출해서 요약+이메일 파이프라인을 실행.
- 사용자 설정(LLM, SMTP, Discord 서버, 스케줄, 언어)을 직관적으로 조작하고 `.env`를 생성/내보내기.
- 언어 토글(Korean/English)과 스케줄(Daily/Weekly/Monthly/Custom) 선택이 CLI 메타데이터에 반영되도록 하며, Markdown 미리보기/이메일 로그를 보여줌.

## UI 구조
1. **설정 탭**:  
   - Discord 서버 리스트(자동으로 `DISCORD_SERVERS` JSON) + 새 서버 추가/채널 입력  
   - LLM provider/model/API key/base URL + language selector (`LANG` ko/en)  
   - Input/output 폴더 경로 / Markdown 저장 옵션  
2. **이메일 탭**:  
   - SMTP host/port/credentials/TLS toggle  
   - From/to 설정, 테스트 전송 버튼(CLI `--dry-run` + sample)  
   - 전송 로그/실패 리트라이 표시  
3. **스케줄 탭**:  
   - Daily/Weekly/Monthly/Custom 선택  
   - 시간/요일/일자 + `SCHEDULE_CRON` 미리보기  
   - `SCHEDULE_TYPE` 설정과 내보내기 버튼(`.env` + optional cron expression)  
4. **Reports 탭**:  
   - 가장 최근 Markdown 요약 프리뷰  
   - “지금 실행” 버튼 (일시적으로 CLI `--dry-run` 또는 실제)  
   - 실행 로그/에러 표시 + 이메일 발송 상태

## CLI 연동
- Tauri backend (Rust)에서 `tauri::Command`로 `bridge.cli`를 호출하거나, 필요한 경우 Tauri가 PyInstaller 빌드된 CLI 바이너리를 shell 호출.
- Ollama 모델을 쓸 때는 `scripts/run_ollama.sh`를 별도 터미널에서 실행해 GPU/CPU fallback 서버를 띄운 다음, Tauri가 `LLM_BASE_URL=http://127.0.0.1:11434`을 호출하도록 합니다.
- 설정 변경 시 `.env` 템플릿 생성 후 `bridge.config.load_env_file`이 읽도록, GUI는 `.env` 복사본을 `src-tauri/bin` 아래 CLI가 읽는 위치에 저장.
- “지금 실행”/스케줄러 작업은 내부적으로 CLI를 `std::process::Command`로 실행.

## 시각/언어
- GUI는 기본 한국어 UI이며, 상단 언어 드롭다운에서 “English” 선택 시 `LANG=en` + UI 텍스트도 영어로 전환.
- Tauri UI는 `react-i18next` 또는 유사한 i18n 라이브러리를 사용해 각 라벨/툴팁을 나누고, `LANG` selector와 동기화.

## 패키징
1. PyInstaller로 Python CLI 배포: `bridge.cli`, providers, `.env`, `tauri` helpers를 하나의 실행 파일로 만든 뒤 `src-tauri/bin`에 포함.  
2. Tauri 빌드: `tauri.conf.json`에서 `bundle.active = true`, `package.binary = "bridge-cli"` 를 지정.  
3. 빌드 결과물 - Windows `.msi`, macOS `.dmg`, Linux `.AppImage`/`.deb` - 에서 Python 바이너리가 호출 가능하도록 상대 경로 설정.  
4. 각 플랫폼 별 서명/스토어 제출 절차는 `docs/release_plan.md` 참조.

## 테스트 전략
- UI는 Storybook/Tauri dev server로 확인, “지금 실행” 버튼은 PyInstaller binary를 mock/stub 하여 테스트.  
- 언어/스케줄/SMTP 설정 UI는 단위 테스트(React Testing Library)로 `lang`/`schedule_type` metadata 생성 검증.

## 다음 단계
1. Tauri 템플릿 생성 (`pnpm create tauri-app`), React 폴더 구조 설정.  
2. Settings form + CLI runner component 구현.  
3. Storybook/Playwright로 실행 시나리오 테스트.  
4. PyInstaller 빌드 스크립트와 Tauri config을 조합하여 Windows/macOS/Linux용 빌드 파이프라인 구성.

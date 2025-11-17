## 상태 요약
- `scripts/build_tauri.sh`를 루트에서 실행하도록 유지하며 Tauri 설정을 명시적으로 지정 (`npx --package @tauri-apps/cli@1.5.11 tauri build -- --tauri-dir src-tauri -c src-tauri/tauri.conf.json`).
- `src-tauri/tauri.conf.json` 스키마 정리: `bundle` 구조 정돈, `allowlist.shell`에서 `scope` 제거 등으로 Tauri 스키마 오류 해소.
- PyInstaller 빌드 및 frontend 의존성 확인 단계는 반복 실행 시 모두 통과함.
- Tauri 빌드 단계에서 계속 `npm error … getaddrinfo EAI_AGAIN registry.npmjs.org`로 @tauri-apps/cli 패키지를 내려받지 못함. 같은 세션에서 `curl -I https://registry.npmjs.org/@tauri-apps/cli`는 HTTP 200까지 도달했으나 npm 프로세스에서는 DNS 해석이 실패하는 상태.

## 다음에 할 일
1) npm 경로 재확인: `npm config get registry` 확인 후 필요 시 `npm config set registry https://registry.npmjs.org/`.  
2) npm 레지스트리 연결 테스트: `npm ping --registry=https://registry.npmjs.org/` 실행. 성공하면 다시 `scripts/build_tauri.sh` 재시도.  
3) 그래도 `EAI_AGAIN`이면, 네트워크가 정상인 환경에서 `npm install --prefix frontend @tauri-apps/cli@1.5.11`로 `frontend/node_modules`를 미리 채워 이 워크스페이스에 복사한 뒤 `scripts/build_tauri.sh` 실행(설치된 CLI를 재사용).  
4) 추가 확인 시 `npx --yes @tauri-apps/cli@1.5.11 tauri --version`을 단독 실행해 다운로드/캐시가 되는지 체크.

## 참고 문서
- `AGENTS.md`: 리포지토리 전반의 작업 규칙 및 빌드/테스트 지침.
- `docs/architecture.md`, `docs/architecture.ko.md`: 스택 개요 및 구조 참고.
- `scripts/build_tauri.sh`: 현재 빌드 플로우 스크립트.
- `src-tauri/tauri.conf.json`: Tauri 설정 및 번들/플랫폼 구성을 정의.

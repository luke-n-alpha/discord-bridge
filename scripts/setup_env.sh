#!/usr/bin/env bash
# Discord Bridge 환경 설정 스크립트
# - Node 23 + pnpm 활성화(corepack)
# - 프런트엔드 의존성 설치
# - 리눅스 Tauri 필수 패키지 안내(dnf/apt/pacman 감지)
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

NVM_RC_VERSION="${NVM_RC_VERSION:-23}"
NODE_VERSION="${NODE_VERSION:-$NVM_RC_VERSION}"

ensure_nvm() {
  if command -v nvm >/dev/null 2>&1; then
    return 0
  fi
  if [ -s "$HOME/.nvm/nvm.sh" ]; then
    # shellcheck source=/dev/null
    . "$HOME/.nvm/nvm.sh"
    return 0
  fi
  echo "[경고] nvm을 찾지 못했습니다. Node ${NODE_VERSION} 설치/전환은 건너뜁니다." >&2
  return 1
}

echo "▶ Node(${NODE_VERSION}) + pnpm 준비"
if ensure_nvm; then
  nvm install "$NODE_VERSION"
  nvm use "$NODE_VERSION"
fi
corepack enable
corepack prepare pnpm@latest --activate

echo "▶ 프런트엔드 의존성 설치 (pnpm install)"
if [ -d "$ROOT/frontend" ]; then
  (cd "$ROOT/frontend" && pnpm install)
else
  echo "[경고] frontend 디렉터리를 찾지 못했습니다. 프런트엔드 설치를 건너뜁니다." >&2
fi

echo "▶ Tauri 리눅스 필수 패키지 확인"
if command -v dnf >/dev/null 2>&1; then
  echo "  - dnf 기반: sudo dnf install webkit2gtk4.1-devel librsvg2-devel"
elif command -v apt-get >/dev/null 2>&1; then
  echo "  - apt 기반: sudo apt-get install libwebkit2gtk-4.0-dev libssl-dev libgtk-3-dev librsvg2-dev"
elif command -v pacman >/dev/null 2>&1; then
  echo "  - pacman 기반: sudo pacman -S webkit2gtk-4.1 librsvg"
else
  echo "[안내] 패키지 관리자(dnf/apt/pacman)를 찾지 못했습니다. Tauri 전제 조건은 수동으로 설치하세요." >&2
fi

echo "완료: Node ${NODE_VERSION}, pnpm 설치 및 frontend 의존성 준비가 끝났습니다."

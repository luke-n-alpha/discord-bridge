#!/usr/bin/env bash
# Discord Bridge Tauri 개발 실행 스크립트
# - Node 23(.nvmrc) + pnpm 환경 로드
# - frontend deps 보장 후 tauri dev 실행
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FRONTEND_DIR="$ROOT/frontend"

load_nvm() {
  if command -v nvm >/dev/null 2>&1; then
    return 0
  fi
  if [ -s "$HOME/.nvm/nvm.sh" ]; then
    # shellcheck source=/dev/null
    . "$HOME/.nvm/nvm.sh"
    return 0
  fi
  return 1
}

echo "▶ Node(.nvmrc) 로드"
if load_nvm; then
  if [ -f "$ROOT/.nvmrc" ]; then
    nvm install "$(cat "$ROOT/.nvmrc")"
    nvm use "$(cat "$ROOT/.nvmrc")"
  fi
else
  echo "[경고] nvm을 찾지 못했습니다. 현재 Node를 그대로 사용합니다." >&2
fi

echo "▶ pnpm 준비"
corepack enable
corepack prepare pnpm@latest --activate

echo "▶ 프런트엔드 의존성 확인"
if [ ! -d "$FRONTEND_DIR/node_modules" ]; then
  (cd "$FRONTEND_DIR" && pnpm install)
fi

echo "▶ Tauri dev 실행"
cd "$FRONTEND_DIR"
pnpm exec tauri dev --config ../src-tauri/tauri.conf.json "$@"

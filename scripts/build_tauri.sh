#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"

if ! command -v pyinstaller >/dev/null 2>&1; then
  echo "PyInstaller가 필요합니다. pip install pyinstaller 후 다시 시도합니다." >&2
  python3 -m pip install --user pyinstaller
fi
if ! command -v cargo >/dev/null 2>&1; then
  echo "[자동 설치] Rust/Cargo가 없어 rustup을 설치합니다..."
  curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
  export PATH="$HOME/.cargo/bin:$PATH"
  if ! command -v cargo >/dev/null 2>&1; then
    echo "[중단] cargo를 찾을 수 없습니다. rustup 설치를 수동으로 확인하세요." >&2
    exit 1
  fi
fi

ensure_frontend_deps() {
  if ! command -v npm >/dev/null 2>&1; then
    echo "[중단] npm이 필요합니다. Node.js를 설치하세요." >&2
    exit 1
  fi
  if [ ! -d "$ROOT/frontend/node_modules" ]; then
    echo "▶ frontend 의존성 설치"
    (cd "$ROOT/frontend" && npm install)
  fi
}

echo "▶ bridge-cli PyInstaller 빌드"
python scripts/build_pyinstaller.py -o src-tauri/bin

echo "▶ frontend 의존성 확인"
ensure_frontend_deps

echo "▶ Tauri 배포 빌드 (msi/dmg/AppImage 등)"
npx --package @tauri-apps/cli@1.5.11 tauri build -- --tauri-dir src-tauri -c src-tauri/tauri.conf.json

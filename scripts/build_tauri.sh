#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"
PYTHON_BIN="python3"

check_linux_prereqs() {
  if [ "$(uname -s)" != "Linux" ]; then
    return
  fi
  if ! ldconfig -p 2>/dev/null | grep -q "libwebkit2gtk-4.0"; then
    echo "[경고] libwebkit2gtk-4.0(.so) 라이브러리를 찾지 못했습니다. 최신 Bazzite/Fedora는 4.1만 제공해 Tauri 빌드/실행 시 'No such file or directory' 오류가 날 수 있습니다." >&2
    echo "        webkit2gtk-4.0 호환 패키지를 설치하거나 4.1 → 4.0 호환 심링크를 준비해 주세요." >&2
  fi
  if ! ldconfig -p 2>/dev/null | grep -q "librsvg-2"; then
    echo "[경고] librsvg-2(.so) 라이브러리를 찾지 못했습니다. 리눅스에서 아이콘 변환에 필요합니다." >&2
  fi
}

check_linux_prereqs

ensure_pyinstaller() {
  if "$PYTHON_BIN" -m PyInstaller --version >/dev/null 2>&1; then
    return
  fi
  echo "PyInstaller가 필요합니다. 로컬 venv에 설치합니다." >&2
  if [ ! -d "$ROOT/.venv" ]; then
    "$PYTHON_BIN" -m venv "$ROOT/.venv"
  fi
  PYTHON_BIN="$ROOT/.venv/bin/python"
  "$PYTHON_BIN" -m pip install --upgrade pip >/dev/null
  "$PYTHON_BIN" -m pip install pyinstaller
}
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
  if ! command -v pnpm >/dev/null 2>&1; then
    echo "[중단] pnpm이 필요합니다. Node.js(>=23)를 설치하세요." >&2
    exit 1
  fi
  if [ ! -d "$ROOT/frontend/node_modules" ]; then
    echo "▶ frontend 의존성 설치"
    (cd "$ROOT/frontend" && pnpm install)
  fi
}

echo "▶ bridge-cli PyInstaller 빌드"
ensure_pyinstaller
"$PYTHON_BIN" scripts/build_pyinstaller.py -o src-tauri/bin

target_triple=""
if command -v rustc >/dev/null 2>&1; then
  target_triple="$(rustc -vV | sed -n 's/^host: //p')"
fi
if [ -n "$target_triple" ]; then
  cp -f "src-tauri/bin/bridge-cli" "src-tauri/bin/bridge-cli-$target_triple"
fi

echo "▶ frontend 의존성 확인"
ensure_frontend_deps

echo "▶ Tauri 배포 빌드 (msi/dmg/AppImage 등)"
cd "$ROOT/frontend"
pnpm install
pnpm run build
ln -sfn ../src-tauri src-tauri
ln -sfn ../icons icons
if ! pnpm exec tauri build --config "$ROOT/src-tauri/tauri.conf.json"; then
  echo "[경고] pnpm exec tauri build 실패. cargo-tauri로 재시도합니다."
  if command -v cargo-tauri >/dev/null 2>&1; then
    cargo-tauri build --config "$ROOT/src-tauri/tauri.conf.json"
  else
    echo "[중단] cargo-tauri를 찾을 수 없습니다. pnpm/tauri 설치를 다시 확인하세요." >&2
    exit 1
  fi
fi

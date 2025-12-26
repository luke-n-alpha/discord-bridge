#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

# PATH 보완(사용자 설치 경로)
export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"

# 라이브러리 경로 보완 (webkit2gtk-4.0 심링크 등)
if [ -d "$ROOT/libs" ]; then
  echo "[Info] 로컬 라이브러리($ROOT/libs)를 LD_LIBRARY_PATH에 추가합니다."
  export LD_LIBRARY_PATH="$ROOT/libs:${LD_LIBRARY_PATH:-}"
fi

check_linux_prereqs() {
  if [ "$(uname -s)" != "Linux" ]; then
    return
  fi
  if ! ldconfig -p 2>/dev/null | grep -q "libwebkit2gtk-4.0"; then
    echo "[경고] libwebkit2gtk-4.0(.so) 라이브러리를 찾지 못했습니다. 최신 Bazzite/Fedora는 4.1만 제공해 Tauri에서 'No such file or directory' 오류가 날 수 있습니다." >&2
    echo "        webkit2gtk-4.0 호환 패키지(예: sudo dnf install webkit2gtk4.0-devel) 또는 4.0 심링크를 준비해 주세요." >&2
  fi
  if ! ldconfig -p 2>/dev/null | grep -q "librsvg-2"; then
    echo "[경고] librsvg-2(.so) 라이브러리를 찾지 못했습니다. 리눅스에서 아이콘 변환에 필요합니다." >&2
  fi
}

check_linux_prereqs

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
  if ! command -v pnpm >/dev/null 2>&1; then
    echo "[중단] pnpm이 필요합니다. Node.js(>=23) 설치 후 corepack enable && corepack prepare pnpm@10.22.0 --activate 하세요." >&2
    exit 1
  fi
  if [ ! -d "$ROOT/frontend/node_modules" ]; then
    echo "▶ frontend 의존성 설치"
    (cd "$ROOT/frontend" && pnpm install)
  fi
}

echo "▶ bridge-cli PyInstaller 빌드"
python scripts/build_pyinstaller.py -o src-tauri/bin

echo "▶ frontend 의존성 확인"
ensure_frontend_deps

echo "▶ 프론트엔드 개발 모드 실행 (Tauri dev)"
cd "$ROOT/frontend"
pnpm install
ln -sfn ../src-tauri src-tauri
ln -sfn ../icons icons

# 1) pnpm으로 실행
if ! pnpm exec tauri dev --config "$ROOT/src-tauri/tauri.conf.json"; then
  echo "[경고] pnpm exec tauri dev 실패. cargo-tauri로 재시도합니다."
  if command -v cargo-tauri >/dev/null 2>&1; then
    cargo-tauri dev --config "$ROOT/src-tauri/tauri.conf.json"
  else
    echo "[중단] cargo-tauri를 찾을 수 없습니다. pnpm/tauri 설치를 다시 확인하세요." >&2
    exit 1
  fi
fi

#!/usr/bin/env bash
# 필수 도구/패키지를 점검하고 필요한 경우 설치를 시도합니다.
# 주의: 시스템 패키지 설치는 사용자의 권한/환경에 따라 실패할 수 있으며, 실패 시 안내만 표시합니다.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

# PATH 보완
export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"

function has_cmd() { command -v "$1" >/dev/null 2>&1; }

echo "▶ Python 패키지 설치 (requirements.txt)"
if ! has_cmd python3; then
  echo "[경고] python3 가 없습니다. 설치 후 다시 실행하세요." >&2
else
  python3 -m pip install --upgrade pip
  python3 -m pip install -r requirements.txt
  # PyInstaller 필요 시 설치
  if ! has_cmd pyinstaller; then
    python3 -m pip install --user pyinstaller
  fi
fi

echo "▶ Node/pnpm 점검 및 frontend deps 설치"
if ! has_cmd pnpm; then
  echo "[경고] pnpm이 없습니다. Node.js(>=23)를 설치한 뒤 corepack enable && corepack prepare pnpm@10.22.0 --activate 또는 npm i -g pnpm 으로 설치하세요." >&2
else
  (cd frontend && pnpm install)
  # 로컬 tauri-cli 확인
  pnpm --dir frontend exec tauri -V >/dev/null 2>&1 || echo "[경고] tauri CLI가 보이지 않습니다. pnpm install 상태를 다시 확인하세요." >&2
fi

echo "▶ Rust/Cargo 점검 (tauri dev/build에 필요)"
if ! has_cmd cargo; then
  echo "[자동 설치] cargo가 없어 rustup을 설치합니다 (사용자 홈에 설치)."
  curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
  export PATH="$HOME/.cargo/bin:$PATH"
  if ! has_cmd cargo; then
    echo "[경고] cargo를 여전히 찾지 못했습니다. rustup 설치를 수동으로 확인하세요: https://www.rust-lang.org/tools/install" >&2
  fi
fi

echo "▶ Ollama 점검 (선택)"
if ! has_cmd ollama; then
  echo "[안내] Ollama가 없습니다. 로컬 모델을 쓰려면 https://ollama.ai/download 에서 설치 후 scripts/run_ollama.sh를 실행하세요." >&2
fi

echo "완료. 다음 단계: 필요 시 ./scripts/run_ollama.sh, python scripts/build_pyinstaller.py -o src-tauri/bin, pnpm --dir frontend exec tauri dev/build."

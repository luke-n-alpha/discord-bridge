#!/usr/bin/env bash
# Start Ollama serve and warm up a model with GPU fallback.
set -euo pipefail

MODEL="${MODEL:-gpt-oss:20b}"
HOST="${HOST:-127.0.0.1}"
PORT="${PORT:-11434}"
LOG_FILE="${LOG_FILE:-/tmp/ollama-discord-bridge.log}"

export OLLAMA_HOST="${HOST}:${PORT}"

function stop_server() {
  if [[ -f "${LOG_FILE}.pid" ]]; then
    local pid
    pid=$(cat "${LOG_FILE}.pid")
    if kill -0 "$pid" >/dev/null 2>&1; then
      kill "$pid" >/dev/null 2>&1 || true
    fi
    rm -f "${LOG_FILE}.pid"
  fi
}

trap stop_server EXIT

echo "Starting Ollama serve at ${OLLAMA_HOST} (model: ${MODEL})" | tee "$LOG_FILE"
ollama serve >>"$LOG_FILE" 2>&1 &
echo $! > "${LOG_FILE}.pid"

sleep 3
if ! curl --silent --fail "http://${OLLAMA_HOST}/api/tags" >/dev/null 2>&1; then
  echo "Ollama serve not responding at http://${OLLAMA_HOST}" | tee -a "$LOG_FILE"
fi

echo "Warming up model ${MODEL} (GPU auto if available, otherwise CPU) ..." | tee -a "$LOG_FILE"
if ! ollama run "$MODEL" <<<"ping" >>"$LOG_FILE" 2>&1; then
  echo "Warmup failed for ${MODEL}. Check logs: $LOG_FILE" | tee -a "$LOG_FILE"
else
  echo "Ollama ready at http://${OLLAMA_HOST}" | tee -a "$LOG_FILE"
fi

echo "Press Ctrl+C to stop."
wait

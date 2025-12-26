# Architecture Overview

This document captures the current Discord Bridge architecture so reviewers know where the major layers live and which artifacts to update when the stack shifts.  
Keep this file in sync with `README.md`, `docs/manual.md`, and the `bridge/` code whenever components move or new runtime paths appear.

## Core Layers
- **CLI layer (`bridge/`)**: `bridge.cli` orchestrates `.env` loading, the provider factory, the pipeline, and SMTP sending. Config validation lives in `bridge/config.py`, and shared dataclasses/summaries are defined in `bridge/llm.py`.
- **LLM providers (`bridge/providers/`)**: Each provider implements `LLMProvider` (OpenAI, Google Gemini, Ollama). Providers receive formatted transcripts, issue prompts, and return the structured `LLMAnalysis` objects that the pipeline converts to Markdown.
- **Tauri front-end (`frontend/` + `src-tauri/`)**: React/Vite UI lets users manage `.env`, pick `LANG/SCHEDULE_TYPE`, and trigger `bridge-cli` via the Rust bridge in `src-tauri/bin`. UI assets live in `frontend/src`, and the Rust shim bundles the PyInstaller binary from `src-tauri/bin`.

## Data Flow
1. Discord exports are optionally preprocessed (`preprocess.py`, `preprocess_hourly.py`) into clean JSON chunks.
2. `bridge.cli` collects input paths, loads `.env` through `bridge.config.load_env_file`, instantiates the requested provider, and runs `bridge.pipeline.run_pipeline`.
3. `run_pipeline` formats messages, calls the provider, and writes Markdown. Email content/attachments are passed to `bridge.emailer.send_email` unless `--dry-run`/`--no-email` are set.
4. The CLI can be bundled via `scripts/build_pyinstaller.py` and invoked by Tauri or other orchestrators.

## Deployment & Tooling
- `scripts/bootstrap.sh` ensures Python deps, pnpm/Tauri tooling, PyInstaller, and Rust/Cargo are ready.
- `scripts/dev_tauri.sh` and `scripts/build_tauri.sh` run PyInstaller, install frontend deps if needed, and execute `npx @tauri-apps/cli@1.5.11 tauri dev/build`.
- Ollama users run `scripts/run_ollama.sh` to start `ollama serve`, warm the model, and point `LLM_BASE_URL` at `http://127.0.0.1:11434`. `Modelfile` tracks the recommended local model.

## Configuration & Scheduling
- `.env` defines Discord servers, directories (`INPUT_DIR`, `OUTPUT_DIR`), LLM settings, SMTP credentials, and schedule metadata (`SCHEDULE_CRON`, `SCHEDULE_TYPE`, `LANG`, `TIMEZONE`).
- `bridge.config.load_config()` enforces required keys, normalizes `SCHEDULE_TYPE`, and supports `DISCORD_SERVERS` JSON or legacy guild/channel lists.
- `SCHEDULE_TYPE` informs the UI scheduler pickers described in `docs/tauri_ui_plan.md`.

## Observability & Testing Notes
- Logs come from `bridge.cli`/`bridge.pipeline` and respect `--verbose`. Secured values are masked whenever SMTP/LLM secrets appear.
- `tests/` covers CLI, config, emailer, pipeline, and provider contracts.
- Update this architecture doc whenever you add new layers (e.g., REST endpoints, additional UI shelling, or new provider paths) so `AGENTS.md` and `README.md` can keep referencing the right sources.

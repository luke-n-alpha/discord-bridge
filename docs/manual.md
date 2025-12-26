# Discord Bridge Desktop Manual (Tauri + Python)

This manual explains how the existing Python summarizer and Tauri UI fit together, the supported environment schema, and the CLI/Tauri workflows that are available today. The Korean translation lives in [`docs/manual.ko.md`](docs/manual.ko.md).

## Architecture Overview
- **Frontend**: Tauri (React/Vite) shells the experience for Windows, macOS, and Linux (MSI, DMG, AppImage, etc.).
- **Backend**: Python workflow covers Discord preprocessing, LLM analysis, Markdown report generation, and SMTP delivery. PyInstaller bundles the Python engine so Tauri can execute a single binary.
- **Invocation**: Tauri either shells the bundled binary or (future) communicates over a local HTTP endpoint when necessary.

- Node 23 (use `nvm install 23 && nvm use 23`; `.nvmrc` is provided) and pnpm (`corepack enable && corepack prepare pnpm@latest --activate`). Linux Tauri requires webkit2gtk-4.0 + librsvg; Fedora/Bazzite often ships only 4.1, so install the 4.0 compatibility packages (e.g., `sudo dnf install webkit2gtk4.0-devel librsvg2-devel`) and verify with `ldconfig -p | grep webkit2gtk-4.0`.
- Python 3.8+
- `requirements.txt`: `openai`, `google-generativeai`, `python-dateutil`, `rich`, `pydantic`, `requests`.
- Optional: Ollama if you rely on `summarize.py` or the local provider (`bridge/providers/ollama_provider.py`). [`Modelfile`](Modelfile) contains the preferred local model spec.

## Environment Configuration
- Copy `.env.example` to `.env` and fill in credentials locally (`DISCORD_CLIENT_ID`, `DISCORD_BOT_TOKEN`, `SMTP_PASSWORD`, etc.). Never commit `.env`.
- You may define `DISCORD_SERVERS` as a JSON array of `{name, guild_id, channel_ids}` objects; omit `channel_ids` to default to `["*"]`. Legacy fields `DISCORD_GUILD_IDS`/`DISCORD_CHANNEL_IDS` are still accepted.
- Paths: `INPUT_DIR`, `OUTPUT_DIR`; schedule metadata: `SCHEDULE_CRON`, `SCHEDULE_TYPE` (`daily|weekly|monthly|custom`); localization: `LANG`, `TIMEZONE`.
- LLM settings: `LLM_PROVIDER`, `LLM_MODEL`, optional `LLM_API_KEY`, `LLM_BASE_URL`. Ollama users should run [`scripts/run_ollama.sh`](scripts/run_ollama.sh) so `http://127.0.0.1:11434` stays warm.
- SMTP hosts/plugins: define `SMTP_HOST`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`, `SMTP_USE_TLS`, `FROM_EMAIL`, `TO_EMAILS`.
- Logs and CLI commands mask secrets automatically.

## Supported Features
- The CLI pipeline presently handles transcript chunking, analysis (summary/FAQ/help interactions/action items), Markdown formatting, and optional SMTP dispatches.
- Providers for OpenAI, Google Gemini, and Ollama sit under `bridge/providers/` and implement the `LLMProvider` contract.
- CLI flags include `--dry-run`, `--no-email`, and `--verbose` for controlling writes and logging.
- Scheduling is governed by cron expressions plus the normalized `SCHEDULE_TYPE`.

## CLI Workflow
1. Install dependencies (see [`requirements.txt`](requirements.txt)):
```
pip install langchain_ollama python-dateutil rich pydantic requests
```
   - Add `langchain-openai` or `langchain-google-vertexai` if you need those provider helpers.
2. Preprocess exports (daily or hourly):
```
python preprocess.py <input.json> <out_dir>
python preprocess_hourly.py <input.json> <out_dir>
```
3. Generate summaries:
```
python summarize.py -i chat_YYYY-MM-DD.json -o report.md
python summarize-qa.py -i chat_YYYY-MM-DD.json -o qa.md
```
4. Orchestrate via `bridge.cli` (runs preprocess → summary → Markdown → email):
```
python -m bridge.cli -i <json/folder> --config .env [--dry-run] [--no-email] [--verbose]
```

## CLI + GUI Integration
- Tauri will eventually surface tabs for Settings/Input, LLM, Email, Schedule, and Logs/Status.
- The GUI manages `.env` serialization, schedule pickers, and calls `bridge-cli` via `src-tauri/bin`.
- “Run Now” triggers the same CLI flow with the current configuration.
- “Export .env” saves the schedule/LLM/email settings with the cron expression embedded ([`.env.example`](.env.example) provides a template).

## Schedule Controls
- Scheduler options: daily (HH:MM), weekly (weekday + HH:MM), monthly (day + HH:MM), or custom cron. Default suggestions are Monday 09:00 for weekly and 1st 09:00 for monthly.
- Set `SCHEDULE_TYPE` in `.env` to match the GUI selection; the loader enforces allowed values.

### Example `.env`
```
SCHEDULE_CRON=0 9 * * *
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=you@example.com
SMTP_PASSWORD=app_password
SMTP_USE_TLS=true
FROM_EMAIL=you@example.com
TO_EMAILS=team@example.com,me@example.com
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o-mini
LLM_API_KEY=sk-...
INPUT_DIR=/path/to/logs
OUTPUT_DIR=/path/to/reports
LANG=ko
TIMEZONE=Asia/Seoul
```

## Deployment Scripts
- [`scripts/setup_env.sh`](scripts/setup_env.sh): installs Node 23 via nvm (if present), enables pnpm, installs frontend deps, and prints Linux Tauri prerequisites.
- [`scripts/bootstrap.sh`](scripts/bootstrap.sh): validates Python/pnpm/Cargo/PyInstaller and guides through Ollama.
- [`scripts/run_tauri_dev.sh`](scripts/run_tauri_dev.sh): loads Node from `.nvmrc`, ensures pnpm deps, and runs `pnpm exec tauri dev` (cargo-tauri fallback).
- [`scripts/dev_tauri.sh`](scripts/dev_tauri.sh): builds the Python binary, installs frontend deps (if missing), and runs `pnpm exec tauri dev`.
- [`scripts/build_tauri.sh`](scripts/build_tauri.sh): same pipeline but uses `pnpm exec tauri build` (with cargo-tauri fallback) to produce distributables for each OS. Both scripts manage pnpm installs when `node_modules` is absent.
- [`scripts/run_ollama.sh`](scripts/run_ollama.sh): starts `ollama serve`, preloads the model, and keeps the HTTP endpoint ready.

## Milestones
1. Finalize env schema + SMTP utilities.
2. Harden provider abstractions and error handling.
3. Compose CLI orchestrator (preprocess → summarize → save → email).
4. PyInstaller build helpers (Windows/macOS/Linux).
5. Tauri UI tabs, “Run now”, “Export env”, logs.

## References
- [`samples/`](samples/) and [`samples/coders_out/`](samples/coders_out/) hold example transcripts and outputs.
- [`Modelfile`](Modelfile) documents the recommended Ollama model configuration.
- Korean living documents: [`docs/tauri_ui_plan.md`](docs/tauri_ui_plan.md), [`docs/dev-principles.md`](docs/dev-principles.md), [`docs/release_plan.md`](docs/release_plan.md), [`docs/plan.md`](docs/plan.md), and `work-logs/luke/discord-summarizer/`.

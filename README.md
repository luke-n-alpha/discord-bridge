# Discord Bridge (Multilingual/TZ-Aware Discord Briefing & Delivery)

This README is the primary English reference for the project. A full Korean translation is available in [`README.ko.md`](README.ko.md).

## Features
- Structured summaries (summary, FAQ, help interactions, action items) generated from Discord chat exports.
- LLM provider abstraction with OpenAI, Google Gemini, and Ollama implementations in `bridge/providers`.
- Markdown + SMTP workflow that can run headlessly (dry-run/no-email flags) or be bundled into Tauri.
- Desktop-scheduler vision: PyInstaller + Tauri packaging with scheduler tabs, “Run now”, and `.env` export tools.

## Dependencies (CLI + UI)
- Node 23 (use `nvm install 23 && nvm use 23`; `.nvmrc` is provided) and pnpm (`corepack enable && corepack prepare pnpm@latest --activate`).
- Python 3.8+
- `requirements.txt`: `openai`, `google-generativeai`, `python-dateutil`, `rich`, `pydantic`, `requests`.
- Optional: Ollama if you rely on `summarize.py` or the local provider (`bridge/providers/ollama_provider.py`). [`Modelfile`](Modelfile) contains the preferred local model spec.
- Linux Tauri prereqs: webkit2gtk + librsvg (e.g., `sudo dnf install webkit2gtk4.1-devel librsvg2-devel` on Fedora/Bazzite).

## Installation & Bootstrap
1. Clone the repository.
2. `./scripts/setup_env.sh` (recommended): installs Node 23 via nvm (if present), enables pnpm, installs `frontend` deps, and prints Tauri Linux prereqs.
3. `./scripts/bootstrap.sh`: installs Python deps, PyInstaller, pnpm/Tauri toolchain, Rust/Cargo, and gives Ollama pointers.
4. Make `scripts/run_ollama.sh` executable (`chmod +x scripts/run_ollama.sh`) before using Ollama locally.

## CLI Usage
```
python -m bridge.cli -i samples/chat_export.json --config .env
```
- Use `--dry-run` to skip file/email writes, `--no-email` to stop SMTP delivery, and `--verbose` for debug logging.
- Set `LANG=ko` or `LANG=en` (default `en`) in `.env` to influence the prompts; unsupported values fall back to English.
- The CLI accepts directories: it processes every `*.json` transcript inside and treats missing `channel_ids` in `DISCORD_SERVERS` as `["*"]`.
- Preprocess exports with `python preprocess.py <input.json> <out_dir>` or `python preprocess_hourly.py <input.json> <out_dir>` before invoking the orchestrator.

## Tauri Development & Release
- Dev: `./scripts/run_tauri_dev.sh` (uses .nvmrc Node 23, ensures pnpm deps, runs `pnpm exec tauri dev` with cargo-tauri fallback).
- Alt dev: `scripts/dev_tauri.sh` builds `bridge-cli` via PyInstaller, installs frontend deps if needed, and runs `pnpm exec tauri dev` (cargo-tauri fallback).
- Release: `scripts/build_tauri.sh` uses the same PyInstaller/Tauri pipeline to produce platform installers (`msi`, `dmg`, `AppImage`). Both scripts manage pnpm installs automatically.
- Manual: `cd frontend && pnpm install && pnpm run dev` to start the Vite dev server on port 1420.

## Environment Variables & Secrets
- Copy `.env.example` to `.env` and populate secrets (`DISCORD_CLIENT_*`, `BOT_TOKEN`, `SMTP_*`, API keys). Never commit `.env`.
- Configure Discord targets either via `DISCORD_SERVERS` (JSON array of `{name, guild_id, channel_ids}`) or fall back to `DISCORD_GUILD_IDS`/`DISCORD_CHANNEL_IDS`.
- Provide paths with `INPUT_DIR`/`OUTPUT_DIR`, cron metadata with `SCHEDULE_CRON`, and a normalized `SCHEDULE_TYPE` (`daily|weekly|monthly|custom`).
- Define `LLM_PROVIDER`, `LLM_MODEL`, optional `LLM_API_KEY`/`LLM_BASE_URL`. Ollama users should point `LLM_BASE_URL` to the warmed-up local server (default `http://127.0.0.1:11434`) after running `scripts/run_ollama.sh`.
- Logs mask credentials; keep API keys and passwords out of source control.

## Docs & Roadmap
- [`docs/manual.md`](docs/manual.md) walks through the architecture, CLI/Tauri workflows, scheduling, and deployment scripts. A Korean translation lives in [`docs/manual.ko.md`](docs/manual.ko.md).
- [`docs/tauri_ui_plan.md`](docs/tauri_ui_plan.md), [`docs/dev-principles.md`](docs/dev-principles.md), [`docs/release_plan.md`](docs/release_plan.md), [`docs/plan.md`](docs/plan.md), and `work-logs/luke/discord-summarizer/` remain Korean living documents describing UI plans, principles, release steps, and historical progress.

## Customization
- Adjust Ollama-specific guidance inside `summarize.py` (prompts, chunk size, structured output limits).
- Update the prompt/JSON mapping within `bridge/providers/*` if you need additional metadata or format tweaks.

## Contributing
Contributions welcome! Submit PRs, describe the commands/tests you ran, and link related issues or docs (e.g., [`docs/manual.md`](docs/manual.md), [`docs/dev-principles.md`](docs/dev-principles.md)).

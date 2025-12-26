# Repository Guidelines

## Primary Context (Read First)
- Always read `.caretrules/project_context.md` before any other docs; it is the authoritative AI context and maps 1:1 to `docs/project_context.ko.md`.

## Work Logs
- Document work logs in `work-logs/luke/discord-summarizer/01.todo`, `02.doing`, and `03.complete` using `YYYYMMDD-%2d-{topic}.md` (two-digit sequence per day).

## Project Structure & Module Organization
- `bridge/`: Python CLI engine, config loader, pipeline, emailer, and LLM provider factory.
- `frontend/` + `src-tauri/`: Vite/React UI plus Rust shim bundling the PyInstaller binary.
- `scripts/`: Supporting automation (`bootstrap.sh`, `run_ollama.sh`, `dev_tauri.sh`, `build_tauri.sh`, `build_pyinstaller.py`).
- `tests/`: `pytest` suites for CLI, config, emailer, pipeline, and providers.
- `docs/`: English/Korean manuals (`docs/manual.md`, `docs/manual.ko.md`), the architecture overview (`docs/architecture.md` plus `docs/architecture.ko.md`), and planning logs/roadmaps.
- [`docs/architecture.md`](docs/architecture.md) / [`docs/architecture.ko.md`](docs/architecture.ko.md) describe the overall stack; update both whenever the architecture shifts so this guide can stay accurate.

## Build, Test, and Development Commands
- `./scripts/bootstrap.sh` installs Python deps, PyInstaller, npm/Tauri tooling, and Rust/Cargo; run it before other scripts.
- `python -m bridge.cli -i samples/chat_export.json --config .env` runs the orchestrator; add `--dry-run`, `--no-email`, or `--verbose` if needed.
- `python preprocess.py` / `python preprocess_hourly.py` for preparing Discord exports.
- `scripts/dev_tauri.sh` and `scripts/build_tauri.sh` enforce PyInstaller → Tauri workflows, including npm installs when needed.
- `python -m pytest tests` executes the regression suite; use `-k` for targeted subsets.
- Ollama workflows depend on `scripts/run_ollama.sh` and the `Modelfile` model spec.

## Coding Style & Naming Conventions
- Python/CLI uses PEP 8 conventions (4-space indent, descriptive docstrings).
- Tests follow `test_*.py` naming; keep fixtures contextual.
- Frontend components adopt PascalCase, props/hooks use camelCase, logic lives in `frontend/src`.
- Environment variables are uppercase with underscores (e.g., `LLM_PROVIDER`, `LANG`, `SCHEDULE_TYPE`); never commit `.env`.

## Testing Guidelines
- Ensure `tests/conftest.py` is available for path injection when running `pytest`.
- Keep test assertions focused on pipeline outputs (summary, FAQ, help, action items, email payloads) rather than LLM internals.
- Add new tests next to the production modules they exercise (e.g., new provider ⇒ `tests/test_providers.py` updates).

## Commit & Pull Request Guidelines
- Use short imperative commits (see recent history for examples).
- PRs should summarize the change, reference commands/tests run, and link to relevant docs (`docs/manual.md`, `docs/plan.md`, etc.).
- Attach screenshots/logs when UI or CLI output changes; note `.env`/secret handling carefully.

## Security & Configuration Tips
- Copy `.env.example` into `.env`, populate credentials, and keep it out of source control.
- Ollama runs use `Modelfile`; make sure `scripts/run_ollama.sh` is executable and `LLM_BASE_URL` matches the warmed-up endpoint.
- Align `LANG`/`SCHEDULE_TYPE` between `.env` and the GUI scheduler pickers; invalid values are rejected by `bridge.config.load_config()`.

## AI Work Guide
- Before starting work, read `docs/ai-work-guide.md` (Phase 0 checklist), then pull only the docs matched to the task type.
- Maintain bilingual content: new prompts/UI/messages must support both `LANG=en|ko` and keep English as the safe fallback; update paired docs (`architecture*.md`, `manual*.md`, README/README.ko.md) together.
- Use level-based logging: Python `logging` with `DEBUG/INFO/WARNING/ERROR`, Rust `log/tracing`, and frontend minimal console logs; never surface secrets.

**Agent Notes:** Think and reason in English to minimize token usage, but always report progress and findings to the user in Korean.

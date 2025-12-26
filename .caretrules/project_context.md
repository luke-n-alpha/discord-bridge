# Project Context (AI, YAML)
project:
  name: Discord Summarizer (Bridge)
  goal: Summarize Discord chat exports and send email reports via desktop app.
  root: project root (use relative paths)
stack:
  core_runtime: Python 3.11+
  ui: React + Vite (TypeScript)
  desktop_shell: Tauri (Rust)
  packaging:
    - PyInstaller
    - Tauri bundler
  llm_providers:
    - OpenAI
    - Google Gemini
    - Ollama
modules:
  bridge: Python CLI, config, pipeline, emailer, provider factory
  frontend: React UI
  src_tauri: Rust shim and bundling
  scripts: automation (bootstrap, dev/build, ollama)
  tests: pytest suites
  docs: manuals, architecture, plans
architecture:
  layers:
    - CLI orchestrator (bridge.cli) loads env, builds provider, runs pipeline, sends email
    - Providers (bridge/providers) implement LLMProvider
    - Pipeline (bridge/pipeline) formats transcripts, calls provider, writes Markdown/email payload
    - Desktop shell (Tauri) invokes bundled CLI
  data_flow:
    - preprocess optional: preprocess.py / preprocess_hourly.py
    - CLI run: python -m bridge.cli -i <export.json> --config .env
    - pipeline: format -> provider -> markdown -> email
    - packaging: PyInstaller -> Tauri
principles:
  - separation_of_concerns: CLI pipeline, UI, and packaging stay decoupled
  - provider_abstraction: add/replace LLMs via LLMProvider interface
  - local_first_option: Ollama path supports local inference
  - config_driven: .env governs providers, schedules, and paths
  - secure_logs: secrets stay in .env; masked in logs
  - bilingual_ux: LANG en|ko with English fallback
  - tdd_first: write failing tests before implementation, then refactor
  - e2e_validation: major changes require at least one e2e scenario covering input->summary->save/send using sample data and mocked LLM/SMTP
  - reuse_before_new: analyze existing modules/utils/scripts before new code
  - structural_extension: use provider/pipeline/config extension points and avoid duplicate logic
  - no_hardcoding: move paths/models/lang/schedule/SMTP to .env or config layer
workflows:
  bootstrap: ./scripts/bootstrap.sh
  preprocess: python preprocess.py | python preprocess_hourly.py
  cli: python -m bridge.cli -i <export.json> --config .env
  tauri_dev: ./scripts/dev_tauri.sh
  tauri_build: ./scripts/build_tauri.sh
  tests: python -m pytest tests
  ollama: ./scripts/run_ollama.sh
  task_specs:
    path: work-logs/luke/discord-summarizer/01.todo
    filename: YYYYMMDD-%2d-{topic}.md
  work_logs:
    path: work-logs/luke/discord-summarizer/02.doing
    filename: YYYYMMDD-%2d-{topic}.md
    rule: use a two-digit sequence per day
  completed_logs:
    path: work-logs/luke/discord-summarizer/03.complete
    filename: YYYYMMDD-%2d-{topic}.md
doc_sync:
  ai_doc: .caretrules/project_context.md
  user_doc: docs/project_context.ko.md
  rule: update both docs together when tech stack or workflow changes; keep content 1:1
ai_usage:
  read_order:
    - .caretrules/project_context.md
    - AGENTS.md
    - task-specific docs
  format_rule: keep this file minimal, structured YAML, ASCII-only

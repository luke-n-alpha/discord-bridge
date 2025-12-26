# Discord Bridge Standalone Release Plan

## Objective
Ship Discord Bridge as a single installer per platform (Windows Marketplace, App Store, Bazzar/Linux) so users download and install without pre-requisite Python/LLM setups. The backend stays the CLI (`bridge.cli`), but the Tauri front-end wraps and exposes settings/scheduling.

## Packaging Strategy
1. **Python Engine**: Use PyInstaller to create native binaries per OS (Linux, Windows, macOS). Bundle the CLI, providers, and `.env` loader so the app is self-contained.
2. **Tauri Frontend**: Build with Tauri (Rust + React/Svelte). The UI:
   - loads/edits settings (LLM, SMTP, schedule, language)
   - shows logs/status
   - offers “Run now” and schedule selectors (daily/weekly/monthly/custom)
   - exports `.env` for CLI runs or cron
   - invokes the bundled Python binary via `tauri::command` or a local shell call.
3. **Installer Creation**:
   - Windows: Tauri builder produces `msi`/`exe`. Sign with EV cert, test on Windows 10/11, and package for Windows Marketplace submission (App Package manifest, privacy details about SMTP/LLM usage).
   - macOS: Tauri builder produces `dmg`/`pkg`. Code-sign with Apple Developer ID, notarize via `altool`, and submit to the App Store (or distribute outside via notarized `.dmg` if needed).
   - Linux/Bazzar: Build AppImage/DEB via Tauri. Provide snaps? Target the Bazzar marketplace by following its packaging requirements (AppStream metadata, icons, release notes).

## Release Process
1. Update `docs/manual.md` and `README` versions with release highlights (new languages, schedule).
2. Run `pytest -q` to confirm CLI/LLM/SMTP tests pass.
3. Run `scripts/build_pyinstaller.py` to produce the `bridge-cli` binary for each OS and embed it in the Tauri `src-tauri/bin` folder.
4. Configure Tauri manifests (`tauri.conf.json`) for each target, referencing the bundled binary.
5. Use `tauri build` per platform to generate installers.
6. Perform manual QA: run on each platform, validate CLI summary + email + language toggle + schedule functionality.
7. Sign/notarize per store: Windows EV cert, macOS Developer ID + notarization, Linux package signing if required.
8. Submit to stores with release notes, privacy/SMTP description, and contact info. Monitor feedback and shipping updates (patch updates via new installer builds).

## Store Notes
- **Windows Marketplace**: Provide MSI metadata, privacy/policy doc for Discord data access, and list SMTP usage. Provide instructions for auto-updates (if supported) via Tauri updater or manual downloads.
- **Apple App Store**: Fulfill App Review Guidelines around data privacy. Mention that Discord tokens live locally and email delivery uses user-provided SMTP credentials (no external data collection).
- **Bazzar (Linux Marketplace)**: Include AppStream metadata, icons, and release notes. Provide manual instructions for installing dependencies (e.g., `libwebkit2gtk`, if required by Tauri).

## Post-Release Tasks
- Monitor issue tracker for platform-specific bugs (window focus, tray behavior, filesystem permissions).  
- Update `.env.example`, docs, and release notes for new features (e.g., Ollama provider, multi-language).  
- Plan patch releases via Tauri builder and PyInstaller updates for each supported platform.

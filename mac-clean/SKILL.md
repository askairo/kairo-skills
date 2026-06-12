---
name: mac-clean
description: Safely clean macOS with two tracks: storage cleanup and zero-risk file organization, both with explicit safety boundaries and reporting.
---

# Mac Clean

Use this skill when the user asks to clean macOS storage or organize long-accumulated files. Default to low-risk actions and ask confirmation before high-impact changes.

## Goals

- Recover space quickly with repeatable, low-risk operations.
- Report before/after sizes for key directories.
- Keep personal data and system-critical areas untouched unless explicitly requested.
- Improve folder order without breaking app behavior or project runtimes.

## Safety Rules

- Do not delete personal folders by default: `~/Desktop`, `~/Documents`, `~/Pictures`, `~/Movies`, `~/Downloads`.
- Do not delete app/system trees by default: `/Applications`, `/System`, `/Library`.
- Do not touch SIP/protected system settings.
- Keep Codex runtime data untouched unless user explicitly asks.
- If macOS returns `Operation not permitted`, skip and continue. Report skipped paths.
- For organization tasks, never touch:
  - `~/Library`
  - `/Library`
  - `/System`
  - `/private/var`
- For project folders, move directories only. Do not edit file contents.

## Default Workflow (`safe`)

1. Baseline scan:
   - `du -sh ~/Library/Caches ~/Library/Logs ~/.npm ~/.m2 ~/.gradle ~/.Trash 2>/dev/null`
2. Clean low-risk caches:
   - `rm -rf ~/Library/Caches/*`
   - `rm -rf ~/Library/Logs/*`
   - `rm -rf ~/.npm/_cacache/*`
3. Verify:
   - Re-run baseline scan and report reclaimed size.

## Organization Workflow (`organize-safe`)

Use this mode when the user wants less chaos, not necessarily more free space.

1. Scan only user file zones:
   - `~/Downloads`, `~/Documents`, `~/Desktop`
   - Optional work roots like `~/IdeaProjects`, `~/vscodeSpace`
2. Create stable target structure:
   - `~/Workspace/{Projects,Documents,Media,Archive,Installers}`
3. Classify obvious loose files (no deletion):
   - `mp4/mov` -> media folder
   - `pdf/docx/txt/xmind/xml` -> typed document folders
4. Project hygiene:
   - Keep active projects in place.
   - Move clear temporary/history candidates into archive folders.
   - Keep a conservative first pass; avoid broad repo moves without user signal.
5. Record changes:
   - Write a migration log under `~/Workspace/Documents/` with moved paths and date.

## Aggressive Workflow (`aggressive`, explicit user request only)

Includes all `safe` steps, plus optional confirmed actions:

- Maven cache purge: `rm -rf ~/.m2/repository`
- Gradle cache purge: `rm -rf ~/.gradle/caches ~/.gradle/wrapper`
- Homebrew cleanup: `brew cleanup -s`
- Empty Trash: `rm -rf ~/.Trash/*`
- Docker cleanup: `docker system prune -a`

For each optional action, explain impact first and ask for clear confirmation.

## Mode Guide

- `safe`: storage cleanup only, low-risk cache/log cleanup.
- `aggressive`: deeper storage cleanup with explicit approval.
- `organize-safe`: no risky system touches; reorganize user files/projects only.

## Output Format

- `Before`: key path sizes
- `Actions`: what was deleted and what was skipped
- `After`: key path sizes
- `Recovered`: estimated reclaimed size
- `Next`: optional high-impact actions for approval
- `Moved`: list of directories/files moved during organization (if `organize-safe`)

## Notes

- On macOS, privacy-protected folders may require Full Disk Access.
- Cache cleanup is usually safe, but first app launch/build after cleanup may be slower.
- Prefer predictable cache directories over ad hoc file deletion.
- For organization, favor traceability over speed: log every move and preserve reversible structure.

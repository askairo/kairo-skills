---
name: mac-clean
description: Safely clean disk space on macOS with a safe-first workflow, optional aggressive steps, and clear before/after reporting.
---

# Mac Clean

Use this skill when the user asks to clean macOS storage. Default to low-risk cleanup first, then request explicit confirmation before high-impact deletion.

## Goals

- Recover space quickly with repeatable, low-risk operations.
- Report before/after sizes for key directories.
- Keep personal data and system-critical areas untouched unless explicitly requested.

## Safety Rules

- Do not delete personal folders by default: `~/Desktop`, `~/Documents`, `~/Pictures`, `~/Movies`, `~/Downloads`.
- Do not delete app/system trees by default: `/Applications`, `/System`, `/Library`.
- Do not touch SIP/protected system settings.
- Keep Codex runtime data untouched unless user explicitly asks.
- If macOS returns `Operation not permitted`, skip and continue. Report skipped paths.

## Default Workflow (`safe`)

1. Baseline scan:
   - `du -sh ~/Library/Caches ~/Library/Logs ~/.npm ~/.m2 ~/.gradle ~/.Trash 2>/dev/null`
2. Clean low-risk caches:
   - `rm -rf ~/Library/Caches/*`
   - `rm -rf ~/Library/Logs/*`
   - `rm -rf ~/.npm/_cacache/*`
3. Verify:
   - Re-run baseline scan and report reclaimed size.

## Aggressive Workflow (`aggressive`, explicit user request only)

Includes all `safe` steps, plus optional confirmed actions:

- Maven cache purge: `rm -rf ~/.m2/repository`
- Gradle cache purge: `rm -rf ~/.gradle/caches ~/.gradle/wrapper`
- Homebrew cleanup: `brew cleanup -s`
- Empty Trash: `rm -rf ~/.Trash/*`
- Docker cleanup: `docker system prune -a`

For each optional action, explain impact first and ask for clear confirmation.

## Output Format

- `Before`: key path sizes
- `Actions`: what was deleted and what was skipped
- `After`: key path sizes
- `Recovered`: estimated reclaimed size
- `Next`: optional high-impact actions for approval

## Notes

- On macOS, privacy-protected folders may require Full Disk Access.
- Cache cleanup is usually safe, but first app launch/build after cleanup may be slower.
- Prefer predictable cache directories over ad hoc file deletion.

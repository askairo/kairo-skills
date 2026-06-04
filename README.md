# Kairo Skills

English | [中文](README_ZH.md)

Personal skills repository for Agent, Codex, and Kimi workflows.

Remote repository:

```text
https://github.com/askairo/kairo-skills
```

## Maintenance Model

This repository is the long-term source repository for skills. Agent user directories are runtime installation targets only.

Recommended flow:

```text
local source repository -> GitHub -> current Agent skills runtime directory
```

In other words, update a skill in this repository first, validate it, commit and push it, then use `skills-loop` to pull it back from GitHub and overwrite the installed runtime copy.

## Skills

| Skill | Group | Description |
| --- | --- | --- |
| `hexo-push` | Blog publishing | Convert Clippings articles into Hexo posts and publish them |
| `dialogue-refine` | Blog publishing | Refine AI conversations into structured Hexo posts |
| `skills-loop` | Skills management | GitHub-based skill iteration loop: publish, sync, reinstall, verify |
| `upgrade-kimi-cli` | Tool maintenance | Detect and upgrade Kimi CLI automatically |
| `merge-to` | Development flow | Merge the current branch into `dev` / `sit` and push |
| `weekly-report` | Business documents | Generate weekly reports from screenshots or task lists |
| `entity-design` | Domain design | Design domain entities from prototypes and business workflows |
| `mac-clean` | System maintenance | Safe macOS cleanup and low-risk file organization |

## Install or Update

Recommended with `skills-loop`:

```powershell
python skills-loop\scripts\sync.py install --repo askairo/kairo-skills --path hexo-push --agent-dir C:\Users\admin\.codex\skills
```

Update a skill with recorded source metadata:

```powershell
python skills-loop\scripts\sync.py update --skill hexo-push --agent-dir C:\Users\admin\.codex\skills
```

Publish local changes and update the current Agent:

```powershell
python skills-loop\scripts\sync.py publish-and-update --skill hexo-push --message "feat: improve hexo push"
```

## Repository Layout

The repository currently keeps one skill per root-level directory, which makes GitHub path-based installation straightforward:

```text
kairo-skills/
├── README.md
├── README_ZH.md
├── dialogue-refine/
├── entity-design/
├── hexo-push/
├── mac-clean/
├── merge-to/
├── skills-loop/
├── upgrade-kimi-cli/
└── weekly-report/
```

Physical grouping such as `blog/` or `work/` is intentionally deferred. Grouping is maintained in the README table for now. Once the number of skills grows significantly, the directory structure and `skills-loop` defaults can be upgraded together.

## Conventions

- Prefer natural language, explicit parameters, config files, and auto-discovery.
- Use environment variables only as fallback compatibility, not as the recommended configuration path.
- Runtime skills installed from GitHub should include `.skill-source.json` source metadata.

## Changelog

- 2026-05-23: Merged `entity-design`, `merge-to`, and `weekly-report` from the Codex runtime
- 2026-05-31: Upgraded `mac-clean` with safe/aggressive cleanup and `organize-safe`
- 2026-05-29: Renamed and upgraded `sync-skills` to `skills-loop`
- 2026-05-23: Refactored `sync-skills` into a GitHub-driven skills management workflow
- 2026-05-23: Improved `hexo-push` previews, category/tag confirmation, and deploy retries
- 2026-04-07: Initialized the repository with `hexo-push` and `upgrade-kimi-cli`

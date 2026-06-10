---
name: kickoff-flow
description: Standardize personal new-project kickoff from idea to executable local workspace. Use when Codex should create/rename a GitHub repository, clone locally, establish naming conventions, resolve a configured project-docs root directory, and generate the skill-defined kickoff document set.
---

# Kickoff Flow

## Overview

Use this skill to bootstrap a new personal project in a repeatable way, separating:

- code workspace (repo)
- project-management docs under a configured root directory

This workflow is for project initialization, not feature implementation.

## Local Config

Use local machine config for stable, user-specific documentation destinations. Keep these files outside project repos and treat them as private state.

- Path config: `<CODEX_HOME>/local-config/kickoff-flow/paths.yaml`
- Fallback path config: `<HOME>/.codex/local-config/kickoff-flow/paths.yaml`

Recommended path config shape:

```yaml
version: 1

docs:
  root: <absolute-project-docs-root>
```

- `docs.root` is the user-specific root that contains all kickoff project document folders, such as an Obsidian `03-req` directory.
- The skill owns the internal structure under `docs.root`: create `<docs.root>/<project_name>/00-overview.md` and `<docs.root>/<project_name>/10-roadmap.md`.
- Prefer configured paths over deriving a docs root from memory.
- If no config exists and the user did not provide a docs root, ask the user for the docs root. After the user provides it, create or update the local path config before generating docs.

## Workflow

1. Capture kickoff input.
   - Required: project name, one-line objective.
   - Optional: GitHub visibility (`public`/`private`), local base directory, tech stack, docs root.

2. Normalize naming.
   - Prefer short lowercase kebab-case names (example: `envflow`).
   - Keep GitHub repo name, local folder name, and `03-req` folder name consistent.

3. Create or rename GitHub repository.
   - If repository does not exist, create it.
   - If user changed the project name, rename repository and sync local `origin`.

4. Prepare local workspace.
   - Clone repo under user-selected base directory.
   - Verify git remote and default branch.

5. Create project-management docs under the resolved docs directory.
   - Resolve the docs root with this priority:
     - Explicit user-provided docs root for the current request.
     - Local path config from `<CODEX_HOME>/local-config/kickoff-flow/paths.yaml`.
     - Local path config from `<HOME>/.codex/local-config/kickoff-flow/paths.yaml`.
   - If the docs root cannot be resolved, pause and ask the user for it; then write it to the local path config.
   - Create directory: `<docs-root>/<project-name>`
   - Create:
     - `00-overview.md` (project definition)
     - `10-roadmap.md` (execution plan and verification tracking)

6. Keep code repo clean.
   - In project repo root, keep only code/config/runtime docs (for example `README.md`).
   - Do not store project-management planning docs in code root when `03-req` is available.

7. Confirm kickoff completeness.
   - GitHub repo exists with correct name.
   - Local directory exists with correct name.
   - `<docs-root>/<project-name>/00-overview.md` exists.
   - `<docs-root>/<project-name>/10-roadmap.md` exists.

## Templates

- Use `references/00-overview.template.md`
- Use `references/10-roadmap.template.md`

## Notes

- This skill is intentionally generic; requirement details vary by project.
- For implementation phases after kickoff, hand off to task-specific skills.

## Script Helper

Use `scripts/init_project_docs.ps1` to generate kickoff docs automatically:

```powershell
pwsh -File scripts/init_project_docs.ps1 \
  -ProjectName envflow \
  -Objective "Build a lightweight desktop environment switch tool" \
  -RepoUrl "https://github.com/askairo/envflow" \
  -LocalRepoPath "<absolute-local-repo-path>" \
  -DocsRoot "<absolute-docs-root>" \
  -SaveConfig
```

It creates/updates:
- `<docs-root>/<project-name>/00-overview.md`
- `<docs-root>/<project-name>/10-roadmap.md`

If neither local config nor explicit docs root is available, the script fails with a clear message instead of using a hard-coded docs path.

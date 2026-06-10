---
name: kickoff-flow
description: Standardize personal new-project kickoff from idea to executable local workspace. Use when Codex should create/rename a GitHub repository, clone locally, establish naming conventions, resolve a configured external docs directory, and generate project-management docs with reusable overview/roadmap templates.
---

# Kickoff Flow

## Overview

Use this skill to bootstrap a new personal project in a repeatable way, separating:

- code workspace (repo)
- project-management docs (resolved from local config or explicit user input)

This workflow is for project initialization, not feature implementation.

## Local Config

Use local machine config for stable, user-specific documentation destinations. Keep these files outside project repos and treat them as private state.

- Path config: `<CODEX_HOME>/local-config/kickoff-flow/paths.yaml`
- Fallback path config: `<HOME>/.codex/local-config/kickoff-flow/paths.yaml`

Recommended path config shape:

```yaml
version: 1

obsidian:
  base_root: <absolute-notes-root>
  doc_dir_template: "{base_root}\\03-req\\{project_name}"
```

- `base_root` is the user-specific Obsidian or notes root.
- `doc_dir_template` controls the final project-doc directory.
- `doc_dir_template` may reference `{base_root}`, `{project_name}`, and `{repo_name}`.
- Prefer configured paths over deriving a docs directory from memory.
- If no config exists and the user did not provide a docs directory, ask the user for the docs root or template. After the user provides it, create or update the local path config before generating docs.

## Workflow

1. Capture kickoff input.
   - Required: project name, one-line objective.
   - Optional: GitHub visibility (`public`/`private`), local base directory, tech stack, docs root/template.

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
   - Resolve the doc directory with this priority:
     - Explicit user-provided docs directory or template for the current request.
     - Local path config from `<CODEX_HOME>/local-config/kickoff-flow/paths.yaml`.
     - Local path config from `<HOME>/.codex/local-config/kickoff-flow/paths.yaml`.
   - If the directory cannot be resolved, pause and ask the user for the docs root or template; then write it to the local path config.
   - Create directory: `<resolved-doc-dir>`
   - Create:
     - `00-overview.md` (project definition)
     - `10-roadmap.md` (execution plan and verification tracking)

6. Keep code repo clean.
   - In project repo root, keep only code/config/runtime docs (for example `README.md`).
   - Do not store project-management planning docs in code root when `03-req` is available.

7. Confirm kickoff completeness.
   - GitHub repo exists with correct name.
   - Local directory exists with correct name.
   - `<resolved-doc-dir>/00-overview.md` exists.
   - `<resolved-doc-dir>/10-roadmap.md` exists.

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
- `<resolved-doc-dir>/00-overview.md`
- `<resolved-doc-dir>/10-roadmap.md`

If neither local config nor explicit docs parameters are available, the script fails with a clear message instead of using a hard-coded docs path.

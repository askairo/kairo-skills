---
name: kickoff-flow
description: Standardize personal new-project kickoff from idea to executable local workspace. Use when Codex should create/rename a GitHub repository, clone locally, establish naming conventions, and generate project-management docs under 03-req with reusable overview/roadmap templates.
---

# Kickoff Flow

## Overview

Use this skill to bootstrap a new personal project in a repeatable way, separating:

- code workspace (repo)
- project-management docs (`03-req/<project-name>/`)

This workflow is for project initialization, not feature implementation.

## Workflow

1. Capture kickoff input.
   - Required: project name, one-line objective.
   - Optional: GitHub visibility (`public`/`private`), local base directory, tech stack.

2. Normalize naming.
   - Prefer short lowercase kebab-case names (example: `envflow`).
   - Keep GitHub repo name, local folder name, and `03-req` folder name consistent.

3. Create or rename GitHub repository.
   - If repository does not exist, create it.
   - If user changed the project name, rename repository and sync local `origin`.

4. Prepare local workspace.
   - Clone repo under user-selected base directory.
   - Verify git remote and default branch.

5. Create project-management docs under `03-req`.
   - Create directory: `03-req/<project-name>/`
   - Create:
     - `00-overview.md` (project definition)
     - `10-roadmap.md` (execution plan and verification tracking)

6. Keep code repo clean.
   - In project repo root, keep only code/config/runtime docs (for example `README.md`).
   - Do not store project-management planning docs in code root when `03-req` is available.

7. Confirm kickoff completeness.
   - GitHub repo exists with correct name.
   - Local directory exists with correct name.
   - `03-req/<project-name>/00-overview.md` exists.
   - `03-req/<project-name>/10-roadmap.md` exists.

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
  -LocalRepoPath "D:\private-vs-space\envflow"
```

It creates/updates:
- `03-req/<project>/00-overview.md`
- `03-req/<project>/10-roadmap.md`

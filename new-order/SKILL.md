---
name: new-order
description: Turn an unclear new project into an ordered project-level document set, architecture boundaries, and execution plans before task-driven development. Use when starting a new project or when existing docs are fragmented and need to be consolidated before task-dev-flow.
---

# New Order

## Overview

Use this skill to bring order to a new project before task execution begins. It focuses on project goals, scope, architecture boundaries, documentation structure, and the point at which the project is ready to hand off to `task-dev-flow`.

This skill does not create `feat-***` / `fix-***` task docs. It prepares the project so task-driven development can work cleanly.

## When to Use

- A brand-new project needs its first stable documentation set.
- Existing project docs are fragmented, duplicated, or out of date.
- The project needs architecture docs before implementation can proceed.
- The project needs a clear decision on whether it is ready for `task-dev-flow`.

## Local Config

Use local machine config for stable, user-specific documentation roots. Keep these files outside project repos and treat them as private state.

### Agent Home Resolution

`<AGENT_HOME>` is the current agent's configuration home directory. Resolve it before reading or writing any local config, using the same priority model as other skill-managed local config:

1. Check the working directory path: if it contains `.qoderworkcn`, use `~/.qoderworkcn/`.
2. Check the working directory path: if it contains `.codex`, use `~/.codex/`.
3. If `~/.qoderworkcn/` exists, use it.
4. If `~/.codex/` exists, use it.
5. Fallback: `~/.config/skills/`.

After resolving, verify the chosen directory exists. If none exists, ask the user which agent home to use and create it.

### Config Paths

- Path config: `<AGENT_HOME>/local-config/new-order/paths.yaml`

Recommended path config shape:

```yaml
version: 1

docs:
  root: <absolute-project-docs-root>
```

- `docs.root` is the user-specific root that contains project document folders, such as an Obsidian `03-req` directory.
- If the config does not exist and the user did not provide a docs root, ask for the docs root first, then create or update the local path config.
- If the repository already uses the same docs root from `task-dev-flow`, reuse it instead of asking again.

## Project Document Layout

`new-order` owns the project-level document layout under:

```text
<docs.root>/<project-name>/
```

Recommended project-level documents:

- `00-overview.md`
- `10-roadmap.md`
- `11-architecture.md`
- `12-interfaces-and-schema.md`
- `13-frontend-architecture.md`
- `14-backend-architecture.md`
- `15-worker-architecture.md` when the project has a separate worker/API backend
- `20-references.md`
- `30-decisions.md`
- `31-open-questions.md`
- `32-risk-log.md`

Execution-planning documents live in the same project folder, under:

```text
<docs.root>/<project-name>/plans/
```

Recommended planning docs:

- `40-implementation-plan.md`
- `41-task-breakdown.md`
- `42-validation-plan.md`
- `43-release-notes.md`

Task-level work-item docs are reserved for `task-dev-flow` and should live under:

```text
<docs.root>/<project-name>/tasks/
```

## Workflow

1. Collect the project input.
   - Accept ideas, notes, screenshots, PRDs, existing docs, prototype references, or a partially started repo.
   - Identify the project name, target audience, repo name, and whether the project already has stable docs.

2. Inspect what already exists.
   - Read the existing project docs first.
   - Inspect repository rules when there is an implementation repo.
   - Look for duplicate, conflicting, or missing docs.

3. Normalize the project-level doc set.
   - Ensure `00-overview`, `10-roadmap`, `11-architecture`, `12-interfaces-and-schema`, and `20-references` exist.
   - Add `13-frontend-architecture` and `14-backend-architecture` for every new product/project unless the project is intentionally frontend-only or backend-only.
   - Add `15-worker-architecture` when the project includes a separate API/worker backend.
   - Add `30-decisions`, `31-open-questions`, and `32-risk-log` when the project has enough substance to need them.
   - Prefer updating existing docs over creating parallel duplicates.

4. Clarify the project structure.
   - Distinguish project-level constraints from task-level work items.
   - Keep project docs in the project folder and planning docs in `plans/`.
   - Leave `tasks/` to `task-dev-flow`.

5. Decide readiness for execution.
   - If scope, architecture, or priorities are still unstable, keep refining project docs.
   - If the project is ready to be decomposed into concrete work items, prepare a handoff to `task-dev-flow`.

6. Hand off with a clear summary.
   - Summarize the current scope, architecture, open questions, risks, and next step.
   - Point to the project docs that define the constraints.
   - Tell the user when the project is ready for `task-dev-flow`.

## Output Expectations

- Prefer Chinese for project documents when the repository or existing docs are already written in Chinese.
- Keep the output concise but structured.
- Separate confirmed facts, open questions, and next actions.
- Do not create task cards or `feat-***` / `fix-***` docs.

## Coordination With Other Skills

- Use `task-dev-flow` after the project is sufficiently ordered and the work can be split into concrete tasks.
- Use `entity-design` when the project is primarily about main/detail entities, table design, or field derivation.
- Use browser or computer control only when external docs or prototypes need to be inspected.


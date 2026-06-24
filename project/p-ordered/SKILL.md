---
name: p-ordered
description: Organize an existing project into ordered docs and boundaries. Use when a project already exists but its docs are fragmented, or when you need to normalize the docs root and project structure before `p-task`.
---

# P Ordered

Use this before task development to turn a project from scattered into actionable.

## When To Use

- A project is just starting and does not yet have a stable documentation structure.
- An older project has scattered, duplicate, or outdated docs.
- You need to clarify the project main line before task breakdown and implementation.

## Docs Root

This skill uses private local configuration to store stable document roots. Do not write this configuration into the project repository.

### Agent Home Resolution

`<AGENT_HOME>` means the current Agent's config root. Resolve it before reading or writing local config, and only use the directory that belongs to the current Agent.

Resolution order:

1. If the working directory path contains `.qoderworkcn`, use `~/.qoderworkcn/`
2. If the working directory path contains `.codex`, use `~/.codex/`
3. If `~/.qoderworkcn/` exists, use it
4. If `~/.codex/` exists, use it
5. Fall back to `~/.config/skills/`

After resolving, confirm that the directory really exists. If none exist, ask the user which Agent Home to use.

**Hard rule:** once `<AGENT_HOME>` has been resolved, only read and write config under that directory. Do not cross Agent directories.

### Config Files

- Preferred path config: `<AGENT_HOME>/local-config/p-ordered/paths.yaml`
- Compatibility path config: `<AGENT_HOME>/local-config/p-task/paths.yaml`

Recommended path config:

```yaml
version: 1

docs:
  root: <absolute-project-docs-collection-root>
```

- `docs.root` is the common root for project requirement docs, for example Obsidian's `03-req`.
- This skill owns the project-level structure under `<docs.root>/<repo-name>/`.
- Do not store a single project's path, such as `<docs.root>/dimoo`, in the global skill config unless the user explicitly says this Agent only works with that one project.
- If only the compatibility `p-task` config exists, reuse its `docs.root` because `p-task` and `p-ordered` share the same project-docs collection root.

### Project Docs Root Resolution

When using `p-ordered`, resolve the actual project docs root in this order:

1. If the user gives a docs path for this turn, use it. If it already contains project files such as `00-overview.md` or `10-roadmap.md`, treat it as the project docs root; otherwise treat it as the collection root and append `<repo-name>`.
2. Else read `docs.root` from `<AGENT_HOME>/local-config/p-ordered/paths.yaml`.
3. Else read `docs.root` from `<AGENT_HOME>/local-config/p-task/paths.yaml`.
4. If a configured `docs.root` already contains project files such as `00-overview.md` or `10-roadmap.md`, treat it as the project docs root for compatibility with older configs.
5. Otherwise treat configured `docs.root` as the collection root and use `<docs.root>/<repo-name>` as the project docs root.

If no docs root is configured and the user has not given a path, ask first, then write only the common collection root into `<AGENT_HOME>/local-config/p-ordered/paths.yaml`. Do not guess the docs root through a full-disk search.

## Doc Hierarchy

`p-ordered` defines only the hierarchy and responsibilities; it does not hardcode the subject area for any specific project.

### 00 Layer

- `00-overview.md`
- Answer only: what this project is, what problem it solves, and where the boundaries are.

### 10 Layer

- `10-roadmap.md`
- Answer only: how this project will move forward, how the phases are split, and what the sequence is.

### 20 Layer

- `20-*.md`
- This is the project-specific collection of focus docs.
- This layer holds the most important topics that need to be captured separately, such as architecture, storage, APIs, UX, rules, compatibility, performance, and security.
- The project decides the exact file names. They do not have to follow a fixed set, but they must serve the project's key focus areas.
- A project can keep just one 20-layer doc or split it into several.

### 30 Layer

- `30-decisions.md`
- Record only confirmed key decisions.

### 31 Layer

- `31-open-questions.md`
- Record only questions that are not yet confirmed and still need follow-up.

### 32 Layer

- `32-risk-log.md`
- Record only risks, dependencies, and blockers.

### `plans/`

- Store phase plans and rollout proposals here.
- The content here is usually "how this phase gets implemented", not a single task card.

### `tasks/`

- Store task docs managed by `p-task`.
- This folder is only for concrete tasks, not the project main line, phase plans, or long-term decisions.

## Base Constraints

`p-ordered` only cares about "how to layer" and "what should happen first"; it does not care what domain name a project uses.

Before task breakdown, establish this order:

1. `00-overview.md`
2. `10-roadmap.md`
3. `20-*.md`
4. `30-decisions.md`
5. `31-open-questions.md`
6. `32-risk-log.md`
7. `plans/`
8. `tasks/`

The key is not the file names themselves, but the responsibilities of each layer:

- 00 layer answers "what it is"
- 10 layer answers "how it moves forward"
- 20 layer answers "how key issues are decided"
- 30/31/32 layers answer "what is decided, what is not decided, and where the risks are"
- `plans/` answers "how the phase gets implemented"
- `tasks/` answers "how the concrete tasks get executed"

## Core Responsibilities

- Define the project goals, scope, boundaries, and roles first.
- Identify which focus areas must be captured separately, then place them in the 20 layer.
- Keep important decisions, open questions, and risks in separate docs.
- Finally, arrange the phase plans and task execution order.

## Relationship To `p-task`

- `p-ordered` is responsible for turning a project from scattered into actionable.
- `p-task` is responsible for turning a concrete task from "to do" into "verified".
- Use `p-ordered` first to establish the main line and focus areas, then enter `p-task` to claim specific task docs.
- If the key focus areas in the 20 layer are still unclear, stop at `p-ordered` and do not issue task cards too early.

## Notes

- This skill does not directly generate `feat-***` or `fix-***` task docs.
- Its job is to make the project "ready to develop, ready to move forward, and ready to hand off."

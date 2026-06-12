---
name: new-order
description: Organize a new project into orderly project docs, architecture boundaries, and execution plans. Use this when a project is just starting, existing docs are fragmented, or you need to normalize the project structure from the configured docs root before entering `task-dev-flow`.
---

# New Order

Use this before task development to turn a project from scattered into actionable.

## When To Use

- A project is just starting and does not yet have a stable documentation structure.
- An older project has scattered, duplicate, or outdated docs.
- You need to clarify the project main line before task breakdown and implementation.

## Docs Root

- Prefer the configured docs root.
- If the project or local config already provides `docs.root`, organize docs around that root.
- If nothing is configured and the user has not given a path, ask which docs root to use.
- Do not guess the docs root through a full-disk search.

## Doc Hierarchy

`new-order` defines only the hierarchy and responsibilities; it does not hardcode the subject area for any specific project.

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

- Store task docs managed by `task-dev-flow`.
- This folder is only for concrete tasks, not the project main line, phase plans, or long-term decisions.

## Base Constraints

`new-order` only cares about "how to layer" and "what should happen first"; it does not care what domain name a project uses.

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

## Relationship To `task-dev-flow`

- `new-order` is responsible for turning a project from scattered into actionable.
- `task-dev-flow` is responsible for turning a concrete task from "to do" into "verified".
- Use `new-order` first to establish the main line and focus areas, then enter `task-dev-flow` to claim specific task docs.
- If the key focus areas in the 20 layer are still unclear, stop at `new-order` and do not issue task cards too early.

## Notes

- This skill does not directly generate `feat-***` or `fix-***` task docs.
- Its job is to make the project "ready to develop, ready to move forward, and ready to hand off."

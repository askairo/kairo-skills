---
name: p-ordered
description: Maintain a project's architecture-planning loop through ordered external docs. Use when Codex needs to clarify project goals, boundaries, roadmap, focus docs, decisions, open questions, risks, plans, and task readiness before `p-task`, or when implementation/user feedback should update project state and guide the next planning cycle.
---

# P Ordered

Use this before task development to turn a project from scattered into actionable.

## Goal

Use external project docs as the shared architecture memory that helps Codex plan, split, execute, verify, learn from feedback, update state, and plan the next step.

`p-ordered` is not a task-execution skill. It is the project-line and architecture-loop skill:

```text
project line -> next plan -> task split -> execution by p-task -> verification feedback -> state writeback -> next plan
```

Its responsibility is to keep the project ready for development by maintaining:

- clear goals, scope, boundaries, and roles
- current roadmap and phase sequence
- focus docs for architecture, UX, data, storage, APIs, rules, compatibility, performance, and security
- confirmed decisions, open questions, risks, dependencies, and blockers
- phase plans and task readiness
- feedback writeback after meaningful implementation or user review

## When To Use

- A project is just starting and does not yet have a stable documentation structure.
- An older project has scattered, duplicate, or outdated docs.
- You need to clarify the project main line before task breakdown and implementation.
- You need to decide what should happen next before entering `p-task`.
- User or implementation feedback changes product direction, architecture constraints, UX rules, risk, or task priority.

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

## Feedback Writeback

Use project docs as external working memory for the architecture loop:

```text
read project line -> plan next work -> split tasks -> implement -> verify -> collect feedback -> write back state -> plan again
```

Do not record every temporary action. Record only feedback that changes future work, constraints, state, or risk.

### What To Write Back

Write back when an event:

- changes project priority, sequencing, scope, or acceptance criteria
- confirms or changes a product, architecture, UX, data, storage, security, or workflow constraint
- completes, blocks, reopens, or materially changes a task
- exposes a bug, risk, dependency, open question, or missing validation
- captures a user decision that future agents should not rediscover
- produces implementation feedback that should shape the next planning cycle

Usually do not write back:

- service starts, log cleanup, file inspection, or other temporary operations
- command attempts that do not affect project state
- exploratory notes that create no decision, risk, task, or follow-up

### Where To Write Back

Choose the document by information type:

- `00-overview.md`: project identity, scope, boundary, or role changes only.
- `10-roadmap.md`: phase status, current focus, priority order, and next-step sequencing.
- `20-*` focus docs: durable architecture, product, UX, data-flow, state-machine, cache, API, storage, security, compatibility, or performance constraints.
- `30-decisions.md`: confirmed key decisions. If this file does not exist yet, record the decision in the most relevant focus doc or task and consider creating it when decisions accumulate.
- `31-open-questions.md`: unresolved questions that can change design, scope, sequence, or acceptance.
- `32-risk-log.md`: risks, blockers, external dependencies, and validation gaps.
- `plans/`: phase plans and rollout proposals.
- `tasks/`: concrete task goals, scope, acceptance criteria, progress, validation, remaining work, and commit/push state.

If one feedback item spans layers, write the durable principle to the focus/decision doc and the concrete work to the task doc. Update `10-roadmap.md` only when priority or phase sequencing changes.

### When To Check Writeback

At these points, explicitly decide whether docs need updates:

1. Before planning: verify that the project line is current enough to split work.
2. When creating a task: record goal, scope, assumptions, acceptance, and validation plan.
3. During implementation: record meaningful discoveries, not every step.
4. After user feedback: classify whether it affects product, architecture, UX, task scope, priority, risk, or process.
5. After verification: update validation results, remaining issues, and task status.
6. Before handoff: ensure task docs, roadmap, focus docs, decisions, questions, and risks are not stale.

### Writeback Shape

Keep entries short and actionable. A useful writeback usually answers at least two of:

- what happened
- why it matters
- what it changes
- what happens next

Example:

```markdown
- Feedback: Cloud storage config stays expanded and crowds the reading workspace.
- Impact: Low-frequency settings interrupt the core "library -> item list -> reader" path.
- Constraint: Configuration surfaces should be collapsed, drawer-based, modal, or moved into settings by default.
- Next: Split a reader-focused layout task before continuing end-to-end reading validation.
```

### Task Status

Task docs should not be write-once. Keep these sections current when they exist:

- background
- goal
- scope
- acceptance criteria
- progress log
- validation results
- remaining work or open issues
- commit and push state

## Loop Discipline

After meaningful work, ask:

- Did this change the roadmap or current focus?
- Did it create a durable architecture, product, UX, data, or process constraint?
- Did it confirm a decision or open a question?
- Did it add or reduce risk?
- Is the task card stale?
- Does the next step need to be reordered?

If yes, write back to the appropriate project docs before moving to the next planning cycle.

## Relationship To `p-task`

- `p-ordered` is responsible for turning a project from scattered into actionable.
- `p-task` is responsible for turning a concrete task from "to do" into "verified".
- Use `p-ordered` first to establish the main line and focus areas, then enter `p-task` to claim specific task docs.
- If the key focus areas in the 20 layer are still unclear, stop at `p-ordered` and do not issue task cards too early.

## Notes

- This skill does not directly generate `feat-***` or `fix-***` task docs.
- Its job is to make the project "ready to develop, ready to move forward, and ready to hand off."

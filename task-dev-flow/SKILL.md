---
name: task-dev-flow
description: Turn an external task, ticket, issue, requirement link, prototype link, or pasted task description into a complete development workflow. Use when Codex needs to understand task metadata, inspect linked requirements, create or use a task branch, split work into implementation cards, follow repository rules, implement changes, validate them, and prepare a commit. Do not use this skill for pure entity/table design; use entity-design for that focused analysis.
---

# Task Dev Flow

## Overview

Use this skill to run a task-driven development loop from an external work item to a verified local implementation. Keep the workflow platform-neutral: ZenTao, Jira, GitHub issues, Axhub, internal docs, screenshots, or pasted task text are all valid inputs.

This skill stops after the finished development work is validated and committed on the task branch. Do not automatically merge branches unless the user explicitly asks in a separate request.

## Workflow

1. Capture the task input.
   - Accept task links, issue IDs, pasted titles, screenshots, prototype links, or natural-language descriptions.
   - Extract stable metadata when present: task title, task ID, source URL, product area, repository, and target branch name.
   - Prefer branch names like `task-<id>` when a numeric task ID is available.

2. Inspect the requirement source.
   - If the requirement is already open in Chrome and the user asks to use browser MCP, inspect it there.
   - If credentials are needed and the user provides them, use them only for the current task.
   - If the task points to prototypes or entity/table design, use `$entity-design` for that focused analysis and bring its results back into this workflow.
   - See `references/task-intake.md` for task-link parsing and requirement intake details.

3. Read repository rules before editing.
   - Inspect the target repository's local instructions first, especially `AGENTS.md`, `CLAUDE.md`, README files, and existing module patterns.
   - If the repo defines an instruction order, follow that order literally.
   - Let repository rules decide layering, naming, validation style, SQL location, and commit conventions.

4. Create or select the task branch.
   - Check the current branch and working tree before switching.
   - Avoid touching unrelated dirty changes.
   - Create the task branch only when needed; if it already exists, switch to it after confirming it is the intended branch.
   - If the inferred task branch does not exist, create it from the repository's baseline branch. Prefer the baseline named by repo instructions.
   - For Znder ERP repositories (`znder-erp`, `znder-erp-api`), default baseline order is: `master` -> `main` -> repository instruction baseline. If the user explicitly requests another baseline, follow the user request.
   - Before creating a new branch from a baseline, update that baseline from the remote when safe to do so. Do not overwrite, delete, or recreate an existing task branch.
   - After creating a task branch, verify the branch head equals the baseline head when no new commits were made yet. If not equal, stop and recreate from the correct baseline.
   - See `references/branch-prep.md` for the compatible branch preparation flow.

5. Split the work into task cards.
   - Produce a short checklist from the requirement before implementation.
   - If the workspace has a dedicated requirements directory (for example `03-req`), create `task-<id>.md` there before editing business code.
   - Keep cards outcome-oriented, such as API contract, persistence change, assembler mapping, operation log, validation, and tests.
   - Update the checklist as work completes.
   - When writing a `task.md` or equivalent task card, follow `references/task-template.md`.

6. Implement according to the repository shape.
   - Start from existing code paths and patterns.
   - Keep orchestration, conversion, persistence, side effects, and presentation responsibilities in their existing layers.
   - Prefer narrow edits that satisfy the task without redesigning unrelated code.
   - If a project-specific convention is missing but repeatedly needed, suggest adding it to the repo's instruction file instead of burying it in this skill.

7. Validate.
   - Run the narrowest meaningful checks first.
   - Broaden validation when shared contracts, controllers, workflow, or persistence behavior changed.
   - Report unrelated blockers clearly and do not hide whether verification passed.

8. Commit the validated work.
   - Stage only files related to the task.
   - Generate a task-aware commit message when task metadata is available.
   - If a `task.md` or task card contains a `commit` code block, use that exact message for `git commit`.
   - Commit only after implementation is complete and validation has passed, or after clearly reporting any validation that could not be run.
   - Example format:

```text
feat(scope): [Task title](Task URL) (task-1234)
```

9. Stop after committing the task branch.
   - Summarize what changed and what was verified.
   - Leave merge, release, or deployment decisions to the user unless explicitly requested later.
   - If the user later asks to merge the committed branch, use the appropriate merge workflow then.

## Interruption And Recovery Rules

- If the user corrects baseline selection (for example asks to use `master` instead of `dev`), stop implementation immediately, fix branch baseline first, and only then continue coding.
- After creating a new task branch, always verify baseline alignment hash before reading or editing business files.
- For privileged git actions (add/commit/push), if approval times out, retry once. If it times out again, pause and ask the user for a one-line go-ahead, then resume the same command.
- Do not continue feature implementation while branch-baseline disputes are unresolved.

## Coordination With Other Skills

- Use `$entity-design` when the task is primarily about deriving entities, tables, main/detail relationships, lifecycle states, fields, or snapshots from prototypes and requirements.
- Use browser automation when the requirement source must be inspected from an already-open browser tab or an authenticated web app.
- Do not fold merge behavior into this workflow by default. Branch integration can be handled manually or by a dedicated merge workflow after the task branch has been committed.

## Examples

```text
Use $task-dev-flow for this task link: https://example.com/task-view-1336.html
```

```text
Use $task-dev-flow to read this Jira issue, create the task branch, implement it in the current repo, and prepare the commit.
```

```text
Use $task-dev-flow with the Axhub prototype I opened in Chrome, but use $entity-design first if entity/table design is needed.
```

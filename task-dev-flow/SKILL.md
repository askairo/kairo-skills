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
   - Detect work-item type from the source when possible and map to a unified prefix:
     - Task links such as `task-view-1336` -> use `feat-1336`
     - Bug links such as `bug-view-6076` -> use `fix-6076`
   - Keep branch name, task-card filename, and commit suffix aligned with the same work-item prefix (`feat` or `fix`).

2. Inspect the requirement source.
   - If the requirement is already open in Chrome and the user asks to use browser MCP, inspect it there.
   - If credentials are needed and the user provides them, use them only for the current task.
   - If the task points to prototypes or entity/table design, use `$entity-design` for that focused analysis and bring its results back into this workflow.
   - See `references/task-intake.md` for task-link parsing and requirement intake details.

3. Read repository rules before editing.
   - Inspect the target repository's local instructions first, especially `AGENTS.md`, `CLAUDE.md`, README files, and existing module patterns.
   - If the repo defines an instruction order, follow that order literally.
   - Let repository rules decide layering, naming, validation style, SQL location, and commit conventions.

4. Create or select the work-item branch.
   - Check the current branch and working tree before switching.
   - Avoid touching unrelated dirty changes.
   - Create the work-item branch only when needed; if it already exists, switch to it after confirming it is the intended branch.
   - If the inferred work-item branch does not exist, create it from the repository's baseline branch. Prefer the baseline named by repo instructions.
   - For Znder ERP repositories (`znder-erp`, `znder-erp-api`), default baseline order is: `master` -> `main` -> repository instruction baseline. If the user explicitly requests another baseline, follow the user request.
   - Before creating a new branch from a baseline, update that baseline from the remote when safe to do so. Do not overwrite, delete, or recreate an existing work-item branch.
   - After creating a work-item branch, verify the branch head equals the baseline head when no new commits were made yet. If not equal, stop and recreate from the correct baseline.
   - See `references/branch-prep.md` for the compatible branch preparation flow.

5. Split the work into task cards.
   - Produce a short checklist from the requirement before implementation.
   - Keep cards outcome-oriented, such as API contract, persistence change, assembler mapping, operation log, validation, and tests.
   - Update the checklist as work completes.
   - When writing a `task.md` or equivalent task card, follow `references/task-template.md`.
   - Create or update a requirement task doc during this step, where filename is always `<prefix>-<id>.md` and `prefix` is `feat` or `fix`.
   - Resolve the doc directory with this priority:
     - For `znder-erp` and `znder-erp-api`, always write to `D:\znder\Obsidian\business\03-req/<repo-name>/`.
     - Otherwise, prefer `03-req/<repo-name>/` when it exists.
     - Else use `03-req/` when it exists.
     - Else create `03-req/<repo-name>/` and place the doc there.
   - Only skip this artifact when the user explicitly asks not to create docs.
   - Keep the task doc metadata (`source`, `branch`, `baseline`, `commit`) synchronized with the actual branch and commit text used later.

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
   - Once the `commit` message is generated in the task card, treat it as immutable for this task. Reuse the exact same text for all task commits.
   - Do not create ad-hoc commit messages later unless the user explicitly asks to change the commit wording.
   - Commit only after implementation is complete and validation has passed, or after clearly reporting any validation that could not be run.
   - Example format:

Task item:
```text
feat(scope): [Task title](Task URL) (feat-1234)
```
Bug item:
```text
fix(scope): [Bug title](Bug URL) (fix-6076)
```

9. Stop after committing the work-item branch.
   - Run a quick consistency check before finishing:
     - work-item branch exists and is correct (`feat-<id>` or `fix-<id>` when applicable)
     - commit message(s) use the exact task-card `commit` text
     - required task doc artifact exists at the resolved path (for example `D:\znder\Obsidian\business\03-req/znder-erp/fix-<id>.md` for znder repos, or `03-req/<repo-name>/fix-<id>.md` for general repos)
   - Summarize what changed and what was verified.
   - Leave merge, release, or deployment decisions to the user unless explicitly requested later.
   - If the user later asks to merge the committed branch, use the appropriate merge workflow then.

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

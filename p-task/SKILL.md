---
name: p-task
description: Turn concrete tasks into a complete development workflow. Use when Codex needs to execute a task, ticket, requirement link, or prototype after `p-ordered`, then verify and hand it off. For pure entity table design, use `entity-design` instead.
---

# P Task

## Goal

Turn a concrete task into a local development flow that is executable, verifiable, and deliverable. This covers Zentao, Jira, GitHub issues, prototype links, internal docs, screenshots, or directly pasted task descriptions.

If the project is still in an exploratory phase, the architecture is unstable, or project-level docs are not yet organized, use `p-ordered` first to establish the project documentation and architecture order, then come back here for task breakdown and implementation.

## Local Configuration

This skill uses private local configuration to store stable paths and authentication information. Do not write this configuration into the project repository.

### Agent Home Resolution

`<AGENT_HOME>` means the current Agent's config root. You must resolve it before reading or writing local config, and you may only use the directory that belongs to the current Agent.

Resolution order:

1. If the working directory path contains `.qoderworkcn`, use `~/.qoderworkcn/`
2. If the working directory path contains `.codex`, use `~/.codex/`
3. If `~/.qoderworkcn/` exists, use it
4. If `~/.codex/` exists, use it
5. Fall back to `~/.config/skills/`

After resolving, confirm that the directory really exists. If none exist, ask the user which Agent Home to use.

**Hard rule:** once `<AGENT_HOME>` has been resolved, only read and write config under that directory. Do not cross Agent directories.

### Config Files

- Auth config: `<AGENT_HOME>/local-config/p-task/auth-sites.yaml`
- Path config: `<AGENT_HOME>/local-config/p-task/paths.yaml`

Recommended path config:

```yaml
version: 1

docs:
  root: <absolute-task-docs-root>
```

- `docs.root` is the root directory for task docs, for example Obsidian's `03-req`.
- This skill owns the structure under `docs.root`:
  - Project-level docs: `<docs.root>/<repo-name>/`
  - Execution plans: `<docs.root>/<repo-name>/plans/`
  - Task docs: `<docs.root>/<repo-name>/tasks/`
- If the project already has an older flat structure, keep it compatible; new projects should prefer `tasks/`.
- If nothing is configured and the user has not given a docs root, ask first, then write the local config.

## Workflow

1. Gather task information.
   - Support task links, issue numbers, screenshots, prototypes, and natural language descriptions.
   - Extract stable facts: title, ID, source link, product area, repository, target branch.
   - If task numbers conflict, follow the user's explicit instruction.
   - Normalize prefixes based on the source:
     - `task-view-1336` -> `feat-1336`
     - `bug-view-6076` -> `fix-6076`
     - performance or optimization items -> `perf-<id>`

2. Check the requirement source.
   - If the requirement is already open in Chrome and the user asked to use the browser, read that page directly.
   - If authentication is needed, check the local auth config first.
   - If a stable output path is needed, check the path config first.
   - If the prototype or entity design needs separate analysis, call `entity-design` first.

3. Read repository rules.
   - Start with the repo's `AGENTS.md`, `CLAUDE.md`, and root README.
   - If there are architecture, SQL, module, or process docs, read only the parts directly related to the current task.
   - If the project has project-level docs, read `00-overview`, `10-roadmap`, `20-*.md`, `30-decisions`, `31-open-questions`, and `32-risk-log` first, then the relevant `plans/` and `tasks/`.

4. Create or select a task branch.
   - Check the current branch and workspace state first.
   - Avoid polluting unrelated changes.
   - If the branch does not exist, create it from the repository baseline branch.
   - Default baseline order for the Znder ERP repo: `master` -> `main` -> repo-specific baseline from the rules.

5. Split the task card.
   - Break the requirement into a short checklist first.
   - Task cards should be outcome-oriented, for example API, persistence, mapping, logging, validation, and tests.
   - Follow `references/task-template.md` when writing task docs.
   - Task doc names are fixed as `<prefix>-<id>.md`, usually with `feat`, `fix`, or `perf` prefixes.
   - Prefer writing docs into `<docs.root>/<repo-name>/tasks/`; put project-level planning in `plans/`.
   - If the project uses `p-ordered` hierarchy constraints, keep the 20-layer focus docs in sync, along with `30-decisions`, `31-open-questions`, and `32-risk-log`.
   - Keep `source`, `branch`, `baseline`, and `commit` in the docs aligned with the real state.

6. Implement according to the repository structure.
   - Start from the existing code paths and patterns.
   - Keep layering, naming, SQL, validation, and commit conventions aligned with the repository.
   - If a recurring project convention is missing, propose adding it to the repo rules file instead of baking it into the skill itself.

7. Verify.
   - Run the narrowest useful checks first, then broaden as needed.
   - Increase verification when shared contracts, controllers, workflows, or persistence are affected.
   - Clearly report blockers that are unrelated to the current task.

8. Deliver.
   - Commit or push only when the user explicitly asks for it.
   - If a commit is needed, treat the commit message in the task doc as fixed once it is generated.
   - Do not change the commit message on your own.

9. Wrap up.
   - Recheck that the branch, task doc, and required files are all present.
   - Summarize the changes, verification results, and remaining risks.

## Working With Other Skills

- If the requirement is mainly about entities, table structure, parent-child relationships, or field derivation, use `entity-design` first.
- If the project is in the early stage, the docs are missing, or the structure is messy, use `p-ordered` first.
- Whether to merge the branch after task completion is not part of this skill's default responsibility.

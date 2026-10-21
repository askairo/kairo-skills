# Task Template

Use this structure when the user asks for a `task.md`, task card, or implementation checklist derived from an external task.

## Template

````markdown
# <workitem-prefix>-<task_id> <workitem-title>

- source: [<workitem-title>](<workitem-url>)
- task_id: <original-source-task-id>
- requirement_id: <title-leading-requirement-id-or-none>
- branch: `<actual-branch-name>`
- baseline: `<master|main|dev|repo-specific>`
- commit:

```text
<type>(<scope>): [<workitem-title>](<workitem-url>) (<actual-branch-name>)
```

## Background

<Short summary of the business goal and affected module.>

## Confirmed Understanding

- <Stable fact confirmed from the source or user discussion>
- <Stable fact confirmed from the source or user discussion>

## Open Questions

- [ ] <Question that must be answered before implementation, or `None`>

## User Decisions

- <Decision confirmed by the user, including any accepted assumption>

## Scope

- <Concrete behavior or API/UI/data change>
- <Concrete behavior or API/UI/data change>

## Task Cards

- [ ] <Outcome-oriented implementation card>
- [ ] <Outcome-oriented implementation card>
- [ ] <Validation card>

## Verification

- [ ] <Narrow compile/test/check command>
- [ ] <Manual or browser verification when needed>

## Commit

- [ ] Stage only files related to this task.
- [ ] Commit after verification with the exact message from the `commit` block above.
- [ ] Leave merge decisions to the user after the task branch is committed.

## Notes

- <Open question, blocker, or important implementation constraint>
````

## Commit Field

Always put the commit message in a fenced code block under `commit:` so the user can copy it directly.

This block is the only commit message for the task branch. Every commit on that branch must use this exact text. Do not invent a new summary for follow-up commits.

Good:

````markdown
- commit:

```text
feat(srm): [【采购计划】详情页改版 后端](https://chandao.bidaapp.club/zentao/task-view-1336.html) (feat-1336)
```
````

Avoid:

```markdown
- commit: `feat(srm): [【采购计划】详情页改版 后端](https://chandao.bidaapp.club/zentao/task-view-1336.html) (feat-1336)`
```

The inline form is harder to copy cleanly from rendered Markdown.

## Workspace Requirement Doc Artifact

Always create a requirement task doc artifact using the configured docs root and the skill-defined internal structure:

```text
<docs.root>/<repo-name>/tasks/<feat|fix|perf>-<id>.md
```

If `docs.root` is not configured and the user has not provided it, ask for the docs root before creating the artifact and then save it to the local path config.

Here `<id>` remains the original task ID, not the requirement-based branch suffix. Keep separate task docs when several tasks share a requirement branch; do not rename existing docs just to match a new branch suffix. Record the actual branch name in metadata and the commit suffix, while preserving the original source task link. Keep the branch-level commit text unchanged if that branch already has one.

## Clarification Records

Before implementation, update the task doc with:

- `Confirmed Understanding`: facts from the requirement source, repository context, or user discussion.
- `Open Questions`: key ambiguities that could change implementation or verification. If none remain, write `None`.
- `User Decisions`: the user's answers and accepted assumptions.

Do not use this section for project-specific coding standards. Put recurring project rules in the repository's rule files or project documentation.

# Task Template

Use this structure when the user asks for a `task.md`, task card, or implementation checklist derived from an external task.

## Template

````markdown
# <workitem-prefix>-<id> <workitem-title>

- source: [<workitem-title>](<workitem-url>)
- branch: `<feat|fix>-<id>`
- baseline: `<master|main|dev|repo-specific>`
- commit:

```text
<type>(<scope>): [<workitem-title>](<workitem-url>) (<feat|fix>-<id>)
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

Keep the metadata and the `commit` code block consistent with the main task card.

## Clarification Records

Before implementation, update the task doc with:

- `Confirmed Understanding`: facts from the requirement source, repository context, or user discussion.
- `Open Questions`: key ambiguities that could change implementation or verification. If none remain, write `None`.
- `User Decisions`: the user's answers and accepted assumptions.

Do not use this section for project-specific coding standards. Put recurring project rules in the repository's rule files or project documentation.

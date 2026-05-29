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

Always create a requirement task doc artifact and resolve the directory dynamically:

```text
1. 03-req/<repo-name>/<feat|fix>-<id>.md      (if this repo-specific directory exists)
2. 03-req/<feat|fix>-<id>.md                  (if flat 03-req exists)
3. create 03-req/<repo-name>/ then write <feat|fix>-<id>.md there
```

Keep the metadata and the `commit` code block consistent with the main task card.

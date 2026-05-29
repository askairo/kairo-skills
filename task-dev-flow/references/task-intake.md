# Task Intake

## Supported Inputs

- Task or issue links from ZenTao, Jira, GitHub Issues, GitLab Issues, internal tools, Axhub, Figma-like prototypes, docs, or spreadsheets.
- Pasted task titles, ticket IDs, screenshots, or plain-language requirements.
- Mixed inputs, such as a title plus URL plus repository name.

## Metadata Extraction

Extract these fields when available:

- `title`: human task title.
- `task_id`: stable issue or task number.
- `source_url`: original requirement URL.
- `platform`: source system if obvious, such as ZenTao, Jira, GitHub, Axhub, or internal docs.
- `repo`: target repository when stated by the user or implied by cwd.
- `branch`: prefer `<prefix>-<task_id>` when a numeric ID exists, where `<prefix>` is `feat` for task/story and `fix` for bug.

For ZenTao-style URLs such as:

```text
https://chandao.example.com/zentao/task-view-1336.html
```

infer:

```text
task_id: 1336
branch: feat-1336
```

If the link text is Markdown:

```text
[【采购计划】详情页改版 后端](https://chandao.example.com/zentao/task-view-1336.html)
```

infer the title from the link label and keep the original Markdown link for commit messages.

## Requirement Inspection

- If the source is authenticated and already open in Chrome, prefer browser MCP over unauthenticated web requests.
- If the task includes prototype or entity design work, use `$entity-design` for that analysis instead of duplicating its rules here.
- If the task page has too much content, collect only the fields needed for implementation: goal, acceptance criteria, affected pages/APIs, data model impact, and edge cases.

## Commit Message Shaping

When task metadata is available, generate a concise message:

```text
feat(scope): [Task title](Task URL) (feat-1234)
```

When placing the message in a `task.md` file, put it in a fenced code block under `commit:`. See `task-template.md`.

After the task is implemented and verified, use this message exactly for `git commit`. Do not treat it as merely a suggestion when the user has asked the skill to complete the development workflow.

If multiple commits are required for the same task, reuse the exact same commit text unless the user explicitly asks for different wording.

Adjust `type` and `scope` to the repository convention. If the repository has no scope convention, infer one from the touched module or ask only when inference would be misleading.

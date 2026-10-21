# Task Intake

## Supported Inputs

- Task or issue links from ZenTao, Jira, GitHub Issues, GitLab Issues, internal tools, Axhub, Figma-like prototypes, docs, or spreadsheets.
- Pasted task titles, ticket IDs, screenshots, or plain-language requirements.
- Mixed inputs, such as a title plus URL plus repository name.

## Metadata Extraction

Extract these fields when available:

- `title`: human task title.
- `task_id`: stable issue or task number.
- `requirement_id`: requirement number extracted from the start of the task title, when available.
- `branch_id`: `requirement_id` when extractable, otherwise `task_id` from the source URL.
- `source_url`: original task or requirement URL; keep it unchanged.
- `platform`: source system if obvious, such as ZenTao, Jira, GitHub, Axhub, or internal docs.
- `repo`: target repository when stated by the user or implied by cwd.
- `branch`: `<prefix>-<branch_id>`, where `<prefix>` is `feat` for task/story, `fix` for bug, and `perf` for performance/optimization. An explicit user-supplied branch name overrides this derivation.
- `task_doc_path`: resolved doc location, using the skill-defined shape `<docs.root>/<repo-name>/tasks/<prefix>-<task_id>.md` when the new layout is used.

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

### Branch Suffix Selection

Read the task title before deriving the branch name. Prefer a clearly identifiable requirement number at its start, for example `2468 采购计划调整`, `【2468】采购计划调整`, `[需求2468] 采购计划调整`, or `需求#2468：采购计划调整`. Each yields `requirement_id: 2468`. Do not treat dates, versions, quantities, or unrelated numbers elsewhere in the title as requirement IDs. If the leading number's meaning or multiple requirement numbers are ambiguous, ask rather than guess.

For title `1138【采购催交】新功能模块采购催交 设计` and URL `task-view-1680.html`, resolve:

```text
task_id: 1680
requirement_id: 1138
branch_id: 1138
branch: feat-1138
task_doc_path: <docs.root>/<repo-name>/tasks/feat-1680.md
```

Read `1138` from the title itself, not the task system's separate `1680` badge. No whitespace is required between the leading requirement number and the following title text.

When no requirement number can be extracted from the title, fall back to the URL's task number: title `采购计划调整 后端` plus `task-view-1336.html` yields `feat-1336`. Apply the same suffix selection to `fix` and `perf`; do not change their prefix rules. If neither source provides a usable ID, ask before naming a new branch.

A requirement ID differing from the URL's task ID is expected. Only resolve genuine disagreements about the same source task ID (for example an explicitly stated task ID `1359` versus URL task ID `1355`). Keep the original task ID and link for traceability; task doc filenames remain task-based, while the commit's branch suffix uses the actual branch name.

Several tasks may share one requirement branch. Preserve separate task docs and original source links, reuse an existing branch without resetting it, and do not overwrite an existing branch-level commit message merely because another task shares the requirement ID.

If the user explicitly says to follow their pasted analysis, screenshots, or description instead of the linked page, use the link only for metadata such as `source_url` and `task_id`. Do not spend time browsing the page unless the user later asks to inspect it.

## Requirement Inspection

- If the source is authenticated and already open in Chrome, prefer browser MCP over unauthenticated web requests.
- Before asking the user for credentials, resolve the local-only auth config path in this order:
  1. an explicit path the user provides for this task or their local setup
  2. `<AGENTS_HOME>/local-config/p-task/auth-sites.yaml`
- Treat that file as private machine state. Never write it into a project repo, the skills source repo, task docs, or commit messages.
- Match credentials by domain first, then narrow by optional path prefixes when present.
- If the config contains matching credentials and the task requires requirement-page access, use those credentials for the current run without re-asking for them.
- If no matching entry exists, or the saved credentials fail, ask the user for the missing or updated credentials only when requirement-page access is still necessary.
- If the user provides credentials during the conversation, ask whether to save them into the local auth config for future runs. Only create or update the local config after explicit confirmation.
- When saving a new entry, prefer a human-readable site record with `name`, `match`, `auth`, `login`, and `policy` fields. Keep the structure easy to inspect and update by hand.
- If the task includes prototype or entity design work, use `$entity-design` for that analysis instead of duplicating its rules here.
- If the task page has too much content, collect only the fields needed for implementation: goal, acceptance criteria, affected pages/APIs, data model impact, and edge cases.

## Clarification Pass

After inspecting the source and repository context, pause before implementation when any unanswered point could change the result. Common categories include API shape, existing endpoint reuse, source-of-truth data, persistence impact, list/export coupling, sorting/filtering expectations, branch baseline, and verification depth.

Present the user with a concise list of questions and any reasonable default assumptions. After the user answers, update the task doc's `Confirmed Understanding`, `Open Questions`, and `User Decisions` sections before creating the final implementation checklist.

If the user explicitly asks to proceed without answering, record the assumptions as user-accepted decisions and continue.

### Local Auth Config Shape

Preferred path order:

```text
1. explicit user-provided path
2. <AGENTS_HOME>/local-config/p-task/auth-sites.yaml
```

Recommended shape:

```yaml
version: 1

sites:
  - name: zentao-bidaapp
    match:
      domains:
        - chandao.bidaapp.club
      path_prefixes:
        - /zentao/
    auth:
      type: form
      username: your_username
      password: your_password
    login:
      login_url: https://chandao.bidaapp.club/zentao/user-login.html
      username_field: account
      password_field: password
      submit_hint: login
    policy:
      local_only: true
      allow_auto_use: true
      require_confirm_before_update: true
```

## Commit Message Shaping

When task metadata is available, generate a concise message:

```text
feat(scope): [Task title](Task URL) (feat-1234)
```

When placing the message in a `task.md` file, put it in a fenced code block under `commit:`. See `task-template.md`.

After the task is implemented and verified, use this message exactly for `git commit`. Do not treat it as merely a suggestion when the user has asked the skill to complete the development workflow.

If multiple commits are required for the same task, reuse the exact same commit text unless the user explicitly asks for different wording.

Adjust `type` and `scope` to the repository convention. If the repository has no scope convention, infer one from the touched module or ask only when inference would be misleading.

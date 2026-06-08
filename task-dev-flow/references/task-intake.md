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
- `task_doc_path`: resolved doc location; for `znder-erp` and `znder-erp-api`, use `D:\znder\Obsidian\business\03-req/<repo-name>/<prefix>-<task_id>.md`.

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

If multiple sources disagree on the task ID, such as pasted text saying `1359` while the URL says `1355`, pause and resolve the canonical ID before creating the branch, task doc path, or commit suffix. Once resolved, keep all three aligned to that same final ID.

If the user explicitly says to follow their pasted analysis, screenshots, or description instead of the linked page, use the link only for metadata such as `source_url` and `task_id`. Do not spend time browsing the page unless the user later asks to inspect it.

## Requirement Inspection

- If the source is authenticated and already open in Chrome, prefer browser MCP over unauthenticated web requests.
- Before asking the user for credentials, resolve the local-only auth config path in this order:
  1. an explicit path the user provides for this task or their local setup
  2. `<CODEX_HOME>/local-config/task-dev-flow/auth-sites.yaml`
  3. `<HOME>/.codex/local-config/task-dev-flow/auth-sites.yaml`
- Treat that file as private machine state. Never write it into a project repo, the skills source repo, task docs, or commit messages.
- Match credentials by domain first, then narrow by optional path prefixes when present.
- If the config contains matching credentials and the task requires requirement-page access, use those credentials for the current run without re-asking for them.
- If no matching entry exists, or the saved credentials fail, ask the user for the missing or updated credentials only when requirement-page access is still necessary.
- If the user provides credentials during the conversation, ask whether to save them into the local auth config for future runs. Only create or update the local config after explicit confirmation.
- When saving a new entry, prefer a human-readable site record with `name`, `match`, `auth`, `login`, and `policy` fields. Keep the structure easy to inspect and update by hand.
- If the task includes prototype or entity design work, use `$entity-design` for that analysis instead of duplicating its rules here.
- If the task page has too much content, collect only the fields needed for implementation: goal, acceptance criteria, affected pages/APIs, data model impact, and edge cases.

### Local Auth Config Shape

Preferred path order:

```text
1. explicit user-provided path
2. <CODEX_HOME>/local-config/task-dev-flow/auth-sites.yaml
3. <HOME>/.codex/local-config/task-dev-flow/auth-sites.yaml
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

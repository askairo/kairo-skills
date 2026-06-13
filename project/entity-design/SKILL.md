---
name: entity-design
description: Design domain entities from product prototypes and business understanding. Use when Codex must inspect Axhub, Figma-like prototypes, screenshots, PRDs, requirement links, or existing business flows, then identify bounded entities, main/detail models, lifecycle states, field sets, snapshots, derived fields, missing fields, redundant fields, and database-ready entity/table designs.
---

# Entity Design

## Purpose

Use this skill to turn prototype screens and business rules into domain entity designs. The goal is not to copy UI fields one-to-one; the goal is to discover durable business concepts, relationships, lifecycle, and fields that can support the product behavior.

Prefer analysis first. Only modify external design documents or spreadsheets when the user explicitly asks to write/update them. If the user says "do not modify", "先分析", "指出即可", or similar, produce findings only.

## Operating Environment

This skill is intended for a browser-operated design workflow:

- Requirements are usually read from Axhub or other prototypes already opened in the user's Chrome browser.
- Entity/table designs are usually written into an Alidocs/DingTalk spreadsheet already opened in the user's Chrome browser.
- The field/template spreadsheet is a concrete source of truth, not just a convention. When the user provides a template link, open and inspect that template before designing rows.
- The user's Chrome browser has the Codex browser-control extension installed. Prefer controlling that Chrome session through the Browser plugin/Computer Use path, especially when Axhub or Alidocs requires the user's login state.
- Do not assume the in-app browser can access authenticated Axhub or Alidocs pages. Use the already-open Chrome tab when available.
- Treat Alidocs as an Excel-like spreadsheet: preserve formulas, sheet structure, required template rows, generated-SQL columns, and user-corrected content.

## Local Configuration

Use private local config when the current request depends on stable project paths or authenticated requirement sources.

- Resolve `<AGENT_HOME>` the same way as `p-task`.
- Read config only from the current agent home, never from the project repo.
- Preferred config files:
  - `<AGENT_HOME>/local-config/entity-design/paths.yaml`
  - `<AGENT_HOME>/local-config/entity-design/auth-sites.yaml`
- `paths.yaml` stores the local docs root used for saved design artifacts.
- `auth-sites.yaml` stores login records for requirement sources such as ZenTao and Axhub.
- If config exists, use it before asking the user for a docs root or credentials.
- If the user provides new credentials, ask before saving them to local config.
- Keep the config shape small and human-readable; see `references/local-config.md` for the expected layout.

## Inputs And Outputs

Read requirements from these sources, in this order:

1. The current conversation, especially user clarifications and corrections.
2. The Axhub/prototype/requirement page currently opened in Chrome, including page tree, visible screens, interaction notes, and exported `data.js` when available.
3. Other explicit requirement sources provided by the user, such as Figma-like prototypes, screenshots, PRDs, ZenTao stories, DingTalk docs, or pasted text.
4. Existing project context, such as `AGENTS.md`, `CLAUDE.md`, existing entity/table examples, module code, workflow conventions, attachment conventions, and naming patterns.
5. Existing design outputs, especially the current Alidocs/DingTalk spreadsheet sheets, SQL-template sheets, database docs, or previously generated field lists.

Read table/form templates from these sources:

1. The explicit template link provided by the user.
2. The currently opened Chrome Alidocs/DingTalk template tab.
3. Existing sibling sheets in the same design document.
4. Local project SQL/entity examples only as a fallback.

For this Znder ERP workspace, the known table-field template link from the current workflow is:

`https://alidocs.dingtalk.com/i/nodes/R1zknDm0WRwvyw61IZMa4R4eVBQEx5rG`

Resolve conflicts by preferring the newest explicit user clarification over prototype labels, and preferring project conventions over generic database habits.

Output destinations:

- For entity/table design tasks, the primary output destination is the user's currently opened Alidocs/DingTalk spreadsheet when the user has asked to generate or modify form/table fields.
- Before writing to Alidocs, state the target document/sheets and the intended change scope, then read the current sheet content first.
- If the user asks for analysis, review, comparison, or says not to modify, output findings in chat only.
- If the user asks to generate a document, create/update the requested local file or document artifact.
- If the user asks for SQL-ready rows without asking to write them, produce rows in the template-compatible shape in chat.

## Workflow

1. Collect context.
   - Read prototype links, PRD links, screenshots, existing table/design links, module prefix, and user clarifications.
   - Read local project rules first when available (`AGENTS.md`, `CLAUDE.md`, existing module code, existing table/entity examples).
   - If the requirement source or output path needs machine-local state, read `<AGENT_HOME>/local-config/entity-design/auth-sites.yaml` and `<AGENT_HOME>/local-config/entity-design/paths.yaml` first.
   - Identify whether the task is to generate entities, review existing designs, or update an external document.

2. Inspect the prototype.
   - Use Browser for Axhub or other interactive prototypes when the user provides links or asks to operate the browser.
   - Open page tree/navigation and enumerate all relevant screens, not only the first page.
   - Capture fields from list columns, filters, tabs, create/edit/detail modals, import/export dialogs, approval/detail pages, state-machine pages, and page annotations.
   - Treat prototype labels as user-facing intent, not final entity or field names.
   - Extract hidden requirements from notes such as default status, button behavior, aggregation rules, delete rules, generated-code rules, and permissions.

3. Build the domain model.
   - Start from business entities and lifecycle, not from screens one-to-one.
   - Separate main/header entities and item/detail entities when the behavior is master-detail.
   - Identify source entities and generated entities, especially "select existing records to create a plan/order/task" flows.
   - Decide which fields are persisted, derived, workflow-provided, attachment-provided, or intentionally omitted.
   - Snapshot external business data needed for audit/display, especially names/codes/addresses visible in the workflow.
   - Avoid foreign keys to external entities if the user explicitly asks for snapshots only.

4. Design fields.
   - Use stable English field names with project/module conventions.
   - Preserve common/template fields when a project spreadsheet or SQL template requires them.
   - Store durable business facts; derive display-only aggregations in query logic unless persistence is required.
   - Keep status fields aligned with lifecycle, tabs, and workflow. Do not invent duplicate statuses for the same state.
   - Do not add attachment ID collections when the project has a common attachment model keyed by business id/model.

5. Review before writing.
   - Compare prototype fields against proposed/current entity fields.
   - Mark each prototype field as stored, derived, common field, workflow/system-provided, attachment-provided, or intentionally omitted.
   - Flag redundant fields: duplicated approval records, attachment ID collections, display-only joined names, calculated ratios, and duplicated statuses.
   - Flag missing fields: filters that require storage, import traceability, source-detail links, status fields needed for tabs, and snapshots needed after upstream data changes.

6. If writing to a spreadsheet/design doc is requested.
   - Before editing, state the target sheets/tables and exact change scope.
   - Do not overwrite user-corrected designs blindly. Read current content first and work with it.
   - In spreadsheet templates, replace only the sample business-field rows with designed business fields.
   - Preserve table-name formulas, business-field formulas, primary-key formulas, and fixed common-field SQL fragments.
   - After writing, verify generated table opening SQL, business-field SQL lines, fixed common fields, and primary key output.

## Browser Notes

- Prefer the user's Chrome browser session where the Codex extension is installed and the user is already logged in.
- First list/open Chrome tabs and identify the relevant Axhub prototype tab and Alidocs/DingTalk spreadsheet tab.
- Use the Browser plugin/Computer Use controls to click, navigate, screenshot, inspect, copy/paste, and verify content in Chrome.
- For Axhub, inspect the page tree, relevant screens, notes, and `data.js` if available.
- For Alidocs, operate the spreadsheet like Excel: switch sheets, read existing fields, preserve formulas, and paste only into the intended range.
- If screenshots or DOM extraction fail on interactive design tools, try page snapshots, iframe text, exported data files, or browser local cache search. Do not keep looping; explain uncertainty if the page is not reliably readable.
- Axhub may expose a `data.js`; when available, use it to recover page notes and hidden strings, but verify visible screens too.
- For password/login prompts, ask the user or use their already-open logged-in tab; do not guess credentials.

## Output Shape

For generation:

- List proposed entities with Chinese name, entity/table name, purpose, and lifecycle.
- Provide field rows with: field name, field code, type, required, remarks.
- Include relationships, status values, and business rules separately from field rows.
- Include naming rationale when the entity name may be ambiguous.

For review:

- Start with "缺失字段" and "冗余/不建议字段".
- Then list "可派生字段" and "需确认项".
- Keep findings tied to prototype screen/function and current entity/table names.

## Project Reference

For ERP/database-oriented work, read `references/project-db-entity-rules.md` before designing or reviewing fields.

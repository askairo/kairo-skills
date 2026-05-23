# Project DB Entity Design Notes

## ERP Defaults

- Java/Spring project: Znder ERP.
- Business modules use prefixes such as `srm`, `pms`, `wms`, `oms`, `tms`.
- Logical delete field: `is_del`, where `0` means active and `1` means deleted.
- Primary key: auto-increment `bigint`.
- Some table designs are maintained in spreadsheet templates with formulas that generate SQL.
- Preserve required common/template fields: `id`, `is_del`, `remark`, `create_time`, `create_by`, `create_id`, `create_name`, `update_time`, `update_by`, `update_id`, `update_name`.

## Spreadsheet Template Source

- Use the concrete spreadsheet template before designing rows. Do not rely only on memory of the template.
- Known template link for the current Znder ERP workflow:
  `https://alidocs.dingtalk.com/i/nodes/R1zknDm0WRwvyw61IZMa4R4eVBQEx5rG`
- When reading the template, confirm:
  - Required columns, such as field name, field code, type, required flag, remark, and generated SQL formula columns.
  - Required common field block and ordering.
  - How table name and table comment cells feed SQL formulas.
  - Existing example sheets that show the expected style.
- When writing to Alidocs, paste into the current project's database design document, not the template document, unless the user explicitly asks to edit the template itself.

## Formula Template Rules

The spreadsheet template has three formula patterns plus fixed SQL fragments:

1. Table-name formula.
   - Generates the `CREATE TABLE` opening line from the table-name cells.
   - Preserve this formula and only replace the Chinese table name / physical table name cells as needed.

2. Business-field formula.
   - Used by editable business-field example rows, such as `address`, `remark`, and `telephone` in the template.
   - When generating a new form/table, replace these example business rows with the designed business fields.
   - Keep/copy the business-field formula so each business field generates its SQL line from field name, field code, type, required flag, and remark.

3. Primary-key formula.
   - Generates the `PRIMARY KEY` line.
   - Preserve this formula; do not hand-type or delete it.

Fixed common fields are not ordinary business-field rows. Fields such as `id`, `is_del`, `create_time`, `create_by`, `create_id`, `create_name`, `update_time`, `update_by`, `update_id`, and `update_name` are fixed SQL fragments in the template. Keep them intact unless the user explicitly provides a new template rule.

When generating a form/table in Alidocs:

- Replace the template's sample business rows (`address`, `remark`, `telephone`, etc.) with the actual designed business fields.
- Use the existing business-field formulas for all inserted/replaced business rows.
- Preserve the table-name formula, primary-key formula, and fixed common-field SQL fragments.
- Verify that generated SQL still contains the table opening line, all business fields, the fixed common fields, and the primary key line.

## Design Rules

- Module prefix must be included in table names, for example `srm_xxx`.
- Keep table names concise but semantically clear. Prefer business abbreviations already used by the user or project.
- Do not create separate approval-record tables when Activiti/workflow already owns approval history.
- A business table may keep a lightweight status/cache field when the list/tab needs it, but workflow history and approver records should come from the workflow system.
- Do not add `attachment_ids`; use the common attachment table with `bizId` and `bizModel`.
- For rollback/cancel behavior, prefer `is_del` plus source-record status restoration when the user specifies logical deletion.
- Avoid storing display-only aggregation fields such as joined supplier names unless the user asks for denormalized search/display.

## Prototype Field Mapping Checklist

For each prototype page, capture:

- Tabs and status counts.
- Search/filter fields.
- List columns.
- Create/edit modal fields.
- Detail/approval modal fields.
- Import/export fields and traceability.
- Buttons and state transitions.
- Default values and generated-code rules.
- Aggregation rules and deduplication rules.

Map each item to one of:

- Stored in main table.
- Stored in detail table.
- Common/template field.
- Workflow/system-provided.
- Attachment system-provided.
- Derived by query/calculation.
- Intentionally omitted with reason.

## CLP Lessons From SRM Loading Plan

For SRM CLP-like "装柜清单/装柜计划" modules:

- Flow: existing loading list rows are selected to generate a loading plan.
- A plan has a main/header table and detail/item table.
- Detail rows should mostly snapshot loading-list fields plus `plan_id` and source loading-list/item id.
- Revocation is not a separate business status if the user says cancel should logic-delete plan header/detail and restore list rows to pending.
- Plan status is approval status; avoid adding a separate approval-record table.
- Loading scheme:
  - Single-site loading requires a main supplier.
  - Multi-site loading does not require a main supplier.
- Supplier display in plan list:
  - Use main supplier when present.
  - Otherwise derive all suppliers from details and de-duplicate.
- Supplier snapshots in list/details should include code, short name, full name, and address when supplier data can change later.
- Do not use supplier id when the user explicitly requests snapshot fields only.
- Keep import traceability if the prototype filters by import person/time or has "my imported" behavior.

## Review Red Flags

- Prototype has `导入人` / `导入时间` filters but table has no import trace field.
- Detail table lacks the source list/item id.
- Plan table stores `attachment_ids`.
- Business table duplicates approval records already owned by workflow.
- Plan detail fields drift away from loading list fields without a business reason.
- Table name and foreign key names use different concepts, such as `loading_list` in one place and `loading_item` in another.
- Required common fields from the project template are missing.

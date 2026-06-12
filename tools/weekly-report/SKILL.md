---
name: weekly-report
description: Write the user's weekly work report from screenshots or pasted task lists, using the existing Obsidian business weekly-report format, historical functional-area wording, and the configured weekly template. Use when the user says to write a weekly report, provides a screenshot of task titles, asks to refer to previous format or functional domains, or asks to update the business weekly report file.
---

# Weekly Report

## Scope

Use this skill for the Obsidian business workspace weekly report workflow.

- Workspace: `D:\znder\Obsidian\business`
- Template: `01-templates\inner\weekly.md`
- Historical examples and write target: `04-reviews\weekly.md`
- Main data source: screenshots or pasted task titles supplied by the user
- Secondary data source: recent entries in `04-reviews\weekly.md` for format, phrasing, functional areas, milestones, and next-week-plan style

## Workflow

1. Read workspace instructions first.
   - Check `AGENTS.md` in `D:\znder\Obsidian\business`.
   - If it does not exist, check parent directories only as needed.
   - Follow those instructions when present.

2. Read the weekly report template.
   - Use `01-templates\inner\weekly.md` as the required section structure.
   - Preserve the existing heading style from `04-reviews\weekly.md` when it is more specific than the bare template.

3. Read recent historical weekly reports.
   - Open the top entries of `04-reviews\weekly.md`.
   - Prefer the most recent 3-6 reports for functional-area naming and tone.
   - Reuse established area labels such as `供应链管理`, `仓储管理`, `库存管理`, `订单管理`, `商品管理`, `新品开发`, `海外物流`, `美仓表现`, `公共能力`, and `系统功能` when appropriate.

4. Extract tasks from the user input.
   - For screenshots, visually transcribe each task title before writing.
   - Keep bracketed module hints, for example `[wms]`, `[oms]`, `【采购单】`, `【装柜清单】`.
   - If OCR or visual reading is uncertain, state the uncertain item and ask only if the ambiguity changes the report meaning.

5. Map task titles to functional areas.
   - Prefer historical labels from `04-reviews\weekly.md`.
   - Map `采购单`, `采购合同`, `供应商`, `采购计划`, `装柜清单`, `排柜计划`, `海运排柜` to `供应链管理` unless the historical report clearly uses another label.
   - Map `[wms]`, `lxWms`, `认领单`, `库存结存`, `入库`, `出库`, `盘点`, `仓库` to `仓储管理` unless the task is explicitly inventory-center reporting, then use `库存管理`.
   - Map `[oms]`, `vcpo`, `VCPO`, `VCDF`, `订单同步`, `标记发货`, `一键代发` to `订单管理`.
   - Map cross-module utilities such as file preview, export center, common APIs, and proxy upgrades to `公共能力` only when no business domain is stronger.

6. Draft the weekly report.
   - Use today's date unless the user gives a specific week/date.
   - Insert the newest report at the top of `04-reviews\weekly.md`.
   - Required structure:

```markdown
## YYYY-MM-DD
### **开发任务**
#### 功能开发

1. 功能领域: 任务说明
2. 功能领域: 任务说明
#### 其他
1. 本周需求分析, 开发设计, 任务安排
2. 已有功能维护

### **里程碑 & 问题**
1. ...

### **下周计划**
1. ...
```

7. Write in the user's established style.
   - Keep lines concise and work-report oriented.
   - Prefer `功能领域: 动作, 结果/范围` phrasing.
   - Use ASCII punctuation where the file already uses it, but keep Chinese text natural.
   - Avoid marketing language and invented metrics.
   - Do not overstate completion. If a title says `开发设计`, write design/planning; if it says `后端`, write backend development; if it says `优化`, write optimization.

8. Verify after editing.
   - Reopen the top 40-80 lines of `04-reviews\weekly.md`.
   - Confirm the new report is at the top, headings match nearby reports, numbering is valid, and every user-provided task appears once.
   - Mention any missing `AGENTS.md` or uncertainty in the final response.

## Data Source Rules

- User screenshot or pasted task list is the source of actual work items.
- `04-reviews\weekly.md` is the source of format, domain vocabulary, and summary style.
- `01-templates\inner\weekly.md` is the source of required report sections.
- Do not derive new work items from SQL files, commits, or memories unless the user explicitly asks for enrichment from those sources.

## Write Target

Write the finished report into:

`D:\znder\Obsidian\business\04-reviews\weekly.md`

Insert it above the previous newest report. Do not create a separate weekly file unless the user explicitly asks.

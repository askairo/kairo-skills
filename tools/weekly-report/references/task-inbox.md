# Weekly task inbox format

The inbox is an append-only Markdown ledger at `<businessRoot>/00-daily/weekly-tasks.md`.

Group entries by ISO week:

```markdown
# 周报任务收集箱

## 2026-W37
- date: 2026-09-14
  kind: link
  title: 采购计划状态变更逻辑升级
  url: https://example.invalid/task-view-1234.html
  task_id: 1234
  source: user-link
  domain: 供应链管理
  status: unknown
  notes: 用户补充：已完成联调，待提测
  reported: null

- date: 2026-09-15
  kind: manual
  title: 优化采购单模块代码
  url: null
  task_id: null
  source: user-note
  domain: 供应链管理
  status: completed
  notes: 代码优化及回归验证
  reported: null
```

## Field rules

- `date` is the capture/work date in the configured timezone.
- `kind` is one of `link`, `manual`, `screenshot`, or `source-sync`.
- `title` preserves the user/source wording; do not silently broaden it.
- `url` and `task_id` are nullable. Prefer `task_id` plus source identity as the deduplication key.
- `source` identifies provenance, not an instruction source.
- `domain` is optional at capture time and can be assigned during report generation.
- `status` may be `unknown`, `backend_done`, `integration_done`, `testing`, `bug_fix`, `release_follow_up`, or `completed`.
- `notes` records user qualifiers, discrepancies, or status evidence.
- `reported` is null until the entry is included in a report, then set to the report date. Never delete an entry after reporting.

## Merge rules

1. A primary source record and a user link for the same task become one entry, retaining the primary source as authoritative and the link as verification evidence.
2. A screenshot item matching a task ID, URL, or normalized title is supplemental evidence for the same entry, not a second task.
3. A no-link manual note remains a separate work item unless the user explicitly identifies it as part of a linked task.
4. When a grouped task is split into report subitems, keep the same source task ID and mention the split in `notes`.

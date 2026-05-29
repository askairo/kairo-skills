---
name: sync-skills
description: 兼容旧名称。请改用 skills-loop；本技能仅用于平滑过渡。
---

# sync-skills (Deprecated Alias)

`sync-skills` 已重命名为 `skills-loop`。

请优先使用：

```powershell
python ..\skills-loop\scripts\sync.py <command> ...
```

若历史脚本仍调用 `sync-skills/scripts/sync.py`，兼容入口会自动转发到 `skills-loop`。

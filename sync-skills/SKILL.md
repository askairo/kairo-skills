---
name: sync-skills
description: 旧名称兼容入口，当前请改用 skills-loop。仅用于平滑过渡和历史脚本兼容。
---

# sync-skills（已弃用）

`sync-skills` 已重命名为 `skills-loop`。

请优先使用：

```powershell
python ..\skills-loop\scripts\sync.py <command> ...
```

如果历史脚本还在调用 `sync-skills/scripts/sync.py`，兼容入口会自动转发到 `skills-loop`。

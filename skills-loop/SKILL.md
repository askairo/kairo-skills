---
name: skills-loop
description: 以“源码仓库 -> GitHub -> Agent运行目录”为闭环管理 skills 的持续迭代。支持在任意工作目录触发发布、回写、同步与校验，也支持从第三方 GitHub 仓库安装和更新。
---

# Skills Loop

把 skills 的长期维护模型统一成：

```text
本地 skills 源码仓库 -> GitHub -> 当前 Agent skills 运行目录 -> 反馈下一轮迭代
```

## 核心原则

- GitHub 是跨机器、跨 Agent 的分发源。
- 本地源码仓库只用于开发和提交，例如 `D:\private-vs-space\kairo-skills`。
- 当前 Agent 的 skills 目录只是运行时安装目标，例如 `C:\Users\admin\.codex\skills`。
- 用户用自然语言表达意图，Agent 负责选择脚本命令。
- 不依赖环境变量作为主要配置。优先级是：自然语言/显式参数 > 本地配置文件 > 已安装来源元数据 > 自动发现 > 环境变量兜底。

## 常见高频场景：在任意工作目录触发技能迭代

当你在业务仓库里优化 skill（而不是在 `kairo-skills` 目录内）时，执行闭环应遵循：

1. 自动识别并回到 skills 源码仓库（默认 `kairo-skills`）。
2. 校验并提交目标 skill 变更。
3. 推送到 GitHub。
4. 从 GitHub 回装到 `C:\Users\admin\.codex\skills`。
5. 保留备份并提示重启会话验证。

脚本已支持从任意目录触发 `publish-and-update`；若自动发现失败，再显式传 `--local-repo`。

## 适用场景

### 1. 维护自己的 skill

当用户要求优化自己的某个 skill，例如 `hexo-push`：

1. 修改本地源码仓库中的 skill：

   ```text
   D:\private-vs-space\kairo-skills\<skill-name>
   ```

2. 验证：
   - `SKILL.md` 可读且描述清楚
   - Python 脚本执行 `py_compile`
   - 如果支持 dry-run，跑一次最小 dry-run
   - 检查 git diff
3. 提交并推送本地 skills 仓库。
4. 再从 GitHub 拉取刚推送的 skill，覆盖当前 Agent 的运行时目录。
5. 校验当前 Agent 目录下的文件与来源一致。
6. 提醒用户重启 Agent 或开新会话加载最新 skill 元信息。

脚本命令：

```powershell
python scripts/sync.py publish-and-update --skill hexo-push --message "feat: improve hexo push publishing flow"
```

### 2. 在另一个 Agent 环境安装或更新自己的 skill

当用户切到另一台机器或另一个 Agent，只想从 GitHub 拉取：

```powershell
python scripts/sync.py install --repo askairo/kairo-skills --path hexo-push
```

如果本地已有同名 skill，会先备份再覆盖。

### 3. 更新已安装的 GitHub skill

安装或更新后，脚本会在 skill 目录写入来源元数据：

```text
.skill-source.json
```

之后可以直接更新：

```powershell
python scripts/sync.py update --skill hexo-push
```

或更新全部带来源元数据的 skills：

```powershell
python scripts/sync.py update-all
```

清理安装/更新时自动生成的备份目录（`*.backup.YYYYmmdd_HHMMSS`）：

```powershell
python scripts/sync.py cleanup-backups
```

只清理某个 skill 的备份：

```powershell
python scripts/sync.py cleanup-backups --skill hexo-push
```

### 4. 安装第三方 skill

第三方 GitHub 仓库也可以使用同样流程：

```powershell
python scripts/sync.py install --repo owner/repo --path path/to/skill --ref main
```

区别是：第三方仓库通常只能安装/更新，不能 publish，除非用户维护 fork 或拥有推送权限。

## 配置文件

推荐使用配置文件，而不是环境变量。

可选配置文件位置：

- 当前 skills 源码仓库：`.skills-loop.json`（兼容 `.sync-skills.json`）
- 当前 `skills-loop` skill 目录：`skills-loop.local.json`（兼容 `sync-skills.local.json`）
- 用户配置目录：`~/.config/skills/.skills-loop.json`（兼容 `.sync-skills.json`）
- Codex 用户目录：`~/.codex/.skills-loop.json`（兼容 `.sync-skills.json`）

示例：

```json
{
  "defaultRepo": "askairo/kairo-skills",
  "defaultRef": "main",
  "localRepoPath": "D:\\private-vs-space\\kairo-skills",
  "agentSkillsDir": "C:\\Users\\admin\\.codex\\skills"
}
```

可以用脚本生成本地配置：

```powershell
python scripts/sync.py write-config --repo askairo/kairo-skills --local-repo D:\private-vs-space\kairo-skills --agent-dir C:\Users\admin\.codex\skills
```

## 常用命令

列出当前 Agent 已安装 skills 和来源：

```powershell
python scripts/sync.py list
```

发布本地修改并更新当前 Agent：

```powershell
python scripts/sync.py publish-and-update --skill skills-loop --message "feat: improve skills loop workflow"
```

只发布本地仓库，不更新当前 Agent：

```powershell
python scripts/sync.py publish --skill skills-loop --message "feat: improve skills loop workflow"
```

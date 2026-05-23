---
name: sync-skills
description: 基于 GitHub 管理 skills 的安装、更新、发布和当前 Agent 运行时同步。支持维护自己的 skills 仓库，也支持从第三方 GitHub 仓库拉取并覆盖更新本地同名 skill。
---

# Skills GitHub 同步工具

把 skills 的长期维护模型统一成：

```text
本地 skills 源码仓库 -> GitHub -> 当前 Agent skills 运行目录
```

## 核心原则

- GitHub 是跨机器、跨 Agent 的分发源。
- 本地源码仓库只用于开发和提交，例如 `D:\private-vs-space\kairo-skills`。
- 当前 Agent 的 skills 目录只是运行时安装目标，例如 `C:\Users\admin\.codex\skills`。
- 用户用自然语言表达意图，Agent 负责选择脚本命令。
- 不依赖环境变量作为主要配置。优先级是：自然语言/显式参数 > 本地配置文件 > 已安装来源元数据 > 自动发现 > 环境变量兜底。

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

### 4. 安装第三方 skill

第三方 GitHub 仓库也可以使用同样流程：

```powershell
python scripts/sync.py install --repo owner/repo --path path/to/skill --ref main
```

区别是：第三方仓库通常只能安装/更新，不能 publish，除非用户维护 fork 或拥有推送权限。

## 配置文件

推荐使用配置文件，而不是环境变量。

可选配置文件位置：

- 当前 skills 源码仓库：`.sync-skills.json`
- 当前 `sync-skills` skill 目录：`sync-skills.local.json`
- 用户配置目录：`~/.config/skills/.sync-skills.json`
- Codex 用户目录：`~/.codex/.sync-skills.json`

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

## 环境变量

环境变量只作为兜底兼容，不作为主推荐方式：

- `SKILLS_DEFAULT_REPO`
- `SKILLS_DEFAULT_REF`
- `SKILLS_PROJECT_DIR`
- `SKILLS_USER_DIR`

不要把稳定路径配置长期只放在环境变量里；这样会增加跨 Agent、跨 shell、跨机器的维护成本。

## 常用命令

列出当前 Agent 已安装 skills 和来源：

```powershell
python scripts/sync.py list
```

从默认仓库安装或覆盖更新：

```powershell
python scripts/sync.py install --skill hexo-push
```

从指定 GitHub 仓库安装：

```powershell
python scripts/sync.py install --repo askairo/kairo-skills --path hexo-push --ref main
```

更新已安装 skill：

```powershell
python scripts/sync.py update --skill hexo-push
```

更新所有带来源元数据的 skills：

```powershell
python scripts/sync.py update-all
```

发布本地修改并更新当前 Agent：

```powershell
python scripts/sync.py publish-and-update --skill sync-skills --message "feat: improve sync skills workflow"
```

只发布本地仓库，不更新当前 Agent：

```powershell
python scripts/sync.py publish --skill sync-skills --message "feat: improve sync skills workflow"
```

试运行：

```powershell
python scripts/sync.py install --skill hexo-push --dry-run
```

## Agent 执行约定

当用户说“优化某个 skill 并同步到当前 Agent”时：

1. 必须修改本地源码仓库，不直接把运行时目录当源码维护。
2. 先验证，再提交推送。
3. 推送后，从 GitHub 拉取并覆盖当前 Agent 目录。
4. 如果覆盖本地同名 skill，脚本会自动备份旧目录。
5. 完成后说明 commit、push、安装/更新结果。

当用户说“从 GitHub 更新这个 skill”时：

1. 优先读取已安装 skill 的 `.skill-source.json`。
2. 如果没有来源元数据，要求用户提供 repo/path，或使用默认配置。
3. 覆盖前备份旧目录。
4. 更新后写回 `.skill-source.json`。

## 注意事项

- 安装和更新需要网络访问 GitHub。
- 私有仓库建议走已配置好的 git 凭据或先 fork 到可访问仓库；当前脚本默认使用 GitHub zip archive 下载公开内容。
- 当前脚本只依赖 Python 标准库。
- 对运行时目录的覆盖是有意行为，但覆盖前会备份同名 skill。

---
name: skills-loop
description: 以源码仓库到 GitHub 再到 Agent 运行目录的闭环管理 skills 持续迭代。Use whenever any skill is created, edited, optimized, upgraded, published, installed, updated, synced, or repaired, even if the user does not explicitly name skills-loop. For skill content creation or modification, coordinate with skill-creator for authoring guidance, then use skills-loop for publishing, installing, updating, backups, and source/runtime consistency.
---

# Skills Loop

把 skills 的长期维护模型统一成：

```text
本地 skills 源码仓库 -> GitHub -> 当前 Agent skills 运行目录 -> 反馈下一轮迭代
```

## 核心原则

- GitHub 是跨机器、跨 Agent 的分发源。
- 本地源码仓库只用于开发和提交；具体路径来自配置、显式参数、已安装来源元数据或自动发现。
- 当前 Agent 的 skills 目录只是运行时安装目标；具体路径来自配置、显式参数或脚本所在位置。
- 用户用自然语言表达意图，Agent 负责选择脚本命令。
- 不依赖环境变量作为主要配置。优先级是：自然语言/显式参数 > 本地配置文件 > 已安装来源元数据 > 自动发现 > 环境变量兜底。
- 如果仓库维护双语 README，应把双语内容收敛到同一个 `README.md` 中，顶部提供可点击的语言切换按钮，语言切换后跳转到同一文件里的对应语言区块，避免维护两份独立 README。
- 对于 `skills-loop` 创建、更新或修复的技能，只要该技能维护 README，就默认要求使用单个 `README.md` 承载中英文双语内容，并在文档顶部提供可点击的语言切换按钮，确保两个语言区块的结构、入口和维护说明保持一致。

## 触发规则

只要任务涉及 skill 的创建、修改、优化、升级、安装、同步、发布、回装、配置迁移、脚本修复、参考文档调整、触发描述调整、或运行目录与源码仓库一致性处理，就使用本技能流程化处理。不要等用户明确说“使用 skills-loop”才触发。

如果任务只是普通业务代码开发、项目文档编写、或不涉及 skill 文件与 skill 生命周期，则不要使用本技能。

## 与 skill-creator 协作

当任务涉及新建 skill、修改 `SKILL.md` frontmatter/description、调整触发规则、增删 scripts/references/assets、或改变技能工作流时，先使用 `$skill-creator` 负责 skill 内容设计与编辑规范，再使用本技能完成生命周期闭环：

- 创建或重构 skill 时，按 `skill-creator` 的流程决定 `SKILL.md`、`scripts/`、`references/`、`assets/` 的内容边界。
- 修改已有 skill 时，仍用 `skill-creator` 判断触发描述是否准确、上下文是否精简、资源是否必要。
- 本技能不重复定义 skill authoring 规则；只负责源码仓库、GitHub、Agent 运行目录之间的发布、安装、更新、备份和一致性检查。
- 发布前可以运行 `skill-creator` 的 `quick_validate.py` 和脚本语法检查，但这属于质量门禁，不替代 `skill-creator` 的设计职责。

## Skill 配置边界

创建或优化任何 skill 时，按同一条边界处理本地路径配置和技能规范：

- 本地配置只保存用户机器相关的“总根目录”或“根路径”，例如 `docs.root`、`localRepoPath`、`agentSkillsDir`。
- 不要把技能内部目录结构、文件名、任务卡命名、项目文档清单等规范外包给本地配置。
- 具体到根目录下面创建哪些子目录和文件，应由 skill 自己定义。
- 不要在 `SKILL.md`、`references/` 或脚本默认值里写死个人机器路径、个人 GitHub 仓库、个人 Obsidian 路径。
- 示例路径使用占位符，例如 `<absolute-docs-root>`、`<local-skills-repo>`、`<agent-skills-dir>`、`<owner>/<repo>`。

推荐模式：

```yaml
version: 1

docs:
  root: <absolute-docs-root>
```

技能内部再定义自己的结构，例如：

```text
kickoff-flow: <docs.root>/<project-name>/00-overview.md
task-dev-flow: <docs.root>/<repo-name>/<prefix>-<id>.md
```

也就是说，`docs.root` 属于用户配置；`<project-name>`、`<repo-name>`、`00-overview.md`、`10-roadmap.md`、`<prefix>-<id>.md` 属于技能规范。

## 常见高频场景：在任意工作目录触发技能迭代

当你在业务仓库里优化 skill（而不是在 skills 源码仓库目录内）时，执行闭环应遵循：

1. 自动识别并回到 skills 源码仓库；若无法识别，读取配置或要求用户提供源码仓库路径。
2. 校验并提交目标 skill 变更。
3. 推送到 GitHub。
4. 从 GitHub 回装到当前 Agent skills 运行目录。
5. 保留备份并提示重启会话验证。

脚本已支持从任意目录触发 `publish-and-update`；若自动发现失败，再显式传 `--local-repo`。

## 适用场景

### 1. 维护自己的 skill

当用户要求优化自己的某个 skill，例如 `hexo-push`：

1. 修改本地源码仓库中的 skill：

   ```text
   <local-skills-repo>/<skill-name>
   ```

2. 验证：
   - `SKILL.md` 可读且描述清楚
   - 若 skill 维护 README，则 `README.md` 应同时包含中英文内容，并且顶部语言切换按钮可跳转到同一文件内的对应语言区块
   - 若改动涉及 skill 内容设计，先按 `skill-creator` 完成创建或修改
   - 使用 `skill-creator` 的 `quick_validate.py` 校验目标 skill
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
python scripts/sync.py install --repo <owner>/<repo> --path hexo-push
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
- 当前 Agent 的用户目录（自动检测，按优先级）：`~/.qoderworkcn/.skills-loop.json`、`~/.codex/.skills-loop.json`、`~/.config/agents/.skills-loop.json`（均兼容 `.sync-skills.json`）

示例：

```json
{
  "defaultRepo": "<owner>/<repo>",
  "defaultRef": "main",
  "localRepoPath": "<absolute-local-skills-repo>",
  "agentSkillsDir": "<absolute-agent-skills-dir>"
}
```

可以用脚本生成本地配置：

```powershell
python scripts/sync.py write-config --repo <owner>/<repo> --local-repo <absolute-local-skills-repo> --agent-dir <absolute-agent-skills-dir>
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

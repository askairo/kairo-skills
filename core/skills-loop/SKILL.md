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
- 源码仓库可以按包分组；脚本会递归发现 `SKILL.md`，并用 frontmatter 的 `name` 解析 skill。
- 用户用自然语言表达意图，Agent 负责选择脚本命令。
- 不依赖环境变量作为主要配置。优先级是：自然语言/显式参数 > 本地配置文件 > 已安装来源元数据 > 自动发现 > 环境变量兜底。
- 多 agent 环境下，不要默认猜测运行目录；如果检测到多个 agent skills 目录，必须显式传 `--agent-dir`。

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

创建或优化任何自有 skill 时，统一分离三类内容：

- **Skill 规范**：工作流、配置 schema、目录结构、文件命名、允许值、默认规则和安全门禁。保存在 skill 源码中并通过 GitHub 分发。
- **Agent 本地配置**：用户或机器特有、需要跨项目复用且不适合进入 Git 的运行数据，例如根路径、账号画像、内容风格、来源清单、环境映射和执行策略。
- **凭证与会话**：密码、Cookie、令牌、恢复码和浏览器登录态。不要保存在普通 skill 配置中；使用 Agent 连接器、系统凭证库或受控会话。

不要把 Skill 规范外包给本地配置。配置可以选择“使用哪个账号、风格、来源或策略”，但这些对象的字段、引用关系、合法值和不可关闭的门禁必须由 Skill 定义。

不要在 `SKILL.md`、`references/` 或脚本默认值里写死个人机器路径、个人 GitHub 仓库、个人 Obsidian 路径和真实账号数据。示例使用 `<absolute-docs-root>`、`<local-skills-repo>`、`<agent-skills-dir>`、`<account-handle>`、`<owner>/<repo>` 等占位符。

### Agent Home resolution

`<AGENT_HOME>` 表示当前 Agent 的用户配置根目录。按以下顺序解析：

1. 使用用户或命令显式指定的 Agent Home。
2. 若当前 Skill 的运行路径位于 `<AGENT_HOME>/skills/<skill-name>/`，从该路径确定 Agent Home。
3. 若工作目录明确位于某个 Agent Home 内，使用该目录。
4. 若本机只存在一个已知 Agent Home，使用它。
5. 若存在多个候选且当前上下文无法区分，必须要求用户或调用方显式选择；不要跨 Agent 读取配置。
6. 若没有已知 Agent Home，使用当前 Agent 定义的通用配置根；仍无法确定时先询问用户。

### Preferred local config directory

所有自有 Skills 的首选本地配置目录统一为：

```text
<AGENT_HOME>/local-config/<skill-name>/
```

- 单文件配置优先命名为 `config.yaml` 或 `config.json`。
- 按职责拆分时使用稳定语义名，例如 `paths.yaml`、`accounts.yaml`、`sources.yaml`；文件结构由 Skill 自己定义。
- 本地配置不得放入源码仓库或已安装 Skill 目录，因为发布和回装不应覆盖用户配置。
- 显式配置路径可以覆盖首选目录。
- 不为旧目录、旧文件名或旧命令保留兼容分支；规范升级时直接使用当前约定，避免长期维护多套入口。

路径配置示例：

```yaml
version: 1

docs:
  root: <absolute-docs-root>
```

技能内部再定义自己的结构，例如：

```text
p-bootstrap: <docs.root>/<project-name>/00-overview.md
p-task: <docs.root>/<repo-name>/<prefix>-<id>.md
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
   <local-skills-repo>/<package>/<skill-name>
   ```

2. 验证：
   - `SKILL.md` 可读且描述清楚
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
python core\skills-loop\scripts\sync.py publish-and-update --skill hexo-push --message "feat: improve hexo push publishing flow"
```

### 2. 在另一个 Agent 环境安装或更新自己的 skill

当用户切到另一台机器或另一个 Agent，只想从 GitHub 拉取：

```powershell
python core\skills-loop\scripts\sync.py install --repo <owner>/<repo> --skill hexo-push
```

如果本地已有同名 skill，会先备份再覆盖。

也可以使用显式包路径：

```powershell
python core\skills-loop\scripts\sync.py install --repo <owner>/<repo> --path blog/hexo-push
```

### 3. 更新已安装的 GitHub skill

安装或更新后，脚本会在 skill 目录写入来源元数据：

```text
.skill-source.json
```

之后可以直接更新：

```powershell
python core\skills-loop\scripts\sync.py update --skill hexo-push
```

或更新全部带来源元数据的 skills：

```powershell
python core\skills-loop\scripts\sync.py update-all
```

清理安装/更新时自动生成的备份目录（`*.backup.YYYYmmdd_HHMMSS`）：

```powershell
python core\skills-loop\scripts\sync.py cleanup-backups
```

只清理某个 skill 的备份：

```powershell
python core\skills-loop\scripts\sync.py cleanup-backups --skill hexo-push
```

### 4. 安装第三方 skill

第三方 GitHub 仓库也可以使用同样流程：

```powershell
python core\skills-loop\scripts\sync.py install --repo owner/repo --path path/to/skill --ref main
```

区别是：第三方仓库通常只能安装/更新，不能 publish，除非用户维护 fork 或拥有推送权限。

## 配置文件

`skills-loop` 自身也遵循 Agent 本地配置目录规范。首选配置文件为：

```text
<AGENT_HOME>/local-config/skills-loop/config.json
```

配置优先级为：显式命令参数 > 首选 Agent 本地配置 > 已安装来源元数据 > 自动发现 > 环境变量兜底。

只支持上述首选配置文件，不读取其他历史位置，也不提供旧命令别名。

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
python core\skills-loop\scripts\sync.py write-config --repo <owner>/<repo> --local-repo <absolute-local-skills-repo> --agent-dir <absolute-agent-skills-dir> --config-dir <agent-home>
```

当只存在一个 Agent Home、脚本从已安装的 `skills-loop` 内运行，或 `--agent-dir` 明确指向 `<AGENT_HOME>/skills` 时，可以省略 `--config-dir`。否则存在多个 Agent Home 时必须显式指定。

## 常用命令

列出当前 Agent 已安装 skills 和来源：

```powershell
python core\skills-loop\scripts\sync.py list
```

发布本地修改并更新当前 Agent：

```powershell
python core\skills-loop\scripts\sync.py publish-and-update --skill skills-loop --message "feat: improve skills loop workflow"
```

只发布本地仓库，不更新当前 Agent：

```powershell
python core\skills-loop\scripts\sync.py publish --skill skills-loop --message "feat: improve skills loop workflow"
```

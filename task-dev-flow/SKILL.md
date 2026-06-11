---
name: task-dev-flow
description: 将外部任务、工单、需求链接、原型链接或任务描述转成完整的开发流程。用于理解任务信息、检查需求来源、创建或使用任务分支、拆解实施卡片、遵循仓库规则、实现变更并完成验证。纯实体表设计请改用 entity-design。
---

# Task Dev Flow

## 目标

把外部任务转成“可执行、可验证、可交付”的本地开发流程。适用对象包括禅道、Jira、GitHub issue、原型链接、内部文档、截图或直接粘贴的任务描述。

如果项目还处在探索期、架构不稳定，或者项目级文档还没理顺，先使用 `new-order` 把项目文档和架构顺序建立起来，再回到这里做任务拆解和实现。

## 本地配置

本 skill 使用本机私有配置保存稳定路径和认证信息。不要把这些配置写进项目仓库。

### Agent Home 解析

`<AGENT_HOME>` 表示当前 Agent 的配置根目录。读取或写入本地配置前必须先解析它，而且只能使用当前 Agent 对应的目录。

解析顺序：

1. 工作目录路径包含 `.qoderworkcn`，使用 `~/.qoderworkcn/`
2. 工作目录路径包含 `.codex`，使用 `~/.codex/`
3. 如果 `~/.qoderworkcn/` 存在，使用它
4. 如果 `~/.codex/` 存在，使用它
5. 兜底到 `~/.config/skills/`

解析后必须确认目录真实存在。若都不存在，就询问用户选择哪个 Agent Home。

**硬规则：** 一旦解析出 `<AGENT_HOME>`，只能读写这个目录下的配置，不要跨 Agent 目录。

### 配置文件

- 认证配置：`<AGENT_HOME>/local-config/task-dev-flow/auth-sites.yaml`
- 路径配置：`<AGENT_HOME>/local-config/task-dev-flow/paths.yaml`

推荐路径配置：

```yaml
version: 1

docs:
  root: <absolute-task-docs-root>
```

- `docs.root` 是任务文档根目录，例如 Obsidian 的 `03-req`。
- 该 skill 负责 `docs.root` 下的结构：
  - 项目级文档：`<docs.root>/<repo-name>/`
  - 执行计划：`<docs.root>/<repo-name>/plans/`
  - 任务文档：`<docs.root>/<repo-name>/tasks/`
- 如果项目已有旧的扁平结构，也要兼容；新项目优先用 `tasks/`。
- 如果没有配置且用户没给文档根目录，就先询问，再写入本地配置。

## 工作流

1. 收集任务信息。
   - 支持任务链接、issue 编号、截图、原型、自然语言描述。
   - 提取稳定信息：标题、ID、来源链接、产品区域、仓库、目标分支。
   - 若任务编号冲突，以用户明确说明为准。
   - 根据来源映射统一前缀：
     - `task-view-1336` -> `feat-1336`
     - `bug-view-6076` -> `fix-6076`
     - 性能/优化项 -> `perf-<id>`

2. 检查需求来源。
   - 若需求已在 Chrome 打开并要求使用浏览器，就直接读该页面。
   - 若需要认证，先查本地认证配置。
   - 若需要稳定输出路径，先查路径配置。
   - 原型或实体设计需要单独分析时，先调用 `entity-design`。

3. 读取仓库规则。
   - 先看仓库里的 `AGENTS.md`、`CLAUDE.md`、根 README。
   - 若还有架构、SQL、模块或流程文档，只读与当前任务直接相关的部分。
   - 项目有项目级文档时，先看 `00-overview`、`10-roadmap`、`20-*.md`、`30-decisions`、`31-open-questions`、`32-risk-log`，再看相关 `plans/` 和 `tasks/`。

4. 创建或选择任务分支。
   - 先看当前分支和工作区状态。
   - 避免污染无关改动。
   - 如果分支不存在，基于仓库基线分支新建。
   - Znder ERP 仓库默认基线顺序：`master` -> `main` -> 仓库规则指定基线。

5. 拆分任务卡。
   - 先把需求拆成简短 checklist。
   - 任务卡要面向结果，例如接口、持久化、映射、日志、校验、测试。
   - 写任务文档时遵循 `references/task-template.md`。
   - 任务文档命名固定为 `<prefix>-<id>.md`，前缀通常是 `feat`、`fix` 或 `perf`。
   - 文档目录优先写入 `<docs.root>/<repo-name>/tasks/`；项目级规划放在 `plans/`。
   - 如果项目采用 `new-order` 的层级约束，要同步维护 20 层关注点文档，以及 `30-decisions`、`31-open-questions` 和 `32-risk-log`。
   - 文档里的 `source`、`branch`、`baseline`、`commit` 要和真实状态同步。

6. 按仓库结构实现。
   - 以现有代码路径和模式为起点。
   - 保持分层、命名、SQL、验证和提交规范与仓库一致。
   - 如果项目约定缺失但重复出现，建议补到仓库规则文件里，而不是塞进 skill 本身。

7. 验证。
   - 先跑最窄的检查，再扩大范围。
   - 共享契约、控制器、流程或持久化改动时要增加验证力度。
   - 明确报告与本次任务无关的阻塞项。

8. 交付。
   - 只有在用户明确要求时才提交或推送。
   - 需要 commit 时，任务文档里的 commit message 一旦生成就视为固定文本。
   - 不要擅自更换提交信息。

9. 收尾。
   - 再核对一次分支、任务文档和必要文件是否齐全。
   - 总结变更、验证结果和剩余风险。

## 和其他 skills 的配合

- 需求主要是实体、表结构、主从关系或字段推导时，先用 `entity-design`。
- 项目处于新建阶段、文档缺失或结构混乱时，先用 `new-order`。
- 任务完成后是否合并分支，不属于这个 skill 的默认职责。

# p-loop 项目推进闭环

`p-loop` 的职责不是替代 `p-task` 执行任务，而是让项目能够在 Agent 更换、会话中断、模型不可用或跨机器运行后，基于外部文档继续推进。

## 1. 外部文档是恢复事实源

项目连续性不依赖当前会话记忆、临时上下文或某个 Agent 的本地状态。恢复时按以下顺序读取：

```text
00-overview.md
→ 10-roadmap.md
→ 20-*.md
→ 30-decisions.md
→ 31-open-questions.md
→ 32-risk-log.md
→ plans/
→ 当前 task doc
```

外部文档必须记录最近一次已确认的项目状态、当前阶段、已完成工作、未决问题、风险、下一步和人工接管点。若文档与代码、任务记录或实际验证结果冲突，先进入 `review_required`，不能凭当前会话猜测并继续。

## 2. 项目状态

每个项目周期使用以下状态之一：

```text
clarifying       # 关键目标、范围或决策仍不明确
planned          # 当前方向和阶段计划已明确
ready_for_task   # 已满足任务拆分条件，可交给 p-task
executing        # p-task 正在执行
review_required  # 发现高风险决策或结果需要人工接管
blocked          # 依赖、验证或权限条件不足
```

任务完成不直接等于项目完成。`p-loop` 必须根据验证结果把项目重新归入 `planned`、`clarifying`、`review_required` 或 `blocked`，并生成下一步。

## 3. 一个规划周期

```text
读取外部状态
 → 建立当前快照
 → 确定焦点与阶段目标
 → 识别决策风险
 → 形成阶段计划
 → 检查 ready_for_task
 → 交给 p-task
 → 接收执行与验证结果
 → 更新外部文档
 → 判断下一阶段或人工接管
```

只有以下条件同时满足，才进入 `ready_for_task`：

- 目标和范围明确；
- 交付对象明确；
- 验收标准可验证；
- 依赖、风险和假设已记录；
- 不存在会改变方案的关键未决问题；
- 已确定是否需要人工确认以及确认发生在哪个节点。

## 4. 自动推进与人工接管

默认自动推进以下低风险工作：

- 读取和整理项目状态；
- 拆分普通任务；
- 编写或更新计划、任务和进度文档；
- 执行已确认范围内的普通实现；
- 运行验证并记录结果；
- 生成下一步计划。

以下情况进入 `review_required`，暂停外部副作用并请求人工确认：

- 改变项目目标、范围、架构方向或阶段优先级；
- 扩大权限、影响范围、成本或第三方依赖；
- 破坏性数据/文件操作、生产环境变更或正式发布；
- 凭证、账号、安全策略或隐私边界变化；
- 不可逆操作、长期配置变更或持续运行任务；
- 关键决策冲突、验收标准改变或执行结果无法确认；
- Agent 无法判断继续执行是否仍符合用户意图。

人工确认必须绑定具体变更、影响范围和回滚方式，不能用笼统的“继续吗”代替。

## 5. p-task 交接协议

交给 `p-task` 的任务必须包含：

```text
projectRef, phaseRef, taskRef,
goal, scope, nonGoals,
inputs, assumptions, dependencies,
acceptanceCriteria, verificationPlan,
riskLevel, approvalBoundary,
writebackTargets, nextOnSuccess, nextOnFailure
```

`p-task` 完成后必须返回：

```text
taskRef, status, changedFiles, verification,
observations, risks, openQuestions,
commitOrPushState, writebackStatus,
recommendedNextState, recommendedNextStep
```

如果执行中发现范围、架构或风险发生变化，`p-task` 不自行扩大范围，转为 `review_required` 并回写原因。

## 6. 阶段回写门

每完成一个阶段或发生一次重要阻断，至少更新：

- `10-roadmap.md`：阶段状态、当前焦点和下一步顺序；
- 相关 `20-*.md`：持久架构、流程或验收约束；
- `30-decisions.md`：已确认的新决策；
- `31-open-questions.md`：仍未确认且会影响后续的问题；
- `32-risk-log.md`：新风险、依赖和阻塞；
- 对应 `plans/` 或 `tasks/`：执行进度、验证结果和交接状态。

回写内容应能让新的 Agent 在没有当前会话上下文时回答：已经做到哪一步、哪些结果可信、哪些动作已经产生副作用、为什么暂停、下一步从哪里继续。

## 7. 继续执行判定

恢复运行时：

1. 读取最新外部文档和任务记录；
2. 找到最后一个有验证证据的阶段；
3. 检查是否存在未完成的人工确认、高风险动作或不确定副作用；
4. 若没有，按 `nextOnSuccess` / `nextOnFailure` 继续；
5. 若文档过期、状态冲突或证据不足，进入 `review_required` 或 `blocked`；
6. 不重复已完成的不可逆动作，不从项目起点重新规划。

“继续执行”必须基于外部记录中的明确下一步，而不是基于模型对上次对话的记忆。

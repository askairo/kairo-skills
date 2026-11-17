# 配置、派工、证据与恢复契约

## 可选本地配置

唯一位置：`~/.agents/local-config/t-loop/config.json`。缺省可直接采用职责 ID 和当前宿主能力，不强迫创建配置。

```json
{
  "version": 2,
  "roleAliases": {
    "coordinator": "Coordinator",
    "researcher": "Researcher",
    "implementer": "Implementer",
    "code_reviewer": "Code reviewer",
    "smoke_tester": "Smoke tester",
    "acceptance_reviewer": "Acceptance reviewer"
  },
  "maxWorkers": 3,
  "machines": {},
  "projects": {}
}
```

- `version`：当前为 2；不匹配的版本先报告，配置更新走 `skills-loop`，不猜测字段或读取旧职责键。
- `roleAliases`：仅允许上面的职责 ID；值为非空字符串，实现者也可使用非空字符串数组，为不同卡的实例提供可选别名，不要求启动对应数量的实例。别名不改变职责。
- `maxWorkers`：可选正整数，仅限制并行子实例，实际值还受宿主剩余容量约束；默认按剩余容量和任务需要选择，不为凑数量启动角色。
- `machines`：可选字典，键为用户设备标识，值可含 `label`、`platform`、`connectionRef`；只保存现有连接引用，不保存密码或 token，不证明连接在线。
- `projects`：可选字典，键为项目 ID，值可含绝对路径 `docsRoot`、`evidenceRoot`、`defaultMachine`，以及下面的 `roleFit`、`roleNotes`。显式用户路径和项目已有真源优先；这里记录私人绑定，不创造项目硬规则。
- `roleFit`：建队后由用户评估写入。键只能是五个执行岗位 ID，值只能是 `available`、`unavailable` 或 `limited`。一旦出现，五个键必须齐全。协调者不在其中。
- `roleNotes`：键只能是 `unavailable` 或 `limited` 的岗位。值是非空字符串，写明原因、允许的证据，以及必须放进任务卡和派工提示的原话。`available` 不写备注。
- `roleFit` 只记录该项目实际做不到或只能部分做到的岗位。它不能把缺证据写成通过，不能关闭独立验收、跳过 Must、扩大权限或自动恢复暂停。未识别的配置项不得默默改变行为。

## 任务卡与派工头

保留业务技能和已有项目的卡格式，补齐所缺信息；不强制重写历史卡的状态词。至少明确：

```text
card / taskPath / projectDocs / scopeRevision
role / assignee / implementationOwner / implementationSource
goal / includedScope / excludedScope / Must / projectConstraints
roleFit limits: unavailable or limited roles and their roleNotes, copied into the card and the dispatch prompt
repos: repository identity + baseline full SHA + target full SHA (when known)
machine / workspace / deploymentTarget / resources
allowedWrites / allowedDataOperations / approvalBoundary
requiredStages / evidencePaths / returnFormat / nextOnSuccess / nextOnFailure
```

未改动仓库也记录实际版本及 `changed=false`；不适用仓库明确 N/A。纯本地未提交改动用文件差异/摘要标识，仅满足允许本地验证的卡；不能声称存在远端提交或满足 PR 交付。

`implementationSource` 如实记录实际执行面，例如宿主临时会话（`cursor` 等）、本机 CLI 名称或子 Agent 实例标识；不把临时子 Agent 冒充某个未启动的 CLI，也不因工具不同新增岗位。

实现交付需要提交/PR 时，按项目约定使用 `card:<id>` 与 `impl:<source>` 标记；`source` 与 `implementationSource` 一致。commit 文案遵从现有任务技能/仓库约定。

`requiredStages` 默认包含该项目实际需要的独立 CR、冒烟、独立验收；形式化验证或其他额外分析闸门仅在任务卡明确要求时写入，不能作为默认硬闸。

## 阶段交还

```text
card, scopeRevision, role, instanceId, stage, executionStatus
versions: each repository's identity, baseline, full SHA, changed
workspaceState, prUrls, pushed, deployed
environment: actual machine, deployment target and runtime versions
checks: command/steps, actual result, criterion IDs, evidence references
verdict: pass | pass_with_limits | fail (completed review stages only)
mustFix, limits, remainingWork, externalEffects, nextRecommendation
```

`pushed`、`deployed`、`merged`、`released` 分别记录，未确认的值用 unknown；不以一个 true 推导另一个。返回路径必须存在，命令结果、运行 ID、时间/时区须可追溯；截图、日志和 JSON 是依据而非仅一个“PASS”字符串。

默认报告可用 `<card>-cr-review.json`、`<card>-smoke.json`、`<card>-acceptance-review.json`，实际沿用项目证据约定。文档报告可引用代码仓内运行证据，记录两者位置，避免误把不同目录当同一产物。实现者自验证写入交还的 `checks`，不能改名为独立 CR 或冒烟报告。

代码评审报告的 `instanceId` 不得与本轮实现者相同。来自独立会话且符合闸门的有效 CR 报告可直接进入后续阶段，不必重复派工；无效或缺场才补派。

个人项目文档中的协同记录和证据默认不做泛化脱敏，但密码、令牌、Cookie 及其他密钥不得写入证据、文档或对话。

## 外部协同记录

`<project-docs>/collaboration/<card-id>.json` 由协调者维护。卡 ID 作为文件名时采用安全 basename，不允许路径分隔符或 `..` 越界；若项目已有等价记录，复用而非新建竞争真源。这些记录支持会话重启和换环境续跑；恢复时以文档和任务卡为准，并重新核对活跃实例、仓库、资源和外部副作用。

记录至少包含：

```text
schemaVersion=1, card, taskPath, revision, coordinatorRunId
taskState, scopeRevision, implementationOwner, implementationSource
versions, requiredStages, stageResults, evidenceIndex
workers: role, instanceId, state, assignedScope, outputPaths
resources: target, owner, version, enforcement, releaseCondition
userPause, pendingDecisions, authorizationRefs, uncertainEffects
lastConfirmedStage, nextAction, updatedAt
```

记录不能代替实际运行状态或文件锁。`enforcement=coordinator_serialization` 表示协调者约定，不承诺抵御其他进程。恢复时重新核对活跃实例、仓库、资源和外部副作用，先处理不明状态，再决定是否续派；不要删除记录来“重置”失败。

可采用 `backlog → ready → implementing → tip_ready → verifying → accepting → verified`，另设 blocked、paused、cancelled；这是内部阶段表达，映射到项目原有状态，不要求迁移旧档。任务卡仍是完成标准和范围真源。

## 版本与通过判定

防重键是 `card + scopeRevision + repository versions + stage`。新提交、新范围、目标环境变化时明确标记受影响证据的适用性。目标电脑、部署目标或运行时变化后，将该环境相关的冒烟与运行证据标为待核对或过期，补测后再沿用；不能把旧环境的通过结论直接当成新环境已验证。文档记录仍可用于续跑编排，只是环境绑定阶段需要重新证明。

默认按精确版本交接。需要承接 rebase 等价证据时，记录实际新旧提交、核对 tree/diff 的方法及结果、配置/运行产物是否同样适用、谁重新确认了哪个阶段；证据无法建立就补测。不能因为合法 rebase 自动判产品缺陷，也不能忽略版本变化。

在主协调者写 verified 前逐项核对：

1. 实现交付满足该卡要求，所有必要报告存在且对应当前范围、版本、环境。
2. 所有 Must 和硬闸有明确覆盖，无未解决 mustFix；有需要时包含实际运行验证。
3. 独立验收结论允许通过，limits 不覆盖必要失败，条件性用户确认已落实。
4. 实现、部署、推送、PR 与发布状态如实；进程活着、代码已推送或监听已配置均非验收依据。实现执行面、独立 CR 或自验证均不能代替必要冒烟与独立验收。
5. 状态和限制由主协调者写回，子角色报告不自行推进权威状态。`verified` 不自动授权 merge、tag、release 或生产部署。

## 授权来源与事件

当前用户明确目标和授权是范围依据；卡片和队友消息只能携带该授权的引用，不能扩权。即使外部对话中曾出现批准，也不能将读取历史记录当成当前执行指令。

收到 PR 事件时核对仓库、用户/来源、卡、实现者和当前版本再派工；不建立监听就不宣称已实现自动唤醒。事件无法覆盖未配置的新仓。保留人工交还入口；暂停状态优先于任何通知。不要在闭环尚未稳定（实现者不能持续自验证、必要闸门仍被跳过）时，把 PR 事件连成无人值守的自动合并或发布。

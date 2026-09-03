# Media Loop 运行与自我改进契约

本契约把一次运营运行拆成可恢复的阶段，并把“失败”“跳过”“待确认”与“数据不足”分开。它是 `media-loop`、`media-core`、`media-ops` 和平台技能共享的运行协议。

## 1. 阶段与检查点

每次运行使用一个稳定的 `runId`，每个内容目标使用 `contentId + targetId` 幂等键，每个来源生产使用 `requestId + pipelineRef` 幂等键。阶段只能向前推进，或进入明确的暂停/待确认状态：

```text
preflight
→ candidate_selected
→ source_verified
→ asset_verified
→ target_adapted
→ ready_admitted
→ draft_prepared
→ submitted
→ published_pending_review | published | publish_failed | publish_unconfirmed
→ recorded
→ cleaned
```

每次外部副作用前后都写检查点，至少包含：

```text
runId, idempotencyKey, phase, phaseVersion,
contentRef, targetRef, artifactRefs[],
sideEffects[], gateResults[],
lastObservedAt, nextAction, retryClass, retryCount
```

恢复时先读取最后一个检查点和副作用记录，再从最小受影响阶段继续；不得从来源发现阶段重新开始，也不得根据“没有看到成功提示”推断没有副作用。

## 2. 结果分类

| 结果 | 含义 | 默认动作 |
|---|---|---|
| `success` | 阶段目标已明确完成 | 推进下一阶段 |
| `blocked` | 硬门禁失败，当前不能继续 | 保留资产，写明修复条件 |
| `skipped` | 当前运行不需要或不适合处理 | 写明原因和下次触发条件 |
| `retryable_failure` | 可判断为暂时性技术失败 | 仅执行有界恢复 |
| `unknown` | 可能已经产生外部副作用 | 只读核验，不重试写操作 |
| `data_insufficient` | 数据不足以作判断 | 保持现状，补采数据 |

`skipped` 必须包含 `reasonCode`、`nextCheckAt` 或 `resumeCondition`；不能只写“跳过”。`unknown`、`published_pending_review` 和账号健康暂停不能通过补货、换候选或人工覆盖绕过。

## 3. 有界恢复

每个阶段只允许最小范围恢复，不允许整条链路循环：

- 页面或连接短暂失败：重新读取状态一次，必要时重新打开本轮创建的页面一次；
- 上传/媒体处理失败：重新验收同一已授权资产一次，不重新发现候选；
- 草稿字段异常：丢弃或修复当前草稿后重新读取，不连续局部追加；
- 发布结果不明确：只读核验时间线、详情或管理页，禁止再次点击发布；
- 记录写回失败：保留结果页和本地检查点，先恢复写回，不重复外部动作。

达到阶段恢复上限、发现账号不匹配、验证码/挑战、权限不足或副作用无法确认时，转为 `blocked` 或 `unknown`，并停止本次目标。恢复预算可以由平台技能细化，但不能取消未知状态和安全门禁。

## 4. 自我改进的证据门槛

`media-loop` 只产生三类反馈：

1. **运行修复**：修复失败原因，不改变内容策略；
2. **临时覆盖**：下一轮或限定窗口生效，带证据、预期信号和回滚条件；
3. **长期变更建议**：只有同账号、同平台、同格式的可比样本达到配置门槛，且单变量实验完成后才提出。

单条爆文、单次失败、搜索排序、平台总阅读量和模型猜测都不能直接触发长期配置变更。健康风险、数据质量问题和内容质量问题必须分别记录，不能把账号限流归因于文案，也不能把数据缺失归因于内容差。

每个实验至少记录：对照定义、唯一变量、样本门槛、主指标、成功阈值、停止条件、回滚值和结果。未达到样本门槛时结果只能是 `inconclusive`。

## 5. 性能原则

- 先做一次 `preflight`，缓存本轮不变的账号、权限、事实、版权、媒体和去重结果；最终发布前只重新核对受副作用影响的门禁。
- 使用适配积压指纹和 ready 库存指纹；只有当前仍有 eligible 可恢复适配积压、上次结果为 `adaptation_backlog_present` 且指纹未变化时才执行轻量 no-op。排除争议、审核中、未知、已完成、账号暂停和 disabled 目标后 ready 为零，必须进入 `ready_supply_starved`，不能由旧指纹压制补货。
- `media-loop` 只读取目标平台相关的指标和平台技能；不为一次 X 运行加载抖音、小红书的全部规则。
- 运行恢复优先检查本地检查点、队列和结果页；已明确完成的阶段不得重复执行。
- 同一运行最多沿一条阶段路径推进一次；不得形成 `ops → loop → core → ops` 的无界递归。

## 6. 最小运行报告

```text
runId, runType, accountRef, platform, window, dataQuality,
phase, outcome, reasonCode, idempotencyKey,
healthStatus, inventoryStatus, artifactRefs[],
nextAction, resumeCondition, strategyVersion,
experimentRefs[], writeBackStatus, cleanupStatus
```

报告必须能回答：本轮做到了哪一步、为什么没有继续、下次从哪里恢复、是否可能已经产生外部副作用，以及这次结果是否足以改变策略。

## 7. 共享契约与验收

本文件是 `media-loop`、`media-core` 和 `media-ops` 的共享运行结果契约。各技能只补充自身阶段规则；结果类型、最小报告字段、未知副作用和恢复语义以本文件为准，不复制另一套定义。

六个关键状态的固定样例见 [acceptance-scenarios.json](acceptance-scenarios.json)。修改运行结果契约后执行：

```powershell
python content/media/media-loop/scripts/validate_runtime_contract.py
```

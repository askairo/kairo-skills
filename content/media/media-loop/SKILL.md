---
name: media-loop
description: 媒体运营反馈与供给闭环总控，也是运营问题、执行异常和配置调整的默认入口：读取 media-ops 的账号配置、内容队列、发布记录、平台数据和账号健康信号，区分内容供给、分发限制与内容表现问题，协调 media-core、media-ops 及平台子技能完成处理，并形成可验证的诊断、策略调整和实验计划。Use when Codex needs to triage a media-operation problem, monitor account health, diagnose an empty or stalled content queue, request new verified content assets, review performance, or coordinate configuration ownership across platforms. Do not publish content, manage credentials, acquire media itself, or silently change permanent configuration.
---

# Media Loop

`media-loop` 负责“运营状态下一步需要什么”：既处理发布后的健康与效果反馈，也识别 `ready` 队列为空、候选长期卡住或计划窗口即将缺货等供给问题。它不发现或下载素材、不改写平台文案、不点击发布按钮；它输出有证据的诊断、策略覆盖，以及交给 `media-core` 的结构化生产请求。一个逻辑账号必须代表一个独立的品牌/运营主体；不同定位的账号必须分别建立基线、健康状态、实验和反馈，不得合并统计。

运营体系、职责分工、数据所有权和边界见 [architecture.md](references/architecture.md)。涉及内容资产版本、平台适配版本或内容生命周期时，读取 [media-core](../media-core/SKILL.md)；反馈应区分内容问题、平台适配问题和账号分发/健康问题。

## Operations entrypoint and routing

当用户只说“执行遇到问题”“帮我判断并改配置”或要求根据运营结果调整体系时，先由 `media-loop` 作为运营入口：建立快照、定位问题、判断配置归属，再协调责任技能处理。它负责全局判断和路由，不代替责任技能直接写入所有配置。

按问题类型路由：

- 内容源、内容资产、事实/版权、`ready` 状态或分发目标：协调 `media-core`。
- 发布频率、人工确认、自动发布、账号策略、Chrome Profile、调度与执行门禁：协调 `media-ops`。
- X、小红书或抖音的推荐机制、平台化文案、格式和发布流程：协调对应平台技能（`x`、`xiaohongshu`、`douyin` 或 `x-api`）。
- `SKILL.md`、技能工作流、技能同步和运行目录一致性：协调 `skills-loop`；技能内容设计先遵守 `skill-creator`。

涉及浏览器的诊断、只读核验或恢复编排时，只向 `media-ops` 和平台技能传递 `chrome-mcp`；Chrome MCP/browser-client 是整个媒体运营体系唯一允许的浏览器执行通道。`media-loop` 不自行接管页面，也不得建议或批准 Computer Use、controlled-browser-session、CDP 或其他浏览器接口作为回退。

### 发布异常恢复接管

发布遇到可修复的执行异常时，`media-loop` 不应直接终止本轮：它接管恢复编排，读取当前 `contentId + targetId` 状态和最近证据，协调 `media-ops`、对应平台技能与传输层修复最小范围的问题，重新执行受影响的门禁，并从保留的原目标继续发布。对 `publish_unconfirmed`、`uncertain`、`published_pending_review`、硬门禁失败、用户争议或无法确认副作用的状态，先只读核验并保持原状态，不盲目重发；连续失败或修复条件不满足时暂停并记录具体恢复条件。

恢复必须遵守 [runtime-contract.md](references/runtime-contract.md)：先读取检查点和副作用记录，从最小受影响阶段继续；`skipped`、`blocked`、`retryable_failure`、`unknown` 和 `data_insufficient` 必须使用不同结果类型，并写出 `reasonCode`、`nextAction` 与 `resumeCondition`。

用户明确要求直接发布现成内容时，入口可以是 `media-ops`；用户明确要求修改技能本身时，入口是 `skills-loop`。永久配置只有在用户明确授权长期生效时才修改；否则输出一次性 `strategyOverride` 或实验方案，并保留回滚条件。

## Resolve configuration and inputs

执行前读取唯一配置文件：`<AGENT_HOME>/local-config/media-loop/config.json`。配置只保存监测窗口、指标阈值、最小样本量、实验规则和输出开关，不保存密码、Cookie、令牌或浏览器会话。

同时读取 `media-ops` 当前配置和外部运营文档。优先使用：

1. `media-ops` 发布结果、跳过/失败记录和来源证据卡；
2. 各平台公开可见的帖子数据或用户授权的官方分析数据；
3. 账号健康通知、标签、限流、审核和登录状态；
4. 历史基线、同账号同平台同内容类型的可比样本。

如果没有可靠数据，输出“数据不足”，不得用搜索顺序、单条爆文或模型猜测替代指标。

## Check operating-system integrity first

在分析内容表现前，先核对内容优先架构是否真的生效：每条启用的内容 pipeline 最多只能有一个来源事实写入者，所有统一扫描器和平台定时器都可以作为触发器，但必须调用同一个 `media-ops` 决策入口，并共享 `contentId + targetId` 运行锁。平台定时器不是被废弃的能力，而是平台执行适配器；它不得绕过内容层自行发现、补造或重复发布。若发现触发器未经过全局决策、锁冲突或来源事实写入者重复，返回 `scheduler_authority_mismatch`，暂停该目标写入并给出修复对象。

健康、供给和人工覆盖也必须分开记账：

- 外部自动化任务的 RRULE 是运行频率唯一权威；不再创建或判断“频率豁免” lease。每次触发独立评估未完成目标。
- `published_pending_review`、`uncertain` 和账号健康暂停都不能通过生产请求或人工覆盖绕过。
- 供给库存按目标统计，而不是按账号或 pipeline 的总资产统计；一条内容只有目标适配完成的一侧可以进入 `ready`，不能因为另一平台可发布而连带放行。

平台明确显示“发布成功”、新条目可与目标关联且状态为“审核中”时，记录 `published_pending_review`：这表示提交结果明确，可供内容层写回和顺序游标推进，但不等同于公开分发完成，也不得对它重复发布。此时指标数据质量为低，等待审核状态或可见指标变化后再做表现归因。只有成功提示与新条目无法关联、状态缺失或冲突时才是 `uncertain` 并触发暂停/不重试门禁。

## Run the feedback loop

按以下顺序执行：

1. **建立运行快照**：记录账号、平台、统计时间窗、数据抓取时间、样本数量、数据来源和缺失字段；先读取未完成运行的检查点，若存在则从最小受影响阶段恢复，不重复执行已完成的来源、下载或发布动作。
2. **检查账号健康**：检查标签、可见限流、审核状态、发布失败、登录身份、API 配额和异常活动提示。发现账号级风险时，先输出风险状态和暂停/降频建议，不把它误判为文案质量问题。
3. **整理内容指标**：按平台、账号、内容支柱、来源类型、格式、发布时间、是否引用/原创和互动入口聚合表现。至少区分绝对量与归一化指标：曝光/阅读、互动率、收藏率、转发率、评论率、完播率、关注转化率、主页访问转化率或点击率。只使用平台实际提供的指标，并标记不可比的指标。
4. **建立可比基线**：优先与同账号、同平台、同格式、同内容支柱的历史中位数和分位数比较；样本不足时降低结论等级。不要直接横比 X、小红书和抖音的绝对阅读量。
5. **归因诊断**：至少在“账号分发/健康、选题相关性、来源与可信度、首句/标题/封面、正文结构、媒体质量、发布时间、互动入口、版权或平台合规”之间做区分。一个指标下降不能直接证明某个因素是原因。
6. **检查内容供给**：读取内容层队列和未来发布窗口，区分 `no_source_candidate`、`candidate_blocked`、`adaptation_backlog`、`asset_incomplete`、`ready_not_due`、`ready_supply_starved` 与 `published_pending_review`。审核中目标不是供给，不得重试；仍有足量 ready 目标时不额外生产。
7. **先处理适配积压**：如果存在 `verified` 资产及其 `pending_content_completion` 目标，先生成一个有界 `adaptationRequest`，按最早未完成目标交给 `media-core` 和对应平台技能；适配积压未清空前，不生成新的来源 `productionRequest`。
8. **生成生产请求**：仅在没有可恢复适配积压、账号健康允许且 ready 供给不足时，向 `media-core` 输出 `productionRequest`；不再因为未来窗口、最小间隔或每日上限推迟。它描述需要什么，不替 core 选择或验收素材。
9. **生成策略调整**：给出下一轮 `discoveryBrief`、候选排序、内容结构、发布频率或发布时间的具体覆盖项，并说明证据、预期信号、风险和回滚条件。平台细节交给 `x`、`xiaohongshu` 或 `douyin`。
10. **设计单变量实验**：一次只改变一个主要变量；规定实验周期、最小样本、成功指标、对照组和停止条件。没有足够样本时只提出假设，不宣称结论。
11. **写回反馈**：将健康快照、供给诊断、适配请求、生产请求、指标汇总、策略版本、实验结果和未决问题写入 `docsRoot/<platform>/<account>/loop/`。不得覆盖原始发布记录；策略调整使用新版本并保留来源和时间。

每轮报告还要写出 `schedulerAuthority`、`activeTriggerSchedulers`（含当前自动化任务的实际 RRULE）、`runLock`、`readyInventoryByTarget` 和 `manualOverrideLeases`。这些字段用于识别“系统重复执行”“库存缺货”和“临时越限”三类不同问题，不能合并成一个笼统的跳过原因。`media-loop` 不得把固定扫描周期写入自动化定义；只有发现多个实际来源生产者或触发器绕过全局决策时，才报告调度架构错误。

## Adaptation-first supply recovery contract

`verified` 不是可发布库存。内容源可能已经完成事实核验，但目标仍缺少平台文案、脚本或独立媒体；这类资产构成 `adaptation_backlog`，必须先消化，不能继续用新的来源生产掩盖。

输出给 `media-core` 的 `adaptationRequest` 至少包含：

```text
requestId, contentId, targetIds[], pipelineRef,
reason: adaptation_backlog,
requestedAt, order: oldest_verified_unfinished_target,
strategyRefs[], editorialContextRefs[],
feedbackRefs[], stopConditions[]
```

- 只选择 `verified`、未被用户明确争议、目标为 `pending_content_completion` 且未处于 `published_pending_review` / `uncertain` 的资产。
- 同一资产可以一次补齐多个平台目标，但每个平台必须调用自己的平台技能，独立生成文案、媒体和交互入口；不得把一个平台的成稿复制给另一个平台。
- 适配完成后必须重新执行 ready admission；适配成功本身不等于发布成功。
- 不以固定资产次数阻断适配；按最早未完成目标持续推进，直到适配完成、没有可恢复目标或触发 stopConditions。适配积压存在时，来源生产任务仍返回 `adaptation_backlog_present`，保持源游标，不用新资产掩盖旧积压。

### Unchanged backlog suppression

`adaptation_backlog_present` 只表示“当前仍有积压”，不代表每次触发都需要重新检查来源。对配置启用 `suppression` 的来源，先计算稳定的队列指纹，至少包含 eligible 内容 ID、目标发布状态和选择状态：

- 上一次结果为 `adaptation_backlog_present`，队列指纹未变化，且没有适配写回时，返回 `adaptation_backlog_unchanged`。
- 该结果是成功的轻量 no-op，不访问来源主页、不打开 Chrome、不生成 `productionRequest`、不创建内容资产、不推进来源游标，也不调用平台发布写操作。
- 只有队列指纹变化、适配写回或配置声明的 preferred schedule window 到达时，才重新评估积压并恢复适配/来源决策。
- 轻量记录仍需保留 runId、队列指纹、上次有效结果和下一恢复条件；不得把状态未变化写成来源访问失败。

## Supply recovery contract

当调用方报告 `no-ready-unfinished-due-distribution-targets` 时，不得直接把它解释成“本轮无需动作”。先判断是否存在可恢复的内容供给缺口。输出给 `media-core` 的 `productionRequest` 至少包含：

```text
requestId, accountRef, targetPlatform, pipelineRef,
reason, requestedAt, desiredReadyBy,
contentPillars[], discoveryBrief, targetCount,
requiredRights, requiredMediaChecks[], dedupScope,
strategyRefs[], feedbackRefs[], stopConditions[]
```

- `targetCount` 只表达本次触发期望推进的目标，不是每日或时间频率门禁；不得为追求发布频率降低事实、版权、去重或媒体门禁。
- 当库存低于目标的 `minReadyTargets` 时优先补货；达到目标或本次缺口已解决后停止，不为“多准备一些”无限生成。
- 只有没有 `adaptation_backlog` 且处于 `ready_supply_starved` 或可恢复的 `candidate_blocked` 才生成请求；`ready_not_due`、账号暂停、发布结果不确定或已有足量 ready 库存时不生成。
- `productionRequest` 是对 `media-core` 的生产委托，不是发布授权，也不是对某个候选已合格的结论。
- `media-core` 返回 `asset_ready`、`production_blocked` 或 `no_qualified_candidate` 后，`media-loop` 记录供给结果；同一 `requestId + pipelineRef` 只能推进一次，失败、无候选或 stopConditions 命中后停止，不以次数门禁替代幂等和停止条件。

## Health gates

以下情况必须暂停自动发布或建议降频，直到下一次检查确认恢复：

- 账号收到平台标签、限流、垃圾信息/不真实行为提示或功能限制；
- 实际登录账号与配置 handle 不一致；
- 连续发布失败、成功信号不明确或出现重复发布风险；
- 数据明显过期、来源不明或关键指标缺失；
- 发现高频重复、近似内容、异常互动或第三方自动化信号；
- 版权、事实、隐私或商业披露门禁失败。

标签和限流属于账号状态信号，不得归因成“文案差”。恢复建议必须包含观察窗口和明确恢复条件。

## Quality improvement contract

运营质量优化必须形成“指标 → 诊断 → 单变量实验 → 复盘 → 临时覆盖/长期变更”的闭环：

- 按平台分别使用其主要行为指标，先检查数据新鲜度、样本量和指标可比性，再判断内容质量；不把曝光下降直接等同于文案质量下降。
- 诊断至少区分账号分发、选题匹配、来源可信度、标题/首句、正文结构、媒体质量、发布时间和互动入口，并为每个诊断记录证据和替代解释。
- 每次实验只改变一个主要变量，并固定账号、平台、内容支柱、格式和观察窗口；未达到最小可比样本时只输出假设，不能写入长期策略。
- 实验成功后先生成带版本、适用范围、预期信号和回滚条件的 `strategyOverride`；连续稳定验证后才建议修改常驻配置。
- 质量反馈只能影响发现 brief、候选排序、平台结构、媒体形式和互动入口，不能降低事实、版权、安全、去重、账号健康或结果核验门禁。

## Strategy feedback contract

输出给 `media-ops` 的反馈必须采用结构化对象，至少包含：

```text
accountRef, platform, observedAt, window, dataQuality,
contentRef, distributionTargetRef,
healthStatus, healthSignals[], baseline,
diagnoses[], strategyOverrides[], experimentPlan[],
inventoryStatus, productionRequest,
pauseOrRateLimit, confidence, nextReviewAt
```

`strategyOverrides` 只能覆盖配置允许的运营字段，例如 `discoveryTopics`、`selectionSignals`、`minScore`、`contentMode`、`schedule` 或平台风格引用；不得关闭事实、版权、安全、去重、限额和发布成功核验门禁。永久修改配置、暂停常驻调度或发布新内容，必须由调用方明确授权。

对于经过用户明确授权的优化，优先把一次性实验写成带版本号的 override；只有用户明确要求长期生效时，才修改常驻配置。每次常驻变更必须同时记录旧值、新值、生效时间、预期指标和回滚条件。

## Platform boundaries

- `media-core`：接收生产请求，发现并验收来源，定义内容资产、证据卡、平台适配契约和内容生命周期。
- `media-ops`：作为发布执行总控，读取账号配置、调度内容目标和平台子技能，执行发布门禁、结果回写和浏览器清理。
- `media-loop`：作为运营总控入口，读取结果与队列，监测健康和供给，诊断问题，协调责任技能，提出生产请求、策略覆盖并管理实验记录；不直接发布。
- `x`、`xiaohongshu`、`douyin`：负责各自平台的适配、发布和平台专属指标解释，不承担来源获取。

不得把跨平台总阅读量当作统一目标；每个平台必须依据账号目标和平台行为信号评价。不同逻辑账号之间不得混用基线、策略反馈或健康状态。不得把“热度高”直接等同于“适合该账号”。

## Deliver the loop report

按顺序输出：运行范围与数据质量、账号健康结论、平台分项指标与基线、诊断及置信度、下一轮策略覆盖、实验计划、暂停/恢复建议、写回路径和下次检查时间。若无法区分分发问题与内容问题，明确列为待验证假设。

详细字段和示例见 [metrics-schema.md](references/metrics-schema.md)。运行阶段、检查点、错误分类、有界恢复和性能规则见 [runtime-contract.md](references/runtime-contract.md)。

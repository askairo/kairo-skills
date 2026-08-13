---
name: media-loop
description: 媒体运营反馈与供给闭环总控：读取 media-ops 的账号配置、内容队列、发布记录、平台数据和账号健康信号，区分内容供给、分发限制与内容表现问题，形成可验证的诊断、生产请求、策略调整和实验计划，并反馈给 media-core、media-ops 及平台子技能。Use when Codex needs to monitor account health, diagnose an empty or stalled content queue, request new verified content assets, review performance, or run a feedback loop across configured platforms. Do not publish content, manage credentials, acquire media itself, or silently change permanent configuration.
---

# Media Loop

`media-loop` 负责“运营状态下一步需要什么”：既处理发布后的健康与效果反馈，也识别 `ready` 队列为空、候选长期卡住或计划窗口即将缺货等供给问题。它不发现或下载素材、不改写平台文案、不点击发布按钮；它输出有证据的诊断、策略覆盖，以及交给 `media-core` 的结构化生产请求。一个逻辑账号必须代表一个独立的品牌/运营主体；不同定位的账号必须分别建立基线、健康状态、实验和反馈，不得合并统计。

涉及内容资产版本、平台适配版本或内容生命周期时，读取 [media-core](../media-core/SKILL.md)；反馈应区分内容问题、平台适配问题和账号分发/健康问题。

## Resolve configuration and inputs

执行前读取唯一配置文件：`<AGENT_HOME>/local-config/media-loop/config.json`。配置只保存监测窗口、指标阈值、最小样本量、实验规则和输出开关，不保存密码、Cookie、令牌或浏览器会话。

同时读取 `media-ops` 当前配置和外部运营文档。优先使用：

1. `media-ops` 发布结果、跳过/失败记录和来源证据卡；
2. 各平台公开可见的帖子数据或用户授权的官方分析数据；
3. 账号健康通知、标签、限流、审核和登录状态；
4. 历史基线、同账号同平台同内容类型的可比样本。

如果没有可靠数据，输出“数据不足”，不得用搜索顺序、单条爆文或模型猜测替代指标。

## Check operating-system integrity first

在分析内容表现前，先核对内容优先架构是否真的生效：每条启用的内容 pipeline 最多只能有一个来源生产调度器，每个 Agent 最多只能有一个统一分发调度器；旧的平台专属发布定时器必须处于停用状态。若发现来源调度器、统一分发器和旧平台定时器同时运行，返回 `scheduler_authority_mismatch`，暂停平台写入并给出修复对象，不把重复运行造成的密度问题归因于文案。

健康、供给和人工覆盖也必须分开记账：

- 用户对单条内容的频率豁免是一次性的 `targetId` 级 lease，不改变常驻策略、每日上限或下一轮资格。
- `published_pending_review`、`uncertain` 和账号健康暂停都不能通过生产请求或人工覆盖绕过。
- 供给库存按目标统计，而不是按账号或 pipeline 的总资产统计；一条内容只有目标适配完成的一侧可以进入 `ready`，不能因为另一平台可发布而连带放行。

平台明确显示“发布成功”、新条目可与目标关联且状态为“审核中”时，记录 `published_pending_review`：这表示提交结果明确，可供内容层写回和顺序游标推进，但不等同于公开分发完成，也不得对它重复发布。此时指标数据质量为低，等待审核状态或可见指标变化后再做表现归因。只有成功提示与新条目无法关联、状态缺失或冲突时才是 `uncertain` 并触发暂停/不重试门禁。

## Run the feedback loop

按以下顺序执行：

1. **建立运行快照**：记录账号、平台、统计时间窗、数据抓取时间、样本数量、数据来源和缺失字段。
2. **检查账号健康**：检查标签、可见限流、审核状态、发布失败、登录身份、API 配额和异常活动提示。发现账号级风险时，先输出风险状态和暂停/降频建议，不把它误判为文案质量问题。
3. **整理内容指标**：按平台、账号、内容支柱、来源类型、格式、发布时间、是否引用/原创和互动入口聚合表现。至少区分绝对量与归一化指标：曝光/阅读、互动率、收藏率、转发率、评论率、完播率、关注转化率、主页访问转化率或点击率。只使用平台实际提供的指标，并标记不可比的指标。
4. **建立可比基线**：优先与同账号、同平台、同格式、同内容支柱的历史中位数和分位数比较；样本不足时降低结论等级。不要直接横比 X、小红书和抖音的绝对阅读量。
5. **归因诊断**：至少在“账号分发/健康、选题相关性、来源与可信度、首句/标题/封面、正文结构、媒体质量、发布时间、互动入口、版权或平台合规”之间做区分。一个指标下降不能直接证明某个因素是原因。
6. **检查内容供给**：读取内容层队列和未来发布窗口，区分 `no_source_candidate`、`candidate_blocked`、`asset_incomplete`、`ready_not_due`、`ready_supply_starved` 与 `published_pending_review`。审核中目标不是供给，不得重试；仍有足量 ready 目标时不额外生产。
7. **生成生产请求**：仅在账号健康允许、策略存在未来窗口且 ready 供给不足时，向 `media-core` 输出一个有界 `productionRequest`；它描述需要什么，不替 core 选择或验收素材。
8. **生成策略调整**：给出下一轮 `discoveryBrief`、候选排序、内容结构、发布频率或发布时间的具体覆盖项，并说明证据、预期信号、风险和回滚条件。平台细节交给 `x`、`xiaohongshu` 或 `douyin`。
9. **设计单变量实验**：一次只改变一个主要变量；规定实验周期、最小样本、成功指标、对照组和停止条件。没有足够样本时只提出假设，不宣称结论。
10. **写回反馈**：将健康快照、供给诊断、生产请求、指标汇总、策略版本、实验结果和未决问题写入 `docsRoot/<platform>/<account>/loop/`。不得覆盖原始发布记录；策略调整使用新版本并保留来源和时间。

每轮报告还要写出 `schedulerAuthority`、`activeLegacySchedulers`、`readyInventoryByTarget` 和 `manualOverrideLeases`。这些字段用于识别“系统重复执行”“库存缺货”和“临时越限”三类不同问题，不能合并成一个笼统的跳过原因。

## Supply recovery contract

当调用方报告 `no-ready-unfinished-due-distribution-targets` 时，不得直接把它解释成“本轮无需动作”。先判断是否存在可恢复的内容供给缺口。输出给 `media-core` 的 `productionRequest` 至少包含：

```text
requestId, accountRef, targetPlatform, pipelineRef,
reason, requestedAt, desiredReadyBy,
contentPillars[], discoveryBrief, targetCount,
requiredRights, requiredMediaChecks[], dedupScope,
strategyRefs[], feedbackRefs[], stopConditions[]
```

- 单次执行默认 `targetCount: 1`；不得为追求发布频率要求降低事实、版权、去重或媒体门禁。
- 当库存低于目标的 `minReadyTargets` 时才允许补货；达到目标后停止生产，不为“多准备一些”无限生成。
- 只有 `ready_supply_starved` 或可恢复的 `candidate_blocked` 才生成请求；`ready_not_due`、账号暂停、发布结果不确定或已有足量 ready 库存时不生成。
- `productionRequest` 是对 `media-core` 的生产委托，不是发布授权，也不是对某个候选已合格的结论。
- `media-core` 返回 `asset_ready`、`production_blocked` 或 `no_qualified_candidate` 后，`media-loop` 记录供给结果；不得在同一轮对同一 pipeline 无限循环请求。

## Health gates

以下情况必须暂停自动发布或建议降频，直到下一次检查确认恢复：

- 账号收到平台标签、限流、垃圾信息/不真实行为提示或功能限制；
- 实际登录账号与配置 handle 不一致；
- 连续发布失败、成功信号不明确或出现重复发布风险；
- 数据明显过期、来源不明或关键指标缺失；
- 发现高频重复、近似内容、异常互动或第三方自动化信号；
- 版权、事实、隐私或商业披露门禁失败。

标签和限流属于账号状态信号，不得归因成“文案差”。恢复建议必须包含观察窗口和明确恢复条件。

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
- `media-ops`：读取账号配置、调度平台子技能和执行发布门禁。
- `media-loop`：读取结果与队列，监测健康和供给，提出生产请求、策略覆盖并管理实验记录。
- `x`、`xiaohongshu`、`douyin`：负责各自平台的适配、发布和平台专属指标解释，不承担来源获取。

不得把跨平台总阅读量当作统一目标；每个平台必须依据账号目标和平台行为信号评价。不同逻辑账号之间不得混用基线、策略反馈或健康状态。不得把“热度高”直接等同于“适合该账号”。

## Deliver the loop report

按顺序输出：运行范围与数据质量、账号健康结论、平台分项指标与基线、诊断及置信度、下一轮策略覆盖、实验计划、暂停/恢复建议、写回路径和下次检查时间。若无法区分分发问题与内容问题，明确列为待验证假设。

详细字段和示例见 [metrics-schema.md](references/metrics-schema.md)。

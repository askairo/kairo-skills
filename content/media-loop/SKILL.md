---
name: media-loop
description: 媒体运营反馈闭环总控：读取 media-ops 的账号配置、发布记录、平台数据和账号健康信号，监测跨平台账号状态与内容效果，区分分发限制和内容问题，形成可验证的诊断、策略调整与实验计划，并把结果反馈给 media-ops 及各平台子技能。Use when Codex needs to monitor media account health, review content performance, diagnose operational problems, adjust discovery or publishing strategy, or run a feedback loop across configured X, Xiaohongshu, and Douyin accounts. Do not publish content, manage credentials, or silently change permanent configuration.
---

# Media Loop

`media-loop` 负责“发布之后发生什么”，不负责发现素材、改写文案或点击发布按钮。它读取 `media-ops` 的运行上下文和平台结果，输出有证据的诊断与下一轮策略覆盖。一个逻辑账号必须代表一个独立的品牌/运营主体；不同定位的账号必须分别建立基线、健康状态、实验和反馈，不得合并统计。

## Resolve configuration and inputs

执行前读取唯一配置文件：`<AGENT_HOME>/local-config/media-loop/config.json`。配置只保存监测窗口、指标阈值、最小样本量、实验规则和输出开关，不保存密码、Cookie、令牌或浏览器会话。

同时读取 `media-ops` 当前配置和外部运营文档。优先使用：

1. `media-ops` 发布结果、跳过/失败记录和来源证据卡；
2. 各平台公开可见的帖子数据或用户授权的官方分析数据；
3. 账号健康通知、标签、限流、审核和登录状态；
4. 历史基线、同账号同平台同内容类型的可比样本。

如果没有可靠数据，输出“数据不足”，不得用搜索顺序、单条爆文或模型猜测替代指标。

## Run the feedback loop

按以下顺序执行：

1. **建立运行快照**：记录账号、平台、统计时间窗、数据抓取时间、样本数量、数据来源和缺失字段。
2. **检查账号健康**：检查标签、可见限流、审核状态、发布失败、登录身份、API 配额和异常活动提示。发现账号级风险时，先输出风险状态和暂停/降频建议，不把它误判为文案质量问题。
3. **整理内容指标**：按平台、账号、内容支柱、来源类型、格式、发布时间、是否引用/原创和互动入口聚合表现。至少区分绝对量与归一化指标：曝光/阅读、互动率、收藏率、转发率、评论率、完播率、关注转化率、主页访问转化率或点击率。只使用平台实际提供的指标，并标记不可比的指标。
4. **建立可比基线**：优先与同账号、同平台、同格式、同内容支柱的历史中位数和分位数比较；样本不足时降低结论等级。不要直接横比 X、小红书和抖音的绝对阅读量。
5. **归因诊断**：至少在“账号分发/健康、选题相关性、来源与可信度、首句/标题/封面、正文结构、媒体质量、发布时间、互动入口、版权或平台合规”之间做区分。一个指标下降不能直接证明某个因素是原因。
6. **生成策略调整**：给出下一轮 `discoveryBrief`、候选排序、内容结构、发布频率或发布时间的具体覆盖项，并说明证据、预期信号、风险和回滚条件。平台细节交给 `media-x`、`media-xiaohongshu` 或 `media-douyin`。
7. **设计单变量实验**：一次只改变一个主要变量；规定实验周期、最小样本、成功指标、对照组和停止条件。没有足够样本时只提出假设，不宣称结论。
8. **写回反馈**：将健康快照、指标汇总、诊断、策略版本、实验结果和未决问题写入 `docsRoot/<platform>/<account>/loop/`。不得覆盖原始发布记录；策略调整使用新版本并保留来源和时间。

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
healthStatus, healthSignals[], baseline,
diagnoses[], strategyOverrides[], experimentPlan[],
pauseOrRateLimit, confidence, nextReviewAt
```

`strategyOverrides` 只能覆盖配置允许的运营字段，例如 `discoveryTopics`、`selectionSignals`、`minScore`、`contentMode`、`schedule` 或平台风格引用；不得关闭事实、版权、安全、去重、限额和发布成功核验门禁。永久修改配置、暂停常驻调度或发布新内容，必须由调用方明确授权。

## Platform boundaries

- `media-ops`：读取账号配置、调度平台子技能和执行发布门禁。
- `media-loop`：读取结果、监测状态、分析效果、归因、提出策略覆盖和管理实验记录。
- `media-x`、`media-xiaohongshu`、`media-douyin`：负责各自平台的推荐机制、素材发现、内容制作、发布和平台专属指标解释。

不得把跨平台总阅读量当作统一目标；每个平台必须依据账号目标和平台行为信号评价。不同逻辑账号之间不得混用基线、策略反馈或健康状态。不得把“热度高”直接等同于“适合该账号”。

## Deliver the loop report

按顺序输出：运行范围与数据质量、账号健康结论、平台分项指标与基线、诊断及置信度、下一轮策略覆盖、实验计划、暂停/恢复建议、写回路径和下次检查时间。若无法区分分发问题与内容问题，明确列为待验证假设。

详细字段和示例见 [metrics-schema.md](references/metrics-schema.md)。

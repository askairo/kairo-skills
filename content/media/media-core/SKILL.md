---
name: media-core
description: 媒体内容核心层：把来源证据、编辑判断、媒体资产、平台适配和分发目标组织成可复用的内容资产，并管理从候选、核验、改编到发布后反馈的生命周期。Use when Codex needs to design a content-first media workflow, normalize one source into reusable content, prepare multiple platform variants, or reconcile content and distribution state. Do not publish content, manage credentials, or replace platform-specific rules.
---

# Media Core

`media-core` 把“内容”作为跨平台运营的第一类对象。它维护一份可核验的内容事实和编辑主线，再为不同平台、账号和策略生成独立的分发目标；它不直接操作平台，也不把同一份原稿机械同步到所有渠道。

## Canonical content asset

每个内容资产至少包含以下对象；缺失会改变事实、版权或选材结论的字段必须先补齐：

```text
contentId
sourceEvidence[]       # 原始 URL、作者、时间、关键段落/时间戳、可见指标
factBoundary           # 已核验事实、作者原意、编辑推断、待核验内容
editorialThesis        # 这一内容只回答的一个核心问题
audiencePromise        # 读者/观众能获得什么
mediaAssets[]          # 图片、视频、音频、封面及其权限和归属
rightsStatus           # confirmed | pending | restricted | rejected
adaptationNotes        # 平台改编时必须保留、可以压缩或不得出现的内容
distributionTargets[]  # 平台、平台账号、风格、策略、计划时间
lifecycleState         # candidate | verified | adapted | ready | published | retired
feedbackRefs[]         # 发布记录、平台指标和 media-loop 反馈
```

来源证据、事实边界和版权状态属于内容资产的共同真相；平台版本可以改变语言、节奏、画面和互动入口，但不得改变已核验事实、人物原意、授权范围或核心编辑判断。

## Content-first workflow

1. **Ingest**：接收原始帖子、网页、视频、访谈或用户素材，记录来源和权限线索。
2. **Normalize**：拆分事实、原作者观点、编辑推断和待核验主张，聚合同一事件的重复来源。
3. **Define**：确定一个编辑主线、受众收益和内容支柱；不能用“热度高”替代账号相关性。
4. **Verify**：完成事实、来源、版权、隐私、重复和媒体可用性门禁，生成可追溯证据卡。
5. **Adapt**：按照每个分发目标调用对应平台技能，生成独立的标题、正文、脚本、画面、引用方式和互动入口。
6. **Distribute**：把已适配版本交给 `media-ops`，由它执行账号、Chrome Profile、频率、人工确认、发布和成功核验。
7. **Learn**：接收 `media-loop` 的内容表现反馈，区分内容问题、平台适配问题和账号分发/健康问题，再创建新版本或实验，不覆盖原始资产。

## Distribution target contract

每个目标至少明确：

```text
platform
platformAccountRef
browserProfileRef or apiContext
styleRef
strategyRef
format
adaptationBrief
publishState
```

同一内容可以有多个目标，例如 X 原生引用、小红书收藏型图文和抖音知识短视频；每个目标都必须经过目标平台技能的专属筛选与改编。平台账号不是内容资产的拥有者，内容资产也不能绕过账号健康和发布门禁。

## Boundaries

- `media-core`：定义内容资产、证据卡、适配契约、生命周期和内容层版本。
- `media-ops`：读取账号配置和内容资产，调度目标，执行 Profile 路由、发布门禁、外部记录回写和浏览器清理。
- `media-loop`：监测账号健康、内容指标和实验结果，提出有证据的策略覆盖。
- `platform/x`、`platform/x-api`、`platform/douyin`、`platform/xiaohongshu`：负责平台推荐机制、平台发现、平台化改编、平台发布和平台指标解释。

`media-core` 不读取密码、Cookie、令牌或浏览器会话，不直接点击发布按钮，不自行决定某个平台的算法权重，也不把跨平台绝对阅读量当作统一成功指标。

## Hard gates

- 事实边界不清、来源不可追溯、版权状态不明或媒体不可用时，内容资产不得进入 `ready`。
- 同一事件的转载、翻译和摘要不能被登记为多个独立原创资产。
- 平台版本必须保留必要的来源归属和披露；翻译或引用本身不构成原创增量。
- 发布结果不明确时保持 `publishState: uncertain`，不得推进生命周期或盲目重试。
- 任何策略优化都创建新版本，保留原始证据、旧文案、发布结果和回滚依据。

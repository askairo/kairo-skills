---
name: media-core
description: 媒体内容核心层：把来源证据、编辑判断、媒体资产、平台适配和分发目标组织成可复用的内容资产，并管理从候选、核验、改编到发布后反馈的生命周期。Use when Codex needs to design a content-first media workflow, normalize one source into reusable content, prepare multiple platform variants, or reconcile content and distribution state. Do not publish content, manage credentials, or replace platform-specific rules.
---

# Media Core

`media-core` 把“内容”作为跨平台运营的第一类对象。它维护一份可核验的内容事实和编辑主线，再为不同平台、账号和策略生成独立的分发目标；它不直接操作平台，也不把同一份原稿机械同步到所有渠道。

## External content records

内容源、内容资产和源流水线必须有独立的外部文档，不再寄存在某个平台账号的 `queue.md`、`runs/` 或 `published.md` 中。启动内容发现、内容资产生成或源流水线定时任务前，读取 Agent 本地配置：

```text
<AGENT_HOME>/local-config/media-core/config.json
```

配置只保存本机文档根目录、内容层子目录、内容源流水线和调度定义，不保存密码、Cookie、令牌或浏览器会话。`<docsRoot>/<contentRoot>` 下的结构由本技能固定：

```text
<docsRoot>/<contentRoot>/
  registry.md
  pipelines/<pipeline-id>/
    queue.md
    published.md
    runs/<run-id>.md
```

`registry.md` 登记内容源、内容流水线与目标映射；`queue.md` 登记候选和内容资产状态；`runs/` 记录每次发现、核验、生成和跳过；`published.md` 只记录内容资产及其分发目标的最终状态。平台目录中的文档继续保留平台适配、平台发布和平台指标历史，不再成为内容源的唯一事实来源。

本地配置中的每个 `sourcePipelines.<pipeline-id>` 至少声明 `sourceGroupRef`、`schedule`、`dispatchMode`、`targetAccounts` 和 `dedupKeys`。源定时任务默认使用 `dispatchMode: producer-only`：只发现、核验并登记可复用内容资产，不直接点击平台发布；后续由内容分发目标或 `media-ops` 执行发布。只有明确配置为内容分发任务时，才允许进入发布流程，并且仍需经过平台、账号、版权、频率和成功核验门禁。

内容源迁移时不删除平台历史文档，也不重复复制历史帖子；在内容流水线文档中登记来源映射和迁移起点，之后新增内容以 `contentId` 为唯一内容资产 ID，以 `contentId + targetId` 为分发幂等键。

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
styleRef
strategyRef
format
adaptationBrief
plannedAt or preferredWindow
publishState
```

`browserProfileRef` 或 `apiContext` 由执行时根据 `platformAccountRef` 解析，不要求在内容资产中重复保存登录环境。这样同一内容可以生成多个目标，例如 X 原生引用、小红书收藏型图文和抖音知识短视频；每个目标都必须经过目标平台技能的专属筛选与改编。平台账号不是内容资产的拥有者，内容资产也不能绕过账号健康和发布门禁。

## Content-driven dispatch

定时器的主对象是“到期的内容分发目标”，不是某个平台技能。`media-core` 负责表达内容何时准备好、哪些目标到期、目标之间是否有顺序依赖；平台的发布时间窗口、频率上限和健康限制仍作为目标级约束保留。

当一个内容的多个目标同时到期时，执行器可以按解析后的 `browserProfileRef` 分组，优先连续处理同一 Profile 下的不同平台目标，减少 Profile 切换。分组只优化执行顺序，不合并账号身份，也不合并发布结果：每个目标仍要单独核对平台账号、事实、版权、重复和成功状态。

同一 Chrome Profile 可以承载用户已确认登录的多个不同平台账号；同一平台的多个账号是否共用 Profile 仍遵守 `media-ops` 的隔离规则。Profile 是账号登录环境，不是内容资产 ID；内容只引用平台账号，执行时再解析 Profile。

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
- 同一内容的多个分发目标必须分别记录 `publishState`；一个平台失败或账号暂停时，不得把其他目标错误标记为失败或成功。

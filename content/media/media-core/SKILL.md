---
name: media-core
description: 媒体内容生产与核心资产层：接收来源流水线或 media-loop 的有界生产请求，发现并验收来源和媒体，把证据、编辑判断、媒体资产、平台适配与分发目标组织成可复用内容资产，并管理完整生命周期。Use when Codex needs to recover an empty content supply, produce a verified asset from a configured source pipeline, normalize content, prepare distribution targets, or reconcile content state. Do not publish content, manage credentials, or replace platform-specific rules.
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
    editorial-framework.md       # 可选的主题/编辑知识
    source-protocol.md           # 来源特有的发现、采集与验收规则（如适用）
    queue.md
    published.md
    runs/<run-id>.md
```

`registry.md` 登记内容源、内容流水线与目标映射；`queue.md` 登记候选和内容资产状态；`runs/` 记录每次发现、核验、生成和跳过；`published.md` 只记录内容资产及其分发目标的最终状态。平台目录中的文档继续保留平台适配、平台发布和平台指标历史，不再成为内容源的唯一事实来源。

本地配置中的每个 `sourcePipelines.<pipeline-id>` 至少声明 `sourceGroupRef`、`schedule`、`dispatchMode`、`targetAccounts` 和 `dedupKeys`。源定时任务默认使用 `dispatchMode: producer-only`：发现、核验、登记可复用内容资产；不直接点击平台发布。若显式声明 `mediaAcquisition`，producer 可以取得已授权候选的媒体并入库，但仍不上传或发布；后续由内容分发目标或 `media-ops` 执行发布。只有明确配置为内容分发任务时，才允许进入发布流程，并且仍需经过平台、账号、版权、频率和成功核验门禁。

`producer-only` 限制的是媒体采集和平台写入，不等于禁止访问来源。若来源协议要求动态主页、回复或对话上下文核验，producer 应使用该协议允许的只读来源访问方式（例如受控浏览器查看公开页面）；不得点赞、评论、关注、私信、提交表单或触发任何来源侧写操作。只读访问不得检查、导出或保存密码、Cookie、令牌、验证码、local storage 或浏览器会话。若不访问动态原始页面就无法判断最新内容，必须把结果记为“最新窗口未核验”，不得根据搜索缓存断言“没有新增内容”。

每个 pipeline 的来源生产调度器必须是唯一来源事实写入者；统一扫描器和平台专属发布定时器都可以触发执行，但必须先进入同一个 `media-ops` 内容目标决策入口。平台定时器可以消费 ready 目标，也可以在目标级库存不足时调用 `media-loop → media-core` 的有界补货流程，但不得自行创建候选、绕过内容层或推进别人的游标。所有触发器必须共享 `contentId + targetId` 运行锁；发现重复来源生产者、未持锁写入或本地记录与内容层游标冲突时，先写入 `scheduler_authority_mismatch`，停止写入。

统一分发扫描器使用同一份配置中的 `dispatchScheduler`。它只规定扫描周期、单轮资源上限和排序方式，不规定所有平台的发布时间，也不覆盖各目标引用的 `strategyRef`。扫描器被外部调度器触发后，才形成一次 `scheduled_run`；读取配置本身不会创建常驻任务。

内容源迁移时不删除平台历史文档，也不重复复制历史帖子；在内容流水线文档中登记来源映射和迁移起点，之后新增内容以 `contentId` 为唯一内容资产 ID，以 `contentId + targetId` 为分发幂等键。

### Authorized media acquisition

仅当 `sourcePipelines.<pipeline-id>.mediaAcquisition.enabled` 为真，且每条候选均已通过来源、授权和去重门禁时，producer 才能采集媒体。配置声明资源根目录、通用验收要求及 `sourceProtocolRef`；来源协议单独定义该来源的发现顺序、允许的交互方式、重试与备选路径、完成判定及游标语义。

- 来源协议不得要求导出、读取或保存 Cookie、密码、令牌或会话数据，也不得绕过来源或下载服务的访问控制。
- 采集结果必须具有本轮来源证据、作者与原始链接、稳定媒体指纹和协议要求的可用性验收；旧文件、临时文件或无法关联至本轮候选的资源一律不算。
- 验收合格后，将文件以稳定名称移入 `resourceRoot`，记录大小、时长、轨道信息（如适用）、内容哈希、作者和原始 URL。下载成功本身不得推进源顺序游标；只有来源协议定义的已核验下游结果回写后才推进。

### Sequential source cursor

当 pipeline 声明顺序消费时，`media-core` 是唯一选材游标所有者；平台技能和平台发布记录只回传结果，不计算下一候选。配置至少声明 `order`、`cursorStateFile`、`candidateStart`、`advanceCondition` 和空游标恢复策略。

- `oldest_to_newest` 必须基于来源的完整可核验顺序或已持久化顺序索引，选择“最后一个顺序释放项的直接后继”；不得从频道最新窗口、推荐列表、热度排序或搜索结果中任选未发布项。
- `nextVideoId` 非空时只处理该项；该项阻塞时保持不变，不能跳过到更新内容。
- `nextVideoId` 为空但存在 `lastReleasedVideoId` 时，先恢复来源顺序并定位其直接后继，再写入 `nextVideoId`；恢复完成前返回 `cursor_recovery_required`，不得创建资产或发布。
- 初始化时没有 `lastReleasedVideoId`，才从来源完整顺序中的最早合格项开始。
- 越序发布必须登记为 `outOfOrderReleased[]` 并参与永久去重，但不得覆盖 `lastReleasedVideoId`、不得改变顺序索引，也不得成为后续游标基线。
- 只有 `advanceCondition` 的下游结果明确且状态成功写回后，才将当前 `nextVideoId` 设为新的 `lastReleasedVideoId`，并计算其直接后继。来源列表变化或直接后继无法核验时停止，不猜测。

## Canonical content asset

每个内容资产至少包含以下对象；缺失会改变事实、版权或选材结论的字段必须先补齐：

```text
contentId
sourceEvidence[]       # 原始 URL、作者、时间、关键段落/时间戳、可见指标
factBoundary           # 已核验事实、作者原意、编辑推断、待核验内容
editorialThesis        # 这一内容只回答的一个核心问题
audiencePromise        # 读者/观众能获得什么
mediaAssets[]          # 图片、视频、音频、封面及其权限和归属
mediaFingerprint        # 已验收媒体的内容哈希；未取得媒体时为空
rightsStatus           # confirmed | pending | restricted | rejected
adaptationNotes        # 平台改编时必须保留、可以压缩或不得出现的内容
distributionTargets[]  # 平台、平台账号、风格、策略、计划时间
lifecycleState         # candidate | verified | adapted | ready | published | retired
feedbackRefs[]         # 发布记录、平台指标和 media-loop 反馈
editorialContextRefs[]  # 可复用的主题知识、栏目框架和编辑边界
```

来源证据、事实边界和版权状态属于内容资产的共同真相；平台版本可以改变语言、节奏、画面和互动入口，但不得改变已核验事实、人物原意、授权范围或核心编辑判断。

### Ready admission check

从 `verified` 写为 `ready` 前，逐项核对并在内容资产中实际写入 `factBoundary`、`audiencePromise`、`adaptationNotes`、`editorialContextRefs` 和 `feedbackRefs`；不得因为媒体已经验收就跳过这些字段。每个待分发目标还必须已有 `plannedAt` 或 `preferredWindow`。缺任一字段时保持 `verified` / `pending`，在来源流水线或内容编辑记录中补齐后再提升；统一扫描器只判断既有资产，不能替资产补造到期时间或把不完整资产直接发布。

## Content-first workflow

1. **Ingest**：接收原始帖子、网页、视频、访谈或用户素材，记录来源和权限线索；动态来源按来源协议使用只读页面访问核验最新窗口和原始上下文。
2. **Normalize**：读取目标内容流水线的 `editorial-framework.md`（如有），拆分事实、原作者观点、编辑推断和待核验主张，聚合同一事件的重复来源。
3. **Define**：依据主题框架确定一个编辑主线、受众收益和内容支柱；不能用“热度高”替代账号相关性。
4. **Verify**：完成事实、来源、版权、隐私、重复和媒体可用性门禁；如有 `source-protocol.md`，按其来源特有规则完成采集与验收，生成可追溯证据卡。
5. **Adapt**：按照每个分发目标调用对应平台技能，生成独立的标题、正文、脚本、画面、引用方式和互动入口。
6. **Distribute**：把已适配版本交给 `media-ops`，由它执行账号、Chrome Profile、频率、人工确认、发布和成功核验。
7. **Learn**：接收 `media-loop` 的内容表现反馈，区分内容问题、平台适配问题和账号分发/健康问题，再创建新版本或实验，不覆盖原始资产。

来源标题、文件名、标签或页面分类中的 `original`、`原创`、`cover`、`live` 等词，只能作为“来源如何自称”的证据，不能单独升级为内容事实。作者身份、词曲归属或原创性必须有独立可见证据支持，例如作者在简介/正文中的明确声明、可信版权信息或其他可核验上下文；证据不足时在 `factBoundary` 中标为未确认，平台适配不得使用“原创歌曲”“原作者”“词曲作者”等确定性表述。

## Produce on demand

`media-core` 可以被来源调度器直接调用，也可以接收 `media-loop.productionRequest` 主动补充供给。后者不是绕过 producer-only 边界，而是在同一内容层执行一次有界生产：

1. 校验 `pipelineRef` 存在且目标账号、内容支柱、来源组和策略引用一致。
2. 读取 pipeline 的状态、协议、队列、已发布记录和最近 run；顺序源先执行 `Sequential source cursor`，只处理当前 `nextVideoId` 或经完整顺序恢复得到的直接后继，不从平台历史、近期窗口或推荐列表猜测素材。
3. 按来源协议发现候选，完成来源、事实、授权、肖像、隐私和去重门禁；只有配置允许时才采集媒体。
4. 对媒体执行稳定文件、指纹、可播放性、时长、画面和音视频轨验收，并将合格文件写入资源根目录。
5. 补齐 canonical asset、ready admission 字段和目标自己的 `plannedAt` / `preferredWindow`；调用目标平台技能生成适配版本，但不执行平台写入。
6. 返回 `asset_ready`、`production_blocked` 或 `no_qualified_candidate`，记录具体原因和下一可恢复动作。

单次 production request 默认最多生成 1 个 ready 资产；同一 run、同一 `requestId + pipelineRef` 只能执行一次。失败不得回退旧 Downloads、已发布资产或低于门禁的候选，也不得无限刷新或循环采集。只有 `asset_ready` 才能交回 `media-ops` 重新扫描；生产成功本身不等于发布成功，顺序游标仍按来源协议规定的下游结果推进。

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

目标的发布时间和频率必须分开表达：`plannedAt` 或 `preferredWindow` 表示这一条内容目标何时可以发布；`strategyRef` 指向的平台/账号策略则提供发布窗口、最小间隔、每日上限、失败退避和账号健康约束。内容层不复制这些策略字段，也不把一个平台的频率传播到其他目标。

`browserProfileRef` 或 `apiContext` 由执行时根据 `platformAccountRef` 解析，不要求在内容资产中重复保存登录环境。这样同一内容可以生成多个目标，例如 X 原生引用、小红书收藏型图文和抖音知识短视频；每个目标都必须经过目标平台技能的专属筛选与改编。平台账号不是内容资产的拥有者，内容资产也不能绕过账号健康和发布门禁。

## Content-driven dispatch

定时器的主对象是“到期的内容分发目标”，不是某个平台技能。统一扫描器和平台定时器只是不同触发面；`media-core` 负责表达内容何时准备好、哪些目标到期、目标之间是否有顺序依赖，`media-ops` 负责统一决策、运行锁和发布回写；平台的发布时间窗口、频率上限和健康限制仍作为目标级约束保留。

统一分发扫描器可以每 10 分钟运行一次，但“扫描一次”不等于“发布一次”。每轮按以下顺序筛选：

1. 只取 `lifecycleState: ready` 且 `publishState` 未完成的目标。
2. 检查目标自己的 `plannedAt` / `preferredWindow` 是否到期。
3. 解析 `strategyRef`，应用平台/账号的时间窗口、最小间隔、每日上限、单轮上限和失败退避。
4. 读取 `media-loop` 健康状态；限流、标签、账号不匹配或不确定发布状态优先阻断目标。
5. 按到期时间、策略优先级和 Profile 分组排序，再交给 `media-ops`；每个目标独立记账和回写。

同一 `platformAccountRef` 存在多个未完成目标时，必须按目标队列选择“最早到期、仍未完成且当前 eligible”的目标，而不是按来源最新、内容热度或最近创建时间抢占。排序键依次为 `plannedAt`、`targetCreatedAt`、`sourceObservedAt`、`targetId`；`targetSelection.neverPreferLatest` 默认必须为 true。目标自己的内容未 ready、尚未到期或目标级适配/版权门禁失败时，保留该目标并记录原因，同时可以继续处理下一条 eligible 目标；账号级限流、标签、不确定发布状态或账号不匹配则暂停该账号的后续目标。这样同一内容在小红书已发布而抖音未发布时，抖音会优先补发最早一条未完成的抖音目标，不会被后来新增且已在小红书发布的内容抢走。

若扫描结果为空，返回结构化库存状态给 `media-loop`，不要只返回终止消息。`media-loop` 判定为 `ready_supply_starved` 并给出有效 `productionRequest` 后，`media-core` 可在同一轮执行一次 `Produce on demand`；若生成 `asset_ready`，调用方必须重新运行 ready admission 和到期扫描，不能把“生产完成”直接当作“允许发布”。

同一内容的多个目标因此可以错峰发布：一个目标因尚未到窗口或账号已达上限而保持 `pending`，不能连带改变其他目标的状态。统一扫描器的周期是资源调度参数；平台发布频率仍由各目标的 `strategyRef` 控制。

当一个内容的多个目标同时到期时，执行器可以按解析后的 `browserProfileRef` 分组，优先连续处理同一 Profile 下的不同平台目标，减少 Profile 切换。分组只优化执行顺序，不合并账号身份，也不合并发布结果：每个目标仍要单独核对平台账号、事实、版权、重复和成功状态。

同一 Chrome Profile 可以承载用户已确认登录的多个不同平台账号；同一平台的多个账号是否共用 Profile 仍遵守 `media-ops` 的隔离规则。Profile 是账号登录环境，不是内容资产 ID；内容只引用平台账号，执行时再解析 Profile。

## Boundaries

- `media-core`：定义内容资产、证据卡、适配契约、生命周期和内容层版本。
- `media-core` 外部内容文档：保存主题知识、栏目框架、归因等级和跨平台编辑门禁；它们通过 `editorialContextRefs` 被内容资产或平台适配读取。
- `media-ops`：读取账号配置和内容资产，调度目标，执行 Profile 路由、发布门禁、外部记录回写和浏览器清理。
- `media-loop`：监测账号健康、内容指标和实验结果，提出有证据的策略覆盖。
- `platform/x`、`platform/x-api`、`platform/douyin`、`platform/xiaohongshu`：负责平台推荐机制、平台发现、平台化改编、平台发布和平台指标解释。

`media-core` 不读取密码、Cookie、令牌或浏览器会话，不执行来源侧或平台侧写操作，不直接点击发布按钮，不自行决定某个平台的算法权重，也不把跨平台绝对阅读量当作统一成功指标。按来源协议进行的受控只读页面访问只用于发现、上下文展开和证据核验，不构成媒体采集、账号互动或发布权限。显式配置的 `mediaAcquisition` 只允许按照对应来源协议为已授权候选采集和入库资源，不构成发布权限。

## Hard gates

- 事实边界不清、来源不可追溯、版权状态不明或媒体不可用时，内容资产不得进入 `ready`。
- `ready` 不是媒体文件验收的同义词；缺少受众承诺、平台改编边界、编辑上下文、反馈引用，或任一目标缺少 `plannedAt` / `preferredWindow` 时，必须阻止提升并返回缺失字段。
- 同一事件的转载、翻译和摘要不能被登记为多个独立原创资产。
- 平台版本必须保留必要的来源归属和披露；翻译或引用本身不构成原创增量。
- 发布结果不明确时保持 `publishState: uncertain`，不得推进生命周期或盲目重试。
- 任何策略优化都创建新版本，保留原始证据、旧文案、发布结果和回滚依据。
- 同一内容的多个分发目标必须分别记录 `publishState`；一个平台失败或账号暂停时，不得把其他目标错误标记为失败或成功。
- 任何资源文件没有可追溯的本轮下载证据、作者/原始链接、媒体指纹或音视频验收时，不得进入 `verified`，不得交给下游分发任务。
- 动态来源需要原始页面才能判断最新窗口时，不得以搜索摘要、缓存时间或旧页面替代实时只读核验；无法完成只读核验时记录能力不足或窗口未核验，不得写成“没有新增内容”。

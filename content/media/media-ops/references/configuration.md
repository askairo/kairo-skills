# 配置模型

配置只描述内容运营上下文，不保存登录凭证，也不负责 Skill 的发布、安装或同步。

## 解析顺序

按以下顺序寻找配置，找到后停止自动发现：

1. 用户在当前请求中传入的配置对象或绝对路径；
2. `<AGENT_HOME>/local-config/media-ops/config.yaml` 或 `config.json`；

按 `skills-loop` 的共享规范解析当前 Agent Home。若存在多个 Agent Home 且上下文无法判断，要求用户显式选择，不跨 Agent 查找。显式运行参数覆盖选中配置，但默认不回写。

新建或更新配置默认写入首选 Agent 本地目录。若 YAML 与 JSON 同时存在，要求用户明确选择，避免静默读取错误版本。不读取旧配置目录或旧文件名。

## 概念关系

```text
browserProfiles
  -> 本机 Chrome Profile 路由，不含凭证
account
  -> platformAccounts：各平台公开身份，不含凭证
  -> styles：账号通用风格及平台风格
  -> sourceGroups：可信名单和发现边界
  -> strategies：候选数量、阈值、频率和发布门禁
content asset
  -> distributionTargets：内容版本、目标平台、平台账号、格式和目标时间
```

所有对象都使用稳定 ID 引用。一个逻辑账号代表一个独立的品牌/运营主体，可以关联多个平台账号，但这些平台账号必须共享同一定位、受众和内容支柱。不同主题、受众、内容形态或运营目标的账号必须拆成不同逻辑账号；不能因为属于同一用户或同一团队就合并。风格、来源组或策略可以被多个逻辑账号复用，但账号健康、历史基线、实验结果和发布频率必须隔离。

## 配置结构与职责

配置采用“Chrome Profile 路由 + 账号共性 + 平台差异 + 运行策略”的四层结构：

```text
execution.adaptationBacklog.suppression
├── scope: eligible_recoverable_adaptation_only
├── requireEligibleBacklog: true
├── unchangedResult: adaptation_backlog_unchanged
└── emptyReadyWithoutEligibleBacklogResult: ready_supply_starved
browserProfiles.<profile>
├── browser: chrome
├── profileName                         # Chrome 中显示的 Profile 名称
├── switchMethod: chrome-mcp | playwright-mcp | current-session
└── status: verified | needs-verification
accounts.<account>
├── vertical / audience / positioning / contentPillars  # 账号共性
├── sourceGroupRefs / baseStyleRef                       # 默认来源与风格
├── strategyRef                                          # 默认执行策略
└── platforms.<platform>
    ├── enabled / accountRef / styleRef                  # 平台身份
    ├── strategyRef                                      # 可选的平台策略覆盖
    └── operation                                        # 平台运营目标与发现策略
        ├── goal
        ├── contentMode
        ├── discoveryTopics
        ├── sourceGroupRefs
        ├── editorialFrameworkRef       # 指向 media-core 内容层主题框架
        ├── coverSpecRef                 # 平台/账号视觉适配文档
        ├── selectionSignals
        ├── exclusions
        ├── rightsPolicy
        ├── transport                         # 平台适配器标识
        ├── interactiveSkill / scheduledSkill
        ├── interactiveTransport / scheduledTransport
        ├── browserAutomation
        └── allowDownload                 # 抖音发布时是否允许下载，默认 false
```

职责边界如下：

- `execution.adaptationBacklog.suppression` 只压制仍然存在的可恢复适配积压。`requireEligibleBacklog: true` 表示必须先排除争议、审核中、未知、已完成、账号暂停和 disabled 目标；排除后 ready 为零时使用 `emptyReadyWithoutEligibleBacklogResult: ready_supply_starved`，不得沿用旧队列指纹跳过补货。
- `accounts.<account>` 描述账号长期定位、受众和内容支柱，不描述某个平台的推荐技巧。
- `browserProfiles.<profile>` 描述本机可见的 Chrome Profile 路由，不保存密码、Cookie、令牌、浏览器用户数据目录或其他认证材料；`profileName` 必须是用户在 Chrome Profile 菜单中看到的名称。
- `accounts.<account>` 是运营隔离边界，不是用户或设备边界。若一个科技 X 账号和一个音乐抖音账号的定位不同，应建立两个 `accounts` 条目，即使由同一人管理。
- `platforms.<platform>.operation` 描述该账号在特定平台“想做什么、找什么、优先什么、排除什么”。例如 X 可以关注讨论、引用、主页访问和关注转化；音乐类抖音账号可以关注音频适配、前三秒记忆点、完播潜力和版权。
- `operation.transport`、`interactiveSkill`、`scheduledSkill` 和对应 transport 字段定义执行路由，不保存凭证。`scheduledTransport` 是定时写操作的必填字段，不能依赖默认值。
- `operation.premium` 是平台账号能力声明，不保存订阅凭证。对 X 可使用 `enabled: true`、`longForm: enabled`、`status: user-confirmed` 和 `capabilityCheck: editor-runtime`；它只允许执行器在当前编辑器实际显示长文入口时选择 Premium 长文，不能绕过账号健康、平台限流、事实、版权、重复或成功核验门禁。
- `sourceGroupRefs` 定义允许寻找的来源；平台级配置可以缩小账号默认来源范围，不得绕过来源和版权门禁。
- `sourceGroups.<group>.priorityAccounts` 是可选的重点账号白名单。每项使用 `sourceId` 引用同一来源组中已启用的 X 来源，并填写规范化 `handle`；平台子技能应优先扫描和排序命中白名单的候选，但不得因此跳过事实、版权、相关性、原创增量、重复和安全门禁。
- `docsRoot` 可选，指向 Agent 本地的外部运营文档根目录；它不进入技能源码。平台发布文档仍按 `<docsRoot>/<platform>/<account>/` 组织。跨平台内容源、内容资产和源流水线不放在这里，而由 `media-core` 的 `<AGENT_HOME>/local-config/media-core/config.json` 指向 `<docsRoot>/content/` 独立管理。
- `media-ops` 读取 `contentRef` 或 `distributionTargetRef` 时，先按 `media-core` 的内容文档规范读取来源证据、事实边界、版权状态和目标状态；平台目录只作为发布、指标和账号运行历史，不得覆盖内容层共同真相。
- `editorialFrameworkRef` 只指向 `media-core` 内容层的主题知识、栏目框架和编辑边界；`coverSpecRef` 只指向平台/账号的视觉适配文档。前者可以被多个平台复用，后者不得反向写入内容层主题框架。
- `selectionSignals` 是运营目标和观察指标，不是平台算法的固定权重；平台子技能将其转换为自己的发现 brief 和候选评分。
- `media-loop` 使用独立的 `<AGENT_HOME>/local-config/media-loop/config.json` 保存监测窗口、健康门禁、最小可比样本量、实验规则和写回开关；不得把这些运行数据塞进 `media-ops` 账号配置。
- `media-ops` 在运行开始时读取 `media-loop` 最近一次有效反馈，运行结束后将发布结果交给 `media-loop`；反馈中的 `strategyOverrides` 只覆盖本轮或下一轮上下文，除非用户明确授权，不回写常驻账号配置。
- 账号健康状态优先于内容优化：标签、平台真实限流、连续发布失败、账号不匹配和不确定发布状态会触发暂停，不能被 `minScore`、热点权重或外部触发覆盖。
- `strategyRef` 定义内容选择、平台适配和单次触发批量保护；旧的数量/时间频率字段不再作为已触发目标的发布门禁，平台级覆盖只影响该平台，不改变不可关闭的事实、版权、安全和成功核验规则。

### 内容驱动调度与 Profile 聚合

内容驱动模式下，`media-core` 内容资产生成一个或多个 `distributionTargets`，每个目标引用 `platformAccountRef`、`styleRef`、`strategyRef`、格式和 `plannedAt` 或 `preferredWindow`。执行器再从 `platformAccounts.<accountRef>.browserProfileRef` 解析登录环境。

因此，内容配置不重复保存 Profile；Profile 仍是账号登录环境配置。一个内容可以在不同平台目标上解析到同一个 Profile，执行器可以按 Profile 聚合这些目标以减少切换，但必须为每个平台目标单独核对公开账号身份，并分别记录发布状态。

`schedule` 在迁移期间仍可保留在 strategy 中，但只作为旧配置和审计信息；实际触发频率以外部自动化任务的 RRULE 为准，`schedule` 不得阻断已触发运行，也不再提供最小间隔或每日上限。

统一分发扫描器由 `media-core` 本地配置声明：

```json
{
  "dispatchScheduler": {
    "mode": "content-target-scanner",
    "frequency": "interval",
    "intervalMinutes": 10,
    "timezone": "Asia/Shanghai",
    "maxTargetsPerRun": 3,
    "ordering": ["plannedAt", "strategyPriority", "browserProfileRef"],
    "targetSelection": {
      "mode": "oldest_due_unfinished_eligible",
      "ordering": ["plannedAt", "targetCreatedAt", "sourceObservedAt", "targetId"],
      "neverPreferLatest": true,
      "preserveUnfinishedTargets": true,
      "blockedTargetHandling": "leave_and_consider_next_eligible",
      "accountLevelBlockHandling": "pause_account"
    }
  }
}
```

它只表示一次外部触发扫描，不表示每个平台都必须按固定周期发布。一次扫描必须对每个未完成目标重新计算有效性：

```text
eligible(target) =
  target.lifecycleState == ready
  AND target.publishState 未完成
  AND target.platform/account identity matches
  AND fact/rights/media/dedup/run-lock gates pass
  AND platform-reported rate-limit/health gates pass
  AND currentRunCount < strategy.maxPublishedPerRun
```

其中账号、平台、策略和失败状态按 `target.strategyRef` 独立解析；同一内容的其他目标不共享这些状态。`plannedAt`、`preferredWindow`、`schedule`、`minIntervalMinutes`、`maxPublishedPerDay` 和媒体获取次数都不是已触发运行的阻断条件。`maxPublishedPerRun` 只是一次触发的批量保护。配置中的 `schedule` 和 `dispatchScheduler` 都不会单独创建常驻系统任务。

内容驱动的 unattended 策略不要求 `publishPolicy.minIntervalMinutes`、`publishPolicy.maxPublishedPerDay` 或 `publishPolicy.platformLimitBackoffHours`；这些旧字段即使残留也不得阻断已触发运行。`media-ops/config` 记录账号和执行路由，外部自动化任务的 RRULE 是发布频率真相；若文档与 RRULE 不一致，记录差异供维护，不得把差异伪装成发布失败或时间门禁。平台真实返回的 rate limit 仍必须暂停并按平台状态恢复。

同一 `platformAccountRef` 的目标选择默认采用 `oldest_unfinished_eligible`：`plannedAt` 最早者优先，随后使用 `targetCreatedAt`、`sourceObservedAt`、`targetId` 打破平局。`neverPreferLatest: true` 禁止用“最新资源”覆盖历史未完成目标；目标级阻塞只保留并记录该目标，账号级健康阻断则暂停该账号队列。

### Runtime context

`media-ops` 读取配置后，向平台子技能传递统一的运行上下文：

```text
accountId, platform, platformAccountRef, browserProfileRef, goal, contentMode, audience,
contentPillars, discoveryTopics, sourceGroups,
selectionSignals, exclusions, rightsPolicy,
lookback, publishingMode, approvalBoundary
```

平台子技能先依据上下文生成 `discoveryBrief`，再参与素材发现和平台专属筛选；`media-ops` 负责合并、核验、调度和发布门禁，不把不同平台压成同一套“热门内容”规则。

## YAML 示例

```yaml
version: 1

accounts:
  personal-efficiency:
    displayName: 个人效率
    vertical: 个人效率
    audience:
      - 希望减少重复劳动的中文知识工作者
      - 关注工具与方法论的个人用户
    positioning: 用可靠信息和亲身可验证的方法，解释如何更清醒地使用工具提升效率
    contentPillars:
      - AI 与自动化工具
      - 时间与注意力管理
      - 知识管理与工作流
    baseStyleRef: practical-analyst
    sourceGroupRefs:
      - productivity-core
    strategyRef: weekday-review
    platforms:
      x:
        enabled: true
        accountRef: efficiency-x
        styleRef: x-concise
        operation:
          goal: 通过可靠的 AI 与自动化信息获得讨论、主页访问和关注转化
          contentMode: 英文原帖发现与中文原创解释/引用帖
          discoveryTopics:
            - AI workflow
            - developer tools
          selectionSignals:
            - reply
            - repost
            - profile_click
            - follow_author
          exclusions:
            - 未经核验的传闻
            - 与账号内容支柱无关的短期热搜
          rightsPolicy: 保留原作者归属，引用帖优先使用平台原生引用能力
      xiaohongshu:
        enabled: true
        accountRef: efficiency-xhs
        styleRef: xhs-collectible
        operation:
          goal: 提供可搜索、可收藏的效率方法
          contentMode: 清单、步骤和避坑图文
          selectionSignals:
            - search_intent
            - save_value
      douyin:
        enabled: true
        accountRef: efficiency-douyin
        styleRef: douyin-explainer
        operation:
          goal: 通过短视频留存和完播建立账号栏目
          contentMode: 竖屏口播
          selectionSignals:
            - first_three_seconds
            - completion
            - comment
          exclusions:
            - 无法确认版权的音乐或视频
          rightsPolicy: 仅使用已获授权或平台可合法使用的音频与画面

platformAccounts:
  efficiency-x:
    platform: x
    handle: <x-handle>
    locale: zh-CN
    browserProfileRef: chrome-efficiency-x
  efficiency-xhs:
    platform: xiaohongshu
    handle: <xiaohongshu-handle>
    locale: zh-CN
  efficiency-douyin:
    platform: douyin
    handle: <douyin-handle>
    locale: zh-CN

styles:
  practical-analyst:
    voice: 克制、清楚、实用
    pointOfView: 第一人称分析，但不虚构亲身体验
    principles:
      - 先说明事实，再给判断
      - 强调适用条件和代价
      - 给出可以立即执行的下一步
    avoid:
      - 制造焦虑
      - 夸大效率收益
      - 把厂商宣传写成独立结论
  x-concise:
    format: 单帖或短 thread
    density: 高
    cta: 提出一个具体问题
  xhs-collectible:
    format: 图文卡片
    density: 中
    cta: 提供检查单或可收藏步骤
  douyin-explainer:
    format: 竖屏口播
    density: 中
    cta: 引导观众尝试一个具体动作

sourceGroups:
  productivity-core:
    discoveryMode: curated-first
    allowTopicSearch: true
    searchTopics:
      - personal productivity
      - AI workflow
      - knowledge management
    sources:
      - id: manual-inbox
        type: manual
        enabled: true
      - id: example-official-blog
        type: website
        url: <source-url>
        trustTier: primary
        enabled: true

strategies:
  weekday-review:
    lookback: P2D
    maxCandidates: 15
    minScore: 75
    selectLimit: 2
    targetPlatforms:
      - x
      - xiaohongshu
      - douyin
    schedule:
      frequency: weekdays
      times:
        - "09:00"
      timezone: Asia/Shanghai
    publishingMode: reviewed
    maxPublishedPerRun: 1
    humanApprovalRequired: true
    autoPublish: false
```

## 字段规则

### accounts

- `vertical`、`audience`、`positioning` 和至少一个 `contentPillars` 必填。
- `platforms` 只支持 `x`、`xiaohongshu` 和 `douyin`；每个平台必须引用匹配的 `platformAccounts`。
- 每个平台可以声明 `operation.goal`、`operation.contentMode`、`operation.discoveryTopics`、`operation.selectionSignals`、执行传输和平台专属约束；这些字段用于生成发现策略和执行路由，不得保存凭证。
- 抖音可以声明 `operation.allowDownload`，布尔值默认是 `false`；`false` 表示发布前关闭“允许下载”（等价于“不允许下载”）。该配置只是期望状态，平台子技能仍必须在最终发布前重新读取页面控件；状态不明或仍允许下载时停止。
- `operation.sourceGroupRefs`、`operation.exclusions` 和 `operation.rightsPolicy` 用于收窄来源与安全边界；缺少 `goal` 或 `contentMode` 且会改变选材结论时，应请求补充。
- `operation.editorialFrameworkRef` 是相对于 `docsRoot` 的外部内容文档路径，必须指向 `media-core` 内容目录中的主题框架；`operation.coverSpecRef` 是相对于 `docsRoot` 的平台/账号视觉规范路径。两者都不保存凭证。
- 平台可以声明 `operation.transport`、`operation.interactiveSkill`、`operation.scheduledSkill`、`operation.interactiveTransport`、`operation.scheduledTransport` 和 `operation.browserAutomation`；浏览器平台的两个 transport 必须显式选择 `chrome-mcp` 或 `playwright-mcp`，API 平台必须选择已接入的 `official-api`。X 的无人值守策略若选择 `x`，不得被默认改写为 `x-api`。
- `chrome-mcp` 通过旧运行时的 `openTabs` / `claimTab`，或新版 Unified Computer Use 中 `cua.getState()` 暴露的 `family: chrome`、`type: extension` browser 与 `cua.getTab(...)`，接管目标 Profile 的既有 Tab。后者操作的是 Chrome Plugin extension Tab，不是 `cua.getApp("Google Chrome")` 的 Computer Use 桌面回退；禁止使用原生窗口、桌面坐标或截图点击。`playwright-mcp` 通过 Playwright MCP Bridge 接管用户在目标 Profile 中授权的既有 Tab。任一通道都必须独立完成页面读取、输入、上传、编辑、发布控件、结果核验和 Tab 清理；禁止在两者之间或向 Computer Use、controlled-browser-session、CDP 及其他 Chrome 控制接口回退。`official-api` 不打开 Chrome。两种 `switchMethod` 都不负责猜测或切换 Profile；没有可确认的目标 Tab 时停止。旧版独立工具名不存在但 Chrome extension browser 和目标 Tab 可见时，不得返回 `profile_route_missing`。
- 当策略是有效 `publishingMode: unattended` 时，传输字段只决定如何执行，不会关闭事实、版权、账号、重复、结果核验或运行时安全策略；缺少、拼写错误或平台不支持的 `scheduledTransport` 必须返回 `scheduled_transport_missing` 或 `scheduled_transport_unsupported`，不得静默回退。
- `platforms.<platform>.strategyRef` 可覆盖账号默认策略；合并顺序为“请求覆盖 → 平台配置 → 账号默认 → Skill 默认”。
- `baseStyleRef`、`sourceGroupRefs` 和 `strategyRef` 必须指向已定义且启用的对象。
- 浏览器平台的 `platformAccounts.<accountRef>.browserProfileRef` 必须指向已定义的 `browserProfiles.<profile>`；同一平台的不同账号不得引用同一个 Profile。`switchMethod: current-session` 只适合单账号当前会话，不能授权同平台多账号无人值守切换。
- `switchMethod: chrome-mcp` 表示先从 Chrome MCP 可见 Tab 中确认目标 browser，再用平台页面核对 handle；运行时暴露 `profileName` 时必须与配置一致。若新版 Chrome extension inventory 不提供 `profileName`，只有在恰好一个 extension browser 可见、其中存在目标站点 Tab、配置 Profile 状态为 `verified` 且页面实读 handle 一致时，才可把本轮 browserId / extensionInstanceId 绑定到 `browserProfileRef`；存在多个无法区分的 extension browser 时必须返回 `profile_route_missing`，不得猜测。`switchMethod: playwright-mcp` 表示用户先在 `profileName` 对应 Chrome Profile 中授权已登录 Tab，再由 Bridge 接管并核对 handle。没有可接管的目标 Tab、配置 Profile 未验证或 handle 不一致时，执行器必须返回 `profile_route_missing` 或 `account_mismatch` 并停止。页面发布必须由已声明的同一通道执行。
- 同一 `accounts.<account>` 下的所有平台必须通过定位、受众和内容支柱一致性检查；不一致时拆分逻辑账号，不得混合基线和反馈。

### platformAccounts

- 只保存平台、公开 handle、地区、语言等内容身份信息。
- 浏览器平台可以增加 `browserProfileRef`，但只能引用 `browserProfiles` 中的本机环境标识；API 平台不需要该字段。
- 禁止保存密码、Cookie、令牌、恢复码、浏览器配置或其他认证材料。
- 发布连接器或浏览器会话属于执行环境，不属于此配置。

### styles

- 用自然语言定义 `voice`、视角、表达原则、禁用表达、格式偏好和行动引导。
- 账号通用风格先应用，平台风格随后覆盖冲突项。
- 风格不能覆盖事实核验、版权、安全和人工确认门禁。

### sourceGroups

- 支持 `manual`、`rss`、`newsletter`、`website`、`x-list`、`youtube`、`podcast` 和 `search` 等来源类型。
- `curated-only` 禁止扩展搜索；`curated-first` 先查名单再按主题补充；`discovery` 允许广泛发现，但仍执行来源核验。
- 为固定来源记录 URL、信任层级、适用主题和启用状态。不要在仓库中的示例配置写入私人名单。

### strategies

- `lookback` 使用 ISO 8601 duration；`maxCandidates`、`minScore` 和 `selectLimit` 控制单次运行。
- `schedule` 只声明期望频率、时间和时区。Skill 被调用时执行一次，不因读取配置而自动建立计划任务；“执行一次”与“创建常驻调度”是两个不同的操作。
- 内容驱动调度时，`schedule` 约束由到期的 `distributionTarget` 继承；调度器应以 `contentId + targetId` 作为幂等运行键，不以平台技能名作为唯一运行键。
- `targetPlatforms` 只能选择账号已启用的平台。
- `publishingMode: reviewed` 要求 `humanApprovalRequired: true` 且 `autoPublish: false`。
- `publishingMode: unattended` 要求 `humanApprovalRequired: false`、`autoPublish: true`、`selectLimit: 1`、`maxPublishedPerRun: 1` 与有效 `scheduledTransport`。`schedule` 不属于无人值守模式的必填门禁；实际由外部控制定时器决定何时触发一次运行，从而控制发布尝试次数，避免固定频率扫描造成大量空转。配置校验通过后，已被调度器触发的一次运行不增加业务层逐条确认；仍必须遵守所选执行通道的运行时安全策略。
- 无人值守模式只授权计划运行按内容门禁发布，不授权读取凭证、降低事实阈值、重复发布或在结果不明确时重试。

执行器应在运行记录中区分 `interactive_run`、`scheduled_run` 和 `schedule_setup`。门禁失败必须返回具体原因：配置无效、没有合格候选、事实/来源/版权不足、账号不匹配、重复或发布成功信号不明确；不能把所有失败都归类为人工确认未满足。

## 校验与合并

按“请求覆盖项 → 平台配置 → 账号引用对象 → Skill 默认规则”合并。执行前检查：

- `version` 为受支持版本；
- ID 唯一且所有引用存在；
- 平台类型与账号引用一致；
- 至少存在一个启用的数据源和目标平台；
- 数量和阈值合理，时区有效；
- 不含疑似凭证字段；
- 发布模式、人工确认、自动发布和执行传输字段组合合法；无人值守模式具备必要限额和显式 `scheduledTransport`。外部控制定时器负责实际触发和发布次数控制，`strategy.schedule` 可以保留作兼容旧配置或审计信息，但不是必填门禁。

校验失败时列出具体字段路径和修复建议，不带着部分配置继续创作。

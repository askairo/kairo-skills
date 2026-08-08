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
account
  -> platformAccounts：各平台公开身份，不含凭证
  -> styles：账号通用风格及平台风格
  -> sourceGroups：可信名单和发现边界
  -> strategies：候选数量、阈值、频率和发布门禁
```

所有对象都使用稳定 ID 引用。一个逻辑账号可以关联多个平台账号；同一风格、来源组或策略也可以被多个账号复用。

## 配置结构与职责

配置采用“账号共性 + 平台差异 + 运行策略”的三层结构：

```text
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
        ├── selectionSignals
        ├── exclusions
        └── rightsPolicy
```

职责边界如下：

- `accounts.<account>` 描述账号长期定位、受众和内容支柱，不描述某个平台的推荐技巧。
- `platforms.<platform>.operation` 描述该账号在特定平台“想做什么、找什么、优先什么、排除什么”。例如 X 可以关注讨论、引用、主页访问和关注转化；音乐类抖音账号可以关注音频适配、前三秒记忆点、完播潜力和版权。
- `sourceGroupRefs` 定义允许寻找的来源；平台级配置可以缩小账号默认来源范围，不得绕过来源和版权门禁。
- `sourceGroups.<group>.priorityAccounts` 是可选的重点账号白名单。每项使用 `sourceId` 引用同一来源组中已启用的 X 来源，并填写规范化 `handle`；平台子技能应优先扫描和排序命中白名单的候选，但不得因此跳过事实、版权、相关性、原创增量、重复和安全门禁。
- `docsRoot` 可选，指向 Agent 本地的外部运营文档根目录；它不进入技能源码。建议按 `<docsRoot>/<platform>/<account>/` 组织账号的队列、发布历史、运行记录和复盘。
- `selectionSignals` 是运营目标和观察指标，不是平台算法的固定权重；平台子技能将其转换为自己的发现 brief 和候选评分。
- `media-loop` 使用独立的 `<AGENT_HOME>/local-config/media-loop/config.json` 保存监测窗口、健康门禁、最小可比样本量、实验规则和写回开关；不得把这些运行数据塞进 `media-ops` 账号配置。
- `media-ops` 在运行开始时读取 `media-loop` 最近一次有效反馈，运行结束后将发布结果交给 `media-loop`；反馈中的 `strategyOverrides` 只覆盖本轮或下一轮上下文，除非用户明确授权，不回写常驻账号配置。
- 账号健康状态优先于内容优化：标签、限流、连续发布失败、账号不匹配和不确定发布状态会触发暂停或降频，不能被 `minScore`、发布时间或热点权重覆盖。
- `strategyRef` 定义数量、时间和发布门禁；平台级覆盖只影响该平台，不改变不可关闭的事实、版权、安全和人工确认规则。

### Runtime context

`media-ops` 读取配置后，向平台子技能传递统一的运行上下文：

```text
accountId, platform, goal, contentMode, audience,
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
- 每个平台可以声明 `operation.goal`、`operation.contentMode`、`operation.discoveryTopics`、`operation.selectionSignals` 和平台专属约束；这些字段用于生成发现策略，不得保存凭证。
- `operation.sourceGroupRefs`、`operation.exclusions` 和 `operation.rightsPolicy` 用于收窄来源与安全边界；缺少 `goal` 或 `contentMode` 且会改变选材结论时，应请求补充。
- 平台可以声明 `operation.transport`、`operation.interactiveSkill`、`operation.scheduledSkill`、`operation.interactiveTransport`、`operation.scheduledTransport` 和 `operation.browserAutomation`；X 的无人值守策略若选择 `media-x`，不得被默认改写为 `media-x-api`。
- 当 `scheduledSkill: media-x` 且策略是有效 `publishingMode: unattended` 时，`scheduledTransport: controlled-browser-session` 与 `browserAutomation: allowed-when-publishingMode-unattended` 表示触发后直接执行，不要求逐条人工确认；仍必须执行账号、事实、版权、重复、限额和发布成功核验。
- `platforms.<platform>.strategyRef` 可覆盖账号默认策略；合并顺序为“请求覆盖 → 平台配置 → 账号默认 → Skill 默认”。
- `baseStyleRef`、`sourceGroupRefs` 和 `strategyRef` 必须指向已定义且启用的对象。

### platformAccounts

- 只保存平台、公开 handle、地区、语言等内容身份信息。
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
- `targetPlatforms` 只能选择账号已启用的平台。
- `publishingMode: reviewed` 要求 `humanApprovalRequired: true` 且 `autoPublish: false`。
- `publishingMode: unattended` 要求 `humanApprovalRequired: false`、`autoPublish: true`、`selectLimit: 1`、`maxPublishedPerRun: 1`，并配置有效 `schedule`。配置校验通过后，已有调度触发的一次运行无需人工确认；用户明确要求按该配置执行一次时，也不应被再次拦截。只有创建或更新常驻调度需要单独的用户请求。
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
- 发布模式、人工确认和自动发布字段组合合法；无人值守模式具备限额和调度。

校验失败时列出具体字段路径和修复建议，不带着部分配置继续创作。

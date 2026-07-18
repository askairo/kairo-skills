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
  -> strategies：候选数量、阈值、频率和人工门禁
```

所有对象都使用稳定 ID 引用。一个逻辑账号可以关联多个平台账号；同一风格、来源组或策略也可以被多个账号复用。

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
      xiaohongshu:
        enabled: true
        accountRef: efficiency-xhs
        styleRef: xhs-collectible
      douyin:
        enabled: true
        accountRef: efficiency-douyin
        styleRef: douyin-explainer

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
    humanApprovalRequired: true
    autoPublish: false
```

## 字段规则

### accounts

- `vertical`、`audience`、`positioning` 和至少一个 `contentPillars` 必填。
- `platforms` 只支持 `x`、`xiaohongshu` 和 `douyin`；每个平台必须引用匹配的 `platformAccounts`。
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
- `schedule` 只声明期望频率、时间和时区。Skill 被调用时执行一次，不因读取配置而自动建立计划任务。
- `targetPlatforms` 只能选择账号已启用的平台。
- `humanApprovalRequired` 必须为 `true`，`autoPublish` 必须为 `false`。

## 校验与合并

按“请求覆盖项 → 平台配置 → 账号引用对象 → Skill 默认规则”合并。执行前检查：

- `version` 为受支持版本；
- ID 唯一且所有引用存在；
- 平台类型与账号引用一致；
- 至少存在一个启用的数据源和目标平台；
- 数量和阈值合理，时区有效；
- 不含疑似凭证字段；
- 人工门禁未被关闭。

校验失败时列出具体字段路径和修复建议，不带着部分配置继续创作。

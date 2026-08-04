# X API 发布与核验

本参考只适用于 X 的程序化发现、身份核验和发布。官方接口文档以 `https://docs.x.com/` 为准；如果官方接口或套餐能力变化，先重新核验，不用网页脚本绕过限制。

## 认证边界

- 发帖和读取用户上下文使用 OAuth 2.0 Authorization Code with PKCE 或 OAuth 1.0a User Context；应用级 Bearer Token 不能代表 `@zzyloxx` 发帖。
- 所需 OAuth 2.0 scopes 至少按实际接口申请 `tweet.read tweet.write users.read offline.access`；只申请必要权限。
- 凭证只能由外部密钥管理器或运行时注入。技能、配置、日志和候选记录不得保存 access token、refresh token、client secret、Cookie 或验证码。
- 发布前调用 `GET /2/users/me`，确认返回的 username 与配置中的 `@zzyloxx` 完全一致；不一致立即停止。

## 主要接口

- 发现与核验：`GET /2/tweets/search/recent`、`GET /2/users/:id/tweets`、`GET /2/tweets/:id`。
- 发帖：`POST https://api.x.com/2/tweets`，正文使用 `text`。
- 引用帖：同一 `POST /2/tweets` 请求使用 `quote_tweet_id`，不要把原帖链接当成网页自动化的替代品。
- 结果核验：使用返回的 Post ID 查询 `GET /2/tweets/:id`，并记录 API 返回的正文、作者 ID、创建时间和原帖 ID。

## 一次性发布流程

1. 从运行记录读取候选、规范化 URL、原帖 ID、预期账号和幂等键。
2. 调用 `/2/users/me` 核验账号；读取本人近期时间线和当天发布记录，执行最小间隔、每日上限、重复事件和重复正文门禁。
3. 重新计算正文长度和链接/媒体约束；引用帖确认 `quote_tweet_id` 与候选原帖一致。
4. 只提交一次 `POST /2/tweets`。成功响应必须包含 `data.id`；用该 ID 形成 `https://x.com/<handle>/status/<id>`。
5. 查询并核对已发布对象，确认作者、正文、引用对象与运行记录一致，再写入成功状态。

## 错误和限流

- 401/403：停止并报告认证、权限、账号或套餐问题；不读取或输出任何凭证。
- 429、每日发布上限、频率限制或类似平台限流：停止提交并按配置暂停 24 小时，只采集、不重试。
- 网络超时、5xx 或响应无法判断：状态记为 `publish_unknown`，保留候选和幂等键，不重试、不推进游标。
- API 不支持当前套餐的引用帖：不要回退到浏览器脚本；按策略跳过，或在明确允许时发布不带 `quote_tweet_id` 的普通原创帖并在内部保留原帖链接。

## 明确禁止

- 不得使用 Playwright、Chrome、Safari、DOM 点击、页面注入或其他脚本化 x.com 网页自动化来发帖。
- 不得为了绕过验证、限流或套餐限制切换账号、重复提交或模拟真人操作。
- 不得在正文中自动添加“来源：”标签；X 原帖链接通过 `quote_tweet_id` 保留，网页来源链接只写入内部证据记录。

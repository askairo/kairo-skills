---
name: media-x
description: X / Twitter 平台子技能：把已核验素材改写为适合 X 推荐分发和关注转化的单帖、Thread 或引用帖，并通过受控登录会话发布和核验结果。Use when Codex needs to write, optimize, publish, or review content specifically for X. Do not use for account credentials or unverified claims.
---

# Media X

本技能只处理 X 平台化工作。素材发现、事实核验、账号配置和跨平台调度由 `media-ops` 总控负责；本技能接收证据卡、账号定位、受众和发布边界。

## Read references

- 增长策略与推荐机制：读取 [x-growth.md](references/x-growth.md)
- 通用来源评分：需要评分或核验时读取 [source-quality.md](../media-ops/references/source-quality.md)
- 浏览器发布：涉及 Chrome 时遵守 `chrome:control-chrome` 技能的受控会话和低自由度发布流程。

## Adapt content

- 默认结构为“具体事实钩子 → 一个关键证据 → 原创解释 → 具体讨论问题”。
- 单帖只承载一个核心信息；长链路拆成 Thread，首帖必须独立成立。
- 翻译、摘要和引用原帖不算原创增量；增加事实边界、技术解释、实际影响或可执行判断。
- 首句不使用空泛的“震撼”“速看”等词；不夸大、不制造焦虑、不把猜测写成事实。
- 关注转化来自稳定栏目和明确账号承诺，不使用机械“点赞关注”。
- 外链服务于证据，正文即使不点开链接也应有完整信息；引用帖优先保留原作者和原帖媒体。
- 配图/视频必须帮助理解或增加停留价值，且来源、版权和归属清楚；不要上传与内容无关的装饰图。

## Growth review

发布前检查：陌生用户能否理解首句、正文是否只有一个核心信息、是否有保存价值、是否有自然回复入口、是否能体现关注后的持续价值、字数/媒体/链接/标签是否合规。

发布后记录曝光、回复率、转发率、收藏率、链接点击、主页访问、关注转化和负向反馈。回复评论时补充证据和上下文，不复制粘贴或批量骚扰。

## Publish

1. 核对当前登录身份与配置 handle 一致。
2. 创建草稿后重新读取正文、受众、引用对象、媒体和发布按钮。
3. 最终发布按钮只点击一次，等待明确成功提示、帖子 URL 或时间线新内容。
4. X 引用帖必须确认引用的是预期原帖，且原帖媒体在编辑器中仍显示；不得重复上传同一官方媒体。

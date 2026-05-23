---
name: hexo-push
description: 读取 Clippings 目录的最新文章，转换为 Hexo 博客文档，自动 git push 并 hexo deploy 发布。支持发布前预览、Agent 确认分类标签、去重更新和自动部署重试。
---

# Hexo Clipping 发布工具

自动将 Clippings 目录中的最新文章转换为 Hexo 博客格式并发布。

## 职责边界

- **Agent 负责内容理解**：阅读全文，判断是否需要翻译、润色、精简，生成自然的标题、摘要、分类和 tags。
- **脚本负责机械发布**：读取 Markdown、生成 Hexo front matter、去重更新、写入文件、执行 git 和 Hexo deploy。
- 用户不需要记脚本参数。用户用自然语言确认分类、标签和发布意图；Agent 将确认结果转换为脚本内部参数。
- `D:\private-vs-space\kimi-skills\hexo-push` 是长期维护源；Codex/Kimi 等用户目录里的 skill 只是同步安装目标。

## 推荐交互流程

1. 读取指定 Clippings 目录的最新文章。
2. 解析 front matter 和正文。
3. 如果文章仍有英文残留、翻译腔、过长或结构松散，Agent 先生成一版发布预览稿给用户确认。
4. Agent 推荐分类和 tags，用户可以自然语言修改，例如“分类改成杂谈，tags 用第一组”。
5. 用户确认发布后，Agent 使用脚本发布，并确保最终生成文件的 `categories` 和 `tags` 与用户确认一致。
6. 发布完成后检查生成文件、git commit/push、hexo deploy 结果。

## 分类和标签规则

可用分类默认是：
- `AI`
- `工作`
- `健康`
- `杂谈`

分类和 tags 优先由 Agent 基于文章语义判断，脚本关键词分类只作为兜底。对于跨主题文章，应以文章主旨而不是个别关键词决定分类。

示例：一篇讨论日本企业制度、制造业和半导体供应链的文章，虽然出现 AI、半导体关键词，但主旨是企业制度和商业观察时，更适合 `杂谈`。

## 发布前预览

当用户要求“先预览”“先输出到对话框”“确认后再发布”时：

1. Agent 不应直接运行完整发布流程。
2. Agent 应先输出精简后的 Markdown 预览，包括标题、摘要、正文结构、分类和 tags。
3. 用户确认后，Agent 再调用脚本。
4. 若需要使用加工稿发布，优先将加工稿写入临时 Markdown 文件，通过 `--content-file` 交给脚本，不要覆盖原始 Clippings。

## 脚本能力（Agent 内部使用）

用户不需要直接输入这些参数；它们是 Agent 将自然语言意图落到脚本的内部接口。

```powershell
python C:\Users\admin\.codex\skills\hexo-push\scripts\publish.py <Clippings目录> `
  --category 杂谈 `
  --tags-file <tags临时文件> `
  --description-file <摘要临时文件> `
  --content-file <加工稿临时文件>
```

常用参数：

- `--description-file <path>`：传入 Agent 生成或确认过的摘要，避免 Windows 中文长参数截断。
- `--category <name>`：传入用户确认的分类。由 Agent 使用，不要求用户手写。
- `--tags <a,b,c>` / `--tags-file <path>`：传入用户确认的 tags。推荐用文件，避免转义问题。
- `--content-file <path>`：使用 Agent 生成的完整 Markdown 加工稿发布，保留原始 clipping 不变。
- `--dry-run`：生成并打印发布内容，不写文件、不 git、不 deploy。
- `--skip-git`：只写入文件，不提交推送。
- `--skip-deploy`：提交推送源码，但不执行 Hexo deploy。
- `--deploy-retries <n>`：Hexo deploy 失败时重试次数，默认 2。

## 默认路径

默认 Clippings 目录：

```text
D:\private-vs-space\hexo-blog\source\_posts\Clippings
```

路径优先级：命令行参数 > 环境变量 `HEXO_CLIPPINGS_DIR` > 自动推断当前 Hexo 根目录 > 默认路径。

## Hexo 文档格式

```markdown
---
title: "文章标题"
date: 2026-04-02 13:58:00
tags:
  - tag1
  - tag2
categories:
  - 杂谈
source: "原文链接"
author: "原作者"
created: "2026-04-02"
---

摘要

<!--more-->

正文
```

## 去重机制

发布前扫描 `source/_posts/` 下已发布文章，排除 `Clippings`：

1. 优先按 `source` URL 匹配。
2. 其次按 `title` 匹配。
3. 如果找到多篇重复文章，保留最早发布的一篇，删除其他重复文章。
4. 更新文章使用 `update:` commit 前缀，新文章使用 `add:` commit 前缀。

## 发布后校验

发布完成后，Agent 应检查：

- 最终生成文件路径。
- front matter 中 `categories` 是否等于用户确认分类。
- `tags` 是否完整保留用户确认结果。
- `git commit` 和 `git push` 是否成功。
- `hexo deploy` 是否成功；若网络重置或超时，脚本会自动重试，仍失败时说明手动命令。

## 注意事项

- 如果文章需要翻译、润色或精简，优先使用 `--content-file` 发布加工稿，避免改动原始 Clippings。
- 如果用户明确要求保留原文，则不要改写正文，只生成摘要和 Hexo front matter。
- 确保博客仓库已配置 git remote 和 Hexo deploy。
- 脚本只使用 Python 标准库，避免在不同 Agent 环境安装额外依赖。

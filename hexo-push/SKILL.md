---
name: hexo-push
description: 读取 Clippings 目录的最新文章，转换为 Hexo 博客文档，自动 git push 并 hexo deploy 发布。支持用户输入源目录，自动处理文件名冲突。
---

# Hexo Clipping 发布工具

自动将 Clippings 目录中的最新文章转换为 Hexo 博客格式并发布。

## 功能

1. 读取指定 Clippings 目录的最新一篇文章
2. **保留原文**：直接使用原标题和正文内容，不做 AI 修改
3. 生成摘要（优先使用 description 或 Agent 生成的 excerpt，否则兜底取正文前 200 字）
4. **智能分类**：根据文章内容自动从已有分类中选择（`AI`、`工作`、`健康`、`杂谈`），不再自动新增分类
5. 生成 Hexo 格式的 Markdown 文档
6. **智能去重更新**：发布前扫描已发布文章，若 `source URL` 或 `title` 相同，则覆盖更新**最早发布**的那篇，并**自动删除其他所有重复文章**
7. 自动处理文件名冲突：若当天已存在文章，则自动往后推一天（如 `20260403.md` → `20260404.md`），确保每天只发布一篇文章
8. 输出到年份目录（如 2026/20260402.md）
9. 自动执行 git add, commit, push
10. 自动执行 hexo deploy 发布

## 使用方法

### 方式一：Agent 生成摘要后调用脚本（推荐）

当文章没有 `description` 时，Agent 应先阅读全文并生成一段简短的摘要（excerpt，约 100~200 字），**写入临时文件后通过 `--description-file` 参数传给脚本**。

> **为什么用 `--description-file` 而不是 `--description`？**
> - **Windows**：PowerShell/CMD 直接传长中文参数容易出现编码截断（实测 175 字中文被截断为 12 字符）。
> - **macOS/Linux**：虽然 UTF-8 通常正常，但如果摘要包含引号、换行等特殊字符，命令行传参仍可能出错。
> - **通过文件传递可 100% 避免所有平台的参数截断和转义问题。**

**Agent 执行模板（Python，跨平台）：**

```python
import sys
import tempfile
from pathlib import Path

# 加载 publish 模块
sys.path.insert(0, str(Path.home() / '.config' / 'agents' / 'skills' / 'hexo-push' / 'scripts'))
from publish import get_latest_file, parse_front_matter

# 1. 确定 Clippings 目录（可自定义）
clips_dir = Path('source/_posts/Clippings').resolve()  # 自动基于当前工作目录
latest = get_latest_file(str(clips_dir))

# 2. 解析文章
with open(latest, 'r', encoding='utf-8') as f:
    meta = parse_front_matter(f.read())

description = meta.get('description', '').strip()

# 3. 若 description 缺失或太短，Agent 基于全文生成 excerpt
if len(description) <= 10:
    description = "【Agent 基于全文生成的摘要，约 100~200 字】"

# 4. 将摘要写入临时文件，调用发布脚本
with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', suffix='.txt', delete=False) as tmp:
    tmp.write(description)
    tmp_file = tmp.name

import subprocess
subprocess.run([
    sys.executable, str(Path.home() / '.config' / 'agents' / 'skills' / 'hexo-push' / 'scripts' / 'publish.py'),
    str(clips_dir), '--description-file', tmp_file
])
```

完整流程：
1. Agent 读取 `Clippings` 目录最新文章
2. 解析 front matter，若 `description` 缺失或太短（≤10 字符），则基于全文理解生成 excerpt
3. 将摘要写入临时文件，调用脚本并传入 `--description-file`
4. 脚本优先使用传入的 description 作为摘要，其余流程不变

### 方式二：手动执行步骤

1. **获取用户输入的 Clippings 目录路径**
   - 默认：`D:\private-vs-space\hexo-blog\source\_posts\Clippings`
   - 用户可自定义输入

2. **读取最新文章**
   - 获取目录下最后修改的文件

3. **解析文章元数据**
   - 提取 title, source, author, description, tags 等

4. **生成摘要（excerpt）**
   - 若原文 front matter 中有 `description`，直接使用
   - 若没有，由 Agent 理解全文后生成一段简短、准确的摘要（约 100~200 字）
   - 将摘要写入临时文件，通过 `--description-file` 参数传给 `publish.py`（跨平台最稳，避免命令行编码截断和特殊字符转义问题）

5. **智能分类**
   - 根据标题、正文、标签自动匹配已有分类（`AI`、`工作`、`健康`、`杂谈`）
   - 若无法自动确定，会交互式提示用户从 4 个分类中选择，或输入新分类

6. **生成 Hexo 文档**
   - **智能去重**：先扫描 `source/_posts/` 下所有已发布文章
     - 优先按 `source URL` 匹配（最精确）
     - 其次按 `title` 匹配
     - 若匹配到多篇重复文章：
       - **保留最早发布的那一篇**（按文件修改时间）
       - **自动删除其他所有重复文章**
       - 覆盖保留的文件，并更新 `date` 为当前时间
   - 若未匹配到，则创建新文件
   - 文件名格式：`yyyyMMdd.md`，若冲突则日期自动往后递增一天
   - 输出目录：`Clippings同目录\yyyy\`
   - 必须包含 `<!--more-->` 分隔符
   - **摘要来源**：优先使用 `--description-file`（或 `--description`）参数传入的 AI 生成摘要，其次使用原文 `description`，最后兜底取正文前 200 字

7. **Git 操作**
   - `git add .`
   - 新建文章：`git commit -m "add: 文章标题"`
   - 更新文章：`git commit -m "update: 文章标题"`
   - `git push`

8. **Hexo 发布**
   - `hexo clean`
   - `hexo deploy`

## Hexo 文档格式

```markdown
---
title: "原文标题"
date: 2026-04-02 13:58:00
tags:
  - tag1
  - tag2
categories:
  - 杂谈
---

摘要（优先使用 description 或 Agent 生成的 excerpt，否则兜底取正文前 200 字）

<!--more-->

原文正文内容（完整保留）
```

## 可用分类

发布文章时，`categories` 只能从以下 4 个已有分类中选择：
- `AI`
- `工作`
- `健康`
- `杂谈`

如果文章内容实在无法归入以上分类，脚本会提示用户手动选择或输入新分类。

## 注意事项

- **工作目录**：脚本会自动检测当前工作目录是否为 Hexo 博客根目录（包含 `source/_posts`），若匹配则自动推断 `Clippings` 路径。建议在博客根目录执行。
- **路径优先级**：命令行参数 > 环境变量 `HEXO_CLIPPINGS_DIR` > 自动推断当前工作目录 > 硬编码默认值
- 确保已配置好 git remote
- 确保已配置好 hexo deploy 配置

## 去重机制说明

当你修复一篇已发布的文章并重新推送时，工具会自动识别并更新原文章，而不是创建一篇新的：

1. **source URL 优先**：如果原文和旧文章都有 `source` 字段（原文链接），且 URL 完全一致，则认为是同一篇文章
2. **title 兜底**：如果没有 `source` 字段，或 source 为空，则比较 `title`，标题完全一致时认为是同一篇文章
3. **处理多篇重复**：如果系统中存在多篇重复文章（比如之前重复发布了多次）：
   - **保留最早的那一篇**（按文件修改时间判断）
   - **自动删除其他所有重复的文章**
   - 覆盖更新保留的那一篇，同时更新 front matter 中的 `date` 为当前时间
4. **Git 标识**：更新时会使用 `update:` 前缀的 commit message，方便在 git 历史中区分新建和修改

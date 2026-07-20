---
name: dialogue-refine
description: 将 AI 对话记录提炼、脱敏并重构为结构化的 Hexo 博客加工稿。用于从对话生成博客文章、隐藏业务敏感细节、依据用户本机 blogRoot 定位素材，并将临时加工稿安全交给 hexo-push 发布。
---

# Dialogue Refine - AI 对话文章提炼工具

将发散的 AI 对话记录转换为结构清晰、主题集中、格式规范的 Hexo 博客文章。

## 功能

1. **读取对话记录**：从指定目录读取 AI 对话原始文本
2. **主题聚焦**：识别核心主题，过滤与主题无关的内容
3. **结构重组**：将发散的对话整理为条理清晰的文章结构
4. **内容提炼**：保留有价值观点，去除重复和冗余表达
5. **格式规范化**：
   - 转换为标准 Markdown 格式
   - 添加适当的标题层级（H1/H2/H3）
   - 优化代码块、列表、引用等格式
   - 生成符合 Hexo 要求的 front matter
6. **智能分类**：自动从已有分类中选择（`AI`、`工作`、`健康`、`杂谈`）
7. **安全输出**：加工稿默认写入系统临时目录，正式文章只由 `hexo-push` 写入配置博客

> **注意**：本工具仅负责文章提炼和格式化。不要在当前业务项目中保存博客加工稿；发布操作交给 `hexo-push`。

## 路径与配置边界

- `blogRoot` 是博客领域共享的机器配置，只保存在 `<AGENT_HOME>/local-config/blog/config.json`。
- 首次使用且无法自动识别 Hexo 根目录时，先询问用户，再写入上述唯一配置文件。
- 不读取工作目录、Skill 目录、隐藏点文件、通用用户配置目录或环境变量中的旧配置，不提供迁移回退。
- 技能固定使用 `<blogRoot>/source/_posts` 作为博客文章根目录；其下的 `Dialogues`、`Clippings` 和年份目录属于技能规范，不需要用户逐项配置。
- 加工稿默认写入系统临时目录。显式输出只允许位于系统临时目录或 `<blogRoot>/source/_posts`，禁止写入无关业务项目。
- 发布完成后删除不再需要的临时加工稿。

## 工作流程

### 阶段一：对话分析（Agent 执行）

1. **读取对话文件**
   - 获取最新的对话记录文件
   - 支持 `.md`、`.txt` 格式
   - 博客根目录优先级：自然语言/`--blog-root` > 用户本地配置 > 从当前 Hexo 目录自动发现
   - 对话输入可由显式文件或目录指定；未指定时依次检查 `<blogRoot>/source/_posts/Dialogues` 和 `Clippings`

2. **分析对话内容**
   - 识别核心主题和讨论目标
   - 标记与主题相关的关键内容
   - 识别可删除的闲聊、重复、跑题内容

3. **设计文章结构**
   - 确定文章标题
   - 规划章节结构（引言、正文、结论）
   - 设计内容流转逻辑

4. **内容重构**
   - 将对话转换为第三人称叙述
   - 合并相似观点，去除重复
   - 补充过渡语句，确保逻辑连贯
   - 优化表达方式，提升可读性

### 阶段二：生成 Hexo 文章（脚本执行）

5. **生成 front matter**
   - title: 提炼后的标题
   - date: 当前时间
   - tags: 根据内容自动提取
   - categories: 自动分类

6. **格式规范化**
   - 标准化 Markdown 语法
   - 优化代码块语言和格式
   - 调整图片、链接等引用
   - 添加 `<!--more-->` 分隔符

7. **输出加工稿**
   - 文件名格式：`yyyyMMdd-refined.md`
   - 默认输出：系统临时目录下的 `dialogue-refine` 子目录
   - 正式文章路径由 `hexo-push` 生成，不由当前工作目录决定

> 生成的文件可直接使用 `hexo-push` skill 进行发布。

## 输入格式要求

对话记录文件应包含以下信息（可选）：

```markdown
---
topic: 讨论主题（可选）
tags: [标签1, 标签2]（可选）
category: 预设分类（可选）
---

# 用户
对话内容...

# AI
回复内容...

# 用户
...
```

或直接提供纯对话文本，Agent 将自动分析。

## 使用方法

### 方式一：交互式提炼（推荐）

Agent 先分析对话，与用户确认后再生成文章：

```python
import sys
import tempfile
from pathlib import Path

# 加载 refine 模块
sys.path.insert(0, str(Path('<AGENT_HOME>') / 'skills' / 'dialogue-refine' / 'scripts'))
from refine import get_latest_dialogue, parse_dialogue

# 1. 从用户本地配置解析 <blogRoot>，再定位对话目录
dialogues_dir = Path('<blogRoot>') / 'source' / '_posts' / 'Dialogues'

# 2. 读取最新对话文件
latest = get_latest_dialogue(str(dialogues_dir))

# 3. 解析对话
with open(latest, 'r', encoding='utf-8') as f:
    meta = parse_dialogue(f.read())

# 4. Agent 分析对话，提炼内容，生成结构化文章
# ...

# 5. 将提炼后的内容写入临时文件
refined_content = """---
title: "提炼后的标题"
date: 2026-04-09 12:00:00
tags:
  - 标签1
categories:
  - 分类
---

摘要内容...

<!--more-->

正文内容...
"""

with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', suffix='.md', delete=False) as tmp:
    tmp.write(refined_content)
    tmp_file = tmp.name

# 6. 调用脚本生成最终文件
import subprocess
subprocess.run([
    sys.executable, 
    str(Path.home() / '.config' / 'agents' / 'skills' / 'dialogue-refine' / 'scripts' / 'refine.py'),
    tmp_file,
    '--output-dir', str(Path(dialogues_dir))
])
```

### 方式二：命令行使用

```bash
# 使用配置文件或自动发现的目录
python scripts/refine.py

# 或指定具体文件
python scripts/refine.py <dialogue_file> [options]

# 或指定目录
python scripts/refine.py --dialogue-dir <dialogues_dir>
```

参数说明：
- `dialogue_file`: 对话记录文件路径（可选，默认使用配置文件、自动发现或最新文件）
- `--dialogue-dir <dir>`: 指定对话记录目录
- `--title <title>`: 指定文章标题
- `--category <cat>`: 指定分类
- `--tags <tag1,tag2>`: 指定标签
- `--summary <summary>`: 指定文章摘要
- `--output-dir <dir>`: 指定输出目录；仅允许系统临时目录或 `<blogRoot>/source/_posts`
- `--blog-root <dir>`: 显式指定 Hexo 博客根目录
- `--agent-home <dir>`: 从源码目录运行时显式指定当前 Agent Home；安装后可自动确定
- `--save-config`: 将已校验的 `blogRoot` 写入用户目录配置

### 配置文件

与 `hexo-push` 共用唯一配置文件：

```text
<AGENT_HOME>/local-config/blog/config.json
```

示例：

```json
{
  "version": 1,
  "blogRoot": "<absolute-hexo-blog-root>"
}
```

首次使用示例：

```powershell
python scripts/refine.py --agent-home <agent-home> --blog-root <absolute-hexo-blog-root> --save-config
```

脚本将配置保存在当前 Agent Home，不得提交到 Skill 或博客仓库。旧配置位置和旧字段不读取、不迁移。

## 文章结构模板

提炼后的文章建议采用以下结构：

```markdown
---
title: "文章标题"
date: 2026-04-08 12:00:00
tags:
  - 标签1
  - 标签2
categories:
  - 分类
---

简要摘要（100-200字），概括文章核心内容。

<!--more-->

## 引言

背景介绍、问题提出或核心观点概述。

## 主要内容

### 子主题一

详细阐述...

### 子主题二

详细阐述...

## 实践建议/总结

可操作的结论或核心要点总结。

## 结语

升华或延伸思考。
```

## 内容处理原则

### 保留内容
- ✅ 核心观点和有价值的见解
- ✅ 重要的技术细节和代码示例
- ✅ 关键的问题分析和解决方案
- ✅ 有启发性的类比和例子

### 删除内容
- ❌ 开场白和结束语（如"你好"、"谢谢"）
- ❌ 重复表达和冗余解释
- ❌ 与主题无关的闲聊
- ❌ 过于口语化的填充词
- ❌ 未完成的思路和跑题内容
- ❌ 真实项目名、业务模块名、类名、任务名、服务器地址、账号密钥和生产参数

生产问题复盘默认使用通用问题、抽象角色和符号参数替代敏感细节；除非用户明确授权，不粘贴业务代码。

### 转换方式
- 对话形式 → 第三人称叙述
- 问答形式 → 条理化的论述
- 发散讨论 → 聚焦主题的结构
- 口语表达 → 书面化、专业化表达

## 可用分类

- `AI`：人工智能、机器学习、大模型等相关内容
- `工作`：编程、架构、职场、效率等相关内容
- `健康`：健身、饮食、心理、医疗等相关内容
- `杂谈`：生活、读书、随笔、社会观察等内容

## 注意事项

1. **主题聚焦**：一篇文章只围绕一个核心主题展开
2. **逻辑连贯**：确保段落间有清晰的逻辑关系
3. **格式规范**：遵循 Markdown 和 Hexo 格式要求
4. **读者友好**：考虑目标读者的背景知识和阅读体验
5. **引用标注**：如涉及外部资料，需添加引用来源

## 完整使用流程示例

```
1. 准备 AI 对话记录，通过显式文件传入，或放到 `<blogRoot>/source/_posts/Dialogues`

2. 运行 dialogue-refine skill
   - 读取最新对话文件
   - Agent 分析并提炼内容
   - 生成结构化文章
   - 输出：系统临时目录中的 `20260409-refined.md`

3. 使用 hexo-push skill 发布
   - 通过 `--content-file` 将临时加工稿交给 `hexo-push`
   - `hexo-push` 将正式文章写入 `<blogRoot>/source/_posts/<yyyy>/<yyyyMMdd>.md`
```

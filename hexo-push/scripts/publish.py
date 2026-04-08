#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hexo Clipping 发布工具
读取 Clippings 目录的最新文章，转换为 Hexo 博客格式并发布
"""

import os
import sys
import re
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

# Windows 终端中文输出修复
try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except AttributeError:
    pass


def get_latest_file(clippings_dir: str) -> Path:
    """获取 Clippings 目录下最新修改的文件"""
    clips_path = Path(clippings_dir)
    if not clips_path.exists():
        raise FileNotFoundError(f"目录不存在: {clippings_dir}")
    
    files = [f for f in clips_path.iterdir() if f.is_file() and f.suffix == '.md']
    if not files:
        raise FileNotFoundError(f"目录中没有 Markdown 文件: {clippings_dir}")
    
    # 按修改时间排序，取最新的
    latest = max(files, key=lambda f: f.stat().st_mtime)
    return latest


def parse_front_matter(content: str) -> dict:
    """解析文章的前置元数据"""
    metadata = {
        'title': '',
        'source': '',
        'author': '',
        'description': '',
        'tags': [],
        'created': '',
        'body': content
    }
    
    # 匹配 YAML front matter
    pattern = r'^---\s*\n(.*?)\n---\s*\n(.*)$'
    match = re.match(pattern, content, re.DOTALL)
    
    if match:
        front_matter = match.group(1)
        metadata['body'] = match.group(2).strip()
        
        # 解析各个字段
        title_match = re.search(r'title:\s*["\']?(.*?)["\']?\s*$', front_matter, re.MULTILINE)
        if title_match:
            metadata['title'] = title_match.group(1).strip('"\'')
        
        source_match = re.search(r'source:\s*["\']?(.*?)["\']?\s*$', front_matter, re.MULTILINE)
        if source_match:
            metadata['source'] = source_match.group(1).strip('"\'')
        
        author_match = re.search(r'author:\s*["\']?(.*?)["\']?\s*$', front_matter, re.MULTILINE)
        if author_match:
            author_val = author_match.group(1).strip('"\'')
            # 处理 YAML 列表格式: "- [[Thariq]]"
            if author_val.startswith('- '):
                author_val = author_val[2:].strip('"\'')
            metadata['author'] = author_val
        
        desc_match = re.search(r'description:\s*["\']?(.*?)["\']?\s*$', front_matter, re.MULTILINE)
        if desc_match:
            metadata['description'] = desc_match.group(1).strip('"\'')
        
        # 解析 tags
        tags_match = re.search(r'tags:\s*\n((?:\s+-\s*.*?\n)*)', front_matter)
        if tags_match:
            tags_text = tags_match.group(1)
            metadata['tags'] = re.findall(r'-\s*["\']?(.*?)["\']?\s*$', tags_text, re.MULTILINE)
        
        created_match = re.search(r'created:\s*(\d{4}-\d{2}-\d{2})', front_matter)
        if created_match:
            metadata['created'] = created_match.group(1)
    else:
        # 没有 front matter，使用第一行作为标题
        lines = content.strip().split('\n')
        if lines:
            metadata['title'] = lines[0].strip('# ')
            metadata['body'] = content
    
    return metadata


def clean_unicode_chars(text: str) -> str:
    """清理 Unicode 特殊字符"""
    replacements = {
        '\u2022': '-',
        '\u25cf': '-',
        '\u2014': '-',
        '\u2013': '-',
        '\u2018': "'",
        '\u2019': "'",
        '\u201c': '"',
        '\u201d': '"',
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


ALLOWED_CATEGORIES = ["AI", "工作", "健康", "杂谈"]


def classify_article(title: str, body: str, tags: list) -> str:
    """根据文章内容自动分类，只允许使用已有的分类"""
    text = (title + " " + body + " " + " ".join(tags)).lower()
    
    # 定义关键词映射
    keywords = {
        "AI": [
            "人工智能", "机器学习", "深度学习", "llm", "大模型", "chatgpt", "gpt", "claude",
            "神经网络", "算法", "nvidia", "gpu", "芯片", "半导体", "sambaNova", "intel",
            "openai", "agi", "aigc", "生成式", "transformer", "模型训练", "推理",
            "python", "tensorflow", "pytorch", "数据科学", "自动驾驶", "机器人"
        ],
        "工作": [
            "编程", "代码", "开发", "架构", "cleancode", "命名规范", "重构",
            "职场", "面试", "管理", "效率", "工具", "git", "docker", "kubernetes",
            "微服务", "前端", "后端", "全栈", "devops", "敏捷", "scrum", "项目管理",
            "沟通", "汇报", "晋升", "简历", "offer", "薪资", "远程工作", "副业"
        ],
        "健康": [
            "健身", "运动", "跑步", "瑜伽", "游泳", "饮食", "营养", "减肥", "增肌",
            "睡眠", "失眠", "心理", "焦虑", "抑郁", "冥想", "养生", "医疗", "疾病",
            "体检", "疫苗", "免疫力", "慢性病", "颈椎", "腰椎", "眼睛", "视力"
        ],
        "杂谈": [
            "生活", "随笔", "感悟", "读书", "阅读", "书评", "电影", "影评", "音乐",
            "旅行", "旅游", "摄影", "美食", "社会", "新闻", "评论", "热点", "八卦",
            "历史", "文化", "哲学", "经济", "金融", "投资", "理财", "房产", "汽车"
        ]
    }
    
    scores = {}
    for cat, words in keywords.items():
        score = sum(1 for word in words if word.lower() in text)
        if score > 0:
            scores[cat] = score
    
    if scores:
        # 返回得分最高的分类
        return max(scores, key=scores.get)
    
    return None


def prompt_for_category() -> str:
    """当自动分类无法确定时，交互式询问用户"""
    print("\n  [INFO] 无法自动确定文章分类，请从以下分类中选择：")
    for i, cat in enumerate(ALLOWED_CATEGORIES, 1):
        print(f"    {i}. {cat}")
    print(f"    0. 新增分类")
    
    while True:
        try:
            choice = input("  请输入编号 (1-4 或 0): ").strip()
            idx = int(choice)
            if 1 <= idx <= len(ALLOWED_CATEGORIES):
                return ALLOWED_CATEGORIES[idx - 1]
            elif idx == 0:
                new_cat = input("  请输入新分类名称: ").strip()
                if new_cat:
                    return new_cat
                print("  [WARN] 分类名称不能为空")
            else:
                print("  [WARN] 无效的选择，请重新输入")
        except ValueError:
            print("  [WARN] 请输入数字")


def generate_summary(body: str, description: str = '', max_length: int = 200) -> str:
    """生成摘要
    优先使用传入的 description（可由 AI 生成），否则取 body 前 max_length 字符作为兜底
    """
    if description and len(description.strip()) > 10:
        return description.strip()
    
    # 清理 body 中的 Markdown 标记
    text = re.sub(r'[#*`\[\]\(\)!]', '', body)
    text = text.replace('\n', ' ').strip()
    
    if len(text) > max_length:
        return text[:max_length].strip() + '...'
    return text


def clean_wiki_links(text: str) -> str:
    """清理 Obsidian/维基百科风格的双括号链接 [[文本]] -> 文本"""
    return re.sub(r'\[\[(.*?)\]\]', r'\1', text)


def generate_attribution(source: str, author: str) -> str:
    """生成来源署名"""
    parts = []
    if source:
        parts.append(f"来源：{source}")
    if author:
        author = clean_wiki_links(author)
        parts.append(f"原作者：{author}")
    
    if parts:
        return "\n\n---\n\n> " + " | ".join(parts)
    return ""


def generate_hexo_content(metadata: dict, target_date: datetime = None, category: str = None) -> str:
    """生成 Hexo 格式的 Markdown 内容"""
    if target_date is None:
        target_date = datetime.now()
    date_str = target_date.strftime('%Y-%m-%d %H:%M:%S')
    
    title = metadata.get('title', 'No Title')
    body = metadata.get('body', '')
    description = metadata.get('description', '')
    source = metadata.get('source', '')
    author = metadata.get('author', '')
    created = metadata.get('created', '')
    
    # 生成摘要（优先使用 metadata 中的 description，可能是命令行传入的 AI 生成摘要）
    summary = generate_summary(body, description)
    
    # 清理 Unicode 字符
    title = clean_unicode_chars(title)
    summary = clean_unicode_chars(summary)
    body = clean_unicode_chars(body)
    
    # 处理 tags
    tags_yaml = ''
    if metadata.get('tags'):
        tags_yaml = '\n'.join([f'  - {tag}' for tag in metadata['tags']])
    else:
        tags_yaml = '  - clippings'
    
    # 清理维基链接
    author = clean_wiki_links(author)
    
    # 构建 front matter 中的额外字段
    extra_fields = []
    if source:
        extra_fields.append(f'source: "{source}"')
    if author:
        extra_fields.append(f'author: "{author}"')
    if created:
        extra_fields.append(f'created: "{created}"')
    
    extra_yaml = ''
    if extra_fields:
        extra_yaml = '\n' + '\n'.join(extra_fields)
    
    # 生成来源署名
    attribution = generate_attribution(source, author)
    
    # 处理 title 中的引号，避免 YAML 解析问题
    # 如果 title 包含双引号，使用单引号包裹；否则使用双引号
    if '"' in title:
        yaml_title = f"'{title}'"
    else:
        yaml_title = f'"{title}"'
    
    # 构建 Hexo front matter
    hexo_content = f"""---
title: {yaml_title}
date: {date_str}
tags:
{tags_yaml}
categories:
  - {category}{extra_yaml}
---

{summary}

<!--more-->

{body}{attribution}
"""
    
    return hexo_content


def find_existing_posts(posts_dir: Path, title: str, source: str) -> tuple:
    """
    在已发布的文章中查找相同文章，优先匹配 source URL，其次匹配 title
    返回: (最早的一篇, 其他重复的列表)
    """
    if not posts_dir.exists():
        return None, []
    
    matched_files = []
    
    # 清理 title 中的 Unicode 特殊字符（如中文引号转英文引号），确保匹配一致性
    title_cleaned = clean_unicode_chars(title)
    
    # 遍历所有已发布的 md 文件（排除 Clippings 源目录）
    for md_file in posts_dir.rglob('*.md'):
        # 跳过 Clippings 目录及其子目录
        if 'Clippings' in md_file.parts:
            continue
        
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            old_meta = parse_front_matter(content)
            old_title = old_meta.get('title', '').strip()
            old_source = old_meta.get('source', '').strip()
            
            # 清理已发布文章的 title，确保比较时格式一致
            old_title_cleaned = clean_unicode_chars(old_title)
            
            is_match = False
            # 优先用 source URL 匹配（最精确）
            if source and old_source and source == old_source:
                is_match = True
            # 其次用 title 匹配（使用清理后的 title）
            elif title_cleaned and old_title_cleaned and title_cleaned == old_title_cleaned:
                is_match = True
            
            if is_match:
                # 获取文件创建/修改时间用于排序
                stat = md_file.stat()
                matched_files.append((md_file, stat.st_mtime))
                
        except Exception:
            continue
    
    if not matched_files:
        return None, []
    
    # 按修改时间排序，最早的排在前面
    matched_files.sort(key=lambda x: x[1])
    
    earliest = matched_files[0][0]
    duplicates = [f[0] for f in matched_files[1:]]
    
    return earliest, duplicates


def get_output_filename(posts_path: Path, now: datetime = None) -> tuple:
    """生成输出文件名，如果当天已存在则自动往后推一天，同时返回对应的完整日期时间"""
    if now is None:
        now = datetime.now()
    current_date = now.date()
    
    while True:
        year_str = current_date.strftime('%Y')
        output_dir = posts_path / year_str
        output_dir.mkdir(exist_ok=True)
        filename = current_date.strftime('%Y%m%d') + '.md'
        output_path = output_dir / filename
        if not output_path.exists():
            target_datetime = datetime.combine(current_date, now.time())
            return output_path, target_datetime
        current_date += timedelta(days=1)


def run_command(cmd: list, cwd: str = None) -> tuple:
    """执行命令并返回结果"""
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            encoding='utf-8',
            shell=True
        )
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return -1, '', str(e)


def get_default_clippings_path() -> str:
    """智能推断默认 Clippings 路径
    若当前目录是 Hexo 博客根目录（包含 source/_posts），则自动拼接；
    否则返回一个通用的硬编码默认值。
    """
    cwd = Path.cwd()
    # 检查当前目录或其父目录是否包含 source/_posts
    check_dirs = [cwd] + list(cwd.parents)
    for d in check_dirs:
        candidate = d / 'source' / '_posts' / 'Clippings'
        if candidate.exists():
            return str(candidate)
    # 兜底：兼容旧用户的硬编码路径
    return r"D:\private-vs-space\hexo-blog\source\_posts\Clippings"


def main():
    # 获取 Clippings 目录路径（优先级：命令行参数 > 环境变量 > 自动推断默认值）
    default_path = get_default_clippings_path()
    env_path = os.environ.get("HEXO_CLIPPINGS_DIR")
    
    # 支持通过 --description 或 --description-file 参数传入 AI 生成的摘要
    custom_description = ''
    description_file = ''
    argv = sys.argv[1:]
    skip_indices = set()
    i = 0
    while i < len(argv):
        if argv[i] == '--description' and i + 1 < len(argv):
            custom_description = argv[i + 1]
            skip_indices.update({i, i + 1})
            i += 2
        elif argv[i].startswith('--description='):
            custom_description = argv[i].split('=', 1)[1]
            skip_indices.add(i)
            i += 1
        elif argv[i] == '--description-file' and i + 1 < len(argv):
            description_file = argv[i + 1]
            skip_indices.update({i, i + 1})
            i += 2
        elif argv[i].startswith('--description-file='):
            description_file = argv[i].split('=', 1)[1]
            skip_indices.add(i)
            i += 1
        else:
            i += 1
    
    # 若指定了 description-file，从文件读取（推荐，避免 Windows 命令行中文截断）
    if description_file and not custom_description:
        try:
            with open(description_file, 'r', encoding='utf-8') as f:
                custom_description = f.read().strip()
        except Exception as e:
            print(f"[WARN] Failed to read description file: {e}")
    
    positional_args = [argv[i] for i in range(len(argv)) if i not in skip_indices and not argv[i].startswith('--')]
    
    if positional_args:
        clippings_dir = positional_args[0]
        source = "command line argument"
    elif env_path:
        clippings_dir = env_path
        source = "environment variable HEXO_CLIPPINGS_DIR"
    else:
        clippings_dir = default_path
        source = "default hardcoded path"
    
    print(f"Using path from {source}: {clippings_dir}")
    if custom_description:
        print(f"Using custom description ({len(custom_description)} chars)")
    
    # 校验目录是否存在
    if not Path(clippings_dir).exists():
        print(f"\n[ERROR] Clippings directory does not exist: {clippings_dir}")
        print("\nPlease fix this by one of the following methods:")
        print(f"  1. Set environment variable: HEXO_CLIPPINGS_DIR=<your_clippings_path>")
        print(f"  2. Pass path as argument: python publish.py <your_clippings_path>")
        print(f"  3. Create the directory: {clippings_dir}")
        sys.exit(1)
    
    try:
        # 1. 获取最新文件
        print(f"\n[1/7] Reading Clippings directory: {clippings_dir}")
        latest_file = get_latest_file(clippings_dir)
        print(f"  Latest file: {latest_file.name}")
        
        # 2. 读取并解析文件
        print(f"\n[2/7] Parsing file...")
        with open(latest_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        metadata = parse_front_matter(content)
        print(f"  Title: {metadata.get('title', 'No title')[:50]}")
        print(f"  Source: {metadata.get('source', 'N/A')}")
        print(f"  Author: {metadata.get('author', 'N/A')}")
        print(f"  Tags: {', '.join(metadata.get('tags', []))}")
        
        # 3. 确定输出路径和日期
        print(f"\n[3/7] Determining output path...")
        clips_path = Path(clippings_dir)
        posts_path = clips_path.parent
        
        # 查找是否已发布过相同文章（优先 source URL，其次 title）
        title = metadata.get('title', '')
        source = metadata.get('source', '')
        earliest_file, duplicate_files = find_existing_posts(posts_path, title, source)
        
        is_update = False
        now = datetime.now()
        if earliest_file:
            output_file = earliest_file
            is_update = True
            match_by = "source URL" if source else "title"
            print(f"  [INFO] Found existing post by {match_by}: {output_file.name}")
            print(f"  [INFO] Will update existing file instead of creating new one")
            
            # 删除其他重复的文章
            if duplicate_files:
                print(f"  [INFO] Found {len(duplicate_files)} duplicate post(s), removing...")
                for dup_file in duplicate_files:
                    try:
                        dup_file.unlink()
                        print(f"    [DELETED] {dup_file.name}")
                    except Exception as e:
                        print(f"    [WARN] Failed to delete {dup_file.name}: {e}")
            
            # 从文件名解析日期，时间用当前时间
            file_stem = output_file.stem
            file_date = datetime.strptime(file_stem, '%Y%m%d').date()
            target_date = datetime.combine(file_date, now.time())
            output_dir = output_file.parent
        else:
            output_file, target_date = get_output_filename(posts_path, now)
            output_dir = output_file.parent
            print(f"  Output directory: {output_dir}")
            print(f"  Output file: {output_file.name}")
        
        # 4. 自动分类
        print(f"\n[4/7] Classifying article...")
        category = classify_article(
            metadata.get('title', ''),
            metadata.get('body', ''),
            metadata.get('tags', [])
        )
        if category:
            print(f"  [OK] Auto-selected category: {category}")
        else:
            category = prompt_for_category()
            print(f"  [OK] User-selected category: {category}")
        
        # 5. 生成 Hexo 内容
        print(f"\n[5/7] Generating Hexo document...")
        if custom_description:
            metadata['description'] = custom_description
        hexo_content = generate_hexo_content(metadata, target_date, category)
        
        # 写入文件
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(hexo_content)
        action = "updated" if is_update else "generated"
        print(f"  [OK] File {action}")
        
        # 6. Git 操作
        print(f"\n[6/7] Executing Git operations...")
        blog_root = posts_path.parent.parent
        print(f"  Blog root: {blog_root}")
        
        rc, out, err = run_command(['git', 'add', '.'], cwd=str(blog_root))
        if rc != 0:
            print(f"  [WARN] git add: {err}")
        else:
            print(f"  [OK] git add")
        
        title = metadata.get('title', 'New post')
        commit_prefix = "update" if is_update else "add"
        commit_msg = f"{commit_prefix}: {title[:50]}"
        rc, out, err = run_command(['git', 'commit', '-m', commit_msg], cwd=str(blog_root))
        if rc != 0:
            if 'nothing to commit' in err.lower() or 'nothing to commit' in out.lower():
                print(f"  [INFO] Nothing to commit")
            else:
                print(f"  [WARN] git commit: {err}")
        else:
            print(f"  [OK] git commit: {commit_msg}")
        
        rc, out, err = run_command(['git', 'push'], cwd=str(blog_root))
        if rc != 0:
            print(f"  [WARN] git push: {err}")
        else:
            print(f"  [OK] git push")
        
        # 7. Hexo 发布
        print(f"\n[7/7] Executing Hexo deploy...")
        
        rc, out, err = run_command(['hexo', 'clean'], cwd=str(blog_root))
        if rc != 0:
            print(f"  [WARN] hexo clean: {err}")
        else:
            print(f"  [OK] hexo clean")
        
        rc, out, err = run_command(['hexo', 'deploy'], cwd=str(blog_root))
        if rc != 0:
            print(f"  [FAIL] hexo deploy: {err}")
            print(f"\nPlease manually run: cd {blog_root} && hexo deploy")
        else:
            print(f"  [OK] hexo deploy")
        
        print(f"\nDone!")
        action_str = "updated" if is_update else "published"
        print(f"  Article {action_str}: {output_file}")
        print(f"  Title: {metadata.get('title', 'No title')[:50]}")
        
    except FileNotFoundError as e:
        print(f"[ERROR] {e}")
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hexo AI 对话文章提炼工具
将 AI 对话记录转换为结构化的 Hexo 博客文章
"""

import os
import sys
import re
import subprocess
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Tuple, List

# Windows 终端中文输出修复
try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except AttributeError:
    pass


ALLOWED_CATEGORIES = ["AI", "工作", "健康", "杂谈"]


def get_default_dialogues_path() -> str:
    """智能推断默认对话记录路径"""
    cwd = Path.cwd()
    check_dirs = [cwd] + list(cwd.parents)
    for d in check_dirs:
        candidate = d / 'source' / '_posts' / 'Dialogues'
        if candidate.exists():
            return str(candidate)
    return r"D:\private-vs-space\hexo-blog\source\_posts\Dialogues"


def get_latest_dialogue(dialogues_dir: str) -> Path:
    """获取 Dialogues 目录下最新修改的文件"""
    dialogues_path = Path(dialogues_dir)
    if not dialogues_path.exists():
        raise FileNotFoundError(f"目录不存在: {dialogues_dir}")
    
    files = [f for f in dialogues_path.iterdir() if f.is_file() and f.suffix in ['.md', '.txt']]
    if not files:
        raise FileNotFoundError(f"目录中没有对话记录文件: {dialogues_dir}")
    
    latest = max(files, key=lambda f: f.stat().st_mtime)
    return latest


def parse_dialogue(content: str) -> dict:
    """解析对话记录文件"""
    metadata = {
        'topic': '',
        'tags': [],
        'category': '',
        'title': '',
        'dialogue': [],
        'raw': content
    }
    
    # 尝试解析 front matter
    pattern = r'^---\s*\n(.*?)\n---\s*\n(.*)$'
    match = re.match(pattern, content, re.DOTALL)
    
    if match:
        front_matter = match.group(1)
        body = match.group(2)
        
        # 解析 front matter 字段
        topic_match = re.search(r'topic:\s*["\']?(.*?)["\']?\s*$', front_matter, re.MULTILINE)
        if topic_match:
            metadata['topic'] = topic_match.group(1).strip('"\'')
        
        category_match = re.search(r'category:\s*["\']?(.*?)["\']?\s*$', front_matter, re.MULTILINE)
        if category_match:
            metadata['category'] = category_match.group(1).strip('"\'')
        
        tags_match = re.search(r'tags:\s*\[?([^\]]*)\]?', front_matter)
        if tags_match:
            tags_str = tags_match.group(1)
            metadata['tags'] = [t.strip().strip('"\'') for t in tags_str.split(',') if t.strip()]
        
        title_match = re.search(r'title:\s*["\']?(.*?)["\']?\s*$', front_matter, re.MULTILINE)
        if title_match:
            metadata['title'] = title_match.group(1).strip('"\'')
    else:
        body = content
    
    # 解析对话内容
    # 支持 # 用户 / # AI 或 用户：/ AI：格式
    dialogue_pattern = r'(?:^#\s*(用户|AI)|^(用户|AI)[：:])\s*\n?(.*?)(?=(?:^#\s*(用户|AI)|^(用户|AI)[：:])|\Z)'
    matches = re.findall(dialogue_pattern, body, re.MULTILINE | re.DOTALL)
    
    for match in matches:
        speaker = match[0] or match[1]
        text = match[2].strip()
        if text:
            metadata['dialogue'].append({
                'speaker': speaker,
                'text': text
            })
    
    return metadata


def classify_article(title: str, content: str, tags: list) -> str:
    """根据文章内容自动分类"""
    text = (title + " " + content + " " + " ".join(tags)).lower()
    
    keywords = {
        "AI": [
            "人工智能", "机器学习", "深度学习", "llm", "大模型", "chatgpt", "gpt", "claude",
            "神经网络", "算法", "nvidia", "gpu", "芯片", "半导体", "openai", "agi", "aigc"
        ],
        "工作": [
            "编程", "代码", "开发", "架构", "设计模式", "重构", "职场", "面试", "管理",
            "效率", "工具", "git", "docker", "kubernetes", "微服务", "前端", "后端"
        ],
        "健康": [
            "健身", "运动", "跑步", "瑜伽", "游泳", "饮食", "营养", "减肥", "增肌",
            "睡眠", "心理", "焦虑", "冥想", "养生", "医疗"
        ],
        "杂谈": [
            "生活", "随笔", "感悟", "读书", "阅读", "电影", "音乐", "旅行", "摄影",
            "美食", "社会", "新闻", "历史", "文化", "哲学"
        ]
    }
    
    scores = {}
    for cat, words in keywords.items():
        score = sum(1 for word in words if word.lower() in text)
        if score > 0:
            scores[cat] = score
    
    if scores:
        return max(scores, key=scores.get)
    
    return "杂谈"


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


def generate_hexo_content(title: str, content: str, tags: List[str], category: str, 
                          summary: str = '', created: str = '') -> str:
    """生成 Hexo 格式的 Markdown 内容"""
    now = datetime.now()
    date_str = now.strftime('%Y-%m-%d %H:%M:%S')
    
    # 清理 Unicode 字符
    title = clean_unicode_chars(title)
    content = clean_unicode_chars(content)
    summary = clean_unicode_chars(summary)
    
    # 处理 title 引号
    if '"' in title:
        yaml_title = f"'{title}'"
    else:
        yaml_title = f'"{title}"'
    
    # 处理 tags
    if tags:
        tags_yaml = '\n'.join([f'  - {tag}' for tag in tags])
    else:
        tags_yaml = '  - ai-dialogue'
    
    # 构建额外字段
    extra_fields = []
    if created:
        extra_fields.append(f'created: "{created}"')
    
    extra_yaml = '\n' + '\n'.join(extra_fields) if extra_fields else ''
    
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

{content}
"""
    
    return hexo_content


def get_output_filename(posts_path: Path, now: datetime = None) -> Tuple[Path, datetime]:
    """生成输出文件名，如果当天已存在则自动往后推一天"""
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


def run_command(cmd: list, cwd: str = None) -> Tuple[int, str, str]:
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


def main():
    """主函数 - 用于接收已提炼好的内容并生成 Hexo 文章"""
    import argparse
    
    parser = argparse.ArgumentParser(description='将提炼后的 AI 对话内容转换为 Hexo 博客文章')
    parser.add_argument('content_file', help='提炼后的内容文件路径')
    parser.add_argument('--title', help='文章标题')
    parser.add_argument('--category', help='文章分类')
    parser.add_argument('--tags', help='文章标签，逗号分隔')
    parser.add_argument('--summary', help='文章摘要')
    parser.add_argument('--output-dir', help='输出目录（默认：source/_posts）')
    parser.add_argument('--no-deploy', action='store_true', help='不执行 hexo deploy')
    
    args = parser.parse_args()
    
    try:
        # 读取提炼后的内容
        content_path = Path(args.content_file)
        if not content_path.exists():
            print(f"[ERROR] 文件不存在: {content_path}")
            sys.exit(1)
        
        with open(content_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 解析 front matter（如果有）
        metadata = {}
        pattern = r'^---\s*\n(.*?)\n---\s*\n(.*)$'
        match = re.match(pattern, content, re.DOTALL)
        
        if match:
            front_matter = match.group(1)
            body = match.group(2).strip()
            
            title_match = re.search(r'title:\s*["\']?(.*?)["\']?\s*$', front_matter, re.MULTILINE)
            if title_match:
                metadata['title'] = title_match.group(1).strip('"\'')
            
            summary_match = re.search(r'summary:\s*["\']?(.*?)["\']?\s*$', front_matter, re.MULTILINE)
            if summary_match:
                metadata['summary'] = summary_match.group(1).strip('"\'')
            
            category_match = re.search(r'category:\s*["\']?(.*?)["\']?\s*$', front_matter, re.MULTILINE)
            if category_match:
                metadata['category'] = category_match.group(1).strip('"\'')
            
            tags_match = re.search(r'tags:\s*\[?([^\]]*)\]?', front_matter)
            if tags_match:
                tags_str = tags_match.group(1)
                metadata['tags'] = [t.strip().strip('"\'') for t in tags_str.split(',') if t.strip()]
        else:
            body = content
        
        # 使用命令行参数覆盖
        title = args.title or metadata.get('title', 'Untitled')
        summary = args.summary or metadata.get('summary', '')
        category = args.category or metadata.get('category', '')
        tags = args.tags.split(',') if args.tags else metadata.get('tags', [])
        
        # 自动分类
        if not category:
            category = classify_article(title, body, tags)
        
        # 确定输出路径
        if args.output_dir:
            posts_path = Path(args.output_dir)
        else:
            # 默认基于当前工作目录
            posts_path = Path.cwd() / 'source' / '_posts'
        
        output_file, target_date = get_output_filename(posts_path)
        
        print(f"\n[1/4] 生成 Hexo 文章...")
        print(f"  标题: {title}")
        print(f"  分类: {category}")
        print(f"  标签: {', '.join(tags) if tags else '无'}")
        
        # 生成 Hexo 内容
        hexo_content = generate_hexo_content(title, body, tags, category, summary)
        
        # 写入文件
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(hexo_content)
        
        print(f"  [OK] 文章已生成: {output_file}")
        
        # Git 操作
        print(f"\n[2/4] 执行 Git 操作...")
        blog_root = posts_path.parent.parent
        
        rc, out, err = run_command(['git', 'add', '.'], cwd=str(blog_root))
        if rc != 0:
            print(f"  [WARN] git add: {err}")
        else:
            print(f"  [OK] git add")
        
        commit_msg = f"add: {title[:50]}"
        rc, out, err = run_command(['git', 'commit', '-m', commit_msg], cwd=str(blog_root))
        if rc != 0:
            if 'nothing to commit' in err.lower() or 'nothing to commit' in out.lower():
                print(f"  [INFO] 无需提交")
            else:
                print(f"  [WARN] git commit: {err}")
        else:
            print(f"  [OK] git commit: {commit_msg}")
        
        rc, out, err = run_command(['git', 'push'], cwd=str(blog_root))
        if rc != 0:
            print(f"  [WARN] git push: {err}")
        else:
            print(f"  [OK] git push")
        
        # Hexo 部署
        if not args.no_deploy:
            print(f"\n[3/4] 执行 Hexo 部署...")
            
            rc, out, err = run_command(['hexo', 'clean'], cwd=str(blog_root))
            if rc != 0:
                print(f"  [WARN] hexo clean: {err}")
            else:
                print(f"  [OK] hexo clean")
            
            rc, out, err = run_command(['hexo', 'deploy'], cwd=str(blog_root))
            if rc != 0:
                print(f"  [FAIL] hexo deploy: {err}")
                print(f"\n请手动执行: cd {blog_root} && hexo deploy")
            else:
                print(f"  [OK] hexo deploy")
        
        print(f"\n[4/4] 完成!")
        print(f"  文章已发布: {output_file}")
        print(f"  标题: {title}")
        
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()

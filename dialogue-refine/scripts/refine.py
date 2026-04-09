#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dialogue Refine - AI 对话文章提炼工具
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
        # 也检查 Clippings 目录
        candidate = d / 'source' / '_posts' / 'Clippings'
        if candidate.exists():
            return str(candidate)
    return ""


def get_latest_dialogue(dialogues_dir: str) -> Path:
    """获取对话目录下最新修改的文件"""
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
        tags_yaml = '  - dialogue-refine'
    
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


def get_output_filename(input_file: Path, now: datetime = None) -> Path:
    """生成输出文件名，在原文目录下生成 yyyyMMdd-refined.md"""
    if now is None:
        now = datetime.now()
    
    filename = now.strftime('%Y%m%d') + '-refined.md'
    output_path = input_file.parent / filename
    
    # 如果文件已存在，添加序号
    counter = 1
    original_output = output_path
    while output_path.exists():
        filename = now.strftime('%Y%m%d') + f'-refined-{counter}.md'
        output_path = input_file.parent / filename
        counter += 1
    
    return output_path


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='将 AI 对话内容提炼为 Hexo 博客文章')
    parser.add_argument('dialogue_file', nargs='?', help='对话记录文件路径（可选，默认使用环境变量或最新文件）')
    parser.add_argument('--title', help='文章标题')
    parser.add_argument('--category', help='文章分类')
    parser.add_argument('--tags', help='文章标签，逗号分隔')
    parser.add_argument('--summary', help='文章摘要')
    parser.add_argument('--output-dir', help='输出目录（默认：与原文同目录）')
    
    args = parser.parse_args()
    
    try:
        # 确定输入文件
        if args.dialogue_file:
            input_path = Path(args.dialogue_file)
            if not input_path.exists():
                print(f"[ERROR] 文件不存在: {input_path}")
                sys.exit(1)
        else:
            # 尝试从环境变量获取目录
            dialogues_dir = os.environ.get('HEXO_CLIPPINGS_DIR')
            source = "environment variable HEXO_CLIPPINGS_DIR"
            
            if not dialogues_dir:
                # 尝试自动推断
                dialogues_dir = get_default_dialogues_path()
                source = "auto-detected path"
            
            if not dialogues_dir:
                print("\n[ERROR] 未指定对话文件，且无法自动确定目录")
                print("\n请通过以下方式之一指定：")
                print("  1. 设置环境变量: HEXO_CLIPPINGS_DIR=<your_dialogues_path>")
                print("  2. 传递文件路径: python refine.py <dialogue_file>")
                print("  3. 在 Hexo 博客根目录下运行此脚本")
                sys.exit(1)
            
            if not Path(dialogues_dir).exists():
                print(f"\n[ERROR] 目录不存在: {dialogues_dir}")
                print(f"\n请检查环境变量 HEXO_CLIPPINGS_DIR 或使用 --dialogue-dir 指定")
                sys.exit(1)
            
            print(f"Using path from {source}: {dialogues_dir}")
            input_path = get_latest_dialogue(dialogues_dir)
        
        print(f"\n[1/3] 读取对话文件...")
        print(f"  文件: {input_path}")
        
        # 读取并解析对话
        with open(input_path, 'r', encoding='utf-8') as f:
            raw_content = f.read()
        
        dialogue_meta = parse_dialogue(raw_content)
        print(f"  解析完成，找到 {len(dialogue_meta['dialogue'])} 条对话")
        
        # 这里应该是 Agent 提炼后的内容
        # 为了演示，我们直接使用原始内容（实际使用时，这里应该是提炼后的结构化内容）
        
        # 确定标题
        title = args.title or dialogue_meta['title'] or input_path.stem
        
        # 确定分类
        category = args.category or dialogue_meta['category']
        if not category:
            category = classify_article(title, raw_content, dialogue_meta['tags'])
        
        # 确定标签
        tags = args.tags.split(',') if args.tags else dialogue_meta['tags']
        
        # 确定摘要
        summary = args.summary or ''
        
        print(f"\n[2/3] 生成 Hexo 文章...")
        print(f"  标题: {title}")
        print(f"  分类: {category}")
        print(f"  标签: {', '.join(tags) if tags else '无'}")
        
        # 生成 Hexo 内容
        # 注意：这里应该使用提炼后的内容，而不是原始对话
        # 实际使用时，Agent 应该先生成提炼后的内容，再调用此脚本
        hexo_content = generate_hexo_content(
            title, 
            "# 请使用 Agent 提炼后的内容替换此部分\n\n原始对话内容已解析，请运行 Agent 进行提炼。",
            tags, 
            category, 
            summary
        )
        
        # 确定输出路径
        if args.output_dir:
            output_dir = Path(args.output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
            output_file = output_dir / (datetime.now().strftime('%Y%m%d') + '-refined.md')
        else:
            output_file = get_output_filename(input_path)
        
        # 写入文件
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(hexo_content)
        
        print(f"  [OK] 文章已生成: {output_file}")
        
        print(f"\n[3/3] 完成!")
        print(f"  输出文件: {output_file}")
        print(f"  标题: {title}")
        print(f"\n提示:")
        print(f"  1. 请使用 Agent 对原始对话进行提炼，替换生成的占位内容")
        print(f"  2. 完成后使用 hexo-push skill 进行发布")
        
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

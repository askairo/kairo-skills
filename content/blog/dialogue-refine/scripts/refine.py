#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dialogue Refine - AI 对话文章提炼工具
将 AI 对话记录转换为结构化的 Hexo 博客文章
"""

import sys
import re
import subprocess
import tempfile
import json
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
BLOG_CONFIG_PATH = Path("local-config") / "blog" / "config.json"


def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError as exc:
        print(f"[WARN] 配置文件解析失败 {path}: {exc}")
        return {}


def script_agent_home() -> Path | None:
    """从 <Agent Home>/skills/<skill>/scripts 中确定当前 Agent Home。"""
    skills_dir = Path(__file__).resolve().parents[2]
    return skills_dir.parent if skills_dir.name == 'skills' else None


def resolve_agent_home(explicit: str = '') -> Path | None:
    if explicit:
        return Path(explicit).expanduser().resolve()
    return script_agent_home()


def load_config(agent_home: Path | None) -> dict:
    """只读取统一的博客领域配置。"""
    return read_json(agent_home / BLOG_CONFIG_PATH) if agent_home else {}


def save_user_config(agent_home: Path, blog_root: Path) -> Path:
    """将共享博客配置写入当前 Agent Home。"""
    config_path = agent_home / BLOG_CONFIG_PATH
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config = read_json(config_path)
    config['version'] = 1
    config['blogRoot'] = str(blog_root)
    config_path.write_text(json.dumps(config, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return config_path


def auto_detect_blog_root() -> Path | None:
    """仅从当前目录向上识别 Hexo 根目录，不使用个人路径默认值。"""
    cwd = Path.cwd().resolve()
    for directory in [cwd] + list(cwd.parents):
        if (directory / '_config.yml').is_file() and (directory / 'source' / '_posts').is_dir():
            return directory
    return None


def validate_blog_root(path: Path) -> Path:
    """校验 Hexo 博客根目录。"""
    root = path.expanduser().resolve()
    required = [root / '_config.yml', root / 'source' / '_posts', root / '.git']
    missing = [str(item) for item in required if not item.exists()]
    if missing:
        raise FileNotFoundError(f"无效的 Hexo 博客根目录 {root}，缺少: {', '.join(missing)}")
    return root


def resolve_blog_root(args, config: dict) -> tuple[Path, str]:
    """确定博客根目录：显式参数 > 用户配置 > 自动发现。"""
    if args.blog_root:
        return validate_blog_root(Path(args.blog_root)), 'command line argument --blog-root'

    configured = config.get('blogRoot') or config.get('blog_root')
    if configured:
        return validate_blog_root(Path(configured)), 'config file blogRoot'

    detected = auto_detect_blog_root()
    if detected:
        return validate_blog_root(detected), 'auto-detected Hexo root'

    raise FileNotFoundError(
        "未配置 blogRoot。请先询问用户的 Hexo 博客根目录，再使用 "
        "--blog-root <path> --save-config 保存到用户配置。"
    )


def resolve_dialogues_dir(args, blog_root: Path) -> tuple[str, str]:
    """确定对话目录：显式参数 > blogRoot 固定结构。"""
    if args.dialogue_dir:
        return args.dialogue_dir, "command line argument --dialogue-dir"

    posts_root = blog_root / 'source' / '_posts'
    dialogues = posts_root / 'Dialogues'
    if dialogues.exists():
        return str(dialogues), "blogRoot-derived Dialogues path"

    clippings = posts_root / 'Clippings'
    if clippings.exists():
        return str(clippings), "blogRoot-derived Clippings path"

    return "", ""


def validate_output_dir(path: Path, blog_root: Path) -> Path:
    """只允许将加工稿写入系统临时目录或配置博客的 posts 目录。"""
    output_dir = path.expanduser().resolve()
    allowed_roots = [
        Path(tempfile.gettempdir()).resolve(),
        (blog_root / 'source' / '_posts').resolve(),
    ]
    if not any(output_dir == root or root in output_dir.parents for root in allowed_roots):
        raise ValueError(
            f"输出目录必须位于系统临时目录或 {blog_root / 'source' / '_posts'} 内，实际为 {output_dir}"
        )
    return output_dir


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


def get_output_filename(now: datetime = None) -> Path:
    """在系统临时目录生成加工稿，避免污染当前业务项目。"""
    if now is None:
        now = datetime.now()
    
    filename = now.strftime('%Y%m%d') + '-refined.md'
    output_dir = Path(tempfile.gettempdir()) / 'dialogue-refine'
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / filename
    
    # 如果文件已存在，添加序号
    counter = 1
    while output_path.exists():
        filename = now.strftime('%Y%m%d') + f'-refined-{counter}.md'
        output_path = output_dir / filename
        counter += 1
    
    return output_path


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='将 AI 对话内容提炼为 Hexo 博客文章')
    parser.add_argument('dialogue_file', nargs='?', help='对话记录文件路径（可选，默认使用配置文件、自动发现或最新文件）')
    parser.add_argument('--title', help='文章标题')
    parser.add_argument('--category', help='文章分类')
    parser.add_argument('--tags', help='文章标签，逗号分隔')
    parser.add_argument('--summary', help='文章摘要')
    parser.add_argument('--output-dir', help='显式输出目录（默认使用系统临时目录，不写入当前项目）')
    parser.add_argument('--dialogue-dir', help='对话记录目录（优先于配置文件和自动发现）')
    parser.add_argument('--blog-root', help='Hexo 博客根目录；首次使用时结合 --save-config 保存')
    parser.add_argument('--agent-home', help='当前 Agent Home；从已安装 skill 运行时可自动确定')
    parser.add_argument('--save-config', action='store_true', help='将 blogRoot 保存到用户目录配置')
    
    args = parser.parse_args()
    
    try:
        agent_home = resolve_agent_home(args.agent_home)
        config = load_config(agent_home)
        blog_root, root_source = resolve_blog_root(args, config)
        print(f"Using blog root from {root_source}: {blog_root}")
        if args.save_config:
            if not agent_home:
                raise ValueError("无法确定 Agent Home，请显式传入 --agent-home")
            config_path = save_user_config(agent_home, blog_root)
            print(f"Saved blogRoot to user config: {config_path}")

        # 确定输入文件
        if args.dialogue_file:
            input_path = Path(args.dialogue_file)
            if not input_path.exists():
                print(f"[ERROR] 文件不存在: {input_path}")
                sys.exit(1)
        else:
            dialogues_dir, source = resolve_dialogues_dir(args, blog_root)
            
            if not dialogues_dir:
                print("\n[ERROR] 未指定对话文件，且无法自动确定目录")
                print("\n请通过以下方式之一指定：")
                print("  1. 传递文件路径: python refine.py <dialogue_file>")
                print("  2. 传递目录: python refine.py --dialogue-dir <dialogues_dir>")
                print("  3. 配置 blogRoot，并在博客目录中创建 Dialogues 或 Clippings")
                sys.exit(1)
            
            if not Path(dialogues_dir).exists():
                print(f"\n[ERROR] 目录不存在: {dialogues_dir}")
                print(f"\n请检查配置文件或使用 --dialogue-dir 指定")
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
            output_dir = validate_output_dir(Path(args.output_dir), blog_root)
            output_dir.mkdir(parents=True, exist_ok=True)
            output_file = output_dir / (datetime.now().strftime('%Y%m%d') + '-refined.md')
        else:
            output_file = get_output_filename()
        
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

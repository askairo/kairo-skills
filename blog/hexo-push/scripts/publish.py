#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hexo Clipping 发布工具
读取 Clippings 目录的最新文章，转换为 Hexo 博客格式并发布。

Agent 负责内容理解、润色、分类和标签选择；脚本负责机械发布、去重、git 和 deploy。
"""

import os
import sys
import re
import subprocess
import time
import json
import shutil
from datetime import datetime, timedelta
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except AttributeError:
    pass


ALLOWED_CATEGORIES = ["AI", "工作", "健康", "杂谈"]
CONFIG_NAMES = (
    "hexo-push.local.json",
    ".hexo-push.json",
)


def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError as exc:
        print(f"[WARN] Failed to parse config {path}: {exc}")
        return {}


def load_config() -> dict:
    """Load stable local config. Environment variables are fallback only."""
    config = {}
    search_dirs = [
        Path.cwd(),
        Path(__file__).resolve().parents[1],
        Path.home() / '.config' / 'skills',
        Path.home() / '.codex',
    ]
    for directory in search_dirs:
        for name in CONFIG_NAMES:
            path = directory / name
            if path.exists():
                config.update(read_json(path))
    return config


def save_user_config(blog_root: Path) -> Path:
    """Persist machine-specific configuration outside the skill source tree."""
    config_path = Path.home() / '.codex' / '.hexo-push.json'
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config = read_json(config_path)
    config['blogRoot'] = str(blog_root)
    config_path.write_text(json.dumps(config, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return config_path


def auto_detect_blog_root() -> Path | None:
    """Find the nearest Hexo root without assuming a user-specific absolute path."""
    cwd = Path.cwd().resolve()
    for directory in [cwd] + list(cwd.parents):
        if (directory / '_config.yml').is_file() and (directory / 'source' / '_posts').is_dir():
            return directory
    return None


def validate_blog_root(path: Path) -> Path:
    """Validate the configured Hexo root before any file or Git operation."""
    root = path.expanduser().resolve()
    required = [root / '_config.yml', root / 'source' / '_posts', root / '.git']
    missing = [str(item) for item in required if not item.exists()]
    if missing:
        raise FileNotFoundError(f"无效的 Hexo 博客根目录 {root}，缺少: {', '.join(missing)}")
    return root


def ensure_within(path: Path, parent: Path, label: str) -> Path:
    """Reject paths that escape the configured blog boundary."""
    resolved = path.expanduser().resolve()
    parent_resolved = parent.expanduser().resolve()
    try:
        resolved.relative_to(parent_resolved)
    except ValueError as exc:
        raise ValueError(f"{label} 必须位于 {parent_resolved} 内，实际为 {resolved}") from exc
    return resolved


def get_latest_file(clippings_dir: str) -> Path:
    """获取 Clippings 目录下最新修改的 Markdown 文件。"""
    clips_path = Path(clippings_dir)
    if not clips_path.exists():
        raise FileNotFoundError(f"目录不存在: {clippings_dir}")

    files = [f for f in clips_path.iterdir() if f.is_file() and f.suffix == '.md']
    if not files:
        raise FileNotFoundError(f"目录中没有 Markdown 文件: {clippings_dir}")

    return max(files, key=lambda f: f.stat().st_mtime)


def split_front_matter(content: str) -> tuple[str, str]:
    """拆分 YAML front matter 和正文。"""
    normalized = content.lstrip('\ufeff')
    match = re.match(r'^---\s*\r?\n(.*?)\r?\n---\s*\r?\n?(.*)$', normalized, re.DOTALL)
    if not match:
        return '', content
    return match.group(1), match.group(2).strip()


def unquote_yaml_value(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
        return value[1:-1]
    return value


def normalize_yaml_list_item(value: str) -> str:
    return clean_wiki_links(unquote_yaml_value(value.strip()))


def parse_simple_front_matter(front_matter: str) -> dict:
    """解析常见 Hexo/Obsidian front matter，避免正则漏掉最后一个列表项。"""
    data = {}
    lines = front_matter.splitlines()
    i = 0

    while i < len(lines):
        line = lines[i]
        if not line.strip() or line.lstrip().startswith('#'):
            i += 1
            continue

        match = re.match(r'^([A-Za-z0-9_-]+):\s*(.*)$', line)
        if not match:
            i += 1
            continue

        key, rest = match.group(1), match.group(2).strip()
        if rest:
            data[key] = unquote_yaml_value(rest)
            i += 1
            continue

        items = []
        i += 1
        while i < len(lines):
            child = lines[i]
            if re.match(r'^[A-Za-z0-9_-]+:\s*', child):
                break
            item_match = re.match(r'^\s*-\s*(.*)$', child)
            if item_match:
                items.append(normalize_yaml_list_item(item_match.group(1)))
            i += 1
        data[key] = items

    return data


def first_list_value(value):
    if isinstance(value, list):
        return value[0] if value else ''
    return value or ''


def parse_front_matter(content: str) -> dict:
    """解析文章元数据和正文。"""
    front_matter, body = split_front_matter(content)
    data = parse_simple_front_matter(front_matter) if front_matter else {}

    metadata = {
        'title': str(data.get('title') or ''),
        'source': str(data.get('source') or ''),
        'author': first_list_value(data.get('author')),
        'description': str(data.get('description') or ''),
        'tags': [str(tag) for tag in data.get('tags', [])] if isinstance(data.get('tags'), list) else [],
        'created': str(data.get('created') or ''),
        'body': body or content,
    }

    if not metadata['title']:
        lines = content.strip().split('\n')
        if lines:
            metadata['title'] = lines[0].strip('# ')
            metadata['body'] = content

    return metadata


def clean_unicode_chars(text: str) -> str:
    """清理容易影响 YAML 或阅读体验的 Unicode 标点。"""
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


def classify_article(title: str, body: str, tags: list) -> str | None:
    """兜底分类。优先让 Agent 从自然语言中确认分类；脚本分类只在未指定时使用。"""
    text = (title + " " + body + " " + " ".join(tags)).lower()
    keywords = {
        "AI": [
            "人工智能", "机器学习", "深度学习", "llm", "大模型", "chatgpt", "gpt", "claude",
            "神经网络", "算法", "nvidia", "gpu", "芯片", "openai", "agi", "aigc", "生成式",
            "transformer", "模型训练", "推理", "python", "tensorflow", "pytorch", "数据科学",
            "自动驾驶", "机器人"
        ],
        "工作": [
            "编程", "代码", "开发", "架构", "cleancode", "命名规范", "重构", "职场", "面试",
            "管理", "效率", "工具", "git", "docker", "kubernetes", "微服务", "前端", "后端",
            "全栈", "devops", "敏捷", "scrum", "项目管理", "沟通", "汇报", "晋升",
            "简历", "offer", "薪资", "远程工作", "副业"
        ],
        "健康": [
            "健身", "运动", "跑步", "瑜伽", "游泳", "饮食", "营养", "减肥", "增肌", "睡眠",
            "失眠", "心理", "焦虑", "抑郁", "冥想", "养生", "医疗", "疾病", "体检", "疫苗",
            "免疫力", "慢性病", "颈椎", "腰椎", "眼睛", "视力"
        ],
        "杂谈": [
            "生活", "随笔", "感悟", "读书", "阅读", "书评", "电影", "影评", "音乐", "旅行",
            "旅游", "摄影", "美食", "社会", "新闻", "评论", "热点", "八卦", "历史", "文化",
            "哲学", "经济", "金融", "投资", "理财", "房产", "汽车", "企业", "制造业", "制度"
        ],
    }

    scores = {}
    for cat, words in keywords.items():
        score = sum(1 for word in words if word.lower() in text)
        if score > 0:
            scores[cat] = score

    if scores:
        return max(scores, key=scores.get)
    return None


def prompt_for_category() -> str:
    """当自动分类无法确定时，交互式询问用户。"""
    print("\n  [INFO] 无法自动确定文章分类，请从以下分类中选择：")
    for i, cat in enumerate(ALLOWED_CATEGORIES, 1):
        print(f"    {i}. {cat}")
    print("    0. 新增分类")

    while True:
        try:
            choice = input("  请输入编号 (1-4 或 0): ").strip()
            idx = int(choice)
            if 1 <= idx <= len(ALLOWED_CATEGORIES):
                return ALLOWED_CATEGORIES[idx - 1]
            if idx == 0:
                new_cat = input("  请输入新分类名称: ").strip()
                if new_cat:
                    return new_cat
                print("  [WARN] 分类名称不能为空")
            else:
                print("  [WARN] 无效的选择，请重新输入")
        except ValueError:
            print("  [WARN] 请输入数字")


def strip_summary_and_more(body: str) -> str:
    """如果 body 中已经包含 <!--more--> 分隔符，只保留后面的正文部分。"""
    parts = body.split('<!--more-->', 1)
    if len(parts) == 2:
        return parts[1].strip()
    return body


def generate_summary(body: str, description: str = '', max_length: int = 200) -> str:
    """生成摘要：优先使用 Agent/原文 description，否则取正文前 max_length 字符。"""
    if description and len(description.strip()) > 10:
        return description.strip()

    body_for_summary = body.split('<!--more-->', 1)[0] if '<!--more-->' in body else body
    text = re.sub(r'[#*`\[\]\(\)!]', '', body_for_summary)
    text = text.replace('\n', ' ').strip()

    if len(text) > max_length:
        return text[:max_length].strip() + '...'
    return text


def clean_wiki_links(text: str) -> str:
    """清理 Obsidian/维基风格链接 [[文本]] -> 文本。"""
    return re.sub(r'\[\[(.*?)\]\]', r'\1', str(text))


def generate_attribution(source: str, author: str) -> str:
    """生成来源署名。"""
    parts = []
    if source:
        parts.append(f"来源：{source}")
    if author:
        parts.append(f"原作者：{clean_wiki_links(author)}")

    if parts:
        return "\n\n---\n\n> " + " | ".join(parts)
    return ""


def yaml_quote(value: str) -> str:
    value = str(value).replace('\\', '\\\\').replace('"', '\\"')
    return f'"{value}"'


def generate_hexo_content(metadata: dict, target_date: datetime | None = None, category: str | None = None) -> str:
    """生成 Hexo 格式的 Markdown 内容。"""
    if target_date is None:
        target_date = datetime.now()
    date_str = target_date.strftime('%Y-%m-%d %H:%M:%S')

    title = clean_unicode_chars(metadata.get('title', 'No Title'))
    body = strip_summary_and_more(metadata.get('body', ''))
    description = metadata.get('description', '')
    source = metadata.get('source', '')
    author = clean_wiki_links(metadata.get('author', ''))
    created = metadata.get('created', '')

    summary = clean_unicode_chars(generate_summary(body, description))
    body = clean_unicode_chars(body)

    tags = [str(tag).strip() for tag in metadata.get('tags', []) if str(tag).strip()]
    if not tags:
        tags = ['clippings']
    tags_yaml = '\n'.join([f'  - {tag}' for tag in tags])

    extra_fields = []
    if source:
        extra_fields.append(f'source: {yaml_quote(source)}')
    if author:
        extra_fields.append(f'author: {yaml_quote(author)}')
    if created:
        extra_fields.append(f'created: {yaml_quote(created)}')
    extra_yaml = '\n' + '\n'.join(extra_fields) if extra_fields else ''

    attribution = generate_attribution(source, author)

    return f"""---
title: {yaml_quote(title)}
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


def find_existing_posts(posts_dir: Path, title: str, source: str) -> tuple[Path | None, list[Path]]:
    """查找相同文章，优先匹配 source URL，其次匹配 title。"""
    if not posts_dir.exists():
        return None, []

    matched_files = []
    title_cleaned = clean_unicode_chars(title)

    for md_file in posts_dir.rglob('*.md'):
        if 'Clippings' in md_file.parts:
            continue

        try:
            content = md_file.read_text(encoding='utf-8')
            old_meta = parse_front_matter(content)
            old_title = old_meta.get('title', '').strip()
            old_source = old_meta.get('source', '').strip()
            old_title_cleaned = clean_unicode_chars(old_title)

            is_match = False
            if source and old_source and source == old_source:
                is_match = True
            elif title_cleaned and old_title_cleaned and title_cleaned == old_title_cleaned:
                is_match = True

            if is_match:
                matched_files.append((md_file, md_file.stat().st_mtime))
        except Exception:
            continue

    if not matched_files:
        return None, []

    matched_files.sort(key=lambda x: x[1])
    earliest = matched_files[0][0]
    duplicates = [f[0] for f in matched_files[1:]]
    return earliest, duplicates


def get_output_filename(posts_path: Path, now: datetime | None = None) -> tuple[Path, datetime]:
    """生成输出文件名，如果当天已存在则自动往后推一天。"""
    if now is None:
        now = datetime.now()
    current_date = now.date()

    while True:
        output_dir = posts_path / current_date.strftime('%Y')
        output_dir.mkdir(exist_ok=True)
        output_path = output_dir / (current_date.strftime('%Y%m%d') + '.md')
        if not output_path.exists():
            return output_path, datetime.combine(current_date, now.time())
        current_date += timedelta(days=1)


def run_command(cmd: list[str], cwd: str | None = None) -> tuple[int, str, str]:
    """执行命令并返回结果。"""
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            encoding='utf-8',
            shell=False,
        )
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return -1, '', str(e)


def run_command_with_retries(cmd: list[str], cwd: str | None = None, retries: int = 1, delay: int = 3) -> tuple[int, str, str]:
    """对网络敏感命令做有限重试。"""
    attempts = max(1, retries)
    last = (1, '', '')
    for attempt in range(1, attempts + 1):
        last = run_command(cmd, cwd)
        rc, out, err = last
        if rc == 0:
            return last
        if attempt < attempts:
            print(f"  [WARN] {' '.join(cmd)} failed, retrying ({attempt}/{attempts - 1})...")
            if err:
                print(f"    {err.strip()[:300]}")
            time.sleep(delay)
    return last


def resolve_hexo_command(blog_root: Path) -> str:
    """Resolve Hexo reliably on Windows and Unix-like systems."""
    local_name = 'hexo.cmd' if os.name == 'nt' else 'hexo'
    local_hexo = blog_root / 'node_modules' / '.bin' / local_name
    if local_hexo.is_file():
        return str(local_hexo)

    for command in ([local_name, 'hexo'] if os.name == 'nt' else ['hexo']):
        resolved = shutil.which(command)
        if resolved:
            return resolved

    raise FileNotFoundError(
        f"找不到 Hexo CLI。请先在 {blog_root} 安装依赖，确保 node_modules/.bin/{local_name} 存在。"
    )


def resolve_blog_root(options: dict, positional_args: list[str], config: dict) -> tuple[Path, str]:
    """Resolve blog root from explicit input, local config, legacy input, or safe auto-detection."""
    if options['blog_root']:
        return validate_blog_root(Path(options['blog_root'])), 'command line argument --blog-root'

    configured = config.get('blogRoot') or config.get('blog_root')
    if configured:
        return validate_blog_root(Path(configured)), 'config file blogRoot'

    legacy_clippings = positional_args[0] if positional_args else (
        config.get('clippingsDir') or config.get('clippings_dir') or os.environ.get('HEXO_CLIPPINGS_DIR')
    )
    if legacy_clippings:
        clips = Path(legacy_clippings).expanduser().resolve()
        return validate_blog_root(clips.parent.parent.parent), 'legacy Clippings path'

    detected = auto_detect_blog_root()
    if detected:
        return validate_blog_root(detected), 'auto-detected Hexo root'

    raise FileNotFoundError(
        "未配置 blogRoot。请先询问用户的 Hexo 博客根目录，再使用 "
        "--blog-root <path> --save-config 保存到用户配置。"
    )


def resolve_clippings_dir(blog_root: Path, positional_args: list[str], config: dict) -> tuple[Path, str]:
    """Resolve Clippings inside the configured blog posts tree."""
    posts_root = blog_root / 'source' / '_posts'
    if positional_args:
        clips = ensure_within(Path(positional_args[0]), posts_root, 'Clippings 目录')
        return clips, 'command line argument'

    configured = config.get('clippingsDir') or config.get('clippings_dir')
    if configured:
        clips = ensure_within(Path(configured), posts_root, 'Clippings 目录')
        return clips, 'legacy config clippingsDir'

    return posts_root / 'Clippings', 'blogRoot-derived path'


def read_optional_file(path: str) -> str:
    return Path(path).read_text(encoding='utf-8').strip()


def parse_tags_text(text: str) -> list[str]:
    tags = []
    for raw in re.split(r'[\n,，]', text):
        tag = raw.strip().lstrip('-').strip().strip('"\'')
        if tag:
            tags.append(tag)
    return tags


def parse_args(argv: list[str]) -> tuple[dict, list[str]]:
    options = {
        'description': '',
        'description_file': '',
        'category': '',
        'tags': [],
        'tags_file': '',
        'content_file': '',
        'dry_run': False,
        'deploy_retries': 2,
        'skip_deploy': False,
        'skip_git': False,
        'blog_root': '',
        'save_config': False,
    }
    positional = []

    i = 0
    while i < len(argv):
        arg = argv[i]
        if arg == '--description' and i + 1 < len(argv):
            options['description'] = argv[i + 1]
            i += 2
        elif arg.startswith('--description='):
            options['description'] = arg.split('=', 1)[1]
            i += 1
        elif arg == '--description-file' and i + 1 < len(argv):
            options['description_file'] = argv[i + 1]
            i += 2
        elif arg.startswith('--description-file='):
            options['description_file'] = arg.split('=', 1)[1]
            i += 1
        elif arg == '--category' and i + 1 < len(argv):
            options['category'] = argv[i + 1]
            i += 2
        elif arg.startswith('--category='):
            options['category'] = arg.split('=', 1)[1]
            i += 1
        elif arg == '--tags' and i + 1 < len(argv):
            options['tags'] = parse_tags_text(argv[i + 1])
            i += 2
        elif arg.startswith('--tags='):
            options['tags'] = parse_tags_text(arg.split('=', 1)[1])
            i += 1
        elif arg == '--tags-file' and i + 1 < len(argv):
            options['tags_file'] = argv[i + 1]
            i += 2
        elif arg.startswith('--tags-file='):
            options['tags_file'] = arg.split('=', 1)[1]
            i += 1
        elif arg == '--content-file' and i + 1 < len(argv):
            options['content_file'] = argv[i + 1]
            i += 2
        elif arg.startswith('--content-file='):
            options['content_file'] = arg.split('=', 1)[1]
            i += 1
        elif arg == '--dry-run':
            options['dry_run'] = True
            i += 1
        elif arg == '--skip-deploy':
            options['skip_deploy'] = True
            i += 1
        elif arg == '--skip-git':
            options['skip_git'] = True
            i += 1
        elif arg == '--blog-root' and i + 1 < len(argv):
            options['blog_root'] = argv[i + 1]
            i += 2
        elif arg.startswith('--blog-root='):
            options['blog_root'] = arg.split('=', 1)[1]
            i += 1
        elif arg == '--save-config':
            options['save_config'] = True
            i += 1
        elif arg == '--deploy-retries' and i + 1 < len(argv):
            options['deploy_retries'] = int(argv[i + 1])
            i += 2
        elif arg.startswith('--deploy-retries='):
            options['deploy_retries'] = int(arg.split('=', 1)[1])
            i += 1
        elif arg.startswith('--'):
            print(f"[WARN] Unknown option ignored: {arg}")
            i += 1
        else:
            positional.append(arg)
            i += 1

    if options['description_file'] and not options['description']:
        try:
            options['description'] = read_optional_file(options['description_file'])
        except Exception as e:
            print(f"[WARN] Failed to read description file: {e}")

    if options['tags_file'] and not options['tags']:
        try:
            options['tags'] = parse_tags_text(read_optional_file(options['tags_file']))
        except Exception as e:
            print(f"[WARN] Failed to read tags file: {e}")

    return options, positional


def print_publish_summary(output_file: Path, metadata: dict, category: str, is_update: bool):
    action = 'update' if is_update else 'create'
    print("\n  Publish summary:")
    print(f"    action: {action}")
    print(f"    output: {output_file}")
    print(f"    title: {metadata.get('title', '')}")
    print(f"    category: {category}")
    print(f"    tags: {', '.join(metadata.get('tags', []))}")
    if metadata.get('source'):
        print(f"    source: {metadata.get('source')}")


def main():
    options, positional_args = parse_args(sys.argv[1:])
    config = load_config()
    blog_root, root_source = resolve_blog_root(options, positional_args, config)
    clippings_path, path_source = resolve_clippings_dir(blog_root, positional_args, config)
    clippings_dir = str(clippings_path)

    if options['save_config']:
        config_path = save_user_config(blog_root)
        print(f"Saved blogRoot to user config: {config_path}")

    print(f"Using blog root from {root_source}: {blog_root}")
    print(f"Using path from {path_source}: {clippings_dir}")
    if options['description']:
        print(f"Using custom description ({len(options['description'])} chars)")
    if options['category']:
        print(f"Using Agent-confirmed category: {options['category']}")
    if options['tags']:
        print(f"Using Agent-confirmed tags: {', '.join(options['tags'])}")

    if not Path(clippings_dir).exists() and not options['content_file']:
        print(f"\n[ERROR] Clippings directory does not exist: {clippings_dir}")
        sys.exit(1)

    try:
        if options['content_file']:
            latest_file = None
            print(f"\n[1/7] Using Agent content file; Clippings directory is not required")
        else:
            print(f"\n[1/7] Reading Clippings directory: {clippings_dir}")
            latest_file = get_latest_file(clippings_dir)
            print(f"  Latest file: {latest_file.name}")

        print("\n[2/7] Parsing file...")
        if options['content_file']:
            content_path = Path(options['content_file'])
            content = content_path.read_text(encoding='utf-8')
            print(f"  Content override: {content_path}")
        else:
            assert latest_file is not None
            content = latest_file.read_text(encoding='utf-8')

        metadata = parse_front_matter(content)
        if options['description']:
            metadata['description'] = options['description']
        if options['tags']:
            metadata['tags'] = options['tags']

        print(f"  Title: {metadata.get('title', 'No title')[:50]}")
        print(f"  Source: {metadata.get('source', 'N/A')}")
        print(f"  Author: {metadata.get('author', 'N/A')}")
        print(f"  Tags: {', '.join(metadata.get('tags', []))}")

        print("\n[3/7] Determining output path...")
        posts_path = blog_root / 'source' / '_posts'
        title = metadata.get('title', '')
        source = metadata.get('source', '')
        earliest_file, duplicate_files = find_existing_posts(posts_path, title, source)

        is_update = False
        now = datetime.now()
        if earliest_file:
            output_file = earliest_file
            is_update = True
            match_by = 'source URL' if source else 'title'
            print(f"  [INFO] Found existing post by {match_by}: {output_file.name}")
            print("  [INFO] Will update existing file instead of creating new one")
            if duplicate_files:
                print(f"  [INFO] Found {len(duplicate_files)} duplicate post(s), removing...")
                for dup_file in duplicate_files:
                    try:
                        if not options['dry_run']:
                            dup_file.unlink()
                        print(f"    [DELETED] {dup_file.name}")
                    except Exception as e:
                        print(f"    [WARN] Failed to delete {dup_file.name}: {e}")
            target_date = datetime.combine(datetime.strptime(output_file.stem, '%Y%m%d').date(), now.time())
        else:
            output_file, target_date = get_output_filename(posts_path, now)
            print(f"  Output directory: {output_file.parent}")
            print(f"  Output file: {output_file.name}")

        print("\n[4/7] Classifying article...")
        category = options['category'].strip()
        if category:
            print(f"  [OK] Agent-confirmed category: {category}")
        else:
            category = classify_article(metadata.get('title', ''), metadata.get('body', ''), metadata.get('tags', []))
            if category:
                print(f"  [OK] Auto-selected fallback category: {category}")
            else:
                category = prompt_for_category()
                print(f"  [OK] User-selected category: {category}")

        print("\n[5/7] Generating Hexo document...")
        hexo_content = generate_hexo_content(metadata, target_date, category)
        print_publish_summary(output_file, metadata, category, is_update)

        if options['dry_run']:
            print("\n[DRY-RUN] Generated content follows. No file, git, or deploy action was performed.\n")
            print(hexo_content)
            return

        output_file.write_text(hexo_content, encoding='utf-8', newline='\n')
        print(f"  [OK] File {'updated' if is_update else 'generated'}")

        if options['skip_git']:
            print("\n[6/7] Skipping Git operations (--skip-git)")
        else:
            print("\n[6/7] Executing Git operations...")
            print(f"  Blog root: {blog_root}")
            changed_files = [output_file, *duplicate_files]
            relative_files = [str(path.resolve().relative_to(blog_root)) for path in changed_files]
            rc, out, err = run_command(['git', 'add', '--', *relative_files], cwd=str(blog_root))
            if rc != 0:
                raise RuntimeError(f"git add failed: {err or out}")
            print(f"  [OK] git add explicit files: {', '.join(relative_files)}")

            commit_prefix = 'update' if is_update else 'add'
            commit_msg = f"{commit_prefix}: {metadata.get('title', 'New post')[:50]}"
            rc, out, err = run_command(
                ['git', 'commit', '--only', '-m', commit_msg, '--', *relative_files],
                cwd=str(blog_root),
            )
            if rc != 0:
                if 'nothing to commit' in err.lower() or 'nothing to commit' in out.lower():
                    print("  [INFO] Nothing to commit")
                else:
                    print(f"  [WARN] git commit: {err}")
            else:
                print(f"  [OK] git commit: {commit_msg}")

            rc, out, err = run_command(['git', 'push'], cwd=str(blog_root))
            if rc != 0:
                raise RuntimeError(f"git push failed: {err or out}")
            print("  [OK] git push")

        if options['skip_deploy']:
            print("\n[7/7] Skipping Hexo deploy (--skip-deploy)")
        else:
            print("\n[7/7] Executing Hexo deploy...")
            hexo_command = resolve_hexo_command(blog_root)
            print(f"  Hexo CLI: {hexo_command}")
            rc, out, err = run_command([hexo_command, 'clean'], cwd=str(blog_root))
            if rc != 0:
                raise RuntimeError(f"hexo clean failed: {err or out}")
            print("  [OK] hexo clean")

            rc, out, err = run_command_with_retries(
                [hexo_command, 'deploy'],
                cwd=str(blog_root),
                retries=options['deploy_retries'],
            )
            if rc != 0:
                raise RuntimeError(f"hexo deploy failed: {err or out}")
            print("  [OK] hexo deploy")

        print("\nDone!")
        print(f"  Article {'updated' if is_update else 'published'}: {output_file}")
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

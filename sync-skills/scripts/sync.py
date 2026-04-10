#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Skills 同步工具
同步项目目录与用户目录的 skills
"""

import os
import sys
import shutil
import argparse
from pathlib import Path
from datetime import datetime
from typing import Set, Dict, Tuple, List

# Windows 终端中文输出修复
try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except AttributeError:
    pass


def get_project_dir() -> str:
    """获取项目目录路径"""
    project_dir = os.environ.get('SKILLS_PROJECT_DIR')
    if not project_dir:
        # 尝试自动检测：查找包含 .git 的父目录
        cwd = Path.cwd()
        check_dirs = [cwd] + list(cwd.parents)
        for d in check_dirs:
            if (d / '.git').exists():
                # 检查是否是 skills 项目（包含多个 skill 目录）
                skills = [x for x in d.iterdir() if x.is_dir() and (x / 'SKILL.md').exists()]
                if len(skills) >= 2:
                    return str(d)
    return project_dir


def get_user_dir() -> str:
    """获取用户目录路径"""
    user_dir = os.environ.get('SKILLS_USER_DIR')
    if not user_dir:
        # 默认使用 Kimi CLI 标准路径
        home = Path.home()
        user_dir = str(home / '.config' / 'agents' / 'skills')
    return user_dir


def get_skills_in_dir(directory: str) -> Set[str]:
    """获取目录中的所有 skill 名称"""
    path = Path(directory)
    if not path.exists():
        return set()
    
    skills = set()
    for item in path.iterdir():
        if item.is_dir() and (item / 'SKILL.md').exists():
            skills.add(item.name)
    return skills


def compare_skill_content(skill_name: str, project_dir: str, user_dir: str) -> Tuple[bool, List[str]]:
    """
    对比两边 skill 的内容差异
    返回: (是否相同, 差异文件列表)
    """
    project_path = Path(project_dir) / skill_name
    user_path = Path(user_dir) / skill_name
    
    differences = []
    
    # 获取两边所有文件
    project_files = set()
    user_files = set()
    
    if project_path.exists():
        for f in project_path.rglob('*'):
            if f.is_file():
                project_files.add(f.relative_to(project_path).as_posix())
    
    if user_path.exists():
        for f in user_path.rglob('*'):
            if f.is_file():
                user_files.add(f.relative_to(user_path).as_posix())
    
    # 检查差异
    all_files = project_files | user_files
    for f in all_files:
        project_file = project_path / f
        user_file = user_path / f
        
        if f not in project_files:
            differences.append(f"[用户独有] {f}")
        elif f not in user_files:
            differences.append(f"[项目独有] {f}")
        else:
            # 文件都存在，对比内容
            try:
                with open(project_file, 'rb') as pf, open(user_file, 'rb') as uf:
                    if pf.read() != uf.read():
                        differences.append(f"[内容不同] {f}")
            except Exception:
                differences.append(f"[无法对比] {f}")
    
    return len(differences) == 0, differences


def backup_directory(directory: str) -> str:
    """备份目录"""
    path = Path(directory)
    if not path.exists():
        return None
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = Path(str(path) + f'.backup.{timestamp}')
    
    shutil.copytree(path, backup_path)
    return str(backup_path)


def sync_skill(skill_name: str, source_dir: str, target_dir: str, dry_run: bool = False) -> bool:
    """
    同步单个 skill
    返回: 是否成功
    """
    source_path = Path(source_dir) / skill_name
    target_path = Path(target_dir) / skill_name
    
    if dry_run:
        return True
    
    try:
        # 如果目标存在，先删除
        if target_path.exists():
            shutil.rmtree(target_path)
        
        # 复制
        shutil.copytree(source_path, target_path)
        return True
    except Exception as e:
        print(f"  [ERROR] 同步失败: {e}")
        return False


def check_mode(project_dir: str, user_dir: str):
    """检查模式：显示差异"""
    print(f"\n{'='*60}")
    print("Skills 差异检查")
    print(f"{'='*60}")
    print(f"项目目录: {project_dir}")
    print(f"用户目录: {user_dir}")
    
    project_skills = get_skills_in_dir(project_dir)
    user_skills = get_skills_in_dir(user_dir)
    
    print(f"\n项目目录 skills ({len(project_skills)} 个):")
    for s in sorted(project_skills):
        print(f"  - {s}")
    
    print(f"\n用户目录 skills ({len(user_skills)} 个):")
    for s in sorted(user_skills):
        print(f"  - {s}")
    
    # 差异分析
    only_in_project = project_skills - user_skills
    only_in_user = user_skills - project_skills
    in_both = project_skills & user_skills
    
    print(f"\n{'='*60}")
    print("差异分析")
    print(f"{'='*60}")
    
    if only_in_project:
        print(f"\n📁 仅在项目目录 ({len(only_in_project)} 个):")
        for s in sorted(only_in_project):
            print(f"    + {s}  →  可 install 到用户目录")
    
    if only_in_user:
        print(f"\n📁 仅在用户目录 ({len(only_in_user)} 个):")
        for s in sorted(only_in_user):
            print(f"    + {s}  →  可 dev 到项目目录")
    
    if in_both:
        print(f"\n📁 两边都有 ({len(in_both)} 个):")
        for s in sorted(in_both):
            same, diffs = compare_skill_content(s, project_dir, user_dir)
            if same:
                print(f"    = {s}  (内容相同)")
            else:
                print(f"    ≠ {s}  (内容不同)")
                for d in diffs[:3]:  # 只显示前3个差异
                    print(f"      {d}")
                if len(diffs) > 3:
                    print(f"      ... 还有 {len(diffs)-3} 个差异")
    
    if not only_in_project and not only_in_user:
        # 检查内容差异
        has_diff = False
        for s in in_both:
            same, _ = compare_skill_content(s, project_dir, user_dir)
            if not same:
                has_diff = True
                break
        if not has_diff:
            print("\n✅ 两边 skills 完全一致，无需同步")
    
    print(f"\n{'='*60}")


def install_mode(project_dir: str, user_dir: str, dry_run: bool = False):
    """Install 模式：项目 → 用户"""
    print(f"\n{'='*60}")
    print("Install 模式: 项目 → 用户")
    print(f"{'='*60}")
    
    project_skills = get_skills_in_dir(project_dir)
    user_skills = get_skills_in_dir(user_dir)
    
    to_sync = project_skills - user_skills
    to_update = project_skills & user_skills
    
    # 检查需要更新的
    to_update_real = []
    for s in to_update:
        same, _ = compare_skill_content(s, project_dir, user_dir)
        if not same:
            to_update_real.append(s)
    
    if not to_sync and not to_update_real:
        print("✅ 无需同步，用户目录已是最新")
        return
    
    print(f"\n将执行以下操作:")
    if to_sync:
        print(f"  新增: {', '.join(sorted(to_sync))}")
    if to_update_real:
        print(f"  更新: {', '.join(sorted(to_update_real))}")
    
    if dry_run:
        print("\n[试运行模式，未实际执行]")
        return
    
    # 备份
    print(f"\n正在备份用户目录...")
    backup_path = backup_directory(user_dir)
    if backup_path:
        print(f"  备份路径: {backup_path}")
    
    # 执行同步
    print(f"\n开始同步...")
    success_count = 0
    
    for skill in sorted(to_sync | set(to_update_real)):
        print(f"  同步 {skill}...", end=' ')
        if sync_skill(skill, project_dir, user_dir):
            print("✓")
            success_count += 1
        else:
            print("✗")
    
    print(f"\n✅ 同步完成: {success_count}/{len(to_sync) + len(to_update_real)} 个 skill")


def dev_mode(project_dir: str, user_dir: str, dry_run: bool = False):
    """Dev 模式：用户 → 项目"""
    print(f"\n{'='*60}")
    print("Dev 模式: 用户 → 项目")
    print(f"{'='*60}")
    
    project_skills = get_skills_in_dir(project_dir)
    user_skills = get_skills_in_dir(user_dir)
    
    to_sync = user_skills - project_skills
    to_update = user_skills & project_skills
    
    # 检查需要更新的
    to_update_real = []
    for s in to_update:
        same, _ = compare_skill_content(s, project_dir, user_dir)
        if not same:
            to_update_real.append(s)
    
    if not to_sync and not to_update_real:
        print("✅ 无需同步，项目目录已是最新")
        return
    
    print(f"\n将执行以下操作:")
    if to_sync:
        print(f"  新增: {', '.join(sorted(to_sync))}")
    if to_update_real:
        print(f"  更新: {', '.join(sorted(to_update_real))}")
    
    if dry_run:
        print("\n[试运行模式，未实际执行]")
        return
    
    # 备份
    print(f"\n正在备份项目目录...")
    backup_path = backup_directory(project_dir)
    if backup_path:
        print(f"  备份路径: {backup_path}")
    
    # 执行同步
    print(f"\n开始同步...")
    success_count = 0
    
    for skill in sorted(to_sync | set(to_update_real)):
        print(f"  同步 {skill}...", end=' ')
        if sync_skill(skill, user_dir, project_dir):
            print("✓")
            success_count += 1
        else:
            print("✗")
    
    print(f"\n✅ 同步完成: {success_count}/{len(to_sync) + len(to_update_real)} 个 skill")
    print("\n⚠️  记得将新同步的 skills 提交到 Git!")


def main():
    parser = argparse.ArgumentParser(description='Skills 同步工具')
    parser.add_argument('--mode', choices=['check', 'install', 'dev'], 
                        default='check',
                        help='同步模式: check=检查差异, install=项目→用户, dev=用户→项目')
    parser.add_argument('--dry-run', action='store_true',
                        help='试运行，不实际执行同步')
    
    args = parser.parse_args()
    
    # 获取目录
    project_dir = get_project_dir()
    user_dir = get_user_dir()
    
    if not project_dir:
        print("[ERROR] 无法确定项目目录")
        print("请设置环境变量: SKILLS_PROJECT_DIR")
        sys.exit(1)
    
    if not Path(project_dir).exists():
        print(f"[ERROR] 项目目录不存在: {project_dir}")
        sys.exit(1)
    
    if not Path(user_dir).exists():
        print(f"[WARN] 用户目录不存在，将创建: {user_dir}")
        Path(user_dir).mkdir(parents=True, exist_ok=True)
    
    # 执行对应模式
    if args.mode == 'check':
        check_mode(project_dir, user_dir)
    elif args.mode == 'install':
        install_mode(project_dir, user_dir, args.dry_run)
    elif args.mode == 'dev':
        dev_mode(project_dir, user_dir, args.dry_run)


if __name__ == '__main__':
    main()

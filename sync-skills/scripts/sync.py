#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub-centered skills manager.

The stable flow is:
  local skills repo -> GitHub -> current Agent skills directory

Environment variables are supported only as a last-resort fallback. Prefer
explicit arguments, local config files, installed-source metadata, and automatic
Agent directory detection.
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import urllib.request
import zipfile
from datetime import datetime, timezone
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except AttributeError:
    pass


DEFAULT_REPO = "askairo/kairo-skills"
DEFAULT_REF = "main"
SOURCE_META = ".skill-source.json"
CONFIG_NAMES = ("sync-skills.local.json", ".sync-skills.json")
EXCLUDE_DIRS = {".git", "__pycache__", ".venv", "node_modules"}
EXCLUDE_SUFFIXES = {".pyc", ".pyo"}


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def script_skill_dir() -> Path:
    return Path(__file__).resolve().parents[1]


def script_agent_dir() -> Path:
    # <agent-skills-dir>/sync-skills/scripts/sync.py
    return Path(__file__).resolve().parents[2]


def is_skill_dir(path: Path) -> bool:
    return path.is_dir() and (path / "SKILL.md").exists()


def is_skills_repo(path: Path) -> bool:
    return path.is_dir() and any(is_skill_dir(child) for child in path.iterdir() if child.is_dir())


def find_skills_repo_from_cwd() -> Path | None:
    cwd = Path.cwd().resolve()
    for candidate in [cwd] + list(cwd.parents):
        if is_skills_repo(candidate):
            return candidate
    return None


def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {}


def write_json(path: Path, data: dict):
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def load_config() -> dict:
    """Load optional config files. Env vars are fallback only."""
    config = {}
    search_dirs = [
        script_skill_dir(),
        Path.home() / ".config" / "skills",
        Path.home() / ".codex",
    ]
    cwd_repo = find_skills_repo_from_cwd()
    if cwd_repo:
        search_dirs.insert(0, cwd_repo)

    for directory in search_dirs:
        for name in CONFIG_NAMES:
            path = directory / name
            if path.exists():
                config.update(read_json(path))

    if "defaultRepo" not in config:
        config["defaultRepo"] = os.environ.get("SKILLS_DEFAULT_REPO", DEFAULT_REPO)
    if "defaultRef" not in config:
        config["defaultRef"] = os.environ.get("SKILLS_DEFAULT_REF", DEFAULT_REF)
    if "localRepoPath" not in config:
        env_repo = os.environ.get("SKILLS_PROJECT_DIR")
        detected = cwd_repo
        if detected:
            config["localRepoPath"] = str(detected)
        elif env_repo:
            config["localRepoPath"] = env_repo
    if "agentSkillsDir" not in config:
        env_agent = os.environ.get("SKILLS_USER_DIR")
        if env_agent:
            config["agentSkillsDir"] = env_agent

    return config


def resolve_agent_dir(args, config: dict) -> Path:
    if args.agent_dir:
        return Path(args.agent_dir).expanduser().resolve()
    if config.get("agentSkillsDir"):
        return Path(config["agentSkillsDir"]).expanduser().resolve()

    detected = script_agent_dir()
    if detected.name != "skills":
        # Common Codex/Kimi defaults as fallback.
        codex = Path.home() / ".codex" / "skills"
        if codex.exists():
            return codex.resolve()
        kimi = Path.home() / ".config" / "agents" / "skills"
        return kimi.resolve()
    return detected


def resolve_local_repo(args, config: dict) -> Path | None:
    if args.local_repo:
        return Path(args.local_repo).expanduser().resolve()
    if config.get("localRepoPath"):
        return Path(config["localRepoPath"]).expanduser().resolve()
    return find_skills_repo_from_cwd()


def run(cmd: list[str], cwd: Path | None = None) -> tuple[int, str, str]:
    result = subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        text=True,
        encoding="utf-8",
        capture_output=True,
        shell=False,
    )
    return result.returncode, result.stdout, result.stderr


def require_success(cmd: list[str], cwd: Path | None = None):
    rc, out, err = run(cmd, cwd)
    if rc != 0:
        raise RuntimeError(f"Command failed: {' '.join(cmd)}\n{err or out}")
    return out


def clean_skill_name(path: str) -> str:
    return Path(path.replace("\\", "/").rstrip("/")).name


def download_github_path(repo: str, ref: str, skill_path: str, target_dir: Path, dry_run: bool = False):
    """Download one skill directory from a GitHub repo archive and overwrite target_dir."""
    repo = repo.strip().removeprefix("https://github.com/").strip("/")
    archive_url = f"https://github.com/{repo}/archive/refs/heads/{ref}.zip"
    if len(ref) == 40:
        archive_url = f"https://github.com/{repo}/archive/{ref}.zip"

    print(f"  Source: GitHub {repo}/{skill_path}@{ref}")
    print(f"  Target: {target_dir}")
    if dry_run:
        print("  [DRY-RUN] Would download and overwrite target skill directory.")
        return

    with tempfile.TemporaryDirectory(prefix="skill-update-") as tmp:
        tmp_path = Path(tmp)
        zip_path = tmp_path / "repo.zip"
        try:
            urllib.request.urlretrieve(archive_url, zip_path)
        except Exception:
            # Branch download may fail for tags/commits. Try generic archive path.
            archive_url = f"https://github.com/{repo}/archive/{ref}.zip"
            urllib.request.urlretrieve(archive_url, zip_path)

        extract_dir = tmp_path / "repo"
        with zipfile.ZipFile(zip_path) as zf:
            zf.extractall(extract_dir)

        roots = [p for p in extract_dir.iterdir() if p.is_dir()]
        if not roots:
            raise FileNotFoundError("GitHub archive did not contain a repository root")
        source_dir = roots[0] / skill_path
        if not is_skill_dir(source_dir):
            raise FileNotFoundError(f"Skill path not found or missing SKILL.md: {skill_path}")

        target_dir.parent.mkdir(parents=True, exist_ok=True)
        if target_dir.exists():
            backup = backup_dir(target_dir)
            print(f"  Backup: {backup}")
            shutil.rmtree(target_dir)
        copy_tree(source_dir, target_dir)


def copy_tree(source: Path, target: Path):
    def ignore(_dir, names):
        ignored = []
        for name in names:
            path = Path(name)
            if name in EXCLUDE_DIRS or path.suffix in EXCLUDE_SUFFIXES:
                ignored.append(name)
        return ignored

    shutil.copytree(source, target, ignore=ignore)


def backup_dir(path: Path) -> Path:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = path.with_name(f"{path.name}.backup.{stamp}")
    shutil.copytree(path, backup)
    return backup


def source_meta(repo: str, skill_path: str, ref: str) -> dict:
    return {
        "sourceType": "github",
        "repo": repo,
        "path": skill_path,
        "ref": ref,
        "installedAt": now_iso(),
    }


def install_or_update(args, config: dict):
    repo = args.repo or config.get("defaultRepo", DEFAULT_REPO)
    ref = args.ref or config.get("defaultRef", DEFAULT_REF)
    skill_path = args.path or args.skill
    if not skill_path:
        raise SystemExit("--skill or --path is required")

    skill_name = args.name or clean_skill_name(skill_path)
    agent_dir = resolve_agent_dir(args, config)
    target = agent_dir / skill_name

    download_github_path(repo, ref, skill_path, target, args.dry_run)
    if not args.dry_run:
        write_json(target / SOURCE_META, source_meta(repo, skill_path, ref))
        print(f"  [OK] Installed/updated {skill_name}")
        print("  Restart the Agent or open a new session to load updated skill metadata.")


def update_installed(args, config: dict):
    agent_dir = resolve_agent_dir(args, config)
    skills = [args.skill] if args.skill else [
        p.name for p in sorted(agent_dir.iterdir()) if is_skill_dir(p) and (p / SOURCE_META).exists()
    ]
    if not skills:
        print("No installed skills with source metadata found.")
        return

    for skill in skills:
        target = agent_dir / skill
        meta = read_json(target / SOURCE_META)
        if not meta:
            print(f"[SKIP] {skill}: no {SOURCE_META}")
            continue
        download_github_path(
            meta["repo"],
            args.ref or meta.get("ref", config.get("defaultRef", DEFAULT_REF)),
            meta["path"],
            target,
            args.dry_run,
        )
        if not args.dry_run:
            meta["installedAt"] = now_iso()
            if args.ref:
                meta["ref"] = args.ref
            write_json(target / SOURCE_META, meta)
            print(f"  [OK] Updated {skill}")


def list_installed(args, config: dict):
    agent_dir = resolve_agent_dir(args, config)
    print(f"Agent skills dir: {agent_dir}")
    if not agent_dir.exists():
        print("  Directory does not exist.")
        return

    for skill_dir in sorted(p for p in agent_dir.iterdir() if is_skill_dir(p)):
        meta = read_json(skill_dir / SOURCE_META)
        if meta:
            print(f"- {skill_dir.name}: {meta.get('repo')}/{meta.get('path')}@{meta.get('ref')}")
        else:
            print(f"- {skill_dir.name}: source unknown")


def validate_skill(skill_dir: Path):
    if not is_skill_dir(skill_dir):
        raise FileNotFoundError(f"Missing SKILL.md: {skill_dir}")

    for py_file in skill_dir.rglob("*.py"):
        if "__pycache__" in py_file.parts:
            continue
        require_success([sys.executable, "-m", "py_compile", str(py_file)])
        print(f"  [OK] py_compile {py_file.relative_to(skill_dir)}")


def publish(args, config: dict):
    local_repo = resolve_local_repo(args, config)
    if not local_repo:
        raise SystemExit("Local skills repo not found. Pass --local-repo or run inside the repo.")
    if not local_repo.exists():
        raise FileNotFoundError(f"Local repo does not exist: {local_repo}")
    if not args.skill:
        raise SystemExit("--skill is required for publish")

    skill_dir = local_repo / args.skill
    print(f"Local repo: {local_repo}")
    print(f"Skill: {skill_dir}")
    validate_skill(skill_dir)

    rc, out, err = run(["git", "status", "--short"], local_repo)
    if rc != 0:
        raise RuntimeError(err or out)
    if not out.strip():
        print("  [INFO] No git changes to publish.")
    else:
        print("\nChanged files:")
        print(out.rstrip())
        if args.dry_run:
            print("\n[DRY-RUN] Would commit and push these changes.")
            return
        require_success(["git", "add", args.skill], local_repo)
        if (local_repo / ".gitignore").exists():
            require_success(["git", "add", ".gitignore"], local_repo)
        message = args.message or f"chore: update {args.skill} skill"
        require_success(["git", "commit", "-m", message], local_repo)
        print(f"  [OK] git commit: {message}")

    if not args.dry_run:
        require_success(["git", "push"], local_repo)
        print("  [OK] git push")


def publish_and_update(args, config: dict):
    publish(args, config)
    install_args = argparse.Namespace(**vars(args))
    install_args.path = args.path or args.skill
    install_args.name = args.name or args.skill
    install_args.dry_run = args.dry_run
    install_or_update(install_args, config)


def write_config(args, config: dict):
    data = {
        "defaultRepo": args.repo or config.get("defaultRepo", DEFAULT_REPO),
        "defaultRef": args.ref or config.get("defaultRef", DEFAULT_REF),
    }
    if args.local_repo:
        data["localRepoPath"] = str(Path(args.local_repo).expanduser().resolve())
    if args.agent_dir:
        data["agentSkillsDir"] = str(Path(args.agent_dir).expanduser().resolve())

    path = script_skill_dir() / "sync-skills.local.json"
    write_json(path, data)
    print(f"Wrote config: {path}")


def build_parser():
    parser = argparse.ArgumentParser(description="GitHub-centered skills manager")
    parser.add_argument("command", choices=[
        "list",
        "install",
        "update",
        "update-all",
        "publish",
        "publish-and-update",
        "write-config",
    ])
    parser.add_argument("--skill", help="Skill name, for example hexo-push")
    parser.add_argument("--repo", help="GitHub repo, for example askairo/kairo-skills")
    parser.add_argument("--path", help="Path to skill inside repo. Defaults to --skill")
    parser.add_argument("--ref", help="Git ref/branch/tag. Defaults to config or main")
    parser.add_argument("--name", help="Installed skill directory name. Defaults to path basename")
    parser.add_argument("--agent-dir", help="Current Agent skills directory")
    parser.add_argument("--local-repo", help="Local writable skills source repository")
    parser.add_argument("--message", help="Commit message for publish")
    parser.add_argument("--dry-run", action="store_true", help="Print actions without writing")
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    config = load_config()

    try:
        if args.command == "list":
            list_installed(args, config)
        elif args.command == "install":
            install_or_update(args, config)
        elif args.command == "update":
            update_installed(args, config)
        elif args.command == "update-all":
            args.skill = None
            update_installed(args, config)
        elif args.command == "publish":
            publish(args, config)
        elif args.command == "publish-and-update":
            publish_and_update(args, config)
        elif args.command == "write-config":
            write_config(args, config)
    except Exception as exc:
        print(f"[ERROR] {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()

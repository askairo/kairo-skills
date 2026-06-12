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
import ast
import json
import os
import re
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


DEFAULT_REF = "main"
SOURCE_META = ".skill-source.json"
CONFIG_NAMES = (
    "skills-loop.local.json",
    "sync-skills.local.json",
    ".skills-loop.json",
    ".sync-skills.json",
)
EXCLUDE_DIRS = {".git", "__pycache__", ".venv", "node_modules"}
EXCLUDE_SUFFIXES = {".pyc", ".pyo"}
BACKUP_PATTERN = re.compile(r"^(.+)\.backup\.\d{8}_\d{6}$")

# Known agent home directories, checked in priority order.
# Each entry is (directory_name, agent_label).
KNOWN_AGENT_HOMES = [
    (".qoderworkcn", "QoderWork"),
    (".codex", "Codex"),
    (".config/agents", "Agents"),
]


def detect_agent_home() -> Path | None:
    """Detect the current agent's home directory by checking known paths.

    Returns the first existing known agent home, or None if none found.
    Priority order: QoderWork (.qoderworkcn) > Codex (.codex) > generic (.config/agents).
    """
    home = Path.home()
    for dirname, _label in KNOWN_AGENT_HOMES:
        candidate = home / dirname
        if candidate.exists():
            return candidate
    return None


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def script_skill_dir() -> Path:
    return Path(__file__).resolve().parents[1]


def script_agent_dir() -> Path:
    # <agent-skills-dir>/<skill-name>/scripts/sync.py
    return Path(__file__).resolve().parents[2]


def is_skill_dir(path: Path) -> bool:
    return path.is_dir() and (path / "SKILL.md").exists()


def is_ignored_path(path: Path) -> bool:
    return any(part in EXCLUDE_DIRS or BACKUP_PATTERN.match(part) for part in path.parts)


def read_skill_name(skill_dir: Path) -> str:
    skill_file = skill_dir / "SKILL.md"
    try:
        lines = skill_file.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError:
        return skill_dir.name

    if not lines or lines[0].strip() != "---":
        return skill_dir.name

    for line in lines[1:]:
        stripped = line.strip()
        if stripped == "---":
            break
        if stripped.startswith("name:"):
            return stripped.split(":", 1)[1].strip().strip('"').strip("'") or skill_dir.name
    return skill_dir.name


def iter_skill_dirs(root: Path) -> list[Path]:
    if not root.exists():
        return []

    if is_skill_dir(root):
        return [root]

    skill_dirs: list[Path] = []
    for skill_file in root.rglob("SKILL.md"):
        if is_ignored_path(skill_file.relative_to(root)):
            continue
        skill_dirs.append(skill_file.parent)
    return sorted(set(skill_dirs))


def is_skills_repo(path: Path) -> bool:
    return path.is_dir() and bool(iter_skill_dirs(path))


def git_root(start: Path) -> Path | None:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=str(start),
            text=True,
            encoding="utf-8",
            capture_output=True,
            shell=False,
        )
    except Exception:
        return None
    if result.returncode != 0 or not result.stdout.strip():
        return None
    return Path(result.stdout.strip()).resolve()


def find_skills_repo_from_path(start: Path) -> Path | None:
    start = start.resolve()
    git_repo = git_root(start if start.is_dir() else start.parent)
    if git_repo and is_skills_repo(git_repo):
        return git_repo

    matches = []
    for candidate in [start] + list(start.parents):
        if is_skills_repo(candidate):
            matches.append(candidate)
    if matches:
        return matches[-1]
    return None


def find_skills_repo_from_cwd() -> Path | None:
    return find_skills_repo_from_path(Path.cwd())


def relative_skill_path(repo: Path, skill_dir: Path) -> str:
    return skill_dir.relative_to(repo).as_posix()


def resolve_skill_dir(repo: Path, skill_ref: str) -> Path:
    normalized = skill_ref.replace("\\", "/").strip("/")
    candidate = repo / normalized
    if is_skill_dir(candidate):
        return candidate

    matches = []
    for skill_dir in iter_skill_dirs(repo):
        if skill_dir.name == skill_ref or read_skill_name(skill_dir) == skill_ref:
            matches.append(skill_dir)

    if not matches:
        raise FileNotFoundError(f"Skill not found by name or path: {skill_ref}")
    if len(matches) > 1:
        choices = ", ".join(relative_skill_path(repo, match) for match in matches)
        raise RuntimeError(f"Skill name is ambiguous: {skill_ref}. Candidates: {choices}")
    return matches[0]


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
    ]
    agent_home = detect_agent_home()
    if agent_home:
        search_dirs.append(agent_home)
    cwd_repo = find_skills_repo_from_cwd()
    if cwd_repo:
        search_dirs.insert(0, cwd_repo)

    for directory in search_dirs:
        for name in CONFIG_NAMES:
            path = directory / name
            if path.exists():
                config.update(read_json(path))

    if "defaultRepo" not in config and os.environ.get("SKILLS_DEFAULT_REPO"):
        config["defaultRepo"] = os.environ["SKILLS_DEFAULT_REPO"]
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
        # Try known agent home directories in priority order.
        agent_home = detect_agent_home()
        if agent_home:
            return (agent_home / "skills").resolve()
        # Last resort: generic XDG-style path.
        return (Path.home() / ".config" / "agents" / "skills").resolve()
    return detected


def resolve_local_repo(args, config: dict) -> Path | None:
    if args.local_repo:
        return Path(args.local_repo).expanduser().resolve()
    if config.get("localRepoPath"):
        configured = Path(config["localRepoPath"]).expanduser().resolve()
        if configured.exists() and is_skills_repo(configured):
            return configured
    detected_from_cwd = find_skills_repo_from_cwd()
    if detected_from_cwd:
        return detected_from_cwd

    candidates = [
        find_skills_repo_from_path(script_skill_dir()),
    ]
    for candidate in candidates:
        if candidate and is_skills_repo(candidate.expanduser().resolve()):
            return candidate.expanduser().resolve()
    return None


def resolve_repo(args, config: dict, skill: str | None = None) -> str:
    if args.repo:
        return args.repo
    if config.get("defaultRepo"):
        return config["defaultRepo"]
    if skill:
        try:
            agent_dir = resolve_agent_dir(args, config)
            meta = read_json(agent_dir / clean_skill_name(skill) / SOURCE_META)
            if meta.get("repo"):
                return meta["repo"]
        except Exception:
            pass
    raise SystemExit("GitHub repo is not configured. Pass --repo or set defaultRepo in local skills-loop config.")


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


def download_github_path(repo: str, ref: str, skill_ref: str, target_dir: Path, dry_run: bool = False) -> str:
    """Download one skill directory from a GitHub repo archive and overwrite target_dir."""
    repo = repo.strip().removeprefix("https://github.com/").strip("/")
    archive_url = f"https://github.com/{repo}/archive/refs/heads/{ref}.zip"
    if len(ref) == 40:
        archive_url = f"https://github.com/{repo}/archive/{ref}.zip"

    print(f"  Source: GitHub {repo}/{skill_ref}@{ref}")
    print(f"  Target: {target_dir}")
    if dry_run:
        print("  [DRY-RUN] Would download and overwrite target skill directory.")
        return skill_ref.replace("\\", "/").strip("/")

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
        repo_root = roots[0]
        try:
            source_dir = resolve_skill_dir(repo_root, skill_ref)
        except Exception as exc:
            hint = f"Skill not found or missing SKILL.md: {skill_ref}"
            local_repo = find_skills_repo_from_cwd()
            if local_repo:
                try:
                    resolve_skill_dir(local_repo, skill_ref)
                    hint += (
                        " | Found locally but missing in GitHub archive. "
                        "Publish/push local repo first, then install again."
                    )
                except Exception:
                    pass
            raise FileNotFoundError(f"{hint} ({exc})")

        target_dir.parent.mkdir(parents=True, exist_ok=True)
        if target_dir.exists():
            backup = backup_dir(target_dir)
            print(f"  Backup: {backup}")
            shutil.rmtree(target_dir)
        copy_tree(source_dir, target_dir)
        return relative_skill_path(repo_root, source_dir)


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
    repo = resolve_repo(args, config, args.path or args.skill)
    ref = args.ref or config.get("defaultRef", DEFAULT_REF)
    skill_ref = args.path or args.skill
    if not skill_ref:
        raise SystemExit("--skill or --path is required")

    skill_name = args.name or clean_skill_name(args.skill or skill_ref)
    agent_dir = resolve_agent_dir(args, config)
    target = agent_dir / skill_name

    resolved_path = download_github_path(repo, ref, skill_ref, target, args.dry_run)
    if not args.dry_run:
        write_json(target / SOURCE_META, source_meta(repo, resolved_path, ref))
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


def list_backup_dirs(agent_dir: Path, skill: str | None = None) -> list[Path]:
    backups: list[Path] = []
    if not agent_dir.exists():
        return backups

    for path in agent_dir.iterdir():
        if not path.is_dir():
            continue
        match = BACKUP_PATTERN.match(path.name)
        if not match:
            continue
        base_name = match.group(1)
        if skill and base_name != skill:
            continue
        backups.append(path)

    return sorted(backups)


def cleanup_backups(args, config: dict):
    agent_dir = resolve_agent_dir(args, config)
    backups = list_backup_dirs(agent_dir, args.skill)
    if not backups:
        print("No backup skill directories found.")
        return

    print(f"Agent skills dir: {agent_dir}")
    for backup in backups:
        print(f"- {backup.name}")

    if args.dry_run:
        print("[DRY-RUN] Would remove backup directories above.")
        return

    removed = 0
    for backup in backups:
        shutil.rmtree(backup)
        removed += 1
    print(f"[OK] Removed {removed} backup director{'y' if removed == 1 else 'ies'}.")


def validate_skill(skill_dir: Path, dry_run: bool = False):
    if not is_skill_dir(skill_dir):
        raise FileNotFoundError(f"Missing SKILL.md: {skill_dir}")

    for py_file in skill_dir.rglob("*.py"):
        if "__pycache__" in py_file.parts:
            continue
        if dry_run:
            source = py_file.read_text(encoding="utf-8")
            ast.parse(source, filename=str(py_file))
            print(f"  [OK] syntax-check {py_file.relative_to(skill_dir)}")
        else:
            require_success([sys.executable, "-m", "py_compile", str(py_file)])
            print(f"  [OK] py_compile {py_file.relative_to(skill_dir)}")


def publish(args, config: dict):
    local_repo = resolve_local_repo(args, config)
    if not local_repo:
        raise SystemExit("Local skills repo not found. Pass --local-repo or run inside the repo.")
    if not local_repo.exists():
        raise FileNotFoundError(f"Local repo does not exist: {local_repo}")
    skill_ref = args.path or args.skill
    if not skill_ref:
        raise SystemExit("--skill or --path is required for publish")

    skill_dir = resolve_skill_dir(local_repo, skill_ref)
    skill_path = relative_skill_path(local_repo, skill_dir)
    skill_name = read_skill_name(skill_dir)
    args._resolved_skill_path = skill_path
    args._resolved_skill_name = skill_name
    print(f"Local repo: {local_repo}")
    print(f"Skill: {skill_dir}")
    validate_skill(skill_dir, args.dry_run)

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
        require_success(["git", "add", skill_path], local_repo)
        if (local_repo / ".gitignore").exists():
            require_success(["git", "add", ".gitignore"], local_repo)
        message = args.message or f"chore: update {skill_name} skill"
        require_success(["git", "commit", "-m", message], local_repo)
        print(f"  [OK] git commit: {message}")

    if not args.dry_run:
        require_success(["git", "push"], local_repo)
        print("  [OK] git push")


def publish_and_update(args, config: dict):
    publish(args, config)
    install_args = argparse.Namespace(**vars(args))
    install_args.path = getattr(args, "_resolved_skill_path", args.path or args.skill)
    install_args.name = args.name or getattr(args, "_resolved_skill_name", clean_skill_name(install_args.path))
    install_args.dry_run = args.dry_run
    install_or_update(install_args, config)


def write_config(args, config: dict):
    data = {}
    if args.repo or config.get("defaultRepo"):
        data["defaultRepo"] = args.repo or config.get("defaultRepo")
    data["defaultRef"] = args.ref or config.get("defaultRef", DEFAULT_REF)
    if args.local_repo:
        data["localRepoPath"] = str(Path(args.local_repo).expanduser().resolve())
    elif config.get("localRepoPath"):
        data["localRepoPath"] = config["localRepoPath"]
    if args.agent_dir:
        data["agentSkillsDir"] = str(Path(args.agent_dir).expanduser().resolve())
    elif config.get("agentSkillsDir"):
        data["agentSkillsDir"] = config["agentSkillsDir"]

    config_dir = None
    if args.config_dir:
        config_dir = Path(args.config_dir).expanduser().resolve()
    else:
        config_dir = detect_agent_home()
    if not config_dir:
        config_dir = Path.home() / ".config" / "skills"

    path = config_dir / ".skills-loop.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    write_json(path, data)
    print(f"Wrote config: {path}")


def build_parser():
    parser = argparse.ArgumentParser(description="GitHub-centered skills manager")
    parser.add_argument("command", choices=[
        "list",
        "install",
        "update",
        "update-all",
        "cleanup-backups",
        "publish",
        "publish-and-update",
        "write-config",
    ])
    parser.add_argument("--skill", help="Skill name, for example hexo-push")
    parser.add_argument("--repo", help="GitHub repo, for example owner/repo")
    parser.add_argument("--path", help="Path to skill inside repo. Defaults to --skill")
    parser.add_argument("--ref", help="Git ref/branch/tag. Defaults to config or main")
    parser.add_argument("--name", help="Installed skill directory name. Defaults to path basename")
    parser.add_argument("--agent-dir", help="Current Agent skills directory")
    parser.add_argument("--local-repo", help="Local writable skills source repository")
    parser.add_argument("--config-dir", help="Agent home directory for config files (auto-detected if omitted)")
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
        elif args.command == "cleanup-backups":
            cleanup_backups(args, config)
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

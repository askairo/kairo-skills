#!/usr/bin/env python3
"""Merge a source branch into dev and/or sit, push, and return."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


class GitError(RuntimeError):
    """Raised when a git command fails."""


DEFAULT_TARGETS = ["dev", "sit"]
PROTECTED_SOURCE_BRANCHES = {"dev", "sit", "master"}


def run_git(repo: Path, args: list[str], *, capture: bool = False, dry_run: bool = False) -> str:
    command = ["git", *args]
    print(f"[git] {' '.join(command)}")
    if dry_run:
        return ""

    result = subprocess.run(
        command,
        cwd=repo,
        text=True,
        capture_output=capture,
        check=False,
    )
    if result.returncode != 0:
        if result.stdout:
            sys.stdout.write(result.stdout)
        if result.stderr:
            sys.stderr.write(result.stderr)
        raise GitError(f"Command failed: {' '.join(command)}")
    return result.stdout.strip() if capture else ""


def get_current_branch(repo: Path, *, dry_run: bool = False) -> str:
    if dry_run:
        return "<current-branch>"
    return run_git(repo, ["branch", "--show-current"], capture=True).strip()


def ensure_clean_worktree(repo: Path, *, dry_run: bool = False) -> None:
    if dry_run:
        print("[check] Skip clean worktree validation in dry-run mode")
        return
    status = run_git(repo, ["status", "--porcelain"], capture=True)
    if status:
        raise GitError("Working tree is not clean. Commit or stash changes before merging.")


def branch_exists(repo: Path, branch: str, *, remote: str | None = None, dry_run: bool = False) -> bool:
    if dry_run:
        return True
    ref = f"refs/remotes/{remote}/{branch}" if remote else f"refs/heads/{branch}"
    result = subprocess.run(
        ["git", "show-ref", "--verify", "--quiet", ref],
        cwd=repo,
        text=True,
        capture_output=True,
        check=False,
    )
    return result.returncode == 0


def is_protected_source_branch(branch: str) -> bool:
    return (
        branch in PROTECTED_SOURCE_BRANCHES
        or branch == "release"
        or branch.startswith("release/")
        or branch.startswith("release-")
    )


def validate_source_branch(branch: str) -> None:
    if is_protected_source_branch(branch):
        raise GitError(f"当前分支是 dev/sit/master/release 分支，不允许作为开发分支执行 merge-to: {branch}")


def checkout_target(repo: Path, target: str, remote: str, *, dry_run: bool = False) -> None:
    if branch_exists(repo, target, dry_run=dry_run):
        run_git(repo, ["checkout", target], dry_run=dry_run)
        return
    if not branch_exists(repo, target, remote=remote, dry_run=dry_run):
        raise GitError(f"Target branch '{target}' does not exist locally or on {remote}.")
    run_git(repo, ["checkout", "-b", target, "--track", f"{remote}/{target}"], dry_run=dry_run)


def sync_target_branch(repo: Path, target: str, remote: str, *, dry_run: bool = False) -> None:
    run_git(repo, ["fetch", remote, target], dry_run=dry_run)
    run_git(repo, ["pull", "--ff-only", remote, target], dry_run=dry_run)


def merge_source(repo: Path, source: str, merge_mode: str, *, dry_run: bool = False) -> None:
    if merge_mode == "merge":
        args = ["merge", source]
    elif merge_mode == "no-ff":
        args = ["merge", "--no-ff", source]
    elif merge_mode == "ff-only":
        args = ["merge", "--ff-only", source]
    else:
        raise GitError(f"Unsupported merge mode: {merge_mode}")
    run_git(repo, args, dry_run=dry_run)


def abort_merge(repo: Path) -> None:
    subprocess.run(
        ["git", "merge", "--abort"],
        cwd=repo,
        text=True,
        capture_output=True,
        check=False,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Merge a source branch into dev and/or sit, push it, and return.",
    )
    parser.add_argument("--repo", required=True, help="Repository path")
    parser.add_argument(
        "--target",
        choices=DEFAULT_TARGETS,
        help="Target branch. Defaults to merging into both dev and sit.",
    )
    parser.add_argument("--source", help="Source branch. Defaults to the current branch.")
    parser.add_argument("--remote", default="origin", help="Remote name. Defaults to origin.")
    parser.add_argument(
        "--merge-mode",
        choices=["merge", "no-ff", "ff-only"],
        default="merge",
        help="Merge strategy. Defaults to plain git merge.",
    )
    parser.add_argument(
        "--no-sync-target",
        action="store_true",
        help="Skip fetch and pull before merging.",
    )
    parser.add_argument(
        "--no-push",
        action="store_true",
        help="Skip pushing the target branch after merge.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the planned commands without executing them.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo = Path(args.repo).resolve()
    if not repo.exists():
        print(f"Repository path does not exist: {repo}", file=sys.stderr)
        return 1

    dry_run = args.dry_run
    original_branch = ""
    current_target = None
    pushed_targets: list[str] = []

    try:
        ensure_clean_worktree(repo, dry_run=dry_run)
        original_branch = get_current_branch(repo, dry_run=dry_run)
        source_branch = args.source or original_branch
        validate_source_branch(source_branch)

        if not branch_exists(repo, source_branch, dry_run=dry_run) and source_branch != original_branch:
            raise GitError(f"Source branch '{source_branch}' does not exist locally.")

        if args.target:
            if source_branch == args.target:
                raise GitError(f"Source and target branches must be different: {args.target}")
            targets = [args.target]
        else:
            targets = [target for target in DEFAULT_TARGETS if target != source_branch]
            if not targets:
                raise GitError("No valid integration target remains after excluding the source branch.")

        for target in targets:
            if not branch_exists(repo, target, dry_run=dry_run) and not branch_exists(repo, target, remote=args.remote, dry_run=dry_run):
                raise GitError(f"Target branch '{target}' does not exist locally or on {args.remote}.")

        print(f"[info] source={source_branch} targets={','.join(targets)} original={original_branch}")

        for target in targets:
            current_target = target
            checkout_target(repo, target, args.remote, dry_run=dry_run)
            if not args.no_sync_target:
                sync_target_branch(repo, target, args.remote, dry_run=dry_run)
            merge_source(repo, source_branch, args.merge_mode, dry_run=dry_run)
            if not args.no_push:
                run_git(repo, ["push", args.remote, target], dry_run=dry_run)
                pushed_targets.append(target)
            print(f"[done] Merge completed for {target}")

        return 0
    except GitError as error:
        print(f"[error] {error}", file=sys.stderr)
        if current_target and not dry_run:
            abort_merge(repo)
        if pushed_targets:
            print(f"[error] Already pushed targets: {', '.join(pushed_targets)}", file=sys.stderr)
        return 1
    finally:
        if original_branch:
            try:
                run_git(repo, ["checkout", original_branch], dry_run=dry_run)
            except GitError as restore_error:
                print(
                    f"[restore-error] Failed to switch back to '{original_branch}': {restore_error}",
                    file=sys.stderr,
                )
                if pushed_targets:
                    print(
                        f"[restore-error] Targets already pushed before restore failed: {', '.join(pushed_targets)}",
                        file=sys.stderr,
                    )


if __name__ == "__main__":
    raise SystemExit(main())


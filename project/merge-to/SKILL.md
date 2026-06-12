---
name: merge-to
description: Merge the current or specified source branch into `dev` or `sit`, push the updated target branch, and switch back to the original branch. Use when Codex needs to handle recurring Git integration flows such as merging a branch into dev, merging a branch into sit, or, when the user does not specify a target, merging the same branch into both dev and sit in sequence. Refuse to run when the current or default source branch is `dev`, `sit`, `master`, or a `release` branch so integration branches are not treated as development branches.
---

# Merge To

## Overview

Use this skill to merge a finished branch into the integration branches `dev` and `sit` with a consistent, safety-first workflow. Keep the target limited to those two branches; if the user does not specify one, process `dev` first and then `sit`.

## Workflow

1. Confirm the repository path and source branch. If the user does not say otherwise, treat the current branch as the source branch.
2. Refuse to continue if the current branch or default source branch is an integration or release branch:
   - `dev`
   - `sit`
   - `master`
   - any branch named `release` or starting with `release/` or `release-`
3. Determine the target set:
   - if the user names `dev`, merge only to `dev`
   - if the user names `sit`, merge only to `sit`
   - if the user does not specify a target, merge to `dev` and then `sit`, but skip any target whose name matches the source branch
4. Check the safety gates before making changes:
   - require a clean working tree
   - refuse `source == target` when the target is explicitly specified
   - stop if any requested target branch is missing both locally and on the selected remote
5. Run the bundled script:

```bash
python ...\merge-to\scripts\merge_to.py --repo <repo-path> [--target <dev|sit>]
```

6. Review the result. The script should:
   - remember the original branch
   - check out each target branch in sequence
   - optionally sync the target branch from the remote
   - merge the source branch
   - push the target branch unless disabled
   - continue to the next target only after the current target succeeds
   - check out the original branch in a `finally` path
7. If the merge conflicts, report the conflict clearly. The script attempts `git merge --abort` before switching away so the source branch stays usable.
8. If the repository requires a specific strategy, pass flags instead of inventing ad-hoc commands:
   - `--merge-mode merge` for a normal `git merge`
   - `--merge-mode no-ff` to force a merge commit
   - `--merge-mode ff-only` to refuse non-fast-forward merges
   - `--no-sync-target` if the user explicitly wants to skip `git pull --ff-only`
   - `--no-push` if the user only wants the local merge prepared

## Examples

```text
Use $merge-to to merge my current branch into dev, push it, and come back.
Use $merge-to to merge this branch into sit with --merge-mode no-ff.
Use $merge-to in D:\idea-workspace\znder-erp and, if I do not specify a target, merge the branch into dev and sit.
```

## Script

The bundled script lives at `scripts/merge_to.py`.

Preferred commands:

```bash
python ...\merge-to\scripts\merge_to.py --repo <repo-path> --target dev
python ...\merge-to\scripts\merge_to.py --repo <repo-path>
```

Optional flags:
- `--source <branch>` to merge a branch other than the current one
- `--target <dev|sit>` to merge to only one integration branch
- `--remote <name>` to use a remote other than `origin`
- `--merge-mode <merge|no-ff|ff-only>`
- `--no-sync-target`
- `--no-push`
- `--dry-run`

## Failure Handling

- Stop immediately on a dirty working tree, a protected source branch, a missing branch, a merge conflict, or a checkout failure.
- Tell the user which target branch failed and whether any earlier target was already pushed.
- Surface a failed restore to the original branch as the highest-priority issue.

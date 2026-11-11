# Branch Preparation

Use this flow after [task-intake](task-intake.md) resolves a branch such as `feat-2468`.

## Goals

- Reuse an existing task branch when it already exists.
- Automatically create the task branch when it does not exist.
- Create new task branches from the freshest safe baseline branch.
- Preserve unrelated working-tree changes.

## Workspace Choice

Preserve an explicit user choice of repository directory and baseline. When the working tree is clean, a different currently checked-out task branch can be left intact by switching branches in the same directory; it does not by itself require a new directory. Do not infer the baseline from the branch that happened to be open.

Use a separate checkout/worktree only when requested or required by actual concurrent writers or an applicable isolation rule. If the user requires one directory, serialize writers and branch switches there; do not satisfy the request by merely renaming an extra worktree. If live work makes switching unsafe, report the specific conflict before changing workspace strategy.

## Flow

1. Inspect the current repository.
   - Check the current branch.
   - Check working-tree status.
   - Do not switch branches when unrelated dirty changes would be put at risk.

2. Determine the task branch.
   - Use the user's explicit branch name if they provide one.
   - Otherwise resolve the identifier first: requirement-based feature branches use `feat-<requirement_id>`; source-task-number branches use `task-<task_id>`. Bug-number branches remain `fix-<bug_id>`; performance prefixes apply to requirement-based branches.
   - When the title provides no extractable requirement ID, fall back to `task-<task_id>`. Also use this form when the user requests a separate task branch under a requirement whose design/shared branch already exists; for example, task 1715 under requirement 1160 becomes `task-1715`, based on the user-selected current branch.
   - Multiple tasks under the same requirement may reuse a branch; keep their task IDs, source links, and task docs separate.

3. If the task branch exists locally, switch to it.
   - Do not recreate it from baseline.
   - If the user asks to refresh it from baseline, handle that as a separate explicit operation.

4. If the task branch exists only on the remote, create the local branch tracking the remote branch.
   - Prefer the repository's normal remote, usually `origin`.
   - Do not create a different branch with the same name from baseline.

5. If the task branch does not exist, create it from a baseline branch.
   - Prefer the baseline branch named by repository instructions.
   - In `znder-erp` and `znder-erp-api`, baseline priority is `master`, then `main`, then repository instruction baseline. If the user explicitly requests another base, follow that request.
   - If no instruction exists, infer from existing project practice.
   - Common baselines are `master`, `main`, and `dev`; do not assume one without checking what exists.

6. Before creating from baseline, update the baseline when safe. If the user explicitly selects the current branch or a specific commit as baseline, create from that exact state; do not silently switch to or refresh another baseline.
   - Fetch the remote.
   - Switch to the baseline branch.
   - Pull with a fast-forward-only strategy when possible.
   - Create the task branch from the updated baseline.

7. Verify baseline alignment immediately after branch creation.
   - Compare `rev-parse <baseline>` and `rev-parse <task-branch>`.
   - If they differ before any task commit is made, stop and recreate the task branch from the correct baseline.

8. Handle user correction and command-interruption quickly.
   - If the user says the baseline is wrong, pause code changes and fix branch baseline first.
   - If privileged git commands time out on approval review, retry once, then request explicit user go-ahead and continue with the same command.

9. Rename the current session to the branch.
   - Do this after the branch is selected or created and its name is final, including when an existing branch is reused.
   - Call `paseo_rename_workspace` with `title` set to the exact branch name, such as `feat-1166`. Omit `workspaceId` so the current workspace is renamed.
   - Do not use the user's first sentence, the task title, or a task id that differs from the branch.
   - If this request already gave the workspace a different explicit title, keep that title.
   - If the rename tool is unavailable, skip it. Do not fail branch preparation.

## Command Shape

Use repo-native Git commands. Typical shape:

```text
git fetch origin
git switch master
git pull --ff-only origin master
git switch -c feat-2468
```

Adjust `origin`, `master`, and `feat-2468` to the actual repo and resolved branch context.

If the repo uses `main` or `dev` as the baseline, replace `master` accordingly.

## Safety Rules

- Never overwrite an existing task branch automatically.
- Never delete or reset unrelated user changes.
- Stop and report clearly if the baseline branch cannot be updated cleanly.
- If the working tree is dirty, separate task-related changes from unrelated changes before switching or creating branches.

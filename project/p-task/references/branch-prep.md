# Branch Preparation

Use this flow after [task-intake](task-intake.md) resolves a branch such as `feat-2468`.

## Goals

- Reuse an existing task branch when it already exists.
- Automatically create the task branch when it does not exist.
- Create new task branches from the freshest safe baseline branch.
- Preserve unrelated working-tree changes.

## Flow

1. Inspect the current repository.
   - Check the current branch.
   - Check working-tree status.
   - Do not switch branches when unrelated dirty changes would be put at risk.

2. Determine the task branch.
   - Use the user's explicit branch name if they provide one.
   - Otherwise use `<prefix>-<branch_id>` from task intake: keep the source-based prefix (`feat`, `fix`, or `perf`), and prefer the requirement ID at the start of the task title over the source URL's task ID.
   - When the title provides no extractable requirement ID, fall back to the URL's task ID. Do not default all tasks to the `task-` prefix.
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

6. Before creating from baseline, update the baseline when safe.
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

# Branch Preparation

Use this flow when task metadata implies a branch such as `task-1234`.

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
   - Prefer `task-<task_id>` when a numeric task ID is available.
   - Use the user's explicit branch name if they provide one.

3. If the task branch exists locally, switch to it.
   - Do not recreate it from baseline.
   - If the user asks to refresh it from baseline, handle that as a separate explicit operation.

4. If the task branch exists only on the remote, create the local branch tracking the remote branch.
   - Prefer the repository's normal remote, usually `origin`.
   - Do not create a different branch with the same name from baseline.

5. If the task branch does not exist, create it from a baseline branch.
   - Prefer the baseline branch named by repository instructions.
   - If no instruction exists, infer from existing project practice.
   - Common baselines are `master`, `main`, and `dev`; do not assume one without checking what exists.

6. Before creating from baseline, update the baseline when safe.
   - Fetch the remote.
   - Switch to the baseline branch.
   - Pull with a fast-forward-only strategy when possible.
   - Create the task branch from the updated baseline.

## Command Shape

Use repo-native Git commands. Typical shape:

```text
git fetch origin
git switch master
git pull --ff-only origin master
git switch -c task-1234
```

Adjust `origin`, `master`, and `task-1234` to the actual repo and task context.

If the repo uses `main` or `dev` as the baseline, replace `master` accordingly.

## Safety Rules

- Never overwrite an existing task branch automatically.
- Never delete or reset unrelated user changes.
- Stop and report clearly if the baseline branch cannot be updated cleanly.
- If the working tree is dirty, separate task-related changes from unrelated changes before switching or creating branches.

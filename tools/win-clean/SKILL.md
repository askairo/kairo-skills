---
name: win-clean
description: 'Safely analyze and clean Windows C: drive space by mapping storage distribution, inspecting the user profile, ranking cleanup candidates with size and recency signals, discussing user-directory candidates, and deleting only approved targets.'
---

# Win Clean

Use this skill when the user asks to understand or clean Windows disk space, especially `C:`. Start with a read-only storage analysis. Clean known low-risk caches in safe mode; discuss other user-directory candidates with the user before deleting them.

## Goals

- Show before/after free and used space.
- Map the main C: consumers, including root files and top-level directories.
- Analyze `C:\Users` and the active user profile, including hidden folders and `AppData`.
- Rank cleanup candidates by size, data type, and recency signals.
- Separate rebuildable caches from configuration, development environments, and personal data.
- Use an exact-target plan and user choice before removing non-trivial user data.

## Safety Rules

- Validate every destructive target as an exact path before deletion. Never use a broad root, unresolved variable, or recursive wildcard as the deletion target.
- Do not delete from personal data folders by default: `Desktop`, `Documents`, `Pictures`, `Videos`, and `Downloads`. Aggregate their sizes without listing filenames unless the user asks for that detail.
- Do not delete app install trees by default: `C:\Program Files`, `C:\Program Files (x86)`, or `C:\ProgramData` except a specifically identified cache subpath.
- Never manually delete inside `C:\Windows\WinSxS`.
- Keep Codex runtime and cache untouched unless the user explicitly includes them.
- Treat `LastWriteTime` as supporting evidence only. `LastAccessTime` may be disabled or unreliable, and an old timestamp does not prove that a directory is unused. Do not delete a directory solely because it has not changed recently.
- Before changing app data, check whether the related process is running. Ask the user to close it or skip locked files; do not force-close an app with possible unsaved work.
- Prefer moving to a recoverable location when practical. If permanent deletion is authorized and used, report that it does not go to the Recycle Bin.
- For each delete operation, tolerate in-use files and report exact skipped paths.

## Default Workflow (Safe Mode)

1. **Baseline and distribution (read-only)**
   - Read free and used space for `C:`.
   - Measure the main top-level directories: `C:\Users`, `C:\Windows`, `C:\Program Files`, `C:\Program Files (x86)`, and `C:\ProgramData`.
   - Measure large root files such as `pagefile.sys`, `hiberfil.sys`, and `swapfile.sys`.
   - Explain that apparent `WinSxS` size can overstate reclaimable space because of hard links.

2. **User-profile analysis (read-only)**
   - Enumerate profiles under `C:\Users` and identify the active profile without assuming a fixed username.
   - Measure the active profile's hidden directories and normal directories separately.
   - Break down `AppData\Local`, `AppData\Roaming`, and `AppData\LocalLow`, then rank their largest immediate children.
   - For each likely candidate, report size, file count when useful, newest file time, and counts of files changed in the last 30/90/180/365 days. Use these as review signals, not proof of usage.
   - Do not enumerate filenames from personal folders in the default report. Check running processes before proposing app-data deletion.

3. **Classify and discuss candidates**
   - Present a compact table with: path, size, category, recency signal, likely impact, and proposed action.
   - **Known rebuildable caches:** user temp, Windows temp, Windows update download cache, Delivery Optimization cache, NVIDIA App update artifacts, `CrashDumps`, `*-updater`, and `npm-cache` when present. These may be cleaned in safe mode after the baseline.
   - **Review before deletion:** browser profiles, IDE system/cache directories, app caches, stale logs, and old version directories. Explain what will be rebuilt or lost.
   - **Protect by default:** configuration and plugin directories, app binaries, developer toolchains such as Rust/Maven/NuGet/Gradle stores, project files, and personal data. Require the user's choice for these.
   - If a candidate is old but has no reliable usage evidence, label it `needs review` rather than `unused`.

4. **Plan and approval boundary**
   - After the user selects candidates, list the exact paths, estimated reclaimable space, expected side effects, and whether the operation is recoverable.
   - Execute known low-risk cache cleanup without a second prompt in safe mode. For any other user-directory path, obtain explicit approval for that exact path or category immediately before deletion.

5. **Execute and verify**
   - Clean approved targets, preferably their contents while retaining the parent directory when an application expects it.
   - Run `Dism.exe /Online /Cleanup-Image /StartComponentCleanup`. If it returns error 740 or is blocked by pending actions, report the condition and advise an elevated prompt or restart; do not retry destructively.
   - Re-read C: free/used space, rescan affected paths, and report recovered space, locked files, skipped items, and remaining major consumers.

## Mode Switch

### `safe` (default)

- Always perform the distribution and user-profile analysis first.
- Clean only the known rebuildable caches listed above automatically.
- Do not delete personal data, configuration, plugins, developer stores, or directories selected only by age.
- Do not change hibernation settings or purge Codex/developer caches unless the user explicitly asks for those targets.

### `aggressive` (explicit user request only)

- Includes safe-mode analysis and cleanup.
- Still requires clear confirmation of each higher-impact category before execution.
- May include hibernation removal, developer-cache cleanup, stale logs, or stale directories when the user approves the exact targets and impact.

## Optional Actions (Explicit Confirmation Required)

- Disable hibernation to remove `hiberfil.sys`: `powercfg /h off`. This disables Hibernate and Fast Startup.
- Clear developer caches such as `C:\Users\<user>\.m2\repository`, `C:\Users\<user>\.nuget\packages`, `C:\Users\<user>\.gradle\caches`, Rust registry caches, npm/Yarn/uv caches, or IDE system directories. State whether the data will be redownloaded or rebuilt.
- Remove old large logs while keeping active logs.
- Remove stale empty directories only after validating ownership, age, and that no installed app or project refers to them. Age alone is insufficient.

## Output Format

Return a compact report with:

- `Before`: free/used GB
- `Distribution`: largest C: directories and root files
- `User profile`: largest hidden/AppData and normal directories
- `Candidates`: category, evidence, estimated reclaim, and proposed action
- `Actions`: exact cleaned paths and notes on failures/in-use files
- `After`: free/used GB
- `Recovered`: total GB gained
- `Skipped`: protected, uncertain, or locked items
- `Next`: optional targets awaiting user choice

## Notes

- Configuration, plugins, caches, logs, and local history may live in different `AppData` subtrees; inspect the application-specific layout before classifying a path.
- A directory's apparent size can differ from reclaimable space because of hard links, sparse files, junctions, or files held open by a process.
- Prefer repeatable, explainable cleanup over one-off deletion based on a timestamp alone.

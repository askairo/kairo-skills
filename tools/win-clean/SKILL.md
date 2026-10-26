---
name: win-clean
description: Analyze Windows disk usage (especially C:), clean junk, uninstall selected apps, or optimize using Mole CLI first, with scope review and before/after verification. Keep legacy PowerShell analysis only when Mole is unavailable.
---

# Win Clean

Use Mole CLI for Windows (`mo`, also distributed as `mole`) as the primary disk-analysis, cleanup, app-uninstall, and maintenance engine. This skill owns scope, authorization, candidate review, and verification. File organization remains a separate, reversible workflow.

Checked against Mole CLI for Windows **1.39.0**. Re-read `--help` on the installed build before relying on flags.

## Prepare Mole

1. Discover `mo` / `mole` on `PATH` (often `%LOCALAPPDATA%\Programs\mole-cli\mo.cmd`). Read `mo --version` and `mo --help`. Prefer the installed version's documentation over this skill when they differ.
2. If absent, install the **open-source CLI only**. Preferred order:
   - `scoop install mole` when Scoop already has the Mole package.
   - Otherwise download and **inspect** `https://raw.githubusercontent.com/tw93/Mole/windows/quick-install.ps1`, then run it with PowerShell (`-ExecutionPolicy Bypass` only if required). Do not pipe remote code into a shell without that review.
   - Or clone the `windows` branch into `%LOCALAPPDATA%\Programs\mole-cli` and run its `install.ps1` as documented upstream.
3. Do **not** install the separate commercial [Mole for Windows](https://mole.fit/windows) GUI unless the user explicitly asks for that app.
4. After install, refresh `PATH` for the current session and verify `mo --version`. Reuse a working installation. Do not automatically upgrade Mole, grant administrator rights, or change UAC settings.

If installation is blocked, explain the blocker and continue with the **Fallback analysis** section; do not replace Mole with broad deletion commands.

## Boundaries

- Analysis is read-only. A request to analyze or upgrade this skill does not authorize cleaning the machine.
- A cleanup request authorizes reviewed, rebuildable cache/log cleanup within its scope. Respect prior explicit authorization; do not ask again for the same action.
- Preserve personal folders (`Desktop`, `Documents`, `Pictures`, `Videos`, `Downloads`), Recycle Bin contents (unless emptying is explicitly authorized), backups, browser profiles, app data/settings, credentials, Agent runtime/configuration, and active projects by default. Do not infer disposability from size or age.
- App removal requires the user to identify or approve the apps. Removing personal app data, emptying the Recycle Bin, project-artifact purging, Docker pruning, hibernation changes, and elevated system cleanup require explicit scope authorization.
- Do not manually delete inside `C:\Windows\WinSxS`, or wipe `C:\Program Files`, `C:\Program Files (x86)`, or `C:\ProgramData` except a specifically identified cache/leftover path Mole (or the user) selected.
- Administrator authentication and UAC prompts remain user-owned. When access is denied, record incomplete coverage and continue accessible analysis; do not claim the path is empty.
- Never use blanket recursive deletes across cache/log trees, force/yes flags to bypass Mole review, or Mole's internal scripts as an undocumented selective-delete API.
- Before changing app data outside Mole's reviewed flow, check whether related processes are running. Ask the user to close them or skip locked files; do not force-close apps that may have unsaved work.

## Analyze

Record free/used space for the target volume (default `C:`) with PowerShell, for example:

```powershell
Get-PSDrive -Name C | Select-Object Used,Free
Get-Volume -DriveLetter C | Select-Object Size,SizeRemaining
```

Prefer bounded Mole scans before inventing custom trees:

```powershell
mo analyze --json
mo analyze --json C:\
mo analyze --json D:\
```

Inspect JSON for incomplete coverage when present. Report missing coverage; unavailable or blocked zero-byte results are not empty directories. Do not add nested directory totals together as if they were independent reclaimable space.

Use `mo uninstall --list` (JSON when piped) for installed-app inventory. Use `mo status --json` only when health diagnostics help the request. Interactive `mo analyze` can move items to the Recycle Bin: do not activate deletion during analysis.

### Fallback analysis (Mole unavailable)

When Mole cannot run, keep a read-only PowerShell map of `C:` top-level consumers (`Users`, `Windows`, `Program Files`, `Program Files (x86)`, `ProgramData`), large root files (`pagefile.sys`, `hiberfil.sys`, `swapfile.sys`), and the active profile's `AppData` largest children. Explain that apparent `WinSxS` size can overstate reclaimable space because of hard links. Rank candidates by size and recency **signals** only; age alone never authorizes deletion. Do not enumerate filenames from personal folders unless asked.

## Clean (`safe` default; `aggressive` expands scope)

1. Run `mo clean --dry-run`; add `--debug` only if candidate paths need clarification. Inspect actual candidates, sizes, skipped sections, and scope. A preview must not delete candidates. Do not request administrator elevation just to enlarge a preview unless system cleanup is in scope.
2. Review the preview against the boundaries above. **Mole CLI for Windows 1.39.0: `mo clean` and `mo purge` delete permanently; verified `uninstall` leftovers go to the Recycle Bin.** A dry-run is not a saved execution plan; the next run rescans and may include new files.
3. If exclusions are needed, use `mo clean --whitelist` and re-preview. Preserve existing protections. Mole's own settings are tool-owned; do not create a second skill whitelist or replace Mole's wholesale.
4. Execute `mo clean` only when the full resulting scope is authorized and exclusions are verified. Optional flags that widen scope need their own authorization:
   - `--system` — system-level cleanup; run elevated PowerShell only when the user authorized admin system clean.
   - `--game-media` — old game replays/screenshots/recordings.
   - `--gpu-shaders` — GPU shader caches (games will recompile).
5. If the CLI cannot constrain cleanup to the authorized scope, stop deletion and present the concrete candidates/remaining limitation. Never run the broad command merely because part of its preview looks safe. Re-preview after changes or a material delay.
6. For a narrow safe subset Mole cannot isolate (for example a single approved temp path), a documented package-manager or OS cleanup may be used after reviewing its scope. Explain the fallback; do not silently revert to blanket filesystem deletion. `Dism.exe /Online /Cleanup-Image /StartComponentCleanup` only when the user authorized component cleanup; on error 740 or pending operations, report and advise elevated prompt or restart—do not retry destructively.
7. Verify with the same volume measurement and, where useful, the same `mo analyze --json` roots. Consult `mo history --json` when supported, attributing only the current run. Do not retry an uncertain destructive run before checking what actually happened.

`aggressive` means considering additional candidates, not bypassing preview or authorization:

| Need | Mole preview | Impact to review |
| --- | --- | --- |
| Old project artifacts | `mo purge --dry-run` | Permanent removal; verify exact projects, active work, rebuild/download cost |
| Game media / GPU shaders | `mo clean --dry-run` with `--game-media` / `--gpu-shaders` | User media and next-launch recompile cost |
| System-level clean | `mo clean --dry-run --system` (admin) | Elevated; review every system candidate |
| Maintenance | `mo optimize --dry-run` | May change services/caches/disk maintenance; skip steps that need admin unless elevated session is authorized |
| Hibernation file | OS `powercfg /h off` (not Mole) | Removes `hiberfil.sys`; disables Hibernate and Fast Startup—explicit request only |

Confirm flags and selection behavior in the installed documentation. Do not assume every dry-run is noninteractive or that selection persists into execution. Do not automatically append optimization, purge, Docker pruning, or hibernation changes to cleaning.

## Uninstall selected apps

1. Resolve the requested app through `mo uninstall --list` (pipe for JSON when scripting). Verify display name, install location, size, and source (registry / Windows Apps). Watch for duplicate entries.
2. Use `mo uninstall --dry-run` and the documented selection interface to inspect the chosen apps and leftover folders. Keep personal settings, plugins, profiles, game saves, and unrelated app data unless explicitly requested.
3. Execute the documented uninstall flow only for the authorized selection. Leftovers Mole verifies typically go to the Recycle Bin; the app's own uninstaller keeps its own behavior—do not promise immediate free-space recovery. If interactive review cannot be controlled reliably (TTY/selection), give the user the exact selection and command to complete it; do not guess keystrokes or bypass confirmation.
4. Verify the app is gone from inventory/path and report leftovers or incomplete removal. Do not delete related shell/MCP configuration automatically or retry an uncertain uninstall blindly.

## Optimize

Use `mo optimize --dry-run` only for an explicit maintenance request. Review which steps need administrator access (TRIM/defrag, some cache flushes); without elevation Mole skips them—report that rather than forcing UAC. Execute only after authorization.

## Organize (`organize-safe`)

Mole supplies disk analysis, not a file-organization policy. Scan user-selected file zones, propose destinations, and move only clearly in-scope items. Preserve active project paths and do not edit project contents. Do not organize `AppData` wholesale, `C:\Windows`, or Program Files trees.

Keep moves reversible: check destination collisions, preserve originals when identity is ambiguous, and log source/destination paths and date in an agreed user document location. No deletion in this mode.

## Report

Return a compact report with:

- `Before` / `After`: free and used space for the target volume
- `Mole`: version and install path/channel when relevant
- `Distribution` or analyze coverage: largest useful consumers; note partial/blocked scans
- `Candidates`: category, evidence, estimated reclaim, proposed action
- `Actions`: exact commands/paths executed; failures, locked files, skipped items
- `Recovered`: estimated vs measured free-space change (Recycle Bin, snapshots, and concurrent activity can differ)
- `Skipped` / `Next`: protected, uncertain, or waiting on user choice

State clearly when analysis or dry-run only was performed.

## Notes

- Configuration, plugins, caches, logs, and local history may live under different `AppData` subtrees; inspect the application-specific layout before classifying a path outside Mole's preview.
- Apparent directory size can differ from reclaimable space because of hard links, sparse files, junctions, compression, or open handles.
- Prefer repeatable, explainable Mole-backed cleanup over one-off deletion based on a timestamp alone.

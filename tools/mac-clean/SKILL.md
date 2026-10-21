---
name: mac-clean
description: Analyze macOS disk usage, clean junk, uninstall selected apps, or organize files using Mole first, with scope review and before/after verification.
---

# Mac Clean

Use Mole CLI (`mo`, also distributed as `mole`) as the primary disk-analysis, cleanup, and app-uninstall engine. This skill owns scope, authorization, candidate review, and verification. File organization remains a separate, reversible workflow.

## Prepare Mole

1. Discover `mo` / `mole` with `command -v`; read its `--version` and `--help`. Use the installed version's documentation before choosing flags. Examples below were checked against Mole 1.62.0; older versions may differ.
2. If absent, install the open-source CLI with `brew install mole`, then verify version/help. Installing this dependency is part of a requested Mole-backed clean; respect execution approvals. Do not install the separate commercial GUI app.
3. If Homebrew is absent, consult the official [Mole repository](https://github.com/tw93/mole) for the current installation method. Inspect any installer before executing it; do not silently install Homebrew or pipe remote code into a shell. If installation is blocked, explain the blocker and continue read-only analysis with `du` / `df` where useful; do not replace Mole with broad deletion commands.
4. Reuse a working installation. Do not automatically upgrade Mole, install its separate agent skill, change sudo/Touch ID, or grant Full Disk Access.

## Boundaries

- Analysis is read-only. A request to analyze or upgrade this skill does not authorize cleaning the machine.
- A cleanup request authorizes reviewed, rebuildable cache/log cleanup within its scope. Respect prior explicit authorization; do not ask again for the same action.
- Preserve personal folders (`~/Desktop`, `~/Documents`, `~/Pictures`, `~/Movies`, `~/Downloads`), Trash, backups, browser profiles, app data/settings, credentials, Agent runtime/configuration, and active projects by default. Do not infer disposability from size or age.
- App removal requires the user to identify or approve the apps. Removing personal app data, emptying Trash, project-artifact purging, Docker pruning, and changes to app binaries require explicit scope authorization.
- Do not alter SIP/protected settings. Administrator authentication and macOS privacy grants remain user-owned. On `Operation not permitted`, record incomplete coverage and continue accessible analysis; do not claim the path is empty.
- Never use blanket `rm -rf` across cache/log directories, force/yes flags to bypass review, or Mole's internal scripts as an undocumented selective-delete API.

## Analyze

Record filesystem free space with `df -k` for the affected volume. Prefer bounded scans of the relevant user/work directory before scanning the entire disk:

```sh
mo analyze --json <absolute-scan-root>
```

Inspect `scan_status` at the root and entry levels when available: `partial` and `unavailable` are incomplete coverage even with exit code 0. Report missing coverage; unavailable zero-byte results are not empty directories. Do not add nested directory totals together.

Use `mo uninstall --list` for installed-app inventory where supported. Use `mo status --json` only when health diagnostics help the request. Interactive `mo analyze` can also delete files: do not activate deletion during analysis. For versions lacking JSON, use their documented read-only interface or bounded `du` scans; do not invent flags.

## Clean (`safe` default; `aggressive` expands scope)

1. Run `mo clean --dry-run`; use `--debug` only if candidate paths need clarification. Inspect actual candidates, sizes, skipped sections, and scope. A preview may write Mole's own reports/cache but must not delete candidates. Do not request administrator access just to enlarge a preview unless system cleanup is in scope.
2. Review the preview against the boundaries above. **Mole 1.62.0 `mo clean` empties user Trash by default and permanently deletes cleanup candidates.** A dry-run is not a saved execution plan; the next run rescans and may include new files.
3. If exclusions are needed, use the installed version's documented `mo clean --whitelist` protections and re-preview. Preserve existing protections. Mole's own native settings are tool-owned; do not create a second skill configuration or replace the whitelist wholesale.
4. Execute `mo clean` only when the full resulting scope is authorized and exclusions are verified. If the CLI cannot constrain cleanup to that scope, stop deletion and present the concrete candidates/remaining limitation. Never run the broad command merely because part of its preview is safe. Re-preview after changes or a material delay.
5. For a narrow safe subset that Mole cannot isolate, a documented package-manager cleanup may be used after reviewing its scope. Explain the fallback; do not silently revert to blanket filesystem deletion.
6. Verify with the same scan roots and filesystem measurement. Consult `mo history --json` where supported, attributing only the current run; ambiguous/interrupted history does not prove completion. Do not retry an uncertain destructive run before checking what actually happened.

`aggressive` means considering additional candidates, not bypassing preview or authorization:

| Need | Mole preview | Impact to review |
| --- | --- | --- |
| Old project artifacts | `mo purge --dry-run` | Permanent removal; verify exact projects, active work, rebuild/download cost |
| Old installers | `mo installer --dry-run` | Permanent removal from personal file zones; inspect exact files |
| Intel slices in apps | `mo slim --dry-run` | Changes app binaries; require explicit request |
| Maintenance | `mo optimize --dry-run` | May change services/caches; use only for a relevant maintenance request |

Confirm flags and selection behavior in the installed documentation. Do not assume every dry-run is noninteractive or that selection persists into execution. Do not automatically append optimization, slimming, dependency-cache purge, or Docker pruning to cleaning.

## Uninstall selected apps

1. Resolve the requested app through `mo uninstall --list` where available; verify exact path, bundle identity, duplicate copies, and install source.
2. Use `mo uninstall --dry-run` and the documented selection interface to inspect the chosen app and its associated files. Keep personal settings, plugins, profiles, shared containers, and unrelated app data unless explicitly requested. Do not add `--with-data` or `--permanent` by default.
3. Execute the documented uninstall flow only for the authorized selection. Mole 1.62.0 normally moves uninstalled files to Trash; do not promise immediate disk-space recovery. If interactive review cannot be controlled reliably with available tools, give the user the exact selection and command to complete it; do not guess keystrokes or bypass confirmation.
4. Verify the exact app path/inventory and report leftovers or incomplete removal. Do not delete related shell/MCP configuration automatically or retry an uncertain uninstall blindly.

## Organize (`organize-safe`)

Mole supplies disk analysis, not a file-organization policy. Scan user-selected file zones, propose destinations, and move only clearly in-scope items. Preserve active project paths and do not edit project contents. Do not organize `~/Library`, `/Library`, `/System`, or `/private/var`.

Keep moves reversible: check destination collisions, preserve originals when identity is ambiguous, and log source/destination paths and date in an agreed user document location. Do not create a universal workspace hierarchy or move whole repositories without user direction. No deletion in this mode.

## Report

Report scan coverage and largest useful candidates, Mole version, reviewed/executed actions, protected/skipped items, and before/after figures. Distinguish estimated removable bytes, measured path-size reduction, and actual filesystem free-space change (APFS snapshots, Trash, and concurrent activity can make them differ). State when analysis/preview only was performed. Offer further high-impact actions only when concrete candidates justify them.

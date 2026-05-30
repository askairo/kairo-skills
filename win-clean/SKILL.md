---
name: win-clean
description: Safely clean C drive space on Windows by prioritizing cache and temporary files, then optionally running deeper cleanup with explicit confirmation for risky actions.
---

# Win Clean

Use this skill when the user asks to clean Windows disk space, especially `C:`. Default to safe cleanup and avoid touching personal files, app binaries, or system-critical folders unless the user explicitly asks.

## Goals

- Recover space with low-risk actions first.
- Show before/after free space and what was cleaned.
- Gate higher-risk actions behind explicit user confirmation.

## Safety Rules

- Do not delete from personal data folders by default: `Desktop`, `Documents`, `Pictures`, `Videos`, `Downloads`.
- Do not delete app install trees by default: `C:\Program Files`, `C:\Program Files (x86)`, `C:\ProgramData` (except known cache subpaths).
- Never manually delete inside `C:\Windows\WinSxS`.
- Keep Codex runtime/cache untouched unless user explicitly requests it.
- For each delete operation: prefer targeted known-cache paths and tolerate in-use files.

## Default Workflow (Safe Mode)

1. Baseline check:
   - Read free/used space for `C:`.
   - Identify top cache candidates and report estimated size.
2. Clean low-risk caches:
   - User temp: `%TEMP%`
   - Windows temp: `C:\Windows\Temp`
   - Windows update download cache: `C:\Windows\SoftwareDistribution\Download`
   - Delivery Optimization cache:
     `C:\Windows\ServiceProfiles\NetworkService\AppData\Local\Microsoft\Windows\DeliveryOptimization\Cache`
   - NVIDIA App update artifacts:
     `C:\ProgramData\NVIDIA Corporation\NVIDIA App\UpdateFramework\ota-artifacts`
   - Common updater caches in user local appdata:
     `CrashDumps`, `*-updater`, `npm-cache` (if present)
3. Component cleanup:
   - Run:
     `Dism.exe /Online /Cleanup-Image /StartComponentCleanup`
   - If blocked by pending actions, report and advise restart, then rerun.
4. Final verification:
   - Report free space delta (GB), remaining major consumers, and any skipped items.

## Optional Actions (Explicit Confirmation Required)

- Disable hibernation to remove `hiberfil.sys`:
  `powercfg /h off`
  - Impact: disables Hibernate and Fast Startup.
- Clear developer caches:
  - Maven: `C:\Users\<user>\.m2\repository`
  - NuGet: `C:\Users\<user>\.nuget\packages`
  - Gradle: `C:\Users\<user>\.gradle\caches`
- Remove stale empty directories in non-system paths.
- Remove old large logs (for example stale `CbsPersist_*.log`) while keeping active logs.

## Output Format

Return a compact summary:

- `Before`: free/used GB
- `Actions`: cleaned paths + notes on failures/in-use files
- `After`: free/used GB
- `Recovered`: total GB gained
- `Next`: optional high-impact actions user can approve

## Notes

- WinSxS apparent size often overstates reclaimable space due to hard links.
- If DISM succeeds but gain is small, this is normal.
- Prefer repeatable cleanup over risky one-off deletes.

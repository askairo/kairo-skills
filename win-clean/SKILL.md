---
name: win-clean
description: 安全清理 Windows C 盘空间，优先处理缓存和临时文件，并在需要更激进操作时要求用户明确确认。
---

# Win Clean

用于清理 Windows 磁盘空间，尤其是 `C:`。默认只做安全清理，不主动碰个人文件和系统关键目录。

## 目标

- 优先回收低风险空间。
- 展示清理前后空间变化。
- 高风险操作必须明确确认。

## 安全原则

- 默认不删除 `Desktop`、`Documents`、`Pictures`、`Videos`、`Downloads`。
- 默认不删除 `C:\Program Files`、`C:\Program Files (x86)`、`C:\ProgramData`。
- 不要手动删除 `C:\Windows\WinSxS`。
- 优先清理已知缓存和临时目录。

## 默认流程

1. 先看 `C:` 当前剩余空间。
2. 清理常见缓存：
   - `%TEMP%`
   - `C:\Windows\Temp`
   - `C:\Windows\SoftwareDistribution\Download`
   - Delivery Optimization 缓存
   - 常见更新器缓存和构建缓存
3. 执行组件清理。
4. 汇总清理前后差值和未处理项。

## 模式

- `safe`：默认模式，只做低风险清理。
- `aggressive`：只有用户明确要求时才进入，包含更激进但仍可控的清理动作。

## 输出要求

- 清理前可用空间
- 已清理路径
- 失败或被占用的路径
- 清理后可用空间
- 下一步可选动作

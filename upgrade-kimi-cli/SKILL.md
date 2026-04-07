---
name: upgrade-kimi-cli
description: 自动检测并将 Kimi CLI (kimi-code) 升级到最新版本。支持 uv tool 和 pip 两种安装方式。当用户请求更新/升级 kimi cli、kimi-code、检查最新版本并自动更新时触发。
---

# Upgrade Kimi CLI

当用户请求升级 Kimi CLI 时，执行以下步骤：

1. 运行 `kimi --version` 获取当前版本。
2. 运行 `pip index versions kimi-code` 获取 PyPI 上的最新版本。
3. 如果当前版本已是最新，告知用户无需更新。
4. 如果存在新版本：
   - 优先检测是否通过 `uv` 安装（`uv tool list` 中包含 `kimi-code`），如果是则执行 `uv tool upgrade kimi-code`。
   - 否则执行 `pip install --upgrade kimi-code`。
5. 升级完成后再次运行 `kimi --version` 验证。

## 注意

- 在 Windows PowerShell 中执行命令时，直接使用命令本身，不需要 `2>nul` 或 `||` 等 cmd 语法
- 例如：`pip index versions kimi-code` 而不是 `pip index versions kimi-code 2>nul || ...`

可直接调用脚本 `scripts/upgrade.py` 完成上述流程。

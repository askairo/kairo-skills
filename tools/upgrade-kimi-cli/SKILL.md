---
name: upgrade-kimi-cli
description: 自动检测并将 Kimi CLI (kimi-cli) 升级到最新版本。支持 uv tool 和 pip 两种安装方式。当用户请求更新/升级 kimi cli、kimi-code、检查最新版本并自动更新时触发。
---

# Upgrade Kimi CLI

当用户请求升级 Kimi CLI 时，执行以下步骤：

1. 运行 `kimi --version` 获取当前版本。
2. 调用 PyPI JSON API 获取 `kimi-cli` 的最新版本。
3. 如果当前版本已是最新，告知用户无需更新。
4. 如果存在新版本：
   - 检测是否通过 `uv tool` 安装（检查 `~/.local/share/uv/tools/kimi-cli/uv-receipt.toml` 或 `uv tool list` 输出），如果是则执行 `uv tool upgrade kimi-cli`
   - 否则尝试使用 `pip3`、`pip` 或 `python -m pip` 执行 `pip install --upgrade kimi-cli`
5. 升级完成后再次运行 `kimi --version` 验证。

## 注意

- 包名为 `kimi-cli`，不是 `kimi-code`
- 优先检测 uv 安装方式，通过检查 receipt 文件比 `uv tool list` 更可靠
- 使用 PyPI JSON API 获取最新版本，不依赖 `pip index versions`

可直接调用脚本 `scripts/upgrade.py` 完成上述流程。

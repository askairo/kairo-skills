---
name: upgrade-kimi-cli
description: 自动检测并将 Kimi CLI（kimi-cli）升级到最新版本。支持 uv tool 和 pip 两种安装方式，适用于更新、升级或检查最新版本并自动执行升级的场景。
---

# 升级 Kimi CLI

当用户请求升级 Kimi CLI 时，按下面步骤执行：

1. 运行 `kimi --version` 获取当前版本。
2. 调用 PyPI JSON API 获取 `kimi-cli` 的最新版本。
3. 如果当前版本已经是最新，直接告诉用户无需更新。
4. 如果有新版本：
   - 先判断是否通过 `uv tool` 安装
   - 如果是，执行 `uv tool upgrade kimi-cli`
   - 否则尝试 `pip3`、`pip` 或 `python -m pip install --upgrade kimi-cli`
5. 升级完成后再次运行 `kimi --version` 验证。

## 注意

- 包名是 `kimi-cli`，不是 `kimi-code`。
- 优先通过 receipt 文件判断是否是 `uv` 安装，比只看 `uv tool list` 更可靠。
- 获取最新版本时使用 PyPI JSON API，不依赖 `pip index versions`。

可直接调用脚本 `scripts/upgrade.py` 完成上述流程。

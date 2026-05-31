---
name: release-flow
description: 通用发布流水线技能。按“版本->构建->产物校验->提交->打Tag->Release->上传资产”执行，默认零配置自动识别项目类型；仅在歧义时使用最小配置覆盖。
---

# release-flow

## 目标

将项目发布流程抽象为统一步骤，并尽量做到零配置自动识别：

1. 版本识别与升级
2. 构建与打包
3. 产物发现与校验
4. 提交与打 Tag
5. 创建或更新 Release
6. 上传资产并清理旧命名资产

## 执行原则

- 默认零配置：优先自动识别项目类型与构建命令。
- 最小交互：无法可靠判断时，再向用户确认关键选项。
- 失败可恢复：每一步都产出明确状态，支持从中断点继续。
- 命名规范：发布资产默认带版本号，避免无版本文件名。

## 识别顺序

1. `tauri`：存在 `src-tauri/tauri.conf.json`。
2. `node/web`：存在 `package.json`。
3. `python`：存在 `pyproject.toml` 或 `setup.py`。
4. `go`：存在 `go.mod`。
5. `rust`：存在 `Cargo.toml`（非 tauri）。

若多个类型同时命中，按用户当前目标与仓库上下文择优，并在执行前说明假设。

## 通用步骤模板

1. 读取当前版本并确定下一版本（patch/minor/major 或用户指定）。
2. 同步更新版本文件（按项目类型自动识别）。
3. 执行构建命令，收集产物。
4. 校验关键产物存在且命名含版本号。
5. 运行最小必要校验（如 `build/check`）。
6. `git add/commit/push`。
7. 创建或更新 `vX.Y.Z` Release。
8. 上传资产；若存在无版本旧资产，按策略清理。
9. 输出发布结果：版本、commit、tag、release 链接、资产清单。

## Tauri 默认策略（内置适配）

- 版本文件：`package.json`、`src-tauri/tauri.conf.json`、`src-tauri/Cargo.toml`（必要时含 `Cargo.lock`）。
- 构建命令：`npm run tauri build`（或用户项目约定）。
- 常见产物：
  - `src-tauri/target/release/bundle/nsis/*-setup.exe`
  - `src-tauri/target/release/bundle/msi/*.msi`
  - `src-tauri/target/release/*.exe`（绿色版）
- 绿色版重命名建议：`<Product>_<version>_x64.exe`。

### Tauri 跨平台产物（P18 推荐）

- CI 校验矩阵：`windows-latest` + `macos-latest`。
- Release 产物矩阵：至少包含 Windows 安装包（`nsis/msi`）和 macOS 安装包（`dmg`）。
- 推荐把“校验流水线”和“发布流水线”分离：
  - `ci.yml`：`npm ci`、`npm run build`、`cargo check`
  - `release.yml`：tag/手动触发，执行 `tauri build` 并上传资产
- 资产命名统一包含版本号，例如 `Clicky_v0.1.4_x64-setup.exe`、`Clicky_v0.1.4.dmg`。

## 最小可选配置（仅在需要时）

可在仓库根目录放置 `.release-flow.json` 覆盖默认行为，例如：

```json
{
  "releaseProvider": "github",
  "versionStrategy": "patch",
  "assetPatterns": [
    "src-tauri/target/release/bundle/nsis/*-setup.exe",
    "src-tauri/target/release/bundle/msi/*.msi",
    "src-tauri/target/release/Clicky_*_x64.exe"
  ],
  "removeUnversionedAssets": true
}
```

### Clicky 示例（Win + Mac）

```json
{
  "releaseProvider": "github",
  "versionStrategy": "patch",
  "assetPatterns": [
    "src-tauri/target/release/bundle/nsis/*-setup.exe",
    "src-tauri/target/release/bundle/msi/*.msi",
    "src-tauri/target/release/bundle/dmg/*.dmg"
  ],
  "removeUnversionedAssets": true
}
```

## Homebrew Tap 兼容（阶段二）

- 该技能应预留 tap 发布能力，但默认关闭，避免影响常规发布。
- 建议新增可选配置字段（仅在用户明确启用时生效）：

```json
{
  "homebrewTap": {
    "enabled": false,
    "repo": "askairo/homebrew-tap",
    "caskPath": "Casks/clicky.rb",
    "assetForMac": "src-tauri/target/release/bundle/dmg/*.dmg"
  }
}
```

- 启用后流程追加：
  1. 读取新版本与 mac 资产 URL
  2. 计算 `sha256`
  3. 更新 cask 版本、URL、校验值
  4. 提交并推送 tap 仓库

## 输出要求

- 必须给出：
  - 新版本号
  - commit id
  - tag
  - release 链接
  - 资产列表（文件名 + 大小）
- 若某步未执行（如网络失败），明确标注阻塞点和下一步命令。

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
- 跨平台明确：构建机平台与目标资产不一致时，提前预警并给出替代路径。

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

## 发布前强制预检（新增）

每次执行前，必须先做以下预检并在输出中写明结果：

1. 分支模型预检
   - 优先读取远端默认分支（`origin/HEAD`）和本地现有分支。
   - 若仓库无 `develop`，不得强行要求 GitFlow；默认采用当前仓库分支策略。
   - 若工具硬编码要求 `develop`，先提示风险，再提供替代执行路径（手动分步）。

2. CLI 兼容预检
   - 检测 `release-flow` CLI 是否存在 Windows 下 `git commit -m '...` 单引号兼容问题。
   - 一旦命中该风险，直接切换“手动安全流程”：
     - 升版
     - 构建
     - `git commit -m "Release vX.Y.Z"`
     - `git tag vX.Y.Z`
     - 创建/上传 Release

3. 平台产物预检
   - 根据当前 OS 判断可构建产物：
     - Windows: `exe/msi/nsis`
     - macOS: `dmg/app`
   - 若配置要求包含异平台资产（如 Windows 上要求 `dmg`），必须提前提示“本机无法生成”，并给出：
     - CI 矩阵（`windows-latest + macos-latest`）
     - 或在对应平台补构建后再补传 Release。

## 中断恢复流程（新增）

当流程中断（例如已切 `release/x.y.z` 但 commit 失败）时，必须进入恢复模式而不是从头重跑：

1. 检查当前分支、工作区、版本文件是否已变更。
2. 检查 tag 是否已创建。
3. 检查 Release 是否已存在。
4. 从最近未完成步骤继续执行，并在最终输出明确“恢复执行”。

## Tauri 默认策略（内置适配）

- 版本文件：`package.json`、`src-tauri/tauri.conf.json`、`src-tauri/Cargo.toml`（必要时含 `Cargo.lock`）。
- 构建命令：`npm run tauri build`（或用户项目约定）。
- 常见产物：
  - `src-tauri/target/release/bundle/nsis/*-setup.exe`
  - `src-tauri/target/release/bundle/msi/*.msi`
  - `src-tauri/target/release/bundle/dmg/*.dmg`
  - `src-tauri/target/release/*.exe`（绿色版）
- 绿色版重命名建议：`<Product>_<version>_x64.exe`。

### Tauri 跨平台产物（P18 推荐）

- CI 校验矩阵：`windows-latest` + `macos-latest`。
- Release 产物矩阵：至少包含 Windows 安装包（`nsis/msi`）和 macOS 安装包（`dmg`）。
- 推荐把“校验流水线”和“发布流水线”分离：
  - `ci.yml`：`npm ci`、`npm run build`、`cargo check`
  - `release.yml`：tag/手动触发，执行 `tauri build` 并上传资产
- 资产命名统一包含版本号，例如 `Clicky_v0.1.4_x64-setup.exe`、`Clicky_v0.1.4_aarch64.dmg`。

## 最小可选配置（仅在需要时）

可在仓库根目录放置 `.release-flow.json` 覆盖默认行为，例如：

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
    "enabled": true,
    "repo": "askairo/homebrew-tap",
    "caskName": "clicky",
    "macArtifactPattern": "_aarch64.dmg",
    "appName": "Clicky",
    "desc": "Cross-platform environment profile switcher for Spring Boot",
    "homepage": "https://github.com/askairo/Clicky"
  }
}
```

- 启用后流程追加：
  1. 读取新版本与 mac 资产 URL（推荐基于 GitHub Release）
  2. 计算 `sha256`
  3. 生成/更新 `Casks/clicky.rb`（版本、URL、`sha256`）
  4. 提交并推送 tap 仓库

## 输出要求

- 必须给出：
  - 新版本号
  - commit id
  - tag
  - release 链接
  - 资产列表（文件名 + 大小）
- 若某步未执行（如网络失败），明确标注阻塞点和下一步命令。
- 若受平台限制导致部分资产缺失，必须显式列出“缺失资产及原因”。

---
name: sync-skills
description: 同步 Skills 项目目录与用户目录的 skills。对比差异，支持双向同步，通过环境变量配置路径。
---

# Skills 同步工具

同步 Skills 项目目录（Git 管理）与用户目录（Agent 使用）的 skills。

## 环境变量配置

```powershell
# 必需：项目目录路径
$env:SKILLS_PROJECT_DIR = "D:\private-vs-space\kimi-skills"

# 可选：用户目录路径（默认使用 Kimi CLI 标准路径）
$env:SKILLS_USER_DIR = "C:\Users\admin\.config\agents\skills"
```

## 使用方法

### 1. 检查差异（默认）

```powershell
python scripts/sync.py
```

显示：
- 项目目录独有的 skills
- 用户目录独有的 skills
- 两边都有但内容不同的 skills

### 2. 项目 → 用户（install）

将项目开发的 skills 同步到用户目录，供 Agent 使用：

```powershell
python scripts/sync.py --mode install
```

### 3. 用户 → 项目（dev）

将在其他目录创建的 skills 拉取到项目目录：

```powershell
python scripts/sync.py --mode dev
```

### 4. 双向同步（sync）

合并两边的 skills：

```powershell
python scripts/sync.py --mode sync
```

## 工作流程

### 开发新 skill 时

1. 在项目中创建/修改 skill
2. 测试完成后运行：`python scripts/sync.py --mode install`
3. 提交到 Git

### 在其他目录创建 skill 后

1. 运行：`python scripts/sync.py --mode dev`
2. 检查同步到项目的 skill
3. 提交到 Git

## 冲突处理

- **项目独有** → 提示是否 install 到用户目录
- **用户独有** → 提示是否 dev 到项目目录
- **内容不同** → 显示差异，让用户选择覆盖方向

## 注意事项

- 同步前会自动备份目标目录（`.backup.时间戳`）
- 删除操作需要显式确认
- 建议先运行检查模式，确认后再执行同步

---
name: kickoff-flow
description: 将个人新项目的启动流程标准化为可执行的本地工作区。用于创建或重命名 GitHub 仓库、拉取到本地、建立命名规范、解析项目文档根目录，并生成 skill 定义的启动文档集。
---

# Kickoff Flow

## 目标

把“一个想法”变成可启动、可推进的新项目，明确分开：

- 代码工作区
- 项目管理文档区

这个流程只负责项目初始化，不负责功能实现。

## 本地配置

使用本机配置保存稳定的、用户私有的文档根目录。配置文件不要放进项目仓库。

- 路径配置：`<CODEX_HOME>/local-config/kickoff-flow/paths.yaml`
- 备用路径配置：`<HOME>/.codex/local-config/kickoff-flow/paths.yaml`

推荐配置结构：

```yaml
version: 1

docs:
  root: <absolute-project-docs-root>
```

- `docs.root` 是用户自己的项目文档根目录，例如 Obsidian 的 `03-req`。
- skill 负责 `docs.root` 下的结构：创建 `<docs.root>/<project_name>/00-overview.md` 和 `<docs.root>/<project_name>/10-roadmap.md`。
- 优先使用已配置路径，不要靠记忆推导。
- 如果没有配置且用户也没提供，就先询问 `docs.root`，再写入本地配置。

## 流程

1. 收集启动信息。
   - 必填：项目名、一句话目标。
   - 可选：GitHub 可见性、本地目录、技术栈、文档根目录。
2. 统一命名。
   - 优先使用简短的 lowercase kebab-case。
   - 仓库名、本地目录名、文档目录名保持一致。
3. 创建或重命名 GitHub 仓库。
   - 仓库不存在就创建。
   - 项目名变更时同步重命名并更新本地 `origin`。
4. 准备本地工作区。
   - 在用户选定目录下克隆仓库。
   - 检查远端和默认分支。
5. 在解析后的文档目录下创建项目文档。
   - 文档根目录优先级：
     1. 当前请求显式提供
     2. 本地路径配置
   - 如果无法解析，就先询问用户，再写入本地配置。
   - 创建目录：`<docs-root>/<project-name>`
   - 创建：
     - `00-overview.md`：项目定义
     - `10-roadmap.md`：执行计划和校验跟踪
6. 保持代码仓库干净。
   - 仓库根目录只放代码、配置和运行时文档。
   - 如果有独立文档根目录，就不要把项目管理文档塞进代码仓库根目录。
7. 确认启动完成。
   - GitHub 仓库名正确。
   - 本地目录名正确。
   - `00-overview.md` 存在。
   - `10-roadmap.md` 存在。

## 模板

- Use `references/00-overview.template.md`
- Use `references/10-roadmap.template.md`

## 说明

- 这个 skill 故意保持通用，具体需求因项目而异。
- 启动完成后，后续实现交给任务型 skills。

## 脚本辅助

Use `scripts/init_project_docs.ps1` to generate kickoff docs automatically:

```powershell
pwsh -File scripts/init_project_docs.ps1 \
  -ProjectName envflow \
  -Objective "Build a lightweight desktop environment switch tool" \
  -RepoUrl "https://github.com/askairo/envflow" \
  -LocalRepoPath "<absolute-local-repo-path>" \
  -DocsRoot "<absolute-docs-root>" \
  -SaveConfig
```

It creates/updates:

- `<docs-root>/<project-name>/00-overview.md`
- `<docs-root>/<project-name>/10-roadmap.md`

If neither local config nor explicit docs root is available, the script fails with a clear message instead of using a hard-coded docs path.

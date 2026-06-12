# Kairo Skills

English | [中文](#chinese)

<a id="english"></a>

Personal skills repository for Agent, Codex, and Kimi workflows.

Remote repository:

```text
https://github.com/askairo/kairo-skills
```

## Current Status

- One skill per root-level directory for simple GitHub path installs.
- `skills-loop` is the source-of-truth for publish, sync, reinstall, and verify.
- `p-ordered` is the project-level skill for project docs, structure, and architecture boundaries.

## Install

Publish local changes and update the current Agent:

```powershell
python skills-loop\scripts\sync.py publish-and-update --skill hexo-push --message "feat: improve hexo push"
```

Install from GitHub into an Agent runtime:

```powershell
python skills-loop\scripts\sync.py install --repo askairo/kairo-skills --path hexo-push --agent-dir C:\Users\admin\.codex\skills
```

Update an installed skill with recorded source metadata:

```powershell
python skills-loop\scripts\sync.py update --skill hexo-push --agent-dir C:\Users\admin\.codex\skills
```

## Local Development

Recommended flow:

```text
local source repository -> GitHub -> current Agent skills runtime directory
```

Make the change in this repository first, validate it, commit and push it, then use `skills-loop` to pull the latest version back into the runtime copy.

## Repository Layout

```text
kairo-skills/
├── README.md
├── dialogue-refine/
├── entity-design/
├── hexo-push/
├── merge-to/
├── p-bootstrap/
├── p-ordered/
├── p-task/
├── skills-loop/
├── upgrade-kimi-cli/
└── weekly-report/
```

Physical grouping such as `blog/` or `work/` is intentionally deferred. Project-discovery skills like `p-ordered` can still define their own project-level folders, such as `00/`, `10/`, `20/`, and `tasks/`, without affecting the root skill layout.

## Config and Storage

- Prefer natural language, explicit parameters, config files, and auto-discovery.
- Use environment variables only as fallback compatibility, not as the primary configuration path.
- Installed skills from GitHub should include `.skill-source.json` metadata.
- If a repository needs bilingual README content, keep it in a single `README.md` and switch sections with internal links.

## Notes

- `p-task` still drives task-specific implementation, validation, and handoff.
- `p-ordered` defines the project-level architecture and document order before task execution starts.
- The root README stays concise so the actual skill folders remain the source of truth.

## Related Docs

- [`skills-loop/SKILL.md`](skills-loop/SKILL.md)
- [`p-bootstrap/SKILL.md`](p-bootstrap/SKILL.md)
- [`p-ordered/SKILL.md`](p-ordered/SKILL.md)
- [`p-task/SKILL.md`](p-task/SKILL.md)

---

<a id="chinese"></a>

[English](#english) | 中文

个人 Agent/Codex/Kimi skills 仓库。

远程仓库：

```text
https://github.com/askairo/kairo-skills
```

## 当前状态

- 根目录保持“一个 skill 一个文件夹”，便于 GitHub path 安装。
- `skills-loop` 是发布、同步、回装、校验的统一闭环。
- `p-ordered` 负责项目级文档顺序、架构边界和启动约束。

## 安装

发布本地修改并更新当前 Agent：

```powershell
python skills-loop\scripts\sync.py publish-and-update --skill hexo-push --message "feat: improve hexo push"
```

从 GitHub 安装到 Agent 运行目录：

```powershell
python skills-loop\scripts\sync.py install --repo askairo/kairo-skills --path hexo-push --agent-dir C:\Users\admin\.codex\skills
```

更新已记录来源元数据的 skill：

```powershell
python skills-loop\scripts\sync.py update --skill hexo-push --agent-dir C:\Users\admin\.codex\skills
```

## 本地开发

推荐流程：

```text
本地源码仓库 -> GitHub -> 当前 Agent skills 运行目录
```

先在本仓库修改、验证、提交并推送，再通过 `skills-loop` 拉回最新版本覆盖运行时目录。

## 目录结构

```text
kairo-skills/
├── README.md
├── dialogue-refine/
├── entity-design/
├── hexo-push/
├── merge-to/
├── p-bootstrap/
├── p-ordered/
├── p-task/
├── skills-loop/
├── upgrade-kimi-cli/
└── weekly-report/
```

暂不做 `blog/`、`work/` 这类物理分组。项目探索类技能如 `p-ordered` 可以自己定义项目级目录，例如 `00/`、`10/`、`20/` 和 `tasks/`，但不影响根目录 skill 布局。

## 配置与存储

- 优先使用自然语言、显式参数、配置文件和自动发现。
- 环境变量只作为兜底兼容，不作为主配置路径。
- 来自 GitHub 的已安装 skill 应包含 `.skill-source.json` 元数据。
- 如果仓库需要双语 README 内容，统一放在一个 `README.md` 里，用文内链接切换。

## 说明

- `p-task` 仍然负责具体任务的拆解、实现、验证和交付。
- `p-ordered` 负责在任务执行前先把项目级文档和架构顺序理清。
- 根目录 README 保持简洁，具体规则以各 skill 目录内文件为准。

## 相关文档

- [`skills-loop/SKILL.md`](skills-loop/SKILL.md)
- [`p-bootstrap/SKILL.md`](p-bootstrap/SKILL.md)
- [`p-ordered/SKILL.md`](p-ordered/SKILL.md)
- [`p-task/SKILL.md`](p-task/SKILL.md)

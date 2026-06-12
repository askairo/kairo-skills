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
- `skills-loop` is the operational backbone for publish, sync, reinstall, and verify.
- `p-bootstrap` starts a new project.
- `p-ordered` normalizes project structure and docs.
- `p-task` executes concrete tasks.

## `skills-loop`

Use `skills-loop` whenever a skill needs to be created, edited, published, synced, reinstalled, or repaired. It keeps the source repo, GitHub, and the current Agent runtime copy in sync.

Typical flow:

1. Edit the skill in this repository.
2. Validate and commit the change.
3. Publish to GitHub.
4. Pull the latest version back into the runtime copy.

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

Recommended flow for any skill change:

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

- `skills-loop` is the only skill that should be used to keep skill source and runtime copies aligned.
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
- `skills-loop` 是发布、同步、回装、校验的统一闭环，也是技能维护的核心入口。
- `p-bootstrap` 负责新项目启动。
- `p-ordered` 负责项目结构和文档秩序。
- `p-task` 负责具体任务执行。

## `skills-loop`

只要涉及 skill 的创建、修改、发布、同步、回装、修复，就优先用 `skills-loop`。它负责把本地源码仓库、GitHub 和当前 Agent 运行目录保持一致。

典型流程：

1. 在本仓库修改 skill。
2. 校验并提交。
3. 发布到 GitHub。
4. 回装到当前运行目录。

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

- `skills-loop` 是技能维护的核心入口，其他 skill 不负责同步源码和运行时副本。
- 根目录 README 保持简洁，具体规则以各 skill 目录内文件为准。

## 相关文档

- [`skills-loop/SKILL.md`](skills-loop/SKILL.md)
- [`p-bootstrap/SKILL.md`](p-bootstrap/SKILL.md)
- [`p-ordered/SKILL.md`](p-ordered/SKILL.md)
- [`p-task/SKILL.md`](p-task/SKILL.md)

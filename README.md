# Kairo Skills

个人 Agent/Codex/Kimi skills 仓库。远程仓库：

```text
https://github.com/askairo/kairo-skills
```

## 维护模型

本仓库是 skills 的长期源码仓库；各 Agent 的用户目录只是运行时安装目标。

推荐流程：

```text
本地源码仓库 -> GitHub -> 当前 Agent skills 运行目录
```

也就是说，修改 skill 时先改本仓库，验证后提交并推送，再通过 `skills-loop` 从 GitHub 拉取并覆盖当前 Agent 的已安装 skill。

## Skills 列表

| Skill | 分组 | 描述 |
| --- | --- | --- |
| `hexo-push` | 博客发布 | 将 Clippings 文章转换为 Hexo 文档并发布 |
| `dialogue-refine` | 博客发布 | 将 AI 对话记录提炼为结构化 Hexo 文章 |
| `skills-loop` | Skills 管理 | 基于 GitHub 的 skills 迭代闭环：发布、同步、回装、校验 |
| `upgrade-kimi-cli` | 工具维护 | 自动检测并升级 Kimi CLI |
| `merge-to` | 开发流程 | 将当前分支合并到 `dev` / `sit` 并推送 |
| `weekly-report` | 业务文档 | 根据截图或任务列表生成周报 |
| `entity-design` | 业务设计 | 根据原型和业务流程设计领域实体 |
| `mac-clean` | 系统维护 | 在 macOS 上按安全优先策略清理存储空间 |

## 安装或更新

推荐使用 `skills-loop`：

```powershell
python skills-loop\scripts\sync.py install --repo askairo/kairo-skills --path hexo-push --agent-dir C:\Users\admin\.codex\skills
```

更新已记录来源的 skill：

```powershell
python skills-loop\scripts\sync.py update --skill hexo-push --agent-dir C:\Users\admin\.codex\skills
```

发布本地修改并更新当前 Agent：

```powershell
python skills-loop\scripts\sync.py publish-and-update --skill hexo-push --message "feat: improve hexo push"
```

## 目录结构

当前保持“根目录一个 skill 一个文件夹”，便于 GitHub path 安装：

```text
kairo-skills/
├── README.md
├── dialogue-refine/
├── entity-design/
├── hexo-push/
├── mac-clean/
├── merge-to/
├── skills-loop/
├── upgrade-kimi-cli/
└── weekly-report/
```

暂不按物理目录拆分为 `blog/`、`work/` 等分类；分组先维护在 README 表格中。等 skills 数量明显增多后，再考虑目录分组，并同步升级 `skills-loop` 对嵌套路径的默认支持。

## 配置约定

- 优先使用自然语言/显式参数、配置文件和自动发现。
- 环境变量只作为兜底兼容，不作为主推荐配置方式。
- 运行时目录中的 skill 如果来自 GitHub，应包含 `.skill-source.json` 来源元数据。

## 更新日志

- 2026-05-23: 合并 Codex runtime 中的 `entity-design`、`merge-to`、`weekly-report`
- 2026-05-31: 新增 `mac-clean`，沉淀 macOS 安全清理与分级回收流程
- 2026-05-29: 将 `sync-skills` 升级并重命名为 `skills-loop`，支持在任意工作目录触发闭环同步
- 2026-05-23: 将 `sync-skills` 重构为 GitHub 驱动的 skills 管理工具
- 2026-05-23: 优化 `hexo-push` 发布前预览、分类标签确认和 deploy 重试流程
- 2026-04-07: 初始化仓库，添加 `hexo-push` 和 `upgrade-kimi-cli`

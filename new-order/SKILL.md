---
name: new-order
description: 将新项目整理成有秩序的项目级文档、架构边界和执行计划。适用于新项目启动、已有文档碎片化，或需要先从已配置的文档根目录理顺项目结构再进入 task-dev-flow 的场景。
---

# New Order

用于在任务开发前，先把项目级文档、架构边界和推进顺序理清楚。

## 适用场景

- 新项目刚开始，没有稳定的文档结构。
- 旧项目文档散乱、重复、过时。
- 需要先明确整体架构，再进入任务拆解和实现。

## 文档根目录

- 优先使用已配置的文档根目录。
- 如果项目或本地配置已经给出 `docs.root`，就围绕该根目录整理文档。
- 如果没有配置且用户也没有明确给出路径，再询问用户要使用的文档根目录。
- 不要通过全盘搜索去猜文档根目录。

## 文档层级

新项目的项目级文档必须按下面这套结构建立，顺序不要打乱：

```text
dimoo/
  00-overview.md
  10-roadmap.md
  11-cloudflare-storage-plan.md
  12-interfaces-and-schema.md
  13-reading-experience-plan.md
  20-references.md
  30-decisions.md
  31-open-questions.md
  32-risk-log.md
  plans/
    40-implementation-plan.md
    41-task-breakdown.md
    42-validation-plan.md
    43-release-notes.md
  tasks/
    feat-dedao-connector.md
    fix-6076.md
```

这条主线是 `new-order` 的基础约束。没有它们，就不要直接进入任务拆解。

## 扩展说明

- `00-overview.md` 记录项目目标、范围、角色和边界。
- `10-roadmap.md` 记录阶段路线和推进节奏。
- `11-cloudflare-storage-plan.md` 记录云端存储/持久化策略。
- `12-interfaces-and-schema.md` 记录接口、字段和数据结构。
- `13-reading-experience-plan.md` 记录阅读体验相关的设计和执行计划。
- `20-references.md` 汇总参考资料和外部链接。
- `30-decisions.md` 记录已确认的关键决策。
- `31-open-questions.md` 记录待确认问题。
- `32-risk-log.md` 记录风险和阻塞点。
- `plans/` 存放阶段性计划文档。
- `tasks/` 存放 task-dev-flow 声称的 `feat-*` / `fix-*` / `perf-*` 任务文档。

如果项目已经有既定目录结构，优先保持一致，只补充缺失部分，但这套基础层级必须最终补齐。

## 核心职责

- 先定义项目目标、范围、边界和角色。
- 再把存储、接口、字段和阅读体验相关计划讲清楚。
- 重要决策、待确认问题和风险要单独沉淀。
- 最后把阶段计划和任务推进顺序排好。

## 和 task-dev-flow 的关系

- `new-order` 负责项目级秩序。
- `task-dev-flow` 负责单个任务的拆解、实现和验证。
- 没有稳定项目文档时，先用 `new-order`，再进入 `task-dev-flow`。

## 说明

- 这个 skill 不直接生成 `feat-***` 或 `fix-***` 任务文档。
- 它的任务是先把项目变得“能开发、可推进、可交接”。

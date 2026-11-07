# 本地配置、外部产物与交还

## 可选本地配置

唯一位置：`~/.agents/local-config/t-design/config.json`。没有私人绑定时可不创建，显式用户指令和已有团队真源优先。

```json
{
  "version": 1,
  "docsRoot": "<absolute-team-docs-root>",
  "maintainerAlias": "dr eggbot",
  "hostBindings": {},
  "teamBindings": {}
}
```

- `version`：当前为 1；其他版本先报告，不猜测迁移或读取旧位置。
- `docsRoot`：可选绝对路径，存团队设计和维护产物，不将占位符作为真实路径。
- `maintainerAlias`：可选非空字符串，默认 dr eggbot，不改变维护职责。
- `hostBindings`：可选字典，键为宿主 ID，值可含 `kind`（`subagent` / `native_bot` / `unknown`）、`connectionRef`、`docsRef`。这些是已有连接/文档引用，不证明工具在线，不保存密码、Token 或 Cookie。
- `teamBindings`：可选字典，键为安全的团队 ID，值可含 `hostId`、`docsRoot`、`externalTeamRef`。具体实例状态放外部记录，不在配置里复制角色规范或敏感对话。

通用岗位、记录格式、合法值与授权边界由技能定义。配置不能关闭独立验证、扩权或恢复用户暂停；不添加工作目录、旧点文件或环境变量配置回退。`t-loop` 和其他技能的配置各按自己的 schema 和唯一位置维护，不把它们复制到这里。

## 外部生成产物

复用现有团队/项目文档真源；没有对应结构时，以选定的 `<team-docs>` 保存：

```text
teams/<team-id>/
  design.md                  目标、架构、岗位与关系，含版本和依据
  roles/<role-id>.md         每个岗位可应用的完整提示词
  deployment.json            宿主映射、配置状态、真实实例与未完成项
  maintenance/<change-id>.md  反馈、候选调整、授权、验证及生效记录
  evidence/<run-id>/          原始证据或引用索引
```

团队/岗位/变更 ID 使用安全 basename，不允许 `..` 或路径分隔符越界。已有等价结构直接沿用，不要求迁移历史文档。用户尚未指定真源且无法从现有配置确认时，在已授权临时目录交付产物并标注未绑定，不能擅自公开或写入无关业务仓库。

`deployment.json` 至少记录：

```text
schemaVersion=1, teamId, designRevision, hostKind, hostRef
mode: design | audit | provision | maintain
authorizationRefs, baseline, generatedArtifacts
roles: roleId, alias, promptPath, instanceIds, configRevision
checks: criterion, result, evidenceRefs, checkedVersion, timeAndZone
status: generated | configured | running | validated | blocked | paused
stateHistory, configured, runtimeObserved, behaviorVerified
published, installedTargets, limits, uncertainEffects, nextAction, updatedAt
```

状态与证据分开：

- `generated`：必要设计和岗位产物已保存，不表示已写入宿主。
- `configured`：已在目标宿主写入并回读配置/实例。
- `running`：观察到指定版本实际执行，不表示行为正确。
- `validated`：约定的行为标准由匹配版本证据支持。
- `blocked` / `paused`：保存已完成阶段及下一步，不抹掉之前事实。

生成、配置、运行、验证是独立事实；临时子 Agent 验证后可以停止，`stateHistory` 保留曾运行及已结束状态，不声称实例持续运行。`published`、安装目标和公开分享分别记录，未确认就用 unknown；模拟证据显式标为 simulation，不外推成真实 Bot 或产品闭环。

## 维护记录与最终交还

维护记录包含原始问题/证据、被审对象用途、基线与候选版本、允许变更与授权引用、决定/未决事项、实际变更、验证方式和限制、生效/同步目标、回退方式与停止原因。

向用户交还核心结果、产物位置、真实实例/版本、实际检查、已发布/安装范围、限制和下一步。只说实际完成的阶段，不把建议、生成草稿或平台工具缺失包装成已搭建完成。维护状态不等于项目 verified，也不触发发布或生产部署。

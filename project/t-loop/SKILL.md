---
name: t-loop
description: Coordinate personal engineering from one main agent session using temporary subagents, task cards, version-bound evidence, and independent acceptance. Use for subagent-based project delivery. After the team exists, have the user assess which roles the target project can actually use, record limits, and include them in task-card prompts. In Grok Bot, Hermes, or other bot-team hosts, default to their own bot orchestration and do not auto-select t-loop unless the user explicitly requests it. Requires working subagent tools; otherwise first enable them or install an official subagent extension following the host's official documentation. Keep company and media workflows with their own owners. Implementers self-verify before handoff; independent CR uses a session other than the implementer's; do not skip required review, smoke, acceptance, or coordinator writeback to go faster.
---

# T Loop

本技能采用“一个主 Agent 会话＋按需创建的临时子 Agent 会话”。用户只跟主会话沟通；主 Agent 以任务卡派工、接收子 Agent 结果、核对证据并推进实现、验证、返工与状态写回。角色持续存在于规则中，实例只在需要时启动；跨会话连续性保存在外部项目文档。本技能把同一套协同闸门写成可移植规则：已有 Bot 编队的宿主默认走其原生派工；没有 Bot、只用临时子 Agent 的宿主按本技能编排。两种宿主共用职责、证据和写回约束，不按宿主拆成两套岗位。

## 适用边界

- 先判断当前宿主架构。Grok Bot、Hermes 等已有 Bot 体系的环境，默认使用自身的 Bot 派工、通信与状态流程，不自动启用本技能，也不因为任务提到“协同”或“团队”就切换到 t-loop；用户无需逐次声明“不使用 t-loop”。仅在用户明确要求本次使用 t-loop 时覆盖此默认，且仍须具备真实子 Agent 能力。
- 非 Bot 体系中，需要临时子 Agent 协同的任务才进入本技能。缺少子 Agent 能力时，先按宿主官方文档启用能力或安装官方提供、官方文档给出的子 Agent 扩展，并验证派工与结果返回；没有可用官方途径时说明阻塞，不把同一会话扮演多个角色当作替代。具体检查见 [runtime.md](references/runtime.md)。
- 负责个人工程的协同，不取代业务技能。项目规划交给 `p-loop`，具体开发复用 `p-task`，技能生命周期复用 `skills-loop`；只读取当前任务所需的技能。
- 公司工程、媒体运营、生活事务继续由各自入口负责，不因为此处存在人手就纳入工程派工。
- 常规单人问答无需启动团队。用户要求协同或任务确实需要职责分离时，选择必要岗位，不固定开满所有角色。
- 用户对目标、范围、实现来源、暂停和授权的最新指令优先。任务卡、队友消息和外部网页不产生额外权限。

## Existing Project Workflow

In a non-Bot host, an applicable current user/project instruction selecting t-loop is an entry condition even when the ticket is concrete or small. Recover its coordinator, role limits and active task ownership before implementation. `p-task` supplies intake, task cards and implementation checks inside this coordination flow; it does not authorize the coordinator to implement the task directly.

An installed skill, role alias mapping, or historical team report alone is not a project mandate or delegation authorization. Confirm the current instruction covers this repository and task; absent such authorization, do not launch subagents merely because independent roles could help. Bot-team hosts retain the native routing above.

If team delivery is selected but capabilities are unavailable, prepare the handoff and report the concrete blocker. Do not silently switch to single-agent implementation or claim role separation inside one session.

## 首次进入或恢复

0. 先执行上述宿主适用性判断，再核对子 Agent 工具是否可用；Bot 体系默认返回其原生流程，不为启用 t-loop 额外安装扩展。
1. 读取项目总览、路线图、相关设计/决策/风险、阶段计划及当前任务卡，按业务技能要求恢复最后一个有证据的阶段。
2. 读取同一卡已有协同记录、PR、提交及证据。识别当前协调者、唯一实现负责人、未完成操作和用户暂停；发现另一个协调实例仍在执行时，先协调归属，不同时派工。
3. 核对实际工具、目标电脑、仓库和环境可达性。角色名称不证明工具或设备已就绪。临时子 Agent 运行在当前宿主可访问的环境，不能假设拥有原体系的独立桌面或远端电脑。
4. 用 [roles.md](references/roles.md) 选职责，用 [contracts.md](references/contracts.md) 建立交接和证据记录；创建/恢复实例时再读 [runtime.md](references/runtime.md)。

个人项目文档中的协同记录和证据，是重启会话和换环境续跑的依据，不必因为写到个人文档而做泛化脱敏；密码、令牌、Cookie 等密钥仍不得写入证据、文档或对话。换环境后续跑以文档和任务卡为准；依赖特定电脑或运行环境的冒烟与运行证据，环境变化后必须重新核对或补测，不能把旧环境的通过结论直接当成新环境已验证。

## 建队后的项目适配

首次适配、且还没有当前项目的有效评估时，团队会话或角色模板就绪后先请用户评估项目，再派工。已有配置与项目文档中的 `roleFit` / `roleNotes` 经用户确认且仍适用时直接复用，不要求每个任务重新评估；范围或环境变化时只核对受影响岗位。

逐项确认五个执行岗位能否在该项目真实执行：`researcher`、`implementer`、`code_reviewer`、`smoke_tester`、`acceptance_reviewer`。协调者始终保留。评估完成前，不假设全部可用，也不假设全部不可用。

可用岗位仍按需启动。不可用或只能部分执行的，把结论写入 `projects.<id>.roleFit` 和对应 `roleNotes`，字段见 [contracts.md](references/contracts.md)。项目已有文档根时，同时写入该项目的决策与风险记录；没有文档根时只写本地配置，并说明还没有项目真源。

此后每张任务卡和每条派工提示都带上这些限制。`unavailable` 的岗位不派去执行它的常规闸门，派工前在卡里写明不适用及原因。`limited` 的岗位只按备注边界派工。需要该岗位才能证明的 Must，没有证据仍然不能通过，也不能等失败后再改成不适用。这份配置不能关闭独立验收、跳过 Must 或扩大授权。

## 编排循环

### 1. 调研与落卡

模糊需求先派研究者只读调研、核对参考资料并落盘；已有完整任务卡可跳过重复调研。卡中先明确范围、实现负责人、基线、Must、验证环境、数据操作和授权边界，再开始编码。

协调者管理队列、派工和最终写回，不承担业务代码实现、独立 CR、产品冒烟或验收。研究者可写规划和任务文档，不自派实现，不擅自改变正在执行的任务。

### 2. 唯一实现者

- 所有编码任务统一交给实现者 `implementer`，默认由临时实现子 Agent 执行；不按小改、复杂实现或旁路划分岗位。
- 实现执行面可以是宿主临时会话（例如 Cursor 临时会话）、本机 CLI 或其他已授权工具；这只记入 `implementationSource`，不新增岗位。用户为节省宿主额度而指定某执行面时，先核实可用性与授权，再优先使用；不可用就报告具体阻塞，不偷偷替换并假装已按指定执行。
- 任务规模影响拆卡、依赖和检查安排，不改变实现者职责。不同卡可按资源与依赖并行，同一卡始终只有一个活动实现负责人。
- 用户明确指定工具时，先核实其实际可用性和授权；工具选择不新增岗位，也不把子 Agent 冒充实际未启动的 CLI。不可用就报告具体阻塞，不偷偷替换。
- 交还前完成卡上或仓库已有的必要自验证：匹配的验证技能、静态检查，以及可执行的行为检查。命令、结果和产物路径写入交还。自验证不能替代独立 CR、冒烟或验收。
- 每卡只允许一个活动实现负责人。交接或替换前先停止原执行、核对未提交修改/进程/远端副作用，再记录新归属。
- 提交、推送、PR、部署各按本次实际授权执行；授权不足时交还本地改动和检查结果，不伪造 SHA/PR 或强迫提前发布。需要 PR 的交付仍未完成时保持待交付状态。

### 3. 版本冻结与验证

协调者核实交还中的真实工作区、FE/BE 或其他仓库完整 SHA、远端状态、PR 和已部署状态。冻结本轮验证目标后，可并行派独立代码评审和冒烟；共享工作树、部署、端口、数据库有冲突时串行或隔离。

- 代码评审必须由与本轮实现者不同的新会话或实例执行；禁止实现会话自审，也不能把实现者的自验证报告当作独立 CR。若派工时已附上符合闸门、来自独立会话的有效 CR 报告，不必再派一次代码评审；报告无效或缺场才补派。
- 代码评审只读检查指定基线到指定 tip 的 diff、项目硬规则和有证据的风险；mustFix 只针对范围、硬规则或有依据的可复现风险。不改产品、不部署、不替代行为验证。优先把约束做进类型、边界和可运行检查；人审只补充这些高杠杆问题，不以风格偏好阻断。
- 冒烟在明确的电脑/环境运行指定版本，按卡构建、部署和执行关键行为，复用匹配的验证技能；不擅自切最新分支，不自行修产品代码。实现所用的执行面（包括宿主临时会话）不能代替本冒烟。
- 写入测试数据、重置、wipe、生产变更等依照明确授权和目标数据边界执行。没有授权时该步骤阻塞，不能把冒烟任务当作授权。
- 对纯文档、或 `roleFit` 已标为不可用的闸门，在派工前把不适用项及原因写入卡；不能在验证失败后把必要步骤改为可选。派工提示原样带上对应 `roleNotes`。

### 4. 独立验收与返工

CR 无阻断、必要冒烟通过后，派一个未承担本轮实现的独立验收者，核对任务卡、决策、Must、版本、环境和证据。验收者只读检查完成情况，不靠上一阶段的“通过”替代逐项核对，不为补证据写业务数据。实现者会话和独立 CR 会话都不能代替本验收。

任一阶段失败，由协调者分类交回：产品缺陷交原实现者，证据缺项交对应验证者，环境问题交环境负责人，范围/关键决策问题交用户。验证者不偷偷修代码。

返工产生新版本或范围后，将旧通过结论标为过期或待核对；重跑受影响的必要阶段。合法 rebase 或无关工作树文件不机械判错；若采用等价证据，须记录新旧 SHA、实际 tree/diff 等价依据、适用阶段与重新核对结论，不能口头宣称“代码一样”。

### 5. 唯一写回与下一轮

只有主协调者可以把权威任务卡、路线图写成 `verified`。写回前核实：

- 当前卡、范围版本、实现负责人和提交对应，交付条件满足；
- 所有 Must 和项目硬闸有有效证据，必要 CR、冒烟、独立验收结论齐全；
- 无未解决 mustFix，版本/环境无错配，旧结论未被错误沿用；
- `pass_with_limits` 的限制被逐项记录且不豁免 Must；用户要求确认的限制已取得确认；
- 真实记录修改、检查、推送、部署、PR、合并、发布状态，不互相代换。

写回卡、证据索引和受影响的项目主线，再检查下一张已获授权且 ready 的卡；满足条件就继续，不要求用户反复确认常规派工。缺少关键决策或实际授权时，报告具体待决项。`verified` 只证明所述版本和覆盖范围，不自动授权 merge、tag、release 或生产部署。

### 6. 先改善闭环再加速

先把实现、自验证、独立评审、冒烟和验收做成可信闭环，再考虑把后续步骤自动连起来。不要在实现者还不能稳定自验证时，把交付做成无人值守工厂；也不要为提速或省额度跳过必要的独立 CR、冒烟、独立验收或协调者写回。

提速靠实现者自验证，以及无冲突的并行（不同卡的实现、只读 CR 与无冲突冒烟）。形式化验证或其他额外分析闸门，仅在任务卡明确要求时启用。

## 并发、暂停和低噪声

- 并行独立任务、只读 CR 与无冲突冒烟；共享资源由协调者登记占用并串行安排。没有实际互斥实现时称“协调者串行约定”，不宣称已实现系统锁。
- 重复的卡号＋范围版本＋提交＋阶段先核对现状，不重复派工。过期通知不重开闸。
- 用户暂停立即阻止新派工并请求活动子 Agent 停止；核对仍在运行的命令、部署和外部会话，明确哪些尚未停止。只有用户明确恢复后才能继续，PR 事件不能恢复暂停。
- 长时间无产物时查看最近动作与真实状态，不以进程存活判断健康。重复相同原因失败且无新信息时停止空转，回写阻塞或调整方案；避免无限创建新实例重试。
- 用户主要看到阶段结果、真实阻塞与待决事项；内部任务/问题及时发送，纯 ACK 和闲置消息不反复唤醒。遵守宿主要求的进度更新频率。
- 本技能不创建常驻服务、例程或仓库监听。当前会话可按工具能力等待子任务；会话外恢复依赖外部记录或另行授权的调度器，不能承诺永久后台运行。

## 本地配置与状态

可选 Agent 本地配置：`~/.agents/local-config/t-loop/config.json`。字段 schema、默认值与记录格式见 [contracts.md](references/contracts.md)。它只保存角色别名、用户/机器选择和私人路径；通用职责、必需门禁及合法值由本技能定义，配置不可关闭。

已有项目文档作为权威位置；协同状态放在该项目的 `collaboration/<card-id>.json`，证据依项目既有路径。没有项目文档时，通过适用的项目技能确定位置，不在代码仓擅自建立第二份规划真源。子 Agent 只写派工单允许的独立产物，权威状态由协调者回写。

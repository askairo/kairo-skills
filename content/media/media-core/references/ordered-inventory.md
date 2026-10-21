# 顺序库存、队首消费与人工跳过

适用于 `sourcePipelines.<id>.selectionPolicy.queuePolicy.mode=strict_source_fifo`。本模式覆盖通用 eligible 排序/跳到下一项规则和单候选采集起点；不改变账号健康、版权、媒体、运行锁、发布结果未知等门禁。由 media-core 唯一维护顺序事实，ops只回传已核验结果。

## 配置与事实文件

配置仍在 `~/.agents/local-config/media-core/config.json`，本模式的 queuePolicy 字段：

- `mode`: `strict_source_fifo`。
- `inventoryFile`: 外部文档的绝对路径；同pipeline一份JSON。
- `sourceOrder`: `oldest_to_newest`；`blockedHeadHandling`: `stop_queue`。
- `allowExplicitUserSkip`: true；`maxNewSubmissionsPerRun`: 1。

inventoryFile 的 schema：`version=1`, `pipelineId`, `order=oldest_to_newest`, `revision`（递增整数）, `updatedAt`, `lastReleasedVideoId`, `items[]`。每项有 `sourceOrdinal`（稳定唯一递增整数）、`videoId`、`sourceUrl`、`title`、`sourceOrderEvidenceRef`、`contentId`（未创建时null）、`targetIds[]`、`assetRef`（未取得时null）、`state`、`createdAt`、`updatedAt`。state取 `candidate|verified|ready|blocked|uncertain|published|published_pending_review|skipped_by_user`；发布结果未知保留为uncertain且不能移除。一次流水线只对应一条来源顺序；多平台目标仍各自保留publishState，按账号/平台判断该项是否结算。

`sourceOrdinal` 是从迁移基线后的局部顺序编号，不冒充频道全局序号。项的来源顺序须有完整持久化索引或从频道最早连续加载的顺序证据，不能以下载完成时间、文件名、plannedAt、创建时间或热度计算。中间项即使尚无文件，也必须登记candidate/blocked占位，不能只登记已ready项后静默跨过缺口。

活动队列是items中尚未结算的有序视图，不另建第二个数组：published、published_pending_review和skipped_by_user退出；其余保留。对多平台只退出当前已结算目标，不能连带改变其他平台。ready库存与活动队列分别统计。JSON是当前顺序事实，资产JSON绑定视频/哈希/copyPlan和目标结果；Markdown仅作镜像与审计。各记录矛盾时停止，不按某段旧ready文本猜测。

## 提前准备与严格发布

1. `state.yaml.nextVideoId`始终镜像活动队首，不是下载进度；`lastReleasedVideoId`只反映实际已核验发布。准备多条不修改发布基线。
2. 采集时复用最早未完成准备项；已有ready项留在队列。需要追加库存时，从最后一个已登记项的来源直接后继继续，先登记候选和顺序证据，再下载/验收/适配。队列为空时，从已结算顺序末项的直接后继恢复，不能退回旧发布基线把用户跳过项重新补入。
3. 顺序尾项包括已发布和人工跳过项；若没有可验证后继，保留`cursor_recovery_required`。不引入一个能覆盖发布nextVideoId的“下载游标”。
4. 发布前按来源序号取当前账号/平台的唯一活动队首，再检查ready、媒体、文案、身份、健康和锁。队首不ready/阻断/锁冲突/结果不明确则`blocked`或`unknown`，本队列停止，不能考虑后项。计划时间和Profile分组不能改变此顺序。
5. 每次触发本队列最多新提交1条。核验published或published_pending_review并回写后，才从活动队列移出该项；重新计算nextVideoId，保留后项原顺序与文案绑定。不确定提交不重发，不释放为下一项。
6. 单pipeline库存修改互斥，另保留每个contentId+targetId发布锁。修改前读取revision和在途检查点，写前复查revision；冲突停止。检查点记录旧/新revision、受影响ID和所有文件写回阶段。部分写回从检查点恢复，不再次下载/跳过/发布。

## 人工跳过入口

用户可以说：`跳过当前队首`、`跳过视频 <videoId或原始URL>`、`把《明确标题》从待发布队列移除`。本入口是逻辑移除，不是删除文件。没有用户明确指令，技术失败、质量疑虑、超时或补货都不能自动跳过。

1. 根据当前队列唯一确定视频和目标范围；默认仅当前会话已确定的账号/平台。重名、同名多版本或账号范围不明时先澄清，期间不修改。只说支持跳过入口不等于跳过当前视频。
2. 检查该项与队首的在途锁/草稿/提交状态。已发布或审核中不能伪装成跳过；submitted、publish_unconfirmed或uncertain先只读对账。活跃执行锁不能强行清除，待执行停止且副作用明确后再修改。
3. 对无在途副作用的待发布项，持锁记录`state=skipped_by_user`及目标`publishState=skipped_by_user`，保留`skipRecord={requestedAt, recordedAt, userInstruction, reasonCode:user_directed_skip, targetIds, previousState, runRef}`。尚无资产时也在inventory登记；有资产时同步对应target，其他平台不变。幂等重放原跳过记录，不追加等价跳过事件。
4. 从活动队列剔除（保留items历史、原始视频与审计），写入state.yaml的`userDirectedSkippedCandidates[]`及队列/registry当前状态。参与来源ID、URL和指纹去重，未来扫描不能再次自动入队。
5. 跳过队首时nextVideoId指向下一最小来源序号活动项；没有已登记后项时置null并注明待恢复“最后结算项”的直接后继。跳过中间项时队首不变，其他项不重排。lastReleasedVideoId/lastReleasedAt保持不变；跳过不计发布成功、不计发布次数。
6. 展示跳过的ID/标题、操作后的队首、保留的文件及写回结果。重新加入必须由用户明确要求，并恢复原来源位置；若后项已发布则停止并报告顺序冲突，不静默追加到队尾。

## 验收场景

- A→B→C，C先下载完：发布仍从A开始，C不抢先。
- A阻塞且B/C ready：不发布B/C；修复A或等待用户明确跳过。
- 用户跳过A：A保留审计且退出活动队列，next=B，发布基线不变。
- 用户跳过B：活动A→C，next仍A；A完成后才到C。
- A提交结果未知，用户要求跳过：先对账，不能直接清除A。
- 重复要求跳过同一项：无新增发布或重复跳过副作用。

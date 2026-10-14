# 授权的来源窗口覆盖

来源窗口临时实验由 media-loop 管理，唯一保存位置是 `<AGENTS_HOME>/local-config/media-loop/config.json` 的 `strategyOverrides` 数组；media-ops 读取并传给 productionRequest，media-core 使用该 effectiveLookback。常驻 media-ops 策略 lookback 不改写。不存在覆盖或已过期/停止时自动使用常驻值，不继承历史 run 中的覆盖。

每个对象必须有 `id`、`version`、`status`（active/stopped/completed）、`accountRef`、`targetRef`（platformAccountRef）、`pipelineRef`、`strategyRef`、带时区的 `startsAt/expiresAt`、`authorizedBy: user_request`、`evidenceRef`（授权/实验记录）、`overrides: {lookback: P2D}` 和 `rollbackValue`（当前常驻 lookback）。只有用户明确授权的实验可写入；此 schema 的 overrides 仅允许 lookback P1D..P7D，不能降低任何门禁。时间区间为 startsAt <= 当前时间 < expiresAt。相同 scope 多个有效覆盖、回滚基线变更或字段非法时停止来源生产并报告配置冲突，不能猜一个值。

每次来源请求前调用本技能的只读 resolver：

```sh
python3 <media-loop-skill>/scripts/resolve_source_window.py \
  --account-ref <account-ref> --target-ref <platform-account-ref> \
  --pipeline-ref <pipeline-ref> --strategy-ref <strategy-ref> \
  --baseline <current-strategy-lookback>
```

输出 `effectiveLookback/overrideRef/overrideVersion/expiresAt` 写入本轮检查点和 productionRequest，再交给 core 扫描。resolver 不写配置、队列或平台。基于已有 asset 恢复时保留当时来源验收，不借覆盖重选或重建。扩大窗口但达到配置 timelineItems 上限时，记录扫描覆盖范围；未覆盖窗口不能声称完整窗口没有候选。

实验记录另含唯一变量、对照、最小有效样本、指标、停止条件和回滚值。供给样本只计完成实时来源扫描的首次触发，技术阻断/同轮恢复不重复计样本；记录 P1D 窗口内与新增窗口内的合格候选数，避免同时改变文案/阈值而作因果结论。账号文案实验保持当前处理方式，本覆盖的归因仅针对发现供给，不能归因阅读或收藏效果。

到期时 resolver 自动回退，未达最小样本写 inconclusive，不自动延期。健康警告、重复发布风险或事实/权利失败时执行原门禁并停止实验；停止状态写回 loop 配置，不能覆盖发布未知状态。实验成功只提出长期变更建议，不自动修改常驻策略。

离线验收：`python3 scripts/test_source_window.py`，覆盖起止时刻、时区、目标隔离、授权/门禁非法值、冲突、到期回退和只读行为。

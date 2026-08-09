# Media Loop 数据结构

## 本地配置

文件：`<AGENT_HOME>/local-config/media-loop/config.json`

```json
{
  "version": 1,
  "enabled": true,
  "accounts": ["<account-ref>"],
  "lookback": "P14D",
  "minimumComparableSamples": 5,
  "healthCheck": {
    "pauseOnAccountLabel": true,
    "pauseOnUnknownPublishState": true,
    "staleAfterHours": 36
  },
  "experiments": {
    "maxActivePerPlatform": 1,
    "minimumRuns": 5,
    "primaryMetricByPlatform": {
      "x": "profile_visit_rate",
      "xiaohongshu": "save_rate",
      "douyin": "completion_rate"
    }
  },
  "writeBack": true
}
```

缺失的账号引用、非法时长、非正数样本量或未知平台应停止运行并报告字段路径。`minimumComparableSamples` 只是结论门槛，不是发布门槛；不可为了得到结论降低事实和安全门禁。

## 运行快照

每次运行保存一个不可变快照，至少包括：

```text
runId, contentRef, distributionTargetRef, accountRef, platform,
browserProfileRef, profileBatchRef,
observedAt, window,
sourceRefs[], sampleCount, missingFields[], dataFreshness,
healthStatus, healthSignals[], publishFailures[],
metrics[], baselineRef, diagnosisRefs[], strategyVersion
```

`browserProfileRef` 和 `profileBatchRef` 只用于解释执行环境与 Profile 聚合效率，不是内容质量指标，也不得替代平台账号身份核验。

## 指标记录

每条内容保留 `postId`、发布时间、内容支柱、格式、来源类型、是否引用、媒体类型和互动入口。指标使用平台原始字段，并标记：

- `absolute`：阅读/曝光、点赞、评论、收藏、转发、完播人数等；
- `normalized`：互动/曝光、收藏/阅读、完播率、关注/访问等；
- `availability`：`observed`、`estimated`、`unavailable`。

估算值不得与实测值混合计算；跨平台指标只做方向性描述，不做绝对排名。

## 诊断记录

```text
diagnosisId, category, evidenceRefs[], affectedFormats[],
confidence, alternativeExplanations[], recommendedAction,
expectedSignal, stopCondition, createdAt
```

允许的 `category` 包括：`account_health`、`distribution`、`topic_fit`、`source_quality`、`hook_or_title`、`copy_structure`、`visual_or_media`、`timing`、`interaction_entry`、`rights_or_compliance` 和 `data_quality`。

## 策略与实验记录

```text
experimentId, hypothesis, accountRef, platform,
controlDefinition, oneVariable, startAt, endAt,
minimumRuns, primaryMetric, secondaryMetrics[],
successThreshold, stopCondition, result, nextAction
```

策略变更必须写明旧值、新值、依据、适用范围和回滚条件。没有达到最小样本时，`result` 只能是 `inconclusive`。

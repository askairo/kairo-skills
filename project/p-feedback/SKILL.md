---
name: p-feedback
description: Turn scoped production logs and operational signals into evidence-backed product feedback, route confirmed work to project planning or task execution, and verify released changes. Use when Codex needs to inspect a configured log system, monitor recurring errors, determine whether a released change worked, or maintain a production feedback loop. Do not use for ordinary implementation work without production feedback.
---

# P Feedback

Convert production signals into a resumable improvement loop:

```text
production signal -> evidence -> attribution -> decision or task
                  -> release -> production verification -> feedback record
```

Logs are an input, not the skill boundary. The skill may also use configured metrics or alerts when they are available and relevant.

## Ownership boundary

`p-feedback` owns the outer production-feedback loop: observe, checkpoint, normalize, classify, deduplicate, record, route, and re-verify. It does not replace project planning or development execution.

- `p-loop`: durable project goals, scope, priority, architecture decisions, risks, open questions, and task readiness.
- `p-task`: concrete code, configuration, test, branch, commit, and implementation verification.
- `p-devops`: build, deployment, and delivery changes.

Use `p-feedback -> p-task -> p-feedback` when the smallest safe fix is already clear. Insert `p-loop` when the evidence changes project scope, priority, architecture, or a durable rule. Keep the production feedback record in `feedback/`; keep project state in `p-loop` documents and implementation history in the linked task.

## Configuration

Use exactly one machine-local configuration file:

```text
<AGENT_HOME>/local-config/p-feedback/config.json
```

Read [references/configuration.md](references/configuration.md) whenever configuring or selecting a project, log system, account reference, or observation target. Do not read legacy paths or create fallback configuration files.

## Workflow

1. Establish the repository, branch, project, environment, service, observation target, time window, and requested outcome. Explicit user values override local defaults for the current run but do not silently rewrite configuration.
2. Resolve the configured project docs path and read any related feedback record. Read project-level decisions, risks, plans, or task records only when they affect attribution or the next action.
3. For recurring observation, follow [references/observation-loop.md](references/observation-loop.md). Use a persisted target checkpoint and a small overlap window instead of rescanning an arbitrary long history. Query the selected source read-only and record the actual query, time range, result limit, first and last timestamps, and count when available. If the target exposes only selected log levels, record that fact and never infer anything from unavailable levels.
4. Normalize and group entries by stable fingerprints such as operation, logger/class, exception type, provider, HTTP status, provider business code, and normalized message. Separate repeated failures from duplicate stack output and compare fingerprints with existing feedback records before calling a group new.
5. Classify each meaningful group:
   - expected business or provider rejection;
   - caller data or contract problem;
   - remote dependency failure;
   - local system defect or resource problem;
   - observability noise such as duplicate stacks, unsafe payloads, wrong level, or missing context.
6. State the evidence, impact, confidence, likely owner, smallest safe next action, unresolved assumptions, and verification condition. Do not turn correlation into a proven cause. Give every feedback item a scope of `observability`, `functional`, or `both` so a logging fix is not mistaken for a root-cause fix.
7. Create or update the feedback record using [references/feedback-record.md](references/feedback-record.md). Link related task records instead of copying their implementation history. Do not rewrite records for unchanged, non-actionable observations.
8. Route work by responsibility:
   - durable product, architecture, priority, or project-rule decisions -> `p-loop`;
   - concrete code, configuration, or test changes -> `p-task`;
   - build, deployment, or delivery changes -> `p-devops`.
9. When monitoring continues, update the target checkpoint and notify only for a new fingerprint, a material change, a clear WARN-noise reduction opportunity, a release verification result, a blocker, or required user action. Apply notification deduplication and a cooldown to unchanged fingerprints and pending-release reminders.
10. After a change reaches the target environment, repeat a comparable scoped query and update the record with before/after evidence. A code change, branch merge, or successful build alone is not production verification.

## Evidence and safety

- Production access is read-only unless the user separately authorizes a specific mutation through the responsible workflow.
- Scope every query by environment and service/container where supported. Avoid unrestricted exports and unnecessarily large time windows.
- Never record passwords, tokens, cookies, private keys, account secrets, full addresses, or unnecessary request/response bodies. Redact evidence before saving it.
- `accountRef` identifies a connector, credential-store entry, or user-owned authenticated session; it is not a place for credentials.
- Keep expected client or provider rejection visible. Log level determines routing and urgency, not whether evidence is discarded.
- Do not interpret a provider business code such as `500` as HTTP 500 without transport evidence.

## Severity guidance

- `WARN`: actionable but expected business/provider rejection that does not indicate service failure.
- `ERROR`: local defects, resource leaks, authentication/configuration failures, contract regressions, repeated remote 5xx, or loss of required functionality.
- `INFO`: lifecycle milestones and aggregate results.
- `DEBUG`: temporary detail when the target environment permits it.

Preserve searchable context such as operation, environment, service, provider, safe business identifier, transport status, provider code, and normalized reason. Prefer one concise contextual exception log at the ownership boundary over repeated full stack traces at every layer.

When reducing WARN output, preserve expected client/provider rejections and enough context to act on them. Aggregate repeated batch results where safe; do not downgrade or suppress local failures, resource leaks, authentication/configuration failures, contract regressions, or loss of required functionality merely because they are frequent.

## Continued observation

When the user asks to keep watching, use the available recurring monitoring mechanism and let `p-feedback` control the observation-to-verification loop. Reuse the same target and fingerprint, keep the last checkpoint outside static configuration, remain quiet while results are unchanged and non-actionable, and notify only for a meaningful change, verification result, failure, or required user action. Monitoring does not authorize deployment or production changes.

## Completion

A feedback cycle is complete when the source and scope are reproducible, evidence is grouped and redacted, attribution is explicit, the next owner and verification condition are recorded, production verification is marked as verified/pending/blocked, and the external feedback record is current.

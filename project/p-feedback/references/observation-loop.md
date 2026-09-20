# Observation Loop

Use this reference for recurring production observation or when a user asks for new, previously unseen, or reducible WARN/ERROR signals.

## Checkpoint

Maintain one target checkpoint in `<project-docs-path>/feedback/_observation-state.md`, separate from static machine configuration and individual problem records. At minimum, retain:

```text
target
lastCheckedAt
lastQueryFrom
lastQueryTo
overlap
lastNotifiedFingerprint and lastNotifiedAt
```

For a first run, use a bounded initial window. For later runs, query from `lastCheckedAt - overlap` to the current time. Keep the overlap small enough to avoid repeated large scans and large enough to tolerate ingestion delay. Advance the checkpoint only after the query result has been read successfully.

Do not use a dashboard's currently selected long time range as the recurring cursor. A visible query page is evidence of one query, not proof that the complete observation plan ran.

## Collection passes

Run the smallest collection plan that answers the request:

1. **Broad sweep**: the configured target, service/container scope, and levels actually available in that environment.
2. **Focused verification**: linked records in `awaiting_release` or `verifying`, plus any provider or operation groups required by the target's acceptance condition.

Record which passes actually ran, their redacted queries, windows, limits, counts, and first/last timestamps. If a requested provider or operation was not queried, say so rather than implying coverage.

## Fingerprints and novelty

Build a stable fingerprint from the most specific safe fields available:

```text
operation/logger + exception type + provider + transport status
  + provider code + normalized reason
```

Remove timestamps, thread ids, volatile identifiers, stack line numbers, and response bodies from the normalized portion. Keep safe business identifiers only in the representative evidence when they are needed for actionability.

Compare the fingerprint with existing feedback records before classifying it as new. A new occurrence of a known fingerprint is not a new problem; it is a recurrence whose count, severity, scope, or context may have changed.

## Action thresholds

- **New fingerprint**: create a feedback record, classify it, and route it if action is needed.
- **Known unchanged fingerprint**: advance the checkpoint and stay quiet; do not append repetitive history.
- **Material change**: update the existing record and notify when occurrence burst, severity, affected operation/provider, error context, or user impact changes meaningfully.
- **WARN reduction candidate**: record the repeated pattern and the safe reduction shape, such as aggregation, deduplication, context improvement, or payload redaction. Do not reduce visibility for a local failure or required functionality loss merely to reduce volume.
- **System failure**: retain ERROR severity and notify even when the fingerprint is known.

Before keeping a group open, apply the objective gate from `SKILL.md`:

- Normal business validation, ordinary token/credential checks, expected provider rejection, and routine lifecycle output with no material user impact are `closed`; frequency alone is not a reason to monitor them.
- Normal behavior with unnecessary logging is a `proposed` code-optimization item. Link a task when implementation is clear, and do not route the normal business event as a functional incident.
- Keep real failures, contract regressions, data risks, and user-impacting performance problems open with the required severity.
- A release verification may become `verified` only after its acceptance condition is evidenced. A user-confirmed “no longer follow” or a confirmed normal event may become `closed` with a concise reason.

## Routing and return

`p-feedback` remains the controller and hands off only the appropriate responsibility:

```text
p-feedback -> p-task -> p-feedback
p-feedback -> p-loop -> p-task -> p-feedback
p-feedback -> p-devops -> p-feedback
```

Use the first path when the concrete fix and acceptance condition are clear. Insert `p-loop` when scope, priority, architecture, compatibility, security, or a durable logging rule is undecided. Use `p-devops` for release or delivery work. After the handoff returns, `p-feedback` re-reads the record, checks the target release, and runs the comparable production query.

## Notification discipline

Notify immediately for a new actionable fingerprint, material worsening, a system failure, a verification result, a blocker, or required user action. Keep unchanged known patterns quiet. Rate-limit reminders for pending release or unchanged old-version logs; a reminder must not become a new feedback item.

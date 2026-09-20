# Feedback Record

## Location

Create or update:

```text
<project-docs-path>/feedback/YYYY-MM-DD-<short-slug>.md
```

Use one record for one stable problem fingerprint or tightly related group. Continue the same record across implementation and release verification instead of creating daily duplicates.

## Required content

```markdown
# <Feedback title>

- status: observed | proposed | implementing | awaiting_release | verifying | verified | closed | deferred | blocked
- scope: observability | functional | both
- project: <project>
- target: <configured-target>
- firstObservedAt: <timestamp>
- lastObservedAt: <timestamp>
- owner: <role, team, or linked task>

## Scope

- source: <log-system>
- environment/service: <scope>
- query: `<redacted reproducible query>`
- time window: <from/to>

## Evidence

- fingerprint: <stable normalized fingerprint>
- occurrence count: <count or unavailable>
- representative sample: <redacted excerpt or concise paraphrase>

## Assessment

- classification: <business rejection | caller contract | remote failure | local failure | observability noise>
- impact: <known impact>
- likely cause: <claim with confidence and alternatives>
- unresolved assumptions: <remaining unknowns>

## Action

- decision or next action: <smallest safe next step>
- linked task/plan: <path or identifier>
- success condition: <observable result>
- rollback or stop condition: <condition>

## Verification

- release/version: <identifier or pending>
- verification query/window: <comparable scope>
- before/after: <result>
- conclusion: <verified | pending | blocked>

## History

- <timestamp>: <material state change and evidence>
```

## Lifecycle consistency

- `awaiting_release` means the implementation is complete enough to release and `conclusion` remains `pending`.
- `verifying` means the target release is available and a comparable production query is in progress.
- `verified` requires the release identifier, verification query/window, and before/after evidence.
- `closed` is a terminal disposition for a confirmed normal business/provider event, an explicitly stopped follow-up, or a record superseded by a separate optimization project. State the reason, and reopen only for a new fingerprint or material change.
- `deferred` or `blocked` must state the reason, owner, and condition for resuming.
- `scope: observability` means only detection or logging behavior is in scope; `functional` means product/system behavior is in scope; `both` requires separate acceptance conditions for each.
- Legacy records without `scope` remain readable; assign the scope on the next material update instead of mass-rewriting historical records.

## Writeback rules

- Record verified facts directly and label hypotheses or incomplete attribution.
- Add history only for material changes: new evidence, changed attribution, implementation handoff, release availability, verification, deferment, or blocker.
- Update project decisions, risks, or open questions through `p-loop` only when the feedback changes durable project state.
- Keep implementation details in the linked `p-task` record and deployment details in the responsible delivery record.
- Redact sensitive data before writing. Do not paste unrestricted logs or full payloads.

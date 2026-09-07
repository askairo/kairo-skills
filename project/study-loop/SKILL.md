---
name: study-loop
description: Manage structured source-code learning across sessions by maintaining an external study plan, progress records, questions, and verified next steps. Use when learning a repository, framework, language, or technical system over multiple sessions.
---

# Study Loop

Turn exploratory technical learning into a resumable loop. Use the configured Obsidian documentation root as the durable source of truth; keep code changes out of this skill unless the user separately requests implementation.

## Configuration

Read `<AGENT_HOME>/local-config/study-loop/config.json` when present. If absent, use the configured p-task docs root as the default source and create only the study-loop config when needed:

```json
{ "docsRoot": "<absolute-obsidian-collection-root>" }
```

Never hardcode a personal path in this skill.

## Obsidian structure

For a repository or subject named `<subject>`, use `<docsRoot>/<subject>/study/`:

- `00-overview.md`: subject, goals, boundaries, and current verified state.
- `10-roadmap.md`: ordered learning phases and the next lesson.
- `20-source-map.md`: source/module map, key entry points, and durable concepts.
- `30-decisions.md`: confirmed learning interpretations or scope decisions.
- `31-open-questions.md`: unresolved questions that should shape future study.
- `32-risk-log.md`: blockers, misleading assumptions, and validation gaps.
- `plans/`: multi-session study plans.
- `records/`: one concise record per completed study session.

Create missing files only when the user asks to start tracking a subject. Preserve existing notes and update relevant sections instead of duplicating content.

## Study loop

1. Resume first: read the overview, roadmap, source map, latest record, and open questions.
2. Define a narrow lesson goal, source files or materials, expected understanding, and stopping condition.
3. Study from primary project sources. Explain unfamiliar syntax or design using the learner's background and a short concrete trace.
4. Record durable findings with evidence locations, remaining questions, risks, and the next lesson.
5. Verify understanding with a small code-reading exercise, call-chain trace, or user restatement.
6. Write back the result to external docs before ending the session. Update the roadmap when sequencing or current focus changes.

## Boundaries

- This skill manages learning state and plans; it does not silently modify the studied repository.
- Distinguish source facts, interpretations, and hypotheses in notes.
- Do not mark a lesson complete without a source location or concrete trace supporting it.
- Questions that change architecture, security, data behavior, or implementation scope belong in `31-open-questions.md` and remain unconfirmed until resolved.

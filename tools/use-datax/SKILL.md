---
name: use-datax
description: Generate, validate, and run DataX sync jobs for MySQL table transfers. Use when the user needs to move one or more tables between environments, prepare explicit-column DataX JSON, read runtime DB settings from a .codex config directory, or troubleshoot a DataX sync run.
---

# Use DataX

## Overview

Use this skill to prepare and execute DataX syncs for project databases. It covers runtime config resolution, explicit job generation, overwrite safety, execution, and fast failure reporting.

## Configuration

Read runtime settings from the user's `.codex` config directory.

Only these values are externalized:

- `config_dir`: directory that contains environment database config files
- `datax_home`: DataX installation root
- `job_dir`: directory for generated executable DataX JSON

Do not hardcode source/target environments, tables, columns, or date ranges in the skill.
Derive JDBC settings from the env config files under `config_dir`.

## Workflow

1. Ask for the source env, target env, table name(s), date range or filter, and whether overwrite/truncate is allowed.
2. Resolve JDBC settings from `config_dir`.
3. Generate DataX JSON into `job_dir` with explicit columns by default.
4. For overwrite syncs, set writer `preSql` / `postSql` to disable FK checks and truncate the target table.
5. Validate the JSON before execution: environment, table, columns, and overwrite SQL.
6. Run DataX from `datax_home`.
7. Stop on the first error and report per-table success/failure counts.

## Rules

- Prefer explicit column lists for nontrivial tables.
- Use full overwrite only when the user confirms the target table should be cleared.
- Fail fast if the generated JSON points at the wrong environment.
- Keep generated job files under the configured `job_dir`, not inside the skill.
- When a project already has local DataX examples, align the generated jobs with those conventions instead of inventing new ones.

## References

- See [references/config.md](references/config.md) for the external config boundary used by this skill.

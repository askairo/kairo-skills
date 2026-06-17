# Use DataX Config

## Runtime config root

Use a user-level `.codex` directory for runtime settings, for example:

```text
~/.codex/use-datax/
└── config.json
```

## Required keys

- `config_dir`: directory containing environment database config files
- `datax_home`: DataX installation root
- `job_dir`: directory for generated executable DataX JSON

## Meaning

- `config_dir` holds the project or environment database config files that the skill reads to derive JDBC settings.
- `datax_home` points to the DataX installation used to execute jobs.
- `job_dir` is where generated JSON jobs are written before execution.

## Constraints

- Keep environment, table, column, and date-range choices out of the config file.
- Use the config only to locate runtime inputs and outputs.

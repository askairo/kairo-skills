# Configuration

## Location

Use only:

```text
<AGENT_HOME>/local-config/p-feedback/config.json
```

Resolve `<AGENT_HOME>` from the current installed skill location or an explicit Agent Home. If more than one Agent Home remains possible, ask the user to choose. Never read another Agent's configuration.

The file contains machine- and user-specific values. Keep it outside the skill source repository, installed skill directory, project repository, and external project documents.

## Schema

```json
{
  "version": 1,
  "docs": {
    "root": "<absolute-project-docs-collection-root>",
    "projects": {
      "<project-name>": {
        "path": "<absolute-project-docs-path>"
      }
    }
  },
  "logSystems": {
    "<log-system-name>": {
      "type": "grafana-loki",
      "baseUrl": "<log-system-url>",
      "datasourceUid": "<datasource-uid>",
      "accountRef": "<connector-or-session-reference>"
    }
  },
  "targets": {
    "<target-name>": {
      "project": "<project-name>",
      "logSystem": "<log-system-name>",
      "environment": "<environment>",
      "service": "<service-name>",
      "availableLevels": ["WARN", "ERROR"],
      "labels": {
        "container": "<container-name>"
      },
      "defaultQuery": "<scoped-query>"
    }
  }
}
```

## Semantics

- `docs.root` is the collection root used when no explicit project mapping exists.
- `docs.projects.<project>.path` overrides `docs.root/<project>` for that project.
- `logSystems` describes access endpoints and datasource identity.
- `accountRef` is a symbolic reference to a connector, credential-store entry, or authenticated browser session. Never store a password, token, cookie, OTP, or private key here.
- `targets` binds a project and environment/service scope to one log system and default query.
- `availableLevels` is optional target metadata. When present, it lists the levels that can actually be observed in that environment; absence of an unlisted level is not evidence that the application did not emit it.
- Provider-specific query syntax belongs in `defaultQuery`; safety and redaction rules remain part of the skill and cannot be disabled by configuration.

## Selection order

For one run, resolve values in this order:

1. explicit user-provided project, source, target, query, or time window;
2. matching configured target;
3. the only configured target when exactly one exists.

If multiple targets remain plausible and the choice changes the evidence, ask the user. Do not silently modify configuration from a one-run override.

## Updates

When the user asks to add or change a stable value, update this one file and preserve unrelated fields. If the file is absent, collect the minimum required non-secret values and create it. Do not read, migrate, or fall back to legacy configuration files.

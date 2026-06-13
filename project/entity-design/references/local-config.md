# Local Config

Use private local config for machine-specific paths and requirement-source authentication.

## Agent Home

Resolve `<AGENT_HOME>` the same way as `p-task`, then read only from:

- `<AGENT_HOME>/local-config/entity-design/paths.yaml`
- `<AGENT_HOME>/local-config/entity-design/auth-sites.yaml`

Do not store these files in the project repo.

## Paths

Recommended `paths.yaml`:

```yaml
version: 1

docs:
  root: <absolute-design-docs-root>
```

- `docs.root` is the user-specific root for saved design artifacts.
- Keep the value as an absolute path.

## Auth

Recommended `auth-sites.yaml`:

```yaml
version: 1

sites:
  - name: zentao-bidaapp
    match:
      domains:
        - chandao.bidaapp.club
      path_prefixes:
        - /zentao/
    auth:
      type: form
      username: <username>
      password: <password>
    login:
      login_url: https://chandao.bidaapp.club/zentao/user-login.html
      username_field: account
      password_field: password
      submit_hint: login
    policy:
      local_only: true
      allow_auto_use: true
      require_confirm_before_update: true

  - name: axhub-im
    match:
      domains:
        - axhub.im
    auth:
      type: password_gate
      password: <password>
    login:
      login_url: https://axhub.im
      password_field: password
      submit_hint: confirm
    policy:
      local_only: true
      allow_auto_use: true
      require_confirm_before_update: true
```

- Use the saved credentials automatically when the requirement page or prototype is already known.
- Ask before saving new credentials or changing existing ones.

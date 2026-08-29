---
name: p-devops
description: Configure Jenkins CI/CD for Git-compatible repositories, including branch-filtered webhooks, build and deployment pipelines, health checks, and DingTalk or other notifications. Use when a repository should build and deploy automatically after commits to a specified branch.
---

# p-devops

## Outcome

Configure and verify this delivery chain:

```text
commit to selected branch
  -> GitLab/Gogs/GitHub-compatible webhook
  -> Jenkins job
  -> checkout and build
  -> image or artifact deployment
  -> health check
  -> success/failure notification
```

This skill is provider-neutral. Treat GitLab, Gogs, and GitHub as Git-compatible sources with different webhook screens; use the repository's actual UI and existing server conventions.

## Required inputs

Collect or infer only the values needed for the requested environment:

- repository URL and branch;
- Jenkins URL and target host;
- service/component/environment name;
- build command, artifact or Dockerfile location;
- deployment method and host-port mapping;
- notification channel and existing Jenkins notifier/template.

If a value affects routing, credentials, data, or production safety and cannot be discovered reliably, ask before making the change.

## Execution workflow

1. **Preflight**
   - Confirm the repository is reachable and the requested branch exists; create or push a branch only when the user explicitly asks for it.
   - Inspect Jenkins for an equivalent working job and reuse its conventions where they match the requested service.
   - Check the target port, existing container/job names, runtime directories, and the health endpoint. Do not overwrite an unrelated service.

2. **Jenkins job**
   - Prefer the naming pattern `<service>-<component>-<environment>`, such as `crm-api-dev`.
   - Configure the exact repository URL, credentials reference, and `*/<branch>` checkout.
   - Keep the pipeline reproducible: checkout, build/test, package or image build, deploy, verify, and post-build notification.
   - Use Jenkins credentials or the configured secret store for Git, webhook, registry, and notification secrets. Never place secret values in this skill, source files, console output, or the final report.

3. **Webhook**
   - Configure a push-only webhook for the selected branch when the provider supports branch filtering; otherwise rely on the Jenkins branch filter.
   - Use the job's final name in the webhook target after any rename.
   - Verify the provider delivery response is HTTP 200 and that Jenkins creates a build. A successful HTTP response without a Jenkins build is not a complete success.
   - Keep webhook secret validation symmetric: either configure the same secret on both sides or use the existing working server convention. Do not silently disable validation on a production endpoint.

4. **Build and deployment**
   - Use the project's actual build system and Dockerfile; do not assume Maven, Node, or a fixed artifact name.
   - Keep container-internal ports stable when possible and allocate a unique host port. For example, `18084:8080` means the service listens on 8080 inside the container and is exposed as 18084 on the host.
   - Isolate service runtime paths under a service directory, for example `/home/znder/crm/logs` and `/home/znder/crm/uploadPath`; create and permission them in the image or an explicit initialization step.
   - Replace only the target service container, preserve the previous image tag when possible, and make rollback information visible.

5. **Verification and notification**
   - Verify build result, deployed image/container, host-port reachability, and the service health endpoint. Check dependencies reported by health if available.
   - Send success or failure through the existing Jenkins notifier. Include job, build number, branch, commit, environment, deployment target, and health result; redact credentials and tokens.
   - Report the complete chain, including any manual step, rejected webhook, skipped branch, or unverified notification.

## Safety boundaries

- Do not guess repository credentials, Jenkins credentials, webhook tokens, notification secrets, database passwords, or production targets.
- Do not delete or stop an unrelated job/container. Before replacing a target container, verify its exact name and image.
- Do not treat a copied pipeline as correct until its repository URL, branch, ports, runtime paths, credentials references, notifier, and health check are verified.
- If deployment fails, diagnose logs and configuration first. Apply a code or pipeline fix only when it is within the user's requested deployment scope, then rebuild and re-verify.
- Stop after repeated external failures or when a required choice changes the target environment; report the exact blocker and the safest next action.

## Supporting references

- Read [references/jenkins-pipeline.md](references/jenkins-pipeline.md) when creating or adapting the Jenkins pipeline, especially for Docker deployments and runtime directories.
- Read [references/webhook-providers.md](references/webhook-providers.md) when configuring or troubleshooting GitLab/Gogs/GitHub-compatible webhook delivery.
- Read [references/notifications.md](references/notifications.md) when configuring DingTalk, WeCom, Slack, or another Jenkins notification channel.

## Final report

Always provide:

- repository and branch;
- Jenkins job name and URL;
- webhook target and delivery result, without secret values;
- build number, commit, image/artifact, and deployment target;
- host port, health endpoint, and verification result;
- notification result;
- remaining risks or manual follow-up.

# Jenkins notification reference

Use this reference when the deployment must report to DingTalk or another team channel.

## Configuration principles

- Reuse an existing Jenkins notifier and robot/channel when it matches the target environment.
- Store webhook URLs, access tokens, signing secrets, and credentials in Jenkins protected configuration or a secret manager.
- Never paste a full token into pipeline source, a public job description, console output, screenshots, or the final report.
- Keep notification configuration separate from deployment commands so a notification failure is visible and does not hide the deployment result.

## Message fields

Include concise, actionable fields:

- service and environment;
- Jenkins job and build number;
- branch and commit;
- result: success or failure;
- host/container and host port;
- health endpoint result;
- link to Jenkins build log.

On failure, include the failed stage and a bounded, redacted error summary. Do not send passwords, access tokens, full environment dumps, or unrestricted logs.

## Verification

Confirm the notifier is attached to the intended job, then verify a real build result reaches the channel. A successful Jenkins build with no channel message is an incomplete delivery workflow.

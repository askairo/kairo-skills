# Git-compatible webhook reference

Use this reference for GitLab, Gogs, GitHub Enterprise, or another Git-compatible web interface.

## Common settings

- Event: push.
- Content type: JSON.
- Active: enabled.
- Target: the Jenkins webhook endpoint with the final job name.
- Secret: use the same secret as Jenkins when validation is enabled; keep it in the provider secret field and Jenkins credentials/configuration, never in source control.

## Branch behavior

If the provider supports branch filtering, restrict the webhook to the requested branch. Always keep a Jenkins-side branch filter as a second guard when the plugin provides one. Confirm the payload ref is `refs/heads/<branch>`.

## Delivery verification

Inspect the provider's latest delivery record:

- HTTP 200 indicates that Jenkins accepted the request at the endpoint.
- HTTP 403 usually indicates a secret mismatch, missing authentication, or a rejected request policy.
- HTTP 404 usually indicates a wrong endpoint or job name.
- HTTP 200 with no Jenkins build usually indicates a branch filter, disabled trigger, quiet period, or job-name mismatch.

After any Jenkins job rename, update the webhook target before testing a new push. Verify both the delivery record and the Jenkins build cause.

## Troubleshooting order

1. Confirm the webhook URL uses the final job name.
2. Confirm the job is enabled and its repository trigger is enabled.
3. Confirm branch filter and payload ref match.
4. Confirm the secret/validation mode is symmetric.
5. Re-send a known push delivery or make a minimal authorized test commit.
6. Check Jenkins logs only as far as needed to identify the rejection reason.

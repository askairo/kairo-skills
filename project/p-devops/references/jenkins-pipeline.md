# Jenkins pipeline reference

Use this reference when a job must be created, copied, renamed, or repaired.

## Job configuration

- Job name: `<service>-<component>-<environment>`.
- SCM URL: the exact repository clone URL, not a browser-only project URL.
- Credential: an existing Jenkins credential ID; never print or recreate its secret in a pipeline.
- Branch: `*/<branch>` in checkout and the same branch in the webhook/branch filter.
- Trigger: the repository's push webhook, with the final Jenkins job name.
- Build retention: use the server's established retention policy.
- Concurrency: disable concurrent deployments to the same environment unless the service explicitly supports them.

## Declarative stage shape

Adapt commands to the repository:

```groovy
pipeline {
  agent any
  options {
    disableConcurrentBuilds()
    timestamps()
  }
  stages {
    stage('Checkout') { steps { /* checkout exact branch */ } }
    stage('Build') { steps { /* test/package */ } }
    stage('Image or Artifact') { steps { /* build and tag */ } }
    stage('Deploy') { steps { /* replace only target */ } }
    stage('Verify') { steps { /* port + health endpoint */ } }
  }
  post {
    success { /* archive or publish if required */ }
    failure { /* collect bounded logs */ }
  }
}
```

Use immutable build tags for deployment and keep a `latest` tag only as a convenience. The deployed tag and commit must be visible in Jenkins logs or metadata.

## Docker deployment rules

- Keep the application port inside the image stable, commonly `8080` for a backend service.
- Allocate host ports from the target server's current inventory; do not collide with existing services.
- Use explicit container names, restart policy, resource limits, environment variables, and labels where the server convention supports them.
- Before replacement, verify the exact target container name. After replacement, inspect running state and port mapping.
- Keep a previous image tag so a failed deployment can be rolled back without rebuilding.

## Runtime directories

Service-specific directories must exist before the process drops privileges. For a service under the shared `znder` root, use a service subtree such as:

```text
/home/znder/<service>/logs
/home/znder/<service>/uploadPath
```

Create them in the Dockerfile or an explicit root initialization step and grant the application user ownership. Make the application's logback/profile configuration point to the same paths; creating a directory that the application does not use is not a fix.

## Verification

Check all of the following:

1. Jenkins build is successful.
2. Container is running and not restart-looping.
3. Host port accepts connections.
4. Health endpoint returns HTTP 200 and the expected status.
5. Database/Redis or other dependency health is acceptable.
6. Jenkins post-build notifier reports the same build result.

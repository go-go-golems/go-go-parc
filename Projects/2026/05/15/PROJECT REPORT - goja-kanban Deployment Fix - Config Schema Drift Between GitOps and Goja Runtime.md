---
title: "goja-kanban Deployment Fix — Config Schema Drift Between GitOps and Goja Runtime"
aliases:
  - goja-kanban deployment fix
  - goja hosting site scripts schema drift
  - GOJA-SITE-SCRIPTS-NOT-FOUND report
  - goja-site scripts required deployment report
tags: [project-report, goja, gitops, argocd, k3s, kubernetes, deployment, debugging, static-site]
status: active
type: project-report
created: 2026-05-15
repo: /home/manuel/code/wesen/2026-03-27--hetzner-k3s
related_repos:
  - /home/manuel/code/wesen/2026-05-03--goja-hosting-site
ticket: GOJA-SITE-SCRIPTS-NOT-FOUND
pull_request: https://github.com/wesen/2026-03-27--hetzner-k3s/pull/85
live_image: ghcr.io/wesen/2026-05-03--goja-hosting-site:sha-b52aecc
public_urls:
  - https://trail.kanban.yolo.scapegoat.dev/
  - https://editorial.kanban.yolo.scapegoat.dev/
  - https://crm.kanban.yolo.scapegoat.dev/
  - https://pizza.kanban.yolo.scapegoat.dev/
---

# goja-kanban Deployment Fix — Config Schema Drift Between GitOps and Goja Runtime

This report explains the `goja-kanban` deployment failure that occurred when the Hetzner K3s GitOps repository deployed a newer `goja-site` image without updating the runtime configuration schema. The goal is to make the failure understandable to the next engineer who has to change this deployment: which files define the system, why the old deployment failed, how the fix was validated, and what guard should be added next.

> [!summary]
> The deployment failed because the newer `goja-site` binary expects each site to declare `scripts:` as a list, while the GitOps ConfigMap still declared the old scalar key `scriptsDir:`. PR #85 fixed the ConfigMap and redeployed the published image `sha-b52aecc`. Argo CD is now `Synced` and `Healthy`, the pod is running, and all four public site hosts return HTTP 200.

## The shortest version

The live system now runs:

```text
Argo CD Application: goja-kanban
Namespace:           goja-kanban
Image:               ghcr.io/wesen/2026-05-03--goja-hosting-site:sha-b52aecc
GitOps revision:     674296eaa79cb70d178052bbc52f261dd4274e38
Status:              Synced / Healthy
```

The four public sites are reachable:

```text
https://trail.kanban.yolo.scapegoat.dev/      -> 200 text/html
https://editorial.kanban.yolo.scapegoat.dev/  -> 200 text/html
https://crm.kanban.yolo.scapegoat.dev/        -> 200 text/html
https://pizza.kanban.yolo.scapegoat.dev/      -> 200 text/html
```

The fix lives in PR #85:

```text
https://github.com/wesen/2026-03-27--hetzner-k3s/pull/85
```

The main fix commit is:

```text
5c4cf07f565f10cc222e043d8c2eaf4426affd60
Fix goja kanban scripts config schema
```

The diary follow-up commit is:

```text
674296eaa79cb70d178052bbc52f261dd4274e38
Diary: record goja kanban rollout
```

## Why this project exists

`goja-kanban` is a multi-site Goja deployment. One container serves multiple small JavaScript applications. The request host chooses the site:

```text
trail.kanban.yolo.scapegoat.dev      -> trail site
editorial.kanban.yolo.scapegoat.dev  -> editorial site
crm.kanban.yolo.scapegoat.dev        -> crm site
pizza.kanban.yolo.scapegoat.dev      -> pizza site
```

The Kubernetes Deployment provides the binary and the packaged site files. The Kubernetes ConfigMap provides the runtime configuration. The binary and the ConfigMap must agree on the schema. If the binary expects a field named `scripts` and the ConfigMap provides a field named `scriptsDir`, the process cannot know where to load JavaScript files from.

This is the central invariant:

```text
The image tag and the ConfigMap schema must be changed together whenever the application config schema changes.
```

PR #81 violated that invariant. It changed the image only. PR #85 restored the invariant by changing the ConfigMap and image together.

## The deployment shape

The deployment is defined in the K3s GitOps repository:

```text
/home/manuel/code/wesen/2026-03-27--hetzner-k3s
```

The application source lives in:

```text
/home/manuel/code/wesen/2026-05-03--goja-hosting-site
```

The relevant GitOps files are:

```text
gitops/applications/goja-kanban.yaml
gitops/kustomize/goja-kanban/configmap.yaml
gitops/kustomize/goja-kanban/deployment.yaml
gitops/kustomize/goja-kanban/ingress.yaml
gitops/kustomize/goja-kanban/service.yaml
gitops/kustomize/goja-kanban/pvc.yaml
```

The Argo CD Application tracks the GitOps repository's `main` branch and renders `gitops/kustomize/goja-kanban` into the `goja-kanban` namespace:

```yaml
source:
  repoURL: https://github.com/wesen/2026-03-27--hetzner-k3s.git
  targetRevision: main
  path: gitops/kustomize/goja-kanban
syncPolicy:
  automated:
    prune: true
    selfHeal: true
```

The runtime config is mounted at:

```text
/etc/goja-site/sites.yaml
```

The container starts with:

```yaml
args:
  - serve-multi
  - --config
  - /etc/goja-site/sites.yaml
```

The site scripts are expected inside the image at paths such as:

```text
/app/sites/trail/scripts
/app/sites/editorial/scripts
/app/sites/crm/scripts
/app/sites/pizza/scripts
```

The Dockerfile in the application repo packages those paths:

```dockerfile
WORKDIR /app
COPY --from=build /out/goja-site /usr/local/bin/goja-site
COPY sites /app/sites
COPY deploy/sites.yaml /etc/goja-site/sites.yaml
ENTRYPOINT ["/usr/local/bin/goja-site"]
CMD ["serve-multi", "--config", "/etc/goja-site/sites.yaml"]
```

The ConfigMap overrides the default `/etc/goja-site/sites.yaml`, so the GitOps config is the config that matters in production.

## The config schema that changed

The older image expected a single string field named `scriptsDir`:

```yaml
sites:
  - name: trail
    scriptsDir: /app/sites/trail/scripts
```

The newer image expects a list field named `scripts`:

```yaml
sites:
  - name: trail
    dbPolicy: guarded
    scripts:
      - /app/sites/trail/scripts
```

The application code defines the newer schema in `pkg/app/multi_config.go`:

```go
type SiteConfig struct {
    Name        string   `json:"name" yaml:"name"`
    Host        string   `json:"host" yaml:"host"`
    ScriptDirs  []string `json:"scripts" yaml:"scripts"`
    DBPath      string   `json:"dbPath" yaml:"dbPath"`
    DBPolicy    DBPolicy `json:"dbPolicy" yaml:"dbPolicy"`
    ReadOnly    bool     `json:"readonly" yaml:"readonly"`
    AllowWrites bool     `json:"allowWrites" yaml:"allowWrites"`
}
```

The validation rule is direct:

```go
if len(site.ScriptDirs) == 0 {
    return fmt.Errorf("site %q: scripts is required", site.Name)
}
```

When YAML contains `scriptsDir`, the newer struct does not populate `ScriptDirs`. The loader then rejects the site before the HTTP server starts. The failure does not depend on Kubernetes, Traefik, TLS, or DNS. The process exits while reading its own config.

## What broke

The bad deploy was PR #81:

```text
Deploy goja-kanban-prod using ghcr.io/wesen/2026-05-03--goja-hosting-site:sha-b52aecc
```

That PR changed only this line:

```diff
- image: ghcr.io/wesen/2026-05-03--goja-hosting-site:sha-a6379c7
+ image: ghcr.io/wesen/2026-05-03--goja-hosting-site:sha-b52aecc
```

It did not change the ConfigMap. The ConfigMap still contained:

```yaml
sites:
  - name: trail
    scriptsDir: /app/sites/trail/scripts
  - name: editorial
    scriptsDir: /app/sites/editorial/scripts
  - name: crm
    scriptsDir: /app/sites/crm/scripts
  - name: pizza
    scriptsDir: /app/sites/pizza/scripts
```

At `sha-b52aecc`, the application schema had already changed to `scripts:`. The resulting startup failure was reproduced outside production:

```text
Error: site "trail": scripts is required
exit status 1
```

The rollback PR #84 changed the image back to `sha-a6379c7`, which restored service because the older binary still accepted `scriptsDir:`. That rollback made production healthy, but it did not fix the underlying schema drift.

## The fixed GitOps config

PR #85 changed the ConfigMap to the newer schema and redeployed `sha-b52aecc` in the same change.

The fixed ConfigMap body is:

```yaml
addr: ":8080"
dataDir: "/data/sites"
baseDomain: "kanban.yolo.scapegoat.dev"
dev: false
sites:
  - name: trail
    dbPolicy: guarded
    scripts:
      - /app/sites/trail/scripts
  - name: editorial
    dbPolicy: guarded
    scripts:
      - /app/sites/editorial/scripts
  - name: crm
    dbPolicy: guarded
    scripts:
      - /app/sites/crm/scripts
  - name: pizza
    dbPolicy: guarded
    scripts:
      - /app/sites/pizza/scripts
```

The fixed Deployment image is:

```yaml
image: ghcr.io/wesen/2026-05-03--goja-hosting-site:sha-b52aecc
```

This is the important part of the fix: the config schema and binary schema now match.

## The runtime sequence

The startup sequence is short enough to write as pseudocode:

```pseudocode
main:
    parse command serve-multi --config /etc/goja-site/sites.yaml
    cfg = LoadMultiConfig(configPath)
    server = NewMultiServer(cfg)
    server.Run()

LoadMultiConfig(path):
    bytes = read file
    cfg = yaml unmarshal bytes into MultiConfig
    cfg.Normalize()
    return cfg

Normalize(cfg):
    require at least one site
    for each site:
        require site.name
        require site.scripts has at least one entry
        derive host from site.name + baseDomain if host missing
        derive dbPath from dataDir + site.name + app.db if dbPath missing
        normalize DB policy
```

This is why the failure appeared before readiness checks could succeed. The server never reached `Run()`. It exited during `Normalize()`.

The fixed config lets the process reach the serving line:

```text
goja-site serving multi addr=:8080 config=/etc/goja-site/sites.yaml hosts=crm.kanban.yolo.scapegoat.dev, editorial.kanban.yolo.scapegoat.dev, pizza.kanban.yolo.scapegoat.dev, trail.kanban.yolo.scapegoat.dev
```

## System diagram

```mermaid
flowchart TD
    GitHubMain[GitHub main branch] --> Argo[Argo CD Application goja-kanban]
    Argo --> Kustomize[gitops/kustomize/goja-kanban]
    Kustomize --> Deployment[Kubernetes Deployment]
    Kustomize --> ConfigMap[Kubernetes ConfigMap sites.yaml]
    Deployment --> Pod[goja-site container]
    ConfigMap --> MountedConfig[/etc/goja-site/sites.yaml]
    MountedConfig --> Loader[LoadMultiConfig]
    Loader --> Normalizer[Normalize SiteConfig]
    Normalizer --> MultiServer[Multi-site HTTP server]
    MultiServer --> Trail[trail host]
    MultiServer --> Editorial[editorial host]
    MultiServer --> CRM[crm host]
    MultiServer --> Pizza[pizza host]

    style ConfigMap fill:#eef,stroke:#446
    style Deployment fill:#eef,stroke:#446
    style Loader fill:#ffe,stroke:#884
    style Normalizer fill:#ffe,stroke:#884
    style MultiServer fill:#efe,stroke:#484
```

The diagram has one critical dependency: `ConfigMap` and `Deployment` both feed the same process. The image decides what schema is valid. The ConfigMap provides the data in that schema. A change to one can invalidate the other.

## What the validation proved

The ticket created a reusable validation script:

```text
ttmp/2026/05/15/GOJA-SITE-SCRIPTS-NOT-FOUND--analyze-goja-hosting-site-deployment-scripts-not-found-failure/scripts/06-validate-rendered-goja-kanban-config.sh
```

The script does four things:

1. It checks out the application repo at the target app commit, `b52aecc`.
2. It extracts the rendered GitOps ConfigMap content.
3. It rewrites only environment-specific paths for local execution:
   - `/data/sites` becomes a temporary local data directory.
   - `/app/sites/...` becomes the matching path in the app worktree.
4. It runs the application with the localized GitOps config and expects the server to keep running until `timeout` stops it.

The successful validation result was:

```text
go_run_exit_status=124
expected_status=124 when config is valid and timeout stops the server
```

The server printed:

```text
goja-site serving multi addr=127.0.0.1:0 config=... hosts=crm.kanban.yolo.scapegoat.dev, editorial.kanban.yolo.scapegoat.dev, pizza.kanban.yolo.scapegoat.dev, trail.kanban.yolo.scapegoat.dev
```

Exit status `124` is the expected result from GNU `timeout` when a long-running process is stopped after the timeout duration. In this validation, `124` means the config was accepted, the server started, and no startup error occurred before timeout.

The older reproduction script still fails locally with:

```text
Error: create site trail (trail.kanban.yolo.scapegoat.dev): create db directory: mkdir /data: permission denied
```

That is a local execution artifact. The production path `/data/sites` exists in the container and is backed by the PVC. The newer validation script avoids that false failure by localizing `dataDir`.

## Production rollout result

After PR #85 was merged, Argo was refreshed:

```bash
kubectl --kubeconfig /home/manuel/code/wesen/2026-03-27--hetzner-k3s/.cache/kubeconfig-tailnet.yaml \
  -n argocd annotate application goja-kanban \
  argocd.argoproj.io/refresh=hard --overwrite
```

The Application reached the expected state:

```text
NAME          SYNC STATUS   HEALTH STATUS   REVISION                                   PROJECT
goja-kanban   Synced        Healthy         674296eaa79cb70d178052bbc52f261dd4274e38   default
```

The pod is running:

```text
NAME                           READY   STATUS    RESTARTS
goja-kanban-67cf7d4bfd-m5wdx   1/1     Running   0
```

The Deployment image is:

```text
ghcr.io/wesen/2026-05-03--goja-hosting-site:sha-b52aecc
```

The public smoke test returned HTTP 200 for all four hosts:

```text
trail      200 text/html; charset=utf-8
editorial  200 text/html; charset=utf-8
crm        200 text/html; charset=utf-8
pizza      200 text/html; charset=utf-8
```

## What still deserves attention

The logs still show duplicate-column migration messages:

```text
duplicate column name: session_id
duplicate column name: tag
duplicate column name: due_date
duplicate column name: done
duplicate column name: image
duplicate column name: amount
duplicate column name: probability
duplicate column name: contact
duplicate column name: next_step
duplicate column name: source
```

These messages do not block startup. The server reaches its serving line and readiness succeeds. They should be treated as a separate migration-idempotency cleanup, not as the deployment failure discussed in this report.

The right fix is probably in the JavaScript site migration code or in the database helper layer. The desired behavior is:

```pseudocode
for each migration:
    if column already exists:
        skip migration step without logging an error
    else:
        apply migration step
```

The important distinction is that this is a log hygiene and migration correctness issue. It is not a Kubernetes rollout issue.

## The working rule for this deployment

The `goja-kanban` deployment has a small but strict release rule:

> Change the image and the ConfigMap together whenever the app config schema changes.

For this repository, an image-only PR is safe only when the new image accepts the exact same production `sites.yaml` schema as the old image. If the app repo changes `deploy/sites.yaml`, `pkg/app/multi_config.go`, or config validation behavior, the GitOps ConfigMap must be reviewed in the same release.

A pre-merge compatibility check should answer one concrete question:

```text
Can the target app commit start with the rendered GitOps ConfigMap?
```

The validation script added in the ticket is a practical prototype for that check.

## Recommended CI guard

The next improvement should be an automated guard in the image publish or GitOps PR workflow. The guard should run before an image bump PR is merged.

A minimal version can use this sequence:

```pseudocode
targetAppCommit = image tag without "sha-"
git checkout app repo at targetAppCommit
render gitops/kustomize/goja-kanban
extract ConfigMap data["sites.yaml"]
localize production-only paths for CI
run goja-site serve-multi --config localized-sites.yaml under timeout
assert exit status is 124
assert startup output contains "goja-site serving multi"
```

The guard should fail on the original problem:

```text
Error: site "trail": scripts is required
```

It should also fail if the image does not contain the expected script directories or if the config points to a site that the image no longer packages.

## Chronology

```text
PR #81  -> image-only bump from sha-a6379c7 to sha-b52aecc
        -> failed because ConfigMap still used scriptsDir

PR #84  -> rollback from sha-b52aecc to sha-a6379c7
        -> restored service because older image accepted scriptsDir

Ticket GOJA-SITE-SCRIPTS-NOT-FOUND
        -> reproduced failure outside production
        -> identified scriptsDir vs scripts schema drift
        -> validated fixed config shape

PR #85  -> ConfigMap scripts list schema + image sha-b52aecc
        -> merged and deployed
        -> Argo Synced / Healthy
        -> four public hosts returned 200
```

## Important project docs

The full analysis ticket lives in the GitOps repo:

```text
/home/manuel/code/wesen/2026-03-27--hetzner-k3s/ttmp/2026/05/15/GOJA-SITE-SCRIPTS-NOT-FOUND--analyze-goja-hosting-site-deployment-scripts-not-found-failure
```

Key files:

```text
design-doc/01-deployment-failure-analysis.md
reference/01-investigation-diary.md
scripts/01-static-contract-check.sh
scripts/02-capture-goja-kanban-cluster-state.sh
scripts/03-github-image-pr-check.sh
scripts/04-reproduce-b52-config-mismatch.sh
scripts/05-validate-fixed-config-shape.sh
scripts/06-validate-rendered-goja-kanban-config.sh
```

The updated reMarkable bundle was uploaded as:

```text
/ai/2026/05/15/GOJA-SITE-SCRIPTS-NOT-FOUND/GOJA_SITE_DEPLOYMENT_FIX.pdf
```

## Related notes

- [[ARTICLE - Kanban DSL - Server Rendered Boards with Goja Callbacks]]
- [[PROJECT REPORT - go-go-host Beta Bringup - From Local MVP to Public Hosted Runtime]]

## Near-term next steps

1. Add the rendered-config compatibility check to CI or to the app image publish workflow.
2. Clean up duplicate-column migration logs so startup logs only show actual failures.
3. Decide whether the app should temporarily accept both `scriptsDir` and `scripts`, or keep the current strict schema and rely on release validation.
4. Document the config schema in the app repo next to `deploy/sites.yaml` so GitOps authors do not have to infer it from Go struct tags.

## Project working rule

> [!important]
> Treat runtime configuration as part of the release. A Goja image bump is not complete until the GitOps ConfigMap has been validated against the exact app commit behind that image tag.

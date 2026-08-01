---
title: "Playbook: Deploy a Vite Static Site on the Shared K3s Host"
aliases:
  - Vite static site deployment
  - shared static-sites host
  - static publisher Job deployment
  - GHCR GitOps static site
tags:
  - playbook
  - frontend
  - vite
  - static-sites
  - gitops
  - argocd
  - kubernetes
  - k3s
  - github-actions
  - ghcr
  - vault
status: active
type: playbook
created: 2026-08-01
repo:
  - /home/manuel/code/wesen/go-go-golems/infra-tooling
  - /home/manuel/code/wesen/2026-03-27--hetzner-k3s
  - /home/manuel/code/wesen/terraform
related:
  - "[[Research/KB/Projects/infrastructure-and-release]]"
  - "[[Research/playbooks/infra/PLAYBOOK - Onboarding a Source Repository to the GitOps Image Pipeline]]"
  - "[[Projects/2026/06/09/ARTICLE - Static-Sites Deployment - A Three-Contract Model for Shipments]]"
  - "[[Projects/2026/07/29/ARTICLE - Static Site Delivery Through GHCR GitOps Argo CD and Cloudflare]]"
---

# Playbook: Deploy a Vite Static Site on the Shared K3s Host

This is the standard procedure for deploying a browser-only Vite site to the shared static-site host on the Hetzner k3s cluster. It applies to React, TypeScript, Storybook, and plain Vite applications whose production output is a directory containing `index.html` and static assets.

The key design decision is that the application image is **not a web server**. The image is an immutable release bundle containing `/site`. A short-lived Kubernetes publisher Job copies that directory into the shared static-sites PersistentVolumeClaim. The existing Caddy server serves the selected release by hostname. Traefik and cert-manager provide public HTTPS.

```text
Vite source repository
  -> pnpm build
  -> Docker image containing /site
  -> GHCR immutable sha image
  -> GitOps PR changes publisher Job release tokens
  -> Argo CD runs publisher Job
  -> shared static-sites PVC: /srv/sites/<host>/current
  -> shared Caddy host
  -> Traefik HTTPS Ingress
  -> https://<host>
```

## 1. When this playbook applies

Use this playbook when all of the following are true:

- the application is primarily browser-side;
- the build produces static files;
- there is no required application API, database, login session, or server-side image processing;
- the site can be served from a directory with `index.html` at its root;
- the target hostname should be served by the cluster's existing shared static host.

Examples include:

- a Vite/React production build in `dist/`;
- a Vite TypeScript tool that performs all processing in the browser;
- a Storybook build in `storybook-static/`;
- a static documentation or marketing site;
- a generated frontend bundle with client-side fallback routing.

Do **not** use this playbook when the application needs a long-running backend, server-side rendering, WebSockets, a database, persistent application state, or an API that must share the same origin. Use the normal application onboarding playbook and deploy a dedicated workload instead.

## 2. Ownership boundaries

The deployment is intentionally split across repositories.

| Boundary | Owner | Contract |
| --- | --- | --- |
| Source and build | Source repository | `pnpm build` produces a complete static tree with `index.html`. |
| Artifact packaging | Source repository and shared CI | OCI image contains only the approved static tree under `/site`. |
| Release handoff | `go-go-golems/infra-tooling` | Reads `deploy/gitops-targets.json` and opens a GitOps PR. |
| Desired cluster state | `wesen/2026-03-27--hetzner-k3s` | Publisher Job, Ingress, Vault wiring, and Argo Application. |
| Secret values | Vault | GHCR image-pull credential, if the package is private. |
| DNS | Terraform | Hostname resolves to the cluster ingress. |
| Serving | Shared `static-sites-host` Caddy Deployment | Reads `/srv/sites/{host}/current` from the shared PVC. |

The source repository must not directly call `kubectl` against production. The GitOps repository must not build frontend artifacts. The shared Caddy Deployment must not be modified for each new site.

## 3. Source repository contract

### 3.1 Build the Vite output

For a normal Vite project:

```bash
corepack enable
pnpm install --frozen-lockfile
pnpm test
pnpm build
test -f dist/index.html
```

The output directory may be named something else, but the Dockerfile should make the contract explicit by copying that directory to `/site`.

For a client-side router, configure the Vite base URL and the shared Caddy fallback intentionally. The shared host uses:

```caddy
root * /srv/sites/{host}/current
try_files {path} {path}/ /index.html
file_server
```

A direct request to a client-side route therefore loads `index.html`; an existing asset path is served directly.

### 3.2 Package the artifact, not a server

Use a small artifact-carrier Dockerfile. The Dockerfile should not run Nginx, Caddy, Node, `vite preview`, or a development server.

```dockerfile
FROM alpine:3.20

WORKDIR /
COPY dist/ /site/

RUN test -f /site/index.html \
    && find /site -type f | sort > /site-manifest.txt
```

If the build is produced inside the CI job, the source workflow must run the build before the Docker build. For example:

```yaml
with:
  setup_go: false
  test_command: corepack enable && pnpm install --frozen-lockfile && pnpm test && pnpm build && test -f dist/index.html
```

The `.dockerignore` must not exclude the generated output that the Dockerfile copies. It should exclude `node_modules`, `.git`, local caches, screenshots, and ticket workspaces, but preserve `dist/` for the packaging step.

Validate the artifact locally:

```bash
pnpm install --frozen-lockfile
pnpm build
docker build -f Dockerfile.static -t site:verify .
docker run --rm --entrypoint sh site:verify \
  -c 'test -f /site/index.html && find /site -maxdepth 2 -type f | sort'
```

Positive file selection is safer than copying the whole repository. If the source repository contains private fonts, design files, test fixtures, or credentials, explicitly copy only the public output files or the generated production directory.

## 4. GitOps handoff contract

Create `deploy/gitops-targets.json` in the source repository:

```json
{
  "targets": [
    {
      "name": "my-vite-site-prod",
      "gitops_repo": "wesen/2026-03-27--hetzner-k3s",
      "gitops_branch": "main",
      "manifest_path": "gitops/kustomize/my-vite-site/publish-job.yaml",
      "container_name": "publish",
      "patch_strategy": "static-publisher-job"
    }
  ]
}
```

`static-publisher-job` is mandatory. A publisher Job encodes the release SHA in multiple places:

- Job name;
- release label;
- image tag;
- shell variable used for the PVC release directory.

Kubernetes Job pod templates are immutable. Changing only the image field causes Argo to reject the update or leaves the old Job in place. The shared `infra-tooling` action rewrites all `sha-*` tokens together.

Validate the target file with the shared tooling repository:

```bash
python3 /home/manuel/code/wesen/go-go-golems/infra-tooling/scripts/gitops/validate_gitops_targets.py \
  deploy/gitops-targets.json
```

### 4.1 Reusable workflow

The source workflow should call:

```yaml
name: publish-static-site

on:
  pull_request:
  push:
    branches: [main]

permissions:
  contents: read
  packages: write
  pull-requests: write
  id-token: write

jobs:
  release:
    uses: go-go-golems/infra-tooling/.github/workflows/publish-ghcr-image.yml@main
    secrets: inherit
    with:
      dockerfile: ./Dockerfile.static
      build_context: .
      setup_go: false
      test_command: corepack enable && pnpm install --frozen-lockfile && pnpm test && pnpm build && test -f dist/index.html
      gitops_target_config: deploy/gitops-targets.json
      push_image: ${{ github.event_name != 'pull_request' }}
      open_gitops_pr: ${{ github.event_name != 'pull_request' && github.ref == 'refs/heads/main' }}
      gitops_pr_token_source: github_app
      vault_role: <site>-gitops-pr
      gitops_app_secret_path: kv/data/ci/github/<site>/gitops-pr-app
      gitops_app_owner: wesen
      gitops_app_repositories: 2026-03-27--hetzner-k3s
```

Use the source repository's actual GitHub owner and repository in the Vault JWT role. Inspect `git remote -v`; never derive identity from a local directory codename.

The image is published as `ghcr.io/<owner>/<repo>:sha-<commit>`. The source workflow opens a PR; it does not apply Kubernetes resources.

## 5. Cluster package contract

Each site gets a Kustomize package under:

```text
gitops/kustomize/<site>/
  serviceaccount.yaml
  vault-connection.yaml
  vault-auth.yaml
  vault-static-secret-image-pull.yaml
  publish-job.yaml
  ingress.yaml
  kustomization.yaml
```

The package is namespaced to `static-sites`. Do not add a per-site Namespace, Deployment, Service, PVC, or NetworkPolicy unless the shared-host architecture has explicitly changed.

### 5.1 ServiceAccount and Vault resources

Use a unique ServiceAccount and a unique `VaultConnection` name for every site. Sharing a `VaultConnection` named `vault` between Argo Applications creates `SharedResourceWarning` ownership conflicts.

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: my-vite-site
  annotations:
    argocd.argoproj.io/sync-wave: "-2"
imagePullSecrets:
  - name: my-vite-site-ghcr-pull
```

The VaultStaticSecret is required only when the GHCR image is private. Its contract is:

```text
kv/apps/<site>/prod/image-pull
  server   = ghcr.io
  username = approved package-reader identity
  password = read:packages credential
  auth     = base64(username:password)
```

The generated Kubernetes Secret must be type `kubernetes.io/dockerconfigjson`. Never commit the Docker config or token.

### 5.2 Publisher Job

Use a placeholder release with seven hexadecimal characters. It must be replaced by the first GitOps PR before the Job can run against a real image.

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: publish-my-vite-site-sha-0000000
  annotations:
    argocd.argoproj.io/sync-wave: "1"
    argocd.argoproj.io/compare-options: IgnoreExtraneous
    argocd.argoproj.io/sync-options: Replace=true
  labels:
    app.kubernetes.io/name: my-vite-site
    app.kubernetes.io/component: publisher
    static.wesen.dev/host: my-vite-site.yolo.scapegoat.dev
    static.wesen.dev/release: sha-0000000
spec:
  backoffLimit: 2
  template:
    metadata:
      labels:
        app.kubernetes.io/name: my-vite-site
        app.kubernetes.io/component: publisher
    spec:
      restartPolicy: OnFailure
      enableServiceLinks: false
      serviceAccountName: my-vite-site
      imagePullSecrets:
        - name: my-vite-site-ghcr-pull
      containers:
        - name: publish
          image: ghcr.io/<owner>/<repo>:sha-0000000
          imagePullPolicy: IfNotPresent
          command: ["sh", "-c"]
          args:
            - |
              set -eu
              host="my-vite-site.yolo.scapegoat.dev"
              release="sha-0000000"
              base="/srv/sites/${host}"
              target="${base}/releases/${release}"
              tmp="${target}.tmp"

              test -f /site/index.html
              rm -rf "${tmp}" "${target}"
              mkdir -p "${tmp}"
              cp -a /site/. "${tmp}/"
              mv "${tmp}" "${target}"
              ln -sfn "releases/${release}" "${base}/current"
              find "${target}" -maxdepth 3 -type f | sort | head -100
          volumeMounts:
            - name: static-sites-content
              mountPath: /srv/sites
      volumes:
        - name: static-sites-content
          persistentVolumeClaim:
            claimName: static-sites-content
```

The publisher copies into a temporary directory, moves the complete release into place, then updates `current`. A partially copied release is never selected. Retain the exact `host` and `release` token structure so `static-publisher-job` can update every occurrence.

### 5.3 Ingress

The Ingress routes to the existing shared service:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: my-vite-site
  annotations:
    argocd.argoproj.io/sync-wave: "2"
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  ingressClassName: traefik
  tls:
    - hosts:
        - my-vite-site.yolo.scapegoat.dev
      secretName: my-vite-site-tls
  rules:
    - host: my-vite-site.yolo.scapegoat.dev
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: static-sites-host
                port:
                  name: http
```

### 5.4 Kustomization and Argo Application

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
namespace: static-sites
resources:
  - serviceaccount.yaml
  - vault-connection.yaml
  - vault-auth.yaml
  - vault-static-secret-image-pull.yaml
  - publish-job.yaml
  - ingress.yaml
labels:
  - pairs:
      app.kubernetes.io/part-of: static-sites
      app.kubernetes.io/name: my-vite-site
```

The Argo Application belongs to the existing `static-sites` AppProject and targets the `static-sites` namespace:

```yaml
spec:
  project: static-sites
  source:
    repoURL: https://github.com/wesen/2026-03-27--hetzner-k3s.git
    targetRevision: HEAD
    path: gitops/kustomize/my-vite-site
  destination:
    server: https://kubernetes.default.svc
    namespace: static-sites
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
```

## 6. DNS, TLS, and activation order

Before activating Argo:

```bash
dig +short my-vite-site.yolo.scapegoat.dev
```

The hostname must resolve to the cluster ingress. Check the authoritative Terraform zone first. The existing `scapegoat.dev` zone has a wildcard `*.yolo` record pointing at the k3s ingress, so most `*.yolo.scapegoat.dev` sites do not need an individual DNS record. Do not create a duplicate record without checking the zone's existing records and Terraform state.

Activate in this order:

1. Build and test the Vite output.
2. Build the artifact image and verify `/site/index.html`.
3. Validate `deploy/gitops-targets.json`.
4. Seed the CI GitHub App credential path in Vault.
5. Seed the image-pull path if GHCR is private.
6. Apply the Kubernetes Vault policy and role declarations.
7. Push the source repository's `main` branch.
8. Verify the image exists in GHCR.
9. Review and merge the GitOps PR.
10. Apply the new Argo Application once, because this cluster does not auto-create new Applications from files in `gitops/applications/`.
11. Verify the publisher Job completes.
12. Verify the Certificate is Ready and the HTTPS hostname serves the new release.

First-time Argo bootstrap:

```bash
cd /home/manuel/code/wesen/2026-03-27--hetzner-k3s
export KUBECONFIG=$PWD/kubeconfig-<tailscale-host>.yaml
kubectl apply -f gitops/applications/<site>.yaml
kubectl -n argocd annotate application <site> \
  argocd.argoproj.io/refresh=hard --overwrite
```

If the AppProject itself is new, apply its project manifest first. The shared `static-sites` AppProject already permits the `static-sites` namespace.

## 7. Validation

### Source and artifact

```bash
pnpm install --frozen-lockfile
pnpm test
pnpm build
test -f dist/index.html
docker build -f Dockerfile.static -t site:verify .
docker run --rm --entrypoint sh site:verify -c 'test -f /site/index.html'
```

### GitOps

```bash
python3 /home/manuel/code/wesen/go-go-golems/infra-tooling/scripts/gitops/validate_gitops_targets.py deploy/gitops-targets.json
cd /home/manuel/code/wesen/2026-03-27--hetzner-k3s
kubectl kustomize gitops/kustomize/<site> >/tmp/site.yaml
kubectl apply --dry-run=client -f /tmp/site.yaml
bash scripts/validate_gitops.sh
```

### Cluster

```bash
kubectl -n argocd get application <site>
kubectl -n static-sites get job,pod,ingress,certificate,vaultauth,vaultstaticsecret,secret
kubectl -n static-sites logs job/publish-<site>-<release>
kubectl -n static-sites describe certificate <site>-tls
curl -fsSI https://<site>.yolo.scapegoat.dev/
curl -fsS https://<site>.yolo.scapegoat.dev/ | head
```

Check that:

- the Argo Application is `Synced` and `Healthy`;
- the publisher Job is `Complete`;
- the image-pull `VaultStaticSecret` is Ready when used;
- `current` points at the expected release;
- the certificate is Ready;
- the response is HTTPS and contains the expected `index.html`;
- direct asset URLs work;
- client-side routes fall back to `index.html` if the site uses a router.

## 8. Failure modes

| Symptom | Likely cause | Action |
| --- | --- | --- |
| Workflow has `startup_failure` and zero jobs | Reusable workflow could not be loaded | Check repository/ref permissions and the workflow reference. |
| Docker image lacks `/site/index.html` | Build did not run or `.dockerignore` excluded output | Build before Docker packaging and inspect the image manifest. |
| GitOps PR changes only `image:` | Missing patch strategy | Set `patch_strategy: static-publisher-job`. |
| Argo reports immutable Job field | Job name/release tokens were not changed | Let infra-tooling rewrite all `sha-*` tokens. |
| Publisher Pod has `ImagePullBackOff` | GHCR private or VSO pull Secret not Ready | Check package visibility, Vault path, Secret type, and ServiceAccount. |
| Argo reports `SharedResourceWarning` | Two site Applications own the same VaultConnection | Use a unique VaultConnection per site. |
| Job completes but site returns 404 | Host/path mismatch or `current` was not updated | Inspect Job logs and `/srv/sites/<host>`. |
| Certificate remains Pending | DNS does not resolve before ACME validation | Verify Terraform/DNS and inspect Certificate, Challenge, and Order. |
| Assets return 404 but root works | Wrong Vite base path or asset URLs | Build for `/`, inspect generated HTML, and check the asset paths. |
| Browser route returns 404 | Shared Caddy fallback missing or route not under `/` | Confirm `try_files {path} {path}/ /index.html`. |
| Old release still serves | Publisher Job did not run or Application is stale | Check Job completion, Argo sync revision, and the `current` symlink. |

## 9. Rollback

Rollback is a Git change to the publisher Job image/release pin. Choose a previously verified GHCR `sha-*` image, update the target through a reviewed GitOps PR, and let Argo replace the Job. Do not copy files manually into the PVC unless recovering from a documented cluster failure.

The publisher's versioned directories make rollback inspectable:

```text
/srv/sites/<host>/releases/sha-old
/srv/sites/<host>/releases/sha-new
/srv/sites/<host>/current -> releases/sha-new
```

A rollback should repoint `current` through a new publisher Job or a controlled operator procedure that preserves the same release layout and audit trail.

## 10. Worked mapping for CAM

For the ABS Bicolor V-Engraver, the intended mapping is:

| Concern | CAM value |
| --- | --- |
| Source repository | `go-go-golems/go-go-cam` |
| Local checkout | `/home/manuel/code/wesen/2026-07-31--cat-mill-roam-fable` |
| Build output | `dist/` |
| Artifact path | `/site/` |
| Public host | `cam.yolo.scapegoat.dev` |
| GitOps package | `gitops/kustomize/cam/` |
| Publisher manifest | `gitops/kustomize/cam/publish-job.yaml` |
| Publisher container | `publish` |
| GitOps strategy | `static-publisher-job` |
| Static namespace | `static-sites` |
| Image-pull Vault path | `kv/apps/cam/prod/image-pull` |
| CI GitHub App path | `kv/data/ci/github/cam/gitops-pr-app` |
| Shared service | `static-sites-host:80` |

The CAM browser application must not receive a server-side upload endpoint as part of this deployment. Its image-processing and G-code generation remain in the browser; the cluster only serves the immutable JavaScript, CSS, HTML, and embedded sample asset files.

## Related references

- [[Research/KB/Projects/infrastructure-and-release]]
- [[Research/playbooks/infra/PLAYBOOK - Onboarding a Source Repository to the GitOps Image Pipeline]]
- [[Projects/2026/06/09/ARTICLE - Static-Sites Deployment - A Three-Contract Model for Shipments]]
- [[Projects/2026/07/29/ARTICLE - Static Site Delivery Through GHCR GitOps Argo CD and Cloudflare]]
- `/home/manuel/code/wesen/2026-03-27--hetzner-k3s/gitops/kustomize/static-sites-host/`
- `/home/manuel/code/wesen/go-go-golems/infra-tooling/actions/open-gitops-pr/`

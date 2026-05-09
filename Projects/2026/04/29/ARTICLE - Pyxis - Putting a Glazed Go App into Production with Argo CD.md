---
title: "Pyxis: Putting a Glazed Go App into Production with Argo CD"
aliases:
  - Pyxis Production Report
  - Pyxis Argo CD Deployment
  - Pyxis Glazed Productionization
tags:
  - article
  - project-report
  - pyxis
  - go
  - glazed
  - argocd
  - gitops
  - kubernetes
  - vault
  - production
status: active
type: article
created: 2026-04-29
repo: /home/manuel/code/wesen/2026-04-23--pyxis
source_ticket: PYXIS-PRODUCTION-ARGOCD-GLAZED
---

# Pyxis: Putting a Glazed Go App into Production with Argo CD

Putting Pyxis into production was not a single act of deployment. It was a sequence of small boundary clarifications: what belongs in the application repository, what belongs in the GitOps repository, what belongs in Vault, what belongs in PostgreSQL, and what belongs in the operator's head until it is written down. The technical work was Docker, GitHub Actions, GHCR, Kustomize, Vault Secrets Operator, PostgreSQL bootstrap jobs, Argo CD hooks, and smoke tests. The real work was making the handoff between those pieces explicit enough that the next deployment does not depend on memory.

This report tells that story as an engineering narrative. It is a record of what changed, why the design settled where it did, what broke during the first rollout, and what those failures teach about production systems. The source project is `/home/manuel/code/wesen/2026-04-23--pyxis`; the GitOps repository is `/home/manuel/code/wesen/2026-03-27--hetzner-k3s`; the ticket workspace is `PYXIS-PRODUCTION-ARGOCD-GLAZED`.

> [!summary]
> - Pyxis now runs in the k3s cluster through Argo CD, with its desired state declared in the GitOps repo and its image published from the app repo to GHCR.
> - The production path uses Vault Secrets Operator for runtime, image-pull, and PostgreSQL admin secrets; a bootstrap Job creates the app database and role; a migration Job runs `pyxis migrate up` before the Deployment rolls.
> - The main rollout failures were instructive: local Go `replace` directives do not survive Docker, Pyxis currently needs CGO because of Glazed help, GitHub Actions clones need Git author identity, GitOps tokens expire or get misconfigured, and Docker's short SHA tag must match the image tag written into Kubernetes manifests.
> - The public site is live at `https://pyxis.yolo.scapegoat.dev`; the staff React app is not yet served as a production `/app` bundle, and real Discord OAuth remains blocked until the Discord application/bot is installed into the target guild with the right role visibility.

## The mental model: three repositories of truth

A production deployment is easier to reason about if we refuse to let one repository own everything. Pyxis follows a three-surface model.

The application repository owns source code and artifacts. It knows how to test Pyxis, build the web bundle, compile the Go binary, package the Docker image, publish the image, and ask the GitOps repository to deploy a particular immutable image tag. It should not own live Kubernetes state.

The GitOps repository owns desired runtime state. It describes the namespace, service accounts, Vault wiring, database bootstrap Job, migration Job, Deployment, Service, Ingress, PVC, and Argo CD Application. It should not build the application image.

The cluster owns actual state. Argo CD reconciles desired state into actual state. Vault Secrets Operator turns Vault paths into Kubernetes Secrets. Kubernetes schedules Jobs and Deployments. PostgreSQL persists the application data. The operator observes the cluster and fixes the contract when the actual state reveals a wrong assumption.

```mermaid
flowchart LR
    subgraph AppRepo[Pyxis app repo]
      Source[Go + Vite source]
      Tests[Tests and checks]
      Docker[Docker image]
      GHCR[GHCR sha tag]
      GitOpsPR[GitOps image-bump PR]
    end

    subgraph GitOpsRepo[k3s GitOps repo]
      Kustomize[Kustomize package]
      App[Argo CD Application]
      Manifests[Deployment / Jobs / Service / Ingress / PVC]
    end

    subgraph Cluster[k3s cluster]
      Argo[Argo CD]
      VSO[Vault Secrets Operator]
      Vault[Vault]
      PG[Shared PostgreSQL]
      Pod[Pyxis pod]
      PVC[Flyer PVC]
    end

    Source --> Tests --> Docker --> GHCR --> GitOpsPR
    GitOpsPR --> Manifests
    App --> Argo
    Manifests --> Argo
    Argo --> VSO
    VSO --> Vault
    Argo --> PG
    Argo --> Pod
    Pod --> PVC
    Pod --> PG
    Pod --> GHCR
```

This separation gives every failure a place to live. If an image tag does not exist, the app repo's publish contract is wrong. If the image exists but the cluster pulls the wrong tag, the GitOps handoff is wrong. If secrets do not appear in the namespace, the Vault/VSO contract is wrong. If the app cannot create tables, the bootstrap/migration sequence is wrong. The design is not valuable because it prevents all failures; it is valuable because failures become localizable.

## The starting point

Pyxis already had a useful shape before productionization began. It was a Go/Glazed command with a `serve` command, PostgreSQL-backed repositories, migrations, public APIs, staff APIs, a public Vite site, a staff React app, flyer storage, Discord OAuth scaffolding, and an optional embedded Discord bot. The system was real enough to deploy, but not yet packaged in a way that a cluster could consume without workstation assumptions.

The production target was intentionally modest:

| Concern | First production decision |
|---|---|
| Application artifact | One Docker image containing the `pyxis` binary and embedded public site. |
| Runtime command | `pyxis serve`. |
| Public URL | `https://pyxis.yolo.scapegoat.dev`. |
| Database | Reuse existing shared in-cluster PostgreSQL. |
| DB creation | Argo-synced bootstrap Job, not Terraform and not a Postgres operator. |
| Secrets | Vault paths synced into Kubernetes Secrets by Vault Secrets Operator. |
| Flyer storage | PVC mounted at `/data`, app writes `/data/flyers`. |
| Deployment control | GHCR image published by app repo; GitOps PR updates k3s repo; Argo CD reconciles. |
| Discord bot | Disabled for first web rollout. |
| Staff React app | Not yet production-served; public site and backend are live first. |

That last row matters. There are two frontend applications in the repo: `pyxis-user-site` and `pyxis-app`. The production Dockerfile currently builds and embeds the public user site. The staff app exists, and the staff APIs exist, but the production binary does not yet serve `pyxis-app` under a route like `/app`. That is not an incidental omission; it is a scope boundary for the first production rollout.

## Phase 1: making the application build as a container

The first production phase was packaging. A production container must build from the repository, not from the developer's filesystem. That rule sounds simple until a Docker build proves which dependencies are invisible.

The new `Dockerfile` uses three stages:

```text
node:22-bookworm-slim
  -> build web/packages/pyxis-user-site

golang:1.26-bookworm
  -> copy source
  -> copy built public site into internal/web/embed/public
  -> CGO_ENABLED=1 go build -tags embed -o /out/pyxis ./cmd/pyxis

debian:bookworm-slim
  -> copy pyxis binary
  -> copy bot scripts
  -> create appuser
  -> create /data/flyers
  -> run pyxis serve
```

This image is deliberately not a minimal static `scratch` image. The reason is not aesthetic. Pyxis currently needs CGO because the Glazed help system initializes `go-sqlite3`. A `CGO_ENABLED=0` build succeeded far enough to produce a binary, then failed immediately when smoke-testing help output:

```text
Binary was compiled with 'CGO_ENABLED=0', go-sqlite3 requires cgo to work. This is a stub
```

That error is a good example of why production packaging needs smoke tests, not just successful compilation. A binary that cannot print `--help` is not a production artifact. The fix was to use `CGO_ENABLED=1` and a Debian runtime image with the expected C runtime available.

The other early packaging failure came from Go modules. The repository originally used local `replace` directives pointing at sibling directories:

```text
github.com/go-go-golems/discord-bot => ../corporate-headquarters/discord-bot
github.com/go-go-golems/go-go-goja => ../corporate-headquarters/go-go-goja
```

That works on a workstation where those sibling paths exist. It fails inside a Docker build context where the repository is the boundary. The production fix was to remove the local replacements and use published module versions. This is the right failure to have early: it turns a hidden local dependency into an explicit release dependency.

A third packaging failure was quieter but equally important. The web build stage copied package files and workspace packages, but not the root `web/tsconfig.json`. TypeScript reported:

```text
error TS5083: Cannot read file '/src/web/tsconfig.json'.
```

The fix was to copy `web/tsconfig.json` into the Docker build stage. Again, the lesson is not "remember this file". The lesson is that a monorepo web build has a root contract, and a Dockerfile must copy the whole contract, not just the package that appears to be the target.

The resulting Makefile grew production-oriented targets: `ci`, `web-check`, `docker-build`, `docker-run`, `docker-smoke`, `golangci-lint-install`, `lintmax`, `gosec`, and `govulncheck`. The important target during this phase was `docker-smoke`, because it made the container prove that `pyxis --help` and `pyxis serve --help` work inside the runtime image.

## Phase 2: turning local defaults into production configuration

A container image is not yet a production application. It needs a runtime contract. Pyxis' `serve` command already accepted flags, but production should not require every operator to remember every flag. Kubernetes wants environment variables from Secrets and ConfigMaps. The `serve` command needed env-backed defaults.

The production environment contract became:

```text
PYXIS_BIND=0.0.0.0:8080
PYXIS_DATABASE_URL=postgres://pyxis_app:...@postgres.postgres.svc.cluster.local:5432/pyxis?sslmode=disable
PYXIS_WEBSITE_URL=https://pyxis.yolo.scapegoat.dev
PYXIS_SESSION_COOKIE_NAME=pyxis_session
PYXIS_FLYER_STORAGE_PATH=/data/flyers
PYXIS_FLYER_BASE_URL=/flyers
PYXIS_DISCORD_CLIENT_ID=...
PYXIS_DISCORD_CLIENT_SECRET=...
PYXIS_DISCORD_REDIRECT_URL=https://pyxis.yolo.scapegoat.dev/auth/discord/callback
DISCORD_BOT_TOKEN=...
DISCORD_GUILD_ID=...
DISCORD_ADMIN_ROLE_ID=...
DISCORD_BOOKER_ROLE_ID=...
DISCORD_DOOR_ROLE_ID=...
PYXIS_DISCORD_BOT_ENABLED=false
PYXIS_DISCORD_SYNC_ON_START=false
PYXIS_DISCORD_DEBUG=false
```

The two flyer variables are a small but important example of production hardening. A local app can write to `./data/flyers`; a Kubernetes app should write to a mounted volume. The cluster mounts a PVC at `/data`, and the app writes flyers under `/data/flyers`. The public URL prefix remains `/flyers`, so the application can serve uploaded assets with stable URLs while storage remains a runtime concern.

The session-secret audit produced a useful non-change. Pyxis sessions are server-side opaque session IDs stored in PostgreSQL. The browser cookie stores the random token, not a signed client-side payload. That means Pyxis does not currently need a `PYXIS_SESSION_SECRET`. Adding an unused secret would make the configuration look more secure without changing the security model. If Pyxis later moves to signed or encrypted client-side session cookies, then a session secret becomes necessary. Until then, PostgreSQL persistence and secure cookie behavior are the real session concerns.

## Phase 3: making GitHub produce tested images

The next boundary was CI/CD. If a cluster is going to pull images from GHCR, GitHub should be the place where those images are tested and published. The app repo gained workflows for validation, image publishing, linting, dependency scanning, CodeQL, Dependabot, and optional GoReleaser artifacts.

The workflow set is conventional, but the convention matters:

| Workflow | Purpose |
|---|---|
| `.github/workflows/push.yml` | Run generation checks, Go tests, web checks, and embedded binary build on PR/main. |
| `.github/workflows/publish-image.yml` | Build Docker images on PRs and publish GHCR images on `main`. |
| `.github/workflows/lint.yml` | Run golangci-lint with the repo's pinned linter version. |
| `.github/workflows/dependency-scanning.yml` | Run dependency review, `govulncheck`, and `gosec`. |
| `.github/workflows/codeql-analysis.yml` | Run CodeQL analysis for Go. |

The image publishing workflow uses `docker/metadata-action` to produce tags such as:

```text
ghcr.io/wesen/pyxis:main
ghcr.io/wesen/pyxis:sha-bf7e8d4
```

The `sha-...` tag is the deployment tag. The `main` tag is convenient for humans, but GitOps should pin immutable tags. A Deployment that says `main` is asking Kubernetes to run a moving target; a Deployment that says `sha-bf7e8d4` is a record of exactly what was requested.

GoReleaser was added for optional CLI artifacts. Its first validation found a version-specific config issue: `snapshot.name_template` is deprecated in GoReleaser v2. The fix was:

```yaml
snapshot:
  version_template: "{{ incpatch .Version }}-next"
```

That failure was not central to the web deployment, but it belongs in the production story because Pyxis is a Glazed command. The CLI deserves a release path even if the first deployment artifact is a Docker image.

## Phase 4: declaring the cluster state in GitOps

The k3s GitOps repository gained a new package under:

```text
gitops/kustomize/pyxis/
```

and an Argo CD Application:

```text
gitops/applications/pyxis.yaml
```

The package follows the existing `hair-booking` shape. It creates a namespace, two service accounts, Vault Secrets Operator resources, a database bootstrap script, a database bootstrap Job, a migration Job, a PVC, a Deployment, a Service, and an Ingress.

The ordering is important. Secrets must exist before jobs can consume them. The database must exist before migrations can run. Migrations should run before the app is considered rolled out. The app needs the PVC before it can serve uploaded flyer files.

```mermaid
flowchart TD
    NS[Namespace pyxis]
    SA[ServiceAccounts]
    VaultAuth[VaultAuth + VaultConnection]
    VSS[VaultStaticSecrets]
    Secrets[Kubernetes Secrets]
    Bootstrap[DB bootstrap Job]
    Migrate[Migration Job]
    PVC[pyxis-data PVC]
    Deploy[Pyxis Deployment]
    Svc[Service]
    Ing[Ingress]

    NS --> SA --> VaultAuth --> VSS --> Secrets
    Secrets --> Bootstrap
    Bootstrap --> Migrate
    Secrets --> Deploy
    PVC --> Deploy
    Migrate --> Deploy
    Deploy --> Svc --> Ing
```

The database strategy is intentionally simple. Pyxis reuses the shared in-cluster PostgreSQL service. The application database and role are created by an idempotent Kubernetes Job, not by Terraform and not by a Postgres operator. That is the right v1 choice for this cluster because the database/user lifecycle is cluster-local application state. Terraform is a better fit for cloud infrastructure, DNS, servers, and platform resources; a Postgres operator may be a future platform decision, but introducing it just for Pyxis v1 would add more moving parts than it removes.

The bootstrap Job reads two kinds of secrets:

- PostgreSQL admin connection information from `kv/infra/postgres/cluster`.
- Pyxis app database name/user/password from `kv/apps/pyxis/prod/runtime`.

The runtime Deployment reads only the app runtime secret. The PostgreSQL admin credential is limited to the bootstrap Job. This is the small security boundary that matters: the long-running application should not need the cluster admin database password.

The first GitOps package used an image placeholder:

```text
ghcr.io/wesen/pyxis:sha-REPLACE_ME
```

That placeholder is not meant to run. It is a declaration that image selection belongs to the CI-to-GitOps handoff.

## Phase 5: making image publication open GitOps PRs

Once GitHub could publish images and GitOps could describe Pyxis, the missing piece was the handoff. A successful image build should not require a human to edit a manifest by hand. It should open a pull request against the GitOps repo.

The app repo gained target metadata:

```json
{
  "targets": [
    {
      "name": "pyxis-prod-app",
      "gitops_repo": "wesen/2026-03-27--hetzner-k3s",
      "gitops_branch": "main",
      "manifest_path": "gitops/kustomize/pyxis/deployment.yaml",
      "container_name": "pyxis"
    },
    {
      "name": "pyxis-prod-migrate",
      "gitops_repo": "wesen/2026-03-27--hetzner-k3s",
      "gitops_branch": "main",
      "manifest_path": "gitops/kustomize/pyxis/migration-job.yaml",
      "container_name": "migrate"
    }
  ]
}
```

There are two targets because the Deployment and migration Job must use the same application image. If the Deployment runs one version and the migration Job runs another, the release is ambiguous. The database schema and the application binary should move together.

The updater script, `scripts/open_gitops_pr.py`, intentionally performs a narrow text patch rather than a full YAML parse-and-dump. It finds the named container and replaces the following `image:` line. This keeps the PR diff small:

```diff
-          image: ghcr.io/wesen/pyxis:sha-REPLACE_ME
+          image: ghcr.io/wesen/pyxis:sha-bf7e8d4
```

The first dry run revealed an easy mistake: dry-run mode patched files in the existing GitOps checkout before returning. That violates the meaning of dry-run. The fix was to store the original manifest text and restore it before exiting. Dry-run must not mean "make the change but do not commit"; it must mean "show what would change and leave the world as it was."

The script was also hardened to redact `GITOPS_PR_TOKEN` from logs. A token-bearing clone URL is convenient for CI, but a CI log is a hostile place for secrets. The command runner now redacts the token before printing commands or failure output.

The first real workflow run found another production detail that local testing often misses: a fresh GitHub runner clone has no Git author identity. The script could clone, patch, and stage the file, but `git commit` failed:

```text
Author identity unknown
fatal: empty ident name ... not allowed
```

The fix was to set local Git config inside the temporary GitOps clone:

```bash
git config user.name pyxis-ci
git config user.email pyxis-ci@users.noreply.github.com
```

The next failure was authentication on `git push`. The secret existed, but GitHub rejected it. The script was hardened to URL-encode the token in the HTTPS remote, but the practical fix was refreshing `GITOPS_PR_TOKEN` in the Pyxis repository. The token used by the workflow needs write access to the GitOps repo, not merely read access to the app repo. The useful rule is:

```text
Source app repo stores GITOPS_PR_TOKEN.
That token must be able to push branches and open PRs in the GitOps repo.
```

The working pattern was compared against `hair-booking`, which already used the same architectural flow. That comparison exposed the final deployment-tag mismatch.

## The short-SHA lesson

The most instructive production bug was not in Kubernetes. It was in a string.

The Docker metadata action published a short SHA tag:

```text
ghcr.io/wesen/pyxis:sha-e485670
```

The GitOps PR step wrote a full SHA tag:

```text
ghcr.io/wesen/pyxis:sha-e4856701629e48fd114747f8c4ae3363d4f1ed95
```

Both strings look reasonable. Only one existed in GHCR. Kubernetes told the truth:

```text
ghcr.io/wesen/pyxis:sha-e4856701629e48fd114747f8c4ae3363d4f1ed95: not found
```

The fix was to compute the image tag the same way `hair-booking` does:

```bash
IMAGE="ghcr.io/${{ github.repository_owner }}/pyxis:sha-${GITHUB_SHA::7}"
python3 scripts/open_gitops_pr.py --image "${IMAGE}"
```

The lesson is larger than Pyxis. Every artifact pipeline has a naming contract. The build step, registry, GitOps updater, and Kubernetes manifest must agree exactly. "It has the same commit in it" is not enough. The tag string is the API.

## Phase 6: first rollout

With the short-SHA fix in place, the `publish-image` workflow succeeded and opened two GitOps PRs:

```text
#50 pyxis-prod-app: deploy ghcr.io/wesen/pyxis:sha-bf7e8d4
#51 pyxis-prod-migrate: deploy ghcr.io/wesen/pyxis:sha-bf7e8d4
```

Those PRs were reviewed and merged. The Argo CD Application was applied once:

```bash
kubectl apply -f gitops/applications/pyxis.yaml
kubectl -n argocd annotate application pyxis argocd.argoproj.io/refresh=hard --overwrite
```

That one-time apply is necessary because this GitOps repo does not currently have an app-of-apps or ApplicationSet layer that automatically materializes every file under `gitops/applications/`. After the Application exists in the cluster, Argo CD can keep reconciling its source path.

Vault secrets and policies were written for Pyxis:

```text
kv/apps/pyxis/prod/runtime
kv/apps/pyxis/prod/image-pull
policy: pyxis-prod
policy: pyxis-db-bootstrap
role: auth/kubernetes/role/pyxis-prod
role: auth/kubernetes/role/pyxis-db-bootstrap
```

The runtime secret contains the app database credentials, public URL, Discord OAuth values, and role IDs. The image-pull secret contains GHCR credentials. The bootstrap policy can read the PostgreSQL admin secret and the Pyxis runtime DB values; the runtime policy can read only Pyxis runtime/image-pull material.

The first Argo sync got stuck on the old failed full-SHA migration hook. This is a subtle Argo CD behavior worth remembering: hook jobs can hold an operation at an older revision. When the hook is stuck because it references an immutable image that does not exist, a later Git fix does not automatically make the old hook correct. The recovery was:

```bash
kubectl -n argocd patch application pyxis --type merge -p '{"operation": null}'
kubectl -n pyxis delete job pyxis-migrate --ignore-not-found
kubectl -n argocd annotate application pyxis argocd.argoproj.io/refresh=hard --overwrite
```

After that, Argo synced the new revision. The database bootstrap Job completed. The migration Job completed. The Deployment became ready. The PVC bound. The Ingress received the expected address.

Final rollout state after the follow-up reconciliation was:

```text
Synced Healthy Succeeded successfully synced (all tasks run)
deployment.apps/pyxis 1/1
ghcr.io/wesen/pyxis:sha-edf2dcb
```

The final image changed from `sha-bf7e8d4` to `sha-edf2dcb` because documenting the rollout triggered another image publish and another pair of GitOps PRs. Those were merged to avoid leaving Pyxis with open drift PRs. That is a success and a smell at the same time. The automation works, but `publish-image.yml` should probably ignore documentation-only paths such as `ttmp/**` and maybe `docs/**` to avoid image churn from diary updates.

## Smoke tests: proving the system, not just the pod

A pod in `Running` state is not enough. Production smoke should test the path a user and the system actually need.

The health endpoint passed:

```bash
curl -k https://pyxis.yolo.scapegoat.dev/health
```

returned:

```json
{"status":"ok"}
```

The public site served embedded HTML from the Go binary:

```bash
curl -k https://pyxis.yolo.scapegoat.dev/
```

returned HTTP 200 and the built Vite index HTML.

The public API responded:

```bash
curl -k https://pyxis.yolo.scapegoat.dev/api/public/shows
```

returned:

```json
{}
```

The database smoke used a temporary PostgreSQL client pod and checked both migration metadata and the canonical ShowLog table:

```text
t|1
```

That output meant `public.show_logs` exists and `schema_migrations` has one row.

The flyer/PVC smoke wrote a file under the mounted volume from inside the running app pod:

```text
/data/flyers/smoke/pvc.txt
```

and fetched it through the public flyer route:

```bash
curl -k https://pyxis.yolo.scapegoat.dev/flyers/smoke/pvc.txt
```

which returned:

```text
ok
```

That last test matters because it crosses the boundary between application config, Kubernetes volume mount, and HTTP static serving. It proves that `PYXIS_FLYER_STORAGE_PATH=/data/flyers` and `PYXIS_FLYER_BASE_URL=/flyers` are not just set; they work together.

## Discord OAuth and the staff app boundary

There is one important caveat in the production story. The public site and backend are live, but the staff React app is not yet served in production. The repository has `web/packages/pyxis-app`, and the backend exposes `/api/app/...` and `/auth/discord/...`, but the production Dockerfile currently builds only `web/packages/pyxis-user-site` and embeds only the public site.

That means the next production UI task is not "set more secrets". It is a serving architecture change:

```text
Serve pyxis-app under /app while keeping pyxis-user-site at /.
```

The likely shape is:

```text
/                  -> public user-site SPA
/app/              -> staff pyxis-app SPA
/api/public/...    -> public backend API
/api/app/...       -> staff backend API, auth protected
/auth/...          -> Discord OAuth and session routes
/flyers/...        -> PVC-backed flyer assets
```

Discord OAuth itself needs these values in `kv/apps/pyxis/prod/runtime`:

```text
discord_client_id
discord_client_secret
discord_redirect_url=https://pyxis.yolo.scapegoat.dev/auth/discord/callback
discord_bot_token
discord_guild_id
discord_admin_role_id
discord_booker_role_id
discord_door_role_id
```

The Discord application must also include the redirect URI in the Developer Portal, and the bot must be installed into the configured guild. The known blocker before productionization was:

```text
{"message": "Unknown Guild", "code": 10004}
```

That error means the bot cannot see the guild. If the bot is installed but role lookup still fails, the Discord Developer Portal may need the Server Members Intent enabled. Pyxis maps Discord roles to local roles in this order:

```text
admin > booker > door > staff
```

If none of the configured role IDs match, the user becomes `staff`, which authenticates but does not have broad access to the protected staff endpoints.

## The educational failures

The deployment succeeded because each failure was treated as information rather than noise. These are the failures worth remembering.

### Workstation dependencies are not production dependencies

Local Go `replace` directives made sense during development. Docker revealed that they were not production dependencies. A container build is a useful truth machine because it has no access to sibling directories unless you deliberately give it that access.

### A compiled binary can still be unusable

`CGO_ENABLED=0` produced a binary that failed at help output because Glazed help touched `go-sqlite3`. Production smoke must execute the binary in the runtime image. Compilation is a necessary condition, not a sufficient one.

### Dry-run must not mutate

The first GitOps updater dry-run modified the local GitOps checkout. That is a broken dry-run. A dry-run should either operate on a disposable copy or restore every byte it changes.

### CI needs an identity

GitHub-hosted runners are not humans. If a script commits into another repository, it must configure `user.name` and `user.email`. This belongs in the script because the script owns the commit.

### A token can exist and still be wrong

The first `GITOPS_PR_TOKEN` existed, but push failed. The useful tests are not "can I clone?" or "does the secret have a name?". The useful tests are "can this token push a branch to the GitOps repo?" and "can it open a pull request?" Cloning can succeed anonymously if the repo is public, or locally through cached credentials.

### The tag string is the deployment API

`sha-e485670` and `sha-e4856701629e48fd114747f8c4ae3363d4f1ed95` refer to the same commit idea, but they are not the same registry tag. Kubernetes pulls strings, not intentions.

### Hooks can pin a failed revision

Argo CD hook jobs are powerful because they let bootstrap and migration work participate in sync. They can also keep an operation stuck at an older revision if the hook cannot complete. Knowing how to clear a stale operation and delete a failed hook is part of operating the system.

### Automation creates noise once it works

After the release path worked, documentation commits triggered image builds and GitOps PRs. That proved the pipeline, but it also created unnecessary deployment churn. The next refinement should be path filters or a split between application-source changes and documentation-only changes.

## Current production state

The cluster state at the end of the rollout was:

```text
Application: pyxis
Namespace: pyxis
URL: https://pyxis.yolo.scapegoat.dev
Argo: Synced Healthy
Image: ghcr.io/wesen/pyxis:sha-edf2dcb
Database: shared PostgreSQL, database pyxis, role pyxis_app
Storage: PVC pyxis-data mounted at /data
Flyers: /data/flyers served at /flyers
Discord bot: disabled in deployment env
```

The smoke evidence was:

```text
/health -> HTTP 200 {"status":"ok"}
/ -> HTTP 200 embedded public HTML
/api/public/shows -> HTTP 200 {}
DB -> public.show_logs exists; schema_migrations has one row
/flyers/smoke/pvc.txt -> HTTP 200 ok
```

The open production items are:

- Serve the staff `pyxis-app` bundle under `/app` in the production binary.
- Install/invite the Discord bot into the target guild and validate real OAuth login.
- Enable/verify Server Members Intent if Discord role lookup still fails.
- Decide whether to enable the embedded Discord bot after the web/auth rollout is stable.
- Add `paths-ignore` or similar filtering so documentation-only commits do not publish images and open GitOps PRs.
- Consider grouping Deployment and migration Job image bumps into a single GitOps PR.

## A reusable deployment sequence

The Pyxis deployment can be generalized into a repeatable playbook for similar Go web apps.

```text
1. Make the app build in a clean container.
2. Remove local filesystem assumptions from go.mod, web builds, and runtime config.
3. Add a production env contract.
4. Publish immutable GHCR image tags from CI.
5. Declare runtime state in the GitOps repo.
6. Put runtime and bootstrap secrets in Vault.
7. Use VSO to sync Kubernetes Secrets.
8. Use an idempotent DB bootstrap Job for app database/user creation.
9. Use a migration Job tied to the same image as the Deployment.
10. Let CI open GitOps PRs for image bumps.
11. Merge, let Argo reconcile, and smoke the real paths.
12. Record every failure because the failure is part of the system design.
```

The sequence is not complicated because each step is small. It becomes complicated only when steps are skipped and the operator has to infer hidden state from cluster symptoms. The main value of the Pyxis work is that those hidden assumptions are now files: Dockerfile, workflows, Kustomize manifests, Vault paths, scripts, playbooks, and a diary.

## Key files

Application repository:

```text
/home/manuel/code/wesen/2026-04-23--pyxis/Dockerfile
/home/manuel/code/wesen/2026-04-23--pyxis/Makefile
/home/manuel/code/wesen/2026-04-23--pyxis/.github/workflows/push.yml
/home/manuel/code/wesen/2026-04-23--pyxis/.github/workflows/publish-image.yml
/home/manuel/code/wesen/2026-04-23--pyxis/deploy/gitops-targets.json
/home/manuel/code/wesen/2026-04-23--pyxis/scripts/open_gitops_pr.py
/home/manuel/code/wesen/2026-04-23--pyxis/docs/deployment/pyxis-production-env.example
/home/manuel/code/wesen/2026-04-23--pyxis/docs/deployment/pyxis-ci-cd.md
/home/manuel/code/wesen/2026-04-23--pyxis/cmd/pyxis/cmds/serve.go
/home/manuel/code/wesen/2026-04-23--pyxis/pkg/config/config.go
/home/manuel/code/wesen/2026-04-23--pyxis/pkg/server/server.go
```

GitOps repository:

```text
/home/manuel/code/wesen/2026-03-27--hetzner-k3s/gitops/applications/pyxis.yaml
/home/manuel/code/wesen/2026-03-27--hetzner-k3s/gitops/kustomize/pyxis/kustomization.yaml
/home/manuel/code/wesen/2026-03-27--hetzner-k3s/gitops/kustomize/pyxis/deployment.yaml
/home/manuel/code/wesen/2026-03-27--hetzner-k3s/gitops/kustomize/pyxis/migration-job.yaml
/home/manuel/code/wesen/2026-03-27--hetzner-k3s/gitops/kustomize/pyxis/db-bootstrap-job.yaml
/home/manuel/code/wesen/2026-03-27--hetzner-k3s/gitops/kustomize/pyxis/runtime-secret.yaml
/home/manuel/code/wesen/2026-03-27--hetzner-k3s/gitops/kustomize/pyxis/postgres-admin-secret.yaml
/home/manuel/code/wesen/2026-03-27--hetzner-k3s/gitops/kustomize/pyxis/image-pull-secret.yaml
/home/manuel/code/wesen/2026-03-27--hetzner-k3s/gitops/kustomize/pyxis/persistentvolumeclaim.yaml
/home/manuel/code/wesen/2026-03-27--hetzner-k3s/gitops/kustomize/pyxis/ingress.yaml
```

Ticket evidence:

```text
/home/manuel/code/wesen/2026-04-23--pyxis/ttmp/2026/04/29/PYXIS-PRODUCTION-ARGOCD-GLAZED--turn-pyxis-into-a-deployed-glazed-application-on-argocd-k3s/reference/01-production-deployment-diary.md
/home/manuel/code/wesen/2026-04-23--pyxis/ttmp/2026/04/29/PYXIS-PRODUCTION-ARGOCD-GLAZED--turn-pyxis-into-a-deployed-glazed-application-on-argocd-k3s/sources/08-production-rollout-smoke.txt
```

## Closing: production as a chain of explicit contracts

The Pyxis rollout is a useful example because none of its pieces are exotic. A Go binary, a Vite app, PostgreSQL, Docker, GitHub Actions, GHCR, Kustomize, Vault, Argo CD, and Kubernetes Jobs are ordinary tools. Production complexity came from the spaces between them.

The app repo and GitOps repo had to agree on image tags. The Kubernetes Deployment and migration Job had to agree on the image. Vault and VSO had to agree on paths and keys. The bootstrap Job and runtime Deployment had to agree on database credentials without sharing unnecessary admin power. The public URL, Discord redirect URL, Ingress, and cookie security logic had to describe the same site. Each agreement became a file, a secret path, a workflow line, or a smoke test.

That is the practical lesson. Production is not the moment a pod turns green. Production is the set of contracts that make a green pod meaningful, reproducible, observable, and recoverable. Pyxis is now on that path: live, smoke-tested, documented, and ready for the next boundary—the staff app and real Discord OAuth—to be made equally explicit.

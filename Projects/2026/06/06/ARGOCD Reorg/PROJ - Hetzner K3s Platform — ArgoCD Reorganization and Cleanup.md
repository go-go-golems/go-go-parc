---
title: "Hetzner K3s Platform — ArgoCD Reorganization and Cleanup"
aliases:
  - "ARGOFCD Reorganization"
  - "K3s Platform ArgoCD Cleanup"
tags:
  - project
  - argocd
  - gitops
  - kubernetes
  - k3s
  - platform-engineering
  - arcfleanup
status: active
type: project
created: 2026-06-06
repo: /home/manuel/code/wesen/2026-03-27--hetzner-k3s
---

# Hetzner K3s Platform — ArgoCD Reorganization and Cleanup

## What changed, why it mattered, and what the platform looks like today

A single-node Hetzner K3s cluster serving 31 production applications was reorganized end-to-end: the documentation was audited and consolidated, nine deprecated applications were removed from both live cluster and GitOps, and all remaining applications were migrated from a flat `default` project into six structured ArgoCD AppProjects with standardized labels. The work also cleaned up leftover credentials, auth roles, Keycloak realms, operator scripts, and stale documentation references.

This note records the entire process as a single project report. It covers the starting state, the audit, the taxonomy design, the AppProject implementation, the live migration, the leftover cleanup, and the lessons learned. It is written for a future operator who needs to understand the current platform structure and the reasoning behind every structural decision.

> [!summary]
> - **Before:** 40 ArgoCD Applications in the `default` project, no labels, 20 overlapping documentation files, nine deprecated applications still deployed.
> - **After:** 31 Applications across six AppProjects, standardized `scapegoat.dev/*` labels, 19 consolidated documentation files, zero deprecated applications.
> - **Key structural decisions:** `prod-services` is its own project (not a sub-group of `prod-apps`) because `herold` and `xmpp` are long-running protocol workloads with different operational characteristics; every app is removed from both live cluster and GitOps to prevent accidental re-creation.

---

## Why this structure was needed

Before any changes, the cluster managed 40 ArgoCD Applications. Every single one belonged to the `default` project. No Application carried labels or annotations for categorization. The `gitops/applications/` directory contained 40 flat YAML files with no structural grouping. The `gitops/kustomize/` directory held the corresponding workload packages.

The `default` project in ArgoCD allows everything — all source repos, all destination namespaces, all cluster resources. This permissive default is fine when a cluster has a handful of applications and everyone operates in the same team. It becomes a liability when the platform hosts applications across multiple domains, when backup operators need visibility into database state but not into user-facing application secrets, and when an accidental namespace change could cascade across unrelated services.

The flat documentation told a similar story. There were 20 files in the `docs/` directory. Four of them described the same CI/CD pipeline — source repo → CI build → GHCR → GitOps PR → ArgoCD sync — but each had its own structure, its own cross-references, and its own level of detail. A new operator had no obvious first document to read. Some referenced GitOps paths that no longer existed. Historical examples like `bot-signup` and `smailnail` were still linked in operational docs but no longer deployed.

The core problem was not technical — everything worked. The problem was organizational: the cluster had outgrown its flat structure, and no one could answer basic operational questions at a glance. Which apps are platform infrastructure? Which ones have stateful data? Which ones share a database? Which ones are experimental and safe to delete?

---

## The audit phase

The reorganization started with two parallel investigations: a documentation audit and an ArgoCD application audit. Both used the same methodology — systematic file-by-file inspection, evidence capture, and pattern extraction.

### Documentation audit

Every file in `docs/` was read and cataloged. The goal was to identify what each document covered, where overlaps existed, and what gaps needed filling. The audit revealed that four of the 20 files all described the deployment pipeline:

- **`source-app-deployment-infrastructure-playbook.md`** (934 lines): The most complete pipeline walkthrough. Called itself "the canonical document."
- **`app-packaging-and-gitops-pr-standard.md`** (526 lines): The standard packaging guide. Contained unique content about the "5 categories of GitOps packages."
- **`public-repo-ghcr-argocd-deployment-playbook.md`** (508 lines): The public-repo-to-GitOps-PR pipeline.
- **`coinvault-k3s-deployment-playbook.md`** (644 lines): A worked example for CoinVault, rich with details about private images, Vault integration, and PVC sync-wave traps.

These four documents described the same core workflow but each had its own structure, its own cross-references, and its own level of detail. Other docs had stale content: `grafana-keycloak-access-playbook.md` described a planned state that no longer matched the live cluster. Historical examples were still linked in operational docs but no longer deployed.

### ArgoCD application audit

Every one of the 40 Application manifests was read. The `spec.project` field confirmed that every application used `project: default`. The `metadata.labels` field was empty on every file. The `spec.source` fields revealed which apps used Kustomize, which used Helm, and which used sync-wave annotations.

The Kustomize packages revealed deeper patterns: 22 applications used Vault integration, 6 used database bootstrap patterns, 5 had StatefulSets, and 5 had PVCs. Some apps already used `app.kubernetes.io/part-of` labels at the Kustomize level, but these labels were on the deployed resources, not on the ArgoCD Application itself. This meant the deployment structure was partially visible in the cluster but invisible in the GitOps layer.

---

## The taxonomy design

Before removing anything or touching the cluster, the taxonomy had to be decided. The question was: how should 31+ applications be grouped into ArgoCD projects?

The six-project taxonomy emerged from the evidence:

| Project | Purpose | Apps |
|---------|---------|------|
| `platform-infra` | Core infrastructure that everything depends on | vault, monitoring, keycloak, loki, cert-manager, argocd (12 total with VSO and smoke tests) |
| `data-services` | Stateful data stores with backup jobs | postgres, mysql, redis |
| `prod-apps` | Production user-facing applications | pyxis, coinvault, go-go-host, hair-booking, docs-yolo, retro-obsidian-publish |
| `prod-services` | Long-running production services and protocols | herold, xmpp |
| `demo-apps` | Experimental and showcase apps | goja-kanban, wesen-os, artifacts, codebase-browser, draft-review |
| `static-sites` | Static content hosted on shared Caddy | static-sites-host, dmeta-examples, go-go-os-examples |

The `prod-services` project was the most important decision. Initially, `herold` and `xmpp` would have been placed in `prod-apps` alongside the regular production applications. But both are long-running protocol and service workloads that behave differently from typical user-facing applications. `xmpp` runs as a StatefulSet with persistent identity; `herold` is an XMPP client bridge that maintains continuous connections. Grouping them with normal `prod-apps` would have obscured their operational characteristics.

The taxonomy also guided the documentation work. Four overlapping pipeline documents became two: a canonical reference (`app-deployment-pipeline.md`) and a worked-examples guide (`app-deployment-examples.md`). Historical examples like CoinVault, MySQL IDE, and static sites were preserved in the examples guide with their unique technical details intact. Five stale documentation files were deleted.

---

## AppProject implementation

The first implementation step was to create the six AppProject manifests. This is the safest possible phase because the project manifests define who is allowed to deploy where, but no Application references them yet. Applying them to the cluster creates the projects without affecting any existing Application.

Each AppProject defines:

1. **sourceRepos**: which Git repositories (and Helm chart repos) that project's applications may use. The `platform-infra` project gets three external Helm repos (`helm.releases.hashicorp.com`, `prometheus-community.github.io/helm-charts`, `grafana.github.io/helm-charts`) because Vault, Prometheus, and Loki are deployed as Helm charts from those repos. All other projects use only the internal GitOps repository.

2. **destinations**: which namespaces applications in that project may deploy to. Each project's destination list matches exactly the namespaces used by its assigned applications. This is a hard boundary — ArgoCD will reject any Application in that project that tries to deploy to a namespace not listed here.

3. **clusterResourceWhitelist** and **namespaceResourceWhitelist**: cluster-scoped resources that projects may create. The `platform-infra` project gets the broadest permissions (`*`/`*`) because it deploys ClusterIssuer resources and the cert-manager CRDs that only platform applications manage. All other projects are limited to creating `Namespace` resources, since each application needs to create its own namespace but should not create cluster-scoped resources.

The four Helm applications (`vault`, `vault-secrets-operator`, `monitoring`, `loki`) were handled carefully. Their `source.type` is `helm` rather than `kustomize`, and their source repos are external Helm chart repositories. The `platform-infra` AppProject's `sourceRepos` list includes those external repos, while the other five projects use only the internal GitOps repository.

---

## Application migration

With the project manifests in place, the next step was to update all 31 Application manifests. This was done using a line-preserving script that parsed YAML only for validation but edited the original text to preserve Helm block-scalar readability. The script updated each Application with:

- `spec.project`: changed from `default` to the correct project name.
- Required labels: `app.kubernetes.io/name`, `app.kubernetes.io/part-of`, `app.kubernetes.io/managed-by`.
- Custom labels: `scapegoat.dev/tier`, `scapegoat.dev/source-type`, `scapegoat.dev/has-database`, `scapegoat.dev/has-persistent-storage`, `scapegoat.dev/has-ingress`, `scapegoat.dev/database-type`.
- Annotation: `scapegoat.dev/description` with a one-line purpose description.

The label values were derived from the project taxonomy and the application's deployment characteristics:

- `scapegoat.dev/tier`: one of `platform-infra`, `data-service`, `app`, `service`, `demo`, `static-site`.
- `scapegoat.dev/source-type`: `kustomize` or `helm`.
- `scapegoat.dev/has-database`: `true` or `false`.
- `scapegoat.dev/has-persistent-storage`: `true` or `false`.
- `scapegoat.dev/has-ingress`: `true` or `false`.
- `scapegoat.dev/database-type`: `postgres`, `mysql`, `redis`, `embedded`, or `none`.

After updating, all 31 Application manifests were validated with `kubectl apply --dry-run=client`. A project allowlist check verified that every Application's destination namespace and source repo was permitted by its AppProject.

---

## Live migration

The live migration followed the same order: apply projects first, then applications. This avoids project-not-found or project-violation errors during sync.

```bash
kubectl apply -f gitops/projects/
kubectl apply -f gitops/applications/
```

All 31 Applications remained `Synced`. All were `Healthy` except `codebase-browser`, which was already `Progressing` before this work and did not change. The live project counts:

| Project | Count |
|---------|-------|
| `platform-infra` | 12 |
| `data-services` | 3 |
| `prod-apps` | 6 |
| `prod-services` | 2 |
| `demo-apps` | 5 |
| `static-sites` | 3 |
| `default` | 0 |

The ArgoCD web UI at `argocd.yolo.scapegoat.dev` now shows applications grouped by project instead of in a flat alphabetical list. Label queries work:

```bash
kubectl get applications -n argocd -l scapegoat.dev/tier=app
kubectl get applications -n argocd -l scapegoat.dev/has-database=true
kubectl get applications -n argocd -l scapegoat.dev/source-type=helm
```

---

## Leftover cleanup

Removing an ArgoCD Application prunes the Application's managed resources and namespaces. But some resources are not part of the Application's resource tree and survive deletion. The leftover cleanup phase addressed these cases.

### Kubernetes leftovers

After deleting nine ArgoCD Applications, one live Kubernetes resource remained:

- `Secret/default/pretext-trace-basic-auth-inline`

This secret had labels identifying it as belonging to `pretext-trace` but no ownerReferences, meaning it was likely bootstrap-created outside ArgoCD. It was deleted with:

```bash
kubectl -n default delete secret pretext-trace-basic-auth-inline --wait=true
```

Post-cleanup verification found zero namespaced resources matching any of the removed app names across all namespaces.

### Vault leftovers

The Vault audit found that removed apps still had active metadata, auth roles, and policies:

- **KV metadata leaves** under `kv/apps/bot-signup/`, `kv/apps/discord-ui-showcase/`, `kv/apps/mirotalk-sfu/`, `kv/apps/pretext-trace/`, `kv/apps/smailnail/`, and `kv/ci/github/bot-signup/gitops-pr-token`. These were removed with `vault kv metadata delete` for each exact leaf path.

- **Kubernetes auth roles**: `bot-signup-prod`, `discord-ui-showcase`, `mirotalk-sfu-prod`, `pretext-trace-prod`, `smailnail`, `smailnail-db-bootstrap`.

- **GitHub Actions auth role**: `bot-signup-gitops-pr`.

- **Policies**: `bot-signup-prod`, `discord-ui-showcase`, `gha-bot-signup-gitops-pr`, `mirotalk-sfu-prod`, `pretext-trace-prod`, `smailnail`, `smailnail-db-bootstrap`.

These were all deleted individually. Verification after cleanup found no removed-app KV metadata paths, no removed-app roles, and no removed-app policies.

### Keycloak leftovers

Public OIDC discovery confirmed that two Keycloak realms still existed:

- `https://auth.yolo.scapegoat.dev/realms/smailnail` — issuer returned `https://auth.yolo.scapegoat.dev/realms/smailnail`
- `https://auth.yolo.scapegoat.dev/realms/video` — issuer returned `https://auth.yolo.scapegoat.dev/realms/video`, associated with the removed `mirotalk-sfu` app

Both were deleted using the `kcadm.sh` tool inside the Keycloak pod without printing admin credentials. Post-cleanup public discovery for both realms returns HTTP 404.

### Operator script cleanup

Seven app-specific bootstrap and validation scripts were removed:

- `bootstrap-mirotalk-sfu-runtime-secrets.sh`
- `bootstrap-pretext-trace-basic-auth-secret.sh`
- `bootstrap-pretext-trace-image-pull-secret.sh`
- `bootstrap-smailnail-image-pull-secret.sh`
- `bootstrap-smailnail-runtime-secrets.sh`
- `build-and-import-pretext-explorer-image.sh`
- `validate-pretext-explorer.sh`

These scripts were app-specific entry points for recreating credentials and images for removed applications.

### Documentation cleanup

`README.md` was updated to:
- Replace stale mentions of Pretext, sanitize, and bot-signup with current platform services
- Update the "Start Here" navigation links to point to the consolidated docs
- Update the deploy-new-app examples to reference current apps instead of deleted ones
- Remove deleted app endpoints from the public endpoints list

Historical Vault and Keycloak docs were updated to clarify that the concrete `bot-signup` and `smailnail` objects were decommissioned and should be treated as historical patterns only.

---

## Commit structure

The work was committed in seven focused slices, each changing one category of files:

| Commit | Message | Files |
|--------|---------|-------|
| `100d1f5` | gitops: remove deprecated ArgoCD applications | 86 files (9 Application YAMLs + 9 kustomize directories) |
| `efd0064` | docs: consolidate deployment guides and refresh app inventory | 19 docs files |
| `0f7ce5e` | docs: record ArgoCD cleanup diary | 4 ticket files |
| `5cf8b74` | gitops: add ArgoCD AppProjects | 6 new AppProject manifests |
| `bf83149` | gitops: assign ArgoCD applications to projects | 31 Application YAMLs |
| `89231a7` | cleanup: remove stale deleted-app operator scripts | 7 scripts + README + 2 docs |
| `5e32c03` | docs: record removed-app leftover cleanup | 2 ticket files |

Each commit targets a single domain: GitOps, documentation, ticket bookkeeping, or cleanup. The commits were pushed to `origin/main` after all live changes were verified.

---

## Lessons learned

### On taxonomy design

Grouping applications by operational characteristics — not just by superficial similarity — produces more useful boundaries. The `prod-services` project demonstrates this: `herold` and `xmpp` are production applications, but their operational profile (StatefulSet, continuous connections, protocol-level behavior) is different from typical user-facing apps. A taxonomy that groups by operational profile is more useful for operators than one that groups by superficial similarity.

### On cleanup strategy

Removing deprecated applications requires action on two planes. Deleting only from the live cluster leaves the GitOps tree intact, which means any future `kubectl apply -k gitops/` or ArgoCD resync would recreate the applications. Deleting only from the GitOps tree leaves stale live resources. Both must happen together.

Live resources survive ArgoCD deletion when they are not managed by the Application's resource tree. Namespace-default objects, externally-managed TLS secrets, and bootstrap-created resources are common survivors. Validation should check Applications, namespaces, ingresses, secrets, and ConfigMaps — not just ArgoCD status.

### On Vault credential lifecycle

Vault retains metadata, auth roles, and policies long after the Kubernetes resources that used them are gone. `vault kv metadata delete` removes all versions and metadata for a secret leaf. `vault delete auth/kubernetes/role/` and `vault delete auth/github-actions/role/` remove auth roles. `vault policy delete` removes policies. These need to be run explicitly — there is no automatic cleanup.

### On documentation hygiene

When applications are removed from a cluster, documentation references to them need to be either deleted or explicitly relabeled as historical. Leaving them unmarked creates confusion: an operator reading a doc that mentions `pretext-trace` will assume it is live and try commands that no longer work. Explicit labeling — "historical example" or "decommissioned" — makes the distinction clear.

### On wildcard DNS

Deleted app hostnames continue to resolve to the cluster IP if a wildcard DNS record (`*.yolo.scapegoat.dev`) exists. The correct live-cluster check is ingress and routing, not DNS. The presence of a DNS entry does not mean the app is reachable; it only means the domain resolves to the node's IP.

---

## What remains

Several items from the audit remain open. They were explicitly excluded from this cleanup by request:

- **GHCR packages**: Public container packages for removed apps (`go-go-golems/sanitize`, `go-go-golems/smailnail`, `wesen/pretext`, `wesen/2026-03-30--pretext-wasm-trace-server`, `wesen/2026-05-01--bot-signup`) remain in the registry. Deletion was not requested.
- **Database cleanup**: PostgreSQL and MySQL databases may contain schemas created for removed apps. Read-only access to the database pods failed without explicit admin credentials. Database audit was not requested.

When these are addressed, they should follow the same cleanup pattern: inspect, list, delete exact named resources, verify absence.

---

## Commands reference

All commands below use the K3s kubeconfig from the repository root:

```bash
export KUBECONFIG=$PWD/kubeconfig-k3s-demo-1.tail879302.ts.net.yaml
export VAULT_ADDR=https://vault.yolo.scapegoat.dev
```

### Application project migration

```bash
kubectl apply -f gitops/projects/
kubectl apply -f gitops/applications/

kubectl -n argocd get applications -o json | \
  jq -r '.items[].spec.project' | sort | uniq -c

kubectl get applications -n argocd -l scapegoat.dev/tier=service -o custom-columns='NAME:.metadata.name,PROJECT:.spec.project,TIER:.metadata.labels.scapegoat\.dev/tier,HEALTH:.status.health.status'
```

### Vault cleanup

```bash
vault kv metadata delete kv/apps/bot-signup/prod/image-pull
vault kv metadata delete kv/apps/bot-signup/prod/runtime
vault kv metadata delete kv/apps/pretext-trace/prod/ingress-basic-auth
# ... (all exact KV metadata leaves)

vault delete auth/kubernetes/role/bot-signup-prod
vault delete auth/github-actions/role/bot-signup-gitops-pr
vault policy delete bot-signup-prod
# ... (all roles and policies)
```

### Keycloak cleanup

```bash
# inside the Keycloak pod using existing admin env vars
kubectl -n keycloak exec <keycloak-pod> -- sh -c \
  '/opt/keycloak/bin/kcadm.sh delete realms/smailnail'
kubectl -n keycloak exec <keycloak-pod> -- sh -c \
  '/opt/keycloak/bin/kcadm.sh delete realms/video'
```

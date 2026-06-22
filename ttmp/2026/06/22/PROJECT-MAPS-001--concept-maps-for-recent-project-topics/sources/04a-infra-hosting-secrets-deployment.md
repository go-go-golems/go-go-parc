# 04a — Infra: Hosting Platform, Secrets/Identity, and Application Deployment

**Partition A** of Topic 4 (Infra/auth/deployment/GitOps).
Covers: Hosting platform evolution · Secret and identity plane · Application deployment and hosted environments.
Does NOT cover: DNS/TLS/networking · Backup/resilience · Release trains and publishing (→ Partition B).

---

## Evidence Ledger

| Path | Evidence level | Lines / basis | Cluster | Why it matters |
|---|---|---|---|---|
| `Projects/2026/03/15/PROJ - Coolify Hetzner - Self-Hosted Deployment Platform.md` | read | full file | Hosting platform | Historical origin: Coolify v4 + Traefik + Keycloak baseline |
| `Projects/2026/03/16/PROJ - Keycloak Identity Platform on Coolify.md` | read | full file | Identity plane | First OIDC realm model, DCR failure mode, local/dev realm split |
| `Projects/2026/03/27/PROJ - K3s Migration Program - From Coolify to GitOps Platform.md` | read | lines 1-80 | Hosting platform | Umbrella migration framing, five-phase plan |
| `Projects/2026/03/27/PROJ - Hetzner K3s Platform - Single-Node GitOps Bring-Up.md` | read | full file | Hosting platform | Platform contract: Terraform → cloud-init → Argo CD → Kustomize |
| `Projects/2026/06/06/ARTICLE - Hetzner K3s GitOps Platform Deep Dive.md` | read | full file | Hosting platform | Mature synthesis + install guide; canonical platform model |
| `Projects/2026/06/06/ARGOCD Reorg/ARTICLE - ArgoCD Reorganization - From Flat List to Structured Platform.md` | read | lines 1-80 | GitOps operations | Taxonomy reorg: 40 apps → 6 projects, doc consolidation |
| `Projects/2026/03/25/PROJ - Terraform Infra - Vault Platform Bring-Up, Auth Hardening, and Hair-Booking Handoff.md` | read | full file | Secrets/identity | First Vault on Coolify; KMS auto-unseal, OIDC, AppRole, GitHub SSO |
| `Projects/2026/03/27/PROJ - Vault on K3s - Auth and Secret Delivery Platform.md` | read | full file | Secrets/identity | Vault on K3s; K8s auth, VSO, three auth mounts |
| `Projects/2026/04/26/ARTICLE - Report - Terraform Managed Vault Admin Access Through Keycloak OIDC.md` | read | full file | Secrets/identity | Group-claim pipeline, `exhaustive=false` Terraform pattern |
| `Projects/2026/05/02/ARTICLE - Vault OIDC for GitHub Actions - Secretless CI GitOps.md` | read | full file | Secrets/identity | Core CI/GitOps credential flow; OIDC → Vault → GitOps PR |
| `Projects/2026/05/26/ARTICLE - Vault OIDC for CI/CD Docs Publishing - Designing Short-Lived Package-Scoped Credentials.md` | read | lines 1-80 | Secrets/identity | Package-scoped publish JWT design, offline registry verification |
| `Projects/2026/06/01/ARTICLE - GitHub App Tokens for GitOps PR Automation.md` | read | full file | Secrets/identity | GitHub App replaces PAT for cross-repo GitOps PRs |
| `Projects/2026/03/18/PROJ - Smailnail - Hosted Identity, Terraform, and Claude Fix.md` | read | full file | App deployment | Hosted identity, Terraform-managed Keycloak, DCR fix |
| `Projects/2026/03/27/PROJ - CoinVault on K3s - First Real GitOps App.md` | read | full file | App deployment | First real app migration proving VSO + Argo + MySQL + Keycloak |
| `Projects/2026/04/24/PROJ - Goja Essay - Argo CD Deployment Report.md` | read | lines 1-50 | App deployment | CGO-enabled Go + Vite frontend, SQLite PVC, sync-wave deadlock |
| `Projects/2026/04/26/ARTICLE - Report - Production Discord Bot on Argo CD k3s and Vault.md` | read | lines 1-50 | App deployment | Single-replica worker pattern, no ingress needed |
| `Projects/2026/04/29/ARTICLE - Pyxis - Putting a Glazed Go App into Production with Argo CD.md` | read | lines 1-60 | App deployment | Three-repo model, VSO for PG/image-pull/runtime, migration Job |
| `Projects/2026/06/09/ARTICLE - Static-Sites Deployment - A Three-Contract Model for Shipments.md` | read | full file | App deployment | Reusable deployment contract model for static sites |
| `Projects/2026/05/12/PROJECT REPORT - go-go-host Beta Bringup - From Local MVP to Public Hosted Runtime.md` | read | full file | App deployment | Hosted runtime platform; wildcard TLS, startup restore, agents |
| `Projects/2026/06/19/PROJECT REPORT - go-go-host Lambda Runtime Control Plane - A Technical Deep Dive.md` | read | full file | App deployment | Lambda-style warm pool, additive execution model |

---

## Condensed Per-Arc Summaries

### Arc 1: Hosting platform evolution

- **Coolify era (mid-March, historical)**: Coolify v4 on Hetzner at `hq.scapegoat.dev`; Traefik + Let's Encrypt; Keycloak at `auth.scapegoat.dev`; DOCKER-USER iptables firewall; daily + 6-hour DB backups. Dashboard-driven hosting with some manual host state. Status: **historical**, superseded by K3s.
- **K3s migration (late March, current)**: Terraform creates VM + firewall; cloud-init bootstraps K3s + cert-manager + Argo CD; Argo CD owns steady-state K8s via Kustomize. Critical invariant: `user_data` is first-boot only (`ignore_changes = [user_data]` in Terraform to avoid replacement pressure). Public `80/443`; operator access via Tailscale (not `tailscale up` in cloud-init).
- **Mature platform (June, current)**: Layered control flow: provisioning time (Terraform) → first boot (cloud-init) → day-two (Argo CD). Argo CD taxonomy reorganized from 40 flat apps → 6 projects (prod-apps, prod-services, platform, etc.). Nine deprecated apps removed from both cluster and Git. Docs consolidated from ~20 overlapping files to 19.
- **Migration framing**: Five-phase program: K3s platform → Vault/auth/VSO → first real app (CoinVault) → operator tooling → ongoing migrations without ad-hoc workflows.

### Arc 2: Secret and identity plane

- **Vault on Coolify (March 25, historical)**: Vault at `vault.app.scapegoat.dev`; AWS KMS auto-unseal; Keycloak `infra` realm OIDC for humans with group-gated access (`infra-admins` / `infra-readonly`); AppRole for machines; KV v2 at `kv/`. GitHub SSO into Keycloak but constrained to group membership, not blanket access.
- **Vault on K3s (March 27, current)**: Vault at `vault.yolo.scapegoat.dev`; three auth mounts: `auth/oidc` (humans via Keycloak), `auth/kubernetes` (workloads via SA JWT), `auth/github-actions` (CI via GitHub OIDC JWT). Vault Secrets Operator (VSO) renders Kubernetes `Secret` objects from Vault KV — Git stores intent, Vault stores values.
- **CI/CD secretlessness (May, current)**: GitHub Actions OIDC → Vault JWT auth → short-lived Vault token → repo-specific GitOps PR credential. Roles bound to `repository`, `ref=refs/heads/main`, `event_name=push`, `bound_audiences`. Source repos deleted their `GITOPS_PR_TOKEN` secrets. Pattern generalized into shared `infra-tooling` reusable workflow; Vault resources imported into Terraform ownership.
- **GitHub App tokens (June 1, current)**: Replaced expiring PAT with GitHub App installation tokens. App private key stored in Vault (not as repo secret); workflow mints short-lived installation token per run. Three token sources now supported in `infra-tooling`: `vault` (legacy PAT), `secret` (legacy GH Actions secret), `github_app` (current preferred).
- **Docs publishing credentials (May 26, design)**: Package-scoped publish JWT design — Vault signs short-lived JWT with package/repository/ref claims; registry verifies offline using Vault's public key. Eliminates registry-side token catalog.
- **Group-claim pipeline (April 26, current)**: Vault OIDC login is both auth and authorization. Missing `groups` claim → login fails before token issuance. Fix: Terraform manages Keycloak group membership via `data.keycloak_user` + `keycloak_user_groups` with `exhaustive = false` (additive, not authoritative).

### Arc 3: Application deployment and hosted environments

- **Smailnail (March 18, historical)**: First hosted identity integration. Merged web app + MCP endpoint into one `smailnaild` process sharing `(issuer, subject)` identity model. Keycloak realm managed via Terraform (`envs/local` + `envs/hosted`). Claude DCR failure fixed by widening anonymous DCR allowed-scope set to include `service_account`.
- **CoinVault (March 27, current)**: First real GitOps app on K3s. Proved VSO + Argo + shared MySQL + Keycloak + PVC. Key failure modes: K8s service-link env collision (`COINVAULT_PORT`), profile registry parsing bug (env+CLI merge). Data migration was part of app migration, not a follow-up.
- **Recurring app-to-K3s pattern (April-May, current)**: Goja Essay, Discord Bot, Pyxis, Glazed Help Browser all follow the same contract: source repo → CI → GHCR image → GitOps PR → Argo CD sync. Each exposed different wrinkles: CGO/SQLite PVC sync-wave deadlocks (Goja), single-replica worker with no ingress (Discord), three-repo model with migration Jobs (Pyxis).
- **Static-sites three-contract model (June 9, current)**: Reusable model: (1) source artifact contract (Docker image with `/site/index.html`), (2) GitOps handoff contract (`gitops-targets.json` + `patch_strategy: static-publisher-job`), (3) cluster serving contract (shared Caddy server + per-site publisher Job + atomic symlink swap). Separate Vault credential paths for image-pull vs GitOps PR.
- **go-go-host (May-June, current)**: Public hosted runtime platform at `hosting.yolo.scapegoat.dev`. Four-layer model: identity (Keycloak) → control plane (Postgres) → runtime (Goja supervisor) → delivery (K3s/Traefik/Vault). Beta proven with wildcard TLS, startup runtime restoration, signed-agent deploys (Ed25519). HOST-013 adds Lambda-style warm pool as additive execution model alongside always-on express sites.

---

## Candidate Map Nodes

| Node | Type | Confidence | Status | Notes |
|---|---|---|---|---|
| Coolify Hetzner platform | platform | high | historical | `hq.scapegoat.dev`, superseded by K3s |
| Keycloak Identity Platform | platform | high | current | `auth.scapegoat.dev` → `auth.yolo.scapegoat.dev` |
| Hetzner K3s GitOps Platform | platform | high | current | Single-node K3s, Terraform + cloud-init + Argo CD |
| Terraform infra repo | artifact | high | current | Owns VM, firewall, DNS, Vault/Keycloak resources |
| cloud-init bootstrap | workflow | high | current | First-boot only; `ignore_changes=[user_data]` |
| Argo CD GitOps | platform | high | current | Reconciles Kustomize from GitOps repo |
| Argo CD project taxonomy | concept | high | current | 6 projects: prod-apps, prod-services, platform, etc. |
| Vault Platform (Coolify) | platform | high | historical | `vault.app.scapegoat.dev`, KMS auto-unseal |
| Vault Platform (K3s) | platform | high | current | `vault.yolo.scapegoat.dev`, Raft + KMS |
| Vault Secrets Operator (VSO) | technology | high | current | Renders K8s Secrets from Vault KV |
| Kubernetes auth mount | concept | high | current | `auth/kubernetes` for workload identity |
| Keycloak OIDC mount (Vault) | concept | high | current | `auth/oidc` for human operators |
| GitHub Actions OIDC mount | concept | high | current | `auth/github-actions` JWT auth for CI |
| GitHub App token path | workflow | high | current | Replaces PAT; private key in Vault |
| Package-scoped publish JWT | concept | medium | design | Offline-verified registry authorization |
| Group-claim authorization pipeline | concept | high | current | Keycloak groups → Vault policies |
| Short-lived credentials | concept | high | current | OIDC tokens, Vault tokens, installation tokens |
| Secret intent in Git, values in Vault | concept | high | current | Core invariant of the secret plane |
| Three-contract static sites model | concept | high | current | Source artifact / GitOps handoff / cluster serving |
| Source repo → CI → GitOps PR → Argo CD | workflow | high | current | Standard deployment chain |
| go-go-host runtime platform | platform | high | current | `hosting.yolo.scapegoat.dev`, Goja hosting |
| go-go-host Lambda warm pool | concept | medium | current | Additive execution model (HOST-013) |
| Signed-agent deployment | workflow | high | current | Ed25519 enrollment + nonce/timestamp |
| Startup runtime restoration | concept | high | current | Rebuild in-memory supervisor from DB on restart |
| Keycloak DCR failure | failure-mode | high | historical | Allowed-scope mismatch blocked Claude |
| K8s service-link env collision | failure-mode | high | current | Auto-injected vars clobber app config |
| Argo CD sync-wave deadlock | failure-mode | high | current | PVC health blocks Deployment that would bind it |
| Flat Argo CD taxonomy | failure-mode | high | historical | 40 apps in `default` project, unreviewable |
| Expired PAT credential | failure-mode | high | historical | Triggered GitHub App migration |
| Terraform `exhaustive=false` pattern | concept | high | current | Additive group membership management |
| `ignore_changes=[user_data]` | concept | high | current | Prevents Terraform-driven server replacement |
| Smailnail hosted identity | project | high | historical | First merged web+MCP identity model |
| CoinVault on K3s | project | high | current | First real GitOps app proving full stack |
| Static-sites host (Caddy) | technology | high | current | Shared server, per-site publisher Jobs |
| infra-tooling reusable workflow | artifact | high | current | Shared publish-ghcr-image + open-gitops-pr |

---

## Candidate Map Edges

```
Coolify Hetzner platform --superseded by--> Hetzner K3s GitOps Platform [high] (Projects/2026/03/27/PROJ - K3s Migration Program)
Keycloak Identity Platform --issues OIDC tokens for--> Vault Platform (Coolify) [high] (Projects/2026/03/25/PROJ - Terraform Infra Vault)
Keycloak Identity Platform --issues OIDC tokens for--> Vault Platform (K3s) [high] (Projects/2026/03/27/PROJ - Vault on K3s)
Keycloak Identity Platform --issues OIDC tokens for--> go-go-host runtime platform [high] (Projects/2026/05/12/PROJECT REPORT - go-go-host Beta)
Terraform infra repo --provisions--> Hetzner K3s GitOps Platform [high] (Projects/2026/03/27/PROJ - Hetzner K3s Platform)
Terraform infra repo --defines intended--> Vault Platform (K3s) [high] (Projects/2026/04/26/ARTICLE - Terraform Managed Vault Admin)
Terraform infra repo --manages--> Keycloak Identity Platform [high] (Projects/2026/03/18/PROJ - Smailnail)
cloud-init bootstrap --bootstraps--> Hetzner K3s GitOps Platform [high] (Projects/2026/06/06/ARTICLE - Hetzner K3s GitOps Platform Deep Dive)
cloud-init bootstrap --first-boot only; not day-two--> Argo CD GitOps [high] (Projects/2026/03/27/PROJ - Hetzner K3s Platform)
Argo CD GitOps --reconciles--> Kustomize packages [high] (Projects/2026/06/06/ARTICLE - Hetzner K3s GitOps Platform Deep Dive)
Argo CD project taxonomy --organizes--> Argo CD GitOps [high] (Projects/2026/06/06/ARGOCD Reorg/ARTICLE)
Vault Platform (K3s) --stores values for--> Vault Secrets Operator (VSO) [high] (Projects/2026/03/27/PROJ - Vault on K3s)
VSO --renders--> Kubernetes Secrets [high] (Projects/2026/03/27/PROJ - Vault on K3s)
Kubernetes auth mount --authenticates--> K8s ServiceAccount JWT [high] (Projects/2026/03/27/PROJ - Vault on K3s)
GitHub Actions OIDC mount --authenticates--> GitHub OIDC token [high] (Projects/2026/05/02/ARTICLE - Vault OIDC for GitHub Actions)
GitHub App token path --replaces--> Expired PAT credential [high] (Projects/2026/06/01/ARTICLE - GitHub App Tokens)
GitHub App token path --reads key from--> Vault Platform (K3s) [high] (Projects/2026/06/01/ARTICLE - GitHub App Tokens)
Group-claim authorization pipeline --bridges--> Keycloak Identity Platform and Vault Platform (K3s) [high] (Projects/2026/04/26/ARTICLE - Terraform Managed Vault Admin)
Terraform `exhaustive=false` pattern --manages--> Group-claim authorization pipeline [high] (Projects/2026/04/26/ARTICLE - Terraform Managed Vault Admin)
Source repo → CI → GitOps PR → Argo CD --standardizes--> CoinVault on K3s [high] (Projects/2026/03/27/PROJ - CoinVault on K3s)
Source repo → CI → GitOps PR → Argo CD --standardizes--> Static-sites host (Caddy) [high] (Projects/2026/06/09/ARTICLE - Static-Sites Deployment)
infra-tooling reusable workflow --generalizes--> GitHub Actions OIDC mount [high] (Projects/2026/05/02/ARTICLE - Vault OIDC for GitHub Actions)
Three-contract static sites model --decomposes--> Source repo → CI → GitOps PR → Argo CD [high] (Projects/2026/06/09/ARTICLE - Static-Sites Deployment)
go-go-host runtime platform --depends on--> Vault Platform (K3s) [high] (Projects/2026/05/12/PROJECT REPORT - go-go-host Beta)
go-go-host runtime platform --depends on--> Keycloak Identity Platform [high] (Projects/2026/05/12/PROJECT REPORT - go-go-host Beta)
go-go-host Lambda warm pool --extends--> go-go-host runtime platform [medium] (Projects/2026/06/19/PROJECT REPORT - go-go-host Lambda)
Signed-agent deployment --alternative to--> Keycloak Identity Platform (for CI) [high] (Projects/2026/05/12/PROJECT REPORT - go-go-host Beta)
Startup runtime restoration --reconstructs--> go-go-host runtime platform [high] (Projects/2026/05/12/PROJECT REPORT - go-go-host Beta)
Keycloak DCR failure --caused by--> Keycloak Identity Platform DCR policy [high] (Projects/2026/03/16/PROJ - Keycloak Identity Platform)
K8s service-link env collision --exposed by--> CoinVault on K3s [high] (Projects/2026/03/27/PROJ - CoinVault on K3s)
Argo CD sync-wave deadlock --exposed by--> Goja Essay deployment [high] (Projects/2026/04/24/PROJ - Goja Essay)
Flat Argo CD taxonomy --remediated by--> Argo CD project taxonomy [high] (Projects/2026/06/06/ARGOCD Reorg/ARTICLE)
Secret intent in Git, values in Vault --invariant of--> Vault Platform (K3s) [high] (Projects/2026/03/27/PROJ - Vault on K3s)
Package-scoped publish JWT --extends--> GitHub Actions OIDC mount [medium] (Projects/2026/05/26/ARTICLE - Vault OIDC for CI/CD)
```

---

## Cross-Links to Other Topic Slices

- **Topic 2 (JavaScript/Goja/xgoja)**: go-go-host is a Goja hosting platform — the runtime supervisor, Lambda warm pool, and `LambdaRuntime` are Goja VMs. The `goja-repl essay` deployment (Topic 2) ships through the same K3s GitOps contract documented here. xgoja buildspec/provider model is the conceptual ancestor of go-go-host capability bundles.
- **Topic 5 (AI agents/observability)**: Signed-agent deployment in go-go-host uses Ed25519 enrollment tokens, nonce/timestamp replay protection, and deploy-run audit — directly relevant to agent enrollment credential threat models. Codex/CI readiness gates in release tooling (Partition B) consume the same Vault OIDC path. go-minitrace transcript artifacts could be deployed through the static-sites three-contract model.
- **Topic 6 (Data/RAG/search)**: `rag-evaluation-storybook` static site is the live proof case for the three-contract deployment model. SQLite is the per-site runtime store in go-go-host and the per-site data store in CoinVault — same pattern as SQLite canonical store in RAG/OCR systems. Buf/protobuf schema publishing (Partition B) uses Vault-backed CI credentials from this slice's OIDC path.
- **Topic 7 (Web UI/apps/media)**: Static-sites deployment serves Storybook, Goja Site, Retro Obsidian Publish, and other web products. The Caddy static host + publisher Job pattern is the delivery substrate for many Topic 7 apps. Smailnail's merged web+MCP identity model is a pattern for browser+API unified auth.
- **Topic 1 (Hardware)**: Backup/power-outage homelab context (Partition B) touches the same Vault credential storage plane. Tailscale operator access pattern originates here but is relevant to hardware device networking. Limited direct overlap otherwise.
- **Topic 4 Partition B (DNS/TLS, Backup, Release trains)**: DNS/TLS is a prerequisite for every deployment documented here (cert-manager, Traefik, wildcard certs). Backup follow-ups (Vault snapshots, audit logs) were opened during the Vault bring-up. Release train tooling (`ggg`) consumes the same Vault OIDC path for CI credentials. The GitHub App token path replaces the same Vault-stored PAT that release train PRs depended on.

---

## Start Here

1. **`Projects/2026/06/06/ARTICLE - Hetzner K3s GitOps Platform Deep Dive.md`** — the mature synthesis that defines the platform contract, maps the repository, and explains the Terraform → cloud-init → Argo CD layering. This is the canonical file for understanding the hosting platform.
2. **`Projects/2026/03/27/PROJ - Vault on K3s - Auth and Secret Delivery Platform.md`** — defines the three-mount secret architecture (`oidc` / `kubernetes` / `github-actions`) and the VSO contract ("intent in Git, values in Vault"). Short, precise, and the reference point for all later secret work.

---

## Open Questions

1. Is the GitHub App token path now the preferred GitOps PR automation method for ALL repos, or do some still use the Vault-stored PAT (`gitops_pr_token_source: vault`)?
2. The docs publishing JWT design (May 26) was described as a design article — was it implemented, or is it still aspirational? The source report lists it under "Secret and identity plane" but its implementation status is unclear.
3. Should go-go-host's signed-agent model be considered the long-term CI deployment identity, or will OAuth Device Flow replace it for human CLI use while agents keep Ed25519?
4. The Argo CD reorg removed 9 deprecated apps — which of the apps in this partition's deployment arc are still current vs removed? The June reorg should be used to validate current vs historical status.
5. Is `vault.app.scapegoat.dev` (Coolify) still running, or has it been fully decommissioned in favor of `vault.yolo.scapegoat.dev` (K3s)?

# Code Context

## Files Retrieved
1. `Projects/2026/03/15/PROJ - Coolify Hetzner - Self-Hosted Deployment Platform.md` (lines 1-70) - first hosting platform, Coolify/Traefik/Keycloak/backup baseline.
2. `Projects/2026/03/16/PROJ - Keycloak Identity Platform on Coolify.md` (lines 1-70) - central Keycloak/OIDC service before K3s migration.
3. `Projects/2026/03/18/PROJ - Smailnail - Hosted Identity, Terraform, and Claude Fix.md` (lines 1-70) - hosted app identity integration, Terraform-managed realm, Claude/DCR failure.
4. `Projects/2026/03/25/PROJ - Terraform Infra - Vault Platform Bring-Up, Auth Hardening, and Hair-Booking Handoff.md` (lines 1-70) - first shared Vault platform on Coolify with Keycloak OIDC/AppRole.
5. `Projects/2026/03/27/PROJ - Hetzner K3s Platform - Single-Node GitOps Bring-Up.md` (lines 1-80) - core K3s/Terraform/cloud-init/Argo CD platform contract.
6. `Projects/2026/03/27/PROJ - Vault on K3s - Auth and Secret Delivery Platform.md` (lines 1-80) - Vault moved into K3s with Kubernetes auth, Keycloak OIDC, VSO.
7. `Projects/2026/05/02/ARTICLE - Vault OIDC for GitHub Actions - Secretless CI GitOps.md` (lines 1-80) - source repo CI obtains short-lived Vault tokens and opens GitOps PRs.
8. `Projects/2026/05/03/ARTICLE - Debugging a k3s Post-Reboot Outage.md` (lines 1-70) - outage case study across Traefik, HelmChartConfig, cloud-controller-manager, DNS/Tailscale.
9. `Projects/2026/05/26/ARTICLE - Managing Go-Go-Golems Release Trains.md` (lines 1-80) - multi-repo release ordering and validation contract.
10. `Projects/2026/05/27/ARTICLE - NPM Publishing for Go Go Golems Packages with Vault OIDC.md` (lines 1-80) - historical Vault-backed package publishing and npm permission failure mode.
11. `Projects/2026/06/06/ARTICLE - Hetzner K3s GitOps Platform Deep Dive.md` (lines 1-80) - mature install/operating guide for the platform.
12. `Projects/2026/06/06/ARGOCD Reorg/ARTICLE - ArgoCD Reorganization - From Flat List to Structured Platform.md` (lines 1-80) - Argo CD taxonomy, cleanup, app/project reorganization.
13. `Projects/2026/06/09/ARTICLE - Static-Sites Deployment - A Three-Contract Model for Shipments.md` (lines 1-80) - reusable deployment-contract model for static sites on K3s.
14. `Projects/2026/06/09/ARTICLE - Crib Backup - From Design to Operational Restic Baseline.md` (lines 1-80) - restic/TrueNAS backup baseline and NFS/local fallback hazard.
15. `Projects/2026/06/17/PROJECT REPORT - Workshops Wildcard DNS and TLS - DigitalOcean Delegation Deep Dive.md` (lines 1-80) - DNS delegation and cert-manager DNS-01 wildcard TLS rollout.

## Scope / Search Method

Scope was Markdown under `Projects/2026/{03,04,05,06}/`. I searched paths and file contents for infra/auth/deployment terms: `k3s`, `argocd`, `terraform`, `vault`, `keycloak`, `oidc`, `oauth`, `coolify`, `github app`, `dns`, `tls`, `backup`, `deployment`, `outage`, `release train`, `publishing`, `hosted`, plus related terms (`helm`, `cert-manager`, `ingress`, `cloudflare`, `letsencrypt`, `tailscale`, `container`, `docker`, `kubernetes`, `gitops`). The corpus count from shell was 569 Markdown files; keyword document hits included deployment 127, Vault 117, hosted 79, TLS 61, OIDC 56, K3s 53, Argo CD 45, Keycloak 43, DNS 41, Terraform 40, publishing 41, backup 36, Coolify 14, outage 9, release train 7, GitHub App 5.

## Projects / Reports Found

### Hosting platform evolution
- `Projects/2026/03/15/PROJ - Coolify Hetzner - Self-Hosted Deployment Platform.md`: Coolify v4 on Hetzner at `hq.scapegoat.dev`; Traefik + Let's Encrypt; Keycloak at `auth.scapegoat.dev`; firewall and daily backups.
- `Projects/2026/03/16/PROJ - Keycloak Identity Platform on Coolify.md`: Keycloak 26.1, OIDC realms, production HTTPS via Traefik, PostgreSQL backups.
- `Projects/2026/03/27/PROJ - K3s Migration Program - From Coolify to GitOps Platform.md` and `Projects/2026/03/27/PROJ - Hetzner K3s Platform - Single-Node GitOps Bring-Up.md`: migration from Coolify/manual host to Terraform + cloud-init + K3s + Argo CD.
- `Projects/2026/06/06/ARTICLE - Hetzner K3s GitOps Platform Deep Dive.md`: mature platform guide and repo map.

### Secret and identity plane
- `Projects/2026/03/25/PROJ - Terraform Infra - Vault Platform Bring-Up, Auth Hardening, and Hair-Booking Handoff.md`: Vault deployed on Coolify host, initialized, AWS KMS auto-unseal, Keycloak OIDC, GitHub SSO, AppRole, KV v2.
- `Projects/2026/03/27/PROJ - Vault on K3s - Auth and Secret Delivery Platform.md`: Vault server in K3s under Argo CD; Kubernetes auth, Keycloak OIDC, Vault Secrets Operator.
- `Projects/2026/04/26/ARTICLE - Report - Terraform Managed Vault Admin Access Through Keycloak OIDC.md`: Terraform-managed OIDC admin access.
- `Projects/2026/05/02/ARTICLE - Vault OIDC for GitHub Actions - Secretless CI GitOps.md`: Vault JWT auth for GitHub Actions, repo-bound roles, short-lived tokens for GitOps PR credentials.
- `Projects/2026/05/26/ARTICLE - Vault OIDC for CI/CD Docs Publishing - Designing Short-Lived Package-Scoped Credentials.md` and `Projects/2026/05/27/ARTICLE - NPM Publishing for Go Go Golems Packages with Vault OIDC.md`: CI publishing credentials through Vault OIDC.
- `Projects/2026/06/01/ARTICLE - GitHub App Tokens for GitOps PR Automation.md`: GitHub App token direction for PR automation.
- `Projects/2026/06/01/ARTICLE - Trusted npm Publishing for Go Go Golems React Packages.md`: later tokenless npm publishing replacement.
- `Projects/2026/06/02/ARTICLE - Protobuf Schema Publishing - Buf Registry and Vault-Backed CI.md`: package/schema publishing with Vault-backed CI.

### Application deployment and hosted environments
- `Projects/2026/03/18/PROJ - Smailnail - Hosted Identity, Terraform, and Claude Fix.md`: hosted Smailnail backend+SPA, OIDC browser/MCP auth, Keycloak Terraform scaffold, Claude dynamic client registration failure.
- `Projects/2026/03/25/PROJ - Hair Booking - MVP Buildout, Hosted Auth, Vault, and Production Fixes.md`: app handoff into hosted auth/Vault/production fix pattern.
- `Projects/2026/03/27/PROJ - CoinVault on K3s - First Real GitOps App.md`: first real GitOps app on K3s.
- `Projects/2026/03/29/PROJ - Serve Artifacts - Deploying to K3s with GitOps.md`: artifact serving deployment.
- `Projects/2026/04/24/PROJ - Goja Essay - Argo CD Deployment Report.md`, `Projects/2026/04/26/ARTICLE - Report - Production Discord Bot on Argo CD k3s and Vault.md`, `Projects/2026/04/29/ARTICLE - Pyxis - Putting a Glazed Go App into Production with Argo CD.md`, `Projects/2026/05/02/ARTICLE - Deploying Glazed Help Browser to Argo CD - Production Deep Dive.md`: recurring app-to-K3s deployment reports.
- `Projects/2026/06/09/ARTICLE - Static-Sites Deployment - A Three-Contract Model for Shipments.md`: reusable source artifact/GitOps handoff/cluster serving contract.
- `Projects/2026/06/19/PROJECT REPORT - go-go-host Lambda Runtime Control Plane - A Technical Deep Dive.md` and `Projects/2026/05/12/PROJECT REPORT - go-go-host Beta Bringup - From Local MVP to Public Hosted Runtime.md`: hosted runtime/control-plane thread.

### DNS / TLS / networking
- `Projects/2026/05/03/ARTICLE - Debugging a k3s Post-Reboot Outage.md`: crib K3s post-reboot ingress outage; Traefik, HelmChart, cloud-controller-manager, Tailscale/DNS.
- `Projects/2026/05/05/ARTICLE - Hetzner k3s Resize Postmortem - Capacity, Reboot, and Recovery.md`: capacity/reboot recovery.
- `Projects/2026/05/05/ARTICLE - Grafana Keycloak Login on Hetzner k3s.md`: Keycloak login for Grafana.
- `Projects/2026/05/10/ARTICLE - XMPP on K3s - Prosody Argo CD Terraform Firewall Deep Dive.md`: protocol service, firewall, Terraform, Argo CD.
- `Projects/2026/06/06/ARTICLE - Herold on K3s - HTTPS-Only MVP Deployment Deep Dive.md`: HTTPS-only deployment.
- `Projects/2026/06/17/PROJECT REPORT - Workshops Wildcard DNS and TLS - DigitalOcean Delegation Deep Dive.md`: delegated subdomain, Terraform DNS, cert-manager ACME DNS-01, wildcard cert.

### Backup / resilience
- `Projects/2026/03/15/PROJ - Coolify Hetzner - Self-Hosted Deployment Platform.md`: daily platform backups and 6-hour database backups, with S3 offsite backup deferred.
- `Projects/2026/03/25/PROJ - Terraform Infra - Vault Platform Bring-Up, Auth Hardening, and Hair-Booking Handoff.md`: Vault snapshot/offsite and audit logging follow-ups.
- `Projects/2026/05/03/ARTICLE - Postmortem - Jellyfin TrueNAS NFS Power Outage.md`: storage availability/outage thread.
- `Projects/2026/06/06/ARTICLE - Backup Architecture - TrueNAS with Vault Credentials.md` and `Projects/2026/06/06/ARTICLE - TrueNAS Backup with Vault - A Systems Integration Case Study.md`: backup architecture with Vault-stored credentials.
- `Projects/2026/06/09/ARTICLE - Crib Backup - From Design to Operational Restic Baseline.md`: operational restic baseline, restore test, SFTP-only path, systemd user timer.

### Release trains and publishing
- `Projects/2026/05/08/ARTICLE - Separating Dagger Build Steps from Split GoReleaser Pipelines.md`: release/build pipeline separation.
- `Projects/2026/05/11/ARTICLE - go-go-os Frontend npm Packages - Publishing and Standalone Consumption.md`: frontend package shape and publishing.
- `Projects/2026/05/26/ARTICLE - Managing Go-Go-Golems Release Trains.md`: dependency-ordered multi-repo releases, `GOWORK=off`, CI/Codex gates.
- `Projects/2026/05/27/ARTICLE - ggg - Codex-Aware Release Tooling for Go-Go-Golems.md` and `Projects/2026/05/27/ARTICLE - ggg Rollout Automation - Real-World Testing and Implementation.md`: release automation tooling.
- `Projects/2026/05/28/ARTICLE - INFRA-004 Release Train Machinery - Dashboard, PR Workflow, and Rollout Control.md`: release train dashboard/control.
- `Projects/2026/06/01/ARTICLE - Trusted npm Publishing for Go Go Golems React Packages.md`: tokenless npm Trusted Publishing.
- `Projects/2026/06/02/ARTICLE - Protobuf Schema Publishing - Buf Registry and Vault-Backed CI.md`: Buf registry/publishing.

## Key Code

No source code was modified or deeply inspected; this was a corpus/report scan. Critical snippets from the reports:

- Platform contract, `Projects/2026/03/27/PROJ - Hetzner K3s Platform - Single-Node GitOps Bring-Up.md` lines 17-39: Terraform creates machine, cloud-init bootstraps K3s, Argo CD owns steady-state Kubernetes state; failure boundaries are Hetzner/Terraform/bootstrap/Kubernetes/DNS/TLS/GitOps.
- Secret contract, `Projects/2026/03/27/PROJ - Vault on K3s - Auth and Secret Delivery Platform.md` lines 17-41: `humans -> Keycloak OIDC -> Vault`, `workloads -> Kubernetes auth -> Vault`, `apps -> Vault Secrets Operator -> Kubernetes Secret`.
- GitHub Actions OIDC flow, `Projects/2026/05/02/ARTICLE - Vault OIDC for GitHub Actions - Secretless CI GitOps.md` lines 17-80: GitHub-issued OIDC token -> Vault JWT auth -> short-lived Vault token -> repo-specific GitOps PR credential -> PR -> Argo CD reconciliation.
- Mature platform model, `Projects/2026/06/06/ARTICLE - Hetzner K3s GitOps Platform Deep Dive.md` lines 18-57: Terraform/provisioning time, cloud-init/first boot, Argo CD/day-two operations.
- Static site deployment contracts, `Projects/2026/06/09/ARTICLE - Static-Sites Deployment - A Three-Contract Model for Shipments.md` lines 13-58: source artifact contract, GitOps handoff contract, cluster serving contract.
- DNS/TLS split, `Projects/2026/06/17/PROJECT REPORT - Workshops Wildcard DNS and TLS - DigitalOcean Delegation Deep Dive.md` lines 31-48: stable visitor DNS via Terraform vs temporary ACME TXT records via cert-manager.

## Architecture

The infra/auth/deployment slice has a clear temporal arc:

1. **Coolify era (mid-March)**: Hetzner host with Coolify, Traefik/Let's Encrypt, Keycloak, PostgreSQL backups. This is fast, dashboard-driven hosting with some manual host state.
2. **Terraform/Vault hardening (late March)**: shared Terraform repo and Vault platform; Keycloak OIDC for humans, AppRole/machine auth, KV layout, KMS auto-unseal, explicit follow-up tickets for backup/audit.
3. **K3s/GitOps era (late March onward)**: single-node Hetzner K3s with Terraform provisioning, cloud-init bootstrap, Argo CD/Kustomize desired state, cert-manager/Traefik public ingress, Vault/VSO secret delivery.
4. **CI/CD secretlessness (May-June)**: GitHub Actions OIDC and/or GitHub App tokens replace long-lived repo secrets for GitOps PR automation and publishing; npm eventually moves to Trusted Publishing.
5. **Operational maturity (May-June)**: outage postmortems, Argo CD taxonomy, static-site contracts, DNS/TLS delegation, backup baselines, release train tooling.

Data/control flow patterns recur:

- **Source repo -> CI -> image/package -> GitOps PR -> Argo CD -> cluster**.
- **Human -> Keycloak OIDC -> Vault/operator tools**.
- **Workload -> Kubernetes auth/VSO -> Kubernetes Secret**.
- **GitHub Actions -> OIDC/JWT -> Vault -> scoped credential -> GitOps or registry operation**.
- **Terraform owns durable infrastructure/DNS; cert-manager owns ephemeral ACME challenge DNS; Argo CD owns Kubernetes desired state**.

## Clusters / Subclusters

1. **Platform foundations**
   - Hetzner VM, Proxmox/crib VM, single-node K3s, Terraform, cloud-init, firewall, Tailscale.
2. **GitOps operations**
   - Argo CD Applications, Kustomize packages, sync waves, app taxonomy, cleanup, docs consolidation.
3. **Identity and auth**
   - Keycloak realms/clients, OIDC/OAuth/PKCE/device flow, JWT validation, dynamic client registration pitfalls, Grafana login, xgoja auth host.
4. **Secrets**
   - Vault server, KMS auto-unseal, Raft, KV v2, Kubernetes auth, AppRole, Vault Secrets Operator, Vault OIDC/JWT auth for CI.
5. **Deployment patterns**
   - Web apps, static sites, protocol services (XMPP/WebRTC), public hosted runtime, GitOps PR handoffs, immutable images.
6. **DNS/TLS/networking**
   - DigitalOcean DNS, Netlify delegation, cert-manager, ACME DNS-01, Traefik ingress, Caddy static host, Tailscale overlay, hostPorts vs DNAT.
7. **Resilience and backup**
   - Coolify backups, Vault snapshots/audit logs, TrueNAS/restic, power outage/NFS hazards, restore tests.
8. **Release and publishing**
   - Go module release trains, GoReleaser/Dagger boundaries, npm publishing, Trusted Publishing, Buf schema publishing, Codex/CI readiness gates.

## Recurring Concepts / Technologies / Failure Modes

### Recurring concepts
- **Explicit ownership boundaries**: each system must own one layer and not perform the next layer's job.
- **Contracts over scripts**: source artifact contract, GitOps handoff contract, cluster serving contract; release train invariant; auth/secret delivery contract.
- **Short-lived credentials**: OIDC tokens, Vault-issued tokens, GitHub App installation tokens, npm Trusted Publishing.
- **Day-two operations**: documentation, taxonomy, app cleanup, backups, monitoring, validation commands.
- **Operator-readable systems**: reports emphasize which layer to debug first and what symptom maps to what control plane.

### Technologies
K3s, Kubernetes, Argo CD, Kustomize, Helm/HelmChartConfig, Traefik, cert-manager, Let's Encrypt/ACME DNS-01, Terraform, cloud-init, Hetzner, DigitalOcean DNS, Netlify/NS1 delegation, Tailscale/WireGuard, Vault, AWS KMS auto-unseal, Vault Secrets Operator, Keycloak, OIDC/OAuth/PKCE/device flow, GitHub Actions OIDC, GitHub Apps, GHCR, npm Trusted Publishing, Buf Registry, restic, TrueNAS, SFTP, Proxmox, Coolify, Docker/Caddy.

### Failure modes
- Manual/Coolify host state drifts away from reproducible platform state.
- Terraform state drift from uncommitted DNS applies (`Projects/2026/05/02/ARTICLE - Incident Deep Dive - Terraform State Drift from an Uncommitted Crib DNS Apply.md`).
- K3s post-reboot outage: Traefik disabled, deleted HelmChartConfig, false health through DNAT, CCM RBAC race.
- Capacity/reboot recovery on Hetzner K3s.
- Keycloak dynamic client registration allowed-scope mismatch for Claude.
- npm publish scope/token permission failure despite Vault OIDC retrieval working.
- Static site first `main` workflow startup failure requiring manual publication through same contracts.
- NFS/local directory fallback after TrueNAS power outage; avoided in backup design by SFTP-only transport.
- Flat Argo CD app/project structure becoming unreviewable as app count grows.

## Candidate Concept-Map Nodes and Edges

### Nodes
- Coolify Hetzner
- Keycloak Identity Platform
- Smailnail Hosted Auth
- Terraform Infra Repo
- Vault Platform
- Hetzner K3s Platform
- Argo CD GitOps
- Vault on K3s
- Vault Secrets Operator
- GitHub Actions OIDC
- GitHub App Tokens
- Source Repository
- GitOps Repository
- GHCR Image
- Argo CD Application
- cert-manager
- DigitalOcean DNS
- Netlify Delegation
- Traefik Ingress
- Static Sites Host / Caddy
- TrueNAS Backup Target
- Restic Baseline
- Release Train Tooling (`ggg`, infra-tooling)
- npm Trusted Publishing
- Buf Schema Publishing

### Edges
- Coolify Hetzner **precedes / is partly replaced by** Hetzner K3s Platform.
- Keycloak Identity Platform **issues OIDC tokens for** Smailnail, Vault human operators, Grafana, go-go-host/xgoja auth.
- Terraform **provisions** Hetzner VM/firewall/DNS and **defines intended** Vault/Keycloak/DNS resources.
- cloud-init **bootstraps** K3s and initial Argo CD.
- Argo CD **reconciles** Kustomize/Helm desired state from GitOps repository.
- Vault **stores/seals/governs** app secrets, GitOps PR credentials, publishing credentials, backup provisioning credentials.
- Kubernetes auth/VSO **delivers** Vault secrets to workloads.
- GitHub Actions OIDC **authenticates to** Vault and **reads** repo-scoped GitOps/publishing credentials.
- GitHub App Tokens **alternative to / improves** PAT-style GitOps PR credentials.
- Source repo CI **publishes** GHCR image and **opens** GitOps PR.
- GitOps PR **updates** image pin / static publisher job / manifests.
- cert-manager **creates** ACME TXT records in DigitalOcean DNS and **writes** TLS secrets.
- Traefik **terminates TLS / routes** to services or static Caddy host.
- Restic **backs up** laptop to TrueNAS over SFTP; Vault **stores** provisioning credential but routine backups **do not depend on** Vault.
- Release train tooling **orders** PR merge/tag/publish across dependent Go repos.
- npm Trusted Publishing **replaces** Vault-backed npm token workflow for public packages.

## Overlaps With Other Topic Slices

- **Agent 2 / JavaScript runtimes**: go-go-goja/xgoja auth hosts, generated host auth, Durable Objects, Lambda runtime control plane, hosted xgoja Keycloak deployment.
- **Agent 5 / AI agents / observability**: Codex release review gates, go-minitrace transcript-driven operational docs, agent enrollment credential threat model, Pi/Dagger service lifecycle debugging.
- **Agent 6 / data/RAG/search**: RAG evaluation Storybook static deployment, document co-read, Buf/protobuf publishing, SQLite/browser apps shipped through same deployment patterns.
- **Agent 7 / web UI/apps/media**: static sites, Goja Site, Go-Go Parc website, Glazed Help Browser, Retro Obsidian Publish, WebRTC/MiroTalk, Jellyfin outage.
- **Agent 1 / hardware**: backup/power-outage homelab context touches device/media infrastructure; otherwise limited.

## Start Here

Open `Projects/2026/06/06/ARTICLE - Hetzner K3s GitOps Platform Deep Dive.md` first. It is the mature synthesis that names the platform layers, maps the repository, and explains how Terraform, cloud-init, Argo CD, Vault, DNS, and CI boundaries fit together. Then read `Projects/2026/03/27/PROJ - Hetzner K3s Platform - Single-Node GitOps Bring-Up.md` for origin context and `Projects/2026/05/02/ARTICLE - Vault OIDC for GitHub Actions - Secretless CI GitOps.md` for the core CI/GitOps credential flow.

## Open Questions

1. Which report should be considered canonical for the current deployment pipeline after the Argo CD documentation reorg: the June deep dive, the source-app playbook in the external repo, or the static-sites contract article?
2. Is the GitHub App token approach now the preferred GitOps PR automation path over Vault-stored PR tokens for all repos?
3. Which Vault deployment is authoritative historically/currently: Coolify-hosted `vault.app.scapegoat.dev` or K3s-hosted `vault.yolo.scapegoat.dev`? Reports show the migration arc, but a map should mark old vs current.
4. Are backups for Vault/K3s platform state now implemented, or still partly follow-up? The backup thread is strong for crib/restic, less clear for production K3s state.
5. Should concept maps distinguish `scapegoat.dev`, `yolo.scapegoat.dev`, `crib.scapegoat.dev`, and external delegated domains as separate environment/namespace nodes?
6. How many hosted apps are current vs historical/deprecated after the Argo CD cleanup? The June Argo CD reorg should be used to avoid mapping removed apps as live.

## Report-Format Lessons

- A useful infra report should be organized by **control-plane boundary** rather than by month only: provisioning, bootstrap, GitOps, secrets, identity, DNS/TLS, CI/CD, backup.
- Include **status labels** per project: historical, current, migrated, deprecated, or active. This prevents old Coolify/Vault patterns from being mistaken as current.
- Concept maps should show **flows and ownership edges**, not only technologies. The recurring insight is “who owns this state, and how does the next system consume it?”
- Capture **failure modes as first-class nodes**. Outages and publishing failures are often the clearest evidence for hidden dependencies.
- Keep a small **canonical-read order** because many reports overlap and later reports supersede earlier ones.

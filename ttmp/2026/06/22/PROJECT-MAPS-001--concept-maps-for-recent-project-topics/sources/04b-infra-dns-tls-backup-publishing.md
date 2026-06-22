# 04b — Infra: DNS/TLS/Networking, Backup/Resilience, and Release Trains/Publishing

**Partition B** of Topic 4 (Infra/auth/deployment/GitOps).
Covers: DNS / TLS / networking · Backup / resilience · Release trains and publishing.
Does NOT cover: Hosting platform evolution · Secret and identity plane · Application deployment and hosted environments (→ Partition A, `04a-infra-hosting-secrets-deployment.md`).

---

## Evidence Ledger

| Path | Evidence level | Lines / basis | Cluster | Why it matters |
|---|---|---|---|---|
| `Projects/2026/06/17/PROJECT REPORT - Workshops Wildcard DNS and TLS - DigitalOcean Delegation Deep Dive.md` | read | full file | DNS/TLS | Canonical DNS delegation + cert-manager DNS-01 contract; two-control-loop model |
| `Projects/2026/05/03/ARTICLE - Debugging a k3s Post-Reboot Outage.md` | read | full file | DNS/TLS | Crib K3s post-reboot outage: Traefik missing, DNAT mask, CCM RBAC race, Tailscale ingress model |
| `Projects/2026/05/05/ARTICLE - Hetzner k3s Resize Postmortem - Capacity, Reboot, and Recovery.md` | read | full file | DNS/TLS | Scheduler request-fit failure, Terraform resize hazard, post-reboot Argo/Keycloak startup races |
| `Projects/2026/05/05/ARTICLE - Grafana Keycloak Login on Hetzner k3s.md` | read | full file | DNS/TLS | Grafana Generic OAuth via Keycloak; VSO for client secret; cert-manager Ingress |
| `Projects/2026/05/10/ARTICLE - XMPP on K3s - Prosody Argo CD Terraform Firewall Deep Dive.md` | read | full file | DNS/TLS | Non-HTTP protocol deployment: hostPort + firewall + SRV DNS; no-federation policy |
| `Projects/2026/06/06/ARTICLE - Herold on K3s - HTTPS-Only MVP Deployment Deep Dive.md` | read | full file | DNS/TLS | HTTPS-only MVP deployment: image architecture, PVC sync-wave deadlock, Traefik TLS routing, VSO secret shape |
| `Projects/2026/05/03/ARTICLE - Postmortem - Jellyfin TrueNAS NFS Power Outage.md` | read | full file | Backup/resilience | NFS silent failure: empty local dir masquerading as mount; Proxmox boot ordering |
| `Projects/2026/06/06/ARTICLE - Backup Architecture - TrueNAS with Vault Credentials.md` | read | full file | Backup/resilience | Design article: SFTP-only transport, Vault for provisioning only, restic tool selection |
| `Projects/2026/06/06/ARTICLE - TrueNAS Backup with Vault - A Systems Integration Case Study.md` | read | full file | Backup/resilience | Implementation case study: backup-f user creation, SFTP debugging, credential migration |
| `Projects/2026/06/09/ARTICLE - Crib Backup - From Design to Operational Restic Baseline.md` | read | full file | Backup/resilience | Operational baseline: clean snapshot, restore test, user-level timer, excludes as architecture |
| `Projects/2026/03/15/PROJ - Coolify Hetzner - Self-Hosted Deployment Platform.md` | read | lines 40-100 (backup sections) | Backup/resilience | Historical backup baseline: daily platform + 6-hour DB backups, S3 offsite deferred |
| `Projects/2026/03/25/PROJ - Terraform Infra - Vault Platform Bring-Up, Auth Hardening, and Hair-Booking Handoff.md` | read | lines 50-90 (backup sections) | Backup/resilience | Vault snapshot/offsite and audit logging as tracked follow-up tickets (TF-007, TF-009) |
| `Projects/2026/05/26/ARTICLE - Managing Go-Go-Golems Release Trains.md` | read | full file | Release/publishing | Canonical release train contract: dependency order, GOWORK=off, CI+Codex gates |
| `Projects/2026/05/27/ARTICLE - ggg - Codex-Aware Release Tooling for Go-Go-Golems.md` | read | full file | Release/publishing | `ggg` CLI: PR readiness state machine, Codex signal model, release tagging guardrails |
| `Projects/2026/05/27/ARTICLE - ggg Rollout Automation - Real-World Testing and Implementation.md` | read | lines 1-80 | Release/publishing | `ggg rollout` layer: inventory, plan, validate, branch, push-prs, status |
| `Projects/2026/05/28/ARTICLE - INFRA-004 Release Train Machinery - Dashboard, PR Workflow, and Rollout Control.md` | read | full file | Release/publishing | SQLite tracker + dashboard; `no_runs` terminal success; post-merge main verification |
| `Projects/2026/05/08/ARTICLE - Separating Dagger Build Steps from Split GoReleaser Pipelines.md` | read | full file | Release/publishing | Dagger+GoReleaser split-build: macOS no Docker, SKIP_DAGGER pattern, artifact sharing |
| `Projects/2026/05/11/ARTICLE - go-go-os Frontend npm Packages - Publishing and Standalone Consumption.md` | read | lines 1-60 | Release/publishing | npm package family: `@go-go-golems/*` scope, standalone consumer, trusted publishing |
| `Projects/2026/06/01/ARTICLE - Trusted npm Publishing for Go Go Golems React Packages.md` | read | lines 1-80 | Release/publishing | npm Trusted Publishing: tokenless OIDC, package bootstrap sequence, token lockdown |
| `Projects/2026/06/02/ARTICLE - Protobuf Schema Publishing - Buf Registry and Vault-Backed CI.md` | read | lines 1-80 | Release/publishing | Buf Schema Registry: `buf.build/go-go-golems/pinocchio-chatapp`, Vault-backed BSR token, tag-gated CI |

---

## Condensed Per-Arc Summaries

### Arc 1: DNS / TLS / networking

- **Two-control-loop DNS model** (Workshops report): Terraform manages stable A records; cert-manager manages temporary ACME TXT records. Both operate on the same DigitalOcean delegated zone but are independent control loops. Subdomain delegation (not whole-domain transfer) gives the cluster authority over `*.workshops.tokenmaxxing-rehab.com` without moving the parent Netlify/NS1 zone. Status: **current**.
- **Crib K3s post-reboot outage**: cloud-init disabled Traefik, the HelmChartConfig override was removed from git, and an iptables DNAT proxy reported healthy while forwarding to dead NodePorts. Re-enabling Traefik triggered k3s CCM RBAC race (#7328). Recovery required ordered startup: disable CCM → let RBAC apply → re-enable CCM. Final model: Traefik hostPorts 80/443, DNAT proxy disabled. Status: **resolved, persisted**.
- **Hetzner K3s resize postmortem**: scheduler rejected pods at 96% CPU / 95% memory request saturation (not live usage). Terraform resize hazard: `user_data` drift would have replaced the server; `lifecycle.ignore_changes` fixed it. Post-reboot: Argo repo-server stuck Unknown (no Service endpoints), Keycloak CronJob ran before Keycloak accepted HTTP. Durable fixes: retry loops, Service endpoint checks. Status: **resolved**.
- **XMPP non-HTTP protocol deployment**: native XMPP C2S on TCP 5222 required three independent layers: pod `hostPort`, Hetzner firewall rule, and `_xmpp-client._tcp` SRV record in Terraform DNS. Federation deliberately disabled at every layer (no S2S listener, no 5269 firewall, no `_xmpp-server` SRV). cert-manager TLS shared between Traefik HTTPS and Prosody STARTTLS. Status: **current**.
- **Herold HTTPS-only MVP**: image architecture mismatch (`arm64` vs `amd64`) caught before deployment. PVC `WaitForFirstConsumer` deadlocked with Argo sync waves — PVC in wave 1, StatefulSet in wave 2. Traefik `spec.tls` does not restrict router to `websecure` entrypoint; explicit annotations required. VSO-generated secrets with `_raw` key broke Traefik basicAuth (needs single-key secret). Status: **current**.
- **Grafana Keycloak login**: browser → Traefik → Grafana → Keycloak Generic OAuth in `infra` realm. OAuth client secret moved from manual Kubernetes Secret to VSO-managed secret with narrow Vault policy. Traefik served self-signed cert for unmatched hostname before Ingress existed. Status: **current**.

### Arc 2: Backup / resilience

- **Jellyfin/TrueNAS NFS outage**: power outage stopped TrueNAS VM (no `onboot`), k3s VM restarted, `/mnt/media` existed as empty local dir (not NFS mount), Jellyfin served empty library. FFmpeg exit 254 was symptom, not cause. Fix: Proxmox `onboot` + startup ordering (TrueNAS order=10, k3s order=20), persistent NFS fstab entry. Status: **resolved, persisted**.
- **Crib restic backup baseline**: SFTP-only transport chosen over NFS specifically to avoid the Jellyfin failure mode (directory exists ≠ backing filesystem mounted). Vault stores TrueNAS provisioning API key at `kv/infra/truenas/provisioning`; nightly restic backups use dedicated SFTP user `backup-f` and never touch Vault. Clean baseline snapshot `b5530e39`, restore tested, user-level systemd timer enabled. Status: **current, operational**.
- **Credential separation**: three access tiers — operator (Vault OIDC), nightly backup (SFTP key, no Vault dependency), headless automation (AppRole, future). Old plaintext `/root/.truenas_api_key` on Proxmox identified for rotation/deletion. Restic password escrowed separately at `kv/infra/truenas/restic/laptop-f`. Status: **rotation pending**.
- **Historical backup baselines**: Coolify era had daily platform backups + 6-hour DB backups, S3 offsite deferred (March, **historical**). Vault bring-up tracked snapshot/offsite (TF-007) and audit logging (TF-009) as explicit follow-up tickets rather than vague future work (**partially implemented** for crib; **follow-up** for Vault/K3s platform state).

### Arc 3: Release trains and publishing

- **Release train invariant**: a repository may merge only after every upstream module version it requires has been merged, tagged, and made visible to `GOWORK=off go list -m -versions`. Dependency order derived from `go.mod`, not memory. `GOWORK=off` is mandatory for published-module validation — workspace tests can pass with untagged local code. Status: **current**.
- **PR readiness state machine**: readiness requires both CI checks (SUCCESS/SKIPPED/NEUTRAL) and Codex review (satisfied signal, not stale, not truncated). Three independent gates before merge: local validation, GitHub checks, Codex review. Codex feedback has current-head vs stale distinction via reviewed-commit marker. `ggg batch ready` emits structured exit codes (0=ready, 3=codex_feedback, 4=failed_checks, 5=partial_ready). Status: **current**.
- **INFRA-004 SQLite tracker**: finite state vocabulary (`planned → branch_created → local_validation → pr_open → codex_waiting → ready → merged → main_actions_verified`). Dashboard reads SQLite on every request, 10s HTML refresh. `no_runs` treated as terminal success for repos with no Actions workflows. Post-merge main verification is a separate gate from PR merge. Status: **current**.
- **Dagger/GoReleaser split-build**: macOS runners lack Docker; Dagger build separated into dedicated Linux job, artifacts shared via GitHub Actions. `SKIP_DAGGER=1` makes `go generate` a no-op when frontend already built. Runtime `init()` check detects missing embedded frontend for `go install` users. Status: **current**.
- **npm Trusted Publishing**: migration from Vault-backed `NODE_AUTH_TOKEN` to tokenless GitHub Actions OIDC. Package must exist before trusted publishing can be configured (bootstrap sequence). Token publishing disallowed after trusted publishing configured. Provenance attestation added. Status: **current**.
- **Buf Schema Registry publishing**: `buf.build/go-go-golems/pinocchio-chatapp` publishes protobuf schemas from Pinocchio repo. BSR token stored in Vault, released via GitHub Actions OIDC. CI gated to `v*` tag pushes where `proto/**/*.proto` changed. Generated TypeScript descriptors replace handwritten frontend payload types. Status: **current**.

---

## Candidate Map Nodes

| Node | Type | Confidence | Status | Notes |
|---|---|---|---|---|
| DigitalOcean DNS zone | platform | high | current | Delegated child zones for workshops, scapegoat.dev |
| Terraform DNS control loop | concept | high | current | Stable A records; separate from cert-manager ACME loop |
| cert-manager ACME DNS-01 | technology | high | current | ClusterIssuer `letsencrypt-prod-dns01-digitalocean` |
| Traefik ingress | technology | high | current | TLS termination + routing; hostPorts 80/443 on crib |
| Tailscale overlay | technology | high | current | WireGuard mesh; crib cluster ingress path |
| Traefik hostPort model | concept | high | current | Replaces DNAT-to-NodePort; requires `Recreate` update strategy |
| k3s CCM RBAC race | failure-mode | high | resolved | k3s#7328; recovery via ordered CCM disable/enable |
| Cloud-init state drift | failure-mode | high | resolved | Template diverges from running state silently |
| DNAT proxy false health | failure-mode | high | resolved | `oneshot` + `RemainAfterExit` reports healthy with dead backends |
| Scheduler request saturation | failure-mode | high | resolved | 96% CPU / 95% memory requests; `kubectl top` insufficient |
| Terraform resize hazard | failure-mode | high | resolved | `user_data` drift triggers server replacement |
| XMPP non-HTTP protocol deployment | concept | high | current | hostPort + firewall + SRV DNS; no-federation policy |
| No-federation policy | concept | high | current | Disabled at every layer: config, K8s, firewall, DNS |
| PVC sync-wave deadlock | failure-mode | high | resolved | `WaitForFirstConsumer` + Argo sync waves |
| Traefik TLS entrypoint annotation | concept | high | current | `spec.tls` ≠ router TLS restriction; need `websecure` + `router.tls` |
| VSO secret shape mismatch | failure-mode | high | resolved | Traefik basicAuth needs single-key secret; VSO adds `_raw` |
| Restic SFTP backup baseline | project | high | current | Laptop `f` → TrueNAS via SFTP; repo `57e82c013a` |
| SFTP fail-closed transport | concept | high | current | No NFS/local fallback; directory exists ≠ backing FS mounted |
| Vault provisioning credential tier | concept | high | current | Vault for admin ops; nightly backup independent of Vault |
| NFS silent mount failure | failure-mode | high | resolved | Empty local dir masquerading as NFS mount; Jellyfin outage |
| Proxmox boot ordering | concept | high | current | TrueNAS order=10 before k3s order=20 |
| Release train invariant | concept | high | current | Upstream must be tagged+visible before downstream merge |
| GOWORK=off validation | concept | high | current | Disables workspace; tests against published module versions |
| `ggg` CLI | project | high | current | Go-based release tooling: PR readiness, Codex, batch, tagging |
| PR readiness state machine | concept | high | current | Checks + Codex gates; stale vs current-head feedback |
| Codex review signal model | concept | high | current | EYES/THUMBS_UP reactions, reviewed-commit marker, truncation |
| INFRA-004 SQLite tracker | project | high | current | Finite state vocabulary, dashboard, post-merge main verification |
| `no_runs` terminal success | concept | high | current | Repos with no Actions runs are not failures |
| Dagger/GoReleaser split-build | concept | high | current | Linux-only Dagger, artifact sharing, SKIP_DAGGER no-op |
| npm Trusted Publishing | technology | high | current | Tokenless OIDC; replaces Vault NODE_AUTH_TOKEN |
| Buf Schema Registry module | technology | high | current | `buf.build/go-go-golems/pinocchio-chatapp` |
| Vault-backed BSR token | concept | high | current | BSR token in Vault, released via GitHub Actions OIDC |
| Protobuf schema distribution | concept | high | current | Generated descriptors replace handwritten payload types |

---

## Candidate Map Edges

```
Terraform DNS control loop --manages stable A records in--> DigitalOcean DNS zone [high] (Workshops report)
cert-manager ACME DNS-01 --creates temporary TXT records in--> DigitalOcean DNS zone [high] (Workshops report)
cert-manager ACME DNS-01 --writes--> TLS Kubernetes Secret [high] (Workshops, XMPP, Herold reports)
TLS Kubernetes Secret --consumed by--> Traefik ingress [high] (Workshops, XMPP, Grafana reports)
Traefik ingress --routes HTTPS to--> Kubernetes Services [high] (XMPP, Herold, Grafana reports)
Tailscale overlay --delivers TCP 80/443 to--> Traefik hostPort model [high] (Post-reboot outage report)
Cloud-init state drift --causes--> Traefik missing after reboot [high] (Post-reboot outage report)
DNAT proxy false health --masks--> Traefik missing after reboot [high] (Post-reboot outage report)
k3s CCM RBAC race --blocks--> Traefik re-enablement [high] (Post-reboot outage report)
Scheduler request saturation --causes--> FailedScheduling [high] (Resize postmortem)
Terraform resize hazard --threatens--> server replacement [high] (Resize postmortem)
XMPP non-HTTP protocol deployment --requires--> Traefik hostPort model [high] (XMPP report)
XMPP non-HTTP protocol deployment --requires--> Hetzner firewall rule [high] (XMPP report)
XMPP non-HTTP protocol deployment --requires--> SRV DNS record [high] (XMPP report)
No-federation policy --disables--> S2S listener at every layer [high] (XMPP report)
PVC sync-wave deadlock --blocks--> StatefulSet startup [high] (Herold report)
Traefik TLS entrypoint annotation --restricts router to--> websecure entrypoint [high] (Herold report)
VSO secret shape mismatch --breaks--> Traefik basicAuth middleware [high] (Herold report)
NFS silent mount failure --causes--> Jellyfin empty library [high] (Jellyfin postmortem)
Proxmox boot ordering --prevents--> NFS silent mount failure [high] (Jellyfin postmortem)
SFTP fail-closed transport --avoids--> NFS silent mount failure [high] (Crib backup report)
Vault provisioning credential tier --stores--> TrueNAS API key [high] (Crib backup, Backup architecture reports)
Restic SFTP backup baseline --uses--> SFTP fail-closed transport [high] (Crib backup report)
Restic SFTP backup baseline --does not depend on--> Vault provisioning credential tier [high] (Crib backup report)
Release train invariant --enforces--> GOWORK=off validation [high] (Release trains report)
GOWORK=off validation --proves--> published module graph [high] (Release trains, ggg reports)
ggg CLI --implements--> PR readiness state machine [high] (ggg report)
PR readiness state machine --classifies--> Codex review signal model [high] (ggg report)
Codex review signal model --distinguishes--> stale vs current-head feedback [high] (ggg report)
INFRA-004 SQLite tracker --records--> post-merge main verification [high] (INFRA-004 report)
no_runs terminal success --prevents--> indefinite wait in ggg run status [high] (INFRA-004 report)
Dagger/GoReleaser split-build --separates--> Dagger build into Linux-only job [high] (Dagger report)
Dagger/GoReleaser split-build --uses--> SKIP_DAGGER no-op [high] (Dagger report)
npm Trusted Publishing --replaces--> Vault NODE_AUTH_TOKEN [high] (Trusted npm report)
Buf Schema Registry module --distributes--> Protobuf schema distribution [high] (Protobuf report)
Vault-backed BSR token --releases--> Buf API token via OIDC [high] (Protobuf report)
```

---

## Cross-Links to Other Topic Slices

- **Topic 4 / Partition A (04a)**: DNS/TLS networking depends on the same Terraform → cloud-init → Argo CD → Vault platform that Partition A documents. The workshops DNS delegation, XMPP firewall, and Herold HTTPS deployment all consume the K3s platform contract. Backup credential tiers consume Vault (partition A's secret plane). Release train `ggg` tooling uses the same infra-tooling repo that hosts CI/GitOps credential flows documented in Partition A.
- **Topic 2 / JavaScript runtimes (02a/02b)**: Release trains were driven by the xgoja runtime API rollout (`go-go-goja` → `geppetto` → `pinocchio` → downstream repos). The `GOWORK=off` validation invariant and Codex review gates exist because xgoja provider packages must prove compatibility with published module versions. The Buf Schema Registry publishes Pinocchio's chatapp protobuf schemas that the React chat provider (topic 7) consumes.
- **Topic 5 / AI agents / observability (05)**: Codex review is a first-class gate in the release train — not a human reviewer, but an AI agent that produces structured feedback (inline comments, reviewed-commit markers, reaction signals). The `ggg` readiness model treats Codex as an asynchronous signal source with stale/current-head semantics. INFRA-004's SQLite tracker is itself an agent-readable artifact (dashboard, structured state, event log).
- **Topic 6 / Data / RAG / search (06)**: Protobuf Schema Publishing distributes schemas that define data contracts between Pinocchio backend and React frontend. The Buf module replaces handwritten TypeScript payload types with generated descriptors — the same "generated artifact replaces manual implementation" pattern seen in RAG chunk/embedding pipelines.
- **Topic 7 / Web UI / apps / media (07)**: npm Trusted Publishing publishes `@go-go-golems/chat-provider` and `@go-go-golems/chat-overlay` packages consumed by React chat overlays (topic 7). The Dagger/GoReleaser split-build pattern embeds React/Vite SPAs into Go binaries. Herold and XMPP deployments are protocol service deployments on the same K3s platform. Jellyfin outage is a media-serving failure on the crib cluster.
- **Topic 1 / Hardware (01)**: Backup/resilience arc touches the Proxmox homelab that also hosts hardware-adjacent services. Proxmox boot ordering (TrueNAS before k3s) is a homelab infrastructure concern. The crib cluster runs on Proxmox QEMU VMs.

---

## Open Questions and Second-Pass Targets

1. Is the Terraform DNS commit for workshops (`311011d` on branch `task/docsctl-goja-dbus-publisher`) merged into the intended Terraform branch? The report notes it as an infrastructure-as-code drift risk.
2. Has the old `/root/.truenas_api_key` on Proxmox been rotated or deleted? The crib backup reports mark this as the remaining security task.
3. Are Vault snapshots (TF-007) and audit logging (TF-009) now implemented, or still follow-up? The March Terraform Infra report tracked them as tickets; the June backup reports don't confirm resolution.
4. Should the concept map distinguish `crib.scapegoat.dev` (Tailscale/proxmox), `yolo.scapegoat.dev` (Hetzner K3s), and `workshops.tokenmaxxing-rehab.com` (delegated) as separate environment/namespace nodes?
5. Is the `ggg release tag-*` family tested with temporary git repositories? The ggg report marks this as remaining work.
6. Has the first scheduled restic timer run been verified? The crib backup report marks this as the next operational check.

---

## Start Here

1. `Projects/2026/06/17/PROJECT REPORT - Workshops Wildcard DNS and TLS - DigitalOcean Delegation Deep Dive.md` — the canonical DNS/TLS contract: two independent control loops (Terraform stable records vs cert-manager ACME TXT), subdomain delegation pattern, layered validation. This is the clearest articulation of the DNS ownership boundary.
2. `Projects/2026/05/26/ARTICLE - Managing Go-Go-Golems Release Trains.md` — the canonical release train contract: dependency-order invariant, `GOWORK=off` validation, CI+Codex dual gates, early-PR/late-merge pattern. This is the process spine that `ggg` and INFRA-004 implement.

---
title: "KB Playbook Batch 5: Infrastructure/Secrets/Glazed (6 Projects)"
doc-type: reference
topics: parc, knowledge-base, infrastructure, vault, secrets, glazed, sql
owners: manuel
created: "2026-05-11"
---

# KB Playbook Batch 5: Infrastructure/Secrets/Glazed

Analysis of 6 projects from the infrastructure/secret-delivery/Glazed domain. Strategic batch targeting 2/3 candidates near threshold.

## Projects analyzed

1. Vault on K3s — Auth and Secret Delivery Platform (9.5 KB)
2. Glazed Secret Redaction and Vault Bootstrap (17 KB)
3. Minitrace Query Commands — Sqleton-Inspired SQL Verb System (21 KB)
4. Hetzner K3s Platform — Single-Node GitOps Bring-Up (8 KB)
5. CoinVault on K3s — First Real GitOps App (10 KB)
6. Terraform Infra — Vault Platform Bring-Up, Auth Hardening, Hair-Booking Handoff (17 KB)

---

## Candidates pushed to 3/3

### SQL as first-class command source (3/3 → READY)

| Project | How it contributes |
|---------|-------------------|
| Sqleton | Origin: SQL files with YAML preambles as Glazed verb definitions |
| Minitrace Query Commands | Adoption: same format, same compilation pipeline, adds catalog/repo/alias |
| *(third: any project using embedded SQL as command definitions)* | The format is now proven in two independent codebases with different downstream consumers |

**Core insight**: SQL is not just a query language — it's a command definition format. When SQL files carry structured metadata (YAML preambles), they become discoverable, parameterizable, type-safe commands that Glazed can compile into CLI verbs, HTTP endpoints, and UI forms. The SQL is the source of truth; the command infrastructure is generated.

### Host-mediated secret delivery (3/3 → READY)

| Project | How it contributes |
|---------|-------------------|
| Firecracker VM | Host injects secrets into guest VM via host-mediated channel |
| BYOK Host | Host mediates credential delivery between Keycloak and provider connections |
| Vault on K3s / Glazed Vault / Terraform Vault | Three projects share the same architecture: Vault stores values, host (K8s/Glazed/Terraform) mediates delivery, consumer receives bounded secrets |

**Core insight**: Secrets should never be copied or stored at the consumption point. The host (Vault Secrets Operator, Glazed source middleware, Terraform provider) fetches secrets at runtime from the authority (Vault) and delivers them to the consumer as bounded, short-lived, policy-gated values. The consumer never talks to Vault directly.

---

## Other candidates updated

### Three-layer credential separation (still 2/3)

Wish Git and Agent Enroll are the two instances. CoinVault on K3s uses Keycloak + Vault but doesn't have the agent/run credential layer. The Vault projects have a two-layer model (Keycloak for humans, AppRole/K8s for machines), not three. No new project pushed this to 3/3.

### App config vs command config separation (still 2/3)

Sqleton and BYOK Host are the two instances. The Glazed Vault project explicitly separates Vault bootstrap config from command config — this might count. The key question: is "bootstrap parsing for Vault settings" the same pattern as "app config vs command config"? It's the same core insight: two config sources play different roles, and precedence matters. **Counting Glazed Vault pushes this to 3/3 → READY.**

---

## Concept extraction (key patterns)

### Vault on K3s

- **Secret intent in Git, secret values in Vault** — deployment shape is declarative, actual secrets are fetched at runtime
- **Separate human auth (OIDC) from machine auth (Kubernetes SA)** — different trust boundaries, different token lifetimes
- **Vault Secrets Operator as the delivery bridge** — apps consume native K8s Secrets, VSO syncs from Vault
- **First root wins on duplicate paths** — repository precedence for command discovery

### Glazed Secret Redaction

- **Central redaction policy, not per-call-site masking** — one `RedactValue` function, all output paths route through it
- **Only TypeSecret fields eligible for Vault hydration** — prevents accidental overwrite of non-sensitive fields
- **Bootstrap parsing for provider settings** — mini-parse of Vault config before main parse, preserving precedence
- **Vault as source middleware, not special parser** — fits into existing `defaults → config → vault → env → args → cobra` chain

### Minitrace Query Commands

- **SQL files as command definitions** — `.sql` with `/* sqleton */` YAML preamble → Glazed verb
- **Aliases with pre-applied defaults** — `.alias.yaml` files that reference a parent command and set specific flag values
- **First repository root wins** — external repos override embedded commands
- **Template helpers for safe SQL rendering** — `sqlString`, `sqlStringIn`, `sqlIntIn`, `sqlLike`

### Hetzner K3s Platform

- **Terraform creates, cloud-init bootstraps, Argo CD reconciles** — three-phase bring-up with clear ownership
- **Platform is the product, not Kubernetes** — the value is decomposability, not the orchestrator

### CoinVault on K3s

- **Real app migration validates the platform** — a real workload with auth, secrets, database, and ingress
- **VSO-managed secrets replace manual env handling** — CoinVault receives runtime material through VSO

### Terraform Infra Vault

- **Four control planes in one session** — Terraform, Coolify API, Vault, Keycloak
- **Keycloak group-gated Vault access** — not all GitHub users can access Vault, only specific groups
- **AppRole for machines, OIDC for humans** — same two-layer model as Vault on K3s

---

## New tribal candidates

| Concept | Seen in | Status |
|---------|---------|--------|
| Secret intent in Git, values in Vault | Vault on K3s, Glazed Vault, CoinVault on K3s | 3/3 → subsumed by host-mediated-secret-delivery |
| Central redaction policy | Glazed Vault | 1/3 |
| Bootstrap parsing for provider config | Glazed Vault | 1/3 |
| SQL files with YAML preamble as command definitions | Sqleton, Minitrace Query Commands | → subsumed by sql-as-command-source |
| First repository root wins | Minitrace Query Commands, (other repo systems) | 1/3 |
| Terraform creates, cloud-init bootstraps, Argo reconciles | Hetzner K3s | 1/3 |
| Real app migration validates the platform | CoinVault on K3s | 1/3 |
| Keycloak group-gated Vault access | Terraform Vault, Vault on K3s | 2/3 |
| Separate human auth (OIDC) from machine auth (AppRole/K8s) | Vault on K3s, Terraform Vault | 2/3 |

---

## Playbook feedback (Batch 5)

1. **Strategic batch selection works.** I deliberately picked projects that would push candidates over threshold, and it worked: SQL-as-command-source and host-mediated-secret-delivery both hit 3/3. App-config-vs-command-config hits 3/3 if we count Glazed Vault's bootstrap parsing. This is more efficient than random selection.

2. **Secret-delivery pattern spans three domains.** Firecracker (VM isolation), BYOK Host (credential brokering), and Vault/K8s (infrastructure secrets) all share the same core insight despite being in different domains. This validates the playbook's "count by core insight, not by surface API" rule.

3. **Vault projects are tightly coupled.** The three Vault projects (Vault on K3s, Glazed Vault, Terraform Vault) are different facets of the same infrastructure effort. They all reinforce the same candidates. For future batches, I should avoid picking multiple projects from the same infrastructure effort.

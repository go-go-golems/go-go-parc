---
title: "Application-Native Authorization — How We Do It"
aliases:
  - app-native authz
  - keycloak plus local auth
  - agent authorization
  - delegated authorization
tags: [knowledge-base, tribal, authorization, agents, keycloak, security]
status: active
type: knowledge-base
created: 2026-05-11
---

# Application-Native Authorization — How We Do It

> [!summary]
> Keycloak authenticates humans; the Go application owns agent, run, and task authorization. This separation is the core pattern for any system where autonomous agents operate under delegated human authority. Three projects independently arrived at the same architecture: BYOK Host, Wish Git, and Agent Enroll.

## The pattern

Our Go services validate Keycloak tokens locally to establish human identity, then make all downstream authorization decisions in application code and application storage. Keycloak does not know about agents, runs, tasks, boards, or scoped delegations. The Go service does.

The pattern has three layers:

1. **Human authentication** — Keycloak issues a signed JWT after the user authenticates (browser redirect, CLI callback, or API credential exchange). The Go service validates the JWT locally using cached JWKS keys. This establishes *who the human is*.

2. **Agent enrollment** — A human with appropriate roles creates an agent identity in the application. The agent receives a credential that proves its identity without involving Keycloak. This establishes *which agent is speaking*.

3. **Scoped delegation** — When an agent acts, the application issues a narrow, short-lived credential that constrains what the agent may do in this specific operation. This constrains *what the agent can touch*.

Each layer is narrower than the one above it. A human can create an agent, but an agent cannot create a human. An agent can claim a task, but a run token cannot claim tasks. This one-way narrowing keeps failures contained.

### The credential chain in each project

| Project | Human credential | Agent credential | Scoped credential | Storage |
|---------|-----------------|-----------------|-------------------|---------|
| BYOK Host | Keycloak JWT | Broker OAuth token (issued by broker, not Keycloak) | Per-connection grant | SQLite |
| Wish Git | Keycloak JWT | SSH user certificate (signed by forge CA) | Certificate principals + force-command + pre-receive hook | PostgreSQL |
| Agent Enroll | Keycloak JWT | Ed25519 keypair + canonical request signing | Opaque run token (hash-only, task/run bound) | SQLite |

The specific credential mechanisms differ, but the architecture is the same: Keycloak authenticates the human, the Go application decides what agents and runs can do.

## Why we do it this way

**Keycloak is the right tool for human authentication but the wrong tool for agent authorization.** Keycloak excels at browser redirects, PKCE flows, token signing, and realm management. But Keycloak does not know about our domain concepts — agents, runs, tasks, boards, repositories, branches, or file paths. Modeling these in Keycloak roles creates coupling that makes permissions hard to audit and impossible to test locally.

**Application-native authorization keeps the trust model explicit.** When the Go service owns the authorization decisions, the database is the source of truth for what each credential can do. You can query the database to answer "what can this agent do?" without consulting Keycloak. You can test authorization logic with unit tests that hit a temporary SQLite database, not a running Keycloak instance.

**The credential chain narrows authority at each step.** This is the most important security property. If an agent's credential leaks, the damage is bounded by the agent's board grants and the run's task binding. If a run token leaks, the damage is bounded by the single task and the token's expiry. The human's Keycloak token never appears in the agent's runtime environment.

**Local JWT validation eliminates the Keycloak runtime dependency.** Our services validate tokens using cached JWKS keys, not by calling Keycloak's introspection endpoint on every request. If Keycloak goes down, existing tokens continue to work until they expire. New logins fail, but authenticated sessions survive.

## Where it lives

| Repo | Path | Use |
|------|------|-----|
| `2026-04-17--byok-host` | `internal/auth/`, `internal/app/broker.go` | Keycloak login + broker authorization decisions |
| `2026-05-01--wish-git` | `internal/auth/`, `internal/certs/`, `internal/sshserver/`, `internal/githook/` | Keycloak validation + SSH cert issuance + hook enforcement |
| `2026-05-03--agent-enroll` | `internal/auth/`, `internal/agent/`, `internal/runs/` | Keycloak validation + agent enrollment + run-token authz |

### Related PARC project reports

- [[PROJ - BYOK Host - Project Report]] — broker-not-proxy architecture: "Keycloak authenticates the user; the broker decides what the user's stored provider connection may be used for"
- [[PROJ - Wish Git - OAuth Scoped Git over SSH for Coding Agents]] — three-credential separation: Keycloak → broker → SSH certificate
- [[PROJ - Agent Enroll - Kanban Agent Credential MVP Deep Dive]] — three-layer narrowing: human token → agent key → run token

## Common mistakes

1. **Conflating authentication and authorization.** The most common mistake is treating a valid Keycloak token as sufficient authorization for everything. A Keycloak token proves *who the human is*, not *what an agent may do*. In Wish Git, the SSH certificate's `force-command` and `principals` are the authorization decision, not the Keycloak token. In Agent Enroll, the run token's task/run binding is the authorization decision, not the agent key. If you skip the application-native authorization layer, any authenticated human can perform any operation — a privilege escalation.

2. **Modeling agent permissions in Keycloak roles.** Keycloak `realm_access.roles` are useful for coarse UI rendering ("show the admin panel"). They are not sufficient for data authorization ("can this agent push to this branch?"). When we tried putting fine-grained permissions in Keycloak roles, the result was: permissions became hard to audit (scattered across Keycloak realm config and application code), hard to test (need a running Keycloak to verify role assignments), and hard to evolve (changing a role required Keycloak admin access plus application code changes).

3. **Giving agents the human's OAuth token.** A Keycloak access token issued for the human should never be available to the agent process. If the agent's environment contains the human's refresh token, a compromised agent can impersonate the human across all services. Wish Git enforces this: the SSH certificate is the *only* credential the agent sees. Agent Enroll enforces this: the agent signs requests with its own Ed25519 key, and the run token is a separate opaque bearer token.

4. **Forgetting `audience` validation.** A JWT issued for `byok-host` should not be accepted by `wish-git`. Each service validates `aud` against its own client ID. Without this check, a token issued for one service is valid for all services in the realm — a subtle privilege escalation. This mistake is specific to the Keycloak layer, but it's the kind of mistake that happens when you rush the auth boundary.

5. **Broad credentials that answer all questions.** The system stays understandable when each credential answers one question. It becomes fragile when one broad credential (like a long-lived API key or a Keycloak admin token) starts answering both "who am I?" and "what can I do?" and "which task may I mutate?" If you catch yourself passing a single credential through three layers of the system, stop and split it.

6. **Not testing authorization logic against a real database.** Authorization decisions in these systems are SQL queries with WHERE clauses binding to org_id, board_id, task_id, and run_id. These queries are easy to get wrong — a missing WHERE clause becomes an authorization bypass. Agent Enroll's integration tests (`TestRunTokenStoredHashedAndBoundToTask`, `TestConcurrentClaimOnlyOneAgentWins`) directly verify that the SQL enforces the security model. Without these tests, a refactor that drops a WHERE clause ships silently.

## Variations

- **Broker as authorizer** (BYOK Host). The broker is not a transparent proxy — it makes authorization decisions, stores grants, and issues its own tokens. The human authenticates at Keycloak; the broker decides what the stored provider connection may be used for.

- **SSH certificates for scope** (Wish Git). The forge signs SSH user certificates with `principals` (repository), `force-command` (git-receive-pack or git-upload-pack), and `valid-before` (5 minutes). SSH server and Git hooks enforce. Uses OpenSSH's certificate infrastructure instead of opaque tokens.

- **Opaque run tokens** (Agent Enroll). The API mints short-lived, hash-only bearer tokens bound to one task and one run. Server checks expiry, revocation, run status, and task binding on every request. The simplest variation — no cryptographic signing infrastructure, just database rows.

- **API keys for machine-to-machine**. Long-lived API keys validated against a database, then look up the associated Keycloak user for audit. No JWT or certificate involved.

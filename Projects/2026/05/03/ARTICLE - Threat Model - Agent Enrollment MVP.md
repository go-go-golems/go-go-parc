---
title: Threat Model for Agent Enrollment MVP
aliases:
  - Agent Enrollment MVP Threat Model
  - Kanban Agent Threat Model
  - Agent Enroll Security Model
tags:
  - article
  - security
  - threat-model
  - agents
  - keycloak
  - go
  - sqlite
status: active
type: article
created: 2026-05-03
repo: /home/manuel/code/wesen/2026-05-03--agent-enroll
ticket: AGENT-ENROLL-MVP
source: /home/manuel/code/wesen/2026-05-03--agent-enroll/ttmp/2026/05/03/AGENT-ENROLL-MVP--agent-enrollment-token-mvp-for-kanban/design-doc/02-threat-model-for-agent-enrollment-mvp.md
summary: Threat model for the Kanban agent enrollment MVP, written for interns implementing or reviewing the system.
---

# Threat Model for Agent Enrollment MVP

## Executive Summary

This chapter explains what can go wrong in the Kanban agent enrollment MVP and how the current design tries to make those failures small, visible, and recoverable. The system lets humans create work, enroll coding agents, and allow those agents to claim and update tasks. That is useful, but it creates a new security problem: an automated process can now mutate project state. The threat model is the map that tells us which mutations are allowed, which are forbidden, and what evidence we expect to have when something suspicious happens.

The most important idea is separation of authority. A human token is not an agent token, and an agent key is not a run token. A human token proves that a person authenticated through Keycloak may manage organization resources. An agent key proves that one enrolled automation identity possesses a private key. A run token proves that one specific run may touch one specific task for a short time. If those three ideas stay separate, most failures are contained. If they blur together, the system becomes much harder to reason about.

The current implementation already includes several important controls:

- Keycloak-backed human JWT validation with JWKS in `internal/auth/jwks.go`.
- Owner/admin role enforcement for agent management in `internal/agent/agent.go`.
- Ed25519 signed agent requests with timestamp and nonce checks in `internal/agent/signature.go`.
- Atomic task claiming and short-lived opaque run tokens in `internal/runs/runs.go`.
- Hash-only storage for enrollment and run tokens.
- Agent revocation, key revocation, and run-token revocation.
- SQLite WAL mode and backup support in `internal/storage/sqlite.go`.
- In-memory rate limiting in `internal/http/ratelimit.go`.
- Audit logging in `internal/audit/audit.go`.

This is enough for a local MVP and a carefully controlled private alpha. It is not enough to treat as a mature internet-facing multi-tenant service without more work. The highest-priority remaining risks are CLI credential storage, deployment TLS/proxy configuration, backup/restore automation, audit visibility, stricter role administration, and operational runbooks for revocation and incident response.

## 1. How to Read a Threat Model

A threat model is not a list of scary possibilities. It is a structured way to connect assets, attackers, entry points, controls, and residual risks. The useful question is not “can something bad happen?” The useful question is “what bad thing are we worried about, how would it happen, what stops it, and what would we see if it happened anyway?”

For this system, the answer usually follows this shape:

```text
Asset:       one task, one board, one agent key, one run token, one org
Attacker:    human user, compromised agent, network attacker, DB reader, buggy client
Entry point: HTTP endpoint, CLI config, SQLite file, Keycloak token, enrollment token
Control:     auth mode, role check, signature, nonce, transaction, token hash, audit log
Residual:    what is still possible after the control works as designed
```

This document uses that structure repeatedly. The goal is not to memorize every row. The goal is to learn the habit: every security feature protects a specific asset from a specific class of failure.

## 2. System Boundaries

The MVP has four main components. Each component has a different trust level, and the boundaries between them matter.

```text
┌────────────────────────────────────────────────────────────────┐
│ Human workstation                                               │
│ - kanban-agent CLI                                              │
│ - Keycloak access/refresh token                                 │
│ - enrolled agent private key                                    │
└──────────────┬─────────────────────────────────────────────────┘
               │ HTTPS in real deployment; HTTP only for local dev
               ▼
┌────────────────────────────────────────────────────────────────┐
│ Go API                                                          │
│ - validates Keycloak human tokens                              │
│ - enforces org roles and board grants                           │
│ - verifies agent signatures                                     │
│ - mints opaque run tokens                                       │
│ - writes audit log                                              │
└──────────────┬─────────────────────────────────────────────────┘
               │ local filesystem / database connection
               ▼
┌────────────────────────────────────────────────────────────────┐
│ SQLite                                                          │
│ - orgs, users, memberships                                      │
│ - boards, tasks, comments                                       │
│ - agents, agent_keys, grants                                    │
│ - enrollment token hashes, run token hashes                     │
│ - nonces, audit log                                             │
└────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────┐
│ Keycloak                                                        │
│ - human identity provider                                       │
│ - OIDC/JWT issuer                                               │
│ - JWKS endpoint                                                 │
│ - device login                                                  │
└────────────────────────────────────────────────────────────────┘
```

The Go API trusts Keycloak for human identity, but it does not trust Keycloak to decide Kanban domain permissions. Keycloak tells us who the human is. The Go API decides whether that human may create an agent, revoke an agent, or create an enrollment token.

The Go API trusts SQLite as its source of application state. If an attacker can arbitrarily write SQLite rows, most application-level controls can be bypassed. That is why deployment, filesystem permissions, backup handling, and operational access are part of the threat model even though they are not HTTP endpoints.

The CLI is powerful because it stores credentials. A compromised CLI machine may contain a human refresh token and one or more agent private keys. The server-side design reduces the blast radius of agent keys, but it cannot make a stolen human refresh token harmless.

## 3. Assets

An asset is something we must protect because losing it, corrupting it, or exposing it would harm the system or its users.

| Asset | Why it matters | Where it lives |
|---|---|---|
| Human Keycloak access token | Lets a human call management endpoints until expiry. | CLI config, HTTP headers. |
| Human Keycloak refresh token | Can mint new access tokens; higher value than access token. | CLI config. |
| Agent private key | Lets an enrolled agent sign claim requests. | CLI config today; should move to separate key file/keychain. |
| Agent public key | Lets the server verify signed requests. | `agent_keys.public_key`. |
| Enrollment token plaintext | Lets a remote machine enroll an agent once. | Returned once to human; never stored plaintext. |
| Enrollment token hash | Lets the server verify one-time enrollment. | `enrollment_tokens.token_hash`. |
| Run token plaintext | Lets a run mutate exactly one task/run until expiry. | CLI output / child process env or args. |
| Run token hash | Lets the server authenticate run-token requests. | `run_tokens.token_hash`. |
| Task data | The work being assigned and mutated. | `tasks`, `comments`. |
| Org membership and roles | Defines who may manage resources. | `memberships`. |
| Audit log | Evidence of sensitive actions. | `audit_log`. |
| SQLite database and backups | Complete application state. | `kanban.db`, backup files. |

Two assets are especially easy to misunderstand: public keys and token hashes. Public keys are not secrets; they are integrity anchors. Token hashes are sensitive but not equivalent to plaintext tokens. If a database reader sees `run_tokens.token_hash`, they should not be able to use it as a bearer token. That is why the server hashes incoming tokens and compares hashes rather than storing the token itself.

## 4. Actors and Attacker Models

The system has legitimate actors and adversarial actors. Sometimes the same person can be both: a legitimate org member may try an action their role should not allow.

### Legitimate actors

- **Owner/admin human:** May create boards, tasks, agents, enrollment tokens, and revoke agents.
- **Member human:** May create/list Kanban work in the current MVP, but should not manage agents.
- **Enrolled agent:** May claim from boards where it has a grant.
- **Active run:** May mutate only the task/run bound to its run token.
- **Operator:** May administer Keycloak, deploy the API, access backups, and inspect logs.

### Adversarial actors

- **Anonymous internet client:** Can hit public HTTP endpoints and try brute force, replay, or load attacks.
- **Malicious org member:** Has a real human token but should not manage agents or other orgs.
- **Compromised agent machine:** Has an agent private key and maybe a run token.
- **Compromised human workstation:** Has human access/refresh tokens and maybe agent private keys.
- **Database reader:** Can read SQLite and backups but cannot modify live requests.
- **Database writer:** Can modify SQLite; this is close to total compromise.
- **Network attacker:** Can observe or modify traffic if TLS is absent or misconfigured.
- **Buggy client or runaway agent:** Not malicious, but can create load, nonce growth, repeated claims, or repeated comments.

The MVP mostly defends against anonymous clients, malicious org members, compromised agents, database readers, replay attempts, and buggy agents. It cannot fully defend against a compromised API host, arbitrary database writes, or a stolen human refresh token without additional operational controls.

## 5. Security Invariants

A security invariant is a statement that must remain true no matter how the implementation changes. Tests, code review, and incident response should come back to these invariants.

1. **A human token may manage agents only if the local role check permits it.** Keycloak authenticates the person; it does not grant Kanban admin powers by itself.
2. **An agent is not a Keycloak user.** Agent identity is application-native and based on stored public keys.
3. **An agent private key may claim only from granted boards.** The key proves possession; `agent_board_grants` decides scope.
4. **A task may be claimed by at most one active run.** The guarded SQL update and transaction enforce this.
5. **A run token may mutate only its bound task and run.** URL parameters must be checked against the token row.
6. **Plaintext enrollment tokens and run tokens are never stored.** SQLite stores hashes only.
7. **Signed requests are fresh and non-replayed.** Timestamp windows and `agent_nonces` enforce this.
8. **Revoked agents and keys cannot authenticate future claims.** Signature verification joins only active agents and active keys.
9. **Security-sensitive actions are auditable.** The audit log records who did what to which resource.
10. **Local database backups are consistent.** WAL mode requires `VACUUM INTO` or another SQLite-safe backup method.

If you change code and one of these statements becomes false, you are probably not doing a refactor. You are changing the security model.

## 6. Data Flow 1: Human Login and Management Actions

Human login starts in Keycloak. The CLI obtains a Keycloak access token and refresh token, stores them locally, and sends the access token to the Go API.

```text
kanban-agent login --keycloak
        │
        ▼
Keycloak device/password flow
        │ returns access token + refresh token
        ▼
CLI config file
        │ Authorization: Bearer <access_token>
        ▼
Go API auth middleware
        │ validates JWT signature via JWKS
        │ checks issuer, expiry, aud/azp, sub
        ▼
local users row keyed by keycloak|sub
        │
        ▼
role checks in memberships
```

The main threat is token misuse. A stolen access token lets an attacker act as the human until it expires. A stolen refresh token is worse because it can mint new access tokens. The current CLI refresh support improves usability, but it also makes the refresh token a high-value asset.

Concrete code references:

- `internal/auth/jwks.go` validates Keycloak access tokens.
- `internal/auth/device.go` starts device login and refreshes tokens.
- `cmd/kanban-agent/main.go` stores tokens and refreshes before human-auth API calls.
- `internal/agent/agent.go` checks `owner` or `admin` before agent management.

Key points to internalize:

- Keycloak answers “who is this human?”
- The Go API answers “what may this human do in this org?”
- A valid Keycloak token without local membership should not imply access to org resources.

## 7. Data Flow 2: Interactive Agent Enrollment

Interactive enrollment is the normal local developer path. The human is already logged in, so there is no copy-paste enrollment token.

```text
Human CLI                         Go API                         SQLite
   │                                │                              │
   │ generate Ed25519 keypair       │                              │
   │ POST /v1/agents                │                              │
   │ Authorization: Bearer human    │                              │
   ├───────────────────────────────▶│ validate human JWT           │
   │                                │ require owner/admin          │
   │                                │ validate public key          │
   │                                │ create agent/key/grant       ├──▶ agents
   │                                │ write audit event            ├──▶ audit_log
   │◀───────────────────────────────┤ agent_id, key_id             │
   │ store private key locally      │                              │
```

The private key is generated on the client and never sent to the server. The public key is stored in SQLite. The server does not need to know the private key to verify future signatures.

Threats and controls:

| Threat | Control | Residual risk |
|---|---|---|
| Ordinary member creates an agent. | `CreateInteractive` requires `owner` or `admin`. | Role model is still simple string roles. |
| Malformed public key inserted. | `decodePublicKey` checks base64 and Ed25519 size. | It does not prove the client kept the private key; first signed request proves that. |
| Human creates overly broad agent. | Grants are board-specific. | Current CLI defaults all board permissions to true. |
| Private key stolen from CLI config. | Server-side board grants and revocation reduce blast radius. | CLI key storage should move out of JSON config. |

The common misunderstanding is thinking the agent inherits the human's authority. It does not. The human authorizes the creation of an agent record and a board grant. After enrollment, the agent uses its own key and its own grants.

## 8. Data Flow 3: Headless Enrollment Token

Headless enrollment exists for CI machines, containers, and remote hosts. It is more dangerous than interactive enrollment because it creates a copy-paste secret.

```text
Human machine                         Remote machine
   │                                        │
   │ create enrollment token                │
   │ enr_live_abc...                        │
   ├───────────────────────────────────────▶│ paste through secure channel
                                            │ generate Ed25519 keypair
                                            │ POST /v1/agents/enroll
                                            │ token + public key
                                            ▼
                                     Go API burns token
```

The token is one-time and short-lived. The server stores only its hash.

Pseudo-code:

```go
func EnrollWithToken(token, publicKey string) error {
    hash := HashToken(token)

    tx := Begin()
    row := SELECT token WHERE token_hash = hash AND used_at IS NULL
    if row missing: reject
    if row.expires_at < now: reject

    validate public key
    create agent
    create key
    create board grant
    UPDATE enrollment_tokens SET used_at = now
    commit
}
```

Threats and controls:

- A database reader cannot enroll with `token_hash` because the plaintext token is not stored.
- A token replay fails because `used_at` is set in the same transaction as agent creation.
- An old token fails because `expires_at` is checked.
- Brute-force attempts are slowed by IP rate limiting on `POST /v1/agents/enroll`.

The residual risk is secret handling between machines. If a human pastes an enrollment token into a chat room or CI log, anyone who sees it before it is used may enroll an agent. Short expiry and one-time burn limit the window; they do not make careless secret handling safe.

## 9. Data Flow 4: Signed Claim-Next

After enrollment, the agent does not use Keycloak. It signs a request using its private key.

Canonical string:

```text
METHOD
PATH
SHA256(body)
TIMESTAMP
NONCE
```

Example:

```text
POST
/v1/runs/claim-next
8ec0...body-hash...
2026-05-03T12:00:00Z
nonce_random
```

The server verifies:

1. Headers are present.
2. Timestamp is recent.
3. Agent and key exist and are active.
4. Signature verifies against the stored public key.
5. Nonce has not been used before for this agent.
6. Agent has a grant for the board.
7. A todo task exists and can be claimed atomically.

```text
Agent CLI                         Go API                         SQLite
   │ sign canonical request         │                              │
   ├───────────────────────────────▶│ verify signature             │
   │                                │ insert nonce                 ├──▶ agent_nonces
   │                                │ begin claim tx               │
   │                                │ check board grant            ├──▶ agent_board_grants
   │                                │ select todo task             ├──▶ tasks
   │                                │ insert run                   ├──▶ runs
   │                                │ guarded update task          ├──▶ tasks
   │                                │ insert run token hash        ├──▶ run_tokens
   │                                │ audit claim                  ├──▶ audit_log
   │◀───────────────────────────────┤ task + rt_live token         │
```

The timestamp and nonce protect against replay. The body hash protects against body substitution. The path and method protect against signing one operation and applying the signature to another.

The subtle risk is canonicalization mismatch. If the CLI signs one byte sequence and the server verifies another, valid requests fail. If the server verifies a weaker string than the one actually executed, an attacker may be able to change meaning without changing the signature. That is why `internal/agent/signature.go` is a high-value file for review.

## 10. Data Flow 5: Run Token Mutations

A run token is an opaque bearer token returned after claim. It is not a JWT. The server stores only a hash.

The token row binds authority to exact IDs:

```text
org_id
board_id
task_id
run_id
agent_id
scopes
expires_at
revoked_at
```

Every run-token endpoint must use those IDs as the source of truth.

```go
func PatchTaskStatus(taskIDFromURL string, tokenPrincipal TokenPrincipal, status string) error {
    if taskIDFromURL != tokenPrincipal.TaskID {
        return forbidden
    }

    UPDATE tasks
    SET status = ?
    WHERE id = tokenPrincipal.TaskID
      AND org_id = tokenPrincipal.OrgID
      AND board_id = tokenPrincipal.BoardID
      AND claimed_by_run_id = tokenPrincipal.RunID
}
```

The important lesson is that URL parameters are claims made by the caller. Token rows are facts stored by the server. The code must compare the caller's claim to the server's fact before mutating anything.

Threats and controls:

| Threat | Control |
|---|---|
| Run token used on another task. | Handler compares route `task_id` to token-bound `TaskID`. |
| Run token reused after expiry. | `AuthenticateRunToken` checks `expires_at`. |
| Run token used after revocation. | `AuthenticateRunToken` checks `revoked_at`. |
| Run token used after run completion. | `AuthenticateRunToken` checks run status is `running`. |
| Database reader steals token hashes. | Hashes are not bearer tokens. |

## 11. Threat Table by STRIDE

STRIDE is a simple taxonomy: Spoofing, Tampering, Repudiation, Information disclosure, Denial of service, and Elevation of privilege. It is not perfect, but it gives us a checklist.

| STRIDE | Example in this MVP | Current controls | Remaining work |
|---|---|---|---|
| Spoofing | Attacker pretends to be a human. | Keycloak JWT signature, issuer, expiry, `sub`, `aud`/`azp`. | TLS deployment, refresh-token protection, logout/revocation handling. |
| Spoofing | Attacker pretends to be an agent. | Ed25519 signature verification against active key. | Better CLI key storage; hardware/OS keychain support. |
| Tampering | Attacker changes claim body after signing. | Canonical string includes SHA-256 body hash. | Add more canonicalization tests for query strings if used later. |
| Tampering | Two agents claim same task. | Transaction and guarded SQL update. | Monitor conflict rate; add retry/backoff strategy. |
| Repudiation | Human says they did not revoke an agent. | `audit_log` records `agent.revoked`. | Add request IP/user-agent and audit query/export. |
| Information disclosure | DB reader sees run tokens. | Only token hashes are stored. | Encrypt backups at rest; restrict filesystem access. |
| Information disclosure | CLI config leaked. | File written `0600`. | Move private keys/refresh tokens to keychain or separate encrypted storage. |
| Denial of service | Anonymous clients spam enroll endpoint. | IP token-bucket rate limiting. | Reverse proxy limits, distributed limits if multi-instance. |
| Denial of service | Buggy agent loops claim-next. | Agent-specific claim limit. | Agent backoff policy and server Retry-After handling. |
| Elevation of privilege | Member creates agent. | Owner/admin check in `agent.Service`. | More complete role model and tests for every management endpoint. |
| Elevation of privilege | Agent updates other task. | Run-token task binding. | Continue adding negative tests for every new run-token endpoint. |

## 12. Current Controls in Code

This section ties the abstract model to files the intern can open.

### Keycloak human authentication

File: `internal/auth/jwks.go`

The authenticator verifies that the token is signed by a Keycloak realm key, has the expected issuer, has not expired, and matches the expected audience or authorized party.

Key implementation points:

- JWKS keys are fetched from `issuer + /protocol/openid-connect/certs`.
- Only RS256 is accepted.
- `sub` is required.
- Local users are keyed as `keycloak|<sub>`.

If this file is weakened, every human management endpoint is weakened.

### Agent signature verification

File: `internal/agent/signature.go`

This file defines what the agent signs. The body bytes used for verification are the same bytes later unmarshaled by the handler.

Key implementation points:

- Timestamp must be within the freshness window.
- Agent key must be active.
- Agent must be active.
- Signature must verify.
- Nonce insert must succeed.

If a future endpoint wants signed agent auth, it should reuse this verifier rather than inventing a new signature format.

### Claim-next and run token authorization

File: `internal/runs/runs.go`

This file is the center of the agent security model. It claims tasks, creates runs, creates run tokens, and validates those tokens for later mutation.

Key implementation points:

- `ClaimNext` uses a transaction.
- The task update checks status and `claimed_by_run_id IS NULL`.
- Run tokens are generated as opaque strings and stored as hashes.
- Run-token principals carry server-side `OrgID`, `BoardID`, `TaskID`, `RunID`, and `AgentID`.

If you add a new mutation, bind it to the token principal, not to caller-provided IDs.

### Role enforcement for agent management

File: `internal/agent/agent.go`

Agent creation, enrollment-token creation, and revocation now require `owner` or `admin`.

This is the first role boundary in the MVP. It is intentionally simple, but it establishes the pattern: authenticate first, then authorize based on local membership.

### Rate limiting

Files: `internal/http/ratelimit.go`, `internal/http/handlers.go`

Rate limiting is in-memory and per-process. It protects against local/private-alpha abuse, not distributed attacks.

Current examples:

- `POST /v1/agents/enroll` is IP-limited.
- `POST /v1/runs/claim-next` is IP-limited and then agent-limited.
- Comment and status updates are run-limited.

If the API is deployed behind a reverse proxy, do not trust `X-Forwarded-For` until trusted proxy configuration exists.

### SQLite WAL and backup

File: `internal/storage/sqlite.go`

WAL mode improves read/write behavior, but it changes backup expectations. A running database may have state in `kanban.db-wal`, so backups must use SQLite's backup mechanisms.

The implementation provides:

```go
func (s *Store) Backup(ctx context.Context, path string) error {
    _, err := s.DB.ExecContext(ctx, `VACUUM INTO ?`, path)
    return err
}
```

A backup is not complete until a restore test proves it can be opened and queried.

## 13. What Happens When Something Is Compromised?

A good threat model tells operators what to do when a control fails or a secret leaks.

### If an agent private key leaks

Impact:

- Attacker can sign as that agent.
- Attacker can claim from boards granted to that agent.
- Attacker cannot use Keycloak human endpoints.
- Attacker cannot mutate arbitrary tasks unless they obtain run tokens through claims.

Response:

1. Revoke the agent:
   ```bash
   kanban-agent agent revoke --agent agt_...
   ```
2. Inspect audit log for `run.claim_next`, `task.comment.created`, and `task.status.updated` by that agent.
3. Review tasks claimed by runs from that agent.
4. Rotate/re-enroll if the agent is still needed.

### If a run token leaks

Impact:

- Attacker can mutate only the bound task/run until expiry or revocation.
- Token expires quickly.
- Token cannot claim new tasks.

Response:

1. Revoke the agent if broader machine compromise is suspected.
2. Mark the run failed or complete based on investigation.
3. Review comments/status changes for the bound task.

### If a human refresh token leaks

Impact:

- Attacker may mint new human access tokens.
- Attacker may create/revoke agents if the human is owner/admin.

Response:

1. Revoke the user's Keycloak session/refresh tokens in Keycloak.
2. Review audit log for human actions.
3. Rotate any agents created during the suspected window.
4. Move CLI credentials to a safer storage mechanism before broader rollout.

### If SQLite backup leaks

Impact:

- Attacker sees task content, comments, org membership, public keys, token hashes, and audit events.
- Attacker should not get plaintext enrollment/run tokens from the DB alone.

Response:

1. Treat task data and comments as disclosed.
2. Rotate/revoke agents if backups include sensitive operational history.
3. Confirm no plaintext tokens or private keys were ever stored in SQLite.
4. Encrypt future backups and restrict backup access.

## 14. What Is Out of Scope for This MVP

Not every security feature belongs in the first MVP. Some would make the implementation harder before the product primitive is validated.

Out of scope for now:

- Keycloak users or service accounts per agent.
- Keycloak token exchange for run tokens.
- JWT run tokens.
- DPoP, mTLS, or hardware-bound agent keys.
- OPA/Rego policy engine.
- Multi-instance distributed rate limiting.
- Enterprise SSO policy mapping.
- Customer-by-customer SQLite split.
- Fine-grained billing/admin roles.

These are not bad ideas. They are deferred ideas. The MVP first proves that task-scoped, short-lived, application-native run tokens are the right primitive.

## 15. Security Review Checklist

Use this checklist before merging changes that touch auth, enrollment, claims, tokens, or storage.

### Human auth

- [ ] Does the API still require Keycloak `sub` in Keycloak mode?
- [ ] Does local dev auth remain clearly non-production?
- [ ] Are role checks performed after authentication and before mutation?
- [ ] Do owner/admin-only endpoints have tests for member rejection?

### Agent auth

- [ ] Does the signed request include method, path, body hash, timestamp, and nonce?
- [ ] Does the handler verify the signature over the exact bytes it later parses?
- [ ] Are revoked agents and revoked keys rejected?
- [ ] Is nonce replay rejected?

### Run tokens

- [ ] Are plaintext run tokens never stored?
- [ ] Are token lookups performed by hash?
- [ ] Are task/run mutations bound to token-row IDs?
- [ ] Are expired, revoked, or completed-run tokens rejected?

### Storage and operations

- [ ] Is WAL enabled and tested?
- [ ] Are backups created with `VACUUM INTO` or SQLite backup API?
- [ ] Has a restore test been run?
- [ ] Are audit events written for security-sensitive mutations?

### Abuse resistance

- [ ] Are anonymous endpoints IP-limited?
- [ ] Are signed-agent endpoints limited by IP and by agent after verification?
- [ ] Are run-token mutation endpoints limited by run?
- [ ] Is `Retry-After` returned on 429 responses?

## 16. Implementation Follow-Ups

The next security work should be operational rather than conceptual. The architecture is now clear; the system needs sharper tools around it.

Recommended next tasks:

1. **Move CLI private keys and refresh tokens out of the main JSON config.** Use separate `0600` files first, then OS keychain support where available.
2. **Add audit query/export tooling.** An audit log is only useful if operators can inspect it quickly during an incident.
3. **Add backup restore automation.** A backup job that has never restored is only a backup hope.
4. **Add trusted proxy configuration.** Only then should the API use forwarded IP headers for rate limiting.
5. **Add incident playbooks.** Write short procedures for leaked agent key, leaked run token, leaked human token, and corrupted database.
6. **Add production Keycloak realm guidance.** The local realm is a development convenience, not enterprise SSO policy.

## 17. Closing: The Shape of a Safe MVP

The MVP is safe when every credential has a narrow job. The human token manages application resources. The agent key proves possession by one automation identity. The run token authorizes one short-lived task mutation context. The database records state and evidence, but it does not contain plaintext bearer tokens. The API performs the domain checks that Keycloak cannot know about.

That is the architecture to protect. When adding features, ask where authority comes from, how long it lasts, what resource it is bound to, how it can be revoked, and what audit event proves it was used. If the answer is vague, the feature is not ready. If the answer is concrete, the implementation will usually follow.

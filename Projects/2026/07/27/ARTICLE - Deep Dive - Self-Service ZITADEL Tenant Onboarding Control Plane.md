---
title: "Deep Dive: Self-Service ZITADEL Tenant Onboarding Control Plane"
aliases:
  - ZITADEL SaaS Onboarding Deep Dive
  - Tenant Control Plane Architecture
  - Subscription Tenant Onboarding Project Report
tags:
  - article
  - deep-dive
  - go
  - zitadel
  - oidc
  - postgresql
  - multitenancy
  - security
  - architecture
status: active
type: article
created: 2026-07-27
analyzed: 2026-07-27
repo: /home/manuel/code/wesen/2026-07-25--zitadel-go-test
repository: git@github.com:wesen/2026-07-25--zitadel-go-test.git
repository_commit: 0f7ea0e55819a5e84e8048a0486609d524a1730a
implementation_commit: 77e4efda621b3371ddb7cccbd2565c1cc24221f0
repository_date: 2026-07-27
go_module: github.com/wesen/zitadel-go-test
binary: tenant-control-plane
ticket: ZITADEL-007-SAAS-ONBOARDING
related_files:
  - /home/manuel/code/wesen/2026-07-25--zitadel-go-test/cmd/tenant-control-plane/serve.go
  - /home/manuel/code/wesen/2026-07-25--zitadel-go-test/internal/onboarding/model.go
  - /home/manuel/code/wesen/2026-07-25--zitadel-go-test/internal/onboarding/service.go
  - /home/manuel/code/wesen/2026-07-25--zitadel-go-test/internal/onboarding/oidc.go
  - /home/manuel/code/wesen/2026-07-25--zitadel-go-test/internal/onboarding/worker.go
  - /home/manuel/code/wesen/2026-07-25--zitadel-go-test/internal/onboarding/httpapp/app.go
  - /home/manuel/code/wesen/2026-07-25--zitadel-go-test/internal/onboarding/postgres/migrations/001_initial.sql
  - /home/manuel/code/wesen/2026-07-25--zitadel-go-test/internal/onboarding/postgres/leases.go
  - /home/manuel/code/wesen/2026-07-25--zitadel-go-test/internal/onboarding/zitadel/organizations.go
  - /home/manuel/code/wesen/2026-07-25--zitadel-go-test/infra/zitadel/local/main.tf
  - /home/manuel/code/wesen/2026-07-25--zitadel-go-test/compose.yaml
  - /home/manuel/code/wesen/2026-07-25--zitadel-go-test/ttmp/2026/07/26/ZITADEL-007-SAAS-ONBOARDING--design-self-service-subscription-tenant-onboarding-and-delegated-customer-administration/design-doc/01-self-service-saas-tenant-onboarding-analysis-design-and-implementation-guide.md
related_notes:
  - "[[01 - Project Architecture Overview]]"
  - "[[02 - External Identity and Local Projection]]"
  - "[[05 - Defense in Depth Tenant Isolation]]"
  - "[[06 - Vault GitOps and Immutable Delivery]]"
  - "[[07 - Acceptance as Architecture Evidence]]"
  - "[[10 - PostgreSQL Backed OIDC Session Follow-up]]"
---

# Deep Dive: Self-Service ZITADEL Tenant Onboarding Control Plane

This article analyzes the implementation of a self-service SaaS tenant onboarding control plane in the `zitadel-go-test` repository. The control plane converts an organization request into a durable identity lifecycle: it records the request, creates an isolated ZITADEL organization, starts organization-scoped hosted registration, verifies the returned identity, maintains server-side browser state, and cleans up abandoned resources. Later phases will add subscription confirmation and tenant runtime provisioning, but the current implementation establishes the security and persistence contracts on which those phases depend.

The analysis is grounded in repository commit `0f7ea0e55819a5e84e8048a0486609d524a1730a`. The main implementation landed in `77e4efda621b3371ddb7cccbd2565c1cc24221f0`. A subsequent live acceptance session discovered an incompatibility between caller-supplied UUID organization IDs and Login V2 v4.16.1. The corrective generated-ID design was present as uncommitted work when this report was written, so this article distinguishes committed behavior from verified work in progress.

> [!summary]
> - The control plane is a separate Go binary with server-rendered HTML, a narrow ZITADEL adapter, and PostgreSQL as the lifecycle store, session store, one-time OIDC-flow store, and worker queue.
> - State transitions, OIDC callback claims, request idempotency, provisioning leases, and cleanup leases are database operations with explicit concurrency semantics.
> - Rich OIDC state remains server-side. Browser cookies contain signed CSRF state, signed pending-onboarding ownership, or a random opaque session identifier.
> - Live acceptance proved organization creation, registration-policy convergence, organization-scoped Login V2 registration, and resource-owner enforcement. It also proved that custom UUID organization IDs are unsafe for Login V2 and that password self-registration can return an unverified identity without sending the expected local challenge.
> - The implementation is active, not complete. Generated numeric organization IDs and an explicit ZITADEL-owned email-verification continuation must be finished and revalidated before Phase 2 can be closed.

## The project objective

The earlier TODO application proved individual platform capabilities: hosted ZITADEL authentication, email verification and recovery, Stripe subscription projection, PostgreSQL persistence, Vault-backed secrets, GitOps deployment, and tenant isolation. It also proved a manual two-tenant model using Alpha and Beta organizations. Each tenant had a separate ZITADEL organization, project, OIDC client, Kubernetes namespace, Vault path, database role, database, hostname, and cryptographic keys.

That experiment did not provide a public customer journey. An operator created each organization, identity application, secret record, database, and Argo CD Application. The next system needs to accept a customer request and coordinate these independent control planes without collapsing their authority boundaries.

The customer-facing sequence is:

1. A prospective customer enters an organization name, stable tenant slug, and administrator email.
2. The system creates a pending ZITADEL organization.
3. The administrator registers through hosted ZITADEL Login V2 in that organization.
4. The callback is accepted only when issuer, audience, state, nonce, PKCE, verified email, requested email, subject, and resource-owning organization all agree.
5. A later phase creates Stripe Checkout from a server-controlled plan.
6. A signed Stripe webhook advances the commercial state.
7. A resumable worker provisions identity application resources, Vault records, a database, and a GitOps declaration.
8. Activation waits for the expected Git merge revision, Argo CD health, TLS, readiness, and authorization acceptance.

Phases 1 and 2 implement the durable control-plane foundation and initial identity onboarding. They deliberately do not implement payment or workload provisioning yet.

## Product boundaries before code

The design starts by defining the entities that the system manages. A **customer** is a business with one subscription. A **tenant** is the customer's isolated application and identity boundary. The **initial administrator** is the first verified human who will eventually receive organization-scoped administration. A **tenant user** is a person owned by the customer's ZITADEL organization. An independently isolated downstream business is not a tenant user; it requires another organization, another billing relationship, and another runtime boundary.

This distinction keeps the first implementation focused. The control plane supports one direct customer organization with multiple users. It does not implement reseller hierarchies, nested tenant ownership, marketplace payouts, customer-defined prices, a general workflow engine, a Kubernetes operator, or an ApplicationSet.

The runtime also remains separate from onboarding. The TODO application does not gain organization-creation authority. The control plane receives a dedicated privileged identity, while tenant applications continue to receive only runtime credentials for their own organization, database, and Vault paths.

## System architecture

The implementation adds a second binary to the existing repository:

```text
cmd/tenant-control-plane/
    main.go
    serve.go
    inspect.go
    healthcheck.go

internal/onboarding/
    model.go
    store.go
    service.go
    oidc.go
    worker.go

internal/onboarding/httpapp/
    app.go
    cookies.go
    templates.go
    templates/*.html
    static/control.css

internal/onboarding/postgres/
    store.go
    migrations.go
    migrations/*.sql
    onboardings.go
    auth.go
    leases.go

internal/onboarding/zitadel/
    organizations.go
```

The binary runs two loops in one process. The HTTP loop serves public onboarding, status, callback, liveness, and readiness routes. The worker loop removes expired OIDC flows and sessions and reconciles expired pending organizations. PostgreSQL coordinates both loops.

```mermaid
flowchart TD
    B[Browser] --> HTTP[tenant-control-plane HTTP server]
    HTTP --> SVC[onboarding.Service]
    HTTP --> OIDC[OIDC authenticator]
    SVC --> DB[(Control-plane PostgreSQL)]
    SVC --> ZP[ZITADEL provisioner]
    OIDC --> ZL[ZITADEL Login V2 and OIDC endpoints]
    ZP --> ZA[ZITADEL Organization and Management APIs]
    W[Cleanup worker] --> DB
    W --> ZP

    DB --> STATE[Onboarding state]
    DB --> FLOW[One-time OIDC flows]
    DB --> SESSION[Opaque browser sessions]
    DB --> AUDIT[Sanitized audit events]
    DB --> LEASE[Worker leases]
```

No Redis, message broker, or workflow engine participates in the current path. The expected onboarding volume is low, every job belongs to one durable onboarding row, and PostgreSQL already exists in the deployment. Adding another queue would increase operational state without improving the current concurrency model.

## The lifecycle model

The domain model separates three dimensions that are related but not interchangeable.

The onboarding state describes technical progress:

```text
draft
  → organization_created
  → administrator_verified
  → checkout_pending
  → subscription_confirmed
  → provisioning
  → awaiting_gitops_merge
  → activating
  → active
```

Abandoned records move through:

```text
pending state → expiring → expired
```

The subscription state records commercial truth:

```text
none | trialing | active | past_due | canceled | unpaid
```

The access state records whether the customer may use the tenant:

```text
pending | enabled | grace | suspended | archived
```

This separation prevents a billing event from rewriting provisioning history. A canceled subscription does not imply that a database was never created. A failed deployment does not imply that Stripe did not confirm payment. A cleanup action does not silently erase the commercial record.

The transition table lives in `internal/onboarding/model.go`. The store checks it before issuing a database update. The database update then checks the expected state again:

```sql
UPDATE tenant_onboardings
SET state = $next,
    updated_at = now(),
    last_error_code = NULL,
    last_error_at = NULL
WHERE id = $id
  AND state = $expected
RETURNING ...;
```

A zero-row result is `ErrStateConflict`. The caller reloads the record rather than assuming that its stale transition should still apply.

## The PostgreSQL schema

The control-plane schema has its own embedded migration ledger and advisory lock. It does not share the TODO application's migration namespace. The initial schema creates four primary structures.

### Tenant onboarding rows

`tenant_onboardings` stores the internal UUID, tenant slug, display name, requested administrator email, lifecycle dimensions, ZITADEL identifiers, administrator identity, expiry, cleanup status, lease ownership, sanitized error code, and timestamps.

The schema enforces several invariants directly:

- Tenant slugs match a lowercase, bounded pattern.
- Requested email is normalized before storage.
- Every state belongs to an explicit check constraint.
- Issuer and subject are both null or both present.
- A verified timestamp cannot exist without a subject.
- ZITADEL organization IDs are unique when present.
- Administrator identities are unique through a partial index on `(issuer, subject)`.

The application still validates input before executing SQL. Database constraints are the final protection against concurrent writers and programming errors.

### OIDC flow rows

`onboarding_oidc_flows` stores:

```text
state_hash
onboarding_id
nonce
code_verifier
expires_at
consumed_at
created_at
```

The raw state is never stored. The browser receives a random 32-byte base64url value, while PostgreSQL receives its SHA-256 hash. The nonce and PKCE verifier remain server-side. A callback claims the flow with one atomic update:

```sql
UPDATE onboarding_oidc_flows
SET consumed_at = $now
WHERE state_hash = $hash
  AND consumed_at IS NULL
  AND expires_at > $now
RETURNING ...;
```

The update gives callback replay a precise meaning. The first valid callback obtains the row. Every later callback receives `ErrFlowConsumed`. An unknown or expired state receives `ErrFlowNotFound`.

### Session rows

`onboarding_sessions` stores a SHA-256 hash of the random browser session identifier, the onboarding UUID, issuer, subject, and expiry. The cookie itself is 43 base64url characters representing 32 random bytes. It does not contain an ID token, access token, user profile, email address, organization identifier, or serialized OIDC context.

This model follows the server-side session pattern already proven in the tenant TODO deployments. A browser cookie remains small, pod replacement does not destroy authentication state, and session revocation is a row deletion.

### Audit rows

`onboarding_audit_events` records internal UUID, onboarding UUID, actor type, action, result, sanitized JSON details, and timestamp. The service rejects detail keys that appear to contain email or token values. Raw callback query strings, cookies, invitation links, verification codes, Stripe payloads, and Vault values are outside the audit contract.

## Idempotent public requests

The initial organization form has two independent security requirements: the POST must originate from the browser that received the form, and retrying the same form must not create another organization.

CSRF uses a random cookie value plus HMAC. The form receives the raw token, and the browser cookie receives the token with its signature. The POST compares the form and cookie in constant time.

Request idempotency uses a separate signed form token. The server generates a random value, signs it for the `form` purpose, and places it in a hidden field. On POST, the server verifies the signature, hashes the raw value, and stores the hash in `request_key_hash`. A unique database constraint ensures that two concurrent submissions of the same form produce one onboarding row.

The service handles the uniqueness result explicitly:

```pseudo
created = store.CreateOnboarding(requestHash, normalizedInput)
if created failed with request conflict:
    created = store.GetOnboardingByRequestKey(requestHash)

if created.state is not draft:
    return created

organization = provider.EnsureOrganization(created.correlation, created.name)
store.MarkOrganizationCreated(created.id, organization.id)
```

This is not a general idempotency framework. It is one narrow mechanism around the one public operation that can create a privileged external resource.

## OIDC below the high-level middleware

The existing TODO application uses ZITADEL's high-level authentication middleware because its organization scope is static for one deployment. The onboarding application cannot do that. Every pending customer has a different organization, so every authorization request needs a different scope:

```text
urn:zitadel:iam:org:id:<pending-organization-id>
```

The implementation therefore uses lower-level relying-party primitives from `github.com/zitadel/oidc/v3/pkg/client/rp`.

The request path is:

```pseudo
onboarding = store.Get(id)
require onboarding.state == organization_created
require onboarding.expires_at > now

state = random(32 bytes)
nonce = random(32 bytes)
verifier = random(32 bytes)
challenge = SHA256(verifier)

store.CreateOIDCFlow(hash(state), onboarding.id, nonce, verifier, expiry)

redirect authorize(
    state = state,
    nonce = nonce,
    code_challenge = challenge,
    code_challenge_method = S256,
    prompt = create,
    scope = [openid, profile, email, organization scope]
)
```

The callback path is:

```pseudo
flow = store.ConsumeOIDCFlow(hash(query.state))
onboarding = store.Get(flow.onboarding_id)

context.nonce = flow.nonce
tokens = OIDC.CodeExchange(query.code, code_verifier = flow.verifier)
userinfo = OIDC.UserInfo(tokens.access_token)

require userinfo.issuer == configured issuer
require token audience contains dedicated client
require userinfo.resource_owner == onboarding.organization_id
require normalize(userinfo.email) == onboarding.requested_email
require userinfo.email_verified == true
require userinfo.subject is nonempty

onboarding = store.BindAdministrator(issuer, subject)
session = random(32 bytes)
store.CreateSession(hash(session), onboarding.id, issuer, subject)
set opaque session cookie
```

Issuer and audience validation happen inside the OIDC verifier. Nonce validation receives the stored nonce through a typed context value used by the verifier callback. PKCE verification uses the server-stored verifier. Organization and email checks happen after UserInfo and before any administrator projection.

The one-time flow is consumed before token exchange. This makes replay behavior strict: a transient token-endpoint failure requires a new registration attempt rather than allowing the same authorization response to be exchanged repeatedly. The user experience cost is acceptable for a privileged initial-administrator flow, but it is a review-critical decision.

## Identity remains `(issuer, subject)`

Email is used for onboarding correlation and verification. It is not the administrator's identity key.

The stable key is:

```text
(issuer, subject)
```

The requested email must equal the normalized verified email returned by ZITADEL, but changing the email later does not create a new local identity. This follows the same contract as the TODO application and prevents account reassignment when email addresses are renamed or recycled.

The database adds a partial unique index over `(administrator_issuer, administrator_subject)`. In the current product model, one administrator cannot bind the same external identity to multiple pending tenant records. Supporting one person who owns multiple tenants would require an explicit account-to-tenant membership table rather than removing the uniqueness constraint casually.

## The ZITADEL provisioning identity

Terraform creates a dedicated machine user for tenant organization lifecycle. It receives `IAM_ORG_MANAGER`, not `IAM_OWNER`. The role is instance-scoped because creating a new organization cannot be authorized by a role inside an organization that does not exist yet.

The service identity is distinct from:

- the public PKCE browser client;
- tenant TODO runtime clients;
- customer administrators;
- database-bootstrap service accounts;
- Vault runtime identities;
- the local Terraform System API bootstrap identity.

The local machine key is generated by Terraform and written by `scripts/configure-local-zitadel.sh` to ignored `.local/tenant-control-plane/zitadel-key.json` with mode `0600`. Compose runs the distroless process as the local non-root UID so it can read that bind-mounted file without making it world-readable. Production is expected to inject the credential through Vault Secrets Operator rather than reproduce the local ownership bridge.

## Organization creation and policy convergence

Creating a ZITADEL organization is not sufficient for hosted self-registration. The organization must also have a login policy that permits registration and local authentication.

The adapter uses Organization Service v2 to create, list, and delete organizations. It uses the Management Service with explicit `x-zitadel-orgid` metadata to inspect and converge the organization's custom login policy.

The desired policy enables:

- username/password authentication;
- self-registration;
- passkeys;
- email login;
- password reset;

It disables:

- external identity providers for the initial controlled flow;
- phone login;
- domain discovery;
- forced MFA during initial acceptance.

The API adapter is read-before-create. On retry, it reads the organization and validates the correlation before issuing another create operation. On cleanup, `NotFound` is success.

## Live discovery: UUID organization IDs are incompatible with Login V2

The first implementation used a caller-supplied UUID organization ID. Organization Service v2 explicitly allows an optional `organization_id`, and its protobuf documentation includes UUID-shaped examples. Persisting the desired UUID before the API call appeared to provide ideal crash recovery: a retry could read exactly that ID and distinguish the intended organization from every other organization.

The Organization API accepted the UUID. The control-plane status advanced to `organization_created`. The authorization request carried the correct scope:

```text
urn:zitadel:iam:org:id:48ba73ca-0825-4683-8c9b-820a04c8c467
```

Login V2 v4.16.1 then rendered its registration URL with:

```text
organization=48
```

The value `48` is the numeric prefix of `48ba73ca-...`. The resulting user was created in the default `ZITADEL` organization rather than the pending customer organization. The control plane correctly rejected the callback because the resource-owner claim did not match.

This result changes the idempotency design. The API contract permits a string identifier, but the hosted UI behaves as though the value must be numeric. The correction is:

1. Generate a stable correlation UUID in PostgreSQL.
2. Derive a globally unique ZITADEL organization name such as `Customer Name [2d0ee95b]`.
3. Call `AddOrganization` without supplying an ID.
4. Persist ZITADEL's generated numeric ID in the guarded `draft → organization_created` update.
5. On crash recovery, search by the exact correlated name.
6. Use the generated numeric ID in the OIDC organization scope.

A second live attempt with the generated-ID correction produced a numeric organization ID. Login V2 retained the full organization ID, and the new user's `resource_owner` matched the pending customer organization.

> [!warning] API compatibility boundary
> A value accepted by a resource API is not necessarily accepted by every UI and protocol path that consumes it. Organization identifiers must be tested through the complete hosted registration path, not only through `AddOrganization` and `ListOrganizations`.

## Live discovery: self-registration returned an unverified identity

The corrected generated-ID flow reached the control-plane callback with the correct resource owner. The user was still rejected because `email_verified` was false. Local Mailpit contained no verification message.

This behavior matches a documented Login V2 self-registration defect previously observed with v4.15.3. Upgrading the local stack to ZITADEL and Login V2 v4.16.1 corrected organization parsing for generated IDs but did not cause password self-registration to send the expected verification challenge.

The security gate must remain. Accepting an unverified email would allow a user to claim an address they do not control and become the initial administrator for the tenant request.

The planned continuation keeps verification inside ZITADEL:

```mermaid
sequenceDiagram
    participant B as Browser
    participant C as Control plane
    participant Z as ZITADEL Login and User API
    participant M as Mail provider

    B->>Z: Organization-scoped prompt=create
    Z-->>C: OIDC callback with email_verified=false
    C->>C: Validate issuer, subject, requested email, and organization
    C->>C: Persist pending issuer and subject
    C->>Z: SendEmailCode for the user
    Z->>M: Verification challenge
    M-->>B: ZITADEL verification link
    B->>Z: Complete hosted verification
    B->>C: Resume organization-scoped login
    Z-->>C: OIDC callback with email_verified=true
    C->>C: Bind administrator and create opaque session
```

The application must not request a returned verification code. User Service v2 exposes a oneof that can either send or return a code. The provider adapter must select `SendEmailCode` so the secret challenge travels from ZITADEL to the mail provider, never through application storage, browser status JSON, logs, or evidence files.

This continuation was not complete when the report snapshot was taken. The pending migration adds fields for a candidate issuer, candidate subject, and verification-request timestamp, but the HTTP and provider paths still require implementation and acceptance.

## Cleanup as a leased external operation

Pending organizations expire. Cleanup cannot be a plain `DELETE FROM tenant_onboardings` because ZITADEL remains authoritative for the external organization and its users.

The worker claims one expired record with `FOR UPDATE SKIP LOCKED`:

```sql
WITH candidate AS (
    SELECT id
    FROM tenant_onboardings
    WHERE state IN (
        'draft',
        'organization_created',
        'administrator_verified',
        'checkout_pending',
        'expiring'
    )
      AND expires_at <= $now
      AND (lease_expires_at IS NULL OR lease_expires_at <= $now)
    ORDER BY expires_at, id
    FOR UPDATE SKIP LOCKED
    LIMIT 1
)
UPDATE tenant_onboardings AS onboarding
SET state = 'expiring',
    lease_token = $token,
    lease_expires_at = $lease_expiry
FROM candidate
WHERE onboarding.id = candidate.id
RETURNING ...;
```

The worker deletes the ZITADEL organization and completes cleanup only if it still owns the lease. If the provider call fails, it releases the lease with `organization_delete_failed`. The `expiring` state remains reclaimable so a transient provider error does not create a permanent dead end.

A draft may exist before the external organization ID is persisted. The generated-ID correction therefore allows cleanup to resolve by the stable correlated organization name when the numeric ID is absent. This closes the crash window between successful API creation and successful database update.

## HTTP surface and browser security

The HTTP surface is intentionally small:

```text
GET  /                         product page
GET  /onboarding/new           organization request form
POST /onboarding               idempotent organization creation
GET  /onboarding/{id}          protected status page
GET  /onboarding/{id}/signup   organization-scoped OIDC start
GET  /auth/callback            one-time OIDC callback
POST /logout                   session deletion
GET  /livez                    process liveness
GET  /readyz                   PostgreSQL readiness
GET  /static/*                 embedded assets
```

A pending status page is not public merely because its UUID is difficult to guess. Access requires either a signed pending-onboarding cookie matching the route UUID or a valid server-backed administrator session bound to that UUID. A request for another onboarding returns 404, not 403, so the endpoint does not confirm whether the peer UUID exists.

Browser responses include:

```text
Content-Security-Policy
Referrer-Policy: no-referrer
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
Permissions-Policy: camera=(), microphone=(), geolocation=()
Cache-Control: no-store
```

POST bodies are bounded before form parsing. CSRF is required for onboarding creation and logout. Cookies are `HttpOnly`, `SameSite=Lax`, and `Secure` when the public URL is HTTPS.

The UI is rendered from embedded Go templates. It contains a product page, an organization form, and a stable progress timeline. The browser never receives a service credential, database URL, ZITADEL machine key, OIDC verifier, nonce, or raw audit event.

## Operator visibility without PII

The Glazed `inspect` command reads one onboarding by internal UUID and emits structured fields suitable for JSON, YAML, CSV, or table output:

```text
id
slug
state
subscription_state
access_state
expires_at
last_error_code
created_at
updated_at
```

It does not emit the requested email, administrator email, subject, session identifier, flow state, nonce, PKCE verifier, service key, or organization credential.

This separation matters operationally. The browser status page provides customer-safe phases. The inspect command provides operator state. PostgreSQL retains the full correlation record. Logs retain only internal UUIDs and bounded error codes.

## Test architecture

The implementation combines pure unit tests, HTTP tests with in-memory stores, provider adapter tests with generated gRPC interfaces, and live PostgreSQL integration tests.

### State and service tests

`internal/onboarding/model_test.go` verifies permitted and rejected transitions. `service_test.go` verifies:

- repeated form submission returns the same onboarding;
- provider failure leaves a retryable draft;
- registration flow replay is rejected;
- unverified email is rejected;
- wrong organization is rejected;
- wrong requested email is rejected;
- a successful identity produces a server-backed session;
- cleanup failure releases its lease and a later retry completes.

### HTTP tests

`internal/onboarding/httpapp/app_test.go` runs the real HTTP handler through `httptest.Server`. It verifies:

- security headers;
- CSRF rejection;
- organization creation redirect;
- pending status rendering;
- cross-onboarding 404;
- OIDC start redirect;
- successful callback session;
- callback replay 401;
- wrong organization 403;
- unverified email 403;
- liveness and readiness;
- 43-character opaque session cookies backed by a SHA-256 database key.

### Provider tests

`internal/onboarding/zitadel/organizations_test.go` verifies create, read-before-create, correlation mismatch, `AlreadyExists` recovery, idempotent `NotFound` deletion, organization-scoped policy metadata, and policy convergence.

### PostgreSQL integration tests

The integration suite creates real rows in a temporary PostgreSQL database and verifies:

- migrations can run twice;
- expected-state guards;
- request-key and slug uniqueness;
- administrator identity uniqueness;
- eight concurrent OIDC flow consumers produce one winner;
- active and expired sessions;
- one worker claim at a time;
- expired lease reclamation;
- stale worker completion rejection;
- cleanup token ownership.

The full validation run recreated the test database and executed:

```bash
TEST_DATABASE_URL='postgres://postgres:postgres@127.0.0.1:5433/onboarding_test?sslmode=disable' \
  go test -race ./... -count=1

go vet ./...
CGO_ENABLED=0 go build ./...
terraform -chdir=infra/zitadel/local validate
docker compose --env-file .env.example config --quiet
bash -n scripts/configure-local-zitadel.sh
```

These commands passed for commit `77e4efd`. The generated-ID correction passed targeted onboarding tests after a fresh database migration, but the final full-suite audit remains outstanding.

## Failures that changed the design

The implementation history contains several failures worth preserving because each exposed a boundary that unit design alone did not establish.

### Generated ZITADEL API dependencies

Importing Organization Service v2 activated generated protobuf dependencies that were absent from `go.sum`:

```text
missing go.sum entry for module providing package github.com/envoyproxy/protoc-gen-validate/validate
```

`go mod tidy` added checksums for the pinned dependency graph. No generated source was copied into the project.

### Static binary versus interactive Glazed help

Adding Glazed's interactive help system pulled in Bubble Tea and `go-sqlite3`. The production binary is built with `CGO_ENABLED=0` and runs in a distroless static image. The interactive help subsystem was removed from this server binary while retaining Glazed command definitions, environment decoding, logging, and structured output.

This is a deliberate binary boundary, not an incomplete command migration.

### Local key permissions

The local service key was generated with mode `0600`. The distroless image runs as its built-in non-root UID, which could not read a bind-mounted file owned by the host user:

```text
read ZITADEL service key: open /run/secrets/tenant-provisioner-key.json: permission denied
```

Changing the key to `0644` would have weakened the local secret boundary. Compose instead runs the local container as the host non-root UID. Production will use Vault injection and does not inherit this local bridge.

### Missing public URL configuration

The first Compose start failed with:

```text
database-url, public-url, zitadel-issuer, zitadel-client-id, and a 32-byte browser-key are required
```

The bootstrap script wrote the dedicated client ID and browser key but omitted `TENANT_CONTROL_PLANE_PUBLIC_URL`. The Compose manifest now has a local default, and the script writes the explicit value into ignored `.env`.

### Login V2 custom-ID truncation

The UUID organization scope passed API-level tests and failed only in hosted registration. This failure caused the generated numeric ID redesign described above.

### Login V2 email verification gap

The corrected organization-scoped user was created in the right organization and still returned `email_verified=false` without a Mailpit message. This failure caused the explicit ZITADEL `SendEmailCode` continuation design. The control-plane gate remained intact.

## Deployment shape

The Dockerfile builds both `todo-demo` and `tenant-control-plane` with `CGO_ENABLED=0`, copies them into a distroless non-root image, and selects the command through Compose entrypoint configuration.

The local control-plane service receives:

```text
TENANT_CONTROL_PLANE_DATABASE_URL
TENANT_CONTROL_PLANE_PUBLIC_URL
TENANT_CONTROL_PLANE_ZITADEL_ISSUER
TENANT_CONTROL_PLANE_ZITADEL_CLIENT_ID
TENANT_CONTROL_PLANE_ZITADEL_SERVICE_KEY_FILE
TENANT_CONTROL_PLANE_BROWSER_KEY
TENANT_CONTROL_PLANE_PENDING_LIFETIME
TENANT_CONTROL_PLANE_WORKER_INTERVAL
TENANT_CONTROL_PLANE_WORKER_LEASE_DURATION
```

PostgreSQL has a separate `zitadel_tenant_control_plane` database. The service key is mounted read-only. The container has a native healthcheck. ZITADEL API, Login V2, PostgreSQL, Mailpit, Traefik, TODO, and the control plane run as separate services.

Production deployment has not been added yet. The intended production shape preserves existing boundaries:

- Terraform creates the long-lived control-plane service identity and public OIDC client.
- Vault stores the service key and browser cryptographic key.
- Vault Secrets Operator injects runtime values.
- Git declares the Deployment, Service, Ingress, NetworkPolicy, VaultAuth, and VaultStaticSecret.
- The container remains immutable, non-root, and distroless.
- Customer-specific runtime provisioning remains a later phase gated by signed subscription evidence.

## Current implementation status

Phase 1 is substantially implemented:

- The binary, server-rendered UI, health routes, schema, migrations, sessions, CSRF, state machine, leases, audit boundary, cleanup worker, operator inspection, Compose runtime, Terraform identity, and broad test suite exist.
- Fresh PostgreSQL race tests, vet, static build, Terraform validation, and Compose validation passed at the committed implementation checkpoint.
- Live local health and readiness returned HTTP 200.

Phase 2 is partially accepted:

- Real ZITADEL organization creation passed.
- Registration policy convergence passed.
- Organization-scoped `prompt=create` reached Login V2.
- Generated numeric organization IDs produced the correct user resource owner.
- Wrong resource owner and unverified email were denied.

Phase 2 is not complete:

- The generated numeric ID correction must be committed after final tests.
- The explicit email-verification request and resume flow must be implemented.
- A complete verified callback must create the local opaque session.
- Callback replay, wrong organization, wrong email, and duplicate subject must be rerun against the completed path.
- Acceptance fixtures, users, organizations, sessions, and temporary passwords must be removed.
- PostgreSQL-backed rate limiting must be added before public exposure.
- Desktop and mobile screenshots must be reviewed after rebuilding the favicon correction.
- The full repository validation and secret/PII audit must be rerun.

## File-by-file reading order

An engineer reviewing or continuing the project should read in this order.

1. `internal/onboarding/model.go` defines the vocabulary and legal transitions.
2. `internal/onboarding/postgres/migrations/001_initial.sql` shows what durability and uniqueness mean physically.
3. `internal/onboarding/store.go` defines the complete persistence boundary.
4. `internal/onboarding/service.go` coordinates form idempotency, organization creation, OIDC flows, identity checks, and sessions.
5. `internal/onboarding/oidc.go` constructs dynamic organization-scoped requests and performs token exchange.
6. `internal/onboarding/zitadel/organizations.go` owns privileged API calls and policy convergence.
7. `internal/onboarding/postgres/leases.go` defines worker concurrency and cleanup ownership.
8. `internal/onboarding/worker.go` reconciles expiration without deleting local history blindly.
9. `internal/onboarding/httpapp/app.go` maps browser requests onto service operations and status pages.
10. `cmd/tenant-control-plane/serve.go` composes configuration, storage, provider clients, HTTP, worker, and graceful shutdown.
11. `infra/zitadel/local/main.tf` shows the dedicated public and privileged identities.
12. `compose.yaml` shows the local runtime and secret mount boundary.

## Stable engineering rules from this work

- Identity is `(issuer, subject)`. Email is a verified attribute and onboarding correlation value.
- An organization claim is validated before any local administrator projection.
- State, nonce, and PKCE are all required. They solve different protocol threats.
- Rich authentication state belongs in PostgreSQL. Browser cookies remain opaque and bounded.
- Public POST idempotency is enforced by a unique database key, not by process memory.
- Every external create operation needs a durable correlation value established before the call.
- Every destructive cleanup operation needs a lease and idempotent `NotFound` behavior.
- A provider API test does not replace a hosted UI acceptance test.
- Credentials, verification codes, invitation URLs, cookies, callback codes, and raw webhook bodies do not belong in logs or evidence.
- Customer administrators receive organization roles only. The provisioning service receives the narrow instance role required to create organizations and remains separate from customer and runtime identities.
- Billing, provisioning, and access are independent state dimensions.
- Git owns nonsecret desired state. Vault owns credentials. ZITADEL owns passwords, factors, recovery, and verification challenges.

## Next implementation sequence

The next slice should complete email verification without weakening the callback gate.

1. Finish migration fields for pending administrator issuer, subject, and verification-request timestamp.
2. Add an atomic store operation that records the unverified candidate only after issuer, subject, requested email, and organization checks pass.
3. Extend the ZITADEL adapter with User Service v2 `SendEmailCode` using the send-code branch, never the return-code branch.
4. Redirect the unverified callback to a customer-safe status page instead of returning an unrecoverable 403.
5. Add a CSRF-protected resend operation with bounded retry and rate limits.
6. Restart organization-scoped OIDC without `prompt=create` after the user completes ZITADEL verification.
7. Require the verified callback identity to equal the persisted pending issuer and subject.
8. Bind `(issuer, subject)` and create the opaque server-backed session.
9. Run live positive and negative acceptance on v4.16.1.
10. Remove every fixture and preserve only sanitized evidence.

Only after this sequence passes should the implementation move to Stripe Checkout and subscription-confirmed provisioning.

## Closing assessment

The control plane has moved beyond a design document. It has a separate executable boundary, a durable data model, explicit concurrency semantics, a server-rendered interface, a least-privilege provisioning identity, low-level OIDC protocol handling, real provider integration, and live acceptance evidence.

The live tests also prevented two unsafe conclusions. First, a UUID accepted by Organization Service v2 was not safe for Login V2 organization routing. Second, successful password self-registration did not establish verified email ownership. In both cases the control plane's local checks rejected the result instead of adapting by weakening identity policy.

The remaining work is focused. The system must finish the ZITADEL-owned email-verification continuation, rerun the complete acceptance matrix, clean fixtures, and validate the final diff. Once those requirements pass, Phase 1 and Phase 2 will provide a reliable identity foundation for subscription-driven tenant provisioning.

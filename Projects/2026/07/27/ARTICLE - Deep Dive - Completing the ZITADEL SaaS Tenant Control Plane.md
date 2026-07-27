---
title: "Deep Dive: Completing the ZITADEL SaaS Tenant Control Plane"
aliases:
  - ZITADEL Tenant Control Plane Completion Report
  - Verified SaaS Administrator Onboarding
  - PostgreSQL Coordinated ZITADEL Onboarding
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
status: complete
type: article
created: 2026-07-27
analyzed: 2026-07-27
repo: /home/manuel/code/wesen/2026-07-25--zitadel-go-test
repository: git@github.com:wesen/2026-07-25--zitadel-go-test.git
repository_commit: f119d6d1c5ea3ed79b1a560a899159e61e18ee15
implementation_commits:
  - 30e74c362f5b09f0799de8c3f6ce72a7095b366d
  - 7947a39fb1404f09c9314fc99da6bfd61f15db27
evidence_commit: b581d3c698cf415f4083d15193bde6ce6339bf7b
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
  - /home/manuel/code/wesen/2026-07-25--zitadel-go-test/internal/onboarding/postgres/onboardings.go
  - /home/manuel/code/wesen/2026-07-25--zitadel-go-test/internal/onboarding/postgres/leases.go
  - /home/manuel/code/wesen/2026-07-25--zitadel-go-test/internal/onboarding/postgres/rate_limits.go
  - /home/manuel/code/wesen/2026-07-25--zitadel-go-test/internal/onboarding/zitadel/organizations.go
  - /home/manuel/code/wesen/2026-07-25--zitadel-go-test/infra/zitadel/local/main.tf
  - /home/manuel/code/wesen/2026-07-25--zitadel-go-test/compose.yaml
related_notes:
  - "[[ARTICLE - Deep Dive - Self-Service ZITADEL Tenant Onboarding Control Plane]]"
  - "[[01 - Project Architecture Overview]]"
  - "[[02 - External Identity and Local Projection]]"
  - "[[05 - Defense in Depth Tenant Isolation]]"
  - "[[06 - Vault GitOps and Immutable Delivery]]"
  - "[[07 - Acceptance as Architecture Evidence]]"
  - "[[10 - PostgreSQL Backed OIDC Session Follow-up]]"
---

# Deep Dive: Completing the ZITADEL SaaS Tenant Control Plane

A self-service SaaS onboarding system must establish a new tenant identity boundary without granting the public application broad identity authority, accepting an unverified administrator, duplicating external resources during retries, or losing work when a process restarts. The completed Phase 1 and Phase 2 implementation in `zitadel-go-test` addresses those requirements with a Go control-plane binary, PostgreSQL concurrency primitives, hosted ZITADEL Login V2, and evidence gathered from a real browser and a real ZITADEL v4.16.1 deployment.

This is the completion report for the architecture introduced in [[ARTICLE - Deep Dive - Self-Service ZITADEL Tenant Onboarding Control Plane]]. That earlier report captured an implementation checkpoint and correctly left two questions unresolved: whether ZITADEL organization identifiers chosen by the application would work through hosted Login V2, and how an unverified self-registration could continue without weakening administrator binding. Both questions are now answered by committed implementation and live acceptance.

> [!summary]
> - ZITADEL generates the tenant organization ID. PostgreSQL establishes a stable UUID correlation key and exact unique organization name before the API call, preserving safe retries without relying on caller-selected IDs.
> - An unverified OIDC callback reserves a candidate `(issuer, subject)` but creates no administrator session. ZITADEL sends its own email challenge, and a fresh organization-scoped callback binds only the same verified subject.
> - PostgreSQL coordinates one-time OIDC state, opaque sessions, expected-state transitions, worker leases, verification-delivery claims, and public rate limits. Concurrency semantics are part of persistence rather than process memory.
> - Completion required automated race tests, live PostgreSQL tests, provider contract tests, hosted browser acceptance, desktop and mobile review, direct cleanup verification, secret auditing, and fixture removal.

## 1. The completed boundary

The control plane handles the period between a public organization request and a verified initial tenant administrator. It does not yet charge the customer or deploy the tenant workload. Those later activities depend on the identity record produced here, but they remain separate lifecycle phases.

The completed sequence is:

1. The browser requests a server-rendered organization form.
2. The server issues CSRF state and a signed random request token.
3. The POST validates and normalizes the display name, slug, and requested administrator email.
4. PostgreSQL inserts a `draft` onboarding row with a correlation UUID and a globally unique correlated organization name.
5. A narrowly privileged ZITADEL machine identity ensures that organization exists and converges its registration policy.
6. ZITADEL returns its generated numeric organization ID, which PostgreSQL persists in the guarded `draft → organization_created` transition.
7. The browser starts a hosted organization-scoped OIDC authorization using random state, nonce, and S256 PKCE.
8. Login V2 creates the user inside the pending organization.
9. If the returned identity is not email-verified, the control plane reserves the candidate identity and asks ZITADEL to send its own challenge.
10. After hosted verification, the browser starts a fresh organization-scoped authorization.
11. The callback accepts only the same `(issuer, subject)` with the expected resource owner, requested email, and `email_verified=true`.
12. PostgreSQL moves the onboarding to `administrator_verified` and stores a hash of a new opaque browser session identifier.

```mermaid
sequenceDiagram
    participant B as Browser
    participant C as Go control plane
    participant P as PostgreSQL
    participant Z as ZITADEL APIs
    participant L as Login V2 and OIDC
    participant M as Mail provider

    B->>C: POST organization request
    C->>P: Insert draft with correlation key and name
    C->>Z: Ensure organization by exact name
    Z-->>C: Generated numeric organization ID
    C->>P: Guarded organization_created transition
    C-->>B: Pending status

    B->>C: Begin registration
    C->>P: Store state hash, nonce, and PKCE verifier
    C-->>B: Redirect to organization-scoped prompt=create
    B->>L: Register password user
    L-->>C: OIDC callback with email_verified=false
    C->>P: Reserve pending issuer and subject
    C->>P: Claim verification delivery slot
    C->>Z: SendEmailCode using send_code
    Z->>M: Deliver ZITADEL challenge
    C-->>B: Check your email status

    B->>L: Complete hosted verification
    B->>C: Resume authentication
    C->>P: Store a fresh one-time OIDC flow
    C-->>B: Redirect with tenant organization scope
    L-->>C: Verified callback for same subject
    C->>P: Bind administrator and create opaque session
    C-->>B: Verified status
```

Every transition in this sequence has a failure outcome that leaves enough durable state for a retry or cleanup operation. The process does not depend on one uninterrupted HTTP request or one continuously running worker.

## 2. Why onboarding is a separate binary

The repository already contained `todo-demo`, the customer-facing application. Giving that runtime permission to create ZITADEL organizations would combine two authority domains. A tenant application needs to authenticate users and enforce application authorization. It does not need instance-level organization-management authority.

The implementation therefore adds `cmd/tenant-control-plane`. Its commands are defined through Glazed:

- `serve` composes PostgreSQL, ZITADEL clients, hosted OIDC, HTTP routes, and the worker.
- `inspect` emits a structured operational projection without requested email, subject, token, or cookie material.
- `healthcheck` performs native liveness or readiness checks suitable for a distroless image.

The final image remains static and non-root. The interactive Glazed help subsystem was intentionally not included because it introduced Bubble Tea and SQLite/CGO-adjacent dependencies that did not belong in the service image. Glazed remains responsible for command schemas, settings, logging, and structured output; interactive help is not required for the runtime contract.

This separation also preserves the production ownership model:

| Concern | Authority |
|---|---|
| Stable provisioner and OIDC client | Terraform |
| Service key and browser cryptographic key | Vault and Vault Secrets Operator in production |
| Tenant organization lifecycle | Control plane through supported ZITADEL APIs |
| Passwords, factors, recovery, verification | ZITADEL |
| Runtime desired state | Git and Argo CD in later phases |
| Tenant application data | Tenant-specific PostgreSQL role and database |

The local Compose topology follows the same conceptual separation, although it uses an ignored mode-0600 service-key file and a host UID/GID ownership bridge. Production guidance explicitly replaces that local mechanism with Vault injection.

## 3. Three lifecycle dimensions

The domain model does not use one status value to represent technical progress, commercial status, and application access. Those facts can change independently.

The onboarding state records technical progress:

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

Expiry follows a separate terminal path:

```text
pending state → expiring → expired
```

The subscription state is:

```text
none | trialing | active | past_due | canceled | unpaid
```

The access state is:

```text
pending | enabled | grace | suspended | archived
```

This representation prevents later billing code from rewriting identity history. A subscription cancellation does not imply that the organization was never created. A deployment failure does not invalidate a signed subscription event. Cleanup of an abandoned pre-subscription organization does not need to fabricate a billing transition.

`internal/onboarding/model.go` contains an explicit transition table. `Transition` verifies the table in Go and then checks the expected current state in SQL:

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

If another process advanced the row first, the update affects zero rows and returns `ErrStateConflict`. The caller does not overwrite the newer state. It reloads and decides whether the requested operation is already complete, still required, or no longer valid.

## 4. Organization creation after the UUID failure

The first implementation supplied a UUID as `organization_id` to Organization Service v2. The API accepted it. Direct create and list operations passed. The hosted flow then exposed a cross-component incompatibility.

The authorization request contained a scope resembling:

```text
urn:zitadel:iam:org:id:48ba73ca-0825-4683-8c9b-820a04c8c467
```

Login V2 v4.16.1 rendered the organization parameter as `48`, the numeric prefix of the UUID. Registration completed in the default organization. The callback resource-owner check rejected the identity, which prevented an incorrect administrator binding, but the proposed idempotency design could not remain.

The completed design separates three identifiers:

| Value | Owner | Purpose |
|---|---|---|
| Onboarding UUID | Control plane | Internal lifecycle identity |
| Organization correlation UUID | Control plane | External create retry and exact-name suffix |
| Numeric organization ID | ZITADEL | Login V2 scope, resource owner, API operations |

Before calling ZITADEL, the service computes a unique organization name:

```go
func provisionedOrganizationName(displayName string, key uuid.UUID) string {
    runes := []rune(strings.TrimSpace(displayName))
    if len(runes) > 189 {
        runes = runes[:189]
    }
    return string(runes) + " [" + key.String()[:8] + "]"
}
```

The actual implementation derives the maximum length from the suffix size, preserving the 200-rune database and provider limit. The suffix is not an authorization value. It is stable correlation material established before the external call.

The provider algorithm is:

```pseudo
function ensureOrganization(correlationKey, correlatedName):
    require correlatedName ends with firstEight(correlationKey)

    existing = listOrganizations(name equals correlatedName, limit 2)
    if existing.count == 1:
        convergeRegistrationPolicy(existing.id)
        return existing
    if existing.count > 1:
        fail correlation ambiguity

    result = addOrganization(name = correlatedName, organizationId omitted)
    if result succeeded:
        require result.organizationId is nonempty
        convergeRegistrationPolicy(result.organizationId)
        return result

    if result is AlreadyExists:
        existing = exactNameLookup(correlatedName)
        require exactly one result
        convergeRegistrationPolicy(existing.id)
        return existing

    fail provider operation
```

This closes two failure windows. A retry after a successful provider call but failed local update finds the existing organization by exact name. Cleanup can also resolve by exact name when the generated numeric ID was never committed.

The implementation does not interpret the numeric ID, derive local authorization from it, or expose it as a browser-selected input. ZITADEL owns the value. The control plane stores and compares it as opaque text after verifying that Login V2 accepts it through the complete hosted path.

## 5. Registration policy convergence

A new organization is not automatically ready for the desired hosted self-registration path. The control plane uses Management Service calls with explicit `x-zitadel-orgid` metadata to read and converge an organization-specific login policy.

The desired local acceptance policy enables username/password, self-registration, passkeys, email login, and password reset. It disables external identity providers, phone login, and domain discovery for the initial controlled path. The policy operation is scoped to the new organization. It does not mutate the instance policy or the platform organization.

This step is part of `EnsureOrganization`, not a separate best-effort operation. An organization is not reported ready until policy convergence succeeds. A retry can safely read the organization and attempt policy convergence again.

The provisioner receives `IAM_ORG_MANAGER`. It does not receive `IAM_OWNER`. The customer administrator will eventually receive an organization-scoped role such as `ORG_OWNER` after the commercial workflow permits it. These roles solve different authorization requirements and are not interchangeable.

## 6. One-time OIDC state remains server-side

The browser receives a random state value. It does not receive serialized onboarding context, a nonce bundle, or a PKCE verifier. PostgreSQL stores:

```text
SHA-256(state)
onboarding UUID
nonce
PKCE verifier
expires_at
consumed_at
```

The raw state is random 32-byte base64url data. A callback hashes the browser value and atomically claims the row:

```sql
UPDATE onboarding_oidc_flows
SET consumed_at = $now
WHERE state_hash = $hash
  AND consumed_at IS NULL
  AND expires_at > $now
RETURNING ...;
```

One callback wins. A replay receives `ErrFlowConsumed`. An unknown or expired state receives `ErrFlowNotFound`. Eight concurrent integration-test consumers produced one winner.

The authorization URL adds the tenant organization scope dynamically:

```text
openid
profile
email
urn:zitadel:iam:org:id:<generated-organization-id>
```

Initial registration adds `prompt=create`. Verification resume creates a new state, nonce, and PKCE verifier but omits `prompt=create`. The existing hosted session can then complete authentication without attempting to create the user again.

Nonce validation is wired into the pinned OIDC verifier through context. S256 PKCE uses the verifier loaded from the claimed PostgreSQL row. Issuer and audience validation remain the relying party's responsibility. Resource owner, requested email, pending subject, and verification status are application-domain checks performed before local binding.

These checks are distinct:

| Check | Prevented failure |
|---|---|
| State | Callback initiated outside the matching browser flow |
| One-time consumption | Authorization response replay |
| Nonce | ID token substituted across authorization requests |
| PKCE | Authorization code redeemed without the initiating verifier |
| Issuer | Identity accepted from another provider |
| Audience | Token accepted for another client |
| Resource owner | User from another ZITADEL organization bound to the tenant |
| Requested email | Different address completes the reserved onboarding |
| Pending subject | A second account replaces the initial candidate after verification begins |
| `email_verified` | Address claimant becomes administrator without proving control |

Removing any one of these checks changes the accepted identity set.

## 7. Verification is a two-callback protocol

Live password registration returned a valid organization-scoped identity with `email_verified=false`. No automatic challenge completed the desired local path. Accepting that callback would have allowed an address claimant to become the initial administrator. Rejecting it permanently would have left a correct user with no continuation.

The solution treats the first callback as candidate identification rather than administrator verification.

### 7.1 Candidate reservation

The first callback must still pass these checks:

- issuer and subject are present;
- the resource-owner organization equals the pending organization;
- normalized email equals the requested administrator email;
- onboarding state is `organization_created` and has not expired.

PostgreSQL then stores `pending_administrator_issuer` and `pending_administrator_subject`. The onboarding does not advance. No session is created.

A combined partial expression index reserves identity across pending and verified states:

```sql
CREATE UNIQUE INDEX tenant_onboardings_administrator_identity_idx
ON tenant_onboardings (
    COALESCE(administrator_issuer, pending_administrator_issuer),
    COALESCE(administrator_subject, pending_administrator_subject)
)
WHERE administrator_issuer IS NOT NULL
   OR pending_administrator_issuer IS NOT NULL;
```

Two independent indexes would be insufficient. One row could contain a verified subject while another row contained the same pending subject because each index would inspect different columns. The expression index produces one identity namespace for both lifecycle stages.

### 7.2 ZITADEL-owned challenge delivery

The control plane calls User Service v2 `SendEmailCode`. The protobuf request contains a oneof with two materially different behaviors:

```text
send_code   → ZITADEL delivers the challenge
return_code → caller receives verification material
```

The adapter selects only `SendEmailCodeRequest_SendCode` with an empty `SendEmailVerificationCode`. It also rejects any response that unexpectedly contains `verification_code`. This defensive check prevents provider drift or incorrect construction from moving challenge material into application state.

The application never requests, stores, logs, renders, or audits the code. ZITADEL and the mail provider retain ownership of verification.

### 7.3 Same-subject verified completion

After the user completes hosted verification, the status page offers **Resume verified sign-in**. This starts another organization-scoped OIDC flow. The callback must return:

```text
issuer == pending issuer
subject == pending subject
resource owner == pending organization ID
normalized email == requested email
email_verified == true
```

Only then does `BindAdministrator` move the lifecycle to `administrator_verified`, copy the stable identity into verified columns, clear pending fields, and create an opaque server-backed session.

A resumed callback from another subject returns an identity conflict even if it presents the same email and organization. Email remains an attribute. `(issuer, subject)` remains identity.

## 8. Verification delivery is a PostgreSQL claim

A timestamp checked only in Go would not prevent two replicas from sending the same challenge concurrently. Sending first and storing the timestamp afterward would also leave an ambiguous failure window: ZITADEL may have accepted the request even if the client observed a timeout.

The completed flow reserves the delivery slot before the external call:

```pseudo
pending = savePendingIdentity(onboarding, identity)

pending, claimed = claimEmailVerificationRequest(
    onboarding,
    identity,
    requestedAt = now,
    cooldownCutoff = now - 10 minutes
)

if claimed:
    zitadel.sendEmailVerification(organizationId, subject)

return EmailVerificationPending
```

The SQL update succeeds only if no recent delivery timestamp exists. A concurrent loser reloads the same pending record and returns `claimed=false`. Eight concurrent integration-test claimers produced one winner.

This design favors bounded at-most-once delivery inside the cooldown. If the provider call fails ambiguously, retry waits for the cooldown rather than sending uncontrolled duplicates. The status records a safe error code for operators. The challenge itself remains outside application logs.

## 9. Public organization creation has durable limits

CSRF prevents cross-site form submission. A signed request token makes one form idempotent. Unique slugs and request hashes prevent duplicate rows. None of those controls limit a client that repeatedly requests fresh forms and submits different values.

Migration 005 adds fixed-window PostgreSQL buckets:

```sql
CREATE TABLE onboarding_rate_limits (
    scope varchar(64) NOT NULL,
    key_hash bytea NOT NULL CHECK (octet_length(key_hash) = 32),
    window_start timestamptz NOT NULL,
    attempts integer NOT NULL CHECK (attempts > 0),
    expires_at timestamptz NOT NULL,
    PRIMARY KEY (scope, key_hash, window_start)
);
```

An atomic upsert consumes allowance only below the configured limit:

```sql
INSERT INTO onboarding_rate_limits
    (scope, key_hash, window_start, attempts, expires_at)
VALUES ($scope, $key, $window, 1, $expiry)
ON CONFLICT (scope, key_hash, window_start) DO UPDATE
SET attempts = onboarding_rate_limits.attempts + 1,
    expires_at = GREATEST(onboarding_rate_limits.expires_at, EXCLUDED.expires_at)
WHERE onboarding_rate_limits.attempts < $limit
RETURNING attempts;
```

`pgx.ErrNoRows` means the limit denied the request. It is not treated as a database error.

Two scopes protect the endpoint:

- A global scope allows 50 organization starts per ten-minute window.
- An email scope allows five starts per one-hour window.

The email key is HMAC-SHA-256 with purpose separation under the browser security key. PostgreSQL receives only the 32-byte digest, not the email address. The HTTP response is 429 with `Retry-After`. Twelve concurrent database claimers produced exactly five winners for a limit of five, and an HTTP test proved denial on the sixth same-email attempt.

The worker removes expired buckets. No in-memory counter participates in the decision, so process restart and horizontal replicas preserve the same limit.

## 10. Opaque sessions and pending ownership

The control plane has two browser authorization stages.

Before administrator verification, a signed pending-ownership cookie permits access only to its exact onboarding UUID. Possessing another UUID is insufficient. Cross-onboarding status access returns 404 so the endpoint does not confirm peer record existence.

After verification, the browser receives a random opaque session identifier. PostgreSQL stores only its SHA-256 hash plus onboarding UUID, issuer, subject, and expiry. Session lookup loads the verified onboarding and requires its bound issuer and subject to match the session row.

The browser never receives:

- an access token or ID token as application session state;
- the OIDC nonce or PKCE verifier;
- a ZITADEL machine credential;
- the administrator subject;
- a serialized profile;
- a verification code or link.

Pod replacement does not destroy sessions because they are not stored in process memory. Logout deletes the server-side row and expires the cookie.

## 11. Leased cleanup protects external state

An abandoned onboarding may have created an organization and user. Deleting only the PostgreSQL row would leave those resources active. Deleting the organization without durable ownership could allow multiple workers to perform the same operation while racing local state.

The cleanup worker claims one expired row with `FOR UPDATE SKIP LOCKED`, changes it to `expiring`, and writes a random lease token with an expiry. The external delete occurs outside the transaction. Completion requires the same token and a still-valid lease.

```mermaid
stateDiagram-v2
    [*] --> Pending
    Pending --> Expiring: expires_at reached and lease claimed
    Expiring --> Expired: ZITADEL deletion and guarded completion
    Expiring --> Expiring: provider failure and lease release
    Expiring --> Expiring: expired lease reclaimed
```

Deletion treats ZITADEL `NotFound` as success. If the local row contains no generated organization ID because the process failed between external create and local update, cleanup resolves the exact correlated name and deletes that organization.

The same lease model protects later provisioning transitions. Tests cover one winner, lease expiry and reclamation, stale completion rejection, provider failure, and retry.

Live acceptance did not stop at checking the local `expired` state. It queried Organization Service v2 directly after cleanup. Three acceptance organization IDs were checked and zero remained. PostgreSQL onboarding, session, OIDC flow, and rate-limit counts all reached zero. The mail provider contained zero acceptance messages. Temporary credentials and verification material were removed.

## 12. Browser security is part of the service contract

The HTTP application uses `net/http` and embedded templates. It applies bounded bodies, CSRF checks, signed request tokens, and explicit response policies.

Relevant headers include:

```text
Content-Security-Policy
Referrer-Policy: no-referrer
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
Permissions-Policy: camera=(), microphone=(), geolocation=()
Cache-Control: no-store
```

The Content Security Policy permits forms only to the control plane and configured ZITADEL origin. Templates do not require inline scripts. The favicon is embedded and served under `/static/` so browser inspection remains free of application-origin 404s.

Live UI inspection found one HTML compatibility defect before completion. The slug pattern used an unescaped hyphen inside a character class:

```html
pattern="[a-z0-9][a-z0-9-]{1,61}[a-z0-9]"
```

Browsers applying RegExp `v` semantics rejected the pattern. The corrected form is:

```html
pattern="[a-z0-9][a-z0-9\-]{1,61}[a-z0-9]"
```

This defect did not appear in Go handler tests. It required a browser console. The final desktop and mobile captures showed no clipping or horizontal overflow, the timeline displayed organization creation as complete and administrator verification as current, and the rebuilt page emitted zero console errors or warnings.

## 13. Testing the contracts at their actual boundaries

The test strategy uses several evidence classes because no single class establishes the complete behavior.

### 13.1 Pure domain and service tests

These verify transition rules, normalization, request idempotency, provider failure retry, organization mismatch, email mismatch, pending continuation, wrong resumed subject, expiry, opaque sessions, and cleanup behavior.

They answer whether the orchestration behaves correctly under controlled inputs. They do not prove PostgreSQL locking or provider API compatibility.

### 13.2 Live PostgreSQL integration tests

A fresh database applies every migration and runs the real store. Tests verify:

- migration idempotency;
- expected-state updates;
- request and slug uniqueness;
- pending and verified identity uniqueness;
- one-time OIDC flow consumption under concurrency;
- session expiry;
- provisioning and cleanup lease ownership;
- stale completion denial;
- concurrent verification-delivery claims;
- concurrent public rate-limit claims;
- rate-limit expiry cleanup.

The final suite recreated `onboarding_test` and ran with the race detector:

```text
TEST_DATABASE_URL='postgres://postgres:postgres@127.0.0.1:5433/onboarding_test?sslmode=disable' \
  go test -race ./... -count=1
```

All packages passed.

### 13.3 Provider contract tests

Generated gRPC client interfaces are replaced with focused fakes. These tests inspect request oneofs, exact-name queries, organization metadata, policy scope, generated-ID handling, `AlreadyExists` recovery, `NotFound` cleanup, and unexpected returned verification material.

The code uses pinned generated clients from `github.com/zitadel/zitadel-go/v3 v3.29.2`. No protobuf source was copied or modified.

### 13.4 Hosted browser acceptance

A real browser proved behavior that API and unit tests did not reveal:

- custom UUID IDs were truncated by Login V2;
- generated numeric IDs survived the complete hosted path;
- registration produced the intended resource-owner claim;
- the first identity remained unverified;
- `SendEmailCode` delivered a real challenge;
- the hosted verification page required code submission rather than GET-only completion;
- resumed OIDC returned the same verified subject;
- the local state advanced and an opaque session was created;
- desktop and mobile rendering remained usable.

Sensitive acceptance values moved only through ephemeral mode-0600 files and a temporary loopback endpoint. They were not returned in terminal output, browser snapshots, logs, evidence, or Git.

### 13.5 Operational validation

The final command set also included:

```text
go vet ./...
CGO_ENABLED=0 go build ./...
make test
make build
make smoke-local
terraform -chdir=infra/zitadel/local validate
terraform -chdir=infra/zitadel/local plan -detailed-exitcode -no-color
docker compose config --quiet
bash -n scripts/configure-local-zitadel.sh
docmgr doctor --ticket ZITADEL-007-SAAS-ONBOARDING --stale-after 30
git diff --check
```

Terraform reported no changes. The control-plane image ran healthy as a non-root user. The repository's Makefile build artifact was removed before final status review.

## 14. Failures that materially changed the implementation

The completion work produced several failures with direct architectural consequences.

### Custom organization IDs passed one API and failed the hosted path

Organization Service v2 accepted UUID identifiers. Login V2 did not preserve them. The solution was not to weaken resource-owner checking. The solution was to change identifier ownership and rerun the full path.

### Unverified registration was not an administrator

A valid OIDC callback can identify a subject without proving email ownership. The solution was not to accept the callback or store a local verification secret. The solution was a pending identity stage and ZITADEL-owned challenge continuation.

### Separate uniqueness indexes did not reserve one identity namespace

Pending and verified identities occupy different nullable columns. Separate indexes could permit a cross-stage duplicate. One expression index over `COALESCE` establishes a single reservation domain.

### A schema expansion broke lease scanning

Adding organization-correlation and pending-verification fields expanded the common onboarding projection from 23 to 26 columns. Lease queries used a separately maintained prefixed column list and failed with:

```text
number of field descriptions must equal number of destinations, got 23 and 26
```

The prefixed projection was updated and the entire fresh PostgreSQL race suite was rerun. This failure identifies a maintenance risk: row projection lists should remain centralized or generated when the model grows further.

### Browser origins must match cookie scope

Starting acceptance at `127.0.0.1` while the configured public URL used `localhost` caused the callback to lose pending ownership and return 404. The supported local origin is now explicit. Browser security depends on origin identity; loopback names are not interchangeable cookie domains.

### Verification links rendered a form

A GET of the verification link rendered the hosted code form but did not verify the user. Acceptance had to submit the hosted form. Provider behavior must be established through an observed state change, not inferred from HTTP 200.

### PDF publication exposed a Markdown escape defect

A literal `\n` in a verbatim diary prompt reached LaTeX as an undefined command. Preserving the exact prompt inside Markdown code formatting corrected rendering without altering the recorded text.

These are not incidental debugging details. Each failure identifies where one subsystem's accepted representation was insufficient evidence for another subsystem's behavior.

## 15. The final security invariants

The completed implementation establishes a concise set of invariants.

- A browser cannot choose the ZITADEL organization ID.
- Organization creation has durable request idempotency and PostgreSQL-backed rate limits.
- A ZITADEL organization is not ready until its registration policy converges.
- Initial authorization is organization-scoped and uses state, nonce, and S256 PKCE.
- OIDC state is one-time and server-side.
- A callback from another resource-owning organization cannot bind locally.
- Email must match the request, but email is not identity.
- `(issuer, subject)` is reserved across pending and verified stages.
- `email_verified=false` creates no administrator session.
- Verification material remains in ZITADEL and the mail provider.
- Verification resume requires the same subject in a fresh OIDC flow.
- Browser sessions are opaque and persisted by hash.
- Worker completion requires a current lease token.
- Cleanup removes external organizations before local fixture deletion.
- Operator output and audit records omit PII, credentials, tokens, cookies, and verification material.
- The provisioner has `IAM_ORG_MANAGER`, not `IAM_OWNER`.
- Customer administration remains organization-scoped and is not implemented as instance authority.

These invariants are represented in code, database constraints, tests, and live acceptance. They are not only documentation statements.

## 16. What Phase 3 may rely on

Subscription work can now consume a verified onboarding record with these properties:

```text
state = administrator_verified
zitadel_organization_id = provider-generated numeric identifier
administrator_issuer = configured ZITADEL issuer
administrator_subject = stable external subject
administrator_verified_at = non-null
pending_administrator_issuer = null
pending_administrator_subject = null
access_state = pending
subscription_state = none
```

Phase 3 can create Stripe Checkout from a server-controlled plan and advance the independent subscription state from signed webhook evidence. It does not need to create or verify the administrator again. It must not derive identity from the requested email, and it must not treat a successful Checkout redirect as payment authority.

Later provisioning can use the stable organization ID and verified subject to create tenant-owned projects, OIDC applications, Vault records, databases, and GitOps declarations. Customer organization ownership must remain scoped to the tenant organization. The control plane's instance-level provisioner authority must not enter tenant runtime credentials.

## 17. Reading the implementation

A productive review order is:

1. `internal/onboarding/model.go` — lifecycle vocabulary and legal transitions.
2. `internal/onboarding/postgres/migrations/001_initial.sql` through `005_rate_limits.sql` — physical invariants.
3. `internal/onboarding/store.go` — durable operation contract.
4. `internal/onboarding/service.go` — orchestration and administrator continuation.
5. `internal/onboarding/postgres/onboardings.go` — guarded writes and identity reservation.
6. `internal/onboarding/oidc.go` — dynamic hosted authorization and token exchange.
7. `internal/onboarding/zitadel/organizations.go` — provider identifier, policy, email, and cleanup behavior.
8. `internal/onboarding/postgres/leases.go` and `rate_limits.go` — concurrency ownership.
9. `internal/onboarding/httpapp/app.go` and `cookies.go` — browser authorization and security.
10. `cmd/tenant-control-plane/serve.go` — executable composition.
11. `internal/onboarding/*_test.go` and PostgreSQL integration tests — contract evidence.
12. The ZITADEL-007 completion audit and acceptance record — live results and cleanup proof.

## 18. Closing assessment

Phase 1 and Phase 2 are complete at repository revision `f119d6d1c5ea3ed79b1a560a899159e61e18ee15`. The result is not only a signup page. It is a durable control-plane boundary that creates a tenant identity organization, proves the first administrator through hosted identity workflows, preserves concurrency and retry semantics in PostgreSQL, and removes abandoned resources without expanding the authority of the tenant application.

The most consequential result came from retaining strict checks during live failures. The wrong-organization user was rejected. The unverified user was not promoted. The implementation changed organization identifier ownership and added a verification continuation instead of weakening validation. The final architecture is therefore supported by both positive acceptance and observed denial behavior.

The next phase can begin from a stable identity record. Stripe subscription state and tenant workload provisioning can remain independent, auditable transitions built on the same expected-state, lease, secret-ownership, and acceptance principles.

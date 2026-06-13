---
title: "go-go-goja Express Auth: Go-Backed Fluent Route Plans"
aliases:
  - go-go-goja Express Auth
  - Express Planned Auth Routes
  - Go-backed Express Route Plans
tags:
  - article
  - go
  - goja
  - javascript
  - express
  - authentication
  - authorization
  - architecture
  - postgres
  - audit
  - persistence
status: active
type: article
created: 2026-06-12
updated: 2026-06-12
repo: /home/manuel/workspaces/2026-06-12/goja-express-auth/go-go-goja
branch: task/goja-express-auth
---

# go-go-goja Express Auth: Go-Backed Fluent Route Plans

This report wraps up the Express authentication work implemented in `go-go-goja` on branch `task/goja-express-auth`. The final implementation is no longer just an MVP side path: the Express verb helpers have been hard-cut over to planned route builders, planned routes now support host-owned auth/resource/authorization/CSRF/audit enforcement, strict hosts can reject raw routes, and the examples include both a route-authoring sketch and a runnable Go-owned auth host.

> [!summary]
> - JavaScript now declares route intent through staged Go-backed builders: `app.get(...).public().handle(...)` or `app.patch(...).auth(...).resource(...).csrf().allow(...).audit(...).handle(...)`.
> - Go owns the security-critical route plan, validates it at registration time, and enforces it in `pkg/gojahttp.Host` before JavaScript handlers run.
> - The old `app.get(path, handler)` style was intentionally removed from the Express verb helpers. Public routes must say `.public()`; protected routes must declare auth policy before `.handle(...)`.
> - The host-side production user/session system is deliberately not built into Express. The module exposes interfaces; applications or future optional packages provide Keycloak/OIDC, sessions, user storage, resource resolution, authorization, CSRF, audit, and capabilities.

## Why this note exists

The original request was to add proper authentication to the `express` module in `go-go-goja`. Before this work, the module was intentionally small: JavaScript could register handlers with methods like `app.get`, `app.post`, and `app.patch`, and `pkg/gojahttp.Host` would match the route and call the JavaScript handler. That was enough for examples and small HTTP tools, but it had no host-owned authentication boundary. A route author had to remember to do security work manually inside JavaScript.

The new design reverses that responsibility. JavaScript describes what kind of route it is, what resource it touches, which action is required, whether CSRF is required, and what audit event should be emitted. Go stores that declaration in a `RoutePlan` and runs the security pipeline before the handler is invoked.

The implementation deliberately avoids accepting arbitrary JavaScript objects as security declarations. A dynamic object like `{ required: true }` is easy to write but hard to trust: Go would have to parse and validate object shape, defaults, nested fields, unknown keys, and conflicting options. Instead, `express.user()` and `express.resource(type)` return Go-backed JavaScript objects. The builder accepts only those trusted objects.

## Final JavaScript API shape

The final public-route shape is explicit:

```javascript
const express = require("express")
const app = express.app()

app.get("/healthz")
  .public()
  .audit("health.checked")
  .handle((_ctx, res) => res.json({ ok: true }))
```

The final protected-route shape is also explicit:

```javascript
app.patch("/orgs/:orgId/projects/:projectId")
  .auth(express.user().required())
  .resource(
    express.resource("project")
      .idFromParam("projectId")
      .tenantFromParam("orgId")
      .mustExist()
  )
  .csrf()
  .allow("project.update")
  .audit("project.updated")
  .handle((ctx, res) => {
    const project = ctx.resource("project")
    res.json({ updated: project.id, tenant: project.tenantId })
  })
```

A current-user route can be minimal while still going through Go-owned authentication and authorization:

```javascript
app.get("/me")
  .auth(express.user().required())
  .allow("user.self.read")
  .audit("user.self.read")
  .handle((ctx, res) => {
    res.json({ id: ctx.actor.id, kind: ctx.actor.kind })
  })
```

The important API rule is now simple: `.handle(...)` is not available until the route has chosen a security mode. `.public()` is a security declaration too; it says the route is intentionally public.

## The hard cutover

A major decision during implementation was to stop preserving the old Express verb overloads. The names `app.get`, `app.post`, `app.put`, `app.patch`, `app.delete`, and `app.all` remain, but they now return staged planned-route builders. This old form is intentionally invalid:

```javascript
app.get("/healthz", (_req, res) => res.json({ ok: true }))
```

The replacement is:

```javascript
app.get("/healthz")
  .public()
  .handle((_ctx, res) => res.json({ ok: true }))
```

This was a breaking change, but it made the API safer and easier to explain. Keeping old raw-route overloads beside the new planned-route API would make it too easy for applications to accidentally create unauthenticated routes that look visually similar to secured routes. The generic `app.route(method, pattern)` escape hatch remains for unusual or dynamic methods, but it also returns the planned builder.

## Architecture

The implementation has three main layers:

1. `modules/express` exposes the JavaScript API and compiles fluent calls into Go-owned route plans.
2. `pkg/gojahttp` stores planned routes, validates plans, and dispatches requests through the security pipeline.
3. The embedding Go application provides host services through `gojahttp.HostOptions.Auth`.

```mermaid
flowchart TD
  JS[JavaScript route author] --> Builder[Go-backed Express staged builders]
  Builder --> Plan[gojahttp RoutePlan]
  Plan --> Registry[gojahttp route registry]
  Request[HTTP request] --> Host[gojahttp Host ServeHTTP]
  Host --> Registry
  Host --> Auth[Authenticator]
  Host --> CSRF[CSRFProtector]
  Host --> Resolver[ResourceResolver]
  Host --> Policy[Authorizer]
  Host --> Audit[AuditSink]
  Host --> Context[Secure planned context]
  Context --> Handler[JavaScript handler]
```

The Express module still does not define a user store. That separation is intentional. Express should not own Keycloak, passwords, sessions, tenant membership, or database schema. Express owns route declaration. `gojahttp` owns route-plan enforcement. The application or future optional packages own identity, session, policy, and persistence.

## RoutePlan: the host-owned contract

The central data structure lives in `pkg/gojahttp/auth_plan.go`:

```go
type RoutePlan struct {
    Name      string
    Method    string
    Pattern   string
    Security  SecuritySpec
    Resources []ResourceSpec
    Action    string
    CSRF      CSRFSpec
    Audit     AuditSpec
}
```

The plan is the contract that must be satisfied before a handler runs. It records:

- route method and pattern,
- public versus authenticated-user security mode,
- resources and value sources,
- required action,
- CSRF requirement,
- audit event name.

Resource binding is intentionally adapter-shaped, not policy-shaped. A route can say that a `project` resource ID comes from `:projectId` and the tenant boundary comes from `:orgId`; it does not decide whether the actor is allowed to update that project. The host `ResourceResolver` and `Authorizer` make those decisions.

## Host auth interfaces

The host services are in `pkg/gojahttp/auth_plan.go`:

```go
type AuthOptions struct {
    Authenticator Authenticator
    Resources     ResourceResolver
    Authorizer    Authorizer
    CSRF          CSRFProtector
    Audit         AuditSink
}
```

The current interfaces are deliberately small:

```go
type Authenticator interface {
    Authenticate(ctx context.Context, req *http.Request, session *SessionDTO, spec SecuritySpec) (*Actor, error)
}

type ResourceResolver interface {
    ResolveResource(ctx context.Context, req ResourceRequest) (*ResourceRef, error)
}

type Authorizer interface {
    Authorize(ctx context.Context, req AuthorizationRequest) (AuthorizationDecision, error)
}

type CSRFProtector interface {
    VerifyCSRF(ctx context.Context, req CSRFRequest) error
}

type AuditSink interface {
    RecordAudit(ctx context.Context, event AuditEvent) error
}
```

A host wires them like this:

```go
host := gojahttp.NewHost(gojahttp.HostOptions{
    RejectRawRoutes: true,
    Auth: gojahttp.AuthOptions{
        Authenticator: myAuthenticator,
        Resources:     myResourceResolver,
        Authorizer:    myAuthorizer,
        CSRF:          myCSRFProtector,
        Audit:         myAuditSink,
    },
})
```

This is the seam that lets different applications use the same Express planned-route API with different auth backends. A demo can use an in-memory bearer token. A production app can use Keycloak/OIDC plus server-side sessions. A test can provide tiny fakes.

## Request execution sequence

A planned route request follows one host-owned sequence:

```text
match route
  -> build RequestDTO
  -> authenticate actor, if required
  -> verify CSRF, if required and method is unsafe
  -> resolve declared resources
  -> authorize declared action
  -> emit allowed audit event
  -> call JavaScript handler with secure ctx and res
  -> emit completed or failed audit event
```

```mermaid
sequenceDiagram
  participant H as Host
  participant A as Authenticator
  participant C as CSRFProtector
  participant R as ResourceResolver
  participant P as Authorizer
  participant S as AuditSink
  participant J as JavaScript handler

  H->>H: Match planned route
  H->>A: Authenticate if route requires user
  A-->>H: Actor
  H->>C: Verify CSRF for unsafe .csrf route
  C-->>H: OK
  H->>R: Resolve declared resource values
  R-->>H: ResourceRef map
  H->>P: Authorize actor/action/resource
  P-->>H: Decision allowed
  H->>S: Audit allowed
  H->>J: Call handler with planned ctx
  J-->>H: Response
  H->>S: Audit completed or failed
```

If any pre-handler step fails, the handler is not invoked. Authentication failures map to 401, authorization and CSRF failures map to 403, resource-not-found maps to 404, and host misconfiguration/backend failures map to 500.

## Secure context shape

Planned handlers receive `(ctx, res)` rather than the raw `(req, res)` used by earlier raw routes. The context contains the safe, resolved view of the request:

```javascript
ctx.actor              // authenticated actor, or null for public routes
ctx.params             // route params
ctx.body               // parsed request body
ctx.resources          // resolved resources map
ctx.resource("project") // convenient lookup
ctx.action             // declared action
ctx.routeName          // declared or generated route name
ctx.request            // request DTO details
```

The implementation explicitly maps Go structs to JavaScript-facing property names such as `id`, `kind`, `tenantId`, and `claims`. This avoids accidentally exposing Go field naming or internal implementation details.

## Strict raw-route rejection

The host now supports:

```go
gojahttp.HostOptions{RejectRawRoutes: true}
```

When this option is enabled, matched routes without a `RoutePlan` are rejected at request time. This gives production hosts a practical fail-closed mode without changing the low-level `Host.Register` signature. Static mounts are unaffected because they are not registry routes.

Route descriptors were also expanded so tools can inspect whether a route is planned and what its security metadata is. That makes migration and diagnostics easier: a host can list routes, identify raw routes, and decide whether to enable strict rejection.

## CSRF and audit

The final implementation includes the planned CSRF and audit hooks that were originally deferred.

`.csrf()` marks a route as requiring host-owned CSRF verification. The host only calls the verifier for unsafe methods, and it does so after authentication but before resource resolution and authorization. This is the right default for cookie/session-authenticated browser routes because the actor being authenticated is not enough to prove the request was intentional.

`.audit(event)` declares an audit event name. The host emits best-effort audit records through `AuditSink` for allowed, denied, completed, and failed outcomes. JavaScript does not write security audit records directly; it declares intent and Go emits the record with actor/resource/action/status context.

Best-effort audit was chosen for this pass: audit sink errors do not change successful business responses. A future production host package may add a strict audit mode for compliance-sensitive deployments.

## Documentation and examples

The user-facing docs now include:

- `pkg/doc/18-express-module.md` — main Express module reference.
- `pkg/doc/29-express-auth-user-guide.md` — auth framework user guide.
- `pkg/doc/30-migrate-express-apps-to-planned-auth.md` — migration tutorial for the hard cutover.

The examples now include:

- `examples/xgoja/15-express-planned-auth/` — compact JavaScript route-authoring reference.
- `examples/xgoja/16-express-auth-host/` — runnable Go-owned auth host with fake authenticator, resource resolver, authorizer, CSRF protector, audit sink, strict raw-route rejection, smoke mode, and manual serve mode.

The runnable host example is important because it demonstrates the intended layering. The Go host owns security services; JavaScript owns route declarations and business handlers.

## Validation status

The final implementation passed targeted validation:

```bash
go test ./pkg/gojahttp ./modules/express ./pkg/xgoja/providers/http -count=1
go test ./examples/xgoja/16-express-auth-host/cmd/host ./pkg/gojahttp ./modules/express ./pkg/xgoja/providers/http -count=1
make -C examples/xgoja/16-express-auth-host smoke
```

The broader suite passed with the known generated-build workaround:

```bash
GOFLAGS=-buildvcs=false go test ./... -count=1
```

The remaining validation caveat is unrelated to Express auth semantics: generated temporary xgoja build workspaces can fail Go VCS stamping unless `-buildvcs=false` is used. The recommended follow-up is to make xgoja generated/temp builds pass `-buildvcs=false` internally.

## Commits produced

The work was committed incrementally:

| Commit | Purpose |
| --- | --- |
| `6af0bbd` | Planned implementation phases in the docmgr ticket. |
| `99a2da3` | Added `gojahttp` planned route auth model. |
| `e19ea0d` | Added planned route dispatch and secure context. |
| `3b1220f` | Added Express fluent auth route builders. |
| `13d4675` | Documented Express planned auth routes. |
| `2ee50b5` | Added provider coverage and planned auth example. |
| `f31a391` | Completed phase bookkeeping. |
| `cdf7b1b` | Planned hard cutover for Express verb helpers. |
| `4492723` | Hard-cut Express verb helpers to planned routes. |
| `de09c15` | Added Express auth help guides. |
| `4f42a55` | Added strict raw route rejection option. |
| `61c858d` | Added planned route CSRF and audit hooks. |
| `f852a21` | Added runnable Express auth host example. |
| `5d0c7fd` | Imported Keycloak/OIDC host auth notes for the next phase. |

The implementation diary is in:

```text
/home/manuel/workspaces/2026-06-12/goja-express-auth/go-go-goja/ttmp/2026/06/12/XGOJA-EXPRESS-AUTH--add-proper-authentication-to-express-http-module/reference/01-investigation-diary.md
```

## What is now finished

The Express route declaration and enforcement foundation is finished for this phase:

- Go-backed staged route builders exist.
- Verb helpers now require planned-route declaration.
- Public/authenticated/resource-bound route plans are validated.
- Host dispatch enforces authentication, resource resolution, authorization, CSRF, and audit before or around handler execution.
- Strict raw-route rejection is available.
- Docs, help pages, tests, and examples have been updated.
- A runnable host example demonstrates the integration shape.

This is the point where Express planned auth can be treated as the framework boundary.

## What remains outside this phase

The next phase is not more Express syntax. It is the actual host-side user/auth system.

That means an opinionated production stack such as:

- Keycloak as IdP,
- OIDC Authorization Code + PKCE,
- server-side application sessions,
- normalized app user records,
- tenant and membership storage,
- explicit Go authorization functions,
- persistent audit sink,
- capability tokens for invites/email verification/password reset/API tokens,
- body/schema validation,
- negative authorization tests.

A simpler dev/demo stack should also exist:

- in-memory users,
- password or bearer demo login,
- in-memory sessions,
- in-memory resources,
- explicit demo authorizer,
- in-memory audit capture,
- smoke tests that show login, protected route access, CSRF denial, mutation success, and logout.

The important boundary remains the same: production identity and user storage should not be moved into `modules/express`. They should live in optional host-side packages or application code that implements the `gojahttp` interfaces.

## Final working rule

For future work, keep this rule intact:

> Express route authors declare intent. Go host code enforces security. Application packages own identity, sessions, users, tenants, capabilities, and policy.

That rule is what keeps the JavaScript API pleasant without letting the JavaScript layer become the security boundary.

---

## Follow-up: porting the Express auth branch across the xgoja/v2 merge

After PR #73 landed on `origin/main`, the Express auth branch had to be merged across the new `xgoja/v2` configuration and example layout. The merge was not just a mechanical rebase: the xgoja examples were renumbered, the native schema changed to `schema: xgoja/v2`, several older xgoja help pages were deleted, and new TypeScript/protobuf examples occupied the old Express-auth example numbers.

> [!summary]
> - The Express auth examples were moved from `15/16/17` to `17/18/19` so the new protobuf and TypeScript xgoja examples can remain `15` and `16`.
> - The new TypeScript xgoja HTTP example had to be updated to the hard-cutover Express API: `app.get(path).public().handle(...)` instead of `app.get(path, handler)`.
> - The build-VCS stamping issue is now fixed on `origin/main`; the branch no longer needs the `GOFLAGS=-buildvcs=false` workaround for normal `go test ./...`.

### What changed during the port

The merge brought in the xgoja/v2 planner and the new example numbering from `origin/main`. The main conflict was that this branch had added Express-auth examples as `15-express-planned-auth`, `16-express-auth-host`, and `17-express-keycloak-auth-host`, while `origin/main` now uses those slots for:

| Number | `origin/main` example | Express-auth branch resolution |
| --- | --- | --- |
| `15` | `15-protobuf-builder-provider` | Kept from `origin/main`. |
| `16` | `16-typescript-jsverbs` | Kept from `origin/main`, then updated to planned Express routes. |
| `17` | free after the new v2 examples | Moved `15-express-planned-auth` here. |
| `18` | free after the new v2 examples | Moved `16-express-auth-host` here. |
| `19` | free after the new v2 examples | Moved `17-express-keycloak-auth-host` here. |

The concrete path changes are:

```text
examples/xgoja/15-express-planned-auth        -> examples/xgoja/17-express-planned-auth
examples/xgoja/16-express-auth-host          -> examples/xgoja/18-express-auth-host
examples/xgoja/17-express-keycloak-auth-host -> examples/xgoja/19-express-keycloak-auth-host
```

All user-facing help pages and example READMEs were updated to reference the new paths:

```text
pkg/doc/18-express-module.md
pkg/doc/29-express-auth-user-guide.md
pkg/doc/30-migrate-express-apps-to-planned-auth.md
pkg/doc/31-express-auth-examples.md
examples/xgoja/README.md
```

The `examples/xgoja/README.md` learning path now has the xgoja/v2 examples first and the Express-auth examples after them:

```text
15. 15-protobuf-builder-provider
16. 16-typescript-jsverbs
17. 17-express-planned-auth
18. 18-express-auth-host
19. 19-express-keycloak-auth-host
```

### The extra fix: TypeScript HTTP example used the old Express API

The only semantic code fix found during the port was in the newly merged TypeScript xgoja example. Its `verbs/sites.ts` used the old raw Express handler overload:

```ts
app.get("/healthz", (_req: unknown, res: any) => {
  res.json({ ok: true, site: "typescript-demo", version })
})
```

Because the Express auth branch intentionally hard-cuts verb helpers, that route must now be planned explicitly:

```ts
app.get("/healthz")
  .public()
  .handle((_ctx: unknown, res: any) => {
    res.json({ ok: true, site: "typescript-demo", version })
  })
```

Running the TypeScript example smoke regenerated `examples/xgoja/16-typescript-jsverbs/js/types/xgoja-modules.d.ts`, which is a useful confirmation that the generated declarations now expose the planned-route builder types (`RouteNeedsSecurity`, `RouteNeedsHandler`, `PlannedContext`, `UserAuthBuilder`, and resource specs) instead of the removed raw handler overloads.

### What was hard to figure out

The first hard part was separating true conflicts from old-number collisions. The merge looked large because xgoja/v2 moved or deleted many files, but most of that was upstream work. The actual Express-auth work was narrow: keep the new xgoja/v2 docs and examples, move the Express-auth examples after them, and fix stale paths.

The second hard part was deciding what to do with conflicts in old xgoja docs and generated tests. `origin/main` intentionally deleted several old tutorial pages and replaced them with v2 docs such as `migrating-to-xgoja-v2` and `xgoja-v2-reference`, so the right resolution was to keep the deletion rather than revive obsolete v1 tutorials. For `cmd/xgoja/internal/generate/generate_test.go`, the branch only had tiny Express route syntax edits, while `origin/main` had a broader v2 planner rewrite. The right resolution was to take the v2 version and then search for stale raw Express route calls elsewhere.

The third hard part was remembering that the new TypeScript example is not part of the Express-auth branch historically, but it imports `express` and therefore must obey the new hard-cutover API. The quick check that caught it was:

```bash
rg 'app\.get\([^\n]+,' examples/xgoja pkg/xgoja/providers/http cmd/xgoja/internal/generate
```

That found `examples/xgoja/16-typescript-jsverbs/verbs/sites.ts`, which was then converted and validated.

### Validation after the port

The merged branch now validates without the old build-VCS workaround:

```bash
go test ./... -count=1
make -C examples/xgoja/16-typescript-jsverbs smoke
make -C examples/xgoja/18-express-auth-host smoke
make -C examples/xgoja/19-express-keycloak-auth-host smoke
```

The targeted auth and docs checks also passed:

```bash
go test ./pkg/gojahttp ./modules/express ./pkg/gojahttp/auth/... ./pkg/xgoja/providers/http ./examples/xgoja/18-express-auth-host/cmd/host ./examples/xgoja/19-express-keycloak-auth-host/cmd/host -count=1
go run ./cmd/goja-repl help express-auth-user-guide
go run ./cmd/goja-repl help express-auth-examples
docmgr doctor --ticket XGOJA-HOST-AUTH --stale-after 30
docmgr doctor --ticket XGOJA-EXPRESS-AUTH --stale-after 30
```

### Documentation that should be improved

The docs are good enough for the PR, but a few improvements would make future merges and feature branches easier:

1. **Add an xgoja/v2 example-numbering rule.** `examples/xgoja/README.md` should explicitly say that new examples should append after the current learning path and should check `origin/main` before choosing a number. This would have made the `15/16/17` collision obvious earlier.

2. **Add a planned-Express migration note to the TypeScript xgoja docs.** The TypeScript example now demonstrates the planned API, but the v2 TypeScript docs could mention that generated declarations reflect the installed provider API. If a provider hard-cuts an API, TypeScript examples should regenerate sidecar `.d.ts` files and update call sites together.

3. **Add a small PR-merge checklist for branches touching examples.** A useful checklist would be:
   - fetch `origin/main`,
   - compare `examples/xgoja/README.md`,
   - check for duplicate example numbers,
   - run `rg 'app\.(get|post|put|patch|delete|all)\([^\n]+,'` when Express is touched,
   - run the affected example smoke targets,
   - regenerate generated declarations when provider APIs changed.

4. **Make `xgoja doctor` surface stale provider API examples if possible.** This is a larger improvement, but stale raw Express usage in a TypeScript jsverb was only caught by smoke. If `doctor` can cheaply parse or compile TypeScript sources with generated declarations, it could catch this kind of provider API mismatch earlier.

5. **Document the distinction between xgoja examples and host-only examples.** `17-express-planned-auth`, `18-express-auth-host`, and `19-express-keycloak-auth-host` are under `examples/xgoja`, but they are not all native `xgoja.yaml` build fixtures. The README now hints at this, but a clearer section would help readers understand which examples are xgoja generated-binary examples and which are host integration examples.

### Current status after the port

The Express auth branch is now rebased/merged over the xgoja/v2 mainline without losing the planned-auth work. The remaining PR shape is cleaner than before because `origin/main` also fixed the generated build VCS stamping issue. The branch now contains:

- planned Express route builders and hard-cut verb helpers,
- host-side auth packages,
- dev-auth and Keycloak examples renumbered after the v2 xgoja examples,
- consolidated Glazed help pages,
- automated dev and Keycloak smokes,
- compatibility with the new xgoja/v2 examples and TypeScript declaration generation.

The main follow-up is not a code blocker: improve docs/checklists so future feature branches can merge across xgoja example/documentation reorganizations with less archaeology.
---

## Follow-up: persistent host auth stores and production-shaped Keycloak/Postgres smoke

The branch did not stop at the planned Express route boundary. After the xgoja/v2 port, the work moved into the host-auth productionization track: durable sessions, durable audit records, contract tests for future store implementations, and a Keycloak smoke that now exercises real Postgres-backed app sessions and audit tables.

This is an important shift in the project. The first part of the work answered: “How does JavaScript safely declare route security intent?” The follow-up work answers: “How does a real Go host back those declarations with durable authentication state, operational audit records, and production-shaped examples?”

> [!summary]
> - `sessionauth/sqlstore` now provides a `database/sql` implementation of `sessionauth.Store`, with SQLite tests and Postgres DDL.
> - `audit/sqlstore` now provides a `database/sql` implementation of `audit.Store`, with durable audit rows, redaction tests, and operational query examples.
> - Reusable store contract packages now define expected behavior for session, audit, capability, and appauth stores before more SQL adapters are added.
> - The Keycloak example now starts Postgres, uses Postgres-backed app sessions and audit records, and verifies persisted audit rows in its smoke test.

### New follow-up tickets

Three follow-up tickets now capture the next productionization tracks:

| Ticket | Purpose | Current shape |
| --- | --- | --- |
| `XGOJA-AUTH-STORES` | Durable production stores for host auth packages. | Active implementation ticket; session and audit stores are now implemented. |
| `XGOJA-AUTH-KEYCLOAK-MFA` | Production Keycloak hardening and concrete MFA freshness flows. | Design ticket for OIDC transaction storage, secure deployment settings, logout semantics, and `Session.MFAAt` update flows. |
| `XGOJA-AUTH-PROD-DOCS` | Production deployment guide, policy-adapter planning, and process cleanup. | Planning ticket for operator docs, optional Casbin/OpenFGA/OPA adapters, example-numbering rules, and TypeScript regeneration process. |

The important body/schema conclusion is also recorded in the Keycloak/MFA design: body schema validation is security-relevant, but it is not authentication. It matters when authorization depends on body fields such as `tenantId`, `role`, `ownerId`, `resourceId`, or capability/invite attributes. It should become a separate request-validation and authorization-safety follow-up after stores and Keycloak/MFA hardening, not a blocker for session persistence.

### Store contracts before SQL adapters

Before adding SQL stores, the branch added reusable contract tests under `pkg/gojahttp/auth/internal/*test`:

```text
pkg/gojahttp/auth/internal/sessionauthtest/store_contract.go
pkg/gojahttp/auth/internal/audittest/store_contract.go
pkg/gojahttp/auth/internal/capabilitytest/store_contract.go
pkg/gojahttp/auth/internal/appauthtest/store_contract.go
```

These contract packages are deliberately small and behavior-focused. They are meant to be run against the in-memory implementations today and every SQL/Postgres implementation later.

| Contract | What it proves |
| --- | --- |
| `sessionauthtest.RunStoreContract` | Sessions can be created, loaded, touched, rotated, revoked, and missing sessions map to invalid cookies. It also asserts clone isolation for slices, maps, and timestamp pointers. |
| `audittest.RunStoreContract` | Audit records are inserted in order and snapshots cannot mutate stored attributes. |
| `capabilitytest.RunStoreContract` | Capabilities store token hashes, redeem with purpose/expiry/revocation checks, and enforce atomic single-use behavior under concurrent redemption attempts. |
| `appauthtest.RunStoreContract` | App-owned users, Keycloak subjects, memberships, roles, resources, revoked/disabled state, and clone isolation behave consistently. |

The contract extraction exposed clone-isolation gaps in the in-memory stores. Those were fixed immediately:

- `sessionauth.cloneSession` now clones `MFAAt` and `RevokedAt` pointers.
- `capability.cloneCapability` now clones `UsedAt` and `RevokedAt` pointers.
- `appauth.MemoryStore` clones users, memberships, and resources on add/load paths.
- `audit.MemoryStore` was added as a concrete in-memory `audit.Store` and clones attributes recursively.

This matters because SQL stores naturally deserialize fresh values from the database, while memory stores can accidentally share caller-owned pointers, slices, maps, or byte slices. The contracts make the intended boundary explicit.

### SQL session store

The first durable adapter is `pkg/gojahttp/auth/sessionauth/sqlstore`. It implements the existing `sessionauth.Store` interface with `database/sql`, without changing `sessionauth.Manager`, Keycloak callback handling, or the Express route API.

```go
db, err := sql.Open("postgres", dsn)
if err != nil { return err }

store, err := sqlstore.New(sqlstore.Config{
    DB:      db,
    Dialect: sqlstore.DialectPostgres,
})
if err != nil { return err }

if err := store.ApplySchema(ctx); err != nil { return err }

sessions, err := sessionauth.New(sessionauth.Config{Store: store})
```

The store supports `Create`, `Get`, `Touch`, `Rotate`, and `Revoke`. `Rotate` runs in a SQL transaction: delete the old session ID and insert the new session in one commit. `Revoke` remains idempotent for missing sessions, matching the memory-store contract.

The session schema stores the fields needed by app sessions, Keycloak normalization, CSRF, and MFA freshness:

```text
id
user_id
keycloak_sub
email
email_verified
tenant_ids_json
csrf_token
mfa_at
created_at
last_seen_at
idle_expires_at
absolute_expires_at
revoked_at
claims_json
```

For Postgres, `tenant_ids_json` and `claims_json` are `JSONB`, and timestamps are `TIMESTAMPTZ`. SQLite DDL exists for fast local tests and contract execution.

```mermaid
flowchart TD
  Browser[Browser] --> Cookie[Opaque app session cookie]
  Cookie --> Manager[sessionauth.Manager]
  Manager --> Store[sessionauth.Store]
  Store --> SQL[sessionauth/sqlstore]
  SQL --> DB[(Postgres auth_sessions)]
  Manager --> Actor[gojahttp.Actor]
  Actor --> Host[planned route pipeline]
```

The SQLite tests run the reusable session store contract and a full-projection test that verifies identity fields, tenant IDs, MFA timestamps, revoked timestamps, and claims survive persistence. The later Keycloak smoke also proved the Postgres path against a real database driver and container.

### Postgres in the Keycloak example

The Keycloak host example now includes Postgres in `examples/xgoja/19-express-keycloak-auth-host/docker-compose.yml`. The service is intentionally for the Go host’s app-side auth state, not Keycloak’s internal dev database. This keeps the example fast while validating the new stores through a real Postgres server.

Default smoke database:

```text
postgres://goja:goja@127.0.0.1:15432/goja_auth?sslmode=disable
```

The example host now has `--session-db-dsn`. When it is empty, the example falls back to `sessionauth.MemoryStore`. When it is set, the host opens Postgres with `github.com/lib/pq`, applies the `sessionauth/sqlstore` schema, and uses Postgres-backed app sessions.

The smoke target now starts both Keycloak and Postgres:

```bash
make -C examples/xgoja/19-express-keycloak-auth-host smoke
```

It verifies public health, unauthenticated denial, Keycloak Authorization Code + PKCE login, Postgres-backed app-session creation, CSRF-token retrieval, unsafe mutation denial without CSRF, unsafe mutation success with CSRF, resource-not-found behavior, logout, and post-logout denial.

The important proof is that the app session used by this flow is no longer only in memory.

### SQL audit store

The second durable adapter is `pkg/gojahttp/auth/audit/sqlstore`. It implements `audit.Store` and is intended to be wired through `audit.Sink`:

```go
store, err := auditsqlstore.New(auditsqlstore.Config{
    DB:      db,
    Dialect: auditsqlstore.DialectPostgres,
})
if err != nil { return err }

if err := store.ApplySchema(ctx); err != nil { return err }

sink := audit.Sink{Store: store}
```

This separation is intentional: `audit/sqlstore` persists normalized records; `audit.Sink` and `audit.Normalizer` perform normalization and redaction before insert. The SQL store does not try to rediscover which fields are secret. The host should wire the normalized sink.

The schema stores route and request context useful for incident review:

```text
id
event
outcome
reason
status_code
route_name
method
pattern
action
actor_id
actor_kind
tenant_id
resource_type
resource_id
request_id
ip_hash
user_agent
attributes_json
created_at
```

For Postgres, `attributes_json` is `JSONB`. Indexes exist for common operational filters: `created_at`, `outcome`, `event`, `actor_id`, `(resource_type, resource_id)`, and `tenant_id`.

The package also includes a small query helper and README examples for operational use:

```go
denied, err := store.QueryByOutcome(ctx, "denied", 100)
```

Equivalent SQL for operators:

```sql
SELECT created_at, event, outcome, reason, actor_id, tenant_id,
       resource_type, resource_id, action, request_id
FROM auth_audit_records
WHERE outcome IN ('denied', 'failed')
ORDER BY created_at DESC
LIMIT 100;
```

The tests prove three important details:

1. The SQL store satisfies the reusable `audittest` contract.
2. Records written through `audit.Sink` are redacted before reaching SQL.
3. `QueryByOutcome` returns denied/failed records in useful newest-first order.

### Persistent audit in the Keycloak smoke

The Keycloak example now also has `--audit-db-dsn` / `AUDIT_DB_DSN`. If no audit DSN is provided, the example uses `audit.LogSink`. If a DSN is provided, it uses `audit/sqlstore` through `audit.Sink`.

The Makefile defaults `AUDIT_DB_DSN` to `SESSION_DB_DSN`, so the smoke uses one Postgres service for both `auth_sessions` and `auth_audit_records`.

The smoke now checks that planned-route audit records were really persisted:

```bash
SELECT count(*)
FROM auth_audit_records
WHERE event IN ('health.checked', 'user.self.read', 'project.updated')
```

A passing smoke now ends with output like:

```text
ok persisted audit records 12
```

This proves the full route-audit path:

```mermaid
sequenceDiagram
  participant JS as JS planned route
  participant Host as gojahttp.Host
  participant Sink as audit.Sink
  participant Store as audit/sqlstore
  participant DB as Postgres

  JS->>Host: .audit("project.updated") in RoutePlan
  Host->>Host: authenticate / CSRF / resolve / authorize
  Host->>Sink: RecordAudit(allowed/completed/denied)
  Sink->>Sink: Normalize + redact attributes
  Sink->>Store: InsertAuditRecord(record)
  Store->>DB: INSERT auth_audit_records
```

### Smoke hardening: detecting stale local hosts

The first attempt to verify persisted audit rows failed with `count=0`, but the root cause was not audit storage. A stale host process was already listening on `127.0.0.1:8790`, so the newly launched host exited with:

```text
listen tcp 127.0.0.1:8790: bind: address already in use
```

The old smoke readiness function only checked whether `/healthz` was reachable. That meant it could talk to the stale process and continue. The smoke script now uses `wait_for_host_url`, which checks that the specific launched host PID is still alive before accepting the health endpoint as ready.

This is a small but important test rule: end-to-end smokes should verify the process they launched, not just that a URL responds.

### Current implementation status

The persistent-store track has completed these `XGOJA-AUTH-STORES` phases:

| Phase | Status |
| --- | --- |
| Reusable store contract tests | Done. |
| SQL session store | Done. |
| Keycloak/Postgres app-session smoke | Done. |
| SQL audit store | Done. |
| Keycloak/Postgres audit persistence smoke | Done. |
| SQL capability store | Not started. |
| SQL appauth user/tenant/membership/resource store | Not started. |
| Full Keycloak + Postgres + sessionauth + appauth + audit + capability smoke | Partially done; session and audit are wired, appauth and capability remain in-memory/not wired. |

The current branch now has a much more concrete production story than the first report did. The Express framework boundary is still the same, but the host side is no longer just an interface sketch: sessions and audit records have working SQL implementations, and the Keycloak example proves those implementations through a realistic browser-login flow.

### New commits after the xgoja/v2 report

The major new commits since the previous vault update are:

| Commit | Purpose |
| --- | --- |
| `9e3eb7d` | Created persistent-store and Keycloak/MFA follow-up planning tickets. |
| `8478fb8` | Created production deployment docs and policy-adapter planning ticket. |
| `22eb7d6` | Added reusable auth store contract tests. |
| `c495b26` | Added generated logcopter stubs for the auth store contract packages. |
| `304f833` | Added `sessionauth/sqlstore`. |
| `8bde147` | Recorded auth store implementation diary steps. |
| `e53d063` | Wired Keycloak smoke to Postgres-backed sessions. |
| `cf7a2d8` | Recorded Postgres Keycloak smoke diary. |
| `8821692` | Added `audit/sqlstore`. |
| `5fcac51` | Added generated logcopter stub for `audit/sqlstore`. |
| `c962de2` | Persisted Keycloak smoke audit records. |
| `19edaf4` | Recorded persistent audit smoke diary. |

### Current validation commands

The branch has passed:

```bash
go test ./pkg/gojahttp/auth/... -count=1

go test \
  ./examples/xgoja/19-express-keycloak-auth-host/cmd/host \
  ./pkg/gojahttp/auth/audit/sqlstore \
  ./pkg/gojahttp/auth/sessionauth/sqlstore \
  -count=1

make -C examples/xgoja/19-express-keycloak-auth-host smoke
```

The pre-commit and pre-push hooks also ran lint and `go test ./...` successfully on the pushed commits.

### What remains next

The next implementation step is `capability/sqlstore`. It is the highest-risk remaining store because single-use token redemption must be atomic. The contract already encodes the desired behavior: many concurrent redeem attempts against the same single-use token should produce exactly one success and the rest `ErrUsed`.

After that, the app-owned auth domain needs a SQL starter store:

- users,
- Keycloak subject mapping,
- tenants,
- memberships and roles,
- resources.

Only after sessions, audit, capabilities, and appauth are all persistent should the production deployment guide and optional policy-adapter work become the main focus.

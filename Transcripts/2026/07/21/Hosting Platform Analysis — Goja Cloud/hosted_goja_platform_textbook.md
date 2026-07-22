# Building a Hosted Goja Application Platform

## A textbook guide to go-go-goja, xgoja, go-go-host, Tiny-IDP, secure HTTP applications, module subscriptions, and agent-driven releases

**Architecture and implementation guide**  
**Research snapshot:** July 20, 2026

---

## Preface

This book explains a specific engineering problem: how to turn the Goja-based tools in the Go Go Golems ecosystem into a hosted platform where customers upload JavaScript or TypeScript programs, select native Go-backed modules, publish secure web applications and functions, manage their own users, and release changes through coding agents without losing auditability or rollback safety.

The repositories already contain many of the required pieces. `go-go-goja` provides an owned JavaScript runtime, an event loop, explicit native-module composition, TypeScript declaration generation, an extensive HTTP framework, planned authorization, server-side sessions, programmatic agent authentication, guarded outbound HTTP, and generated xgoja hosts. `go-go-host` provides an early control plane for organizations, sites, deployments, agents, domains, quotas, capabilities, audit, and runtime activation. The `task/prod-tiny-idp` branch of Tiny-IDP develops a particularly strong model for constrained JavaScript programs: serializable contracts, named lambdas, schemas, outcomes, capabilities, effects, budgets, fingerprints, worker pools, and durable browser continuations. The Widget DSL research demonstrates how server-side JavaScript can produce a versioned user-interface intermediate representation that a generic browser renderer can display. [S1][S4][S10][S17][S21]

The book has two obligations. First, it must describe the current implementations accurately. Second, it must explain the target architecture without pretending that recommendations already exist in production code. Sections therefore use three labels:

- **Current implementation** describes code or documented behavior found in the reviewed repositories.
- **Design principle** explains the reasoning that should survive refactoring.
- **Target platform** describes the recommended hosted system.

The central correction to the earlier architectural review is that the HTTP subsystem is not a small route bridge. `go-go-goja` already contains a substantial web application framework. JavaScript uses an Express-style declaration API, but Go owns the listener, router, request parsing, session state, authentication, CSRF checks, resource resolution, authorization, rate limits, audit, static mounts, generic handler mounts, asynchronous handler completion, OIDC lifecycle routes, and graceful shutdown. The hosted platform should build on that framework rather than replacing it with a second, narrower HTTP stack. [S4][S5][S6][S7][S8][S9]

### How to read this book

Parts I and II establish the runtime and HTTP foundations. Part III turns those foundations into a control plane, build plane, and execution plane. Part IV generalizes the Tiny-IDP and Widget DSL work into an agent-friendly application model. Part V evaluates the current code, assigns repository responsibilities, and provides an implementation sequence.

A new intern should read the chapters in order. An experienced engineer may begin with Chapter 4 for the HTTP framework, Chapter 10 for releases, or Chapter 17 for the gap analysis.

### Source notation

References such as `[S7]` point to the source map in Appendix C. Sources are repository files, design documents, and the two PARC project notes requested for this review. The codebase is active; line numbers and package details may change after the stated research snapshot.

---

# Part I — Foundations

# 1. The System We Are Building

The proposed product is a managed application platform for JavaScript programs executed by Goja. A customer uploads source code, chooses a set of native modules, connects resources such as a database or identity realm, and promotes an immutable release. The platform runs that release as an HTTP application, a request-driven function, a scheduled job, or an automation agent. The customer pays for modules and resources rather than operating the Go runtime or compiling a custom binary by hand.

That description contains several different kinds of software. Separating them early prevents most architectural confusion.

| Kind of code | Author | Trust level | Examples |
| --- | --- | --- | --- |
| Tenant application code | Customer or coding agent | Untrusted or partially trusted | Route handlers, workflows, page composition, business rules |
| Native runtime module | Platform or reviewed provider author | Trusted | SQLite API, planned HTTP framework, payments adapter, auth client, Widget DSL |
| Browser asset | Customer build pipeline | Untrusted content served under policy | React bundle, CSS, images, static HTML |
| Control-plane service | Platform | Highly trusted | Release API, entitlements, policy, audit, domains, worker scheduler |
| Identity kernel | Platform or dedicated customer service | Highly trusted | OIDC validation, credentials, sessions, signing keys, continuation state |

The platform must not treat these categories as interchangeable. JavaScript is allowed to express application behavior. It is not allowed to choose its own operating-system privileges, inject arbitrary Go packages, read the platform process environment, obtain raw database handles, or define how tokens are verified. Native modules expose selected authority through typed APIs. The control plane decides whether the customer is entitled to use that authority. The worker enforces the decision.

## 1.1 Four planes

A useful first decomposition has four planes.

```text
Authoring and build plane
    source -> static analysis -> runtime profile -> artifact

Control plane
    organizations -> projects -> releases -> policy -> traffic

Execution plane
    routers -> isolated workers -> capability brokers -> resources

Identity plane
    platform users -> application users -> sessions -> tokens -> keys
```

The planes communicate through immutable records and narrow protocols. They should not share a large mutable process merely because all services are written in Go.

## 1.2 The product promise

A credible product promise is stronger than “we execute JavaScript.” It is:

- A release names the exact source, native modules, policies, bindings, renderer, and runtime ABI that executed.
- The platform can explain why a request was allowed or denied before JavaScript ran.
- A coding agent can propose a release, but cannot silently enlarge its own authority.
- A failed release does not replace a healthy release.
- A rollback selects an exact earlier release and records the new traffic decision.
- Subscription changes affect release eligibility through an internal entitlement model, not through a billing API call on every request.
- Customer code is isolated from the control plane and from other customers.

These promises determine the architecture. They require immutable releases, explicit capabilities, host-owned HTTP security, reproducible builds, transactional state transitions, and an execution boundary stronger than a Go interface.

## 1.3 Why Goja is appropriate

Goja is useful when JavaScript drives an engine written in Go and frequently crosses the Go/JavaScript boundary. It is pure Go and gives the host precise control over available modules and concurrency. A `goja.Runtime` is not goroutine-safe; only one goroutine may use a runtime at a time. The host must therefore own scheduling rather than allowing arbitrary request goroutines to call the VM. [S2][S3]

Goja is not a complete Node.js runtime and should not become one accidentally. The platform chooses which Node-like facilities exist. That constraint is an advantage for a managed product: it makes the runtime surface reviewable.

## 1.4 The first design decision

**Decision:** JavaScript expresses behavior; Go owns authority.

If JavaScript owned listeners, cookies, token verification, filesystem access, network sockets, or database credentials directly, each application would construct a different security boundary. The platform could no longer reason about releases uniformly. By keeping authority in Go-backed services, the platform can validate a static plan, enforce it before callbacks, meter it, audit it, and revoke it.

### Key points

- The product is a managed authority system, not only a script runner.
- Tenant code, native modules, browser assets, control-plane code, and identity code have different trust levels.
- The target architecture has separate build, control, execution, and identity planes.
- JavaScript should receive narrow capabilities rather than ambient process authority.

---

# 2. Runtime Ownership, Scheduling, and Lifecycle

A Goja runtime is a mutable interpreter state. It contains global variables, loaded modules, JavaScript objects, pending promises, and references to Go values. The most important runtime rule is therefore ownership: at any moment, one serialized execution path owns the VM.

## 2.1 The owned runtime

`go-go-goja` wraps the raw VM in an `engine.Runtime`. The runtime contains the VM, the CommonJS `require` implementation, a Node-style event loop, a runtime owner, runtime-scoped values, a lifetime context, and registered cleanup functions. The factory constructs these pieces in a deliberate order. [S2]

```text
RuntimeFactory
    -> new goja.Runtime
    -> new event loop
    -> new RuntimeOwner
    -> lifetime context
    -> runtime bridge bindings
    -> require registry
    -> native module registration
    -> enable require and standard globals
    -> runtime initializers
    -> owned Runtime
```

This order solves concrete problems. Native modules need the event loop and owner before they can create asynchronous APIs. Modules must register loaders before `require` is enabled. Runtime initializers may import modules, so they run afterward. Cleanup hooks are registered during construction and run in reverse order during shutdown.

## 2.2 RuntimeFactory versus Runtime

The factory is an immutable composition plan. A runtime is one mutable execution instance created from that plan.

| Object | Lifetime | Mutable state | Responsibility |
| --- | --- | --- | --- |
| `RuntimeFactoryBuilder` | Build/configuration | Yes, until `Build` | Collect modules, middleware, initializers, and require options |
| `RuntimeFactory` | Process or release generation | No | Create equivalent runtime instances |
| `Runtime` | Worker or invocation pool slot | Yes | Own one VM, event loop, values, and resources |

This separation is essential for pooling. A platform can validate and freeze one release profile, then create several equivalent workers without rebuilding policy on every request.

## 2.3 RuntimeOwner

`runtimeowner.RuntimeOwner` exposes `Call`, `Post`, `WaitIdle`, `Shutdown`, and `IsClosed`. `Call` schedules work on the owner context and waits for a result. `Post` schedules work without a return value. Both associate the caller's context with the VM operation through the runtime bridge. [S3]

```go
result, err := runtime.Owner.Call(ctx, "load-program", func(ctx context.Context, vm *goja.Runtime) (any, error) {
    return vm.RunProgram(compiled)
})
```

The owner also handles reentrant calls. If native module code is already running on the owner path and calls another owner operation using the marked context, the owner executes it directly rather than deadlocking by scheduling onto itself.

## 2.4 Contexts are not execution limits by themselves

A context can stop waiting without stopping JavaScript. If a caller's deadline expires while JavaScript is in an infinite loop, `Call` may return cancellation while the scheduled callback continues to occupy the VM. The HTTP response can time out while the worker remains blocked.

The Tiny-IDP scripting branch demonstrates a stronger pattern. An invocation creates a deadline, installs a callback that invokes `VM.Interrupt`, marks the worker unsafe, clears the interrupt during bounded cleanup, and discards the worker instead of returning it to the pool. [S19][S20]

The hosted runtime should formalize this sequence:

```text
invocation deadline
    -> cancel native capabilities
    -> interrupt VM
    -> mark worker poisoned
    -> attempt bounded cleanup
    -> discard VM
    -> kill worker process if it does not stop
```

The process boundary is the final enforcement mechanism. Goja interruption protects the pool. Operating-system limits protect the node.

## 2.5 Promise settlement

Asynchronous native modules must not resolve a promise from a background goroutine by touching the VM directly. The correct pattern is:

1. Create the promise on the owner path.
2. Run blocking work outside the VM.
3. Post settlement back to the owner.
4. Resolve or reject while the VM is owned.

The HTTP host and Tiny-IDP worker both account for promises. The HTTP host accepts a promise returned by a route handler and polls its state through owner calls until it is fulfilled or rejected. Tiny-IDP capability bindings perform native work asynchronously and post the result back through the owner. [S5][S20]

## 2.6 Runtime lifecycle

A runtime must close all resources it created: database connections, HTTP clients, file watchers, timers, plugin processes, and background goroutines. Native modules receive an `AddCloser` hook during registration. The runtime cancels its lifetime context, waits briefly for owner activity, interrupts if required, executes closers, removes bridge state, shuts down the owner, and stops the event loop. [S2]

**Decision:** Every native module must be runtime-scoped unless its state is demonstrably immutable and process-safe.

A global module registry may describe available module types, but mutable connections and services belong to a runtime or a release worker. This prevents one tenant's state from leaking into another tenant's VM.

### Key points

- A raw `goja.Runtime` is not the platform execution unit; the owned runtime is.
- Factories freeze policy, while runtimes hold mutable execution state.
- All VM calls and promise settlements must pass through the owner.
- Context cancellation must be paired with VM interruption and worker disposal.
- Native resources must register cleanup with the runtime lifecycle.

---

# 3. xgoja as the Build and Composition System

`xgoja` is the bridge between application intent and a concrete Go binary. It selects provider packages, native runtime modules, JavaScript or TypeScript sources, command surfaces, generated artifacts, and workspace behavior. The v2 schema makes these concepts explicit and produces an embedded runtime plan. [S1]

## 3.1 Providers and runtime modules

A provider is a trusted Go package that contributes one or more capabilities to xgoja. A provider may register runtime modules, command sets, source sets, TypeScript declarations, help text, assets, host services, and runtime initializers. A runtime module is one selected JavaScript-visible API supplied by a provider. [S1]

```yaml
providers:
  - id: http
    import: github.com/go-go-golems/go-go-goja/pkg/xgoja/providers/http

runtime:
  modules:
    - provider: http
      name: express
      as: express
```

The alias is part of the source contract. A TypeScript or JavaScript file may import `express`, and the planner preserves that bare import so the Goja runtime resolves it through the native registry.

The distinction between provider and module matters for subscriptions. A provider is a build-time package. A module is a selected API. An entitlement is the customer's commercial right to select it. A permission is the authority the module may exercise. A binding is the concrete resource attached to it. These concepts must remain separate.

## 3.2 Sources and the closed graph

Executable source sets have a declared origin, language, include/exclude patterns, and compile intent. xgoja parses static imports and validates local helpers and bare module names. Nonliteral dynamic imports are rejected because a generated application requires a closed source graph. [S1]

```text
source set
    -> parse imports
    -> resolve local files
    -> verify native module aliases
    -> bundle TypeScript if requested
    -> emit executable source artifact
```

A closed graph provides several benefits:

- The release can name every source file and native dependency.
- Missing imports fail during planning rather than on a production request.
- Agents can generate TypeScript against exact declarations.
- The platform can calculate a stable source digest.
- Runtime module entitlements can be checked before building.

## 3.3 Commands are explicit surfaces

Runtime modules and command sets are different provider outputs. The Express module lets JavaScript register routes. The HTTP provider's `serve` command owns the listener and keeps the runtime alive. A command chooses which source sets it can execute. [S1][S12]

This design should be preserved in the hosted platform, even if the public product hides the generated CLI. A release still needs an explicit execution surface:

- HTTP application.
- Request-driven function.
- Scheduled job.
- Queue consumer.
- One-shot migration.
- Agent command.

The platform should not infer every possible surface from arbitrary top-level JavaScript effects.

## 3.4 Generated runtime packages

xgoja can generate a runtime package containing an embedded plan, provider registration code, embedded source files, TypeScript declarations, and APIs for creating runtimes. The embedding host may configure host services or apply controlled runtime configuration before constructing the bundle. [S1]

For local tools, this flexibility is useful. For hosted releases, it must be narrowed. A customer must not be able to alter provider imports, use local `go.work` replacements, or inject arbitrary Go dependencies. The platform should generate the xgoja specification from an operator-controlled module catalog.

## 3.5 Reproducible runtime profiles

The current runtime plan intentionally omits build-only information such as provider import paths, module versions, and replacements. That is suitable for a generated binary that already contains its code, but it is insufficient as the sole hosted release identity. [S1]

The target release lock should record:

```json
{
  "runtimeAbi": "gogo-host/v1",
  "toolchain": "go1.x.y",
  "gojaVersion": "...",
  "goGoGojaVersion": "...",
  "sourceDigest": "sha256:...",
  "programDigest": "sha256:...",
  "profileDigest": "sha256:...",
  "modules": [
    {
      "id": "sqlite",
      "version": "1.3.2",
      "providerModule": "github.com/example/provider",
      "providerSum": "h1:...",
      "alias": "db",
      "configDigest": "sha256:..."
    }
  ]
}
```

**Decision:** Hosted builds use exact module versions from a curated catalog and disable workspace discovery and arbitrary replacements.

The alternative—building from the customer's xgoja provider list—would let uploaded source expand the trusted computing base. That is not a safe subscription model.

### Key points

- xgoja is already a build planner and module linker, not merely a CLI wrapper.
- Providers are trusted Go packages; runtime modules are selected JavaScript APIs.
- Closed import graphs enable reproducible releases and early failures.
- Command surfaces should remain explicit even when the hosted product hides the CLI.
- A hosted release needs a complete runtime lock in addition to the embedded runtime plan.

---

# Part II — The Secure HTTP Application Framework

# 4. Go Owns the Server; JavaScript Declares the Application

The HTTP architecture begins with a strict separation. JavaScript declares routes and handlers. Go owns the network listener, top-level mux, request lifecycle, route registry, security services, and VM scheduling. The API is Express-style because the fluent route syntax is familiar, but it is not an attempt to reproduce the full npm Express ecosystem. [S4]

## 4.1 The main components

| Component | Responsibility |
| --- | --- |
| `gojahttp.Host` | Route matching, mounts, request DTOs, sessions, planned enforcement, dispatch, response handling |
| `modules/express` | JavaScript route and mount declaration API |
| HTTP provider `serve` command | Listener, `http.Server`, top-level mux, native handlers, runtime construction, signal handling, graceful shutdown |
| `Enforcer` | Router-independent authentication, CSRF, resource resolution, authorization, rate limits, and audit |
| `hostauth` | Optional session, OIDC, app authorization, capability, and programmatic-auth services |
| `RuntimeOwner` | Serialized callbacks into the Goja VM |

A request path in a generated application looks like this:

```text
client
  -> http.Server
  -> top-level ServeMux
       -> native Go auth/readiness routes, when configured
       -> hot-reload helper routes, when configured
       -> gojahttp.Host
            -> static or generic mounted handler
            -> planned Go route
            -> planned JavaScript route
            -> raw JavaScript route, only when allowed
```

The `serve` command mounts native auth handlers before the JavaScript fallback, then constructs a runtime with per-runtime host services, executes the selected route-registration source, starts the listener, and performs graceful shutdown on cancellation or signals. JavaScript does not call `app.listen()`. [S12]

## 4.2 Express is a declaration layer

A normal public route is explicit:

```javascript
const express = require("express");
const app = express.app();

app.get("/healthz")
  .public()
  .handle((_ctx, res) => res.json({ ok: true }));
```

An authenticated mutation declares its security intent before supplying a handler:

```javascript
app.patch("/orgs/:orgId/projects/:projectId")
  .auth(express.sessionUser())
  .resource(
    express.resource("project")
      .idFromParam("projectId")
      .tenantFromParam("orgId")
      .mustExist()
  )
  .csrf()
  .rateLimit(
    express.rateLimit("project-update")
      .perMinute(30)
      .byActor()
      .byResource("project")
  )
  .allow("project.update")
  .audit("project.update")
  .handle((ctx, res) => {
    res.json({ id: ctx.resource("project").id, updated: true });
  });
```

The route file does not load a session row, parse a bearer token, query a membership table, or decide whether the actor may update the project. It names the requirements. Go enforces them.

## 4.3 Why the server is not started from JavaScript

Allowing scripts to create listeners would create several problems:

- Multiple scripts could bind conflicting addresses.
- The platform could not mount native OIDC or readiness handlers consistently.
- Signal handling and graceful shutdown would vary by application.
- Hot reload would have to replace listeners rather than route snapshots.
- The platform could not guarantee one routing and observability boundary.

The HTTP provider therefore owns `net.Listen`, `http.Server.Serve`, and shutdown. Express is route registration only. [S12]

## 4.4 Static mounts and generic Go handlers

The host supports three forms of non-route dispatch:

1. Static filesystem directories.
2. Static content from an embedded asset module.
3. Generic Go `http.Handler` mounts exposed by trusted native modules.

```javascript
app.staticFromAssetsModule("/static", require("fs:assets"), "/app/public");
app.mount("/ws", sessionstream.webSocket.server(hub));
```

Generic mounts preserve the original path by default. Static helpers strip the prefix. Exclusion prefixes allow a broad mount to leave selected paths for later routes. This makes the host usable for WebSockets and other Go-owned transports without constructing a second JavaScript routing system. [S4][S5]

## 4.5 Raw routes

The host still supports low-level raw JavaScript handlers for compatibility. `RejectRawRoutes: true` makes matched raw routes fail rather than bypass planned policy. Planned routes and approved mounts continue to work. [S5][S9]

**Decision:** Production generated hosts should reject raw routes by default.

The important property is reviewability. Every ordinary route should visibly declare public or authenticated access. An accidental `app.get(path, handler)` overload must not create an unplanned security path.

## 4.6 Request and response objects

`gojahttp` parses the method, URL, path, query values, path params, headers, cookies, session, client IP, body, and raw body into a request DTO. JSON, URL-encoded, and multipart forms are parsed automatically; other bodies remain strings. The current parser caps request bodies at 64 MiB and multipart in-memory use at 32 MiB. [S5]

The response API provides status, headers, JSON, send, HTML rendering, redirects, and end. It ensures that a response is only sent once. A handler may return a promise; the host waits for fulfillment through owner-scheduled checks. [S4][S5]

The hosting platform should make body and response limits configurable per route profile and usually much smaller than the generic framework maximum.

### Key points

- The Go HTTP host is the server; Express is the application declaration language.
- The `serve` command owns listener lifecycle, native handlers, runtime startup, and shutdown.
- Planned routes, planned Go handlers, static mounts, generic mounts, and compatibility raw routes share one host.
- Production should reject raw routes.
- Request parsing and promise completion are already integrated with runtime ownership.

---

# 5. Planned Routes: Security Intent as Data

A planned route is a `RoutePlan` produced when the application registers a route. The plan is validated before traffic is accepted. It contains the method, pattern, security mode, acceptable credential requirements, resources, action, CSRF requirement, audit event, and rate-limit policies. [S6]

## 5.1 The route plan

```go
type RoutePlan struct {
    Name       string
    Method     string
    Pattern    string
    Security   SecuritySpec
    Resources  []ResourceSpec
    Action     string
    CSRF       CSRFSpec
    Audit      AuditSpec
    RateLimits []RateLimitSpec
}
```

This is the central HTTP design. Security is no longer hidden in middleware order or handler branches. It is a value that can be validated, listed, documented, diffed, tested, and audited.

## 5.2 Staged builders

The Go API uses distinct builder stages:

```text
RouteNeedsSecurity
    -> Public()
        -> RouteNeedsHandler

RouteNeedsSecurity
    -> Auth(spec)
        -> RouteNeedsPolicy
            -> Resource / CSRF / Audit / RateLimit
            -> Allow(action)
                -> RouteNeedsHandler
```

The JavaScript API uses Go-backed builder objects with the same conceptual stages. A handler cannot be registered until the route has called `.public()` or completed `.auth(...).allow(...)`. [S4][S8]

This is stronger than documentation. It makes omitted security declarations a registration error.

## 5.3 Registration-time validation

`ValidateRoutePlan` normalizes and checks the plan. Important invariants include: [S6]

- The method and pattern are required.
- A route must choose public or authenticated security.
- Public routes cannot declare authenticated principal requirements.
- Authenticated routes require an action.
- OAuth routes require audit.
- Resource value sources must reference real path params.
- Authentication requirements are normalized and deduplicated.
- Rate-limit specs are normalized before registration.

A typo such as `idFromParam("id")` on `/projects/:projectId` fails at startup rather than producing an authorization gap on a live request.

## 5.4 Security requirements

The framework distinguishes credential method from principal kind.

| Dimension | Examples |
| --- | --- |
| Authentication method | Session, API token, access token |
| Principal kind | User, agent, service |

A browser route can require `sessionUser()`. An automation endpoint can require `agent()`. A deliberately shared endpoint can use `anyOf(sessionUser(), agent())`. [S15]

This prevents a common mistake: an API token with a matching action should not automatically enter a browser-only route. The principal requirement is checked before the handler.

## 5.5 Resources and authorization

A resource declaration describes where the resource identity comes from. It does not load the resource itself.

```javascript
express.resource("project")
  .idFromParam("projectId")
  .tenantFromParam("orgId")
  .mustExist()
```

The host calls a `ResourceResolver`, receives a minimal `ResourceRef`, then passes the actor, action, primary resource, and all resolved resources to the `Authorizer`. The handler receives the resolved references only after authorization succeeds. [S6][S7]

This division keeps domain policy in Go while keeping route intent near the application behavior.

## 5.6 CSRF

A route may call `.csrf()`. On unsafe methods, the enforcer invokes the host `CSRFProtector` when the authentication result requires CSRF. Browser session authentication normally requires it. API-token authentication does not rely on ambient cookies, but a route can reject API tokens through `sessionUser()` before this distinction matters. [S7][S15]

CSRF is therefore not a JavaScript convention. It is a host service enforced before the callback.

## 5.7 Rate limits

Rate limits are route policy. The builder can construct keys from IP, route, actor, params, tenant params, headers, body fields, or resolved resources. Some limits run before authentication; limits that require actor or resource data run afterward. Denied callers do not consume shared post-authorization resource buckets. [S7][S8][S15]

```text
pre-auth limit
  -> authentication
  -> principal requirement
  -> CSRF
  -> resource resolution
  -> grant/action check
  -> authorizer
  -> post-auth limit
  -> handler
```

A hosted platform should attach plan metadata to metrics so that operators can answer which policy rejected a request without logging secrets or high-cardinality payloads.

## 5.8 Audit

If a route declares an audit event, the enforcer records denied, allowed, failed, and completed outcomes. Audit records include route identity, action, actor, resources, status, reason, and redacted authentication attributes. [S7]

The present code ignores errors returned by `AuditSink.RecordAudit`. For a general library this may avoid breaking user traffic when audit storage is unavailable. For the hosted control plane, security-relevant mutations need a stricter durability contract. The platform can use a transactional outbox or fail closed for selected actions.

## 5.9 SecureContext

After enforcement, handlers receive a `SecureContext` containing:

- The validated route plan.
- Parsed request data.
- Params and body.
- Redacted authentication information.
- The actor.
- Resolved resources.
- The action.

The context is not a raw store or token container. Raw bearer values, password material, and refresh-token identifiers do not enter it. [S6]

### Key points

- Planned routes compile security intent into a validated value.
- Builder stages prevent handler registration before access policy is declared.
- Principal kind and credential method are separate constraints.
- Resource identity is declared in JavaScript, but resource loading and authorization remain in Go.
- Rate limits and audit are first-class route-plan fields.

---

# 6. The Enforcer Pipeline

The `Enforcer` is the router-independent implementation behind planned routes. `gojahttp.Host`, standard `net/http` middleware, generated hosts, and custom adapters can all use the same pipeline. [S7][S8]

## 6.1 Ordered enforcement

The order is deliberate:

```text
1. Validate route plan
2. Construct initial SecureContext
3. Apply pre-auth rate limits
4. Authenticate when required
5. Check route credential/principal requirements
6. Verify CSRF for applicable unsafe requests
7. Resolve declared resources
8. Intersect credential grants with the action
9. Call the authorizer
10. Apply post-auth rate limits
11. Record allowed audit state
12. Invoke handler
13. Record completed or failed audit state
```

Changing this order changes security semantics. For example, post-auth rate limits must not run before authorization if a denied caller could exhaust another tenant's resource bucket. CSRF must run before the mutation callback. Resource resolution must happen before resource-based authorization and post-auth limits.

## 6.2 Authentication adapters

The basic `Authenticator` returns an actor. The richer `ResultAuthenticator` returns an `AuthResult` with method, principal kind, credential metadata, grants, scopes, CSRF behavior, and optional verified OAuth context. Older authenticators are adapted to browser-session user results. [S6][S7]

This supports several credential families without making handlers parse headers:

- Server-side browser sessions.
- Application API tokens.
- OAuth-style access tokens.
- Future service credentials.

## 6.3 Grant checks and authorizer checks

A credential may carry grants. The enforcer first checks whether those grants allow the route action on the resource. It then calls the host authorizer for application policy. [S7]

Both checks matter:

- A token cannot exceed the permissions encoded into it.
- A token grant does not override current application policy, membership, suspension, or resource state.

This is especially useful for coding agents. An agent token can be narrowly scoped, while the authorizer still checks current project ownership and environment policy.

## 6.4 Error mapping

Typical status behavior is:

| Condition | Status |
| --- | --- |
| Required credential missing or invalid | 401 |
| Authenticated principal does not satisfy route requirement | 403 |
| CSRF invalid | 403 |
| Resource absent | 404 |
| Action or authorizer denied | 403 |
| Rate limit exceeded | 429 |
| Missing host service or invalid route plan | 500 |

Development mode may expose internal 500 details. Production mode should return generic errors and record detailed diagnostics in structured logs and audit. [S5][S7][S15]

## 6.5 Using the framework without JavaScript

The same route-plan system is available to Go applications:

- `gojahttp.NewApp(host)` for a fluent Go route builder.
- `RegisterPlannedHTTP` for generated or low-level plans.
- `PlannedMiddleware` for an existing router.
- `NewEnforcer` for custom adapters. [S8]

This is important for platform architecture. Native control or management endpoints can share the same security model as JavaScript routes. The system does not need one authorization framework for Go and another for tenant applications.

## 6.6 Why not use middleware order as policy

Traditional middleware stacks can be secure, but their effective policy is procedural. Reviewers must trace the exact nesting order and determine whether a handler is mounted inside or outside each wrapper. A `RoutePlan` is declarative and serializable.

**Decision:** Treat route policy as data and the enforcer as the only interpreter of that data.

This allows the platform to produce a release-time route inventory:

```text
PATCH /orgs/:orgId/projects/:projectId
  principal: session user
  resource: project from projectId, tenant from orgId
  csrf: required
  action: project.update
  rate limits: project-update
  audit: project.update
```

A coding agent can generate this inventory, a policy engine can reject it, and a reviewer can approve it before deployment.

### Key points

- The enforcer is reusable independently of a particular router or JavaScript runtime.
- Enforcement order is part of the security contract.
- Token grants and current application authorization are separate checks.
- Go and JavaScript routes can share one planned-auth system.
- Route inventories should become release artifacts and authority diffs.

---

# 7. Host Authentication, OIDC, Capabilities, and Automation Agents

The HTTP framework separates route policy from authentication infrastructure. Route files declare requirements. `hostauth` constructs sessions, stores, OIDC handlers, application authorization services, capability services, programmatic credentials, and native endpoints. [S9][S10]

## 7.1 Browser OIDC flow

In OIDC mode, native Go handlers own:

```text
GET  /auth/login
GET  /auth/callback
GET  /auth/logout
POST /auth/logout
GET  /auth/session
```

The callback exchanges the authorization code, validates the provider response, maps issuer and subject to a local application user, and creates a server-side application session. The browser receives an opaque app-session cookie. Provider tokens remain server-side. [S9][S10]

This is the correct boundary. JavaScript sees the authenticated actor and redacted claims. It does not receive the OIDC client secret, refresh token, or signing keys.

## 7.2 Public URL versus listen address

The process may listen on `:8080` while users access `https://app.example.test`. OIDC callback URLs and secure-cookie policy must use the browser-visible origin, not the bind address. The configuration therefore separates public base URL, redirect URL, and listen address. [S9][S10]

This distinction should become a standard hosted environment field:

- Internal listen address belongs to the worker.
- Public origin belongs to the environment/domain binding.
- Redirect URIs are derived from the public origin under policy.

## 7.3 Five store families

Hostauth uses separate store interfaces for separate security concepts. They may share one Postgres connection pool, but they must not collapse into one generic key/value API. [S11]

| Store | Responsibility |
| --- | --- |
| Session | Opaque app sessions, CSRF state, metadata |
| Audit | Security-relevant route outcomes |
| AppAuth | App users, tenants, memberships, resources |
| Capability | Limited bearer-like grants, validation, and single-use consumption |
| ProgramAuth | Agents, API tokens, access/refresh families, device codes |

This is a strong model for the hosting platform. Persistence can be physically consolidated while interfaces preserve semantics.

## 7.4 App identity is local identity

An OIDC subject identifies a person at an issuer. Application authorization needs local state: tenants, memberships, resources, suspension, and roles. The appauth store maps external identity into the application's domain model. [S11]

The hosted platform has two identity populations:

1. Platform users who manage organizations, billing, and releases.
2. End users of each hosted application.

They should not share one issuer namespace, key set, or administration boundary merely because Tiny-IDP can serve both.

## 7.5 Capability tokens

The high-level `auth` module lets JavaScript issue and consume constrained capability tokens without direct database access. A token can name its type, resource, tenant, claims, expiry, creator, and single-use policy. The raw token is returned once; the store keeps a hash. [S13]

The issue route is authenticated and authorized. The consume route may be public because possession of the token is the capability, but it validates expected type and resource and atomically marks single-use tokens as consumed.

This pattern is useful beyond invitations:

- Email verification.
- One-time deployment approval.
- Passwordless action links.
- Limited webhook callbacks.
- Delegated file upload.

## 7.6 Programmatic agents

Programmatic authentication separates the durable agent principal, the bearer credential, and the grants. JavaScript can provision agents and issue API tokens through Go-owned builders. Raw token values appear only in issuance results; list and revoke APIs return redacted metadata. [S14]

A route intended for automation declares `express.agent()` and an action. The enforcer parses the token and checks the principal kind and grant before JavaScript runs.

```javascript
app.get("/agent/reports/:reportId")
  .auth(express.agent())
  .allow("report.read")
  .audit("agent.report.read")
  .handle((ctx, res) => {
    res.json({ reportId: ctx.params.reportId, agent: ctx.actor.id });
  });
```

This is directly relevant to coding agents that upload and release applications. Agent identity should remain distinct from human sessions.

## 7.7 Device authorization

Hostauth includes an application-owned device flow for coding agents. A browser user approves a device request, after which the application creates an agent and issues application-owned access and refresh credentials. These are not Tiny-IDP tokens even if the user authenticated through Tiny-IDP. [S17]

The latest production-hardening design identifies remaining single-node work:

- Derive a trustworthy client address behind a configured proxy.
- Apply rate limits and action policy to native device endpoints before durable work.
- Use a server-owned verification URI.
- Allow owners to inspect, deny, list, disable, and revoke their own agents.
- Make readiness probe actual SQL dependencies rather than configuration shape. [S17]

The document also distinguishes a later OAuth resource-server slice. The route contract already models exact issuer, resource, and scope requirements, but the first production verifier profile and end-to-end Tiny-IDP access-token flow remain a separate delivery. [S6][S17]

## 7.8 Single-node versus high availability

The current strict hostauth profile is intentionally single-node. It rejects in-memory persistent stores for critical state, requires secure sessions, and expects schema migration outside the serving process, but it does not claim distributed limiting or multi-replica OIDC transaction behavior. [S17]

The hosted platform should preserve this honesty. A profile must state whether it supports:

- One process.
- Multiple workers on one node.
- Multiple replicas with shared state.
- Cross-region failover.

### Key points

- OIDC login is Go-owned infrastructure; route authorization remains application policy.
- Provider tokens stay server-side and become a local opaque app session.
- Session, audit, app authorization, capability, and programmatic-auth stores are separate concepts.
- Agents, tokens, and grants are distinct objects.
- The current production hardening plan is a measured single-node profile, not an HA claim.

---

# 8. Guarded Outbound HTTP and Native Capabilities

Inbound HTTP is only half of a hosted application. Applications call payment APIs, email providers, storage services, model endpoints, and other internal services. Arbitrary outbound network access would undermine the module and entitlement model, so `go-go-goja` exposes a guarded `fetch` module. [S16]

## 8.1 Outbound HTTP is authority

The fetch module requires an explicit `allow: true`. It can restrict origins, set a default timeout, cap buffered response size, and limit credential sources. [S16]

```yaml
runtime:
  modules:
    - provider: host
      name: fetch
      config:
        allow: true
        allowedOrigins:
          - https://api.example.test
        timeout: 5s
        maxResponseBytes: 1048576
        credentials:
          allowFiles: true
          allowedFiles:
            - /run/secrets/example-token.json
```

This is the correct general rule for hosted modules: selecting the module is not enough. The module has a policy and a binding.

## 8.2 Go-owned credential sources

The API provides Go-owned bearer credential builders for literals, environment variables, and files. The client rejects arbitrary JavaScript auth maps for sensitive input so that policy checks and redaction remain in Go. [S16]

For the hosted platform, raw environment and filesystem sources should usually be replaced with a secret-reference capability:

```javascript
fetch.client()
  .baseUrl("https://api.example.test")
  .auth(fetch.auth.bearer().fromBinding("example-api"))
```

The worker would resolve `example-api` through its release bindings and inject the credential only into the outbound request.

## 8.3 Origin policy is not full egress policy

An origin allowlist at the module layer is useful but not sufficient for hostile tenants. The execution environment should also enforce network policy through a proxy or sandbox. The proxy can handle DNS rebinding resistance, private-address restrictions, TLS policy, request/response metering, and central audit.

```text
JavaScript fetch
  -> Go module validation
  -> release binding and origin policy
  -> egress proxy
  -> destination
```

## 8.4 Payments as a narrow module

A payments module should not expose a provider secret and generic fetch. It should expose reviewed operations:

- Create checkout session.
- Create customer portal session.
- Read bounded subscription state.
- Request a refund under policy.
- Verify and decode webhook events.

The module owns credentials, idempotency, allowed products, redirect domains, webhook signatures, and replay protection. JavaScript supplies business choices through typed inputs.

## 8.5 Capability descriptor

Every hosted native module version should declare:

| Field | Purpose |
| --- | --- |
| Canonical ID and version | Release identity and upgrades |
| Runtime ABI | Compatibility with worker binary |
| Permissions | Network, storage, secrets, effects |
| Configuration schema | Static non-secret module options |
| Binding schema | Required resources and secret references |
| Egress policy | Allowed service classes or origins |
| Limits | Calls, bytes, rows, concurrency |
| Metering dimensions | Billable usage |
| Type declarations | Agent and developer experience |
| Lifecycle | Build-time, runtime, or invocation-scoped |
| Risk class | Required isolation and approval |

**Decision:** Commercial entitlement, runtime selection, permission, quota, and resource binding are separate checks.

A customer may be entitled to use SQLite but have no database bound in a specific environment. A token may be entitled to call a payment module but lack the action grant for refunds. These distinctions should be visible in the data model.

### Key points

- Outbound HTTP is an explicit host capability.
- Origin limits, timeouts, body limits, and credential-source policy belong in Go.
- Secrets should be referenced through release bindings rather than copied into JavaScript variables.
- Sensitive integrations should expose narrow domain operations, not generic network plus a secret.
- Module metadata must support policy, metering, documentation, and reproducibility.

---

# 9. Browser Assets, Widget IR, and Server-Driven UI

A hosted platform needs a browser strategy. xgoja already establishes one boundary: browser bundles are built by browser tooling and included as assets; xgoja compiles JavaScript that runs inside Goja, not frontend code. [S1]

The platform should support two primary UI modes.

## 9.1 Static browser applications

Customers may build React, Vue, Svelte, or plain browser assets. The build plane runs standard frontend tooling in a separate sandbox, stores content-hashed artifacts, and serves them through a CDN or read-only asset module.

The Goja application supplies APIs and server actions. The browser application remains an ordinary browser program subject to a Content Security Policy and origin policy.

## 9.2 Widget IR pages

The Widget DSL research uses JavaScript to construct a serializable page intermediate representation. Go owns data access and execution. React owns rendering through a component registry. Actions and bindings are data rather than callbacks on the wire. [S21]

```text
Goja page handler
    -> versioned WidgetPage JSON
    -> Go validation
    -> browser WidgetRenderer
    -> approved component registry
```

A minimal node protocol has text, element, and component nodes. A production protocol should additionally define:

- Schema version.
- Renderer and component-registry digest.
- Component allowlist.
- Maximum depth, node count, text size, collection size, and total bytes.
- Typed properties.
- Action schema.
- Binding and interpolation rules.
- Accessibility requirements.
- Cache variation rules.

## 9.3 Actions refer to program handlers

A server action should be a reference to a named application handler, not a serialized function:

```json
{
  "type": "server",
  "handler": "checkout.start",
  "input": {
    "productId": { "from": "row.id" }
  }
}
```

The host resolves the handler in the release's application contract, validates input, applies route/action policy, enforces idempotency, invokes JavaScript, and records effects.

## 9.4 The current HTML UI DSL

`ui.dsl` constructs HTML nodes and includes a raw HTML primitive. It is useful for trusted applications and simple server-side pages. It should not be the default safe UI protocol for arbitrary tenants because raw HTML, scripts, styles, arbitrary attributes, and direct redirects require a much broader browser trust model. [S4]

A hosted product can expose two profiles:

- `widget.ui` as the normal constrained, versioned interface.
- `unsafe.html` as a privileged module requiring explicit approval and a restrictive CSP.

## 9.5 Why UI needs a versioned protocol

A coding agent can generate Widget IR against TypeScript declarations and component documentation. If the renderer is pinned in the release, the same source produces the same intended component contract. Without a pinned renderer and registry, a frontend deployment could silently reinterpret an old release.

**Decision:** The renderer version and registry digest are part of the release lock.

### Key points

- Browser bundles and Goja programs are different build products.
- Widget IR provides a constrained server-driven UI path for coding agents.
- Actions should reference named server handlers rather than serialize functions.
- Raw HTML should be privileged, not the default managed UI capability.
- Renderer identity belongs in the immutable release.

---

# Part III — From Repositories to a Hosting Platform

# 10. What go-go-host Contributes

`go-go-host` is an early hosting control plane. It already models users, organizations, memberships, sites, domains, quotas, capabilities, deployments, agents, keys, grants, nonces, deploy runs, audit events, and runtime status. It separates HTTP transport, control services, persistence, deployment validation, runtime lifecycle, and JavaScript-facing modules. [S18]

These concepts are worth preserving. The current in-process execution implementation is not the final production plane.

## 10.1 Valuable control-plane structure

The repository's layering rule is sound:

```text
HTTP handler / CLI adapter
    -> control service
        -> store / deploy / runtime subsystem
            -> database / filesystem / runtime
```

Authorization and product invariants belong in control services. HTTP handlers and dashboards are adapters, not enforcement points. Postgres migrations and sqlc provide a disciplined persistence path. [S18]

## 10.2 Immutable deployment records

A deployment record is reserved before validation so artifact paths and version identity are stable. Upload and activation are separate. A candidate is unpacked, loaded in a dry-run runtime, smoke-tested, then marked validated or rejected. Activation creates a new runtime and checks health before swapping traffic. [S18]

The principles are correct:

- Candidate identity exists before validation.
- Validation does not immediately affect traffic.
- Live traffic changes only after a health check.
- Previous versions remain available for rollback.

## 10.3 Agent identity and grants

Agents have separate machine identities and keys. Grants scope them to organizations and sites, allowed channels and paths, and activation rights. Nonces provide replay protection. This is the correct foundation for coding-agent release workflows. [S18]

## 10.4 The current execution subsystem

The current `SiteRuntime` opens a per-site SQLite database, builds a Goja runtime, registers a small set of modules, loads every `.js` file in lexical order, and serves routes through a site-specific web host. The `Supervisor` maps hosts and sites to active runtimes and swaps the map after health checking a candidate. [S18]

This implementation was useful for proving the product loop. It should now be replaced by the richer `gojahttp` and xgoja framework rather than extended in parallel.

The duplication is important:

| Current go-go-host subsystem | Existing go-go-goja capability |
| --- | --- |
| `internal/sitejs/web` route host | `pkg/gojahttp.Host` |
| Local Express registrar | `modules/express` plus HTTP provider |
| Anonymous session DTO | `gojahttp` hostauth session system |
| HTML `ui.dsl` | Existing module plus Widget DSL direction |
| Manual module selection | xgoja providers and runtime plans |
| Manual script directory walk | xgoja source graph and generated application loading |

**Decision:** go-go-host should consume generated runtime profiles and `gojahttp`; it should not maintain a second HTTP framework.

## 10.5 Control plane versus worker plane

The daemon currently contains both the control plane and active customer VMs. A hostile loop, native module defect, or memory exhaustion can therefore affect the API that manages all customers.

The target split is:

```text
Control-plane API and database
    -> desired release and worker records
    -> worker scheduler / reconciler
    -> isolated worker processes or pods
    -> router sends traffic to ready release workers
```

The control plane should not import customer application packages or open customer SQLite files.

### Key points

- go-go-host already has valuable product entities and service layering.
- Upload, validation, and activation are correctly separated in concept.
- Agent keys and grants are a strong foundation for coding-agent workflows.
- The current JavaScript host duplicates a narrower version of go-go-goja's HTTP framework.
- The control plane and tenant execution must become separate processes.

---

# 11. Releases, Deployments, and Traffic Generations

A single “deployment” object is often asked to represent source code, a build attempt, an artifact, environment configuration, live traffic, and running processes. That overload makes rollback and audit ambiguous. The hosted platform should separate these objects.

## 11.1 The release vocabulary

| Object | Meaning |
| --- | --- |
| Source revision | Exact uploaded archive or Git commit |
| Build | One attempt to compile a source revision under a runtime profile |
| Artifact | Immutable signed executable/image plus source bundle, SBOM, and provenance |
| Release | Artifact plus environment configuration, module lock, bindings, policy, and entitlement snapshot |
| Deployment | One attempt to make a release available in an environment |
| Traffic generation | Immutable routing decision assigning percentages to releases |
| Worker revision | Concrete running instance or pool for one release |

A release is the unit that should be reproducible and rollbackable. A deployment is an operation that may fail. A traffic generation is the live decision.

## 11.2 Candidate lifecycle

```text
source revision created
    -> build queued
    -> build succeeded
    -> artifact signed
    -> release assembled
    -> policy approved
    -> preview workers started
    -> smoke checks passed
    -> release ready
    -> traffic generation committed
    -> previous release draining
    -> previous release retired
```

Each transition records actor, inputs, expected prior state, output digests, and audit event.

## 11.3 Database as source of truth

The current supervisor swaps in-memory maps and then updates the database. If the database update fails, traffic and persisted state can disagree. The target platform uses a database compare-and-swap for the traffic generation, writes an outbox event in the same transaction, and lets routers reconcile. [S18]

```text
transaction:
  verify expected current generation
  insert new traffic generation
  update environment current generation
  insert audit event
  insert outbox event
commit
```

The router may briefly lag the database, but it is reconciling toward one authoritative state.

## 11.4 Draining

A replaced worker should stop receiving new requests and continue serving in-flight requests until completion or a drain deadline. Only then should its runtime close.

```text
ready candidate
    -> publish new generation
    -> router stops new traffic to old release
    -> wait for in-flight count = 0
    -> cancel background work
    -> close runtime
    -> kill after hard deadline
```

## 11.5 Rollback

Rollback creates a new traffic generation pointing to a named earlier release. It does not mutate history and does not choose “previous validated” implicitly.

Database compatibility must be explicit. A code rollback may be unsafe after a destructive migration. Releases should declare schema compatibility ranges and use expand/contract migrations. Backup restore is a separate privileged operation.

## 11.6 Artifact contents

A release artifact should include:

- Exact source archive.
- Compiled JavaScript/TypeScript bundle.
- Serializable application contract.
- Callback-registry fingerprint.
- Runtime profile and module lock.
- TypeScript declarations used by the build.
- Static assets or asset digest.
- Renderer/Widget registry identity.
- Tests and build-check results.
- SBOM and provenance.
- Signature.

### Key points

- Source, build, artifact, release, deployment, traffic, and worker are different objects.
- The database should own the live traffic decision.
- Routers and workers reconcile desired state rather than invent it.
- Rollback creates a new immutable traffic generation.
- Database compatibility and code rollback must be designed together.

---

# 12. Module Catalogs, Subscriptions, Entitlements, Quotas, and Bindings

A commercial module system introduces vocabulary that technical registries do not currently provide. `xgoja` calls optional provider extension interfaces “capabilities,” while go-go-host uses site capabilities as module allow flags. The platform needs more precise terms.

## 12.1 Six separate concepts

| Concept | Definition |
| --- | --- |
| Provider extension | Trusted Go hook contributed to xgoja composition |
| Runtime module | JavaScript-visible API selected into a profile |
| Permission | Authority granted to executing code |
| Entitlement | Commercial right held by an account |
| Quota | Allowed amount of resource or operation |
| Binding | Concrete resource or secret connected to an environment |

Rename xgoja's generic `PackageCapability` concept to `ProviderExtension` or `ProviderContribution` before adding hosted permissions. The current name is technically valid but will collide with product security language. [S1]

## 12.2 Module version record

A catalog entry should contain:

```text
module identity
  id, version, aliases, provider package, checksum, ABI

security contract
  permissions, risk class, egress, secret types, effects

resource contract
  required bindings, state ownership, migration behavior

execution contract
  lifecycle, concurrency, timeouts, max payloads

commercial contract
  feature/SKU, metering dimensions, quota classes

user contract
  TypeScript declarations, docs, examples, deprecation status
```

Aliases such as `database`, `db`, and `sqlite` resolve to one canonical module version and one entitlement. An alias must never bypass policy.

## 12.3 Entitlement resolution

Release creation performs entitlement checks:

```text
requested modules
    -> canonical catalog resolution
    -> exact versions
    -> account entitlement check
    -> environment policy check
    -> resource binding resolution
    -> effective permission calculation
    -> build profile
    -> immutable entitlement snapshot in release
```

Workers do not call the billing provider. They verify that the signed release contains an approved entitlement snapshot and that the control plane has not suspended it.

## 12.4 Subscription changes

A downgrade policy should be explicit:

- New releases requiring the removed module are blocked immediately.
- Existing releases may continue for a configured grace period.
- A security or abuse suspension may stop them immediately.
- Re-enabling service produces a new control-plane decision, not a mutated artifact.

This prevents a billing webhook from unpredictably changing a running VM's module set.

## 12.5 Quotas and metering

Quotas can apply at several levels:

| Level | Examples |
| --- | --- |
| Build | Source bytes, build minutes, artifact bytes |
| Release | Module count, domains, bound resources |
| Worker | Memory, CPU, process count, pool size |
| Invocation | Timeout, output bytes, capability calls, DB rows |
| Monthly usage | Requests, compute milliseconds, egress bytes, storage |

Metering events should be append-only and idempotent. Billing aggregation is downstream of enforcement. A failed billing export must not erase usage evidence.

## 12.6 SQLite as module and resource

SQLite is not only a JavaScript API. It is also a persistent file, backup policy, schema state, and placement constraint.

- The **module** exposes query and transaction operations.
- The **resource instance** owns the database file and backups.
- The **binding** attaches an environment to the resource.
- The **worker policy** ensures a single active writer when local storage is used.

A product should not imply arbitrary horizontal scale for a local SQLite file. It can provide a well-defined single-active-worker profile and separate scalable database products.

### Key points

- Provider hooks, modules, permissions, entitlements, quotas, and bindings must not share one field.
- Module versions need security, resource, execution, commercial, and user-facing metadata.
- Entitlements are resolved when a release is created and captured immutably.
- Subscription changes do not mutate a running runtime profile.
- Stateful modules require explicit resource and placement semantics.

---

# 13. Agent-Driven Releases, Approval, and Audit

Coding agents are expected users of the platform. The release system should assume that an agent can generate valid code quickly and can also make an incorrect authority request quickly. The safety model cannot depend on a human reading every line.

## 13.1 Agent identity

An agent has:

- Durable principal ID.
- Public keys and key lifecycle.
- Organization/project/environment grants.
- Allowed source paths and channels.
- Permission to build, propose, promote, or rollback.
- Optional expiry.
- Nonce and replay-protection state.

Human credentials are not reused for automated deployment.

## 13.2 Signed proposal payload

A release proposal signature should cover a canonical payload:

```json
{
  "organization": "o1",
  "project": "p1",
  "environment": "production",
  "sourceDigest": "sha256:...",
  "artifactDigest": "sha256:...",
  "releaseDigest": "sha256:...",
  "expectedTrafficGeneration": 41,
  "runtimeProfileDigest": "sha256:...",
  "policyDigest": "sha256:...",
  "bindingsDigest": "sha256:...",
  "migrationDigest": "sha256:...",
  "idempotencyKey": "...",
  "timestamp": "...",
  "nonce": "..."
}
```

The signature proves who submitted the proposal and what bytes were proposed. It does not prove that the proposal is safe. The server recomputes policy and entitlement decisions.

## 13.3 Authority diff

A release review should show authority changes before code changes:

```text
+ module payments@1.2.0
+ permission network.egress: payment-provider
+ binding stripe-production
+ effect payment_session_create
~ database schema 12 -> 13
- module legacy-mailer@0.8.1
```

Require explicit approval for:

- New native modules.
- New secrets or bindings.
- New egress destinations.
- Identity and payment authority.
- Unsafe HTML.
- Destructive migrations.
- Increased time, memory, concurrency, or body limits.
- Major module upgrades.

## 13.4 Compare-and-swap promotion

A promotion request includes the traffic generation the agent expects. If another actor has promoted a release since the agent prepared its proposal, the operation fails rather than silently overwriting the newer state.

## 13.5 Audit durability

Audit events should be append-only and transactionally coupled to state mutations. At minimum they record:

- Actor type, principal, key ID.
- Organization, project, environment.
- Request and idempotency IDs.
- Source, artifact, release, profile, and policy digests.
- Before and after traffic generation.
- Approval result.
- Worker rollout result.
- Failure reason.

The current repositories often ignore audit sink errors. The hosted product should classify operations:

- **Best-effort request audit** may continue when the sink is degraded, with a security event.
- **Control-plane mutation audit** must commit with the mutation through an outbox or fail.

## 13.6 Release evidence

A coding agent should be able to attach machine-readable evidence:

- Static route inventory.
- Program contract validation.
- Unit tests using fake capabilities.
- Preview smoke results.
- Browser screenshots or accessibility results for Widget pages.
- Database migration checks.
- Dependency and vulnerability reports.
- Authority diff.

This evidence is part of the release record and can be re-evaluated by policy.

### Key points

- Agents are first-class machine principals, not disguised users.
- Signatures authenticate proposals; server policy still decides.
- Authority diffs make risky changes visible before line-level review.
- Promotion uses compare-and-swap against the expected traffic generation.
- Control-plane mutation audit must be transactionally durable.

---

# 14. The Execution Plane and Isolation

Goja constrains the JavaScript language environment, but it is not an operating-system sandbox. A native module is Go code in the worker process. A defect or excessive allocation can affect the process even when JavaScript has no `fs` or `exec` module.

## 14.1 Worker boundary

The target execution unit is one tenant release in an isolated worker process or sandbox.

```text
router
  -> release worker group
       -> bounded pool of exclusive Goja runtimes
       -> capability/resource brokers
       -> external resources
```

A worker contains only the native modules selected by the runtime profile. It receives no control-plane database credentials.

## 14.2 One invocation per VM

A VM worker is acquired exclusively. One request or job invokes one named handler. The worker is released only if the invocation completed within policy and cleanup succeeded. Any interrupt, panic, protocol violation, or uncertain state poisons the worker.

This follows the Tiny-IDP pool design, which creates equivalent runtime images from an immutable artifact and replaces unsafe workers. [S20]

## 14.3 Warm pools

A warm pool belongs to one release generation. Do not mix tenants or releases in one VM pool.

Benefits:

- Source and module state are loaded once per worker.
- Callback registry fingerprint is verified on load.
- Invocation-scoped capabilities can be installed and removed.
- A poisoned worker can be replaced from the same artifact.

Pool saturation should return a controlled overload response or queue according to the surface. It should not start unbounded goroutines or VMs.

## 14.4 Operating-system limits

Each worker should have:

- Read-only root filesystem.
- Dedicated unprivileged UID.
- CPU, memory, PID, file, and log limits.
- No host filesystem mounts.
- No network by default.
- Egress through a policy proxy.
- Ephemeral writable space except explicit resource mounts.
- Short-lived workload identity.
- Hard process termination after deadline.

A sandbox runtime such as gVisor can strengthen tenant separation. The exact mechanism is an infrastructure choice; the architectural requirement is that hostile tenant code cannot share the control-plane process.

## 14.5 Stateful placement

A local SQLite resource requires placement and lease rules. A worker scheduler should acquire a lease before mounting the resource. A second worker cannot become active on another node until the first lease expires or is revoked safely.

```text
release requests sqlite binding
    -> scheduler obtains resource lease
    -> worker mounts volume
    -> readiness verifies DB
    -> router enables traffic
```

## 14.6 Worker protocol

The control plane should communicate desired state, not execute callbacks directly. A worker protocol may include:

- Load release.
- Report readiness.
- Invoke handler.
- Begin drain.
- Report in-flight count.
- Stop release.
- Export metrics and structured logs.

The signed release manifest is verified by the worker before loading source.

### Key points

- Goja is a language/runtime boundary, not the final tenant isolation boundary.
- One tenant release belongs in a separate worker process or sandbox.
- VM workers are exclusive and discarded after uncertain execution.
- Warm pools are release-specific.
- Stateful resources require leases and explicit placement semantics.

---

# Part IV — A General Application Program Model

# 15. What Tiny-IDP Teaches About Safe JavaScript Programs

The Tiny-IDP scripting branch addresses a different product, but it solves the hardest general problem: how to let JavaScript implement real behavior while Go retains protocol authority.

## 15.1 Serializable program, separate callbacks

`idpprogram.Program` contains workflows, providers, lambda specifications, schemas, capabilities, and declarative tests. It contains no Goja dependency and no JavaScript function values. Callbacks are stored separately in the runtime by stable lambda ID. [S19][S20]

This separation produces two artifacts:

1. A serializable contract that tools can validate and inspect.
2. A runtime callback registry that only a VM owner can invoke.

## 15.2 Lambda contract

Each lambda declares:

- ID and kind.
- Input and output schema.
- Allowed outcome kinds.
- Required capability versions.
- Allowed native effects.
- Timeout.
- Maximum capability calls.
- Maximum output bytes.
- Source location. [S19]

The metadata is enforcement data. A lambda cannot call an undeclared capability. A result outside the allowed outcomes or output schema invalidates the invocation.

## 15.3 Compiler runtime

The compiler executes source in an isolated runtime that exposes only the Tiny-IDP builder module. Ambient file loaders and default modules are disabled. It applies source and time limits, materializes the program, validates it, computes fingerprints, and creates an immutable artifact. [S20]

At worker load, the same source must reproduce the same program and callback registry. A mismatch fails activation.

## 15.4 Invocation-scoped capabilities

A worker receives capability bindings for one invocation. Each binding has an ID/version, input and output byte limits, and a Go function. Capability calls create promises, perform native work, and settle back on the runtime owner. The binding counts calls and becomes inactive when the invocation ends. [S20]

This prevents a callback from retaining a capability object and using it later under a different request.

## 15.5 Secrets and evidence

Secret values are represented by opaque handles. Native-verified evidence, such as a verified email, is injected by the executor and cannot be forged by returning a similar JavaScript object. [S19][S20]

The general platform can apply the same distinction:

- **Input data** can come from the request.
- **Secret handles** refer to host-owned values.
- **Evidence** proves a native verification step occurred.
- **Effects** request native state changes.

## 15.6 Structured outcomes

Tiny-IDP handlers return outcome families such as continue, present, challenge, commit, complete, deny, skip, and error. Exceptions are infrastructure errors, not policy denials. [S19]

This explicit result model is more auditable than arbitrary side effects. It also supports durable workflows.

## 15.7 General lesson

**Decision:** The agent-facing application API should compile JavaScript into a serializable program contract plus named callbacks.

Express remains valuable, especially for existing applications, but a general hosted platform benefits from a higher-level program description for functions, pages, actions, schedules, and workflows.

### Key points

- Safe scripting separates a serializable program contract from VM-owned callbacks.
- Lambda metadata is enforced, not merely documented.
- Compilation runs in an isolated collector runtime.
- Capabilities, secrets, evidence, and effects are distinct boundary types.
- Worker load verifies fingerprints before activation.

---

# 16. A Generic Hosted Application Contract

The Tiny-IDP contract can be generalized into a repository-neutral application model.

## 16.1 Program shape

```go
type Program struct {
    APIVersion   string
    Name         string
    Routes       map[string]RouteSpec
    Functions    map[string]HandlerSpec
    Pages        map[string]PageSpec
    Actions      map[string]HandlerSpec
    Schedules    map[string]ScheduleSpec
    Workflows    map[string]WorkflowSpec
    Schemas      map[string]Schema
    Capabilities map[string]CapabilityRequirement
    Resources    map[string]ResourceRequirement
    Tests        []ProgramTest
}
```

The contract is not required to replace `RoutePlan`. A route specification can contain or compile to the existing `gojahttp.RoutePlan`. This preserves the mature enforcer while adding release-wide static analysis.

## 16.2 Handler contract

```go
type HandlerSpec struct {
    ID                   string
    Kind                 HandlerKind
    InputSchema          string
    OutputSchema         string
    RequiredCapabilities []CapabilityRequirement
    AllowedEffects       []EffectKind
    AuthPlan             *gojahttp.RoutePlan
    Idempotency          IdempotencyPolicy
    Budget               InvocationBudget
    SourceLocation       SourceLocation
}
```

Budgets should cover:

- Wall-clock and CPU time.
- Input, output, and log bytes.
- Capability calls and concurrency.
- Database rows and result bytes.
- Network requests and bytes.
- Effects and continuation payload size.

## 16.3 JavaScript API

```javascript
const A = require("@gogo/app").v1;

module.exports = A.program("shop", app => {
  app.http("catalog.home", {
    method: "GET",
    path: "/",
    public: true,
    output: "widget.page/v3",
    capabilities: ["catalog.read@1"],
    budget: {
      timeoutMs: 100,
      maxCapabilityCalls: 10,
      maxOutputBytes: 262144
    }
  }, async ctx => {
    const products = await ctx.cap.catalog.read({ limit: 20 });
    return ctx.page.shop({ products });
  });

  app.action("checkout.start", {
    input: "checkout.request/v1",
    output: "checkout.result/v1",
    capabilities: ["payments.checkout.create@1"],
    effects: ["payment_session_create"]
  }, async ctx => {
    return ctx.cap.payments.createCheckout(ctx.input);
  });
});
```

The compiler registers callback IDs, validates declarations, emits the route inventory and module requirements, and runs declarative tests with fake capabilities.

## 16.4 Integration with gojahttp

At activation:

```text
Program.RouteSpec
    -> compile/validate RoutePlan
    -> register planned route in gojahttp.Host
    -> route handler invokes named application lambda
    -> lambda result converted to response or Widget page
```

The enforcer remains the sole interpreter of HTTP security policy. The generic application executor owns handler schemas, budgets, capabilities, and effects.

## 16.5 Compatibility Express profile

Existing Express applications can remain supported:

- The route script registers planned routes directly.
- xgoja static analysis inventories native imports.
- Runtime budgets apply around each HTTP callback.
- Raw routes are disabled.
- A route-descriptor export becomes part of the release.

The new program API is the preferred agent-facing profile, not an immediate requirement for all existing code.

## 16.6 Declarative tests

A program test names a handler, input, fake capability outputs, expected outcome, and optional effect assertions. It contains no arbitrary host authority.

```javascript
app.test("catalog empty state", {
  handler: "catalog.home",
  input: {},
  fakes: {
    "catalog.read": []
  },
  expect: {
    outcome: "complete",
    outputSchema: "widget.page/v3"
  }
});
```

These tests give coding agents a fast release gate before a worker is started.

### Key points

- The generic program contract should compile to existing route plans rather than replace the enforcer.
- Handler schemas, budgets, capabilities, effects, and idempotency are release metadata.
- A compatibility Express profile can coexist with a higher-level agent-facing API.
- Declarative tests are bounded artifacts that the platform can run with fake capabilities.

---

# 17. Durable Workflows and Explicit Continuations

An HTTP request can await a bounded database or network call. It cannot keep a JavaScript promise alive across a browser form, process restart, release rollout, or worker relocation. Durable workflows require explicit continuation state.

## 17.1 In-request await

This is safe when bounded:

```javascript
async function submitted(ctx) {
  const member = await ctx.cap.community.lookup({ email: ctx.input.email });
  return member ? ctx.complete(member) : ctx.deny("not_a_member");
}
```

The request remains open. The capability has a deadline and call budget. Promise settlement occurs through the runtime owner.

## 17.2 Browser boundary

A form presentation returns normally:

```javascript
return ctx.present.form({
  schema: "signup.form/v1",
  resume: "signup.submitted"
});
```

Go validates the presentation, stores a continuation, renders the form, and releases the VM worker. The later POST loads the continuation and invokes `signup.submitted` as a fresh call.

## 17.3 Continuation record

A continuation should pin:

- Program/release digest.
- Workflow and resume handler.
- Input and carry schema versions.
- Authenticated actor and tenant binding where applicable.
- Browser/session/CSRF binding.
- Original validated request digest.
- Evidence and secret references.
- Creation, expiry, consumption, and terminal outcome.

It must not serialize a Goja heap, closure, promise resolver, raw password, cookie, or database transaction.

## 17.4 Release changes during a workflow

When a new release is promoted before a continuation resumes, the system needs an explicit policy:

- Resume under the pinned old release while it remains retained.
- Migrate the continuation through a declared schema adapter.
- Expire the continuation and restart the workflow.

Implicitly invoking the new handler with old carry data is unsafe.

## 17.5 Identity workflows

Tiny-IDP should remain the identity kernel. Tenant-authored identity workflows can run in the isolated worker plane through a typed remote protocol:

```text
Tiny-IDP validates OAuth/browser request
    -> calls pinned workflow release with bounded event
    -> receives structured outcome
    -> applies native challenge/effect
    -> stores continuation
    -> issues protocol artifacts
```

JavaScript never validates redirect URIs, PKCE, JWTs, cookies, codes, or signing keys. [S19]

### Key points

- An in-request promise is not a durable workflow state.
- Browser and external waits use explicit versioned continuations.
- Continuations pin release and schema identity.
- Go owns replay protection, secrets, evidence, and irreversible effects.
- Identity protocol authority stays in Tiny-IDP even when workflow behavior is scripted.

---

# Part V — Evaluation and Implementation Plan

# 18. What to Preserve, Change, Retire, and Add

This chapter converts the architectural reasoning into repository-level decisions.

## 18.1 Preserve

### go-go-goja and xgoja

Preserve:

- Owned runtime, event loop, runtime owner, call context, closers.
- Explicit provider and runtime-module composition.
- xgoja v2 sources, commands, artifacts, and static import graph.
- TypeScript declaration generation.
- `gojahttp.Host`, planned routes, staged builders, `Enforcer`, mounts, and HTTP provider.
- Hostauth separation of sessions, audit, appauth, capabilities, and programauth.
- Guarded fetch and Go-owned credential builders.
- Generated runtime packages and host-service injection.

### go-go-host

Preserve:

- Organizations, memberships, projects/sites, environments, domains.
- Agents, keys, grants, nonces, deploy runs.
- Quotas, audit vocabulary, Postgres/sqlc layering.
- Separate upload, validation, activation, and rollback concepts.
- Candidate smoke checks and immutable deployment history.

### Tiny-IDP

Preserve:

- Strict OAuth/OIDC kernel.
- Public embedding boundaries and production validation.
- Serializable program and lambda contracts.
- Isolated compiler runtime and fingerprints.
- Exclusive worker pools and poisoned-worker disposal.
- Opaque secrets, native evidence, structured outcomes and effects.
- Explicit browser continuations.

### Widget DSL

Preserve:

- Versioned serializable UI IR.
- JavaScript composition, Go data/execution, React rendering.
- Data-driven actions and bindings.
- Component registry and browser validation.

## 18.2 Change

### go-go-goja

- Add hosted module descriptors and exact module locks.
- Rename provider extension “capabilities.”
- Formalize interruptible invocation and poison state in the runtime owner layer.
- Freeze registries after build.
- Replace opaque host-service string keys with namespaced typed keys where possible.
- Make body, response, DB, and log limits profile-configurable.
- Define stricter audit durability options.

### go-go-host

- Replace `internal/sitejs/web` and local Express/UI copies with `gojahttp` and xgoja providers.
- Replace recursive script loading with compiled source/program artifacts.
- Persist and enforce the exact effective module and permission set.
- Move tenant execution into isolated workers.
- Replace in-memory traffic swaps with transactional traffic generations and reconciliation.
- Move artifacts from mutable local paths to content-addressed object storage.
- Split deployment records into source, build, artifact, release, rollout, and worker entities.

### Tiny-IDP

- Extract generic program, schema, budget, artifact, and worker abstractions into neutral packages.
- Keep identity-specific effects, evidence, and continuations in Tiny-IDP.
- Add a remote workflow executor for tenant-authored identity behavior.
- Fix pool close semantics so a timeout does not leave resources permanently uncloseable.

### Widget DSL

- Publish a standalone wire-format and validator.
- Pin renderer and registry versions in releases.
- Link server actions to named program handlers.
- Put strict limits on nodes, depth, data, and output bytes.
- Keep raw HTML outside the normal safe profile.

## 18.3 Retire from the primary platform path

- Control plane and tenant VMs in one process.
- `DefaultCapabilities()` on hosted runtime creation.
- One shared site VM serving unbounded concurrent requests.
- Recursive execution of every `.js` file.
- Response timeout without VM interruption.
- Raw routes in production.
- Generic network plus provider secret for payments.
- Anonymous opaque cookie IDs presented as authentication.
- Local mutable filesystem paths as release identity.

## 18.4 Add

- Module catalog, versions, dependencies, entitlements, and pricing features.
- Resource instances and bindings.
- Source revisions, builds, artifacts, attestations, and release locks.
- Traffic generations, allocations, and rollout events.
- Worker revisions, leases, invocations, logs, and usage events.
- Policy decisions, approvals, idempotency records, and transactional outbox.
- Platform identity and separate application identity realms.
- Egress proxy and secret broker.

### Key points

- The target is a refactoring and integration of strong existing components, not a rewrite from zero.
- The most important reuse decision is adopting `gojahttp` throughout go-go-host.
- The largest new subsystem is the isolated worker and release-control model.
- Tiny-IDP's generic scripting mechanisms should be extracted without weakening the identity kernel.

---

# 19. Current Risks and Missing Invariants

The current repositories are active implementation projects, not a finished multi-tenant service. The following risks should be treated as release blockers for unrelated customer code.

## 19.1 Effective capabilities in go-go-host

Bundle validation calculates requested and effective capabilities, but runtime creation currently uses default capabilities rather than the persisted effective set. Database modules are registered regardless of the database boolean. This breaks the connection between policy and execution. [S18]

**Required invariant:** The signed release lock is the only source of runtime modules and permissions, and the worker verifies it before constructing the runtime.

## 19.2 Execution timeout

HTTP timeout wrappers can stop response waiting without interrupting the VM. [S3][S5][S18]

**Required invariant:** Every invocation has an interrupt path, poison state, process-level deadline, and hard kill.

## 19.3 Activation consistency

The current supervisor can swap in-memory routing before persisting the active deployment. [S18]

**Required invariant:** Traffic changes are committed transactionally and routers reconcile the committed generation.

## 19.4 Archive ingestion

The current deployment validator buffers the archive and entries in memory before fully enforcing uncompressed quotas, and canonical path collisions need stronger handling. [S18]

**Required invariant:** Archive scanning is streaming, size-bounded, duplicate-safe, path-safe, and staged atomically.

## 19.5 Audit errors

Several code paths ignore audit write failures. [S7][S18]

**Required invariant:** Control-plane mutation audit is transactionally durable; request audit has an explicit degradation policy.

## 19.6 Trusted proxy identity and readiness

The July 18 hostauth hardening analysis found inconsistent client-IP interpretation between audit and rate limiting, native device endpoints outside the planned enforcer, and readiness that reported configuration rather than SQL reachability. [S17]

**Required invariant:** One canonical request identity is derived once, native routes have their own bounded policy perimeter, and readiness probes actual dependencies.

## 19.7 Pool shutdown

The Tiny-IDP pool can set itself closed, return on a close timeout before canceling/closing workers, and then reject later cleanup attempts. [S20]

**Required invariant:** “not accepting work” and “resources fully closed” are separate states; cleanup is retryable and idempotent.

## 19.8 UI authority

The generic HTML DSL can emit raw HTML and broad attributes. [S4]

**Required invariant:** Arbitrary tenant UI uses a validated Widget protocol or a separately approved unsafe HTML profile.

### Key points

- Current gaps are primarily broken links between declared policy and actual execution.
- Timeouts, activation, archive parsing, audit, proxy identity, and cleanup require explicit invariants.
- The HTTP framework itself is a major asset; the target should harden and integrate it rather than discard it.

---

# 20. Implementation Sequence for an Intern Team

The implementation should advance through coherent vertical slices. Each phase proves one invariant and leaves the system runnable.

## Phase 0 — Baseline and terminology

Deliverables:

- Architecture decision records for the four planes.
- Glossary adopted in code and docs.
- Current route, module, and entity inventory.
- Integration test proving go-go-host can run a `gojahttp` planned public route.

Exit evidence:

- No new use of ambiguous “capability” for both provider extensions and permissions.
- One documented source of truth for route policy and runtime module selection.

## Phase 1 — Replace the duplicate HTTP host

Deliverables:

- go-go-host worker prototype using xgoja/gojahttp HTTP provider.
- Planned public and authenticated routes.
- Raw routes rejected.
- Existing static assets and SQLite binding wired through host services.
- Request timeout paired with VM interruption and worker disposal.

Exit evidence:

- Route inventory lists public/auth/resource/action/CSRF/audit/rate-limit policy.
- A blocked infinite loop does not block the control plane.

## Phase 2 — Artifact and release model

Deliverables:

- Source revision, build, artifact, release, traffic generation tables.
- Content-addressed object storage.
- Runtime lock with exact module versions.
- Signed artifact verification in worker.
- Transactional outbox.

Exit evidence:

- The same release can be loaded on a clean worker and reproduces the same program/profile fingerprints.
- Traffic promotion is compare-and-swap and auditable.

## Phase 3 — Isolated workers

Deliverables:

- Separate worker binary/process.
- Release-specific runtime pool.
- Resource and secret bindings.
- CPU, memory, PID, filesystem, network, log, and invocation limits.
- Drain and hard-stop protocol.

Exit evidence:

- A worker crash or OOM does not interrupt the control-plane API.
- One tenant cannot address another tenant's worker or resource.

## Phase 4 — Generic application contract

Deliverables:

- Neutral program, schema, handler, budget, test, artifact, and worker packages extracted from Tiny-IDP patterns.
- Compiler collector module.
- HTTP route specs compiled to `RoutePlan`.
- Named actions and Widget page handlers.
- Declarative test runner.

Exit evidence:

- Agent-authored source produces a deterministic contract and callback registry.
- Invalid schemas, undeclared capabilities, or illegal outcomes fail before activation.

## Phase 5 — Module catalog and subscriptions

Deliverables:

- Module/version catalog.
- Entitlement and quota model.
- Release-time entitlement snapshot.
- SQLite module/resource/binding split.
- Usage event pipeline.

Exit evidence:

- A user without an entitlement cannot create a release containing the module.
- Removing an entitlement follows the documented grace/suspension policy without mutating artifacts.

## Phase 6 — Platform and application identity

Deliverables:

- Platform OIDC for customer teams.
- Managed application realm and external OIDC modes.
- Programmatic agent lifecycle.
- Trusted proxy identity and SQL readiness.
- Remote Tiny-IDP workflow executor for selected scripted flows.

Exit evidence:

- Platform users and application users have separate issuer and authorization boundaries.
- Agent and browser routes reject the wrong principal types.

## Phase 7 — Widget UI and payments

Deliverables:

- Versioned Widget wire protocol and validator.
- Renderer/registry lock.
- Named server actions.
- Narrow payments module and verified webhook evidence.

Exit evidence:

- Widget pages pass schema, size, accessibility, and browser tests.
- Payment secrets never enter JavaScript or logs.

## Phase 8 — Distributed execution

Deliverables:

- Multi-node scheduler and worker leases.
- Canary and percentage traffic.
- Distributed-safe resources and rate-limit profiles.
- Central metrics, logs, traces, and usage aggregation.

Exit evidence:

- Node loss triggers reconciliation without double-activating single-writer resources.
- Rollout and rollback work through traffic generations across nodes.

### Key points

- Each phase proves a complete invariant rather than adding broad scaffolding.
- The first vertical slice is reuse of `gojahttp` in an isolated worker.
- Reproducible releases and traffic generations precede commercial module complexity.
- Generic scripting extraction follows, rather than blocking, the first hosted HTTP slice.

---

# 21. Worked Trace: From Source to an Authenticated Response

This chapter connects the major components in one concrete sequence.

## 21.1 Build

A coding agent uploads:

```text
app.ts
web/dist/*
app.manifest.json
```

The manifest requests:

```json
{
  "runtime": "web",
  "modules": ["express@1", "sqlite@1", "widget.ui@3"],
  "entrypoint": "app.ts"
}
```

The build plane:

1. Stores the exact source archive and digest.
2. Resolves module versions through the catalog.
3. Checks entitlements and environment policy.
4. Generates an xgoja v2 specification using curated providers.
5. Validates the static source graph.
6. Compiles TypeScript.
7. Runs the program collector and declarative tests.
8. Emits route inventory, program contract, static assets, runtime lock, SBOM, and provenance.
9. Signs the artifact.

## 21.2 Release

The control plane binds:

- `sqlite.primary` to database resource `db_17`.
- `identity.default` to managed realm `realm_9`.
- Public domain `shop.example.test`.
- Widget renderer `renderer_3.4.1`.

It creates release `rel_42` with an immutable entitlement and policy snapshot.

## 21.3 Activation

The worker scheduler:

1. Acquires the SQLite lease.
2. Starts a sandboxed worker with the profile-specific binary.
3. Verifies the release signature and module lock.
4. Creates a runtime factory.
5. Loads a bounded pool of runtime images.
6. Registers planned routes into `gojahttp.Host`.
7. Mounts native OIDC and readiness handlers.
8. Runs smoke requests.
9. Reports ready.

The control plane commits traffic generation 42 pointing 100% to `rel_42`.

## 21.4 Browser login

The browser requests `/account` without a session.

```text
GET /account
  -> route match
  -> pre-auth rate limit
  -> session authenticator
  -> no actor
  -> 401
```

The frontend sends the user to `/auth/login`. The native OIDC handler redirects to the issuer. After callback validation, the host creates a local session and returns an opaque cookie.

## 21.5 Authenticated route

The browser sends:

```http
PATCH /orgs/o1/projects/p7
Cookie: sid=opaque
X-CSRF-Token: ...
Content-Type: application/json

{"name":"New name"}
```

The host executes:

```text
body limit and JSON parsing
  -> request DTO
  -> planned route lookup
  -> pre-auth rate limit by IP and route
  -> session lookup
  -> session-user requirement
  -> CSRF verification
  -> resolve project p7 in tenant o1
  -> token/session grant intersection
  -> authorizer checks project.update
  -> post-auth rate limit by actor and project
  -> audit allowed
  -> acquire release VM worker
  -> inject invocation capabilities
  -> invoke named handler through RuntimeOwner
  -> validate output/effects
  -> send response
  -> audit completed
  -> release worker
```

At no point does JavaScript parse the cookie, load the membership table, verify CSRF, or receive the database filename.

## 21.6 Failure cases

| Failure | Result |
| --- | --- |
| Missing session | 401 before JavaScript |
| Agent API token on session-only route | 403 before JavaScript |
| Stale CSRF token | 403 before resource mutation |
| Project belongs to another tenant | 404 or 403 according to resolver policy |
| Missing `project.update` grant | 403 before authorizer callback or handler |
| Rate limit exceeded | 429 with policy metadata in audit |
| JavaScript exceeds deadline | VM interrupted, worker discarded, 500/504 according to surface |
| Candidate worker unhealthy | No traffic-generation change |

### Key points

- The release lock connects build-time selection to runtime enforcement.
- Authentication and authorization complete before the JavaScript callback.
- The handler runs in an exclusive, bounded worker with only release capabilities.
- Failure paths preserve the active release and produce structured evidence.

---

# 22. Intern Exercises

These exercises are designed to make the architecture concrete. Each exercise should produce code, tests, and a short written explanation of the invariant being proved.

## Exercise 1 — Trace a planned route

Choose one route in an example xgoja host. Record:

- Route registration source.
- Generated or runtime `RoutePlan`.
- Required host services.
- Enforcer order.
- Handler context fields.
- Audit outcomes.
- Expected status for missing auth, wrong principal, missing CSRF, denied action, and success.

Do not begin by changing code. The exercise is complete when another engineer can review the route policy from your trace.

## Exercise 2 — Add a route rate limit

Add a pre-auth IP/route limit and a post-auth actor/resource limit. Write tests proving:

- Anonymous callers share only the intended bucket.
- Two authenticated actors do not share the actor bucket.
- A denied actor does not consume the allowed actor's resource bucket.
- `Retry-After` is returned on 429.

Explain why each limit belongs before or after authorization.

## Exercise 3 — Replace a raw route

Find a raw Express route and migrate it to a planned route. Enable `RejectRawRoutes`. Prove startup or request failure for the old route and success for the planned route.

## Exercise 4 — Define a hosted module descriptor

Write a catalog descriptor for `sqlite@1` containing:

- Permissions.
- Resource binding schema.
- Query and result limits.
- Migration lifecycle.
- Metering dimensions.
- TypeScript declarations.
- Entitlement feature.
- Single-writer placement requirements.

Then show the generated release-lock entry.

## Exercise 5 — Poison a worker

Create a handler that exceeds its execution deadline. Verify:

- The VM is interrupted.
- The invocation returns an error.
- The worker is not returned to the idle pool.
- A replacement worker loads successfully.
- A second request succeeds.

## Exercise 6 — Implement a traffic-generation CAS

Create two concurrent promotion requests with the same expected generation. Exactly one must commit. The other must receive a conflict and must not change traffic.

## Exercise 7 — Build a Widget action

Define a Widget page with a server action. Verify:

- The action names an existing handler.
- Input binding paths validate.
- Unauthorized users cannot invoke it.
- Oversized output is rejected.
- Renderer and registry versions are pinned in the release.

## Exercise 8 — Model a continuation upgrade

Create workflow version 1 with a pending continuation. Promote version 2 with an incompatible carry schema. Implement one explicit policy: pinned old release, migration adapter, or expiry/restart. Prove that the system never passes old carry data to the new handler implicitly.

---

# Appendix A — Reference Architecture

```text
                           CONTROL PLANE

 Dashboard / API / CLI / Coding Agents
                 |
          Platform OIDC + RBAC
                 |
 Organizations / Projects / Environments / Domains
 Releases / Policies / Approvals / Entitlements
 Agents / Keys / Grants / Audit / Usage
                 |
       PostgreSQL + transactional outbox
                 |
          desired traffic generations
                 v

                            BUILD PLANE

 Source archive or Git revision
       -> bounded scanner
       -> JS/TS static graph
       -> program compiler
       -> module and entitlement resolver
       -> xgoja profile generator
       -> tests / SBOM / provenance
       -> signed content-addressed artifact
                 |
                 v

                         EXECUTION PLANE

 Edge/router -> traffic generation -> release worker group
                                      |
                          isolated process/sandbox
                                      |
                           exclusive Goja VM pool
                                      |
                    gojahttp Host + Enforcer + handlers
                                      |
                      capabilities / secrets / resources
                                      |
                    DB / object store / payments / egress

                          IDENTITY PLANE

 Platform issuer ---------------------> control-plane sessions
 Managed app realm / external OIDC ---> app-local sessions
 Tiny-IDP kernel ---------------------> credentials, tokens, keys,
                                        continuations, protocol effects
```

---

# Appendix B — Glossary

**Actor** — A host-owned authenticated principal exposed to a planned route after authentication.

**Agent** — A durable automation principal, distinct from its API tokens and grants.

**Application contract** — Serializable description of routes, handlers, schemas, capabilities, effects, budgets, pages, and tests.

**Artifact** — Signed immutable build output and its provenance.

**Binding** — Connection between an environment/release and a resource or secret reference.

**Capability binding** — Invocation-scoped Go implementation of one declared application capability.

**Continuation** — Durable record that allows a workflow to resume in a fresh invocation after an external boundary.

**Deployment** — Attempt to make a release available.

**Effect** — Native state change requested by a handler and applied under host policy.

**Entitlement** — Commercial right for an account to use a product feature or module.

**Enforcer** — Router-independent interpreter of `RoutePlan` security policy.

**Evidence** — Native-verified fact injected into a handler and not forgeable as ordinary input data.

**Native module** — Trusted Go-backed JavaScript API installed into a Goja runtime.

**Permission** — Authority that a module or handler may exercise.

**Planned route** — HTTP route with a validated host-owned security contract.

**Provider** — Trusted Go package that contributes xgoja modules, commands, sources, declarations, or host services.

**Quota** — Enforced limit on resource or operation amount.

**Release** — Artifact plus exact environment configuration, modules, bindings, policy, entitlements, and renderer identity.

**Resource instance** — Persistent or external service owned by the platform, such as a database or identity realm.

**Runtime lock** — Exact, signed identity of toolchain, source, native modules, ABI, configuration, and renderer.

**Runtime owner** — Serialized scheduler through which all Goja VM access occurs.

**Source revision** — Exact source input to a build.

**Traffic generation** — Immutable routing decision assigning traffic to releases.

**Widget IR** — Versioned serializable page and action protocol rendered by an approved browser component registry.

**Worker revision** — Running process or pool loaded from one release.

---

# Appendix C — Source Map

The following sources were used for the current-implementation descriptions. Repository paths are more stable than prose summaries and should be consulted before changing a subsystem.

[S1] `go-go-golems/go-go-goja`, xgoja v2 planning and generated runtimes:  
- `cmd/xgoja/doc/17-xgoja-v2-reference.md`  
- `pkg/xgoja/app/types.go`  
- `pkg/xgoja/providerapi/module.go`  
- `pkg/xgoja/providerapi/provider_registry.go`  
- `cmd/xgoja/internal/generate/templates/runtime_package.go.tmpl`  
https://github.com/go-go-golems/go-go-goja

[S2] `go-go-golems/go-go-goja`, owned runtime construction and lifecycle:  
- `pkg/engine/factory.go`  
- `pkg/engine/runtime.go`  
- `pkg/engine/module_specs.go`

[S3] `go-go-golems/go-go-goja`, serialized VM ownership:  
- `pkg/runtimeowner/types.go`  
- `pkg/runtimeowner/runner.go`

[S4] `go-go-golems/go-go-goja`, Express-style HTTP module:  
- `pkg/doc/18-express-module.md`

[S5] `go-go-golems/go-go-goja`, HTTP host implementation:  
- `pkg/gojahttp/host.go`  
- `pkg/gojahttp/request_response.go`  
- `pkg/gojahttp/body.go`

[S6] `go-go-golems/go-go-goja`, route-plan types and validation:  
- `pkg/gojahttp/auth_plan.go`

[S7] `go-go-golems/go-go-goja`, planned-route enforcement:  
- `pkg/gojahttp/enforcer.go`

[S8] `go-go-golems/go-go-goja`, Go-native planned-auth API:  
- `pkg/gojahttp/app.go`  
- `cmd/xgoja/doc/18-go-planned-auth-api.md`

[S9] `go-go-golems/go-go-goja`, host composition for Express and OIDC:  
- `cmd/xgoja/doc/19-express-auth-host-integration-guide.md`

[S10] `go-go-golems/go-go-goja`, generated hostauth configuration:  
- `cmd/xgoja/doc/20-hostauth-config-reference.md`

[S11] `go-go-golems/go-go-goja`, auth stores:  
- `cmd/xgoja/doc/21-auth-stores-reference.md`

[S12] `go-go-golems/go-go-goja`, HTTP serve command and hot reload:  
- `cmd/xgoja/doc/22-http-serve-command-reference.md`

[S13] `go-go-golems/go-go-goja`, high-level audit and capability JavaScript APIs:  
- `cmd/xgoja/doc/24-generated-auth-javascript-apis.md`

[S14] `go-go-golems/go-go-goja`, agents and API tokens:  
- `cmd/xgoja/doc/25-programmatic-auth-javascript-apis.md`

[S15] `go-go-golems/go-go-goja`, route credential requirements and rate limits:  
- `cmd/xgoja/doc/26-express-route-auth-requirements.md`

[S16] `go-go-golems/go-go-goja`, guarded outbound HTTP:  
- `cmd/xgoja/doc/27-guarded-fetch-client-api.md`

[S17] `go-go-golems/go-go-goja`, current production hardening plan:  
- `ttmp/2026/07/18/XGOJA-HOSTAUTH-PROD-HARDENING-001--single-node-hostauth-production-hardening/design-doc/01-intern-implementation-guide-for-single-node-hostauth-hardening.md`

[S18] `go-go-golems/go-go-host`, control plane, deployment, runtime, and data model:  
- `README.md`  
- `docs/architecture/data-model.md`  
- `docs/contributing/runtime-and-deployment-guidelines.md`  
- `internal/deploy/bundle.go`  
- `internal/control/deployments.go`  
- `internal/runtime/runtime.go`  
- `internal/runtime/supervisor.go`  
https://github.com/go-go-golems/go-go-host

[S19] `go-go-golems/tiny-idp`, lambda-first identity scripting design on `task/prod-tiny-idp`:  
- `ttmp/2026/07/10/TINYIDP-GOJA-001--go-go-goja-identity-microkernel-scripting-layer/design-doc/03-lambda-first-tiny-idp-javascript-api-with-explicit-browser-continuations.md`  
https://github.com/go-go-golems/tiny-idp/tree/task/prod-tiny-idp

[S20] `go-go-golems/tiny-idp`, program and runtime implementation on `task/prod-tiny-idp`:  
- `pkg/idpprogram/program.go`  
- `pkg/idpprogram/lambda.go`  
- `pkg/idpprogram/validate.go`  
- `pkg/idpscript/compiler.go`  
- `pkg/idpscript/runtime_factory.go`  
- `pkg/idpscript/invoke.go`  
- `pkg/idpscript/pool.go`

[S21] PARC Widget DSL project note and related Widget DSL v3 report:  
- `https://parc.yolo.scapegoat.dev/note/research/kb/projects/widget-dsl`  
- `go-go-golems/go-go-parc`, Widget DSL v3 and Publish Vault project reports

[S22] PARC go-go-goja project note and runtime-system reports:  
- `https://parc.yolo.scapegoat.dev/note/research/kb/projects/go-go-goja`  
- `go-go-golems/go-go-parc`, go-go-goja runtime and HTTP/auth reports

---

# Closing

The reviewed system is not missing a web framework. It already has one of the strongest foundations in the project: Go-owned HTTP lifecycle, planned routes, reusable enforcement, explicit principal requirements, resource-aware authorization, CSRF, rate limits, audit, OIDC sessions, agent tokens, native mounts, guarded outbound access, and generated-host integration.

The hosting platform should make that framework the application boundary. xgoja should define the trusted runtime profile. go-go-host should become the control plane and reconciler. Isolated workers should execute immutable releases. Tiny-IDP should remain the identity kernel while contributing a general model for serializable JavaScript programs, bounded capabilities, effects, evidence, and continuations. Widget IR should provide the normal agent-friendly UI protocol.

The final architecture is coherent because each layer has one responsibility. JavaScript describes behavior. Route plans describe HTTP security. Native modules expose reviewed authority. Releases freeze source and dependencies. The control plane records policy and traffic. Workers enforce limits. Identity services own credentials and protocol state. These boundaries are the platform.

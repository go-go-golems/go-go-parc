---
title: "Devmesh Follow-Up: One Routing Authority, Safe HTTP, and Devctl Integration"
aliases:
  - Devmesh v2 implementation report
  - Devmesh lifecycle simplification
  - Devmesh devctl integration
  - DEVMESH-001 follow-up
tags: [project-report, devmesh, go, networking, tcp, http, docker, devctl, leases, reverse-proxy, lifecycle]
status: active
type: project-report
created: 2026-09-20
repo: /home/manuel/code/wesen/2026-09-20--devmesh
source_ticket: DEVMESH-001
ticket_path: ttmp/2026/09/20/DEVMESH-001--devmesh-implementation-and-intern-analysis-guide
predecessor_report: "[[PROJECT REPORT - Devmesh - Stable Local Endpoints for Ephemeral Backends - A Technical Deep Dive]]"
implementation_commits:
  - e568ca3 Simplify devmesh lifecycle and scripting
  - 04d8d56 Harden devmesh HTTP routes and endpoints
  - d585397 Close devmesh resources and durable allocations
  - 080387e Add devctl compose endpoint integration example
validation:
  - go build ./...
  - go vet ./...
  - go test -race ./... -count=1
  - make glazed-lint
  - real Docker recreate and PostgreSQL post-replacement query
related_vault_notes:
  - "[[PROJECT REPORT - Devmesh - Stable Local Endpoints for Ephemeral Backends - A Technical Deep Dive]]"
  - "[[PROJECT REPORT - devctl - Transactional Lifecycles, Process Ownership, and Executable Provenance]]"
---

# Devmesh Follow-Up: One Routing Authority, Safe HTTP, and Devctl Integration

The first Devmesh report described a local service registry that gives consumers stable endpoints while native processes and Docker containers use ephemeral backend ports. This follow-up documents the corrective implementation work that turned the initial architecture into a narrower and more reliable local-development system. The main result is not a larger orchestration framework. It is a system with fewer independently mutable values, fewer lifecycle paths, and a concrete integration with `devctl` that uses the existing responsibilities of both tools.

The implementation now has one authoritative current-backend value per service, stored in the registry. TCP runtimes own frontend listeners but read the registry when accepting a new connection. HTTP routes do the same when accepting a new request. A producer removal—lease expiry, explicit deletion, or Docker container stop—takes effect only when its concrete producer identity still matches the current service record. This prevents an old lease or an old container event from disabling a newer replacement backend.

> [!summary]
> 1. Devmesh retains the original frontend/backend separation, but the registry is now the sole authority for the current backend. TCP and HTTP consume one snapshot of that authority rather than retaining independent mutable copies.
> 2. A service now distinguishes a stable logical owner from a concrete producer. Docker recreation keeps the stable owner key but changes the container ID; a late event for the old container is ignored when the new container is current.
> 3. HTTP routing now selects a backend once per request and rewrites the outbound target unconditionally. Explicit hostnames are unique and immutable during a daemon run; returned URLs include the actual scheme and non-default port.
> 4. The CLI supports shell consumption with `services resolve --raw --wait`, and foreground `register` shares the Go client's lease loop. A runnable devctl example uses these commands to inject a stable database endpoint into a supervised consumer.
> 5. The system intentionally stops before advanced machinery: no event replay protocol, no idle frontend eviction, no public hot-update API, no route aliases, no dependency graph, and no cross-service transaction coordinator.

## Why a follow-up was necessary

The initial implementation had the right major components: a registry, bind-first frontend allocation, a TCP proxy, leases, a Go client, Docker discovery, HTTP routing, TLS loading, and Glazed command/configuration support. Its first acceptance tests also passed. A deeper review found that some lifecycle guarantees were stated more strongly than the code could enforce.

The important distinction is between a race detector result and a lifecycle invariant. `go test -race` can show that data is synchronized correctly while a sequence of synchronized operations still produces the wrong final state. Devmesh had several of these sequences. For example, a Docker replacement container could register successfully, then a delayed removal event for the old container could clear the service because both containers shared the same stable owner key. The stable owner key was correct for replacement permission, but it was too broad to authorize removal.

The follow-up did not attempt to solve every theoretical ordering problem. It reduced the system to the smallest state model that protects ordinary local workflows: native process registration, daemon restart, Docker container replacement, explicit HTTP routing, and supervised consumer startup.

## The central model after the correction

A **service name** is the logical identity consumed by other programs, such as `checkout.postgres` or `devctl.example.postgres`. A **frontend** is the stable listener bound by Devmesh. A **backend** is the current loopback address owned by a producer. A **producer** is a native process, manual CLI registration, or Docker container that supplies the backend. A **consumer** resolves the name and connects to the frontend.

The follow-up adds two identities that must not be conflated:

- An **owner key** identifies the logical producer that may replace its own backend. Docker uses a recreation-stable owner key such as `docker:checkout:db:5432`; it intentionally excludes the container ID.
- A **producer ID** identifies the concrete publication that is current now. Native/manual registrations use the daemon-issued registration ID. Docker registrations use the container ID.

The owner key answers “may this registration replace the service?” The producer ID answers “may this removal clear the service?” Those questions need different answers.

```mermaid
flowchart LR
    P1["Container A\nowner docker:shop:db:5432\nproducer A"]
    P2["Container B\nowner docker:shop:db:5432\nproducer B"]
    R["Registry record\nname: shop.postgres\nowner: docker:shop:db:5432\nproducer: B\nbackend: 127.0.0.1:49901"]
    F["Stable frontend\n127.0.0.1:15432"]
    C["Consumer"]

    P1 -. stale stop event .-> R
    P2 -->|replace permitted| R
    R --> F --> C

    style P1 fill:#fee2e2,stroke:#b91c1c
    style P2 fill:#dcfce7,stroke:#15803d
    style R fill:#dbeafe,stroke:#1d4ed8
    style F fill:#fef3c7,stroke:#b45309
```

When the stale event for container A arrives, Devmesh compares A to the current producer ID B. They differ, so the removal is a no-op. This is a local compare-and-clear operation. It is not a general event ordering service.

## From duplicated backend state to one routing authority

The first implementation stored a backend in the registry and also in each TCP runtime. The HTTP router looked the backend up through a closure. That made it possible for metadata and forwarding behavior to diverge. A registry record could say `ready` while the TCP runtime had already cleared its pointer, or a runtime could retain an address that the registry no longer advertised.

The corrected architecture assigns distinct ownership to the two long-lived entities:

- `registry.ServiceRecord` owns service metadata and the current routing snapshot: status, backend, frontend, owner key, producer ID, source, and optional HTTP hostname.
- `runtime.ServiceRuntime` owns a bound TCP frontend listener and its accept loop. It does not own a second mutable backend.

At TCP accept time, the runtime calls a provider that reads the registry and returns a copy of the current ready backend. The accepted connection keeps that copy for its lifetime. A later backend replacement changes only future connections, which remains correct for database and arbitrary TCP protocols.

```text
accept TCP connection
    backend := registry.currentReadyBackend(serviceName)
    if backend is nil:
        close client
        return
    start proxy(client, copied backend)
```

The provider is not called while bytes are being forwarded. `proxy.TCP` dials the copied address and performs bidirectional `io.Copy`; it propagates TCP write-half closure when available. The registry lock is not held while dialing or copying.

The HTTP route takes the same conceptual path. The route map stores a hostname-to-provider association, while the provider reads the registry. The HTTP request obtains one backend snapshot before proxy rewriting. TCP and HTTP therefore differ in protocol behavior but not in the source of truth for routing.

### Why idle runtime reaping was removed

The initial design included an idle grace period and a reaper that closed a frontend listener after an unavailable backend had remained absent for ten minutes. This was reasonable as a potential resource policy, but it introduced another state transition: a registration could find an existing backendless runtime while the reaper simultaneously removed it. Fixing that perfectly would require more coordination for an uncommon local-scale concern.

The follow-up removes automatic runtime reaping. A frontend listener remains reserved until the daemon shuts down. This gives a simpler within-run guarantee: once a service name has received a frontend, transient backend loss and replacement do not release it. The state file still remembers port assignments across daemon restarts when possible.

The trade-off is explicit. Very high name churn can consume the configured frontend range until the daemon is restarted. Devmesh reports port exhaustion rather than silently evicting a service. A future eviction policy requires a demonstrated workload and an acceptance test; it is not part of the current implementation.

## Conditional removal: leases, deletion, and Docker events

The daemon exposes one internal operation conceptually equivalent to this pseudocode:

```go
func endPublication(name, expectedProducerID string) bool {
    lock daemon mutation mutex
    if registry.current(name).ProducerID != expectedProducerID {
        unlock
        return false // stale removal
    }
    registry.clearBackend(name)
    unlock
    return true
}
```

The actual registry method is `ClearBackendIf(name, producerID)`. It retains the frontend and changes status to `unavailable` only on a producer-ID match. The daemon uses it for three removal paths:

| Removal cause | Concrete producer ID | Result if no longer current |
| --- | --- | --- |
| Native/manual lease expires | Registration ID | Ignore stale expiry |
| Native/manual caller deletes | Registration ID | Ignore or reject stale deletion |
| Docker watcher forgets a container | Container ID | Ignore old-container event |

A same-owner process/manual replacement also retires the old lease entry. The old token cannot continue renewing an obsolete publication. A public producer normally does not perform an in-place update: it deletes its old registration, then creates a new one. The dormant service retains its frontend, so the new producer can reclaim the name without a new frontend allocation.

### Per-entry lease duration

A lease manager has a configured default TTL, but a registration may request another valid TTL. The original manager used the request duration to create the first expiry and then used the manager default for every renewal. A sixty-second registration could therefore renew to fifteen seconds. The corrected `lease.Entry` stores its effective TTL and uses it for both creation and renewal.

```text
register with TTL = 60 seconds
    expiry = now + 60 seconds
heartbeat
    expiry = now + entry.TTL  // still 60 seconds
```

The supported range is three through 3,600 seconds. The lower bound leaves a real heartbeat margin: the shared client schedules a normal heartbeat at TTL divided by three. Devmesh rejects invalid requested TTL values before it allocates a frontend or writes a registry record.

Expiration uses `TakeExpired(now)`, which selects and removes expired leases under one lease-map lock. A client cannot successfully renew an entry after it has been taken for expiry and then have a second operation remove the renewed value. When a lease is already at or past its deadline, renewal returns the same missing-registration condition the Go client uses to trigger re-registration.

## A single producer client loop

The Go client in `pkg/devmesh` registers an already-bound backend, stores its registration ID and token privately, and maintains the lease until its context is canceled or the handle is closed. The CLI foreground `devmesh register` now uses that same client loop rather than maintaining a second implementation of heartbeat, backoff, and daemon-restart recovery.

```text
create registration
    -> receive frontend, ID, token, effective TTL
wait TTL / 3
    -> heartbeat
    -> success: schedule normal heartbeat
    -> 404: re-register and replace local credentials
    -> transient error: bounded jittered retry
close or context cancellation
    -> stop loop
    -> read latest ID/token
    -> best-effort DELETE under short timeout
```

The public client treats caller-context cancellation as the lifetime boundary for heartbeats. This is explicit: callers that use a short creation timeout should create a longer-lived registration context rather than assume a request-scoped context keeps a service published.

The command has two different operational modes:

```bash
# Persistent manual producer: keep this process running.
devmesh register --name checkout.api --backend 127.0.0.1:49173

# Diagnostic publication: no heartbeats; expires after TTL.
devmesh register --name test.echo --backend 127.0.0.1:25999 --once
```

The persistent command flushes a structured output row before it blocks on its context. An isolated smoke test confirmed a JSONL result was present before an interrupt was sent. The command does not print lease tokens.

## Script-safe resolution

Many consumers only need an endpoint, not a table or JSON object. The command layer now provides a narrow domain behavior rather than changing Glazed’s universal output model:

```bash
endpoint=$(devmesh services resolve checkout.postgres --raw --wait 20s)
```

`--raw` prints exactly one endpoint plus a newline. For TCP services this is `host:port`; for HTTP services it is the complete public URL. `--wait` retries unknown, unavailable, and transient daemon lookup conditions until one overall deadline. It has no database-, Redis-, or application-specific readiness semantics. A registered PostgreSQL backend can still be initializing, so the consumer retains its normal connection retry or health behavior.

The output distinction matters. A structured resolve without `--raw` can represent `unavailable` as a service row. Raw resolve exits nonzero rather than printing an endpoint that is not currently usable as a successful script result.

## Public registration is narrower than trusted Docker registration

The administrative API remains HTTP/JSON over a user-only Unix socket, but public creation no longer accepts internal producer identity fields. A caller supplies name, kind, backend, preferred frontend port, optional lease TTL, protocol hint, and explicit HTTP host. The daemon creates the registration ID, token, and owner identity.

The public API rejects a Docker source request. Docker registration is lease-free and requires a concrete container ID; allowing arbitrary callers to submit it would create a backend with no correct cleanup owner. The Docker watcher calls a typed in-process daemon path instead.

This is an important boundary even for a local tool. A consumer can inspect owner metadata for debugging, but copying that value into an ordinary public request cannot replace the service. The JSON decoder rejects removed identity fields as unknown, and `source=docker` receives an invalid-request response.

## HTTP routing: one selected target per request

HTTP is different from generic TCP because an HTTP request carries a `Host` header. Devmesh can therefore route several explicit hostnames through one listener. This does not apply to PostgreSQL, Redis, or arbitrary TCP; their stable frontend remains a distinct loopback address and port.

The corrected router executes the following request path:

```text
canonical hostname from request Host
    -> hostname route lookup
    -> missing route: 404
    -> read current backend once
    -> nil backend: 503
    -> store copied backend in request context
    -> ReverseProxy.Rewrite sets URL scheme and host from that copy
    -> remove inbound X-Forwarded-* values
    -> compute clean X-Forwarded-* values for this request
    -> proxy or return 502 on upstream failure
```

The important step is selecting one backend snapshot. The old router queried the provider once to decide whether the route was available and again in the reverse-proxy director. If the first result was non-nil and the second was nil, the outgoing request could retain an absolute URL supplied by the caller. An acceptance test now makes exactly that sequence: it sends an absolute-form request toward an unintended local server, makes the provider return a valid backend once and nil thereafter, and asserts a `SAFE` response from the selected backend. The provider is called once.

```mermaid
sequenceDiagram
    participant Client
    participant Router
    participant Registry
    participant Proxy
    participant Backend

    Client->>Router: GET absolute-form URL, Host: api.local
    Router->>Registry: currentReadyBackend(api.local)
    Registry-->>Router: copied 127.0.0.1:49382
    Router->>Proxy: request context contains copied backend
    Proxy->>Proxy: Rewrite outbound URL from copied backend
    Proxy->>Backend: HTTP request
    Backend-->>Client: response
```

The router always sets the outbound target from the verified snapshot. If an internal future caller bypasses the normal route method and no snapshot exists, rewrite forces a guaranteed failing loopback target rather than leaving the caller’s URL intact.

### Fixed explicit hostnames

The initial implementation allowed a second service to silently overwrite a hostname route, and it could leave an old route installed when a service changed host. The current contract is simpler:

- One canonical explicit hostname belongs to one service.
- Hostname comparison lowercases and removes a trailing dot.
- Kind and hostname are immutable for an existing service during one daemon run.
- A conflicting host, kind, or hostname mutation returns a conflict rather than partially changing route state.

There are no aliases, automatic hostname generation, generated wildcard subdomains, or route migration. A project that needs a different route creates a different logical service or restarts after reconfiguration. This removes several route cleanup and certificate-coverage combinations from the supported surface.

### Truthful public URLs and listener ownership

Devmesh must not report `http://api.local` when it actually listens on `127.0.0.1:8088`, nor must it report a healthy daemon when a configured proxy port is already occupied.

At daemon construction, Devmesh validates configuration, loads any configured TLS key pair, selects a public scheme, and binds configured HTTP/HTTPS listeners. Only then does command startup expose the Unix administrative socket and begin serving. If the HTTP or HTTPS bind fails, startup fails. When TLS is configured, the advertised route URL uses HTTPS; non-default ports are included.

```text
HTTP configured at 127.0.0.1:8088
  explicit host api-checkout.test
  frontend.url = http://api-checkout.test:8088

HTTPS configured at 127.0.0.1:8443 with certificate
  explicit host api-checkout.test
  frontend.url = https://api-checkout.test:8443
```

CLI list, resolve, inspect, and the Go client’s `Endpoint()` all use one endpoint formatter: prefer `frontend.url`, otherwise format the TCP frontend as `host:port`. The public Go options and CLI registration flags include the explicit HTTP host required for `kind=http`.

TLS remains intentionally scoped to loading an existing certificate/key pair and enforcing TLS 1.2 as a minimum. The follow-up does not claim ACME issuance, certificate reload, alias coverage, or a comprehensive certificate-permission policy.

## Docker discovery: responsive events with periodic repair

Docker is still an adapter over the core registry. The watcher reads labels, inspects the host-published port for the declared container port, forms a stable Compose owner key where labels are available, and calls the daemon’s trusted Docker registration method.

Events provide prompt updates, but the watcher now also reconciles the inventory every five seconds. This is the selected repair mechanism for local use. It intentionally accepts a small convergence delay after a missed event rather than introducing an event replay cursor, epoch management, or exactly-once delivery protocol.

```text
startup inventory -> upsert enabled containers
    |
    +-> lifecycle event -> inspect, upsert, or conditionally forget
    |
    +-> every 5 seconds -> inventory reconcile
    |
    +-> event stream failure -> bounded reconnect then reconcile
```

Each Docker list and inspect operation has a ten-second bound. During reconcile, a devmesh-labeled container that is present in the inventory but temporarily fails inspection is treated as present, not as removed. This avoids inventing a disappearance from a transient Docker API failure.

The watcher also checks every host binding for the managed container target when loopback-only policy is active. A binding on `127.0.0.1` does not make a mixed binding safe if the same port is also published on `0.0.0.0`. The default is rejection. An explicit opt-in remains available for non-loopback publication, but it is not the recommended development posture.

## Shutdown, durable allocation, and Unix socket safety

A listener closure stops new TCP accepts, but it does not terminate connections that have already been accepted. The corrected runtime tracks accepted client sockets and proxy workers. Shutdown performs the following bounded sequence:

```text
cancel background work
    -> stop frontend listener admission
    -> close all active client sockets
    -> proxy copy loops unblock and close upstreams
    -> wait for workers under the existing shutdown context
    -> flush durable state
```

The policy is prompt local cleanup, not transaction-preserving draining. A database query in progress can fail when Devmesh shuts down. This is appropriate for the current local tool because the daemon is restartable and consumers already need reconnection behavior. A configurable drain policy is deferred until a concrete workload needs it.

Persistent frontend mapping is part of the stable-endpoint promise. The allocator binds a candidate port and then writes the name-to-port assignment. If persistence fails, it closes that candidate listener and returns an error. It does not report a volatile allocation as successful. The state store tracks a dirty in-memory change after a failed write, so a later request for the same value retries the write instead of returning nil merely because the in-memory map already contains the value.

The Unix administrative socket listener now uses `Lstat` before stale-socket recovery. A failed Unix dial permits removal only when the existing path is actually a socket. A regular file or symlink is rejected and left unchanged. This prevents a socket path typo from deleting unrelated data.

## Devctl integration: compose, resolve, exec

`devctl` and Devmesh have distinct roles. Devctl plans and supervises processes, records their run state, captures logs, checks health, and stops the process groups it owns. Devmesh publishes and resolves stable local endpoints. Combining those responsibilities would duplicate lifecycle state and create competing cleanup behavior.

The executable example at `/home/manuel/code/wesen/2026-09-20--devmesh/examples/devctl-compose-postgres/` demonstrates the first useful boundary without modifying devctl core schema.

```mermaid
flowchart TD
    DCTL["devctl\nplans and supervises"]
    COMPOSE["foreground docker compose\ndatabase service"]
    WATCH["devmeshd Docker watcher\nlabels + inspect"]
    FRONT["stable frontend\ndevctl.example.postgres"]
    LAUNCH["run-consumer.sh\nresolve --raw --wait"]
    APP["consumer.py\nDATABASE_URL"]

    DCTL --> COMPOSE
    COMPOSE --> WATCH
    WATCH --> FRONT
    DCTL --> LAUNCH
    LAUNCH --> FRONT
    LAUNCH --> APP

    style FRONT fill:#fef3c7,stroke:#b45309
    style WATCH fill:#dbeafe,stroke:#1d4ed8
    style APP fill:#dcfce7,stroke:#15803d
```

The Compose service publishes PostgreSQL port 5432 on an ephemeral loopback host port and carries Devmesh labels. Devmesh, not devctl, is the only registration owner for that database. The plugin returns `docker compose up` as a foreground supervised service, so devctl owns logs and termination of Compose.

The consumer process uses a shell launcher that resolves immediately before `exec`:

```bash
endpoint="$(devmesh services resolve devctl.example.postgres --raw --wait 45s)"
export DATABASE_URL="postgres://dev:dev@${endpoint}/app?sslmode=disable"
exec python3 consumer.py
```

The plugin does not resolve the endpoint during `config.mutate` or `launch.plan`. Plugins terminate after planning and cannot own a long-lived registration lease or safely freeze an endpoint before the consumer environment is created. The persistent devctl wrapper owns the launcher process, so the resolve occurs at the correct boundary.

A real tmux-backed smoke test built an isolated devctl binary, started Devmesh with a temporary Unix socket and state file, ran `devctl up`, inspected status and consumer logs, resolved the service through Devmesh, and ran `devctl down`. The recorded consumer log was:

```text
devctl consumer resolved devctl.example.postgres as 127.0.0.1:15186
consumer started with DATABASE_URL=postgres://dev:dev@127.0.0.1:15186/app?sslmode=disable
```

The example does not start or stop the shared `devmeshd` process. `devctl down` stops the Compose and consumer services it owns; it does not remove unrelated Devmesh services. The wait establishes backend registration, not PostgreSQL query readiness, so a real consumer retains its normal database retry policy.

## What intentionally remains outside the implementation

The implementation is not incomplete merely because it lacks every possible generalization. The current scope is a choice supported by the tests and example.

| Deferred capability | Why it is deferred |
| --- | --- |
| Docker replay cursors, event epochs, and deduplication framework | Periodic reconciliation repairs local missed-event conditions with less state. |
| Automatic idle frontend eviction | Listener retention removes an important lifecycle race; no demonstrated local workload exhausts the range. |
| Public hot backend update API | Ordinary public producers can delete and re-register; no current caller needs an atomic update contract. |
| Devctl dependency graph or transaction coordinator | The shell launcher’s bounded resolve is sufficient for the first consumer workflow. |
| Native devctl backend-file wrapper | No concrete non-self-registering application requires it yet. |
| Hostname aliases, generation, migration, or route rename | Explicit fixed hostnames avoid collision, cleanup, and wildcard-certificate combinations. |
| Backend HTTPS selection and automatic certificate issuance | Existing local TLS termination covers the current supported path. |
| Volatile state mode or retry worker | Failing new allocation is simpler and truthful when stable state cannot be written. |
| Cross-host discovery, local DNS, per-service IPs, and protocol-aware database proxies | They are separate product directions beyond stable loopback frontends. |

A deferred capability should be reconsidered only with a concrete failure, user impact, simpler alternatives, and an acceptance test. The fact that an edge case is possible is not enough to add another subsystem.

## Evidence and validation

The repository’s primary hardening commits are `e568ca3`, `04d8d56`, `d585397`, and `080387e`. The ticket at `ttmp/2026/09/20/DEVMESH-001--devmesh-implementation-and-intern-analysis-guide/` contains the detailed review, source references, diary, follow-up design, runnable probes, and captured receipts.

The final validation gate passed:

```bash
GOWORK=off go build ./...
GOWORK=off go vet ./...
GOWORK=off go test -race ./... -count=1
GOWORK=off make glazed-lint
```

The Docker-specific acceptance run also passed explicitly:

```text
TestDockerDiscoveryAndRecreatePreservesFrontend (1.66s)
TestPostgresThroughFrontend (2.12s)
```

The PostgreSQL test now queries the stable frontend before and after starting replacement B, removing A, and confirming B remains the current Docker producer. This tests more than port metadata: it proves the PostgreSQL protocol reaches the replacement through the unchanged frontend.

The ticket-local verification probe records the corrected behavior for the prior lifecycle findings. Its final observations include stale old lease deletion rejected while the replacement stays ready, stale Docker removal ignored, duplicate HTTP hostname rejected, one backend provider call producing the safe proxy target, mixed Docker publication rejected, regular socket path file preserved, allocation failure on state persistence error, and EOF on an active TCP connection after daemon shutdown.

## Key points

- Stable frontends remain the central Devmesh value, but a frontend is useful only if its current backend state and removal semantics are coherent.
- A stable owner key is correct for replacement permission. A concrete producer ID is required for safe removal.
- The registry is the routing authority. TCP and HTTP choose a copy of its current backend for each new connection or request.
- A local system benefits from narrower contracts: retain listeners, use periodic repair, reject mutable routes, and fail allocation when durability cannot be established.
- Script integration needs a bounded resolve command, not a new transaction protocol. `devctl` supervises processes; Devmesh resolves endpoint dependencies at consumer launch.
- A correct smoke test includes the negative ordering: start replacement B, then remove A, then prove the stable endpoint still reaches B.

## Current status and near-term direction

Devmesh now has a validated local TCP, Docker, HTTP, TLS-loading, scripting, and devctl example path. The DEVMESH-001 focused implementation tasks are complete and the repository working tree was clean at the final audit. The next work should be driven by a real requirement, not by attempting to preemptively build every deferred capability.

The most plausible future extension is the optional native devctl wrapper registration contract, where a concrete application binds its backend and writes a fresh per-run address file. That work should begin only when a non-self-registering application actually needs it. The current Compose integration is sufficient to establish the ownership boundary and prove the consumer workflow.

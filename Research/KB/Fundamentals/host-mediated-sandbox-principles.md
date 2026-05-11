---
title: "Host-Mediated Sandbox Principles"
aliases:
  - host-mediated sandboxing
  - sandbox boundary principles
  - host guest boundary
  - capability mediated runtime
  - mediated I/O
tags: [knowledge-base, fundamental, sandbox, security, wasm, vm, goja, capabilities]
status: active
type: knowledge-base
created: 2026-05-11
---

# Host-Mediated Sandbox Principles

> [!summary]
> A sandbox is useful only when the guest cannot reach the outside world except through the host. The guest owns computation. The host owns capabilities: files, network, secrets, UI, devices, persistence, and policy. This principle explains why our microVMs, Wasm modules, goja runtimes, browser workers, and plugin systems all end up with the same shape even though they run on very different technology.

## The core idea

A sandbox has two roles:

- the **guest** runs code or evaluates a program;
- the **host** decides what that code may observe or change outside itself.

The host/guest split is not just an implementation detail. It is the security and debugging model. The guest may compute, allocate memory, evaluate scripts, transform data, or produce requests. It should not directly open files, call the network, read secrets, draw on the page, write to devices, or mutate persistent state unless the host provides an explicit capability.

In our projects, the guest takes many forms:

| Guest | Host |
|---|---|
| Firecracker microVM | Go process that creates disks, network, vsock, and secret delivery |
| WAMR module | ESP32 firmware that loads Wasm and exposes hardware functions |
| goja runtime | Go application that installs selected modules/globals |
| Go compiled to browser Wasm | Browser JavaScript shell using `syscall/js` bridge |
| wazero plugin | Go host that implements imports and manages guest memory |
| SQLite Wasm worker | Browser main thread that sends worker RPC and renders results |

The technologies differ, but the invariant is the same: **the guest computes; the host mediates side effects.**

## Why it matters to our work

Several KB entries depend on this model:

- [[Tribal/microvm-as-execution-boundary]] — VM owns execution, host owns I/O and lifecycle.
- [[Tribal/data-only-vs-host-access-module-split]] — safe modules are default; host-access modules are explicit capabilities.
- [[On-Ramp/wasm-from-go]] — Go/Wasm code cannot directly own browser capabilities; JavaScript hosts the bridge.
- [[Tribal/go-to-wasm-compilation]] — browser kernels stay testable when host interaction is a narrow API.
- [[Tribal/goja-execution-model]] and [[Tribal/goja-embedding-in-go]] — Go owns runtime setup, module installation, and side-effect surfaces.

Without this fundamental model, many project reports look unrelated. Firecracker, Wasm plugins, goja modules, browser workers, and Chrome extension content scripts feel like separate topics. With this model, they become instances of one design question: **what may the guest ask for, and what does the host do with that request?**

## The key result

A host-mediated sandbox has four invariants.

### 1. The boundary is explicit

There must be a concrete interface between guest and host. That interface might be:

- a vsock protocol,
- a Wasm import function,
- a `syscall/js` callback,
- a Go function installed into a goja runtime,
- a browser `postMessage` RPC,
- a JSON-through-memory ABI,
- a worker message protocol.

If there is no explicit interface, there is no useful boundary. Direct access turns the sandbox into a library call.

### 2. Capabilities are granted, not assumed

A fresh guest should start with little or no power. It receives capabilities from the host.

A capability is any authority to do something outside the guest:

- read a file,
- write a file,
- send a network request,
- access a secret,
- draw to a screen,
- query a database,
- call a model,
- inspect a page DOM,
- persist state.

The safe default is: **data-only computation is available; host access is opt-in.**

### 3. The host can inspect, deny, transform, and log requests

Mediation is not pass-through. If the guest asks to fetch a URL, the host can check an allowlist. If the guest asks to draw, the host can clip or batch. If the guest asks for a secret, the host can issue a short-lived scoped credential instead of handing out the real secret.

This is the difference between a sandbox and a tunnel. A tunnel lets the guest reach the world. A sandbox turns world access into a host decision.

### 4. The guest's view and the host's view are different

The guest sees abstractions: a filesystem, a function, a pointer, a module, a canvas, a database. The host sees implementation objects: disk images, memory buffers, imported functions, blob URLs, worker messages, OPFS handles.

Bugs happen when code forgets which side it is on.

## The intuition

Think of a sandboxed guest like a tenant in an apartment building. The tenant can arrange furniture and cook dinner inside the apartment. But the tenant cannot rewire the building, access the boiler room, copy the master keys, or open other apartments. If they need maintenance, they file a request. The building manager decides what to do.

The apartment is the guest. The building manager is the host. The maintenance request is the boundary protocol.

A bad sandbox gives the tenant a ladder, bolt cutters, and the master key because it is convenient. A good sandbox makes every outside-world action a request.

## What goes wrong when you don't know this

### 1. You give the guest direct access instead of a capability

The tempting shortcut is to pass the real thing into the guest: a filesystem handle, an HTTP client, a DOM object, a database connection, or a refresh token.

This is usually wrong. The guest can now do more than the host intended, and the host loses a place to log or deny behavior. In [[Tribal/data-only-vs-host-access-module-split]], this is why filesystem and process modules are not safe defaults in embedded goja runtimes.

### 2. You treat a wrapper as a sandbox

A wrapper around a dangerous capability is still a dangerous capability if it does not enforce policy.

For example, `readFileIfExists(path)` is still filesystem access. `fetch(url)` is still network access. `query(sql)` is still database access. The question is not whether the function name sounds safe; the question is what authority it conveys and whether the host can constrain it.

### 3. You confuse serialization with mediation

Passing requests as JSON does not make a boundary safe. JSON is only the message format. The host still needs a policy decision.

The [[PROJ - WASM Plugin REPL - Goja wazero Deep Dive]] report shows this clearly. The JSON-through-memory ABI is useful because it makes guest calls structured, but the security property comes from the host module and primitive registry deciding what imports exist and what they do.

### 4. You let the guest own persistence

Persistent state is authority. If a guest can write arbitrary persistent data, it can often affect future runs, leak information, or create confused-deputy bugs.

SQLide Browser avoids this by splitting responsibilities: Go/Wasm handles editor intelligence, while the SQLite worker owns database operations and OPFS persistence. The boundary is explicit enough that each layer has a job.

### 5. You forget lifecycle and cleanup

A host-mediated sandbox is not only about startup. The host also owns shutdown.

When a guest exits or crashes, the host must clean up:

- VM processes,
- network taps,
- block devices,
- Wasm instances,
- guest memory allocations,
- blob URLs,
- workers,
- content-script overlays,
- temporary credentials.

If cleanup is not host-owned, failed guests leak resources or leave authority behind.

## How the principle appears in our projects

### Firecracker and pi-sandbox

In Firecracker-style projects, the guest sees a Linux machine. The host sees a microVM process, root filesystem, block devices, vsock, network taps, and prepared workspaces.

The guest should not fetch secrets directly from Vault. The host prepares or brokers secret delivery, logs what happened, and collects outputs afterward. This is host mediation at the operating-system boundary.

### Capsule Lab and goja-in-Wasm

Capsule Lab runs user JavaScript inside goja inside Wasm inside the browser. That sounds excessive until you look at the capability story: the inner script has no DOM, no network, and no filesystem. It can only emit operations that the browser host interprets.

The browser is not just a display. It is the policy boundary.

### Goja module systems

A goja runtime starts empty or nearly empty. The Go host decides which globals and modules exist. Data-only helpers can be default; host-access modules require explicit installation.

This is the capability model in miniature. The host decides whether the script gets `fs`, `exec`, `http`, `obsidian`, `canvas`, or only pure helpers.

### Go/Wasm browser kernels

A Go program compiled to Wasm cannot freely touch the browser. It talks through `syscall/js`. That bridge can become a mess if the Go code grabs `document` and starts acting like it owns the page.

Our better pattern is a kernel boundary: Go owns computation; JavaScript owns browser capabilities. The host calls into Go and receives structured results or operations.

### Wazero plugins

In the WASM Plugin REPL, guests call imports like `repl.http_get` or `repl.prim_call`. The guest cannot open sockets by itself. The host provides an import and can validate, log, or reject.

The JSON-through-memory ABI solves data movement. The host module solves authority.

### Browser workers and overlays

A browser worker is also a sandbox boundary. The main thread sends messages; the worker computes or owns a subsystem. In SQLide, the SQLite worker owns DB execution and OPFS. The main thread owns UI.

The Hover Component Inspector shows a neighboring principle for content scripts: an overlay should be a guest on the page. It can inspect and render, but it should not steal pointer events, pollute the page, or claim more certainty about components than the browser can provide.

## A design checklist

When designing any sandbox or plugin boundary, ask these questions:

1. **What code is the guest allowed to run?**
2. **What can the guest observe by default?**
3. **What can the guest mutate by default?**
4. **What host capabilities are exposed?**
5. **Where is policy enforced?**
6. **Can the host log every privileged request?**
7. **Can the host deny a request without crashing the system?**
8. **Is the guest API narrow enough to test?**
9. **Who owns persistence?**
10. **Who owns lifecycle and cleanup?**

If the answer to “where is policy enforced?” is “inside the guest,” the boundary is probably wrong.

## Where we use it

- [[Tribal/microvm-as-execution-boundary]]
- [[Tribal/data-only-vs-host-access-module-split]]
- [[On-Ramp/wasm-from-go]]
- [[Tribal/go-to-wasm-compilation]]
- [[Tribal/goja-execution-model]]
- [[Tribal/goja-embedding-in-go]]

### Related PARC project reports

- [[PROJ - Firecracker VM - Guest Bring-Up, Host-Mediated Secrets, and Isolation Design]] — host prepares inputs, mediates secrets, and collects outputs from a microVM guest
- [[PROJ - Capsule Lab - A Sandboxed JS Capsule Runtime in the Browser]] — browser host mediates operations from a goja-in-Wasm guest
- [[PROJ - WASM Plugin REPL - Goja wazero Deep Dive]] — host module and primitive registry mediate guest plugin capabilities
- [[PROJ - Goja WASM Web REPL - A JavaScript Sandbox in the Browser]] — nested runtimes isolate user JavaScript from browser capabilities
- [[PROJ - SQLide Browser - Go Wasm SQL IDE]] — Go/Wasm owns editor intelligence while SQLite worker owns DB execution and OPFS
- [[PROJ - Hover Component Inspector - Building a Browser Overlay Lens]] — content-script overlay inspects page state without becoming page state
- [[PROJ - PaperS3 WAMR Debugging - Embedded Wasm Root Cause]] — Wasm guest loading on embedded hardware exposes host/guest memory ownership assumptions

## Where to go deeper

1. **Saltzer & Schroeder (1975), “The Protection of Information in Computer Systems.”** The classic source for least privilege, economy of mechanism, complete mediation, and fail-safe defaults.
2. **WASI capability model.** WASI is useful because it treats host functions and handles as capabilities instead of assuming a process has ambient OS authority.
3. **Firecracker architecture docs.** Firecracker is a concrete example of small VM isolation where the host owns devices and lifecycle.
4. **WebAssembly core and component-model material.** Wasm makes the host/guest memory and import boundary explicit, which is why it is a good teaching substrate for this principle.

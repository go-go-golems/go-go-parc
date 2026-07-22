# LangBlocks

## A pattern language, semantic kernel, and Go/Goja construction kit for scriptable systems

**Status:** architecture proposal and extraction plan  
**Source snapshot:** Tiny-IDP `d164ae59408bdd8bc21516274b446339b1761b1e`; go-go-goja `ae413f594d0ed4e36123ac925e195666e0f0e759`; PARC project and tribal notes as of `e0536cacd7626432c8ad78901543f3a77dee6033`  
**Scope:** scriptable applications, embedded language hosts, DSL compilers, durable workflow engines, generated hosts, firmware, operating systems, compilers, proof assistants, and formal-method kernels

---

# 1. Executive proposal

The work in Tiny-IDP should not be extracted as an identity-specific workflow package, nor should the broader go-go-goja ecosystem be collapsed into a single universal scripting engine. The reusable achievement is a **method for constructing scriptable systems whose language runtime is expressive but not sovereign**.

The proposed framework has three products:

1. **LangBlocks Specification** — a language-independent pattern language. It defines vocabulary, pattern cards, composition rules, lifecycle state machines, assurance profiles, and machine-readable architecture manifests. It is applicable to JavaScript, Lua, Starlark, WASM, custom DSLs, compiler pass languages, tactic languages, and generated code systems.
2. **go-go-langkit** — a Go implementation of the language-independent semantic blocks: contracts, canonical values, diagnostics, artifacts, callback manifests, outcomes, effects, continuations, generations, event records, assurance checks, and conformance suites. It contains no Goja values and no dependency on a guest language.
3. **go-go-goja/platformkit** — the concrete Goja backend and authoring toolkit, built on the existing `engine.RuntimeFactory`, `runtimeowner`, `runtimebridge`, module descriptors, and xgoja provider/runtime-plan machinery. It implements Goja compilation, definition collectors, VM-local callback registries, nominal handles, Promise settlement, runtime leasing, interruption, and activation checks.

Applications then provide **domain kits**, for example:

- Tiny-IDP supplies identity schemas, capability families, outcomes, effects, continuations, committers, and evidence.
- A 3D editor supplies scene/object handles, tool state machines, scene-operation effects, undo records, viewport presentations, and renderer adapters.
- A window manager supplies layout IR, window/query capabilities, shell effects, input-mode continuations, typed presentations, and an operation journal.
- A compiler supplies AST handles, pass contracts, diagnostic outcomes, rewrite plans, artifact identities, and verifier passes.
- A proof assistant supplies term and goal references, tactic contracts, proof-state continuations, candidate theorem effects, and a small native proof checker that remains the authority.

The central architecture is:

```text
Authoring languages
  JavaScript | Go builders | YAML | Lua | Starlark | custom syntax
                         |
                         v
             Parse / normalize / validate
                         |
                         v
        Layered, serializable semantic IRs
                         |
               compile / lower / link
                         |
                         v
     Immutable artifact + registration manifest
                         |
           activate under a runtime profile
                         |
                         v
       Owned runtime instance / worker lease
                         |
       typed input + invocation capability lease
                         |
                         v
       closed decision + inert effect plan
                         |
            native host interpreters
       /             |              \
 presentation   durable state   authoritative effects
 renderer       continuation    transaction/outbox/kernel
```

The primary design principle is:

> **A guest language may describe, select, calculate, and propose. The host kernel validates, owns authority, persists durable state, and commits externally meaningful changes.**

This is not a restriction to declarative languages. Imperative callbacks remain useful. The restriction is that stable and security-significant boundaries are represented by explicit contracts rather than by arbitrary guest heap state.

---

# 2. What the source systems collectively discovered

## 2.1 Tiny-IDP: a policy language above an identity microkernel

Tiny-IDP contributes the high-assurance end of the design space:

- definition-time JavaScript produces a pure-Go program contract while callbacks remain VM-local;
- handler contracts combine value schemas, permitted outcomes, required capabilities, allowed effects, and resource budgets;
- activation re-materializes the program and verifies program, callback, and schema identities;
- each invocation receives only explicitly bound, bounded, revocable capabilities;
- JavaScript returns one member of a closed outcome family;
- externally meaningful changes are inert effect plans until native code validates and commits them;
- browser-spanning control flow is a serialized continuation containing a handler label and typed environment, not a suspended Promise or VM heap;
- continuations are pinned to executable generations;
- a runtime is reusable only after a positive proof of safe completion and complete asynchronous settlement.

This is a practical combination of staging, defunctionalization, object capabilities, effect interpretation, runtime-enforced type/effect contracts, generation management, and fail-stop resource leasing.

## 2.2 go-go-goja: the owned runtime and generated-host substrate

go-go-goja contributes the reusable runtime substrate:

- an immutable runtime factory is built from explicit modules and initializers;
- each runtime has one owner, an event loop, a lifetime context, runtime-scoped values, and ordered cleanup;
- asynchronous native work executes outside the VM and posts settlement back to the owner;
- startup, runtime-lifetime, current owner-entry, and custom operation contexts are distinct;
- module-selection middleware separates data-only defaults from host-access modules;
- xgoja distinguishes packages compiled into a binary from modules exposed by a runtime plan;
- provider packages register modules, command sets, help, sources, and capabilities under stable IDs;
- module-owned descriptors generate TypeScript declarations and permit drift checks;
- generated applications are explicit products rather than invisible runtime wiring.

The decisive abstraction is **frozen composition plan versus live owned instance**.

## 2.3 Widget DSL and DMETA: intent, layered IRs, and target ownership

The Widget DSL and DMETA work contribute the compiler and presentation side:

- authors express semantic intent rather than target implementation details;
- normalization and validation precede rendering;
- typed widget instances, slots, actions, and data contracts form a stable IR;
- target layers own styling, widgets, layout, React details, and target-specific event wiring;
- semantic IR, interaction IR, web metadesign-system IR, and React target are separate lowering stages;
- actions are represented in IR rather than hidden inside renderer callbacks;
- versions and host migrations are explicit compatibility events;
- semantic tests, serialized-IR tests, and visual tests remain separate;
- generated files have declared lifecycle modes: regenerate-only, scaffold-once, or sidecar.

The reusable lesson is that a universal layer must stop before target-specific nouns enter it.

## 2.4 researchctl: graph construction, deterministic execution, and evidence promotion

researchctl contributes a rigorous distinction between a specification language and an execution workbench:

- YAML, JSON, and JavaScript converge on the same validated Go graph;
- research project loading does not execute experiments;
- experiment plans compile to deterministic simulator runs;
- execution emits events, metrics, manifests, and artifacts;
- importing results into the research graph is a separate, reviewable transition;
- callback flexibility supports exploration, while mature behavior can be promoted into tested native device, policy, or metric families.

The reusable lesson is **no silent mutation across semantic domains**. Execution artifacts become knowledge only through an explicit evidence-import operation.

## 2.5 The common shape

Across these systems, the repeated architecture is:

```text
human-friendly authoring
  -> normalized semantic representation
  -> compiled or lowered plan
  -> explicit runtime composition
  -> bounded execution
  -> typed decisions/events/effects
  -> native interpretation
  -> durable artifacts and evidence
```

The systems differ in assurance requirements, but the boundaries are structurally the same.

---

# 3. Goals and non-goals

## 3.1 Goals

LangBlocks should make the following reusable:

- phase separation and layered lowering;
- language-neutral contracts and stable identities;
- runtime ownership and asynchronous scheduling;
- explicit authority and capability leasing;
- outcome and effect interpretation;
- durable, versioned control state;
- deterministic registration and activation checks;
- event, snapshot, replay, and evidence patterns;
- target-independent presentation IRs;
- conformance, diagnostics, documentation, and generated-language bindings;
- assurance profiles ranging from a trusted REPL to a proof-kernel-adjacent extension system.

## 3.2 Non-goals

LangBlocks must not become:

- one universal AST or one universal workflow language;
- one fixed schema system;
- one global taxonomy of all domain effects;
- a wrapper that pretends in-process Goja is a hostile-code security boundary;
- a requirement that every script be stateless or durable;
- a serializer for VM heaps, closures, stacks, goroutines, or Promises;
- a replacement for a domain kernel, transaction manager, renderer, compiler verifier, or proof checker;
- a generic interface so broad that every backend implements meaningless stubs;
- a compatibility prison. When a core semantic model is wrong, versioned hard cutovers remain legitimate.

---

# 4. The three-tier product architecture

## 4.1 Tier 1: LangBlocks Specification

This repository or specification package contains:

- a glossary and reference architecture;
- versioned pattern cards;
- a machine-readable pattern schema;
- platform manifests;
- composition constraints and diagnostic IDs;
- lifecycle state machines;
- assurance profiles;
- backend and domain conformance requirements;
- case studies and threat-model templates;
- optional formal models in TLA+, Alloy, or another suitable notation.

It must be implementable outside Go. A Rust/QuickJS host, a C/Lua firmware, a JVM language server, or a theorem prover should be able to use the same pattern vocabulary.

## 4.2 Tier 2: go-go-langkit

This is a language-neutral Go library. Its types contain no `goja.Value`, `goja.Callable`, Lua stack pointer, WASM memory pointer, or other backend-owned object.

Proposed packages:

```text
go-go-langkit/
  contract/       programs, handlers, state machines, schemas by reference
  value/          canonical wire values and codec interfaces
  schema/         pluggable type-system and information-flow interfaces
  diagnostic/     stable paths, IDs, source spans, deterministic ordering
  artifact/       source, semantic, link, schema, profile, and ABI identities
  registry/       stable IDs, manifests, dependency/link checks
  outcome/        domain-defined closed decision families
  effect/         effect requests, plans, policies, preparation, receipts
  continuation/   defunctionalized continuation envelopes and stores
  generation/     activation, retention, migration, retirement
  event/          commands, events, projections, snapshots, transcripts
  assurance/      profiles, composition checks, proof obligations
  conformance/    backend-independent test vectors and state-machine tests
  descriptor/     API/module/capability descriptors for docs and bindings
```

This tier implements semantic mechanisms but does not execute JavaScript.

## 4.3 Tier 3: go-go-goja/platformkit

This tier adapts Goja to go-go-langkit while preserving the current runtime substrate:

```text
go-go-goja/
  pkg/engine/          existing frozen factory and live runtime
  pkg/runtimeowner/    existing single-owner Call/Post discipline
  pkg/runtimebridge/   existing context and runtime-service bridge
  pkg/xgoja/           existing generated-host and provider composition
  pkg/platformkit/
    compiler/          source bundle -> goja.Program + source map
    definition/        collector, program export, callback manifest
    activation/        materialize, compare, link, fingerprint
    invoke/            canonical input/output, Promise handling, task drain
    capability/        invocation leases and budget meters
    brand/             VM-local nominal object registries
    pool/              exclusive worker lease and disposition policy
    descriptor/        Goja module descriptors and generated JS/TS surfaces
    testing/           Goja backend conformance suite
```

Tiny-IDP-specific schemas, outcomes, effects, evidence, browser projection, and identity transactions remain in Tiny-IDP. The reusable Goja mechanisms move down.

---

# 5. A reference model for scriptable systems

A scriptable system can be factored into six planes.

## 5.1 Authoring plane

The authoring plane contains source languages and ergonomic APIs:

- JavaScript modules and fluent builders;
- YAML/JSON declarations;
- Go builders;
- custom textual syntax;
- interactive REPL cells;
- generated source.

Authoring values may be convenient, partial, and syntactic. They are not runtime plans.

## 5.2 Semantic plane

The semantic plane contains normalized, complete, inspectable representations:

- program contracts;
- workflow/state-machine graphs;
- widget or interaction IR;
- compiler pass graphs;
- experiment run specifications;
- schemas, source spans, warnings, and stable IDs.

This plane is the primary interoperability boundary.

## 5.3 Runtime plane

The runtime plane owns:

- guest runtime construction;
- module and global exposure;
- runtime ownership and scheduling;
- live callback registries;
- invocation and asynchronous settlement;
- interruption, draining, pooling, and disposal.

The runtime plane never becomes the durable source of truth unless an explicit session pattern says otherwise.

## 5.4 Authority plane

The authority plane owns:

- capabilities and their leases;
- opaque native handles;
- secrets and evidence;
- effect policies and committers;
- transactions, outboxes, sagas, hardware access, IPC, or kernel calls.

Authority is supplied by the host; it is not discovered by the guest.

## 5.5 Durability plane

The durability plane owns:

- continuations;
- event journals;
- snapshots and projections;
- artifact generations;
- migration and retention;
- replay transcripts;
- durable evidence and receipts.

It stores semantic values and references, never runtime-owned guest objects.

## 5.6 Assurance plane

The assurance plane is orthogonal. It contains:

- canonicalization and fingerprints;
- deterministic diagnostics;
- resource budgets;
- trust profiles;
- conformance vectors;
- trace and provenance records;
- property tests, model checks, differential tests, and independent checkers.

A system selects only the assurance blocks its risk model requires.

---

# 6. The core vocabulary

## 6.1 Source, definition, contract, artifact, generation

These terms should not be conflated:

- **Source** is author-controlled text or structured input.
- **Definition IR** is the result of evaluating or parsing the authoring language.
- **Contract IR** is the validated language-neutral declaration of handlers, types, capabilities, outcomes, effects, state machines, and budgets.
- **Executable artifact** is backend-specific compiled code plus the contract and manifests needed to activate it.
- **Generation** is an activated artifact under a particular host ABI and runtime profile, retained for invocation and durable resumption.

## 6.2 Callback reference

A callback reference is a stable, serializable name. It is not a closure. Each runtime instance links that reference to a runtime-local function.

```text
stable world                 runtime-local world
------------                 -------------------
handler "tool.drag.v2"  <->  closure in runtime worker 7
handler "tool.drag.v2"  <->  closure in runtime worker 8
```

## 6.3 Canonical wire value

Stable boundaries should use a codec-neutral envelope rather than assuming every domain uses JSON:

```go
type WireValue struct {
    Type     TypeRef
    Codec    CodecID          // canonical-json, protobuf, cbor, proof-term-v1, ...
    Data     []byte
    Digest   Digest
    Labels   []DataLabel      // public, confidential, secret-ref, evidence, ...
}
```

JSON is an excellent default for human-facing DSLs. It should not be mandatory for compiler IR, proof terms, fixed-memory firmware, or large binary geometry.

## 6.4 Handler contract

A handler contract is a runtime-enforced type, effect, authority, region, and resource declaration:

```go
type HandlerContract struct {
    ID                    HandlerID
    Kind                  string
    Input                 TypeRef
    Outcomes              map[OutcomeKind]TypeRef
    RequiredCapabilities  []CapabilityRef
    AllowedEffects        []EffectRef
    Budget                ResourceBudget
    State                 StatePolicy
    Determinism           DeterminismContract
    Source                SourceSpan
}
```

It states not merely what values a callback accepts, but what control decisions it can make, what authority it receives, what effects it may propose, how long it may run, which state lifetimes it may touch, and what replay claims are valid.

## 6.5 Decision and effect

A guest invocation returns a **decision**. A decision may contain an inert **effect plan**. It does not directly perform authoritative effects.

```go
type Decision struct {
    Kind          OutcomeKind
    Payload       WireValue
    Continuation  *ContinuationRequest
    Effects       []EffectRequest
}
```

The domain defines the closed set of decision kinds. The host performs exhaustive interpretation.

## 6.6 Runtime disposition

Every invocation also yields a runtime disposition:

```go
type RuntimeDisposition string

const (
    Reuse      RuntimeDisposition = "reuse"
    Destroy    RuntimeDisposition = "destroy"
    Quarantine RuntimeDisposition = "quarantine"
)
```

A valid business decision and a reusable runtime are separate facts. A callback may have produced a valid denial while leaving uncertain asynchronous work; the decision can be accepted while the worker is destroyed.

---

# 7. Pattern catalog

The patterns below are the initial reusable catalog. Each should eventually be represented as a machine-readable pattern card with `requires`, `provides`, `conflicts`, invariants, proof obligations, conformance tests, and backend realizations.

## 7.1 Compilation and representation patterns

### P01 — DSL → normalized configuration → compiled plan

**Problem:** Human-friendly input is partial, ambiguous, defaulted, and unsuitable for direct execution.

**Shape:** Parse raw input, normalize and validate it, then compile or lower it into a complete immutable plan. The executor sees only the plan.

**Invariants:**

- raw DSL never reaches the executor;
- defaults are inserted exactly once;
- references resolve before compilation;
- warnings survive into the plan and user-facing output;
- the compiled plan is immutable.

**Uses:** media pipelines, widget DSLs, xgoja generated hosts, compiler pass plans, firmware build images.

### P02 — Layered IR with target ownership

**Problem:** A single IR accumulates semantic, interaction, rendering, platform, and code-generation details.

**Shape:** Introduce separate IR layers with explicit lowering passes. Universal layers remain target-neutral; target layers own target nouns.

**Law:** If an IR intended to be universal mentions React components, X11 windows, GPU buffers, HTTP response writers, machine registers, or proof-assistant UI widgets, lowering boundaries are misplaced.

### P03 — Semantic firewall

**Problem:** Guest objects, functions, pointers, host wrappers, and runtime-specific values escape into durable or shared state.

**Shape:** Every stable boundary crosses through a canonical codec and a language-neutral type. Runtime values remain behind the backend adapter.

**Invariants:**

- no guest function or object identity in contract IR;
- no VM value in continuation, event, artifact metadata, or database record;
- every crossing has a codec, type reference, byte bound, and data classification.

### P04 — Stable callback name, VM-local closure

**Problem:** Executable callbacks are inherently runtime-local, but contracts and durable state require stable references.

**Shape:** Store stable callback IDs in contracts; materialize one private callback registry per runtime instance.

**Consequence:** Runtime instances are independently reproducible without sharing guest functions across VMs.

### P05 — Dual-channel definition agreement

**Problem:** Definition-time code may register one program through host callbacks while exporting a different value.

**Shape:** Collect definitions through a host collector and require the module's public export to be canonically equal to the collected program.

**Use:** catches hidden registration side effects, accidental exports, and ambiguous module contracts.

### P06 — Canonical artifact identities

**Problem:** A single source hash cannot explain whether a change affects executable code, semantic contracts, schemas, authority, or linking.

**Shape:** Maintain separate identities:

```text
Source identity        exact authoring source or source graph
Executable identity    backend bytecode/program and compiler version
Semantic identity      normalized contract and state machines
Link identity          callback/entry-point manifest
Schema identity        type and data-classification registry
Profile identity       exposed modules, globals, budgets, trust policy
Host ABI identity      capability/effect/module descriptor versions
```

A generation ID can hash the identities required by the domain's resumption policy.

### P07 — Deterministic diagnostics

**Problem:** Map iteration, parallel validation, or backend ordering produces unstable errors and CI noise.

**Shape:** Every diagnostic has a stable ID, path, source span, severity, and deterministic sort order.

**Benefit:** activation failures, generated reports, tests, and migration tools become reproducible.

## 7.2 Runtime and concurrency patterns

### P08 — Frozen factory, live instance

**Problem:** Runtime composition and runtime state become entangled.

**Shape:** Build and validate an immutable factory or runtime plan. Instantiate independent live runtimes from it.

**Invariants:**

- the factory contains no mutable per-runtime state;
- duplicate module and initializer IDs fail at build time;
- two runtimes from one factory do not share guest globals or runtime-scoped services unless explicitly configured.

### P09 — Single-owner runtime

**Problem:** Most embedded interpreters are not safe for concurrent host access.

**Shape:** Exactly one owner serializes every operation touching the guest runtime. Other goroutines or threads perform blocking work and post closures/messages back to the owner.

**Required operations:** request/response call, fire-and-forget post, idle drain, shutdown, reentrant fast path, named operation labels.

### P10 — Named cancellation domains

**Problem:** A generic context or cancellation token is reused for construction, request work, retained resources, and cleanup.

**Shape:** Name lifetimes by semantics:

- build/compile context;
- runtime startup context;
- runtime lifetime context;
- current invocation context;
- custom external-event context;
- cleanup context;
- durable continuation lifetime.

**Law:** A value or callback retained beyond an invocation may not depend on the invocation's cancellation domain.

### P11 — Owner-mediated asynchronous rendezvous

**Problem:** Native async work must settle guest Promises, coroutines, futures, callbacks, or mailboxes without touching the VM concurrently.

**Shape:** Create the guest rendezvous on the owner, do blocking work externally, then post settlement back through the owner under an explicit context.

**Language realizations:** Goja Promise; Lua coroutine/mailbox; WASM poll handle; Starlark host future; custom DSL operation token.

### P12 — Invocation task group

**Problem:** A handler returns while capability calls or callbacks remain pending.

**Shape:** Every invocation owns a task group and active/revoked flag. Completion requires the primary result and complete settlement or cancellation of all spawned work.

**Law:** An invocation cannot be declared reusable while its task count is nonzero or settlement state is uncertain.

### P13 — Transactional runtime lease

**Problem:** A pooled runtime may be corrupted, interrupted, or contaminated even when an error is caught.

**Shape:** Lease one runtime exclusively. Return it only after a positive safety proof. Otherwise destroy or quarantine it and create a replacement.

**Poison conditions include:** timeout, interruption race, panic, uncaught exception, malformed boundary value, failed drain, late callback, backend invariant violation, or uncertain reset.

### P14 — Session as runtime + policy + history

**Problem:** REPL or notebook semantics emerge accidentally from repeated evaluation.

**Shape:** Treat a session as a live runtime, an explicit evaluation policy, and durable source/history. Restore by replay or explicit snapshots according to the selected profile.

**Warning:** replay is not transparent for side-effectful cells. Such cells require idempotency, recorded transcripts, or replay suppression.

## 7.3 Authority, capability, and effect patterns

### P15 — Three-stage authority exposure

The ecosystem suggests a useful authority lattice:

```text
1. Compiled availability  — code exists in the host binary
2. Runtime exposure       — a profile exposes a module or API name
3. Invocation binding     — a particular handler receives a capability lease
4. Effect acceptance      — the host accepts a proposed effect kind
5. Commit authority       — a native kernel actually changes authoritative state
```

Each stage can only narrow authority. A module compiled into a binary need not be visible; a visible capability need not be bound to every handler; a handler permitted to propose an effect cannot commit it itself.

### P16 — Data-only versus host-access modules

**Problem:** Convenience defaults silently create ambient authority.

**Shape:** Data-transforming modules may be enabled in permissive profiles. Filesystem, process, network, device, display, database, and other host-access modules require explicit exposure.

**Caveat:** a thin wrapper around a host resource remains host access.

### P17 — Invocation capability lease

**Problem:** A global host object grants every script broad, persistent authority.

**Shape:** A handler contract declares capability versions. The host binds only those capabilities for one invocation. The lease has:

- active/revoked state;
- invocation context;
- input/output schemas and byte bounds;
- call, concurrency, and time budgets;
- audit identity;
- optional determinism and transcript policy.

A retained guest function becomes powerless after revocation.

### P18 — Opaque nominal handle

**Problem:** Raw host objects or forgeable tagged records leak internal authority and representation.

**Shape:** Give the guest an opaque nominal handle whose validity is checked by a host table.

**Backend realizations:**

- Goja object identity mapped in Go;
- Lua userdata with protected metatable;
- WASM integer handle with slot and generation counter;
- Starlark custom frozen value;
- IPC capability token or file descriptor;
- proof-assistant native term/goal reference.

**Law:** Handle representation is not authority. The host table, type brand, lifetime, and generation perform validation.

### P19 — Closed decision algebra

**Problem:** `undefined`, exceptions, arbitrary maps, and convention-based result shapes acquire security or control-flow meaning.

**Shape:** Define a finite family of domain decisions. Validate each payload and interpret exhaustively in native code.

Examples:

- identity: continue, present, challenge, commit, complete, deny, skip, error;
- editor tool: preview, await-input, commit-operations, cancel, error;
- compiler pass: unchanged, rewrite-plan, emit-diagnostics, defer, fail;
- proof tactic: solved, subgoals, suspended, rejected, internal-error.

### P20 — Effect plan, native interpreter

**Problem:** Guest code directly mutates authoritative state, making validation and transaction boundaries implicit.

**Shape:** Guest code returns inert, typed effect requests. A native interpreter:

1. checks that the handler may propose each effect;
2. validates payloads and references;
3. checks preconditions and idempotency;
4. prepares a concrete plan;
5. commits through the correct authority boundary;
6. records a receipt.

### P21 — Honest commit models

Not every effect can be one database transaction. Effect specifications declare a commit model:

- **pure** — no external mutation;
- **atomic-local** — one local transaction;
- **outbox** — atomic local state plus durable delivery record;
- **saga** — ordered operations with compensations;
- **ephemeral** — external action with no durability guarantee;
- **kernel-check** — accepted only after an independent verifier;
- **hardware** — device operation with explicit partial-failure semantics.

The framework must reject an `atomic` claim that includes uncoordinated email, network, GPU, filesystem, or device side effects.

### P22 — Native evidence and secret references

**Problem:** A guest manufactures proof state or receives secrets as ordinary serializable values.

**Shape:** Authoritative verification happens natively. Guest code sees either:

- an opaque secret handle scoped to one invocation;
- a bounded evidence projection created by native verification;
- a durable reference to native evidence, not the sensitive value itself.

Persistence policies prevent secret-labeled values from entering public continuations, logs, or presentations.

## 7.4 Durability and evolution patterns

### P23 — Defunctionalized durable continuation

**Problem:** Browser waits, user input, device interrupts, long jobs, or proof subgoals outlive the current runtime.

**Shape:** Replace a suspended closure with a data record:

```text
Continuation =
  format version
  + program and generation identity
  + machine/workflow identity
  + resume-handler label
  + typed environment
  + environment schema/version
  + revision
  + expiry and status
  + binding digests
  + opaque native references
```

This is defunctionalization: the closure's code becomes a stable handler label; its free variables become a schema-checked environment.

**Law:** capabilities, guest values, closures, stacks, Promises, goroutines, and raw secrets are never persisted.

### P24 — Generation-pinned resumption

**Problem:** Hot reload causes old durable state to run under new code with changed semantics.

**Shape:** Continuations and durable jobs identify the generation that created them. Resume under that generation unless an explicit migration is validated.

**Generation manager responsibilities:** activation, reference counts, retention, retirement, migration, rollback, and garbage collection.

### P25 — Revisioned state transition

**Problem:** retries, double submissions, reconnects, and concurrent workers advance a continuation more than once.

**Shape:** Durable state has a monotonically increasing revision and is advanced with compare-and-swap semantics. Terminal, revoked, expired, or stale revisions cannot advance.

### P26 — Event journal, projection, snapshot

**Problem:** live UI or runtime-local state becomes the source of truth.

**Shape:** Commands produce canonical events. Projections derive UI or query state. Snapshots accelerate recovery. Reconnect receives snapshot before live events.

This block is optional but valuable for editors, window managers, collaborative webapps, operating systems, research workbenches, and proof sessions.

### P27 — Replay transcript

**Problem:** execution is called deterministic even though it reads clocks, randomness, network responses, device state, or scheduling order.

**Shape:** Record capability answers, seeds, scheduling decisions, effect receipts, and relevant environment identities. Replay substitutes or verifies the transcript.

**Key distinction:** deterministic registration, deterministic execution, deterministic scheduling, deterministic effects, and deterministic replay are separate properties.

### P28 — Explicit migration

**Problem:** schema or handler changes are silently applied to durable state.

**Shape:** Migration is a pure, versioned operation with source and target identities, diagnostics, and conformance tests. The default is strict rejection, not best-effort reinterpretation.

## 7.5 Presentation and target patterns

### P29 — Typed presentation instance

**Problem:** scripts, plugins, or models generate arbitrary target code such as HTML, JSX, X11 drawing commands, or editor widgets.

**Shape:** The producer selects a registered presentation type and supplies schema-checked properties, actions, and slots. A target registry owns rendering.

### P30 — Action as IR, not hidden callback

**Problem:** renderer-local callbacks hide authority and make presentations non-serializable.

**Shape:** Actions carry stable IDs, intents, schemas, and effect or command bindings. The renderer emits a typed action event; the host dispatches it.

### P31 — Headless core, target adapter

**Problem:** React, terminal, desktop, or device UI becomes the architecture owner.

**Shape:** Transport, state, validation, registries, and action routing remain headless. React, terminal, X11/Wayland, native mobile, or 3D viewport adapters consume the same typed instances.

### P32 — Preset and recipe layer

**Problem:** the universal IR either becomes too low-level or absorbs product-specific conventions.

**Shape:** Put reusable product and design-system choices in presets/recipes above the IR and below authoring. Core semantics remain portable.

## 7.6 Assurance, testing, and tooling patterns

### P33 — Separate verification language

**Problem:** test scripts receive the same authority as production scripts and can bypass the kernel they are meant to verify.

**Shape:** Verification source compiles to data-only scenarios, fakes, transcripts, assertions, and expected outcomes. A native runner materializes them against an explicit step/capability registry.

### P34 — Evidence promotion as an explicit transition

**Problem:** running an experiment, simulation, compiler pass, or proof search silently rewrites the authoritative project or theorem state.

**Shape:** Execution produces artifacts and receipts. A separate import/promotion operation validates provenance and proposes a reviewable update.

### P35 — Descriptor as tooling source of truth

**Problem:** runtime APIs, TypeScript declarations, schemas, docs, CLI help, and capability catalogs drift.

**Shape:** Modules and domain kits own structured descriptors. Registration, generated bindings, docs, examples, and conformance stubs derive from the same descriptor where practical.

### P36 — Flexible callback to native primitive promotion

**Problem:** exploratory callbacks become permanent, opaque infrastructure.

**Shape:** Give extension behavior a maturity ladder:

```text
ad-hoc callback
  -> named callback with contract
  -> reusable declarative IR node
  -> registered native primitive/provider
  -> independently verified kernel primitive
```

Promotion is driven by frequency, assurance needs, performance, and the desire for stronger tests.

### P37 — Generated-artifact lifecycle

**Problem:** regeneration overwrites hand-maintained work or stale generated files masquerade as source.

**Shape:** Every generated output is classified as regenerate-only, scaffold-once, or sidecar. Tools enforce the lifecycle.

### P38 — Assurance profile

**Problem:** every application either pays the full high-assurance cost or receives no guidance.

**Shape:** Bundle required patterns and conformance tests into named profiles while permitting additional blocks.

Profiles are detailed in section 12.

---

# 8. Cross-cutting algebras

The deepest generic extraction is not an API but a set of small algebras that can be composed.

## 8.1 Lifetime algebra

Every relevant object belongs to a lifetime region:

```text
build < generation < runtime < session < invocation < async-operation
                              \
                               durable-continuation / journal
```

The partial order is semantic rather than strictly temporal. The key rule is:

> A longer-lived container cannot retain a shorter-lived authority-bearing value unless it stores a validated durable reference and reacquires authority later.

Examples of invalid flows:

- an invocation capability stored in a runtime global;
- a Goja object stored in a continuation;
- a request context used by a hardware listener;
- a database transaction handle retained by a Promise after the request ends;
- a proof-goal pointer retained after its environment generation is unloaded.

This is a runtime-enforced region discipline.

## 8.2 Authority algebra

Authority narrows through stages:

```text
compiled set ⊇ runtime-exposed set ⊇ handler-declared set
             ⊇ invocation-bound set ⊇ accepted effects ⊇ committed effects
```

No downstream stage may widen the set without a new host decision.

## 8.3 Data-classification algebra

A minimal classification system might be:

```text
public
internal
confidential
secret
opaque-reference
native-evidence
```

Schemas and codecs specify where each class may flow. For example, `secret` cannot enter presentation or public continuation state; `native-evidence` can be projected only through a declared declassifier; `opaque-reference` can cross a boundary only if the destination knows its type, generation, and resolver.

## 8.4 Decision/effect algebra

A decision controls interpreter flow; an effect requests mutation. They are related but not identical.

```text
invoke(handler, input, capabilities) -> decision
interpret(decision, durable-state)   -> transition-plan
commit(transition-plan, authority)   -> receipt + new-state
```

Keeping the three judgments separate prevents a callback return from being mistaken for a committed fact.

## 8.5 Determinism algebra

A manifest should declare determinism dimension by dimension:

- **normalization determinism:** same source and explicit environment yield the same normalized IR;
- **definition determinism:** same artifact yields the same registration manifest;
- **execution determinism:** same input and capability transcript yield the same decision;
- **scheduling determinism:** async order is fixed or recorded;
- **effect determinism:** same prepared plan and authoritative state yield the same receipt;
- **replay determinism:** a complete transcript reconstructs the specified observable state;
- **build reproducibility:** identical build inputs produce the same executable identity.

A system must not infer any of these merely because its interpreter has no JIT.

---

# 9. Formal operational core

A compact language-neutral semantics helps prevent the implementation API from becoming the specification.

Let:

- `A_g` be activated artifact generation `g`;
- `h` be a stable handler reference;
- `v` be a canonical input value;
- `C` be an invocation capability lease;
- `d` be a decision;
- `τ` be a trace/transcript;
- `q` be a runtime disposition;
- `S` be durable host state;
- `E` be authoritative external state.

## 9.1 Invocation judgment

```text
A_g ; h ; v ; C  ⇓  d ; τ ; q
```

This judgment is valid only when:

- `h` resolves in the runtime-local registry for `A_g`;
- `v` satisfies the handler input type;
- `C` satisfies exactly the required capability versions and bounds;
- `d` is an allowed decision with valid payload and effects;
- all invocation tasks have settled or been canceled;
- `q` records whether the runtime can be reused.

## 9.2 Native interpretation judgment

```text
A_g ; d ; S ; E  →  P
```

`P` is a prepared transition plan. This stage validates domain semantics, references, revisions, preconditions, and commit model.

## 9.3 Commit judgment

```text
P ; S ; E  ↦  S' ; E' ; receipt
```

Only the host authority layer can perform this judgment.

## 9.4 Resume judgment

For continuation `κ = (g, h, env, rev, bindings, refs)` and external event `x`:

```text
load-and-verify(κ, x) -> input
A_g ; h ; input ; reacquire(bindings) ⇓ d ; τ ; q
advance-CAS(κ.rev, d) -> κ' | terminal
```

The guest runtime is reconstructed or leased fresh. The persisted continuation does not contain suspended execution.

---

# 10. Lifecycle state machines

These state machines should become conformance models.

## 10.1 Artifact and generation

```text
Source
  -> Parsed
  -> Normalized
  -> Validated
  -> Compiled
  -> Linked
  -> Activated
  -> Retiring
  -> Collected

Any pre-activation state -> Rejected
Activated -> Revoked
```

## 10.2 Runtime worker

```text
New -> Materialized -> Idle -> Leased -> Draining -> Idle
                                  |          |
                                  +--------> Poisoned -> Closed
Idle -> Closing -> Closed
```

Only `Draining -> Idle` returns a worker to the pool.

## 10.3 Capability lease

```text
Declared -> Bound -> Active -> Revoking -> Revoked
                         |
                         +-> Exhausted -> Revoked
```

Calls after `Revoked` fail locally without invoking the host operation.

## 10.4 Continuation

```text
Active(rev n)
  -> Advanced(rev n+1)
  -> Consumed
  -> Denied
  -> Revoked
  -> Expired
```

Transitions require the expected revision and generation.

## 10.5 Effect plan

```text
Proposed -> Validated -> Prepared -> Committed -> Receipted
                 |           |
                 -> Rejected -> Aborted
```

Outbox and saga models add delivery and compensation substates.

---

# 11. Machine-readable pattern composition

The pattern language should be executable enough to catch architectural contradictions.

## 11.1 Pattern card example

```yaml
apiVersion: langblocks.dev/pattern/v1
kind: Pattern
metadata:
  id: defunctionalized-continuation
  version: 1
  family: durability
spec:
  problem: durable control flow cannot retain guest runtime state
  requires:
    - stable-callback-reference
    - canonical-wire-value
    - generation-identity
    - revisioned-store
  provides:
    - durable-resumption
    - restart-safety
  conflicts:
    - serialized-vm-heap
    - persisted-invocation-capability
  invariants:
    - environment contains no backend-owned values
    - resume handler resolves in the pinned generation
    - advancement uses compare-and-swap revision
  conformance:
    - continuation-roundtrip
    - forged-handle-rejection
    - stale-generation-rejection
    - duplicate-resume-rejection
```

## 11.2 Platform manifest example

```yaml
apiVersion: langblocks.dev/platform/v1
kind: ScriptPlatform
metadata:
  name: scene-editor-tools
spec:
  frontend:
    language: javascript
    backend: goja
    trust: operator-authored
  compilation:
    pipeline: [parse, normalize, validate, compile, link]
    contract: scene-tool/v1
  runtime:
    factory: frozen
    owner: single
    workers: exclusive-pool
    reusePolicy: positive-proof
    moduleProfile: scene-tool-safe
  authority:
    capabilities:
      - scene.query.selection/v1
      - scene.query.raycast/v1
    effects:
      - scene.object.create/v1
      - scene.object.transform/v1
      - scene.mesh.replace/v1
  durability:
    continuations: modal-tool/v1
    generationPolicy: pinned
    journal: scene-operations/v1
  assurance:
    profile: contracted-durable
```

## 11.3 Composition diagnostics

A `langblocks doctor` tool should report contradictions such as:

- `LBK-LIFE-001`: invocation-scoped capability referenced by durable continuation;
- `LBK-ASYNC-002`: async host binding selected without runtime owner or settlement drain;
- `LBK-POOL-003`: pooled runtime selected without reset or poison/disposition policy;
- `LBK-DET-004`: deterministic-execution claim includes unrecorded clock capability;
- `LBK-EFFECT-005`: atomic effect plan includes uncoordinated external delivery;
- `LBK-IR-006`: universal IR references target-specific component type;
- `LBK-GEN-007`: durable continuation selected without generation retention or migration policy;
- `LBK-SECRET-008`: secret-labeled field permitted in public presentation or carry;
- `LBK-REPLAY-009`: replay restore includes non-idempotent top-level effect without transcript policy;
- `LBK-SANDBOX-010`: hostile-code trust profile uses only an in-process interpreter boundary.

---

# 12. Assurance profiles

Profiles are cumulative defaults, not a ranking of product quality.

## 12.1 Profile W — Workbench

Use for trusted REPLs, local automation, experiments, and operator tools.

Required:

- explicit runtime lifetime and close;
- single-owner runtime where required by backend;
- module inventory;
- basic diagnostics and tracing.

Permitted:

- persistent guest globals;
- broad host modules;
- direct host calls;
- replay-based sessions.

No claim of hostile-code isolation or durable semantic safety.

## 12.2 Profile A — Application

Use for scriptable applications and generated hosts.

Adds:

- frozen factory/runtime plan;
- explicit module profile;
- data-only versus host-access split;
- named contexts;
- canonical boundary values;
- API descriptors and generated bindings;
- runtime isolation tests.

## 12.3 Profile C — Contracted invocation

Use for plugins, policy callbacks, compiler passes, and server handlers.

Adds:

- handler contracts;
- schemas and closed decisions;
- invocation capability leases;
- resource budgets;
- activation/link manifest checks;
- task drain and runtime disposition;
- opaque handles and data classifications.

## 12.4 Profile D — Durable orchestration

Use for browser workflows, modal tools, device interactions, jobs, collaborative state, and proof sessions.

Adds:

- defunctionalized continuations;
- revisioned persistence;
- generation pinning and retention;
- event/transcript policy;
- explicit migration;
- replay and duplicate-delivery tests.

## 12.5 Profile K — Kernel-adjacent assurance

Use where guest decisions affect identity, authorization, theorem validity, OS policy, firmware control, compiler trust, or other critical invariants.

Adds:

- effect-only authoritative mutation;
- independent native validation or checker;
- native evidence and secret references;
- deterministic activation across workers;
- separate verification language;
- explicit commit model and receipts;
- minimized trusted computing base;
- process, WASM, privilege, or hardware boundary when scripts are hostile;
- model-checked lifecycle machines where justified.

For a proof assistant, the proof checker should remain smaller than this framework. LangBlocks can orchestrate elaboration and tactics, but validity must reduce to the kernel's independent check.

---

# 13. Concrete Go interfaces

The Go API should use small capability interfaces rather than one universal backend interface.

## 13.1 Compilation

```go
type SourceBundle struct {
    Entry   string
    Files   map[string][]byte
    Options map[string]WireValue
}

type Compiler interface {
    Compile(context.Context, SourceBundle, CompileRequest) (CompiledUnit, Diagnostics)
}

type CompiledUnit interface {
    BackendID() string
    OpaqueExecutable() any // never serialized by the semantic layer
    SourceIdentity() Digest
}
```

Backend-specific executable values remain private to adapter packages.

## 13.2 Definition materialization and linking

```go
type RegistrationSnapshot struct {
    Contract         ProgramContract
    Callbacks        []CallbackDescriptor
    Schemas          []TypeDescriptor
    Surface          []APIDescriptor
    Identities       ArtifactIdentities
}

type Materializer interface {
    Materialize(context.Context, CompiledUnit, RuntimeProfile) (
        RuntimeInstance,
        RegistrationSnapshot,
        error,
    )
}

type Linker interface {
    Verify(expected, actual RegistrationSnapshot) Diagnostics
}
```

## 13.3 Invocation

```go
type RuntimeInstance interface {
    Invoke(context.Context, InvocationRequest) InvocationResult
    Drain(context.Context) error
    Interrupt(error)
    Close(context.Context) error
}

type InvocationRequest struct {
    Handler       HandlerID
    Input         WireValue
    Capabilities  CapabilityLeaseSet
    Handles       HandleSet
    Evidence      EvidenceSet
    Trace         TraceSink
}

type InvocationResult struct {
    Decision     Decision
    Transcript   Transcript
    Metrics      InvocationMetrics
    Disposition  RuntimeDisposition
    Err          error
}
```

No guest value is returned by this interface.

## 13.4 Effects

```go
type EffectInterpreter interface {
    Preflight(context.Context, Decision, TransitionContext) (PreparedPlan, Diagnostics)
    Commit(context.Context, PreparedPlan) (CommitReceipt, error)
}
```

Domains may split preparation and commit across different services.

## 13.5 Continuations

```go
type ContinuationStore interface {
    Create(context.Context, ContinuationEnvelope) (ContinuationHandle, error)
    Load(context.Context, ContinuationHandle) (ContinuationEnvelope, error)
    CompareAndAdvance(context.Context, ContinuationHandle, expectedRevision uint64,
        next ContinuationEnvelope) error
    CompareAndFinish(context.Context, ContinuationHandle, expectedRevision uint64,
        terminal TerminalRecord) error
}
```

## 13.6 Pluggable schemas and codecs

```go
type TypeSystem interface {
    Validate(TypeRef, WireValue) Diagnostics
    Canonicalize(TypeRef, WireValue) (WireValue, Diagnostics)
    CheckFlow(TypeRef, DataSink) Diagnostics
    Compatible(source, destination TypeRef) bool
}
```

Adapters can support JSON Schema, CUE, Protobuf, custom Go validators, proof-term formats, or fixed-layout firmware structures.

---

# 14. Concrete Goja realization

## 14.1 Preserve the existing substrate

The current go-go-goja abstractions should remain foundational:

- `RuntimeFactoryBuilder` composes modules and runtime initializers and freezes them into `RuntimeFactory`;
- `RuntimeFactory.NewRuntime` creates a fresh VM, event loop, runtime owner, lifetime context, runtime services, module registry, and initializers;
- `RuntimeOwner.Call` and `Post` serialize VM access and propagate owner-entry context;
- `Runtime.Close` cancels lifetime resources, drains or interrupts active JavaScript, runs closers, removes bridge services, shuts down the owner, and stops the event loop;
- xgoja providers determine what code is linked into generated hosts, while `RuntimePlan` determines what is exposed at runtime.

The platform kit should sit above these APIs rather than replacing them.

## 14.2 Extract generic Tiny-IDP mechanisms

The following Tiny-IDP mechanisms are good candidates for extraction:

| Tiny-IDP mechanism | Generic package/block |
|---|---|
| `LambdaSpec` | `contract.HandlerContract` |
| program validation and deterministic diagnostics | `contract.Validate`, `diagnostic` |
| canonical program and independent fingerprints | `artifact.Identities` |
| runtime-local collector and callback map | `platformkit/definition` |
| Goja object-identity handles | `platformkit/brand.Registry[T]` |
| input JSON parse and deep freeze | `platformkit/invoke.ValueProjection` |
| required capabilities and call/byte limits | `capability.InvocationScope` |
| pending settlement tracking | `invoke.TaskGroup` |
| Promise await and owner settlement | `platformkit/invoke.PromiseBridge` |
| safe/unsafe worker result | `pool.RuntimeDisposition` |
| pool discard and replacement | `pool.LeaseManager` |
| continuation envelope and revision state | `continuation` |
| generation fingerprints and retention | `generation` |
| outcome/effect validation | `outcome` and `effect` |

Identity-specific effect kinds, fields, actions, challenge types, provider semantics, request digests, browser bindings, and committers remain in Tiny-IDP.

## 14.3 Generic definition collector

A reusable Goja collector can support multiple DSLs:

```go
type Collector[C any] struct {
    Contract   C
    Callbacks  map[CallbackID]goja.Callable
    Brands     brand.Set
    Trace      []RegistrationEvent
}
```

The collector should expose only language-neutral snapshots. Callables remain private and are accessed only inside owner calls.

The collector should support:

- stable callback IDs and source spans;
- duplicate detection;
- callback signatures/contracts;
- branded declaration handles;
- deterministic callback manifests;
- optional registration event traces;
- canonical export agreement;
- domain-provided builder functions.

## 14.4 Generic nominal-brand registry

```go
type Registry[T any] struct {
    values map[*goja.Object]T
}

func (r *Registry[T]) New(vm *goja.Runtime, value T) *goja.Object
func (r *Registry[T]) Resolve(v goja.Value) (T, bool)
```

Variants can create blank objects, frozen method-bearing handles, or revocable invocation handles. The registry owns the nominal type; JavaScript properties do not.

## 14.5 Invocation scope

A reusable `InvocationScope` should own:

- context and cancel function;
- active/revoked state;
- capability bindings;
- task group and pending count;
- resource meter;
- secret/evidence/handle tables;
- trace sink;
- close and drain semantics.

All host functions installed for an invocation close over this scope. A capability call checks activity and budget before doing work. The scope is revoked before the runtime can be returned to the pool.

## 14.6 Value projection

The Tiny-IDP technique of crossing through `JSON.parse` rather than exposing Go host maps is broadly useful for plain-data inputs: it creates ordinary guest objects that can be frozen and prevents reflection-backed host values from leaking mutability or methods.

The generic adapter should support projection modes:

- canonical JSON -> ordinary deep-frozen guest value;
- Protobuf/message descriptor -> explicit wrapper or plain projection;
- opaque native handle -> branded object;
- large binary -> bounded buffer or streaming handle;
- mutable session value -> explicit host-backed wrapper with declared lifetime.

## 14.7 Runtime pool policy

The pool should be policy-driven:

```go
type ReusePolicy interface {
    Classify(InvocationReport) RuntimeDisposition
}
```

Recommended policies:

- `AlwaysFresh` — create and close one runtime per invocation;
- `PositiveProof` — reuse only after valid result and complete drain;
- `ResetAndVerify` — run a domain reset hook and compare a clean-state fingerprint;
- `SessionPinned` — runtime belongs to one explicit session and is never cross-leased;
- `QuarantineForensics` — retain failed runtime metadata or heap diagnostics without returning it to service.

## 14.8 xgoja integration

xgoja should gain optional platform sections rather than absorbing domain semantics:

```yaml
platforms:
  - id: scene-tools
    provider: scene
    contract: scene-tool/v1
    sources: [scene-tool-scripts]
    runtimeProfile: scene-safe
    assuranceProfile: contracted-durable
```

Generated hosts can embed:

- selected provider packages;
- runtime profile;
- source bundles or compiled artifacts;
- generated TypeScript declarations;
- contract and capability documentation;
- conformance command surfaces such as `doctor`, `validate`, `compile`, `inspect-artifact`, and `run-tests`.

Build-time availability, runtime exposure, and invocation binding remain separate.

---

# 15. Domain mappings

## 15.1 Scriptable 3D editor

### Semantic layers

```text
tool DSL
  -> tool contract and state-machine IR
  -> scene-operation IR
  -> renderer/engine-specific commands
```

### Capabilities

- query selection snapshot;
- resolve object or mesh handle;
- raycast against a snapshot;
- query units, snapping, constraints, and asset catalog;
- schedule bounded geometry computation.

### Decisions

- `preview` — typed transient geometry/presentation;
- `awaitInput` — durable/modal continuation;
- `commitOperations` — scene effect plan;
- `cancel`;
- `error`.

### Effects

- create/delete object;
- transform object;
- replace mesh;
- attach material;
- modify scene graph;
- emit undo transaction;
- enqueue render/bake job.

### Important invariants

- scripts never receive raw engine pointers;
- handles include object generation so deleted/reused IDs cannot alias;
- commit plans are validated against the current scene revision;
- preview state is distinct from authoritative scene state;
- modal tools serialize handler label plus typed tool environment;
- operation receipts feed undo/redo and collaboration logs.

## 15.2 Scriptable window manager

### Semantic layers

```text
configuration/rule DSL
  -> normalized rule and keybinding plan
  -> pure layout operations
  -> shell/X11/Wayland effects
```

### Capabilities

- query windows, workspaces, monitors, focus, and typed presentations;
- inspect immutable snapshots rather than mutate internal maps;
- register bounded input or presentation handlers.

### Effects

- focus, move, resize, map, unmap;
- spawn process only under an explicit capability;
- publish menu/presentation;
- mutate the pure layout tree through serializable operations.

### Continuations

- keybinding modes;
- launch/search prompts;
- object accept protocols;
- multi-step placement or selection interactions.

The pure layout model and the shell-side external state should remain separate interpreters.

## 15.3 Scriptable web application

### Semantic layers

```text
route/form/widget DSL
  -> route and interaction IR
  -> handler contracts
  -> HTTP/server target
```

### Capabilities

Request-scoped database queries, authenticated principal projection, cache access, message enqueue, and bounded external service calls.

### Effects

Database mutations, session transitions, outbox messages, redirects, rendered presentation instances, and audit events.

### Durability

Multi-page forms, approval flows, device authorization, and human-in-the-loop operations use explicit continuations pinned to a generation. Hot reload creates new generations rather than silently reinterpreting active workflows.

## 15.4 Embedded firmware

The same patterns apply with different implementations:

- run authoring and normalization on the build host;
- compile to a compact fixed-layout plan or bytecode;
- expose a statically linked capability table for sensors, buses, GPIO, storage, and actuators;
- use integer handles with generation counters;
- meter instructions, stack, memory, calls, and I/O bytes;
- use a cooperative single-owner scheduler;
- persist continuations or event records in checksummed, revisioned flash slots;
- sign artifacts and retain rollback generations;
- make power-loss and partial hardware effects explicit commit models;
- eliminate dynamic module loading in production profiles.

The guest runtime may be part of the device's trusted computing base. This increases the need for small adapters, static profiles, bounded codecs, and independent effect validation.

## 15.5 Scriptable operating system

At OS scale, the pattern becomes an object-capability and message-passing architecture:

- scripts or plugins run in processes, WASM sandboxes, or language domains;
- kernel and service objects are opaque capability handles;
- effects become syscalls or typed IPC requests;
- resource budgets include CPU, memory, descriptors, messages, and device access;
- durable jobs and UI interactions use generation-pinned continuations;
- event journals and projections support restart and desktop reconstruction;
- build-time packages, runtime services, per-process capabilities, and per-request leases form the authority lattice.

The in-process Goja adapter is useful for trusted system components, but hostile extensions require an isolation backend.

## 15.6 Scriptable compiler

### Contracts

A pass declares accepted IR level, produced IR level, analyses required, diagnostics, effects, determinism, and resource budget.

### Opaque handles

AST nodes, symbols, types, source files, and analysis results are native references with generation/revision checks. Raw pointers do not cross the language boundary.

### Decisions

- unchanged;
- rewrite plan;
- diagnostics only;
- request analysis/defer;
- reject compilation;
- internal error.

### Effects

- apply rewrite set atomically to an IR revision;
- emit diagnostic records;
- produce generated artifacts;
- invalidate analyses;
- schedule later passes.

Artifact and callback identities make pass pipelines reproducible. A verifier can independently validate rewritten IR before the compiler accepts it.

## 15.7 Proof assistant or formal-method kernel

This domain exposes the most important trust boundary.

### Guest responsibility

Tactic scripts may search, elaborate, choose lemmas, construct candidate terms, split goals, and propose declarations.

### Kernel responsibility

A small native kernel checks every candidate proof term against the exact environment. The scripting framework cannot insert a theorem merely by returning `success`.

### Contracts

A tactic contract declares goal/input type, allowed capability queries, decision kinds, budgets, and determinism/transcript policy.

### Decisions

- solved with candidate proof term;
- produced subgoals;
- suspended with proof-state continuation;
- inapplicable;
- tactic failure;
- internal error.

### Continuations

Persist goal IDs, metavariable assignments in a kernel-owned format, environment fingerprint, tactic handler label, revision, and opaque references. Never persist a guest closure or unchecked pointer.

### Effect plan

`DeclareTheorem` is a kernel-check commit model:

1. resolve exact environment generation;
2. parse candidate term through a canonical term codec;
3. kernel type-check independently;
4. record theorem and proof receipt only after success.

### Trusted computing base

The proof checker and theorem-store commit path remain in the TCB. The Goja runtime, tactic DSL, search procedures, UI, and most of LangBlocks may be untrusted helpers whose output is checked.

---

# 16. Extraction methodology

A framework of this scope can fail through premature abstraction. Use the following discipline.

## 16.1 Extract invariants, not filenames

Do not copy Tiny-IDP package names and generalize nouns. Identify the invariant first:

- `idpcontinuation` becomes defunctionalized continuation plus generation/revision rules, not a generic browser package;
- `CapabilityBinding` becomes an invocation lease, not a generic map of functions;
- `OutcomeDeny` remains identity-specific while the closed-decision mechanism is generic;
- Goja object pointer maps become the opaque nominal-handle pattern, not the only handle implementation.

## 16.2 Rule of three

Promote a mechanism into the general core when at least three domains demonstrate the same invariant or when a formal correctness argument requires it. Otherwise keep it in an incubating domain package.

The current evidence already supports:

- normalized IR and compiled plans;
- owned runtimes and explicit contexts;
- explicit module/capability profiles;
- stable IDs and registries;
- typed presentations;
- event/artifact boundaries;
- defunctionalized durable state;
- effect interpretation;
- generation and fingerprint identities.

## 16.3 Prove language independence early

After the Goja adapter, implement one deliberately different backend. Starlark is useful for a deterministic, restricted source language; a wazero/WASM adapter is useful for a stronger serialization and isolation boundary. Either will expose accidental assumptions about CommonJS, object identity, Promises, or JavaScript exceptions.

## 16.4 Keep pattern cards versioned

Each pattern evolves independently. A platform manifest pins pattern versions. Breaking semantic changes receive new versions rather than hidden compatibility behavior.

## 16.5 Maintain reference examples

Every core pattern should have:

- a minimal executable example;
- at least one low-assurance and one high-assurance example where applicable;
- backend conformance vectors;
- domain tests;
- an anti-example demonstrating the failure it prevents.

---

# 17. Implementation sequence

## Phase 1 — Vocabulary and conformance skeleton

- establish LangBlocks glossary, pattern-card schema, diagnostic namespace, and lifecycle models;
- create a cross-project pattern matrix for Tiny-IDP, go-go-goja, Widget DSL/DMETA, researchctl, and one additional non-Goja system;
- specify canonical `WireValue`, handler contracts, artifact identities, runtime disposition, and continuation envelope;
- write backend-independent conformance vectors before moving code.

## Phase 2 — Extract the semantic kernel

Move or reimplement language-neutral mechanisms in go-go-langkit:

- contracts and deterministic diagnostics;
- canonical artifact identities;
- callback manifests and link checks;
- outcome/effect registries;
- continuation and generation types;
- resource and data-flow policies.

Tiny-IDP remains behaviorally unchanged during this phase.

## Phase 3 — Build the Goja adapter

- implement generic definition collector and branded handle registry;
- implement canonical value projection and deep freeze;
- implement invocation scope, capability leases, task drain, Promise bridge, and disposition report;
- implement artifact materialization and deterministic link verification;
- implement reusable pool policies above `engine.Runtime`;
- integrate module/API descriptors and generated TypeScript surfaces.

## Phase 4 — Rebase Tiny-IDP onto the extracted blocks

Tiny-IDP becomes the high-assurance reference consumer. Preserve its domain contracts and tests while replacing generic implementation pieces. Any abstraction that makes the Tiny-IDP invariants weaker is rejected.

## Phase 5 — Add contrasting consumers

Use at least two:

- Widget DSL or a small presentation compiler to exercise layered IR and target lowering;
- researchctl or a miniature deterministic simulator to exercise plans, event streams, manifests, and evidence import;
- a scene-editor tool demo or compiler-pass demo to exercise opaque handles and transactional effect plans.

## Phase 6 — Add a second language backend

Implement Starlark or WASM. Run the same contract, capability, effect, continuation, and conformance vectors. Refactor any Goja leakage discovered.

## Phase 7 — Formal assurance package

- model runtime lease, capability lease, continuation, and effect-commit state machines;
- add property-based and model-derived tests;
- define transcript and determinism contracts;
- add threat-model templates and trusted-computing-base inventories;
- demonstrate a kernel-check effect with a small verifier example.

---

# 18. Recommended first concrete slice

The initial implementation should remain narrow enough to finish and strong enough to prove the architecture.

Build these blocks first:

1. `contract.HandlerContract` and `ProgramContract`;
2. `value.WireValue` with canonical JSON codec;
3. deterministic diagnostics;
4. artifact identities and callback manifests;
5. Goja definition collector and activation linker;
6. Goja invocation scope with capability leases and task drain;
7. closed decisions and effect-plan validation;
8. positive-proof runtime pool policy;
9. backend-independent conformance tests.

Defer generic continuations, event sourcing, presentation IR, and formal models until the first slice successfully hosts Tiny-IDP handlers and one small non-identity example. Then add continuation and generation blocks using Tiny-IDP as the reference.

A useful minimal non-identity example is a scene graph with three operations:

- query selected object through a capability;
- return a `commitOperations` decision containing a typed transform effect;
- validate and apply it to a revisioned in-memory scene.

This exercises the semantic firewall, callback linking, capability lease, opaque handle, closed decision, effect interpreter, budget, runtime disposition, and deterministic artifact identity without requiring a full editor.

---

# 19. Major risks and design cautions

## 19.1 Lowest-common-denominator abstraction

A universal backend interface can erase useful language differences. Prefer small interfaces and optional capability traits. A backend that has no async feature should not implement fake Promise methods.

## 19.2 Goja leakage

CommonJS, `goja.Object` identity, Promise polling, and event-loop ownership are backend implementations, not general semantics. The second backend is the primary defense.

## 19.3 Schema overreach

Tiny-IDP's small schema language is appropriate for bounded identity values but insufficient as the universal type system. Use a pluggable type/codec interface.

## 19.4 False determinism

Deterministic registration does not imply deterministic callbacks. No-JIT execution does not imply determinism. Clocks, randomness, capability answers, floating point, scheduling, external state, and backend versions must be explicit.

## 19.5 False atomicity

A plan containing external network, email, filesystem, GPU, device, or IPC operations is not made atomic by naming it a transaction. Commit models and receipts must be honest.

## 19.6 Continuation retention

Generation pinning requires artifact retention, revocation policy, storage cleanup, migration tooling, and operational visibility. It is not only a record format.

## 19.7 Runtime global contamination

A pooled runtime can retain module globals even after a clean invocation. Profiles must declare whether runtime globals are allowed, reset, session-pinned, or prohibited. Positive settlement proves asynchronous cleanliness, not semantic statelessness.

## 19.8 Trusted computing base inflation

For proof kernels, authorization kernels, firmware, or OS policy, the framework must remain outside the final checker where possible. More abstractions do not automatically mean more assurance.

## 19.9 Pattern bureaucracy

Machine-readable patterns are useful only when they generate diagnostics, tests, scaffolds, or threat-model checklists. Avoid a catalog that becomes architecture-themed documentation with no executable consequence.

---

# 20. The resulting thesis

The most reusable abstraction is not “embed JavaScript safely.” It is:

> **Compile human intent into a stable semantic contract; instantiate language runtimes under explicit profiles; lease bounded authority to named computations; require typed decisions rather than ambient mutation; interpret effects in a native kernel; represent long-lived control as versioned data; and make every transition inspectable, replayable, or independently checkable according to an explicit assurance profile.**

Tiny-IDP demonstrates the contracted, durable, kernel-adjacent end. go-go-goja supplies the runtime-owner and generated-host machinery. Widget DSL and DMETA demonstrate layered semantic lowering and target ownership. researchctl demonstrates explicit execution artifacts and evidence promotion. Together they are sufficient to define a general construction discipline, provided the framework preserves domain kernels and does not turn their differences into a premature universal language.

---

# 21. Source map

Primary source links:

- [Tiny-IDP branch snapshot](https://github.com/go-go-golems/tiny-idp/tree/d164ae59408bdd8bc21516274b446339b1761b1e)
- [Tiny-IDP handler contract](https://github.com/go-go-golems/tiny-idp/blob/d164ae59408bdd8bc21516274b446339b1761b1e/pkg/idpprogram/lambda.go)
- [Tiny-IDP outcomes and effect plans](https://github.com/go-go-golems/tiny-idp/blob/d164ae59408bdd8bc21516274b446339b1761b1e/pkg/idpprogram/outcomes.go)
- [Tiny-IDP canonical identities](https://github.com/go-go-golems/tiny-idp/blob/d164ae59408bdd8bc21516274b446339b1761b1e/pkg/idpprogram/canonical.go)
- [Tiny-IDP continuation envelope](https://github.com/go-go-golems/tiny-idp/blob/d164ae59408bdd8bc21516274b446339b1761b1e/pkg/idpcontinuation/types.go)
- [Tiny-IDP runtime materialization](https://github.com/go-go-golems/tiny-idp/blob/d164ae59408bdd8bc21516274b446339b1761b1e/pkg/idpscript/runtime_factory.go)
- [Tiny-IDP invocation and Promise handling](https://github.com/go-go-golems/tiny-idp/blob/d164ae59408bdd8bc21516274b446339b1761b1e/pkg/idpscript/invoke.go)
- [Tiny-IDP capability leases](https://github.com/go-go-golems/tiny-idp/blob/d164ae59408bdd8bc21516274b446339b1761b1e/pkg/idpscript/capabilities.go)
- [Tiny-IDP worker pool](https://github.com/go-go-golems/tiny-idp/blob/d164ae59408bdd8bc21516274b446339b1761b1e/pkg/idpscript/pool.go)
- [Tiny-IDP Goja collector and nominal handles](https://github.com/go-go-golems/tiny-idp/blob/d164ae59408bdd8bc21516274b446339b1761b1e/internal/gojamodules/tinyidp/module.go)
- [go-go-goja runtime factory](https://github.com/go-go-golems/go-go-goja/blob/ae413f594d0ed4e36123ac925e195666e0f0e759/pkg/engine/factory.go)
- [go-go-goja runtime lifecycle](https://github.com/go-go-golems/go-go-goja/blob/ae413f594d0ed4e36123ac925e195666e0f0e759/pkg/engine/runtime.go)
- [go-go-goja runtime owner](https://github.com/go-go-golems/go-go-goja/blob/ae413f594d0ed4e36123ac925e195666e0f0e759/pkg/runtimeowner/runner.go)
- [xgoja overview](https://github.com/go-go-golems/go-go-goja/blob/ae413f594d0ed4e36123ac925e195666e0f0e759/cmd/xgoja/doc/01-overview.md)
- [xgoja runtime plan](https://github.com/go-go-golems/go-go-goja/blob/ae413f594d0ed4e36123ac925e195666e0f0e759/pkg/xgoja/app/runtime_plan.go)
- [PARC go-go-goja project map](https://github.com/go-go-golems/go-go-parc/blob/e0536cacd7626432c8ad78901543f3a77dee6033/Research/KB/Projects/go-go-goja.md)
- [PARC Widget DSL project map](https://github.com/go-go-golems/go-go-parc/blob/e0536cacd7626432c8ad78901543f3a77dee6033/Research/KB/Projects/widget-dsl.md)
- [PARC researchctl project map](https://github.com/go-go-golems/go-go-parc/blob/e0536cacd7626432c8ad78901543f3a77dee6033/Research/KB/Projects/researchctl.md)
- [PARC DSL to normalized config to compiled plan](https://github.com/go-go-golems/go-go-parc/blob/e0536cacd7626432c8ad78901543f3a77dee6033/Research/KB/Tribal/dsl-normalized-config-compiled-plan.md)
- [PARC runtime ownership and context propagation](https://github.com/go-go-golems/go-go-parc/blob/e0536cacd7626432c8ad78901543f3a77dee6033/Research/KB/Tribal/goja-runtime-ownership-and-context-propagation.md)
- [PARC DMETA compiler pipeline](https://github.com/go-go-golems/go-go-parc/blob/e0536cacd7626432c8ad78901543f3a77dee6033/Research/KB/Tribal/dmeta-design-system-compiler-pipeline.md)
- [PARC typed widget instance streaming](https://github.com/go-go-golems/go-go-parc/blob/e0536cacd7626432c8ad78901543f3a77dee6033/Research/KB/Tribal/typed-widget-instance-streaming-for-chat-overlays.md)

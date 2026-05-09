# Persistent Multi-Cell JavaScript REPLs with goja: Deep Research on Session Models, IIFEs, Jupyter Protocol, Embedded Engines, and Scope Simulation

## Persistent session models through history

A “persistent REPL session” is fundamentally a commitment to *continuity of program state across many evaluations*: name bindings, heap objects reachable from those bindings, and often also “meta-state” such as loaded code, tooling objects, and debugging context. Different systems solved the continuity problem by choosing different *state containers* (an image file, a long-lived interpreter process, or a browser execution context) and by defining different *reset and checkpoint* semantics. citeturn14search0turn4search5turn11search3

**Smalltalk’s “image” lineage treats state as the system.** In classic Smalltalk systems, the environment is designed around a live object memory that can be snapshotted and resumed. In the modern Smalltalk family (e.g., Squeak-derived systems), the virtual machine runs an **image file** that is described explicitly as a snapshot of a live session; a companion **changes file** records source-level changes (and a sources file can hold base-system sources). This model makes “keep state between evaluations” nearly trivial: every evaluation mutates the same live object graph, and persistence is achieved by periodically writing an image snapshot. citeturn4search5turn4search6

GNU Smalltalk documents this snapshot concept in very direct operational terms: after creating/restoring the environment, the system “takes a snapshot of the new memory image,” saving it over the previous image file (or to the current directory), and also exposes snapshotting as an explicit operation (e.g., `ObjectMemory snapshot`). citeturn4search2turn4search6

Historically, Smalltalk was also explicitly conceived as an integrated interactive programming environment, not “just” a language runtime. citeturn20search0 That matters for REPL design: the “persistent session” is not an add-on feature, it is the *default substrate* on which tools (inspectors, browsers, debuggers) operate.

**Process-based kernels treat state as the memory of a long-lived interpreter service.** Jupyter’s design (building on IPython’s networked execution model) is that a kernel is a long-running process providing “execute this code” services; state persists because that process persists. The Project Jupyter architecture documentation emphasizes that multiple frontends can attach to the *same kernel process* and “will have access to the same variables,” explicitly making the persistent heap and bindings the shared resource. citeturn14search0

This design has a characteristic operational “reset”: you **restart the kernel** to clear state. It also has the characteristic notebook hazard of “stale state” when execution order differs from notebook order—one reason `execution_count` and explicit state indicators matter. citeturn6search5turn14search0

**Browser DevTools consoles treat state as an execution context (realm and scope chain) attached to a running page.** In the Firefox Web Console documentation, the rule is stated almost as a guarantee: “Code that you have executed becomes part of the execution context,” meaning later evaluations can use earlier definitions regardless of whether they were entered in a single-line prompt or a multi-line editor. citeturn11search3

Chrome’s ecosystem exposes the same concept in more protocol-level terms: the Chrome DevTools Protocol `Runtime.evaluate` explicitly takes an `executionContextId`, and if omitted evaluation “will be performed in the context of the inspected page.” This makes the persistence model concrete: state is tied to the lifetime of that execution context (and thus to navigation/reload boundaries, frame selection, etc.). citeturn11search23

DevTools also draw a sharp line between *persisting state* vs *persisting logs/UI artifacts*. For example, Chrome and Edge document “Preserve log” for console messages across navigations (a UI/logging persistence), while separately noting that many kinds of in-DevTools edits disappear on reload unless using overrides/workspaces (a tooling persistence). This distinction is relevant to a notebook-like JS REPL: “persistent session state” (bindings/heap) and “persistent UI history” (cells, outputs, logs) are separable design axes. citeturn2search0turn11search28

**Related “image-like” ancestry in Lisp/Emacs reinforces the design space.** GNU Emacs historically used “dumping” to preload Lisp libraries into a dumped state to speed startup, and modern Emacs documents “portable dump” files—another instance of snapshotting a live managed heap as the persistence mechanism. While not a JS REPL solution directly, it reinforces that “dump an initialized runtime snapshot” is a recurring strategy when startup cost or initialization ordering matters. citeturn4search11

## IIFEs as scope control, module boundaries, and REPL cell wrappers

The **Immediately-Invoked Function Expression** (IIFE) became a standard JavaScript idiom for creating a fresh scope immediately, largely as a response to pre-ES6 scoping limitations (where only functions create scope for `var`) and to the need for modular encapsulation in a language that originally lacked standardized modules. citeturn7search8turn7search12

**Origin and terminology.** The term “IIFE” is strongly associated with entity["people","Ben Alman","javascript developer"]’s 2010 post arguing for “Immediately-Invoked Function Expression” as a clearer name than “self-executing anonymous function,” including examples of the canonical `(function(){ ... }())` / `(function(){ ... })()` forms. citeturn7search8turn7search12

**Crockford, closures, and pre-ES6 “module pattern” isolation.** A major reason IIFEs became culturally important is that they enable closure-based privacy: variables defined inside an IIFE are not reachable by name from outside, but can be referenced by returned functions/objects. entity["people","Douglas Crockford","javascript author"]’s discussion of private members demonstrates this closure-based information hiding as a JavaScript-native pattern, and it sits historically alongside “module pattern” approaches used before ES modules. citeturn7search5

At the ecosystem level, the CommonJS Modules specification explicitly frames modules as providing “privacy of their top scope” plus explicit import/export mechanisms. That “top-scope privacy” is conceptually the same boundary an IIFE provides—one reason IIFEs and module patterns interlock historically. citeturn7search2

**Async IIFEs as “top-level await simulation.”** Before top-level `await` existed (and still today in non-module contexts), developers commonly wrap code in an async function—often an async IIFE—so that `await` is syntactically legal and can be used in what feels like “top-level” code. MDN documents the pattern explicitly: an “async IIFE allows you to use await … in contexts where top-level await is not available.” citeturn21search8turn21search9

This pattern also shows up in REPL design discussions: the historical need to support “await at the top” in interactive shells led to implementations that wrap each user input in an async function and await its completion before printing. For example, TypeScript-oriented REPLs discussed precisely this strategy—wrapping in an async IIFE—years before top-level await became widely standardized. citeturn21search6

Top-level await itself became part of the ECMAScript standard in ES2022 (13th edition), where it is defined as a module-level capability (modules “act as big async functions,” delaying dependents until completion). citeturn21search16turn21search1

Node’s REPL is a particularly relevant reference point because it is an interactive multi-evaluation environment that *explicitly* supports top-level `await` and documents the tradeoffs: “Support for the `await` keyword is enabled at the top level,” and Node warns of a limitation that using top-level await in the REPL can “invalidate the lexical scoping” of `const`/`let` in that interactive context. That warning is a concrete example of the semantic edge cases that appear when you retrofit notebook-style evaluation onto JS’s lexical environment rules. citeturn21search3

**IIFEs as REPL cell wrappers with explicit “exports.”** For a notebook-like JS REPL, an IIFE wrapper can serve two simultaneous design goals:

1. isolate *temporary* cell-local variables so they don’t leak into the long-lived global object, and  
2. explicitly export a chosen subset of bindings (or a “cell namespace”) by returning an object.

This mirrors patterns from “revealing module” approaches, where the return object is the public surface and everything else remains private inside the closure. citeturn7search32

However, the wrapper/export approach has unavoidable consequences tied to the ECMAScript execution model: lexical declarations (`let`/`const`/`class`) create bindings in declarative (lexical) environment records, not as properties on an object. That makes “automatic capture” of all bindings fundamentally non-trivial without either (a) rewriting user code, or (b) requiring explicit export syntax, because the language does not offer a built-in reflection mechanism to enumerate lexical environment bindings like object properties. citeturn9search2turn9search6turn9search10

## Jupyter messaging protocol ideas transferable to a REST-based JS REPL

Jupyter’s protocol is often described at two levels: (1) a message *semantics model* (execute requests, outputs, status, correlation IDs), and (2) a *transport and framing model* historically built on ØMQ multipart messages. Both levels contain transferable ideas, even if your JS REPL backend is exposed via HTTP/REST rather than raw ZMQ sockets. citeturn14search31turn6search13turn6search6

image_group{"layout":"carousel","aspect_ratio":"16:9","query":["Jupyter kernel architecture diagram shell iopub stdin control heartbeat","Jupyter messaging protocol <IDS|MSG> delimiter diagram","ZeroMQ multipart message frames diagram","Jupyter notebook kernel frontend architecture diagram"],"num_per_query":1}

**Kernel-as-a-service, shared state, and multi-frontend concurrency.** Jupyter’s architecture formalizes the “persistent session” as the kernel process: it’s explicitly designed so that more than one frontend may connect and share the same variables/state. This is not just a transport detail; it’s a semantic commitment that influences identity, message routing, and “who owns the session.” citeturn14search0turn6search13

**Message envelopes and correlation metadata.** The protocol standardizes message fields such as:

- a `header` containing identifiers (including message id and session id),
- a `parent_header` that lets asynchronous outputs be attributed back to the request that triggered them,
- `metadata` and `content` dicts that hold payloads.

This separation is documented in protocol references and is part of why outputs can be streamed and later associated with a particular cell execution. citeturn2search3turn6search13

Even if you move from ZMQ to REST, the core idea translates cleanly: every evaluation should have a stable **request id**; every produced side effect (stdout chunk, console log, display object, error) should carry that request id (or parent id) to support correct attribution in the UI. This becomes especially important once you add concurrency (multiple clients, multiple inflight requests, cancellations). citeturn6search13turn2search3

**ZeroMQ wire framing is specific, but the “multipart + signature + delimiting” pattern is instructive.** The Jupyter messaging spec builds on multipart messages: a routing prefix (0+ identities), a delimiter `<IDS|MSG>`, then an HMAC signature, then multiple serialized dict frames in a fixed order (header, parent_header, metadata, content). citeturn6search13turn2search3turn6search23

In REST, you likely won’t reproduce this exact framing. But the transferable architectural ideas are:

- separate **routing** info from **payload** (ZMQ identities vs REST path + auth),
- separate **authentication/integrity** (HMAC signature) from the payload itself,
- treat messages as **composable frames** (which maps to structured JSON objects, or to WebSocket frames with a channel + payload field). citeturn6search13turn2search39turn6search23

**Channels as a concurrency architecture: request/reply vs broadcast side effects.** Jupyter’s protocol distinguishes a request/reply path (shell) from a broadcast path for side effects (IOPub), plus stdin for interactive input, plus a control channel intended for out-of-band control like interrupts/shutdown, plus heartbeat for liveness checks. citeturn14search3turn14search6turn14search16

The REST-friendly translation is *not* “five sockets,” but rather “five roles”:

- **Execution RPC** (`POST /sessions/{id}/execute`) returns an immediate acknowledgement with `request_id`.
- **Event stream** (WebSocket or SSE, `GET /sessions/{id}/events`) carries stdout/stderr, rich display payloads, and status transitions keyed by `request_id`.
- **Input requests** can be modeled as server-sent prompts that the client answers via another REST call (`POST /sessions/{id}/input`).
- **Control operations** (`POST /sessions/{id}/interrupt`, `/shutdown`) should be handled out-of-band so they aren’t blocked behind long-running evaluations—mirroring the protocol’s recommendation to run the control channel separately for responsiveness. citeturn14search16turn14search6
- **Liveness/health** can be heartbeat-like pings or a `/health` endpoint, but the key lesson is that the UI needs a fast way to distinguish “kernel is busy” from “kernel is dead/unreachable.” citeturn14search6turn14search3

**`execution_count` as an explicit model of temporal ordering.** In IPython/Jupyter messaging, the kernel maintains a monotonically increasing execution counter (for `store_history=True` executions), and returns it in `execute_reply` (and related messages) as `execution_count`. This supports UI affordances like `In [42]` and provides a concrete mechanism to reason about execution chronology even when cells are executed out of notebook order. citeturn6search5turn14search0

A REST-based JS REPL can borrow this directly: per session, keep an `execution_count` that increments on accepted executions and is included in the acknowledgement and in any subsequent streamed events. This is not merely cosmetic; it becomes part of the user’s mental model for “what state is current,” exactly because notebook-like systems permit non-linear runs. citeturn6search5turn14search0

**Jupyter-over-WebSocket as an existence proof for transport adaptation.** Jupyter Server documents WebSocket wire protocols that wrap Jupyter messages (including channel and message dicts) over a single WebSocket connection. This is directly relevant if your architecture is “REST for control + WebSocket for events,” because it demonstrates one mature approach to multiplexing channels in a browser-friendly transport while preserving correlation metadata. citeturn2search39

## Embedded JavaScript engines for a Go-backed REPL

Your choice of embedded engine sets the hard constraints for “persistence” semantics, concurrency, module loading, and the degree to which you can mirror browser/Node behavior. Comparing goja (pure Go) with QuickJS and Duktape (C engines) is best done along four axes: (a) runtime/state model, (b) evaluation APIs, (c) module loading model, and (d) thread/concurrency constraints. citeturn22view1turn13search8turn13search16turn12search3

**goja (pure Go) emphasizes ES5.1 compliance and Go integration.** goja describes itself as an ECMAScript 5.1(+) implementation in pure Go, with a design goal of standard compliance and performance, and it provides the canonical embedding pattern: create a runtime and call `RunString` to evaluate code. citeturn12search0turn22view1

For a persistent session model, the key point is that a single `Runtime` instance naturally holds onto state across many `RunString` calls because it is a long-lived VM object. The concurrency constraint is explicit and central: “An instance of goja.Runtime can only be used by a single goroutine at a time,” and JS values cannot be passed between runtimes. This pushes REPL/server designs toward *per-session single-threaded execution*, typically by funneling all evaluation through one goroutine or by guarding with a mutex and ensuring no concurrent entry. citeturn22view1

goja also stresses that common “platform features” like `setTimeout` are not part of ECMAScript proper and must be provided by the host, and it points to node-compatibility support as a separate project. This matters for notebook-like JS REPLs because asynchronous cell execution is usually an event-loop question as much as a language question. citeturn22view1turn12search4

On module loading, goja proper is not an ES module engine; the common route is to use **goja_nodejs**, which provides a Node.js compatibility layer and a `require` implementation via a `Registry` that can be shared across runtimes. citeturn12search4turn12search1 The `require` package also documents global native-module registration and warns about concurrency around module registration versus concurrent `require()` calls, another practical constraint for a multi-session server. citeturn12search5turn12search1

**QuickJS (C) models “runtime” and “context/realm” similarly to web engines and supports ES modules.** QuickJS’s embedding API distinguishes `JSRuntime` (object heap) from `JSContext` (realm/global environment). The developer guide explicitly notes that multiple contexts can exist per runtime and “can share objects, similar to frames of the same origin sharing JavaScript objects in a web browser,” which is conceptually aligned with browser DevTools “execution contexts.” citeturn13search8

QuickJS evaluation is done via `JS_Eval()`, and module evaluation is a first-class concept (script vs module). It also supports custom module loaders (`JS_SetModuleLoaderFunc`), which is important if you want notebook cells to import modules from a virtual filesystem, database, or user workspace. citeturn13search8turn12search2

Concurrency constraints are also explicit in QuickJS documentation: within a single `JSRuntime`, “no multi-threading is supported.” In practice, this is the same shape as goja’s goroutine rule and implies the same architectural pattern: serialize all interaction with a given runtime. citeturn13search8

**Duktape (C) optimizes for portability/compactness and offers optional module frameworks.** Duktape’s guide describes a `duk_context *` as the primary API handle: an ECMAScript “thread of execution” inside a Duktape heap, with contexts associated with global objects/environments and an API that manipulates values through a value stack. It explicitly states the multi-threading restriction: “only one native thread can execute any code within a single heap at any time,” and Duktape’s threading documentation reinforces that there are no internal concurrency protection mechanisms—concurrent access to a heap is unsafe. citeturn13search1turn13search16turn13search4

Duktape’s module story is intentionally modular: the older built-in module framework (1.x) was moved into extras in 2.x, and multiple alternatives exist (including a Node.js-semantics loader in extras). This makes Duktape viable for embedded REPL workloads, but also means you, as host, must choose and integrate the loader semantics you want. citeturn12search3turn12search24turn12search7

**Comparative implications for a persistent multi-cell JS REPL.** Across all three engines, “persistent state” is naturally achieved simply by reusing the same runtime/context object across evaluations; the harder problems are (1) isolation boundaries (per session? per user? per notebook?), (2) concurrency/interruptibility, and (3) module and async semantics that match user expectations from Node/DevTools/Jupyter.

The concurrency constraint convergence is notable: goja is single-goroutine per runtime, QuickJS is single-thread per runtime, and Duktape is single-native-thread per heap. That shared shape makes the “kernel-per-session with an event loop / serialized dispatcher” architecture more like a necessity than a design preference if you want correctness. citeturn22view1turn13search8turn13search16turn13search1

## `with` and Proxy scope simulation: why it exists, why it’s discouraged, and why `let`/`const` break the illusion

### Why `with` was used in REPL-like designs

The `with` statement exists to inject an object into the front of the scope chain for the duration of a statement: MDN summarizes it as adding “the given object to the head of this scope chain,” where unqualified identifier lookups consult that object first. citeturn8search3 From a REPL designer’s perspective, this is tempting: you can treat a plain object as a “variable environment” and run user code “inside” it, effectively implementing a scope overlay.

When paired with `Proxy`, the illusion becomes more powerful: because identifier lookup inside `with` depends on property existence checks, a Proxy can trap those checks (notably the `has` operation) to implement custom lookup rules such as “every name exists” or “names exist if present in a backing map.” Real-world discussions of “Proxies and with statements” point out that you must implement `has` behavior for the proxy to satisfy the way `with` performs name resolution. citeturn10search7turn9search23

### Why `with` is discouraged and “deprecated” language status is nuanced

ECMAScript has long treated `with` as problematic for optimization and readability: its presence makes lexical resolution dynamic, preventing compilers from making many static assumptions. MDN lists performance and readability issues and emphasizes that `with` is forbidden in strict mode. citeturn8search3turn8search10

The specification itself encodes that strict-mode prohibition as an early error: in the “Statements and Declarations” chapter, `WithStatement` is a syntax error if `IsStrict` is true. citeturn8search2

The “deprecated” label is partially a documentation convention rather than a spec removal plan. MDN’s statements index labels `with` as “Deprecated.” citeturn8search24 But there has also been explicit discussion that such labeling can be misleading because `with` remains in the language (in non-strict code) for web compatibility; MDN’s browser-compat-data issue tracker reflects this nuance (“feature is not allowed in strict mode … allowed in sloppy mode … highly discouraged”). citeturn8search26

It’s also important to correct a common citation confusion: **ECMA-262 Annex B.3.5 is not “the with statement.”** In current TC39-published spec structure, Annex B.3.5 is “Initializers in ForIn Statement Heads,” while `WithStatement` is in the main statement chapter, with its early-error rules referencing legacy extensions in Annex B only indirectly (e.g., labelled function declaration legacy rules). citeturn8search2turn8search4turn8search9

### The spec-level mechanism: Object Environment Records vs Declarative Environment Records

To understand why Proxy-based scope simulation fails for `let`/`const`, you have to use the spec’s environment record model:

- A `with` statement conceptually introduces an **Object Environment Record**; TC39’s execution context model explicitly says Object Environment Records define the effect of constructs like `WithStatement` that associate identifier bindings with object properties. citeturn8search13turn1search39  
- A `let` or `const` declaration creates bindings in a **Declarative Environment Record**, associated with the running execution context’s `LexicalEnvironment`. TC39 states directly that `let` and `const` are scoped to the running execution context’s LexicalEnvironment. citeturn9search2turn9search4

The critical algorithmic bridge is `HasBinding` for Object Environment Records: the spec defines `HasBinding(N)` as determining whether the binding object has a property named `N`. In other words, name resolution inside `with` is property-based. citeturn9search4turn9search12 This is also exactly why a Proxy can influence `with` lookup—because property existence checks are proxy-trappable operations in JavaScript semantics. citeturn9search4turn9search23

### Why `let`/`const` bindings are fundamentally invisible to Proxy-backed `with` scopes

Because `let`/`const` create declarative (lexical) bindings, not properties, they do not participate in the object-property lookup that an Object Environment Record performs, and therefore they do not become visible “through” a Proxy-backed object used in a `with` statement. This is not an implementation quirk; it follows from the environment record type hierarchy and the fact that `with` operates via an Object Environment Record while `let`/`const` operate via declarative records. citeturn8search13turn9search2turn9search4

A closely related (and widely observed) manifestation of the same rule is that top-level `let`/`const` do not become properties of the global object in browsers, unlike `var` in classic scripts. Exploring JS summarizes this in terms of the global environment record split: top-level `let`/`const` create bindings in the *declarative* record, while `var`/function create bindings in the *object* record. citeturn9search10turn9search6

### Consequences for a multi-cell JS REPL design

For a notebook-like JS REPL, this environment model produces a “hard wall”:

- If you rely on `with (proxy)` to simulate a mutable scope object that collects variables, you can capture *property-backed* name resolution paths, but you cannot “see” new lexical declarations created by `let`/`const`/`class` without transforming code or changing the evaluation strategy. citeturn9search2turn9search4turn8search3  
- If you avoid `with` and evaluate cells at the top level of a shared runtime, you can get closer to DevTools/Node semantics where lexical bindings persist in the runtime’s lexical environment across evaluations—yet those bindings are still not simply enumerable as object properties, and redeclaration rules will behave like real JavaScript (e.g., repeated `let x` is a syntax error). Node’s REPL documentation illustrates that even “top-level await enabled” interactive evaluation has to contend with lexical scoping edge cases. citeturn21search3turn9search6turn9search10  
- If you use an IIFE wrapper and a “return object” export mechanism, you can make persistence explicit and controllable, but you are choosing a semantics that differs from DevTools/Jupyter in important ways: you are no longer in a single shared lexical top-level; you are in per-cell function scope unless you re-inject exports and/or rewrite future cells to import them. This is the same closure/export boundary logic that makes module patterns work. citeturn7search32turn7search5turn7search8

For goja-backed systems specifically, the spec-level constraints interact with host constraints: because goja requires serialized access per runtime, any design that tries to “simulate scope” by running multiple evaluations concurrently against one runtime is not just semantically hard—it is also unsafe at the embedding level. That tends to align best with a kernel-like model: per session runtime, sequential evaluation, explicit ids/counts, and an event stream for outputs. citeturn22view1turn14search0turn14search3
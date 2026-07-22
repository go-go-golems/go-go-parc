# JavaScript Interpreter Instrumentation

- URL: https://chatgpt.com/c/6a5e07e5-6d60-83ea-b12f-ffad59327cdd
- Created: 2026-07-20T11:35:02.012Z

---

> I want to add something like ebpf but to a JavaScript interpreter (goja for go, see also GitHub.com/go-go-golems/go-go-goja ), so that one can instrument not just the interpreter but do things like inject hooks into function calls or returns that can then assert invariant on state and such, for metrics and performance but also runtime and static analysis, proof stuff.

```json
{"search_query":[{"q":"github dop251 goja interpreter source VM function call opcode hooks"},{"q":"github go-go-golems go-go-goja"},{"q":"Linux kernel eBPF verifier documentation BPF trampoline fentry fexit"},{"q":"goja parser compiler Program RunProgram source github"}],"response_length":"long"}
```

I’ll inspect goja and go-go-goja’s execution hooks, then outline a concrete jBPF-style probe runtime, verifier, safety model, hook semantics, and incremental implementation path.

<details><summary>💭 Thinking</summary>

**Searched multiple sources for Goja repo and eBPF docs**

</details>

```unknown
bash -lc rm -rf /tmp/goja /tmp/go-go-goja && git clone --depth 1 https://github.com/dop251/goja.git /tmp/goja && git clone --depth 1 https://github.com/go-go-golems/go-go-goja.git /tmp/go-go-goja && printf 'goja %s\ngo-go-goja %s\n' "$(git -C /tmp/goja rev-parse HEAD)" "$(git -C /tmp/go-go-goja rev-parse HEAD)"
```

<details><summary>💭 Thinking</summary>

**Cloned GitHub repositories for inspection**

**Searched Goja VM details and fetched relevant file portions**

</details>

```json
{"find":[{"ref_id":"turn846934search18","pattern":"type instruction"},{"ref_id":"turn846934search18","pattern":"func (vm *vm) run"},{"ref_id":"turn846934search18","pattern":"type Program struct"},{"ref_id":"turn846934search18","pattern":"callStack"}],"response_length":"medium"}
```

<details><summary>💭 Thinking</summary>

**Searched the web and github.com**

**Inspected repo structure and fetched engine data**

**Designing JavaScript Probing**

I’m thinking about how to approach JavaScript instrumentation and runtime analysis, drawing parallels to eBPF. I'll explore existing systems like DTrace, OpenTelemetry, and dynamic instrumentation for clues.

**Designed JavaScript Probing**

</details>

```json
{"find":[{"ref_id":"turn846934search18","pattern":"type call "},{"ref_id":"turn846934search18","pattern":"type _ret"},{"ref_id":"turn846934search18","pattern":"func (ret"},{"ref_id":"turn846934search18","pattern":"vmCall(vm"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched the web and github.com**

**Located vmCall(vm) instructions in GitHub repo**

</details>

```json
{"find":[{"ref_id":"turn846934search18","pattern":"vmCall"},{"ref_id":"turn846934search18","pattern":"assertCallable"},{"ref_id":"turn846934search18","pattern":"popCtx()"},{"ref_id":"turn846934search18","pattern":"vm.result"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched the web and GitHub**

**Fetched specific lines from a GitHub file**

**Fetched file content for analysis and executed instructions**

</details>

```json
{"click":[{"ref_id":"turn110910view2","id":74}],"response_length":"short"}
```

<details><summary>💭 Thinking</summary>

**Searched the web and GitHub multiple times**

**Fetched code snippet and file content from GitHub repository**

</details>

```json
{"search_query":[{"q":"site:github.com/dop251/goja/blob/master/compiler.go \"type Program struct\""},{"q":"site:github.com/dop251/goja/blob/master/compiler.go \"funcName\" \"srcMap\""},{"q":"site:github.com/dop251/goja/blob/master/compiler.go \"code []instruction\""}],"response_length":"long"}
```

Goja’s central bytecode loop and explicit call/return transitions provide precise attachment points, including native, async, and generator paths. Probes should target stable semantic events, remain read-mostly, and require explicit mutation privileges.

<details><summary>💭 Thinking</summary>

**Searched GitHub and Gist for Program struct and metadata**

**Fetched file content from GitHub repository**

**Clarifying eBPF-inspired probe design**

I’m thinking of proposing an eBPF-inspired probe system for JavaScript. I'll clarify it’s not exactly eBPF, but drawing from it to create a custom event model based on JS internals.

**Clarified eBPF-inspired probe design**

**Designing JS Probing Events**

I'm considering various event types for JS probing such as function entry, exit, and mutation. I need to ensure safe operations, bounded loops, and clear control flow, with efficient integrations for Go/JS.

**Designed JS Probing Events**

**Instrumenting async and static analysis**

I’m considering how to enhance async handling and runtime safety in Go/JS. I’ll link context between async calls, integrate static analysis with CFG, and use proofs to verify invariant conditions.

**Instrumented async and static analysis**

**Evaluated probe execution strategies with Go and WebAssembly**

**Building an eBPF-inspired probe plane**

I’m considering a Go/JS fork that introduces an eBPF-like probe system. Key steps: defining events like function entry, compiling hooks, profiling, and verifying program correctness with structured proof techniques.

</details>

```json
{"search_query":[{"q":"site:docs.kernel.org/bpf fentry fexit BPF trampoline tracing program documentation"},{"q":"site:docs.kernel.org/bpf verifier documentation initialized stack bounded loops"},{"q":"site:docs.kernel.org/bpf ring buffer map documentation BPF"},{"q":"site:docs.kernel.org/bpf BTF documentation type metadata"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched eBPF documentation and related kernel sources**

**Inspected Goja repo and searched for profiler insights**

</details>

```json
{"open":[{"ref_id":"turn596878view0","lineno":636}],"response_length":"medium"}
```

Because Programs are runtime-independent and shareable, dynamic probes should use immutable metadata and runtime-local attachment tables, not bytecode rewriting. Full semantic coverage likely requires a goja fork.

<details><summary>💭 Thinking</summary>

**Searched the web and GitHub**

</details>

```json
{"paths":["GitHub"],"query":"repository"}
```

```json
{"uri":"/response/turn27","query":"type _ret"}
```

```json
{"uri":"/response/turn27","query":"vmCall(vm"}
```

```json
{"uri":"/response/turn27","start_line":4700,"num_lines":300}
```

# Build a verified semantic-probe layer

This is feasible, and goja is a good target because its interpreter, compiler, stack, object model, and scheduler-facing mechanisms are all implemented in Go. Its runtime is intentionally single-goroutine, which also gives the instrumentation subsystem a relatively simple execution and consistency model. fileciteturn2file0L66-L75

The clean design is not “invoke arbitrary callbacks around every operation.” It is:

```text
JavaScript source
      │
      ▼
 parser / compiler ───────► static-analysis metadata
      │
      ▼
 goja Program + semantic site IDs
      │
      ▼
 interpreter ── semantic events ──► verified probe programs
                                         │
                       ┌─────────────────┼──────────────────┐
                       ▼                 ▼                  ▼
                    typed maps       ring buffer       invariant action
                    counters         trace events      report / abort
                       │                 │
                       └───────── host control plane ───────┘
```

The eBPF concepts worth retaining are attachment types, a verifier, restricted helpers, typed maps, stable metadata, and detachable links. The Linux facilities treat these as separate components; the exact eBPF instruction set is not the important part here. citeturn211411search0turn211411search6turn211411search13turn211411search3

I would describe the result as **verified semantic probes for goja**, rather than literally JavaScript eBPF.

## The fundamental event model

Separate **call-site events** from **callee lifecycle events**. They are not equivalent.

| Execution | Event sequence |
|---|---|
| Normal JavaScript call | `CallBefore → FunctionEnter → FunctionReturn → CallAfter` |
| JavaScript call that unwinds | `CallBefore → FunctionEnter → FunctionThrow → CallThrow` |
| Native Go function | `CallBefore → HostEnter → HostReturn/HostThrow → CallAfter/CallThrow` |
| Constructor | `ConstructBefore → FunctionEnter → FunctionReturn/Throw → ConstructAfter/Throw` |
| Async function | Invocation returns a Promise; eventual settlement generates separate `AsyncResolve` or `AsyncReject` |
| Generator | Invocation creates a generator without entering the body; later `next()` produces `Enter`, `Yield`, `Resume`, and `Complete` events |

That distinction lets one probe measure caller latency while another asserts the callee’s preconditions and postconditions.

A useful initial event set is:

```go
type ProbeEvent uint64

const (
    EventCallBefore ProbeEvent = 1 << iota
    EventCallAfter
    EventCallThrow

    EventFunctionEnter
    EventFunctionReturn
    EventFunctionThrow

    EventConstructBefore
    EventConstructAfter
    EventConstructThrow

    EventHostEnter
    EventHostReturn
    EventHostThrow

    EventAwaitSuspend
    EventAwaitResume
    EventAsyncResolve
    EventAsyncReject

    EventGeneratorYield
    EventGeneratorResume
    EventGeneratorComplete
)
```

Property reads, property writes, allocations, branches, promise jobs, module loading, and individual instructions can follow later. They are substantially higher-volume and semantically harder.

## Why this belongs in the goja core

AST rewriting is useful for a prototype, but it is not a complete implementation.

Goja’s VM contains the active `Program`, program counter, value stack, argument and stack-base indexes, lexical stash, call stack, try stack, async runner, and profiler state. Instructions are internal objects implementing `exec(*vm)`. fileciteturn11file0L102-L133 Its main execution loop dispatches those instructions directly. fileciteturn11file0L345-L390

There are several separate invocation and exit paths:

- The ordinary bytecode call instruction retrieves the callee from the value stack and invokes `obj.self.vmCall(vm, n)`. fileciteturn31file0L234-L246
- A function called externally from Go goes through `baseJsFuncObject.__call`, which constructs a VM frame and runs the VM itself. fileciteturn10file0L13-L75
- Native functions have a separate `vmCall` implementation that synchronously invokes the Go function and updates the caller’s stack. fileciteturn10file0L175-L201
- Normal JavaScript returns are implemented by `_ret.exec`, which moves the result into the caller’s frame and pops the current context. fileciteturn33file0L245-L265
- Exceptional exits are not ordinary returns. `handleThrow` restores stack and lexical state and may truncate several call frames while searching for a catch or finally target. fileciteturn12file0L153-L197
- Constructors and `super()` have paths separate from ordinary calls. fileciteturn23file0L17-L55

Wrapping source-level function bodies will therefore miss or mishandle some combination of:

- Go-to-JavaScript invocation
- native Go functions
- constructors and derived constructors
- getters, setters, proxies, and internal calls
- direct `eval` and dynamically created functions
- exception unwinding through multiple frames
- generators and asynchronous functions
- functions compiled or introduced after initial source transformation

The production implementation should be a small goja fork or an upstream instrumentation API. The AST-rewriting version is still useful for validating the probe language and user experience.

## Exact core hook strategy

### Calls

Introduce one internal invocation path and gradually route every call site through it:

```go
func (vm *vm) invoke(
    callee *Object,
    numArgs int,
    kind CallKind,
    site CallSiteID,
) {
    frame := vm.probes.beforeCall(vm, callee, numArgs, kind, site)

    // For interpreted functions this switches VM context.
    // For native functions it completes synchronously.
    callee.self.vmCall(vm, numArgs)

    if vm.probes.callCompletedSynchronously(frame) {
        vm.probes.afterCall(vm, frame)
    }
}
```

Patching only `call.exec` is insufficient. Internal operations and external Go calls must eventually use the same lifecycle machinery.

For an interpreted function, `vmCall` merely changes the active VM context. `CallAfter` cannot be emitted immediately. Store probe correlation data alongside the saved VM context and complete it when `_ret` executes or when `handleThrow` removes that frame.

One workable internal addition is:

```go
type context struct {
    // existing VM fields...

    probeFrame ProbeFrameID
    callSite   CallSiteID
}
```

A parallel probe-frame stack is another option, but aligning it with `callStack` makes unwind correctness easier.

### Function entry

Define `FunctionEnter` as occurring **after parameter and local-frame initialization**, not merely when the program pointer changes.

Goja has multiple function-prologue instructions, including regular, stash-based, and stashless forms. Have each prologue call a small common method after it establishes the frame:

```go
func (vm *vm) finishFunctionEnter() {
    if vm.probes.mask&EventFunctionEnter != 0 {
        vm.probes.functionEnter(vm)
    }
}
```

This gives the probe a stable view of `this`, arguments, and initialized parameter bindings.

`CallBefore` remains the appropriate event for inspecting or guarding the raw arguments before the callee begins.

### Normal return

Immediately before `_ret` overwrites the caller’s result slot and pops the context:

1. Read the final return value.
2. Fire `FunctionReturn`.
3. Fire the correlated caller-side `CallAfter`.
4. Apply an intervention result only when the probe has explicit rewrite capability.
5. Perform the existing frame pop.

Because this occurs at the actual VM return, it naturally observes return values after `finally` blocks have finished altering control flow.

### Exceptional return

Instrument `handleThrow`, not just the `_throw` instruction.

A thrown value may be caught in the current function, cross one function, or cross many. Before `handleThrow` truncates call frames, emit `FunctionThrow` and `CallThrow` for every function frame that is actually crossed. Do not emit a function-exit event when the exception is caught inside the same function.

This is also where an invariant failure should enter the interpreter. An enforcement-mode violation should normally be a dedicated uncatchable host error; otherwise script code can catch and suppress the invariant failure. Goja already distinguishes uncatchable runtime errors while leaving a program. fileciteturn18file0L175-L193

### Constructors

Wrap the central constructor invocation rather than just `_new.exec`. The event context should identify:

```go
type ConstructContext struct {
    Constructor ValueHandle
    NewTarget   ValueHandle
    Arguments   ArgView
    Instance    ValueHandle // available after successful construction
    Derived     bool
}
```

A derived constructor may not have an initialized `this` until `super()` succeeds, so the verifier and helper API must model `this` as potentially unavailable.

### Async functions and generators

These require their own semantics, rather than pretending they are synchronous calls.

For an async function:

- `FunctionReturn` for the invocation means “returned its Promise.”
- `AsyncResolve` and `AsyncReject` represent eventual completion.
- `AwaitSuspend` and `AwaitResume` describe internal continuation boundaries.

For a generator:

- Calling the generator function returns a generator object without running its body.
- `FunctionEnter` occurs on the first `next()`.
- `GeneratorYield`, `GeneratorResume`, and `GeneratorComplete` form the execution lifecycle.

Goja already has separate async call and runner machinery, so these events have concrete places to attach. fileciteturn10file0L229-L291

## Do not expose raw VM state to probes

A probe must not receive `*vm`, `*stash`, Go pointers, or unrestricted `goja.Value`s.

Use borrowed, opaque handles:

```go
type ProbeContext struct {
    Event      ProbeEvent
    RuntimeID  uint64
    ProgramID  ProgramID
    FunctionID FunctionID
    CallSiteID CallSiteID
    FrameID    FrameID
    Depth      uint32

    This      ValueHandle
    Arguments ArgView
    Result    ValueHandle
    Exception ValueHandle

    Source SourceLocation
}
```

The handles are valid only for the duration of the event. A probe can use verified helpers such as:

```text
arg_count()
arg(index)
typeof(value)
bool_value(value)
i64_value(value)
f64_value(value)
string_hash(value)
same_value(a, b)
object_id(value)
own_data_property(value, property_id)
map_lookup(map, key)
map_update(map, key, value)
counter_add(map, key, delta)
histogram_observe(map, key, value)
emit(event_type, payload)
violation(code, payload)
```

The distinction between `own_data_property` and an ordinary JavaScript property read is important. Reading a property can execute a getter or proxy trap, recursively enter JavaScript, mutate state, throw, or trigger the same probe again.

For contract and proof modes, the safe helper should:

- accept only ordinary objects;
- reject proxies, accessors, and dynamic host objects;
- read only an existing own data property;
- perform no JavaScript conversion;
- have bounded output size.

A separate capability may permit effectful JavaScript-semantic property reads for debugging, but such probes are not observationally transparent.

Similarly, maps should not retain raw `goja.Value`s. Store primitive copies, stable runtime-local IDs, hashes, or bounded snapshots. Otherwise probes can accidentally retain the JavaScript object graph indefinitely.

## The probe program should not itself be JavaScript

Executing arbitrary JavaScript for every event would introduce:

- unbounded execution;
- recursion into the instrumented runtime;
- allocations and garbage-collection pressure;
- getters, proxies, exceptions, and Promise jobs;
- uncontrolled host access;
- nondeterminism;
- no useful resource-safety proof.

Use a dedicated restricted IR. It can have JavaScript-like source syntax, but it should compile to a small verified program.

For example:

```text
probe debit_contract {
    attach function "ledger.js"::"debit";

    frame_local<i64> entry_balance;
    counter calls;
    histogram<i64> duration_ns;

    on enter(amount) {
        assert i64(amount) >= 0;
        entry_balance = own_i64(this, "balance");
        calls += 1;
    }

    on return(amount, result) {
        let current = own_i64(this, "balance");

        assert current >= 0;
        assert current == entry_balance - i64(amount);

        duration_ns.observe(frame_elapsed_ns());
    }

    on throw(error) {
        emit("debit_failed", object_id(this), error_code(error));
    }
}
```

This source is only notation. Its compiled program might use ten 64-bit registers, a fixed stack, typed handles, map operations, conditional branches, and helper calls.

### Verifier requirements

A first verifier should establish:

- every register is initialized before use;
- handle types are valid on every control-flow path;
- helper argument and return types match;
- stack accesses are in bounds;
- map keys and values match their declared schemas;
- there are no backedges in version 1;
- total instructions per event are bounded;
- emitted data is bounded;
- snapshot traversal depth and bytes are bounded;
- requested helpers are allowed by the probe’s capability set;
- the probe cannot re-enter goja;
- mutation instructions are rejected in read-only mode.

Loops can be added later when the verifier can establish a static bound. A no-loop first version is enough for metrics, contracts, finite-state monitors, and most event filters.

## Separate observation, enforcement, and intervention

These should be different modes with different capability sets.

### Observation

The probe may read approved context, update maps, and emit records. It cannot change execution.

This mode supports metrics, profiling, coverage, call graphs, traces, and debugging.

### Enforcement

The probe remains read-only but may terminate execution with a structured invariant violation.

This supports preconditions, postconditions, state invariants, protocol enforcement, resource limits, and runtime policy.

### Intervention

The probe may replace arguments, replace a return value, suppress a call, synthesize an exception, or alter selected state.

This can support fault injection and dynamic patching, but it is no longer transparent instrumentation. Results from intervention mode should not be presented as evidence about the behavior of the unmodified program.

The API should make this distinction impossible to overlook:

```go
type ProbeMode uint8

const (
    ProbeObserve ProbeMode = iota
    ProbeEnforce
    ProbeIntervene
)
```

## Maps and temporal invariants

Maps are what make this more useful than ordinary tracing.

Useful map types include:

```text
array
hash
LRU hash
counter
histogram
frame-local storage
function-local storage
runtime-local storage
ring buffer
finite-state monitor
```

A protocol property such as “a transaction cannot commit before it has begun” becomes a monitor keyed by transaction ID:

```text
on call begin(tx):
    state[tx] must_be ABSENT
    state[tx] = STARTED

on call commit(tx):
    assert state[tx] == STARTED
    state[tx] = COMMITTED

on call rollback(tx):
    assert state[tx] == STARTED
    delete state[tx]
```

Frame-local storage should be built into the runtime rather than implemented as an ordinary hash keyed by frame ID. That makes entry-to-return state inexpensive and guarantees cleanup on normal return, throw, interrupt, and cancellation.

## Static analysis and the “proof” layer

Runtime assertions are monitors. They can find counterexamples and enforce properties on executed paths. By themselves, they are not universal proofs over every possible execution.

The useful architecture is **residual verification**:

1. The compiler produces a CFG, binding metadata, function IDs, call-site IDs, source spans, and conservative effect information.
2. A static analyzer proves the obligations it can discharge.
3. Unresolved obligations are compiled into verified runtime monitors at precise semantic sites.
4. A manifest binds the source hash, compiler options, goja version, program metadata hash, probe ABI, native-module contracts, and residual monitors.
5. Runtime failures produce a compact counterexample trace with monitor state.

A runtime monitor can be modeled precisely as:

```text
M = (S, s₀, δ, Bad)

δ : S × Event × ProjectedState → S
```

An execution violates the property when `δ` reaches `Bad`. This supports finite-state protocols directly. Restricted temporal properties can be compiled into such monitors.

For a closed-world proof mode, the assumptions must also be explicit:

- `eval` and `Function` are disabled, or dynamically produced code passes through the same analysis pipeline.
- Native modules provide effect and contract summaries.
- Proxies, getters, reflective operations, and dynamic host objects are modeled conservatively.
- `with` and other dynamically scoped constructs are marked opaque or rejected.
- time, randomness, I/O, and asynchronous scheduling are either modeled or recorded.
- no event can be dropped.
- probes cannot be detached by untrusted JavaScript.

The probe verifier proves the safety and boundedness of the **monitor**. A separate analyzer or theorem prover proves properties of the JavaScript program.

## Compiler metadata is the BTF-equivalent

Goja’s current `Program` stores internal instructions, function name, source file, and a source map. fileciteturn35file0L64-L78 It also publicly exposes parsing and AST compilation, which is enough for an initial source-level analyzer. fileciteturn18file0L66-L110

For durable attachment and proof artifacts, add an immutable metadata object:

```go
type ProgramMeta struct {
    ABI         uint32
    ProgramHash [32]byte
    ProgramID   ProgramID

    Functions []FunctionMeta
    CallSites []CallSiteMeta
    Bindings  []BindingMeta
}

type FunctionMeta struct {
    ID           FunctionID
    Name         string
    Source       SourceSpan
    Parameters   []BindingID
    Locals       []BindingID
    DynamicScope bool
    Async        bool
    Generator    bool
}

type CallSiteMeta struct {
    ID       CallSiteID
    Function FunctionID
    Source   SourceSpan
    Kind     CallKind
}
```

Selectors such as:

```text
module == "ledger.js"
function == "debit"
line in 80..120
annotation contains "@invariant"
```

should be resolved at attachment time into compact IDs and bitsets. The hot path should never perform string matching.

For local-variable inspection, use `BindingID`, plus a compiler-generated liveness and location table. A helper such as `read_local(bindingID)` should fail unless that binding is live at that event site. This avoids exposing raw stack indexes, which are compiler implementation details.

## Performance model

The disabled path must be designed first.

For call-level probes, the expected disabled overhead can be limited to one predictable mask check at semantic boundaries:

```go
if vm.probes.mask&EventCallBefore != 0 {
    vm.probes.fireCallBefore(...)
}
```

Do not put an unconditional generic dispatcher in the instruction loop.

For instruction-level or branch-level instrumentation, select a different run loop once:

```go
if vm.probes.instructionMask != 0 {
    vm.runWithInstructionProbes()
} else {
    vm.runFast()
}
```

This mirrors the general shape of goja’s existing profiler, which uses a specialized execution path and captures VM stack information during sampling. fileciteturn8file0L314-L330

Other important implementation rules:

- Preverify and freeze probe programs.
- Pre-resolve attachments to program/function/site IDs.
- Use fixed-layout, allocation-free event records.
- Write telemetry into a bounded ring buffer.
- Drain and encode the buffer outside the VM owner goroutine.
- Give every probe a step and helper-cost budget.
- Disable or fail a probe that repeatedly exceeds its budget.
- Sample instruction, property, and allocation events.
- Never format strings in the hot path.
- Benchmark disabled, no-op-attached, counter-only, contract, native-call, throw, async, and recursive workloads separately.

## Integration into go-go-goja

`go-go-goja` already has the correct control-plane boundary. Its `RuntimeInitializer` receives the VM, require system, event loop, runtime owner, and a runtime-scoped values map. fileciteturn37file0L18-L33 The builder supports adding those initializers to every created runtime. fileciteturn16file0L101-L107

The integration could look like:

```go
factory, err := engine.NewRuntimeFactoryBuilder().
    WithRuntimeInitializers(
        probe.Initializer(probe.Config{
            MaxMapBytes:   16 << 20,
            RingBytes:     4 << 20,
            AllowEnforce:  true,
            AllowMutation: false,
        }),
    ).
    Build()
```

The initializer would:

1. Create a `probe.Manager`.
2. Attach it to the underlying goja runtime.
3. Store it in `ctx.Values["probe.manager"]`.
4. Register cleanup with the runtime lifecycle.
5. Optionally install a trusted host-only control module.

Attach and detach operations should execute through the runtime owner because goja itself must only be accessed by one goroutine at a time. `go-go-goja` already centralizes runtime ownership and scheduling for this reason. fileciteturn3file0L301-L336

A likely package arrangement is:

```text
goja fork
├── probe_api.go
├── probe_runtime.go
├── probe_context.go
├── probe_metadata.go
├── probe_maps.go
├── probe_verifier.go
└── probe_ir.go

go-go-goja
├── pkg/probe/
│   ├── initializer.go
│   ├── manager.go
│   ├── loader.go
│   └── exporter.go
├── modules/probe/       # optional trusted control module
└── cmd/goja-repl/
    └── probe_commands.go
```

Possible CLI surfaces:

```text
goja-repl --probe contracts.jpf run application.js

goja-repl probe verify contracts.jpf
goja-repl probe list
goja-repl probe attach contracts.jpf
goja-repl probe maps
goja-repl probe events
```

The JavaScript-facing module should not normally permit arbitrary scripts to detach enforcement probes or inspect all runtime state.

## A realistic implementation sequence

### Phase 1: establish event semantics

Fork goja and implement a trusted, read-only Go event sink for:

```text
CallBefore
FunctionEnter
FunctionReturn
FunctionThrow
CallAfter
CallThrow
ConstructBefore
ConstructAfter
ConstructThrow
HostEnter
HostReturn
HostThrow
```

Do not build the probe bytecode yet. First make event ordering correct.

Tests should cover normal calls, recursive calls, native calls, external Go-to-JavaScript calls, caught exceptions, multi-frame unwinds, `return` through `finally`, constructors, derived constructors, `super()`, proxy apply/construct, interruption, and runtime shutdown.

### Phase 2: introduce stable metadata

Add program, function, call-site, and binding IDs. Produce a program metadata fingerprint and resolve attachment selectors into IDs.

This avoids designing the verifier around unstable VM stack positions.

### Phase 3: add the verified probe VM

Start with:

- no loops;
- integer and Boolean operations;
- typed value handles;
- counters, hashes, frame-local storage, and ring buffers;
- primitive argument and return inspection;
- safe own-data-property reads;
- `emit`;
- `violation`;
- strict step and memory budgets.

That is already enough for metrics, preconditions, postconditions, state invariants, and temporal protocols.

### Phase 4: add compiler analysis

Produce CFGs, binding/liveness metadata, effect summaries, and residual-monitor manifests. Integrate an SMT solver or abstract interpreter outside the hot runtime.

### Phase 5: add difficult semantic domains

Add async completion, generators, Promise jobs, property operations, allocations, branch coverage, instruction sampling, dynamic compilation, and optional intervention mode.

Property and instruction probes should not be part of the first implementation. Their event volume and semantic side effects can obscure whether the core call-frame model is correct.

## Recommended first milestone

The first useful deliverable is not a complete eBPF clone. It is:

```text
goja fork
  + stable function and call-site IDs
  + read-only call/enter/return/throw/construct events
  + frame-local state
  + counter/histogram/ring-buffer maps
  + uncatchable invariant violations
  + go-go-goja RuntimeInitializer integration
```

That milestone supports:

- per-function latency and call metrics;
- call graphs;
- argument and return contracts;
- cross-entry/return state invariants;
- exception policies;
- temporal state machines;
- structured counterexample traces.

After those event semantics are proven correct, introducing the restricted ISA and verifier is straightforward. Reversing that order risks building a sound verifier for an unsound event model.


---

> Research how this relates and influences and enables work on operational and dejotational semantics, both theoretically, but also as daily tools to assist actual academic work

<details><summary>💭 Thinking</summary>

**Researching formal semantics**

I’m digging into the relationship between tools, such as instrumentation and formal semantics, and their practical applications. I’ll focus on primary sources like papers and documentation, trying to clarify the theories and workflows involved.

**Researched formal semantics**

</details>

I’ll treat “dejotational” as “denotational” and connect the probe system to semantics theory, runtime verification, and practical academic workflows.

```json
{"search_query":[{"q":"site:dl.acm.org JavaScript formal operational semantics paper executable semantics"},{"q":"site:arxiv.org JavaScript denotational semantics paper"},{"q":"site:pldi.acm.org runtime verification instrumentation semantics paper"},{"q":"\"dejotational semantics\""}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched for primary papers on JavaScript semantics on arxiv.org**

**Researching niche topics**

I’m aiming to dive deep into operational and denotational semantics, tracing topics like instrumentation semantics and runtime verification. The literature review will focus on primary papers and recent publications.

**Researched niche topics**

**Searched for primary papers on JavaScript semantics**

**Exploring trace semantics**

I’m considering how operational semantics, trace domains, and verification approaches intersect. I want to understand how these tools can be used for analyzing and verifying execution across different systems.

**Explored trace semantics**

</details>

```json
{"search_query":[{"q":"JSCert Coq JavaScript semantics paper PDF"},{"q":"KJS complete formal semantics JavaScript paper PDF"},{"q":"PLT Redex semantics engineering paper PDF executable models"},{"q":"runtime verification monitor operational semantics instrumentation paper PDF"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched for research papers and sources on semantics and verification**

**Refining semantic tools**

I’m focusing on integrating formal semantics like K, Lean, and Coq with daily academic tools. I’ll search for documents on these frameworks, exploring how they relate to operational and denotational semantics.

**Refined semantic tools**

</details>

```json
{"search_query":[{"q":"Plotkin Pretnar handlers of algebraic effects paper official PDF"},{"q":"algebraic effects denotational semantics handlers paper PDF Plotkin Pretnar"},{"q":"free monad trace semantics instrumentation programming languages paper"}],"response_length":"long"}
```

The key move is treating hooks as labels on semantic transitions and probes as trace observers, enabling projection, refinement, monitor-product semantics, and independent checking.

<details><summary>💭 Thinking</summary>

**Searched for academic papers on algebraic effects and semantics**

**Researching formal semantics tools**

I’m working on connecting academic tools with operational and denotational semantics. The goal is to map theoretical findings, like approximate semantics, to practical tooling using trace and event systems for verification.

</details>

```json
{"search_query":[{"q":"Abstracting Denotational Interpreters paper 2024 PDF"},{"q":"Abstracting Abstract Machines Van Horn Might 2011 PDF"},{"q":"Trace-Relating Compiler Correctness paper PDF"},{"q":"runtime monitoring instrumentation survey paper PDF"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched for academic sources on abstract machines and topics**

</details>

Separate implementation transitions, canonical JavaScript events, and specification steps so bytecode details do not define semantics. The event calculus can support monitoring, symbolic execution, abstract interpretation, and proof assistants.

# Semantic probes as infrastructure for semantics research

Properly designed, this is not merely an observability feature. It is a **semantic interface between a concrete interpreter and formal models**.

The central artifact would be a stable, typed event algebra emitted at language-semantic boundaries:

```text
source program
      │
      ▼
goja execution ── semantic events ──► verified probe
      │                                   │
      │                                   ├── runtime monitor
      │                                   ├── metric/cost algebra
      │                                   ├── trace generator
      │                                   └── invariant checker
      │
      └──────── semantic map ─────────► Redex / K / Rocq / Lean / SMT
```

This combines several traditions that mostly exist separately:

- Redex and K begin with an executable semantic model and derive testing, execution, symbolic execution, or proof tools.
- JSCert begins with a mechanized ECMAScript specification and proves a reference interpreter correct with respect to it.
- KJS provides an executable JavaScript semantics and uses semantic-rule coverage and symbolic execution.
- JSExplain turns a specification-oriented interpreter into a “double debugger” showing both the interpreter and interpreted program.
- Monitoring-oriented programming and contract systems weave runtime monitors into programs.
- Interaction trees and algebraic effects give a compositional denotational account of computations as event-producing structures.

The proposed goja system would add something distinct: **verified, dynamically attachable semantic observers inside a production-style interpreter**, with enough metadata to relate concrete execution back to formal rules. citeturn117935search0turn727407search2turn454603search0turn190468search6turn547820search1

## 1. The operational-semantics interpretation

### From callbacks to labelled transitions

A small-step operational semantics normally has configurations such as

\[
C = \langle e,\rho,\sigma,\kappa,J,H\rangle
\]

where:

- \(e\) is the current expression or instruction;
- \(\rho\) is the lexical environment;
- \(\sigma\) is the store or heap;
- \(\kappa\) is the continuation or call stack;
- \(J\) is the job or asynchronous-work state;
- \(H\) is the host environment.

The uninstrumented semantics is a relation

\[
C \longrightarrow C'
\]

The probe architecture should turn this into a **labelled transition system**:

\[
C \xrightarrow{\ell} C'
\]

where \(\ell\) is either an internal event \(\tau\), or a semantic event such as:

```text
CallBefore
FunctionEnter
FunctionReturn
FunctionThrow
PropertyRead
PropertyWrite
JobEnqueue
JobStart
AwaitSuspend
AwaitResume
PromiseResolve
PromiseReject
```

This is directly in the tradition of structural operational semantics: transitions and their labels give a mathematically explicit account of the steps by which behavior is produced. citeturn573716search1turn573716search3

The important phrase is **semantic event**. A semantic event is not necessarily identical to a goja function call or bytecode instruction. For example:

- `FunctionReturn` means the function has semantically completed, after any relevant `finally` processing.
- `FunctionThrow` means an exception actually crosses the function boundary.
- `AwaitSuspend` means the async execution has produced and registered its continuation.
- `PropertyRead` may need to distinguish a raw own-data-property observation from a JavaScript read that invokes getters or proxies.

Goja already has the concrete material needed for this mapping: its VM tracks the active program and program counter, value stack, lexical stash, call stack, exception frames, async runner, and profiler state. fileciteturn11file0L102-L129 Its interpreter loop directly dispatches internal instructions. fileciteturn11file0L345-L390

### The monitor-product semantics

A verified probe can be modeled as a state machine

\[
\delta : M \times E \times O \rightarrow M \times A
\]

where:

- \(M\) is probe state;
- \(E\) is the semantic event;
- \(O\) is a bounded observation projected from the VM state;
- \(A\) is an action such as `continue`, `violation`, or, in an explicitly privileged mode, `intervene`.

The instrumented semantics is the product of the program machine and the monitor:

\[
\frac{
 C \xrightarrow{e/o} C'
 \qquad
 \delta(m,e,o)=(m',\mathsf{continue})
}{
 (C,m)\Longrightarrow(C',m')
}
\]

Internal transitions leave the monitor unchanged:

\[
\frac{C\xrightarrow{\tau}C'}{(C,m)\Longrightarrow(C',m)}
\]

This standard product construction gives a clear basis for runtime invariants, temporal properties, typestate, protocol monitoring, and trace collection. Monitoring-oriented programming already synthesizes monitors from formal specifications and integrates them at selected program locations; parametric monitoring additionally gives a semantics for slicing one event stream into per-object or per-transaction traces. citeturn880375search0turn880375search3turn880375search5

### The proof obligations this creates

A publication-quality implementation should distinguish several independent theorems.

| Obligation | Representative statement | What it establishes |
|---|---|---|
| **Erasure or transparency** | \(\mathsf{erase}(\mathsf{run}_{probe}(p,m))=\mathsf{run}(p)\) | Read-only probes do not alter JavaScript behavior. |
| **Event adequacy** | Every emitted event corresponds to a defined source-semantic transition or macro-transition. | The trace means what its schema claims. |
| **Trace completeness** | Every selected semantic transition emits exactly the required event. | Monitors cannot silently miss relevant behavior. |
| **Monitor compilation** | A compiled monitor rejects exactly the bad prefixes described by its source property. | The probe compiler implements the specification logic correctly. |
| **Probe safety** | Verified probes terminate within a bound, access only typed observations, and cannot re-enter or corrupt the VM. | Attaching a probe is operationally safe. |
| **VM/source refinement** | \(\mu(\mathsf{trace}_{VM}(\mathsf{compile}(p)))\in\mathsf{Traces}_{source}(p)\) | The implementation trace refines the formal JavaScript semantics. |

The erasure theorem is the semantic analogue of “disabled or observing probes are transparent.” Depending on whether event production introduces extra administrative steps, the appropriate relation will usually be a simulation or weak bisimulation rather than literal step-for-step equality.

The current ECMAScript specification explicitly describes execution contexts as specification devices that need not correspond directly to implementation artifacts. That means the project needs an explicit abstraction relation from goja frames, stacks, and jobs to ECMAScript-level contexts and completions; it cannot simply declare the VM structures to be the formal semantics. citeturn727407search0

### Observation, enforcement, and intervention have different semantics

The three probe modes should be treated formally differently.

**Observation** conservatively enriches an execution with a trace. Erasing the trace should recover the original behavior.

**Enforcement** allows a probe to stop execution when it recognizes a bad prefix. The monitored semantics produces a subset of the original complete executions, plus explicit violation outcomes. This is useful for safety properties, but it is not behavior preserving.

**Intervention** can rewrite arguments, results, exceptions, or state. At that point the probe mechanism is a language extension, aspect system, fault-injection mechanism, or dynamic program transformation. Results from such a run are not evidence about the unmodified program.

That separation is especially important for academic claims. “The monitor was verified” may mean only that the monitor is safe to execute. It does not automatically mean that the monitored program satisfies the intended property or that interventions preserve program meaning.

## 2. The denotational-semantics interpretation

### Programs as event-producing computations

A simple stateful denotation might map a program to a result and store:

\[
\llbracket p\rrbracket : \Sigma \rightarrow \mathsf{Outcome}\times\Sigma
\]

Instrumentation enriches that denotation with events:

\[
\llbracket p\rrbracket_E :
\Sigma \rightarrow \mathsf{Trace}(E)\times\mathsf{Outcome}\times\Sigma
\]

For JavaScript, a finite trace is insufficient because of divergence, asynchronous interaction, host effects, and potentially nondeterministic scheduling. A more useful model is coinductive:

\[
\llbracket p\rrbracket :
\Sigma \rightarrow \mathsf{ITree}\ E\ (\mathsf{Outcome}\times\Sigma)
\]

Interaction trees represent recursive, effectful computations as trees of uninterpreted events and continuations. Event handlers subsequently assign meanings to those events, while weak bisimulation supports reasoning that ignores internal administrative steps. They were explicitly designed to combine executability, compositional semantics, testing, and mechanized proof. citeturn561141academia36turn561141search1

This gives a clean denotational account of probes:

```text
JavaScript execution denotation
          │
          ▼
   event-producing tree
          │
   ┌──────┼─────────┬───────────┐
   ▼      ▼         ▼           ▼
 trace  metrics   monitor   symbolic constraints
```

### Probes as handlers or algebras

A handler interprets semantic events in some target domain:

\[
h : E \rightarrow M
\]

More accurately, for a stateful monitor:

\[
h : E \rightarrow \mathsf{State}\ M
\]

Different handlers give different meanings to the same execution:

- A tracing handler appends events.
- A counter handler maps function-entry events into natural-number addition.
- A cost handler maps events into a cost semiring.
- A temporal monitor maps events into automaton-state transitions.
- A dependency handler constructs a graph.
- A symbolic handler turns observations into logical constraints.
- An invariant handler produces either success or a violation witness.

This is closely related to the algebraic-effects view in which computations are constructed from operations, while handlers interpret those operations as models or algebras. citeturn443166search3turn443166search13

A substantial theoretical advantage follows: probes can compose by taking products of their interpretation domains.

\[
h_1 \times h_2 : E \rightarrow M_1\times M_2
\]

Thus one execution can simultaneously compute:

```text
(call graph, semantic coverage, cost, contract state, trace digest)
```

without giving each analysis a separate ad hoc instrumentation mechanism.

### Metrics become semantic folds

Many metrics are monoid homomorphisms over traces:

\[
f(\epsilon)=1_M
\]

\[
f(t_1\cdot t_2)=f(t_1)\otimes f(t_2)
\]

Examples include:

- event counts;
- function-call multisets;
- accumulated abstract cost;
- maximum stack depth;
- sets of semantic rules exercised;
- histograms, when represented by an appropriate merge algebra.

This is more than mathematical decoration. It gives a principled way to:

- parallelize offline trace analyses;
- merge results from multiple runs;
- prove that aggregation is independent of trace chunking;
- compare online and offline implementations;
- specify exactly which metrics are compositional.

### Instrumentation changes observational equivalence

A central denotational issue is that instrumentation expands what can be observed.

Two programs may be contextually equivalent to ordinary JavaScript contexts but distinguishable by a probe:

```javascript
function f(x) {
    return x + 1;
}
```

and

```javascript
function f(x) {
    return helper(x);
}
function helper(x) {
    return x + 1;
}
```

A normal caller may be unable to distinguish them. A probe that sees function entries, call counts, allocation patterns, or bytecode instructions can distinguish them immediately.

Therefore:

\[
p \approx_{\mathrm{JS}} q
\quad\not\Rightarrow\quad
p \approx_{\mathrm{probe}} q
\]

The event alphabet itself defines an observer and therefore defines an observational theory.

This strongly suggests three event tiers:

| Tier | Examples | Intended stability |
|---|---|---|
| **Language-semantic** | call completion, throw crossing a frame, job enqueue, Promise settlement | Stable across correct implementations of the same language/host model |
| **Proof or derivation** | ECMAScript abstract-operation ID, formal-rule ID, completion-record transition | Stable relative to a chosen formal specification |
| **Implementation-intensional** | bytecode PC, allocation site, inline cache, stack slot | Specific to a goja version or compiler configuration |

Only the first two tiers should normally appear in claims about source-level semantics. The third is still valuable for performance and implementation research, but it creates a stronger and implementation-dependent observer.

A worthwhile theoretical result would be **full abstraction relative to an event capability**: characterize exactly when two programs are indistinguishable to all probes permitted by a given event and helper set.

## 3. A single probe language can have four semantics

The most productive design is not merely to execute the probe IR in the runtime. Give the same probe language several interpreters:

```text
                  ┌── concrete interpreter ─► runtime monitoring
probe source ─► IR├── symbolic interpreter ─► path constraints / SMT
                  ├── abstract interpreter ─► static approximation
                  └── logical translation ──► Rocq / Lean theorem
```

### Concrete interpretation

The verified VM executes a bounded monitor over actual goja values and events.

### Symbolic interpretation

Arguments, properties, and return values become symbolic terms. Assertions become solver constraints. This can drive symbolic execution, concolic test generation, or counterexample construction.

### Abstract interpretation

Values become abstract elements such as:

```text
sign
interval
type set
string abstraction
shape
points-to set
taint
automaton state
```

Each probe instruction receives an abstract transfer function. Abstract interpretation is explicitly the construction of approximate semantics over an abstract universe, linked soundly to the concrete semantics. citeturn190468search0turn190468search4

A contract such as:

```text
on enter(amount):
    assert amount >= 0
```

could therefore be:

- checked concretely on actual calls;
- executed symbolically to find a negative input;
- interpreted over intervals to prove that `amount ∈ [0,+∞]`;
- translated into a theorem-prover obligation.

### Logical interpretation

The probe becomes a predicate over traces or states. A theorem prover can establish that the monitor never reaches its violation state, assuming an operational or denotational model of the program.

This creates a useful distinction:

1. **The probe verifier** proves that the probe itself is bounded, typed, and safe.
2. **The monitor compiler proof** proves that the probe implements a temporal or state property.
3. **The program proof** proves that every program execution satisfies the property.
4. **Runtime monitoring** checks only the executions that actually occur.

Keeping these layers separate prevents an unsafe conflation of “verified monitor” and “verified application.”

## 4. Static–dynamic and residual verification

The probe architecture is a natural substrate for hybrid verification.

Suppose a source contract generates obligations

\[
\Phi=\{\phi_1,\ldots,\phi_n\}
\]

A static analyzer partitions them into:

\[
\Phi_{\mathrm{proved}}
\quad\cup\quad
\Phi_{\mathrm{residual}}
\]

The proved obligations disappear from runtime instrumentation. The residual obligations compile to probes at precise semantic sites.

This is the same general strategy as hybrid type checking: use static reasoning where possible and dynamic checks where necessary. Soft contract verification similarly tries to verify behavioral contracts statically and retain runtime checks only where proof is unavailable. citeturn532609search3turn532609academia47turn532609academia45

For JavaScript specifically, TreatJS demonstrates that higher-order contracts can be implemented through runtime monitoring and emphasizes non-interfering contract execution. A VM-level mechanism could provide stronger control over event coverage, boundedness, reentrancy, and side effects than unrestricted JavaScript contract predicates. citeturn532609search4turn532609academia48

The workflow would be:

```text
contract / theorem candidate
          │
          ▼
 static analysis or symbolic proof
          │
   ┌──────┴─────────┐
   ▼                ▼
proved         unresolved
   │                │
erase check     compile probe
                    │
                    ▼
              runtime evidence
                    │
          counterexample or new facts
                    │
                    └────► refine analysis
```

This can also support counterexample-guided refinement. A static false positive is matched against actual semantic traces, which identify where an abstract domain lost precision. Conversely, runtime violations supply concrete witnesses to improve the static model.

## 5. Runtime properties, temporal semantics, and hyperproperties

### Trace properties

A runtime monitor naturally checks a property

\[
P\subseteq E^\ast
\]

or, for infinite behavior,

\[
P\subseteq E^\omega
\]

Safety violations are particularly suitable because a violation has a finite bad prefix. The probe can preserve that prefix as a compact counterexample.

Temporal protocols become automata:

```text
ABSENT --begin(tx)--> STARTED
STARTED --commit(tx)--> COMMITTED
STARTED --rollback(tx)--> ABSENT
```

Object, Promise, request, transaction, or closure identities make the trace parametric. Parametric trace slicing provides a formal account of splitting the global execution into the relevant per-binding traces before applying ordinary monitors. citeturn880375academia46turn880375academia47

### Liveness

A finite execution prefix generally cannot show that an eventually-required event will never occur. The tool must report results such as:

```text
satisfied
violated
inconclusive
satisfied assuming normal termination
violated at end-of-run
```

rather than treating every monitor as a Boolean assertion.

### Hyperproperties

Properties such as noninterference, determinism across inputs, compiler equivalence, or observational consistency relate multiple traces. They are not ordinary single-trace properties. Hyperproperties were introduced precisely to classify such requirements. citeturn154629search0

A single attached probe cannot establish general noninterference. The workbench would need a multi-run layer:

```text
input relation
    │
    ├── run 1 ─► trace 1
    ├── run 2 ─► trace 2
    └── ...
             │
             ▼
       trace alignment
             │
             ▼
       hyper-monitor
```

HyperLTL monitoring research supplies algorithms and complexity results for processing multiple traces in parallel or sequentially. citeturn154629academia36

This would make the system useful for:

- information-flow experiments;
- observational determinism;
- differential testing;
- compiler or optimization validation;
- constant-time and side-channel studies;
- semantic equivalence up to selected events.

## 6. How this advances operational-semantics research

### Executable derivation traces from a real interpreter

A semantic trace can be more informative than an ordinary debugger trace:

```text
Source span: ledger.js:18:12
VM operation: call 2
Semantic event: CallBefore
Formal rule: E-CALL-ORDINARY
ECMAScript operation: EvaluateCall
Callee function ID: 0x4d1...
Receiver class: Ledger
Argument projection: [Int(10)]
```

That gives researchers a concrete derivation candidate for every execution. It can be compared with a Redex, K, Rocq, or Lean relation.

### Differential semantics validation

Run the same program through:

1. goja with semantic probes;
2. an executable formal semantics;
3. possibly another JavaScript implementation.

Normalize their events to a common alphabet, then identify the first divergence.

JSCert shows that a mechanized specification can support a proved-correct extracted reference interpreter tested against Test262. KJS shows that an executable semantics can be tested at scale, symbolically executed, and used to measure semantic-rule coverage; the KJS work reports that this coverage exposed missing tests and bugs in engines and other semantics. citeturn117935search0turn727407search2

The semantic event layer makes such comparisons much more local than comparing only final output.

### Rule coverage rather than line coverage

The tool can report:

```text
ECMAScript abstract operations exercised
formal inference rules exercised
completion kinds exercised
exception-unwind cases exercised
host interactions exercised
proof obligations exercised
```

This is directly useful when evaluating whether a paper’s test suite actually covers its semantics. KJS’s experience is strong evidence that semantic-rule coverage can expose gaps that ordinary source coverage misses. citeturn727407search2

### Testing metatheory against implementation behavior

A researcher may state a lemma such as:

> Every successful property assignment produces either an own-property update or an observable setter invocation.

A generated monitor can look for a counterexample in actual executions. This does not prove the lemma, but it can falsify an incorrect formulation rapidly.

Redex is a close methodological precedent: it supports executable reduction systems and randomized attempts to falsify metatheoretic properties. The “Run Your Research” study reports that mechanizing nine published models uncovered mistakes in all nine, demonstrating the daily value of lightweight executable semantics. citeturn547820search0turn190468search6

## 7. How this advances denotational-semantics research

### Executable and inspectable effect denotations

The probe events can form an explicit effect signature:

```text
Call
Return
Throw
Read
Write
Allocate
Enqueue
Resume
HostCall
```

A denotational model assigns an algebra to that signature. Researchers can swap handlers to study different semantic interpretations without modifying the JavaScript evaluator.

For example:

```text
handler Trace       : Event → Trace
handler Cost        : Event → Nat
handler Dependency  : Event → Graph
handler Security    : Event → SecurityLattice
handler Contract    : Event → MonitorState
```

The concrete interpreter becomes one source of event trees against which these denotations can be tested.

### Empirical testing of algebraic laws

Suppose a denotational model claims:

\[
\llbracket p;q\rrbracket
=
\llbracket p\rrbracket \bind (\lambda\_.\llbracket q\rrbracket)
\]

or that two handlers commute. The workbench can search concrete executions for counterexamples to the proposed equality under a selected observation algebra.

It remains testing, not proof, but it provides rapid feedback during model development.

### Contextual equivalence experiments

By selecting different event capabilities, researchers can empirically explore equivalence relations:

```text
result-only equivalence
result-and-exception equivalence
heap-effect equivalence
async-job equivalence
cost equivalence
full implementation-trace equivalence
```

The formal question becomes:

> Which event alphabets characterize which contextual equivalences?

This can lead to full-abstraction, adequacy, and representation-independence results.

### Cost semantics

Assign a symbolic cost to semantic events:

\[
\mathsf{cost}(\mathsf{Call})=c_c,\qquad
\mathsf{cost}(\mathsf{Read})=c_r,\qquad
\mathsf{cost}(\mathsf{Allocate})=c_a
\]

The denotation computes an abstract resource polynomial or weighted trace. Actual goja measurements can then calibrate or validate the model.

Wall-clock timing alone is problematic because instrumentation perturbs execution and includes host scheduling and garbage collection. Semantic operation counts, allocation counts, queue depth, and selected host durations provide a more stable bridge between formal cost models and measurements.

## 8. Daily academic tools

A serious implementation could expose the following workbench.

| Tool | Daily use | Research result |
|---|---|---|
| **Semantic double debugger** | Step by source construct, formal rule, ECMAScript abstract operation, or VM transition. | Faster diagnosis of errors in a semantics or implementation. JSExplain demonstrates the utility of simultaneously viewing interpreter and interpreted-program state. citeturn454603search0 |
| **Trace differential runner** | Run goja and an executable semantics, align canonical events, stop at the first divergence. | Conformance bugs, underspecified host assumptions, incorrect formal rules. |
| **Semantic coverage explorer** | Display uncovered rules, completion cases, proxy paths, Promise transitions, and exception edges. | Better test suites and quantitative artifact evaluation. |
| **Invariant miner** | Collect typed values at semantic program points and infer candidate equalities, ranges, shapes, and implications. | Candidate lemmas and contracts. Daikon established this trace-based workflow for discovering likely invariants, while emphasizing their dependence on the observed test suite. citeturn561141search0 |
| **Counterexample recorder** | Save the finite event prefix, inputs, host responses, and projected state that caused a violation. | Reproducible theorem counterexamples and regression tests. |
| **Proof debugger** | Attach assertions corresponding to induction hypotheses or simulation invariants. | Finds the first concrete point where the proposed invariant fails. |
| **Abstract-analysis calibrator** | Compare abstract states with observed concrete states at matching semantic sites. | Identifies precision loss, incorrect transfer functions, and unnecessary widening. |
| **Temporal protocol laboratory** | Write automata or temporal formulas over object- and Promise-parameterized events. | Runtime semantics for typestate, APIs, resources, and async protocols. |
| **Cost-semantics laboratory** | Apply cost handlers to traces and compare predicted cost with measured execution. | Empirical validation and refinement of resource semantics. |
| **Artifact packager** | Bundle source, runtime commit, semantic schema, monitor, trace digest, checker, and query. | Reproducible paper artifacts and independently checkable experimental claims. |

### A concrete async-semantics workflow

Suppose a paper proposes a semantics for `async`/`await`.

1. Assign formal IDs to rules such as `AWAIT-SUSPEND`, `PROMISE-REACTION`, and `ASYNC-RESUME`.
2. Map goja events to those rule IDs.
3. Generate programs involving nested `await`, rejection, `finally`, reentrancy, and host callbacks.
4. Execute them in both goja and the formal model.
5. Compare normalized event traces.
6. Attach an invariant:

   ```text
   every AwaitResume(frame, job)
   must be preceded by exactly one AwaitSuspend(frame, promise)
   and a PromiseReaction(job, promise)
   ```

7. On failure, save the minimal trace and source.
8. Export the trace as data for a Rocq or Lean checker.
9. Turn the minimized case into a regression test and, where appropriate, a corrected semantic rule.

That is the kind of tight loop currently requiring separate interpreters, hand-written logging, bespoke scripts, and proof-assistant work.

## 9. Proof-relevant traces

Ordinary traces say that an event occurred. A proof-relevant trace includes enough information for a small checker to validate why it was allowed.

A record might contain:

```go
type SemanticEvent struct {
    SchemaVersion uint32

    RunID      RunID
    Sequence   uint64
    Kind       EventKind

    ProgramID  ProgramID
    FunctionID FunctionID
    SiteID     SiteID

    SpecOperationID SpecOperationID
    FormalRuleID   FormalRuleID

    FrameID   FrameID
    JobID     JobID
    PromiseID PromiseID

    Observation Observation
    Witness     TransitionWitness
}
```

The witness should be bounded and avoid serializing the entire heap. Depending on the event it might contain:

- operand tags;
- selected primitive values;
- property descriptors;
- completion type;
- environment or store version IDs;
- causal predecessor IDs;
- a hash of a larger snapshot;
- the branch of a formal rule that was taken.

An independent checker could verify:

\[
C_i \xrightarrow{\ell_i} C_{i+1}
\]

for each recorded transition or for larger certified macro-steps.

This produces a certificate for **that execution**. It still does not prove a property for all executions. Universal proof requires symbolic reasoning, induction, abstract interpretation, model checking, or theorem proving over the program semantics.

## 10. A concrete architecture for academic use

### Semantic schema

The schema should define:

- event kinds;
- pre-state and post-state observation types;
- causal relationships;
- formal-rule identifiers;
- specification-version identifiers;
- whether the event is source-semantic, proof-oriented, or implementation-specific;
- whether events may be sampled or dropped.

For proof and conformance modes, dropping events must be impossible or explicitly invalidate the run.

### Semantic map

Compilation produces a map:

```text
source span
  ↔ AST node
  ↔ function / call-site / binding ID
  ↔ goja Program and PC interval
  ↔ ECMAScript abstract operation
  ↔ Redex/K/Rocq/Lean rule ID
```

This is the analogue of debug metadata plus a formal-semantics cross-reference.

### Probe IR

The restricted IR should support:

- typed primitive operations;
- event matching;
- bounded conditionals;
- frame-local state;
- typed maps;
- finite-state and bounded register automata;
- counters and histograms;
- bounded event emission;
- violations;
- no unrestricted recursion or allocation.

### Offline engine

The same trace format should be usable without rerunning the program:

```text
trace query
monitor replay
temporal checking
invariant mining
semantic coverage
causal graph generation
cost aggregation
trace comparison
proof-certificate checking
```

### Formal adapters

Adapters should export or import:

- Redex terms and reduction-rule IDs;
- K configurations and rule labels;
- Rocq or Lean inductive events and traces;
- SMT-LIB constraints;
- Datalog facts;
- Graphviz causal graphs;
- notebook-friendly Arrow or Parquet tables.

### Research-oriented command surface

For example:

```bash
# Produce a semantic trace.
goja-sem trace \
  --schema ecma-2026 \
  --probe contracts.sprobe \
  --output run.strace \
  program.js

# Compare implementation and reference-model traces.
goja-sem diff \
  --left goja:run.strace \
  --right kjs:model.strace \
  --normalize ecma-core

# Show semantic-rule coverage.
goja-sem coverage \
  --kind formal-rule \
  run.strace

# Mine likely entry/exit invariants.
goja-sem mine \
  --sites function-enter,function-return \
  --output candidates.smt2 \
  run.strace

# Check an offline temporal property.
goja-sem monitor \
  --property promise-lifecycle.qea \
  run.strace

# Export a counterexample to a proof assistant.
goja-sem export \
  --format rocq \
  --slice violation:17 \
  run.strace
```

## 11. A plausible research program

### Project A: semantics-preserving instrumentation

Formalize a JavaScript subset, its VM, and an observing probe machine. Prove:

- type safety and boundedness of probes;
- erasure;
- non-reentrancy;
- trace adequacy;
- monitor composition.

Evaluation would measure disabled overhead, attached no-op overhead, and trace fidelity.

### Project B: a semantic event ABI for ECMAScript

Design a versioned event vocabulary spanning:

- source semantics;
- completion records;
- calls and constructors;
- property operations;
- exceptions;
- generators;
- Promise jobs and async functions;
- host boundaries.

Validate it through differential traces against a specification-oriented interpreter and Test262.

### Project C: residual verification for dynamic JavaScript

Develop a contract or refinement language whose obligations are:

- statically proved;
- symbolically refuted;
- or compiled into verified probes.

The main theorem would connect the static proof, residual monitor, and concrete execution.

### Project D: programmable denotations

Give the event signature an interaction-tree or algebraic-effect semantics. Prove laws for handler composition, erasure, trace interpretation, and selected equivalences.

The practical result would be one analysis specification usable online, offline, symbolically, and abstractly.

### Project E: proof-aware semantics workbench

Build the double debugger, semantic trace comparator, rule-coverage explorer, and proof-assistant exporter. Evaluate it on the replication or extension of published JavaScript semantics.

The Redex experience suggests that the useful empirical question is not only whether a tool proves theorems, but whether it integrates cheaply enough into the normal workflow to expose mistakes early. citeturn190468search1turn190468search6

## 12. Critical limitations

Several boundaries should remain explicit.

**Observed runs are not universal proofs.** A passing monitor says that no violation was observed on those executions. Invariant mining produces likely invariants, not established invariants.

**The event mapping is part of the trusted base.** If `FunctionThrow` is emitted at the wrong place, a perfectly verified monitor proves facts about the wrong trace.

**Host semantics matter.** ECMAScript does not completely define browser, Node, or go-go-goja event-loop behavior. The host model must be represented separately from core language semantics.

**Native modules require contracts or models.** Unmodeled Go functions form semantic oracles. A proof must either assume their contracts or include them in the formal model.

**Dynamic compilation must be enrolled.** `eval`, `Function`, module loading, and generated code must receive semantic metadata and instrumentation before execution, or proof claims must exclude them.

**Instrumentation can perturb quantitative observations.** Wall-clock performance, scheduling, garbage collection, and allocation-sensitive behavior require careful experimental controls.

**Strong probes refine equivalence.** Exposing object identities, call counts, bytecodes, or allocation order makes more programs distinguishable.

**Single-run monitors do not cover arbitrary hyperproperties.** Relational security and equivalence claims need multiple traces or static proof. citeturn154629search0turn154629academia36

## 13. Recommended first semantics-oriented milestone

The first academic milestone should be deliberately narrower than full JavaScript:

1. Define a labelled operational semantics for calls, normal returns, throws, and constructors.
2. Implement corresponding goja events with stable function, call-site, and frame IDs.
3. Build a restricted read-only monitor IR with frame-local state.
4. Prove an erasure theorem for a small abstract machine or executable model.
5. Implement a normalized trace comparator between the model and goja.
6. Add semantic-rule coverage and counterexample minimization.
7. Build a three-pane debugger showing source, formal rule, and concrete VM event.
8. Only then add properties, proxies, generators, and asynchronous jobs.

That milestone is already publishable because it tests the central claim:

> A production interpreter can expose a stable semantic event interface that is low-overhead enough for routine use, precise enough for formal correspondence, and restricted enough for verified third-party analyses.

The larger opportunity is a **bidirectional semantics workbench**. Formal semantics would no longer be only a document or separate reference interpreter, and runtime instrumentation would no longer be only implementation-specific telemetry. The same event calculus would connect concrete execution, operational derivations, compositional denotations, abstract analyses, runtime monitors, and machine-checked proof artifacts.


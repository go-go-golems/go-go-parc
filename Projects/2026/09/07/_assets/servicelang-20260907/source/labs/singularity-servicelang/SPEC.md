# ServiceLang v0: executable host contract

Status: implementation contract for the first host-only vertical slice. The ticket's
long-form guides explain the architecture and theory; this document freezes the
initial executable surface. General protocol/server generation and MCU deployment
are not implied by completing this slice.

## Source and diagnostics

UTF-8 files use ASCII identifiers and `//` comments. Maximum source size is 64 KiB,
maximum parser nesting is 64, and declarations/locals are bounded to 256 per file or
function respectively. Diagnostics carry byte offsets, stable codes and the source
location of an earlier ownership transfer. Source rejection exits 1; CLI/tool errors
exit 2; success exits 0. The compiler never emits C++ for rejected source.

A module imports a closed native capability inventory with `use sensor;`,
`use memory;` and/or `use output;`. Unknown capabilities are rejected. Ordinary
functions cannot manufacture endpoints. The host supplies them as owned parameters.
Imports describe the trusted operations available to this module, not remote
cryptographic authority.

```
use sensor;
fn begin(own ready: Ready, now: Time) -> StartResult {
    return rpc_start(move ready, now, 8000);
}
```

Function syntax is `fn name(parameters) -> Type { statements }`. Parameters are
`name: CopyType` or `own name: ResourceType`. Statements are `let name = expression;`,
`name = expression;`, expression statements, `if expression { ... } else { ... }`,
`match expression { Variant(bindings) => { ... } ... }`, and `return expression;`.
`return;` returns Unit. Branch/match bodies are braced. No implicit shadowing.

Expressions include signed I32 literals, Bool literals, variables, `move variable`,
function/intrinsic calls, record field access and scalar comparisons (`==`, `!=`,
`<`, `<=`, `>`, `>=`). Arithmetic is through checked intrinsic results, not C++
signed-overflow expressions. Evaluation is left-to-right. No loops, recursion,
borrowing, raw pointers, arbitrary native includes/calls, partial moves, closures,
user-defined resource records, or dynamic loading. Unsupported declarations and
operators are errors, not ignored input. v0 exposes a fixed built-in record/variant
inventory rather than claiming a general user-defined data/protocol compiler.

## Value and resource inventory

Copyable: Unit, Bool, I32, Time (native uint64 microseconds), Sample (`value: I32`),
and CallResult (`Ok(Sample) | RemoteError(I32) | NotSent | Unknown | RuntimeFault(I32)`).

Resources:

- Buffer: an `sl::OwnedBuffer`.
- Ready and Pending: only the built-in SensorRPC client role, adapter ABI 1.
- Allocation: `Allocated(Buffer) | AllocFailed(I32)`.
- StartResult: `Started(Pending) | Rejected(Ready,I32) | Unavailable(I32)`.
- Continuation: `Reusable(Ready) | Lost(I32)`.
- PollResult: `Waiting(Pending) | Complete(CallResult,Continuation)`.
- Step: `Again(Pending) | Finished(Continuation)`.

All variants require exhaustive, nonduplicate matches. Resource-bearing variants
must be moved into a match and all resource payload fields must be accounted for.
Constructors are globally unique in this fixed inventory; argument types and move
requirements are checked. An owned aggregate is one owner until destructured into
the active arm's fields. Copyable aggregates can be copied.

## Ownership and control flow

Owned locals are uninitialized, live or consumed. A move/release consumes its
source. Reads of moved variables, implicit owner copies, live-owner overwrite and
unconsumed owners on a normal exit are errors. Explicit `move` is required at every
ownership-taking argument/return/match. A consumed source may be assigned a new
owner; stale references are not expressible.

The checker lowers to an acyclic CFG with explicit operation ordering and joins.
Only reachable successors contribute to a join. All incoming paths must agree on
whether each in-scope owner is live or consumed. Moved and released share the
consumed state, with separate diagnostic provenance. Branch-local resources must
be consumed before leaving that scope. Every reachable function path must return.
Function summaries come from checked signatures; recursive call cycles are rejected.

## Trusted intrinsics

- `rpc_start(move Ready, Time, I32 milliseconds) -> StartResult` (sensor).
- `rpc_poll(move Pending, Time) -> PollResult` (sensor).
- `close(move Ready) -> Unit` (sensor): deliberately retire the lease; no rebinding.
- `allocate(I32 bytes) -> Allocation` (memory): general slots only, bytes 0..128.
- `release(move Buffer) -> Unit` (memory).
- `length(Buffer) -> I32` (memory): restricted nonescaping read, not a first-class borrow.
- `observe(I32 outcome, I32 value) -> Unit` (output): bounded host observation sink.
- `add(I32,I32) -> Arithmetic`: `Number(I32) | Overflow`; checked widened addition.

Invalid deadline arguments are rejected before native start and return Ready.
Native Accepted transfers Pending; unexpected Invalid/Busy/IdExhausted retires the
wrapper and returns Unavailable. This conservative policy does not pretend every
native Invalid is recoverable. The host must provide a genuinely live Ready.
Waiting retains Pending. Terminal results preserve a reusable or lost continuation;
no branch manufactures Ready. Success payloads are checked for Sensor shape before
constructing Sample. Logical completion never releases a driver's TX allocation.

## Component plan contract

ABI-1 JSON plans declare one to four fixed SensorRPC/client instances and exactly
one component per instance. Each component names a declared exclusive endpoint,
checked begin/poll entry functions, authorities and general_slots. Entry signatures
are Ready,Time -> StartResult and Pending,Time -> Step. Unknown fields, duplicate
keys, duplicate owners, undeclared endpoints, wrong signatures/roles, missing
transitive intrinsic authorities and excessive buffer demand are rejected before
application emission. The allocation bound sums every branch/callee allocation
attempt, so it is conservative; each entry returns no Buffer-bearing value.

Generated application.hpp holds stable nonmovable frames and maps supplied host
Simulation references in instance order. Host Pool/Simulations must outlive it;
only the host advances the model. Frame admission additionally requires host
quiescence. A runtime acquisition failure publishes no application and retires
previously acquired leases rather than promising an unavailable transactional
rollback. Existing externally held leases are not consumed. This policy does not
rebind or arm radios. See README.md for the complete startup/failure contract.

## Backend and acceptance

Generate one C++17 header plus a metadata file under a new output directory's
`artifacts/` subdirectory. Write the complete artifact set to a staging directory,
reserve the fresh destination with an exclusive directory creation, then rename
the completed set atomically to `artifacts/`. An absent `artifacts/` is not a
published output. Refuse an existing destination (even empty) rather than risk
confusing stale and new generated code.
Only an opaque checked program can reach the emitter. Generated names are mangled,
source paths are escaped, runtime ABI is asserted, and argument temporaries make
ordering explicit. There is no unchecked IR import. `dump-ir` is inspection only.

The first host program calls generated begin/tick functions around the unchanged
`srpc::Simulation`. It compares outcomes, attempts, observations and quiescent pool
accounting with handwritten control under matching scenarios. Endpoint invalidation
is independently tested through the actual Client API. No GPIO, flash or serial
operation is part of this milestone. Parser/checker/backend correctness remains
trusted and tested, not formally proved.

## Phase gates

P0: freeze this contract and source fixtures. P1: parse/resolve/check copyable values.
P2: lower/control-flow ownership checks and compile-fail fixtures. P3: protocol
inventory, C++ emitter and runtime adapter. P4: generated execution and handwritten
simulation parity. P5: implement checked component startup wiring (fixed instances, endpoints,
authorities, resource counts and lifetime ordering), rejecting undeclared access
and publishing no partial application on invalid plans. This is required by the
original guide; the earlier v0 deferral was too narrow. P6: implement the requested
React/TypeScript/Redux Toolkit compiler visualizer with a left-side CodeMirror
editor and comparison presets, using the actual compiler API. P7: review optional
MCU integration, document actual APIs and limits, and audit commits/tests/prints.
General generated servers and MCU application mode remain optional decisions.

Validation cadence: use a small targeted fixture set for each changed compiler layer,
then one generated-C++ host integration suite. Do not repeat historical firmware
campaigns or add fuzzing/sanitizer infrastructure without a concrete failure or gap.
Documentation-only edits require documentation checks, not compiler/runtime reruns.

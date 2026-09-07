# ServiceLang

Host compiler for a small, explicitly owned language over the existing C++ RPC
runtime. See [SPEC.md](SPEC.md) for the executable language contract.

Implemented through P6: parser, resolver, fixed type/protocol inventory, finite
ownership CFG checker, checked-only C++17 emission, source maps, command-line
interface, generated Sensor/native simulation parity, checked component startup
wiring and an interactive compiler explorer.

## Use

Requires Go 1.23+; native examples require g++ with C++17. No external Go modules.
From this directory:

```sh
(cd compiler && go build -o /tmp/servicec ./cmd/servicec)
/tmp/servicec check examples/sensor.svc
/tmp/servicec dump-ir examples/sensor.svc
/tmp/servicec emit-cpp examples/ownership.svc --out /tmp/servicec-example
```

The destination must not exist. Complete outputs appear atomically under
`/tmp/servicec-example/artifacts/`:

- `generated.hpp`: functions in `svc_generated`, using fixed-width values,
  explicit optional ownership slots and ordered argument temporaries.
- `metadata.json`: source byte spans to emitted line ranges, source/implementation
  SHA-256 hashes, source-to-native function names and required adapter ABI.

Only a successful `Check` result reaches `EmitCPP`. `dump-ir` is inspection output,
not an input format. Source hash mismatches and nil/zero checked programs are
rejected. Exit codes: 0 success, 1 source rejection, 2 usage or tool/I/O error.
The CLI bounds source reading before parsing. Diagnostics use one-based lines and
byte columns; source maps use zero-based byte offsets and one-based native lines.

Native include paths are `runtime`, `../singularity-local/core/include` and
`../singularity-rpc/core/include`, plus the generated `artifacts` directory. Compile
with `-std=c++17 -Wall -Wextra -Wpedantic -Werror -fno-exceptions -fno-rtti -pthread`.
Generated function names prefix `fn` and encode each underscore as `_u`; use the
metadata function map rather than guessing names.

## Focused checks

```sh
cd compiler
go test ./internal/compiler -run TestFrontend
go test ./internal/compiler -run TestOwnership
go test ./internal/compiler -run 'TestEmissionGate|TestGeneratedOwnershipCPP'
go test ./cmd/servicec -run TestCLI
```

The native ownership check compiles and executes generated buffer allocation,
release and checked arithmetic. It skips if g++ is unavailable; such a skip is
not native acceptance evidence. The project completion build will require the
native toolchain explicitly. Do not repeat these checks for documentation-only
edits.

## Generated Sensor simulation

Run `make simulation` from this directory. `make check` is the host lab's local CI
entry point: simulation plus Go formatting, vet and tests. Neither command probes
hardware. Generated outputs and binaries live in ignored `build/` directories.

`host/simulation.cpp` saves four deterministic configurations (SF7, seed 13):
success, denied RF permission, 100% reply loss and a 1 ms logical deadline retaining
fake TX ownership. Each compares generated and handwritten native clients for
outcome, value, attempts, all simulation counters, completion time, number of steps,
cleanup iterations and Ready continuation. Both paths call Simulation::audit after
quiescence. A direct Client test covers recoverable rejection, NotSent/Lost and
Unknown/Lost after invalidation, and stale Ready producing Unavailable.

The generated path calls source `begin_for` and `tick`; the handwritten reference
calls ReadyClient::start and PendingCall::poll directly. No second endpoint owner
polls the generated Pending. Generated attempt accounting uses request-start
counters for these single-call scenarios; the native reference independently reads
the terminal Result.attempts. Simulation admission/completion tracing used only by
Simulation::call is not fabricated by either manually driven path.

These are model results, not RF measurements. In the short-deadline case, Unknown
returns with a reusable logical endpoint while fake TX remains busy; the host drains
three further steps before pool audit. Source completion does not release fake TX.

## Checked component startup

```sh
/tmp/servicec emit-app examples/sensor.svc examples/sensor.plan.json --out /tmp/servicec-app
make application
```

The JSON plan declares one to four fixed SensorRPC/client instances and exactly one
component owner for each. Component order and instance order may differ. Each
component selects checked `Ready,Time -> StartResult` and `Pending,Time -> Step`
functions and declares its `sensor`, `memory` and/or `output` authorities. The
checker follows all reachable user calls for required intrinsic authorities;
undeclared endpoint access, shared endpoint owners, wrong roles/signatures and
missing authorities are errors before publication. Unknown fields and duplicate
JSON keys are rejected.

`general_slots` is a conservative capacity declaration, not a separately enforced
runtime allocator quota. The checker sums allocate calls across all branches and
transitive callees of an entry, uses the larger begin/poll demand, and requires the
sum of component declarations to fit the pool's 12 general slots. This can reject
plans whose actual mutually exclusive paths would fit. There are no source loops,
recursion or Buffer payloads escaping these entry result types. Source allocation
failure remains explicit; native code outside the checked application is trusted
not to invalidate its capacity assumptions.

Successful emission adds `application.hpp` and a plan hash. The generated factory
maps host Simulation references in instance order to stable component frames.
Construct Pool/Simulations first and destroy the Application before them. The host
alone steps simulations; frames only call generated begin/tick functions. Admission
also checks host quiescence, rather than interpreting Ready as physical TX permission.

Invalid static plans emit nothing. Runtime factory validation rejects occupied
output, null/duplicate hosts, invalid mappings and insufficient available capacity
before acquiring leases. If a later native endpoint acquisition is unavailable,
no Application is published, but earlier acquired leases are retired by their
normal destructors. This is **fail-closed cleanup, not rollback**: those earlier
bindings are invalidated, never silently rebound. An already-held external endpoint
is left untouched. Native acquisition cannot be made an all-or-nothing lease
transaction through the current public API.

The native smoke test uses reversed endpoint order with success/NotSent hosts,
checks stable-frame completion and teardown audits, verifies duplicate-host denial
before acquisition, and demonstrates the documented fail-closed acquisition case.
This is checked local startup wiring, not authenticated radio authority or a
hardware deployment.

## Compiler Explorer

```sh
make serve                         # build + http://127.0.0.1:4786
# Or run the already-built single binary from any directory:
/path/to/build/serviceweb --addr 127.0.0.1:4786
```

The React/TypeScript frontend uses Redux Toolkit/RTK Query and CodeMirror. Presets
and the editable source/startup plan are on the left; the right side shows the
actual parser AST, typed CFG, stabilized ownership sets, diagnostics/provenance,
generated C++, validated startup wiring and embedded implementation source. Pin a
baseline and select the nearby negative mutation to compare results. Source-map
and diagnostic links select the corresponding editor range; UTF-8 byte spans are
translated into CodeMirror's UTF-16 offsets, including non-ASCII comments.

The HTTP API calls compiler.Inspect, which uses the same parser/lowering/solver as
Check and the same checked-only emitter. It never launches g++, executes emitted
code, accesses serial devices or arms RF. Rejected source/plans return diagnostics
and no native output. Facts on rejected paths are solver approximations, not valid
executions. Inspection is capped at 100,000 fact cells without skipping compiler
checks. Baselines retain their input/report snapshot; revision/request identities
prevent delayed responses from appearing current after edits. Stale results cannot
be pinned or used to jump into a newer source buffer.

Routes are standard net/http ServeMux: GET /api/presets, GET /api/implementation,
POST /api/analyze and the SPA. Source and plan are each limited to 64 KiB, requests
to 1 MiB; analysis concurrency is one and busy requests get 429. The server binds
loopback by default. It exposes only bundled implementation files, never arbitrary
host paths. API misses and missing assets do not fall back to HTML.

`make web` installs the frozen pnpm lockfile, invokes go generate, then builds the
always-embedded server. Generation builds the frontend and copies examples/native
headers into ignored embed directories. The standalone servicec CLI does not import
webui and can be built without frontend artifacts. For HMR, run the backend plus
`make dev-frontend`; Vite proxies /api to port 4786. `make check` now covers the
frontend build/type/format checks, Go vet/tests and native simulation/application
checks. No separate HTTP framework or Go dependency was added.

The local workbench bundles the editor grammars with React/RTK in one roughly
811 kB minified (263 kB gzip) JS asset. Vite reports its default size advisory; the
warning is not suppressed and no broader loading-performance claim is made.

## Ownership boundary

The compiler, adapter and native toolchain are trusted. The language has no raw
native-call escape and no generic wire protocol generation. Ready/Pending are the
fixed SensorRPC client role. Normal source paths must account for every owner;
this is not a proof about malicious native code or abrupt board resets.

The host must supply live endpoint parameters and keep the underlying Client/Pool
alive until all wrappers are destroyed. The Context is noncopyable/nonmovable;
its observation sink is bounded to 64 entries and explicitly counts dropped
observations. Native completion and endpoint continuation remain separate facts.
No wrapper is a radio driver, an RF grant, automatic rebinding or a competing
physical owner. No firmware or hardware validation is implied by host results.

# Formalizing Go concurrency

- URL: https://chatgpt.com/c/6a7b3b3e-6b0c-83ea-a82a-1747eb314786
- Created: 2026-08-11T15:10:38.310Z

---

> generating golang from coq proofs or lean proofs or so, or how to bridge actual go runtime behavior with more formal proofs and analysis mechanisms. Modelling in a formal tool is great but doesn't cover the actually important runtime concurrency behavior and little issues that arise there

There are two distinct problems here: **extracting executable Go from proofs** and **proving that hand-written Go obeys a formal model despite goroutines, channels, atomics, scheduling, and the Go memory model**. The second is usually the more useful path for real systems.

```json
{"system2_search_query":[{"q":"Goose Perennial Coq Go verification official paper Go semantics"},{"q":"Gobra Go verifier official documentation Viper"},{"q":"Coq extraction OCaml Haskell Scheme official documentation CertiCoq"},{"q":"Lean compiler C backend extraction code generation official documentation"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 21 websites**

</details>

The strongest existing bridge is not “Coq/Lean → Go.” It is closer to **Go → formal semantics → proof**: keep the implementation runnable as ordinary Go, translate a disciplined subset into the prover, then prove properties of that translated program. Goose/Perennial is specifically built around that architecture.

```json
{"open":[{"ref_id":"turn829631view0","lineno":185},{"ref_id":"turn829631search1"},{"ref_id":"turn829631search0"}],"system2_search_query":[{"q":"site:github.com/goose-lang/goose README unsupported channels goroutine mutex select Go subset"},{"q":"site:github.com/goose-lang/goose sync.Mutex goroutine atomic channels select"},{"q":"site:github.com/viperproject/gobra docs channels select mutex goroutine shared memory permissions"},{"q":"Go model checker goroutines channels Promela Spin official paper GitHub Gomela Go concurrency"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 12 websites**

</details>

For runtime fidelity, I would not try to formalize the Go scheduler itself unless scheduler behavior is part of the property. Most correctness properties should be stated against the **Go memory/synchronization contract**—happens-before from channels, mutexes, atomics, etc.—then checked again against real executions. The Go memory model explicitly defines those synchronization edges and warns that racy programs can have non-sequentially-consistent behavior.

```json
{"system2_search_query":[{"q":"site:go.dev testing/synctest Go official package 2026"},{"q":"site:go.dev/doc/articles/race_detector Go race detector official"},{"q":"site:pkg.go.dev/runtime/trace Go runtime trace official"},{"q":"site:go.dev/doc/security/fuzz Go fuzzing official"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Shaping a verified compiler**

I’m seeing a strong research direction: compiling proof-carrying specifications into Go while preserving observable behavior. I’d frame it as a small verified core, explicit runtime semantics, generated-code validation, and clearly separated trusted components.

**Shaped a verified compiler**

</details>

```json
{"system1_search_query":[{"q":"site:go.dev/doc/articles/race_detector.html data race detector only finds races executed official"},{"q":"site:go.dev/doc/security/fuzz Go fuzzing official tests coverage"},{"q":"site:go.dev runtime trace goroutine blocking unblocking official 2026"}],"response_length":"medium"}
```

<details><summary>💭 Thinking</summary>

**Designing a verification bridge**

Yes—direct Go extraction is uncommon, so I’d separate deterministic verified state transitions from a small Go runtime shell. I’d compare proof-producing extraction, Go verification, trace validation, and explicit scheduler assumptions rather than relying on generated code alone.

**Designed a verification bridge**

**Searched 2 websites**

</details>

Yes. The weak point in “prove a model, then implement it in Go” is exactly the refinement boundary. A proof of the abstract algorithm says little about a misplaced `close(ch)`, goroutine leak, forgotten cancellation path, non-atomic read, `select` behavior, or incorrect synchronization in the executable.

### Direct Coq/Lean → Go is not the best-supported route

Rocq/Coq's standard extraction machinery targets OCaml, Haskell, Scheme, and related representations rather than Go; CertiCoq provides a route toward C. Lean similarly has a native compiler pipeline that currently emits C and provides a C ABI for FFI, rather than an official Go backend. So a Lean/Rocq → Go generator is quite feasible, but unless you verify that generator, the generator becomes part of your trusted computing base. citeturn369572search6turn369572search13turn829631view3turn829631search2

For concurrent systems, I think the more interesting direction is the reverse one:

`actual Go source → formal semantics → proof`

**Goose + Perennial** does almost exactly this. Goose translates a deliberately restricted but runnable subset of Go into Rocq; Perennial then lets you reason about that program using Iris-style concurrent separation logic, including concurrent and crash-safe systems. The important detail is that the artifact being proved is derived from the Go implementation, rather than separately reimplementing the algorithm in the prover. Goose explicitly notes that its translator and Go semantics are trusted components, so it does not magically eliminate the refinement problem, but it shrinks it considerably. citeturn162992view0turn829631view1

There is also **Gobra**, which may actually be more immediately practical for normal Go. It is an automated verifier built on Viper that works on annotated Go-like source. Its concurrency logic covers goroutines, shared memory, mutexes, and channel communication, with permissions transferred through concurrency operations; verified programs get data-race-freedom guarantees along with user-specified functional properties. citeturn162992view1turn162992view5turn177430academia48

One project particularly close to what you're describing is **PGo**. It goes from Modular PlusCal to both model-checkable specifications and executable Go. More interestingly, it includes **TraceLink**, which checks implementation execution traces against the model. That's the architecture I would steal even if I didn't use PGo itself: formal model + executable implementation + runtime traces projected back into abstract model actions. citeturn162992view2

For channel-heavy code, **Gomela** takes another useful slice of the problem: extract an over-approximation of Go message-passing behavior into Promela and use SPIN for bounded model checking. That is much more suitable for finding deadlocks/protocol mistakes/interleaving failures than proving arbitrary functional correctness. citeturn177430academia45

### The architecture I'd use

I wouldn't generate the whole concurrent Go application from Lean or Rocq. I'd deliberately separate the mathematically clean part from the nasty runtime part:

1. **Prove a deterministic transition kernel.** Define something like `Step(state, input) -> (state', effects)` in Lean/Rocq. Prove invariants, state-machine safety, authorization rules, protocol transitions, etc. This part can reasonably be generated into Go, or kept behind an FFI boundary.

2. **Keep concurrency as a thin Go shell.** Goroutines, channels, mutexes, timers, contexts, disk/network calls and retries translate external events into calls to that kernel. The shell should contain as little application logic as possible.

3. **Define explicit linearization/model events.** Instead of trying to reproduce every goroutine instruction in the prover, instrument meaningful events such as `BeginRequest`, `AcquireLease`, `Commit`, `Send`, `Receive`, `Cancel`, `Timeout`. A real execution produces a trace; erase implementation details and ask whether the abstract model admits that trace. This gives you an executable refinement checker.

4. **Attack the concurrency shell separately.** Use Gobra or Goose where the code fits; use SPIN/Gomela for finite protocol interleavings; run the actual implementation under `-race`, different `GOMAXPROCS` values, failures and delays. `testing/synctest` is now a standard Go facility specifically for concurrent tests: it isolates groups of goroutines, virtualizes time, and lets a test wait until the goroutines are blocked. Runtime tracing also exposes goroutine creation, blocking/unblocking, syscalls, GC and scheduler activity, so you can correlate abstract events with what actually occurred. citeturn620188search7turn620188search0turn511884search1

5. **Treat proof and runtime validation as different guarantees.** The proof establishes “all executions permitted by semantics S satisfy invariant P.” Trace refinement establishes “this concrete execution corresponds to S.” Race detection/fuzzing/runtime instrumentation find places where your assumptions about S and the real binary don't line up. None substitutes for the others.

The last point matters particularly with Go. You generally **shouldn't model the specific Go scheduler**. Its scheduling order is deliberately not part of the language contract; the Go project has explicitly changed scheduling behavior in the past and noted that programs depending on scheduling order were erroneous. Instead, prove correctness under arbitrary allowed interleavings and the synchronization guarantees of the Go memory model. citeturn755928search3turn755928search2

That also exposes an important distinction:

`runtime implementation detail ≠ language semantics`

For example, whether a goroutine happens to be run immediately, which P's run queue it lands on, work stealing behavior, or when asynchronous preemption occurs should normally be irrelevant to correctness. The things you *do* want your model to capture are synchronization edges, channel semantics, atomic operations, mutex ownership, cancellation, external I/O ordering, and whichever fairness/liveness assumptions your algorithm genuinely needs. Go's memory model gives a DRF-SC-style guarantee to correctly synchronized programs, while racy programs can exhibit behavior that makes a simplistic sequential-interleaving model unsound. citeturn755928search2turn177430view2

So for something I wanted to deploy rather than publish as a verification exercise, I'd probably aim for:

```text
        Lean/Rocq
     specification
          │
      safety proofs
          │
   abstract transition
        semantics
       ↙       ↘
 generated/     runtime trace
 verified core  checker
       │           ↑
       └──── Go concurrency shell
               │
       Gobra / Goose / SPIN
               │
       race + synctest + trace
               │
          actual Go binary
```

That gets much closer to the real target: **not merely “the algorithm has a proof,” but “the binary is constrained by several independently checked links back to the proof.”**

And if I were experimenting with this specifically for Go, **PGo's trace-refinement idea + a Lean/Rocq-proved state-transition core + `testing/synctest`/runtime trace around the Go shell** is the combination I'd investigate first. It addresses the exact gap you're pointing at rather than pretending code extraction makes the runtime disappear. citeturn162992view2turn620188search0turn511884search1


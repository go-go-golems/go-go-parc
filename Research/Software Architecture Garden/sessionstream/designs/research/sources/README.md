# Sources for refinement-first verification of concurrent Go

This directory preserves the primary documentation snapshots used by
`02 - Constraining the Go Binary - Layered Refinement from Proved Kernels to Executables.md`.
The files were retrieved with Defuddle on 2026-08-11. `SHA256SUMS` records the exact archived bytes.

The archive separates three claims that must not be conflated:

1. proof about an abstract or translated semantics;
2. evidence that executable Go refines that semantics;
3. runtime diagnostics about one concrete execution.

## Source inventory

| File | Original source | Why retained |
|---|---|---|
| `01-rocq-program-extraction.md` | Rocq/Coq 8.20, “Program extraction.” <https://rocq-prover.org/doc/v8.20/refman/addendum/extraction.html> | Records the standard extraction targets and the extraction trusted boundary; establishes why direct Rocq-to-Go is not a standard supported route. |
| `02-certirocq-verified-compiler.md` | CertiRocq/CertiCoq project. <https://certicoq.org/> | Records the verified-compiler route from Gallina toward Clight/C and WebAssembly, useful for a proved deterministic core behind an FFI boundary. |
| `03-lean-foreign-function-interface.md` | Lean language reference, Foreign Function Interface. <https://lean-lang.org/doc/reference/latest/Run-Time-Code/Foreign-Function-Interface/> | Records Lean's C-ABI-based interoperability and the `extern`/`export` boundary; supports C/FFI integration rather than claiming an official Go backend. |
| `04-goose-go-to-rocq.md` | Goose repository README, archived near commit `3be88bbb4982f58e5813b6f0344302d5582c8e8a`. <https://github.com/goose-lang/goose> | Describes translating a runnable Go subset into Rocq/Coq semantics for Perennial proofs, and explicitly names the translator and semantics as trusted components. |
| `05-perennial-concurrent-crash-safe-verification.md` | Perennial repository README, archived near commit `aa4b4b61f9f564173b01a606360a7583910cd78f`. <https://github.com/mit-pdos/perennial> | Describes Iris-based verification of concurrent, crash-safe storage and distributed systems, including Goose-generated programs. |
| `06-gobra-tutorial.md` | Gobra tutorial, archived near repository commit `de3eba0198239cafcc2b7ba707e2442b782f21dc`. <https://github.com/viperproject/gobra/blob/master/docs/tutorial.md> | Records Gobra's annotated Go-like language, permissions, goroutines, shared memory, mutex/channel reasoning, and data-race-freedom guarantee. |
| `07-gobra-mutex-reasoning.md` | Gobra book, “Reasoning about mutual exclusion with sync.Mutex.” <https://viperproject.github.io/gobra-book/05/mutex.html> | Supplies the concrete invariant/permission-transfer pattern needed to assess the dispatcher admission mutex. |
| `08-pgo-modular-pluscal-to-go.md` | PGo repository README, archived near commit `401674a6901d6d306ce4ca22566880e876f2708f`. <https://github.com/DistCompiler/pgo> | Describes Modular PlusCal compilation to model-checkable TLA+ and executable Go; retained primarily for the design/implementation linkage architecture. |
| `09-tracelink-validating-program-traces.md` | “Validating Traces of Distributed Programs Against TLA+ Specifications,” arXiv:2404.16075. <https://arxiv.org/html/2404.16075v1> | Provides the direct precedent for projecting implementation traces into model actions and checking trace conformance against a TLA+ specification. |
| `10-gomela-go-to-promela-spin.md` | “Bounded verification of message-passing concurrency in Go using Promela and Spin,” arXiv:2004.01323. <https://arxiv.org/abs/2004.01323> | Describes over-approximating Go communication behavior as Promela for SPIN, targeting deadlocks and finite protocol/interleaving mistakes. |
| `11-go-blog-testing-concurrent-code-with-synctest.md` | Go Blog, “Testing concurrent code with testing/synctest.” <https://go.dev/blog/synctest> | Explains isolated goroutine bubbles, fake time, durable blocking, and deterministic waiting for concurrent tests. |
| `12-go-testing-synctest-package.md` | Standard library `testing/synctest` documentation. <https://pkg.go.dev/testing/synctest> | Records the exact current API and operational contract for virtual time and waiting until goroutines are durably blocked. |
| `13-go-runtime-trace-package.md` | Standard library `runtime/trace` documentation. <https://pkg.go.dev/runtime/trace> | Records scheduler/runtime trace events plus tasks, regions, logs, flight recorder, and `go test -trace`; useful for correlating abstract refinement events with runtime behavior. |
| `14-go-memory-model.md` | The Go Memory Model. <https://go.dev/ref/mem> | Supplies the DRF-SC guarantee and precise synchronization edges for channels, close, mutexes, atomics, and goroutine creation. This is the semantic contract the refinement argument should use instead of scheduler folklore. |
| `15-go-1-5-scheduler-change-guidance.md` | Go 1.5 release notes. <https://go.dev/doc/go1.5> | Records the explicit warning that scheduler order was never language-defined and programs depending on it were erroneous; supports arbitrary-interleaving models rather than scheduler-specific models. |
| `16-grove-separation-logic-distributed-systems-sosp23.pdf` | Grove SOSP 2023 paper, linked from Perennial. <https://pdos.csail.mit.edu/papers/grove:sosp23.pdf> | Demonstrates Perennial/Grove separation-logic verification of distributed systems and the scale of the proof architecture beyond one in-memory concurrent object. |
| `17-vmvcc-multiversion-concurrency-control-osdi23.pdf` | vMVCC OSDI 2023 paper, linked from Perennial. <https://pdos.csail.mit.edu/papers/vmvcc:osdi23.pdf> | Concrete verified high-performance concurrency-control case study using the Perennial program framework. |
| `18-goose-verifying-concurrent-go-code-coqpl20.pdf` | “Verifying concurrent Go code in Coq with Goose,” CoqPL 2020, linked from Perennial. <https://www.chajed.io/papers/goose:coqpl2020.pdf> | Short primary description of Goose's Go-to-Coq approach, directly relevant to proving an implementation-derived term rather than a separate model. |
| `19-tej-chajed-phd-thesis.pdf` | Tej Chajed, PhD thesis, linked from Perennial. <https://www.chajed.io/papers/tchajed-thesis.pdf> | Chapter 7 gives the fuller Goose/Perennial account, including semantics and verified-systems methodology. |
| `20-waddle-proven-go-semantics-meng-thesis.pdf` | Sydney Gibson, “Waddle: A proven interpreter and test framework for a subset of the Go semantics,” MEng thesis, linked from Perennial. <https://pdos.csail.mit.edu/papers/gibsons-meng.pdf> | Directly relevant to shrinking the trusted Go-semantics boundary and validating Goose translations/interpreters. |
| `21-gojournal-verified-concurrent-crash-safe-osdi21.pdf` | GoJournal OSDI 2021 paper, linked from Perennial. <https://www.chajed.io/papers/gojournal:osdi2021.pdf> | End-to-end example of verified concurrent, crash-safe Go-derived implementation using Perennial. |
| `22-gotxn-crash-safe-concurrent-transactions-meng-thesis.pdf` | Mark Theng, “GoTxn: Verifying a Crash-Safe, Concurrent Transaction System,” MEng thesis, linked from Perennial. <https://pdos.csail.mit.edu/papers/mtheng-meng.pdf> | Detailed proof engineering for concurrency + crash safety atop Perennial/Goose. |
| `23-perennial-concurrent-crash-safe-sosp19.pdf` | Perennial SOSP 2019 paper, linked from Perennial. <https://www.chajed.io/papers/perennial:sosp2019.pdf> | Original Perennial framework and recovery-logic foundations; README warns the current codebase has evolved substantially from this version. |
| `24-pgo-compiling-distributed-system-models-asplos23.pdf` | PGo ASPLOS 2023 paper, repository copy. <https://raw.githubusercontent.com/DistCompiler/pgo/main/doc/papers/asplosb23main-p12-p-e73de3693c-62943-final.pdf> | Primary architecture/evaluation of Modular PlusCal compilation to TLA+ and executable Go. |
| `25-tracelink-validating-program-traces-arxiv.pdf` | TraceLink paper, arXiv:2404.16075. <https://arxiv.org/pdf/2404.16075> | PDF companion to the archived HTML; formalizes constrained model checking of partial implementation traces against TLA+. |
| `26-gomela-go-promela-spin-arxiv.pdf` | Gomela paper, arXiv:2004.01323. <https://arxiv.org/pdf/2004.01323> | Full paper for Go message-passing extraction, bounded parameters, Promela encoding, and SPIN verification. |
| `27-certicoq-cps-to-c-compiler-paper.pdf` | CertiCoq CPS-to-C compiler paper, linked from the CertiRocq project page. <https://www.cs.princeton.edu/~appel/papers/CPStoC.pdf> | Primary compiler-design evidence for translating verified Gallina/CPS programs toward C/Clight rather than directly to Go. |

## Retrieval and revision method

All web pages, rendered GitHub READMEs/tutorials, and arXiv HTML/abstract pages were archived with:

```bash
defuddle parse <url> --md
```

Line endings and trailing horizontal whitespace were normalized. If Defuddle returned a single long line, it was rewrapped with `fold -w 110 -s` per the Defuddle skill's known-output workaround.

Repository HEAD revisions were recorded with `git ls-remote <repository> HEAD` on 2026-08-11. They identify the repository state near retrieval time; the archived rendered page and its SHA-256 are the retained evidence.

PDF papers and theses linked from the Perennial and PGo project pages, plus the TraceLink and Gomela arXiv pages, were downloaded directly with `curl -fL`. Every retained `.pdf` was checked with `file` and required to identify as a PDF document before checksums were generated.

## Integrity check

From this directory:

```bash
sha256sum --check SHA256SUMS
```

## Scope and rights

These are private research snapshots. Copyright and redistribution rights remain with the original authors and publishers. Follow each source's license and terms before redistributing the archive.

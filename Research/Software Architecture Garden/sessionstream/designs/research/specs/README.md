# Verification artifacts for the Bounded Asynchronous Observer Dispatcher

Companion to
[[Research/Software Architecture Garden/sessionstream/designs/research/01 - Proving the Bounded Asynchronous Observer Dispatcher|01 - Proving the Bounded Asynchronous Observer Dispatcher]].

All artifacts are self-contained and reproducible with the commands below
(expected tool versions in parentheses).

## tla/ — TLA+ concurrent model (TLC 2.19)

```
cd tla
java -jar ~/Downloads/tla2tools.jar -config DispatcherGuarded.cfg   -workers 4 -cleanup Dispatcher.tla
java -jar ~/Downloads/tla2tools.jar -config DispatcherUnguarded.cfg -workers 4 -cleanup Dispatcher.tla
```

- Guarded: all 12 invariants + `Termination` + `ClosingSticky` hold
  (118,771 distinct states, depth 39, ~25 s).
- Unguarded (`Guarded = FALSE`): TLC reports a `NoSendAfterClose`
  counterexample at depth 7 (close, then submit sends on the closed queue).
- Captured output: `results/guarded.txt`, `results/unguarded.txt`.

## alloy/ — Alloy 6 temporal model (org.alloytools dist, SAT4J)

```
cd alloy
javac -cp ~/Downloads/org.alloytools.alloy.dist.jar RunAlloy.java
./run_all.sh        # parallel per-command runs, writes results/
```

- Guarded: 8 assertions hold within scope (4 Item, 1 Flag, 6 seq, 10 steps);
  `ExampleLifecycle` produces a witness at 14 steps.
- Unguarded (no closing guard): `NoEnqueueAfterClose` AND `DrainComplete`
  counterexamples — post-exit submissions land in a queue nobody drains.
- `RunAlloy.java` is a minimal headless command runner
  (`java -cp .:alloy.jar RunAlloy <file.als> [labelPrefix]`).

## coq/ — Coq 8.20 mechanized proofs (Coq Platform CP.2025.08.0~8.20)

```
cd coq
eval $(opam env --switch CP.2025.08.0~8.20~2025.01)
coqc Dispatcher.v
```

All seven exported theorems print `Closed under the global context`
(axiom-free). Log: `results/build.txt`.

## lean/ — Lean 4 (4.33.0) mechanized proofs

```
cd lean
~/.elan/bin/lean Dispatcher.lean
```

All seven theorems report axioms `[propext, Quot.sound]` only (no
`Classical.choice`, no `sorryAx`). Log: `results/build.txt`.

## go/ — executable scaffold: dispatcher, oracle, tests, fuzzer, mutations

```
cd go
go vet ./...
go test ./... -count=1                              # deterministic + stress + turnstile
go test -race -count=20 -timeout 300s ./...         # race repetitions
go test -race -run FuzzDispatcherOps -count=1 .     # fuzz seeds under -race
go test -fuzz=FuzzDispatcherOps -fuzztime=45s .     # campaign (3.3M execs PASS)
./mutate.sh                                         # 5 mutations, all caught
```

Results: `results/fuzz_campaign.txt`, `results/mutations.txt`.

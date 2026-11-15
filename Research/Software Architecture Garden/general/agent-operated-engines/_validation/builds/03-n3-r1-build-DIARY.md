# Diary

## Goal

Build `gridflow`, a lazy, hash-consed, content-keyed computation graph over small 2D float grids, applying the
content-keyed lazy graph pattern of `CHAPTER.md`, and record each phase of the work here.

## Step 1: Reading the chapter, the task and the diary format; design

I read `CHAPTER.md`, `TASK.md` and `DIARY-FORMAT.md` in full, then fixed the module layout and the participant
mapping before writing any code. The task's required interface (Engine, op, source, Node.call, evaluate, runs,
stats, within, demo_engine) maps one-to-one onto the chapter's participants, so the design was mostly deciding which
chapter note belongs in which object and where the two ambiguities are (`runs` under the identity short-cut, and
whether the run memo or the value cache owns warning replay).

### Prompt Context

**User prompt (verbatim):** "You are a software engineer joining a project. Your working directory contains three
files: CHAPTER.md: a chapter of a design-pattern book describing the pattern you must apply; TASK.md: the software
to build, with its required public interface; DIARY-FORMAT.md: how to keep your work diary. Read all three
completely first. Keep DIARY.md as you go, one step per phase of work, in that format. Then design, build and test
the software in this directory. Work only inside this directory (do not read or write outside it). Use only the
Python 3 standard library. Run your tests and fix what fails before you finish, and make sure DIARY.md is complete.
Your final message must follow the output format at the end of TASK.md."

**Assistant interpretation:** Implement the pattern from the chapter as a small Python library whose public surface
is exactly the one TASK.md lists, with tests and a truthful diary, and finish with the JSON report TASK.md defines.

**Inferred user intent:** A working, honest reference implementation of the pattern that an evaluator can test
against the stated interface, including the hard parts (interning, content keys, quantised scale, function
arguments as subgraphs, frozen values, warning replay, byte-budgeted eviction).

### What I did
- Read all three documents completely; noted the interface list in `TASK.md` and the participant table in
  `CHAPTER.md` §Structure.
- Decided the module split: `gridflow/errors.py` (E_ARG / E_PLACEHOLDER / E_EVAL codes), `canonical.py`
  (canonical form + refusal), `grids.py` (freeze / thaw / byte size), `node.py` (Node, Result), `cache.py`
  (byte-budgeted LRU), `engine.py` (registry, builder, evaluator, within), `demo.py` (add/gain/blur/threshold),
  and `__init__.py` exporting the public names.
- Decided the key shape: node digest = SHA-256 of (op name, canonical args, input digests); signature = SHA-256 of
  (node digest, op version, quantised params, input signatures). Version deliberately *not* in the node digest so a
  re-registered operation keeps the same nodes but misses the old cache entries.

### Why
- §Structure's participant table drives the module split: Node + Builder + Source + Signature + Evaluator +
  Run memo + Value cache. In-flight group is omitted because there is one caller and no async runtime
  (note 9: "Share in-flight work only when there are concurrent callers").
- Note 1: interning at build time and refusing non-canonical arguments is a builder responsibility, so `canonical`
  is called inside `_build`, never inside `evaluate`.
- Note 2: quantisation must happen at the request boundary, and the *quantised* value must be what the operation
  sees through `ctx.scale`, otherwise a value is stored under another key.

### What worked
- The chapter's sketch translated almost mechanically into the interface: `request`, `signature`, `evaluate`,
  `intern`, `substitute` all have a direct method counterpart.

### What didn't work
- Nothing to run yet in this step; no commands executed beyond `ls` and `python3 --version` (3.10.3).

### What I learned
- The interface has no `await` and no `look()`: `evaluate` is the single evaluation point, which makes note 11
  trivial here (one call, and building a node can never run an operation).
- `TASK.md` does not say whether `runs()` counts a neutral call. The chapter's identity short-cut skips `op.run`
  entirely, so I chose "the operation actually ran" to mean the function was invoked, and will document it.

### What was tricky to build
- Nothing yet; the open question is warning replay (note 8): a cache hit must replay the warnings of the whole
  subgraph below it, so the entry must store accumulated warnings, while within one request a warning must appear
  once. Design: `_Request` keeps `sig -> warnings` (so a parent can absorb its inputs' warnings) plus a `reported`
  set (so the caller sees each distinct warning once per `evaluate`).

### What warrants a second pair of eyes
- Whether "no canonical form" should raise `ArgumentError` (my choice) or `TypeError`; `TASK.md` only names
  `EvalError`, so the builder error type is a guess that must not break the specified surface.
- Whether `runs()` should be 0 or 1 for `gain(k=1)`.

### What should be done in the future
- Consider an `in_flight` group and parallel input evaluation only if a concurrent API is ever added.

### Code review instructions
- No code yet. When it exists: start at `gridflow/engine.py::Engine._build`, `_signature`, `_evaluate_node`,
  `_substitute`; run `python3 -m unittest discover -s tests`.

## Step 2: Core modules — errors, canonical form, grids, node, cache

I wrote the five leaf modules first so that the engine could be written against them: error codes, the canonical-form
refusal, freeze/thaw and byte sizing, the Node/Result value types, and the byte-budgeted LRU value cache. None of
them knows about evaluation, which kept the engine free to be the only place where keys, warnings and freezing meet.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Implement the pattern's value types and refusal rules before the engine, so the
engine's code reads like the chapter's sketch.

**Inferred user intent:** A codebase where each participant in the chapter's Structure table is a real, findable
object, not one monolith.

### What I did
- `gridflow/errors.py`: `GridflowError` base with a `code`, and `ArgumentError` (E_ARG), `UnknownOperation`,
  `NotANodeError`, `EvalError` (E_EVAL), `PlaceholderError` (E_PLACEHOLDER, an `EvalError`).
- `gridflow/canonical.py`: `canonical(x)` with one spelling per value (1 == 1.0, sorted mapping keys, JSON text for
  strings), refusing functions/handles/opaque objects with E_ARG; `canonical_args`; `quantize(scale)`.
- `gridflow/grids.py`: `freeze` (tuple of tuples of floats, rejects ragged/non-numeric/empty), `thaw`, `shape_of`,
  `nbytes_of`, `content_hash`.
- `gridflow/node.py`: `Node` with `__slots__`, an identity `__setattr__` that refuses writes, `hash`/`digest`,
  `call()` going back through the builder, and `__getattr__` raising an `E_NOT_AWAITED`-style message for property
  reads; `Result` with `.value` and `.warnings`.
- `gridflow/cache.py`: `Entry(value, warnings, nbytes)` and `ValueCache`: LRU `OrderedDict`, evict *before* insert,
  refuse entries larger than the whole budget, counters for hits/misses/evictions/bytes.

### Why
- Note 1 (refuse what has no canonical form at build time) lives in `canonical.py` so the builder cannot forget it.
- Note 7 (store values frozen, copy only where a value leaves the graph) is split between `grids.freeze` and the
  single `thaw` call in `Engine.evaluate`.
- Note 10 ("a size-aware policy must evict before inserting, or it can evict the value it was asked to store") is
  why `ValueCache.put` calls `_evict_until(entry.nbytes)` before inserting, never after.

### What worked
- Putting the byte size in the cache entry rather than recomputing it on eviction made the budget accounting exact.

### What didn't work
- Nothing failed in this step; no tests existed yet.

### What I learned
- `Node.__getattr__` has to re-raise `AttributeError` for underscore names or `copy`/`pickle`/`hasattr` probes
  recurse; I special-cased names starting with `_` to avoid it.

### What was tricky to build
- Freezing has to reject a ragged grid *and* accept tuples of ints; the width check is remembered per row rather
  than computed from row 0 so the error message can name the offending row.

### What warrants a second pair of eyes
- `ValueCache.put` returning False for an oversized entry is how "reports its warnings immediately" (note 8) is
  triggered; a reviewer should check that no other path can silently drop warnings.

### What should be done in the future
- A second cache policy (GreedyDual-Size) as a setting, per note 10; the `ValueCache` interface is ready for it.

### Code review instructions
- Read `gridflow/cache.py` first (small, self-contained), then `gridflow/canonical.py`. Validate with
  `python3 -c "import gridflow as gf; print(gf.canonical({'b':1,'a':2}))"`.

## Step 3: The engine — builder, signature, evaluator, within; demo operations

I wrote `gridflow/engine.py` as the four collaborating pieces (registry + builder + evaluator + cache) and
`gridflow/demo.py` with `add`, `gain`, `blur`, `threshold`, then smoke-tested by hand before writing any test file.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Write the builder (intern, refuse), the signature function, the evaluator (memo,
cache, identity short-cut, freeze, store), and the function-argument machinery (`within` + `substitute`).

**Inferred user intent:** The pattern's Collaborations section, working, behind exactly the interface TASK.md lists.

### What I did
- `Engine.__init__(cache_bytes=10_000_000)` holds the op registry, the interned node table, per-node run counters,
  the source store and the `ValueCache`; it registers the two internal operations `__source__` and `__within__`.
- `_build`: looks up the record, checks every input is a node of this engine, fills declared defaults, canonicalises
  the arguments (refusing E_ARG), then `_intern`.
- `_intern`: SHA-256 over `[op name, canonical args, input digests]`; returns the existing node if the digest is
  known. Version deliberately excluded, so re-registering an operation keeps the nodes and misses the cache.
- `_signature`: SHA-256 over `[node digest, op version, quantised params, input signatures]`, memoised per request.
- `_evaluate_one`: run memo, then cache (reporting stored warnings), then the identity short-cut (returns the
  input's frozen value, not cached), then compute with a `Context` that collects warnings, freeze, store.
- `within`/`_substitute`: build against a placeholder, substitute the receiver through the subgraph, re-interning
  each node on the path; memoised per node digest.
- Hand smoke test: chain build/evaluate, cache hit, `within` masking, and node identity across two spellings of the
  same call all behaved as expected (e.g. `src.call('gain', k=2) is src.call('gain', k=2.0)` → True).

### Why
- Note 6: the placeholder must never reach the evaluator, so `_record` raises `PlaceholderError` for it and
  `_substitute` re-interns so `within(mask, p => p.gain(k=2))` shares the node `img.gain(k=2)`.
- Note 2: `quantize` is applied in `evaluate` and the quantised value is what `Context.scale` carries, so the
  computation and the key cannot disagree.
- Note 8: the entry stores the *whole subgraph's* warnings, because a hit on a node serves none of its inputs.

### What worked
- Interning by digest made "two sources with equal content are the same node" fall out for free once `source` hashed
  the grid content into the node's arguments.

### What didn't work
- Dropped the in-flight group deliberately (note 9: only worth it with concurrent callers) and recorded that
  decision in the module docstring rather than leaving it unexplained.

### What I learned
- Warning replay has two independent needs — accumulate down the graph for storage, deduplicate across a request
  for reporting — and one dict cannot do both; `_Request` keeps `warnings_for` (per signature) and `reported`.

### What was tricky to build
- `runs()` under the identity short-cut: the operation's function is never called, so the counter stays at 0. I chose
  to read TASK.md's "actually ran" literally and documented it in the method docstring.

### What warrants a second pair of eyes
- Whether `EvalError` from a child should be re-raised unchanged by the parent (my choice) or wrapped with the
  parent's name as well.

### What should be done in the future
- An explicit release rule for the node table and the source store (note 10); for now `nodes_built()` exposes the
  growth and nothing frees it, which is fine for one session.

### Code review instructions
- `gridflow/engine.py`: `_build`, `_intern`, `_signature`, `_evaluate_one`, `within`, `_substitute`.

## Step 4: Tests written, first full run: 4 failures

I wrote five test modules covering building, evaluating, the cache, `within` and the demo operations, then ran the
whole suite once.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Prove the pattern's promises with tests: interned nodes, laziness, cache hits across
"rounds", quantised scale, refused arguments, frozen values, warning replay, eviction, run memo.

**Inferred user intent:** Tests that would catch a cache serving a stale or shared value, not just happy-path checks.

### What I did
- `tests/test_build.py`, `tests/test_evaluate.py`, `tests/test_cache.py`, `tests/test_within.py`, `tests/test_demo.py`
  (94 tests at this point), using a local `CountingEngine` helper that registers counting/warning/combine/boom ops.
- Ran `python3 -m unittest discover -s tests`.

### Why
- One test per promise in TASK.md plus the chapter notes that are easy to get wrong (notes 1, 2, 6, 7, 8, 10).

### What worked
- 90 of 94 passed on the first run; the failures were all in my expectations, not in the engine.

### What didn't work
- `python3 -m unittest discover -s tests` → `Ran 94 tests in 0.010s / FAILED (failures=3, errors=1)`:
  - `ERROR: test_blur_radius_shrinks_with_the_scale ... gridflow.errors.UnknownOperation: no operation is
    registered under the name 'blur'` (that test used the counting engine, which has no demo ops).
  - `FAIL: test_a_value_larger_than_the_budget_is_not_cached ... AssertionError: 88 != 0` (the 1-cell source does
    fit in a 100-byte budget; only the 20x20 value was refused).
  - `FAIL: test_operations_are_deterministic_and_composable ... AssertionError: Lists differ: [[0.0, 0.0], [1.0,
    1.0]] != [[0.0, 1.0], [1.0, 1.0]]` (my arithmetic: (2+1) is not > 5).
  - `FAIL: test_second_program_shares_the_first_programs_work ... AssertionError: Lists differ: [[3.0, 3.0]] !=
    [[3.0, 4.0], [3.0, 4.0]]` (a 1x2 grid blurs to a 1x2 grid of 3.0, not a 2x2 one).

### What I learned
- Four of four failures were wrong expectations; that is a good sign for the engine but a reminder to compute
  expected grids by hand rather than by intuition.

### What was tricky to build
- Nothing structural; the fixes were arithmetic and engine choice (use `gf.demo_engine()` where `blur` is needed).

### What warrants a second pair of eyes
- The tests that assert exact `stats()` counters are coupled to when the source node is cached; they may be brittle
  if the cache policy changes.

### What should be done in the future
- Add a randomised property test comparing cached results against freshly built engines.

### Code review instructions
- `python3 -m unittest discover -s tests -v`; start with `tests/test_cache.py::WarningTests`.

## Step 5: Fixes — expectations, then two real robustness fixes

I fixed the four wrong expectations, then went looking for behaviour the chapter asks for that I had not applied:
defaults filled before hashing (note 1) and a raw-grid mask for `within`, and finally a real limit I found by
probing: deep chains.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Turn the red run green, and close the gaps between my first cut and the chapter's
notes rather than just the failing assertions.

**Inferred user intent:** A library that behaves correctly on the ugly inputs, not only on the tests I wrote first.

### What I did
- Fixed the four test expectations; suite went to 96 tests, all passing.
- Note 1 gap fixed: `Engine.op(..., defaults={...})` (an extra optional keyword, so the required signature is
  unchanged) fills defaults in `_build` before hashing, and `demo_engine` declares them, so `src.call("gain")` and
  `src.call("gain", k=1)` are one node. Two tests added.
- `within` now accepts a raw 0/1 grid as well as a node for `mask` (coerced through `source`); one test added.
- Found with `python3 -c "...900 nested .call('add', k=1)..."`:
  `RECURSION FAIL maximum recursion depth exceeded while calling a Python object`.
- Rewrote `_signature` and the evaluator to walk the graph iteratively in post-order (`_postorder`, `_signature`,
  `_evaluate`, `_evaluate_one`), so the call stack no longer grows with the graph's depth.

### Why
- Note 1: "Hash the bound arguments in canonical form (defaults filled, units declared), or two spellings of the same
  call become two nodes."
- The recursion failure is the classic consequences-table problem ("the budget bounds values, not the graph"): the
  graph is a data structure and should be traversed, not recursed.
- Post-order traversal also made the run memo's guarantee obvious: every input's value is in the request's memo
  before a node is computed, which is exactly what note 9's absent in-flight group would otherwise have to provide.

### What worked
- After the rewrite, a 2000-link chain evaluates and re-evaluates from the cache (`runs` stays 1); the whole suite
  still passed unchanged, which suggests the refactor was behaviour-preserving.

### What didn't work
- `python3 -m unittest discover -s tests` → `FAILED (errors=1)` with
  `gridflow.errors.EvalError: __within__: mask is (3, 6) but the grid is (6, 6)` in my new scenario test — a mask I
  built with `[[1.0] * 6] * 3`; fixed to six rows. Then `Ran 103 tests ... OK`.

### What I learned
- The chapter's "run memo" row (only when the cache may evict) is not optional in practice: with `cache_bytes=0` the
  diamond in my test would compute the shared input twice without it. I test that explicitly now.

### What was tricky to build
- Iterative post-order with a diamond graph: a node can be pushed twice before it is seen, so the `seen`-on-pop
  guard and the `(node, expanded)` marker must both be right; the tests for shared subgraphs inside one request
  (diamond value and single run) are what pins it down.

### What warrants a second pair of eyes
- `_evaluate` returns the value produced for the last node in post-order, relying on the root being last; an
  assertion or a dictionary lookup would make that invariant explicit.

### What should be done in the future
- Convert the post-order result to an explicit topological worklist with an assertion on the root.

### Code review instructions
- `gridflow/engine.py::_postorder`, `_signature`, `_evaluate`, `_evaluate_one`; run
  `python3 -m unittest discover -s tests` and `python3 -c "import gridflow as g; e=g.demo_engine(); n=e.source([[1.0]]);
  [None for i in range(2000) if not (n:=n.call('add', k=1))]"` -- or `tests/test_scenario.py::DepthTests`.

## Step 6: Final check — full suite, hostile calls, cleanup

I re-ran the whole suite under a warnings-as-errors flag, probed a handful of odd-but-legal calls by hand, removed
the `__pycache__` directories and confirmed the tree. Nothing in the source changed in this step.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** A last pass that both runs the required command and looks for behaviour the tests do
not express, then leave the directory clean and the diary complete.

**Inferred user intent:** A submission whose reported test result is the last thing that actually ran.

### What I did
- `find . -name "__pycache__" -type d -exec rm -rf {} +; python3 -m unittest discover -s tests` →
  `Ran 103 tests in 0.028s / OK`.
- `python3 -W error::DeprecationWarning -m unittest discover -s tests` → `Ran 103 tests in 0.029s / OK`.
- Hostile pass on a 50-byte budget: a blur whose radius exceeds the grid returns the global mean with one warning;
  an `inf` radius is refused at build time with `ArgumentError: arguments: inf has no canonical form`; `scale=0`
  raises `ValueError: scale must be in (0, 1], got 0`; evaluating another engine's node raises `NotANodeError`;
  `gain(k=1)` returns silently with `runs == 0`.
- Removed `__pycache__`; final tree is `CHAPTER.md`, `DIARY.md`, `DIARY-FORMAT.md`, `TASK.md`, `gridflow/` (8 modules),
  `tests/` (6 modules).

### Why
- TASK.md requires the tests to be run and to pass, and the diary to be complete; `-W error::DeprecationWarning`
  guards against anything that would break on a newer Python.

### What worked
- Everything passed without changes; the earlier refactor to post-order evaluation did not alter results.

### What didn't work
- Nothing failed in this step.

### What I learned
- A cache smaller than a single value reports warnings immediately and stores nothing (`bytes == 0`,
  `evictions == 0`), which is the behaviour note 8 asks for at the boundary; it is comforting that it needed no
  special case, just `ValueCache.put` returning False.

### What was tricky to build
- Nothing; the last step was verification only.

### What warrants a second pair of eyes
- The pattern's "budget bounds values, not the graph" limitation is real here: nothing evicts `Engine._nodes` or
  `Engine._sources`, so a long session grows without bound by design. A reviewer should decide whether a release
  rule is wanted before this is used beyond one session.
- `Engine.stats()` counters are cumulative and cannot be reset, so tests asserting exact numbers depend on the
  order of requests.

### What should be done in the future
- Node/source release rule (note 10) and a second cache policy (note 10); optionally a persistent cache (Variations)
  once keys carry a content hash of sources, which they already do for sources.

### Code review instructions
- Start at `gridflow/engine.py` (`_build`, `_signature`, `_evaluate_one`, `within`, `_substitute`), then
  `gridflow/cache.py`. Validate with `python3 -m unittest discover -s tests` (expect `Ran 103 tests ... OK`) and spot
  check `tests/test_scenario.py` for the motivating rounds.

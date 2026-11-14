# Diary

## Goal

Build `gridflow`, a lazily evaluated, content-keyed graph engine for small 2D float grids, applying the
Content-Keyed Lazy Graph pattern of `CHAPTER.md`; this diary records the design, each build step, the test runs and
the fixes.

## Step 1: Reading the chapter, the task and the diary format; designing the engine

I read `CHAPTER.md` (Content-Keyed Lazy Graph), `TASK.md` (the `gridflow` public interface) and `DIARY-FORMAT.md`
completely, then sketched the design before writing any code: an interned `Node` identified by a SHA-256 of
operation name + canonical arguments + input hashes, a `Signature` that adds the operation version, the quantised
evaluation scale and the input signatures, a per-request run memo, a byte-budgeted LRU value cache, an in-flight
group for single-flight, and a build-time placeholder substitution for `within`.

### Prompt Context

**User prompt (verbatim):** "You are a software engineer joining a project. Your working directory contains three
files:
- CHAPTER.md: a chapter of a design-pattern book describing the pattern you must apply;
- TASK.md: the software to build, with its required public interface;
- DIARY-FORMAT.md: how to keep your work diary.
Read all three completely first. Keep DIARY.md as you go, one step per phase of work, in that format. Then design,
build and test the software in this directory. Work only inside this directory (do not read or write outside it). Use
only the Python 3 standard library. Run your tests and fix what fails before you finish, and make sure DIARY.md is
complete. Your final message must follow the output format at the end of TASK.md."

**Assistant interpretation:** Implement the chapter's pattern as a small standard-library Python package with the
exact interface listed in TASK.md, test it with `python3 -m unittest discover -s tests`, keep a phase-by-phase diary,
and finish with a single JSON object in a fenced block.

**Inferred user intent:** A reviewer wants evidence that I can read a pattern chapter, translate its participants
and implementation notes into working code, keep the required interface stable, and be honest about where the
chapter helped or misled.

### What I did
- Read all three files in full, plus listed the directory (only `CHAPTER.md`, `TASK.md`, `DIARY-FORMAT.md` present).
- Chose the module layout: `gridflow/errors.py` (`EvalError`), `gridflow/graph.py` (canonical hashing, immutable
  `Node`, topological iteration), `gridflow/operations.py` (`Operation` record, warn context), `gridflow/cache.py`
  (`Entry`, byte-budgeted LRU `ValueCache`), `gridflow/engine.py` (`Engine`, `Result`, signatures, evaluation,
  single-flight), `gridflow/demo.py` (`demo_engine`).
- Fixed the design decisions that the task leaves open, see "What was tricky to build".

### Why
- Structure table of `CHAPTER.md`: Node / Builder / Source / Signature / Evaluator / Run memo / Value cache /
  In-flight group each get an explicit home, so the pattern is visible in the code rather than implied.
- Implementation notes 1–9 drove the concrete mechanics: intern at build time with canonical args (1), scale in the
  key *and* in the computation, quantised to 1e-4, plus the operation version (2), SHA-256 keys (3), never key a
  function by text but run it once against a placeholder (5), single-flight plus parallel inputs (6), copy on the
  identity short-cut (7), warnings stored with the value (8), byte budget with LRU (9).

### What worked
- The chapter's sketch maps almost one-to-one onto the task's API: `node.call` is the builder, `evaluate` is the
  evaluator, `stats()`/`runs()` expose the instrumentation the note 6 asks for.

### What didn't work
- Nothing yet; this step was reading and design.

### What I learned
- The task's `within(node, mask, build)` is exactly the chapter's `withinMask`: the function argument must be run
  once at build time against a placeholder so the key never depends on function text.
- The chapter allows two readings of the placeholder: keep it in the graph and substitute at evaluation, or
  substitute at build time. Build-time substitution interns the rebuilt subgraph, so two rounds that write
  `within(img, mask, lambda p: p.blur(radius=2))` share both the sub-graph nodes and the cached values. I chose
  build-time substitution and kept a placeholder node that raises `E_PLACEHOLDER` if it is ever evaluated.

### What was tricky to build
- Deciding what belongs in the node hash versus the signature: the chapter puts `op.version` in the signature, so a
  re-registered operation keeps its nodes but misses its cache. That only works if nodes store the operation *name*
  and the registry is consulted at evaluation time, which is what I did.
- Byte accounting for grids: no exact answer, so entries are charged 8 bytes per cell plus a fixed per-row and
  per-entry overhead; the number is a budget knob, not a measurement.

### What warrants a second pair of eyes
- Returning cached values by reference (flyweight semantics) means a caller that mutates `result.value` corrupts the
  cache; the identity short-cut copies, but nothing else does. The chapter's contract is "never modify a cached
  value", which I enforce inside the engine and document for callers.
- Parallel input evaluation uses one thread per distinct input signature; deep-and-wide graphs create many short
  threads. A worker pool would deadlock under nested submission, so threads are deliberate.

### What should be done in the future
- Measure the cache policy (note 9) on a workload instead of hard-coding LRU.

### Code review instructions
- Start with `gridflow/graph.py` (`Node`, `canonical_value`, `digest`) and `gridflow/engine.py`
  (`Engine._prepare` for signatures, `Engine._eval` for memo/cache/single-flight, `Engine.within`).
- Validate with `python3 -m unittest discover -s tests`.

## Step 2: Building the graph layer — canonical hashing, interned immutable nodes

I wrote `gridflow/errors.py`, `gridflow/graph.py`, `gridflow/operations.py` and `gridflow/cache.py`: the pieces that
have no evaluation in them. `graph.py` turns an argument mapping into canonical JSON text (numbers canonicalised so
`2` and `2.0` agree, mapping order removed), hashes operation + arguments + input hashes with SHA-256, freezes
sources by content, and defines an immutable `Node` that hands `call(...)` back to the engine that built it.
`cache.py` holds `Entry` (value, warnings, bytes, cost) and an LRU `ValueCache` with a byte budget.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Build the structural half of the pattern first, with no evaluation yet, so that
interning and keys can be tested in isolation.

**Inferred user intent:** A correct, inspectable graph layer whose hashes are stable and whose nodes cannot be
mutated by a careless caller.

### What I did
- Created `gridflow/errors.py` (`EvalError` carrying `op` and `node`), `gridflow/graph.py` (`canonical_value`,
  `args_text`, `grid_text`, `digest`, `op_hash`, `source_hash`, `Node`, `iter_topological`),
  `gridflow/operations.py` (`Operation`, `Context`), `gridflow/cache.py` (`Entry`, `grid_bytes`, `ValueCache`).
- Made `Node` immutable by raising from `__setattr__`/`__delattr__` and by storing `args` as a
  `MappingProxyType`; iteration over the graph is iterative (`iter_topological`) so deep pipelines do not hit the
  recursion limit while building or hashing.

### Why
- Note 1: hash the *bound* arguments in canonical form, or two spellings of a call become two nodes.
- Note 3: SHA-256 per node, 256 bits, far fewer nodes than values.
- Note 11: a source's identity is a hash of its content, computed once when the source is created.
- Note 9: the cache is a byte-budgeted LRU behind a lock, with an `Entry` that keeps the warnings and the measured
  cost of the computation beside the value.

### What worked
- Interning immediately behaved: `eng.source([[1.0, 2.0]]) is eng.source([[1, 2]])` and two spellings of the same
  call return one node.

### What didn't work
- Nothing in this step; the layer was testable as soon as it existed.

### What I learned
- Canonicalising numbers (`2` vs `2.0`) needed a decision: I convert ints below 2**53 to their float `hex()` text and
  keep larger ints exact, so number spellings intern together without silently losing precision.

### What was tricky to build
- Keeping `Node` immutable while still letting `node.call(...)` intern into the right engine: the node keeps a
  private `_builder` reference that is not part of its hash.

### What warrants a second pair of eyes
- `canonical_value` rejects anything that is not bool/int/float/str/None/sequence/mapping; that is how a function
  argument is refused, but it also refuses, for example, a `set` or `bytes`.

### What should be done in the future
- N/A

### Code review instructions
- `gridflow/graph.py`: read `canonical_value`, `op_hash`, `source_hash`, `Node.__setattr__`.
- Validate: `python3 -m unittest tests.test_graph`.

## Step 3: Building the engine — interning builder, signatures, evaluator, cache, single flight

I wrote `gridflow/engine.py` with the participants the rest of the pattern needs: `Engine.op` for the registry,
`Engine.source` for content-addressed leaves, `Engine.build` as the interning builder, `Engine._prepare` as the
signature computation, `Engine.evaluate`/`_eval`/`_compute` as the evaluator with a per-request run memo, a shared
value cache and single-flight groups, and `Engine.within` with build-time placeholder substitution.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Turn the graph layer into the working engine with the exact `Engine` interface of
TASK.md, including `runs`, `stats`, `within` and evaluation points.

**Inferred user intent:** An engine a script can use naively — rebuild the same chain as often as it likes — without
paying twice for a value.

### What I did
- `Engine.__init__(cache_bytes=10_000_000)`; `op(name, fn, version=1, identity=None, defaults=None)`; `source`;
  `placeholder`; `build`; `within`; `evaluate`; `signature`; `runs`; `stats`; `clear_cache`.
- Signature = SHA-256 of `(node hash, op version, quantised scale, input signatures…)`, computed iteratively over
  the reachable graph in `_prepare`, which also resolves the operation records and fails fast on unregistered
  operations or a stray placeholder.
- Evaluation order: run memo → value cache → join in-flight group or compute; inputs in parallel threads; identity
  short-cut; store value + warnings + bytes; record `runs`.
- `within` runs `build(placeholder)` once, rewrites the sub-graph so the placeholder reads the real node
  (`_substitute`, interning each rebuilt node), and returns a `within` node over `(mask, sub-pipeline, base)`.

### Why
- Collaborations steps 2–5 of the chapter, literally: signature from hash + params + inputs, memo, cache, join or
  compute, inputs in parallel, store with warnings.
- Note 2: the scale is quantised once (`quantise_scale`) and the *quantised* value is what `ctx.scale` reports, so
  the key and the computation agree; the operation version is in the key so a fixed kernel misses.
- Note 5: substituting at build time keeps `build` out of the key entirely; the rebuilt sub-graph also interns
  against the main graph, so a sub-pipeline written in round two is round one's nodes.
- Note 6: single-flight groups keyed by signature; threads rather than a worker pool, because nested submission to a
  bounded pool deadlocks.
- Note 7: the identity short-cut copies the first input's grid before storing it under its own signature.
- Note 8: warnings are stored in the entry and reported when the value is served.

### What worked
- `python3 -m unittest discover -s tests` was already at 91 tests before the first run of the suite (`Ran 91 tests`),
  and the core behaviours — laziness, interned reuse across "programs", scale quantisation, identity, single flight,
  `within` — passed on the first run except for the failures recorded in Step 5.

### What didn't work
- The first version of the entry stored only the warnings of the node itself (`Entry(value, warnings, …)`), which
  broke replay of *upstream* warnings on a cached request. See Step 6.

### What I learned
- Interning must be independent of evaluation (note 2's split between `intern` and `signature`): the node hash must
  not contain the scale, and the signature must not be used for interning, or a different scale would create a
  second node with its own `runs` counter.

### What was tricky to build
- Where to count a `miss`: only the thread that actually starts a computation counts one; a joiner is neither a hit
  nor a miss, since the point of the counter is "how much work was done", and a joined computation is not work.
- Avoiding deadlock with parallel inputs: one thread per *distinct input signature* per node, all joined before the
  operation runs, plus a guard that refuses to wait on an in-flight group owned by the current thread (a graph that
  reads itself) instead of hanging.

### What warrants a second pair of eyes
- `_eval_inputs` creates threads per node with several inputs; on a wide graph that is many short-lived threads.
- Evaluation itself recurses per input level, so a graph a thousand nodes deep hits Python's stack limit (measured:
  depth 400 evaluates, depth 800 raises `RecursionError`); building and hashing are iterative and fine.

### What should be done in the future
- Consider an explicit work-stack evaluator if pipelines deeper than a few hundred nodes matter.

### Code review instructions
- `gridflow/engine.py`: `_prepare` (signatures), `_eval` (memo/cache/single-flight), `_compute` (identity, warnings,
  store), `within`/`_substitute`.
- Validate: `python3 -m unittest tests.test_evaluation tests.test_within`.

## Step 4: Building the demo operations

I wrote `gridflow/demo.py` and `gridflow/__init__.py`: `add`, `gain`, `blur` and `threshold` registered by
`demo_engine()`, with the package exporting `Engine`, `EvalError`, `Node`, `Result` and `demo_engine`.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Provide the four demonstration operations TASK.md names, with the exact semantics it
states (blur radius in cells at scale 1, shrinking proportionally below that; `gain` neutral at `k == 1`).

**Inferred user intent:** Something to test the engine against that behaves like the chapter's image operations.

### What I did
- `add` (adds `k`), `gain` (multiplies by `k`, identity at `k == 1`), `blur` (separable box mean, radius
  `floor(radius * ctx.scale + 0.5)` cells), `threshold` (1 where `value > t` else 0).
- Registered each with `defaults` so `blur()` and `blur(radius=1.0)` intern to one node.

### Why
- The chapter's motivation needs an expensive-but-deterministic operation (`blur`) and cheap ones; `blur` is also the
  operation that reads `ctx.scale`, so the scale-in-the-key rule has something to demonstrate.

### What worked
- The separable box mean keeps `blur` cheap enough for tests while still being a real computation.

### What didn't work
- N/A

### What I learned
- The demo operations showed the value of `defaults`: without it, `f()` and `f(k=default)` would be two nodes with
  equal values, and the second would miss the cache.

### What was tricky to build
- Choosing `round(radius * scale)` rather than truncation so that radius 2 at scale 0.5 is radius 1, and radius 1 at
  scale 0.5 stays 1 instead of vanishing.

### What warrants a second pair of eyes
- `blur` rejects ragged grids (an `EvalError` naming `blur`); other demo operations silently zip along each row.

### What should be done in the future
- N/A

### Code review instructions
- `gridflow/demo.py`; validate with `python3 -m unittest tests.test_demo`.

## Step 5: First full test run — 8 failures, all recorded

I wrote the test suite (`tests/test_graph.py`, `tests/test_evaluation.py`, `tests/test_cache.py`,
`tests/test_within.py`, `tests/test_demo.py`) and ran `python3 -m unittest discover -s tests` for the first time.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Get the suite green, distinguishing my arithmetic mistakes in the tests from real
defects in the engine.

**Inferred user intent:** Evidence that the engine is correct, not that the tests were bent to fit it.

### What I did
- Ran `python3 -m unittest discover -s tests`; 8 of 91 failed.

### Why
- Tests are the only evidence the chapter's claims hold in code.

### What worked
- 83 tests passed first time, including laziness, interning, scale quantisation, identity, single flight, `within`
  and the error paths.

### What didn't work
- `python3 -m unittest discover -s tests` ended with:

      Ran 91 tests in 0.426s

      FAILED (failures=8)

  with `FAIL: test_evicted_values_are_recomputed (test_cache.BudgetTest)`,
  `FAIL: test_warnings_of_upstream_nodes_reach_the_caller (test_cache.WarningTest)`,
  `FAIL: test_a_full_pipeline (test_demo.DemoEngineTest)`,
  `FAIL: test_blur_radius_half_at_half_scale_uses_one_cell (test_demo.DemoEngineTest)`,
  `FAIL: test_blur_spreads_a_peak (test_demo.DemoEngineTest)`,
  `FAIL: test_shared_input_is_computed_once_per_request (test_evaluation.MemoTest)`,
  `FAIL: test_two_inputs_are_evaluated_concurrently (test_evaluation.ParallelInputTest)`,
  `FAIL: test_blur_box_mean (test_evaluation.ValueTest)`.

  Two representative tracebacks:

      FAIL: test_blur_spreads_a_peak (test_demo.DemoEngineTest)
      AssertionError: 2.25 != 1.0 within 7 places (1.25 difference)

      FAIL: test_warnings_of_upstream_nodes_reach_the_caller (test_cache.WarningTest)
      AssertionError: Lists differ: [] != ['using a coarse grid']
      Second list contains 1 additional elements.

### What I learned
- Six of the eight were my own arithmetic in the tests (box-mean windows at grid borders, and a diamond sum I
  mis-added); one was a too-small cache budget in a test, and exactly one was a real defect: warnings raised by an
  *upstream* node disappeared when the root was served from the cache, because the root hit never visits its inputs.
  That is the note-8 failure mode in a new place.

### What was tricky to build
- Distinguishing "the test is wrong" from "the code is wrong" for the blur cases: I recomputed the clamped box means
  by hand for a 3x3 peak (9/4 = 2.25 at a corner, 9/6 = 1.5 at an edge, 9/9 = 1.0 in the middle) and for the
  1x5 row with radius 2 ([0, 0, 0.6, 0.75, 1.0]).

### What warrants a second pair of eyes
- Whether my chosen semantics (warnings deduplicated by text, reported once per evaluation) is the right reading of
  note 8.

### What should be done in the future
- N/A

### Code review instructions
- Re-run the suite; the failing tests as first written are visible in this step's list.

## Step 6: Fix — store the whole sub-graph's warnings with a value

The failing `test_warnings_of_upstream_nodes_reach_the_caller` showed that a cache hit on the *root* replayed only
the root's own warnings. I changed the cache entry to hold everything the value's computation reported, inputs
included, and made the request collect warnings per signature, deduplicated by text.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Make warnings survive any cache hit, not only the first one.

**Inferred user intent:** No silently disappearing diagnostics.

### What I did
- `_Request` now records `signature -> tuple(warnings)` with `warnings_for(sig)` and deduplicates by text
  (`_dedupe`), so a warning is reported once per evaluation.
- `_compute` builds `combined = _dedupe(inherited_from_inputs + own)` and stores that in the `Entry`, then records it
  under the node's signature; the identity short-cut inherits its input's warnings the same way.
- Fixed the test budgets and expectations from Step 5 (`cache_bytes=1600` for 8x8 grids, corrected box-mean values,
  `[[9.0, 15.0]]` for the diamond, `gain`/`slow` distinct inputs for the parallel test).

### Why
- Note 8: "a warning appears on the first request and silently disappears on every cached one" is exactly the bug
  the chapter warns about; the fix is that the stored warnings describe the whole value, not just the last operation.

### What worked
- `python3 -m unittest discover -s tests` → `Ran 91 tests in 0.422s` … `OK`.

### What didn't work
- First attempt left `request.memo[signature] = value` out of `_compute` when I rewrote the tail of the function;
  without it a value too large to cache would be recomputed twice inside one request. I restored it.

### What I learned
- A cache keyed on a node's own signature hides the warnings of everything below it; the entry, not the request, has
  to carry the sub-graph's warnings.

### What was tricky to build
- Avoiding double reporting in a diamond: the same upstream warning reaches two branches, and the diamond's own entry
  must still report it once. Deduplicating by text at every level (entry and request) gives that.

### What warrants a second pair of eyes
- Two distinct nodes warning the same sentence now collapse into one report. Defensible ("once per evaluation"), but
  a reader should agree.

### What should be done in the future
- N/A

### Code review instructions
- `gridflow/engine.py`: `_Request.record_warnings`/`warnings_for`, the tail of `_compute`, `_dedupe`.
- Validate: `python3 -m unittest tests.test_cache -v`.

## Step 7: Green, then hardening — cycle guard, run counting, stress test

With the suite green I hardened two things I did not trust: what happens if an operation evaluates the node it
belongs to (previously it would wait on its own in-flight group forever), and whether `runs` counts an operation that
was invoked but raised. I also stress-tested eight threads over forty random graphs with mixed scales and a cache
small enough to evict constantly.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Look for the failure modes the tests do not cover before declaring the work done.

**Inferred user intent:** A library that fails loudly instead of hanging, and whose counters mean what they say.

### What I did
- `_Inflight` records its owning thread; a joiner that finds itself the owner raises
  `EvalError("E_CYCLE: ...")` instead of waiting.
- `_count_run` moved before the operation call, so an operation that runs and raises is counted as having run.
- Added `tests/test_evaluation.py::CycleTest` and three `within` tests (placeholder used twice, sub-pipeline reading
  another source, nested `within`).
- Stress run: 8 threads x 40 evaluations over 40 random graphs with scales 1.0/0.5/0.25 and
  `cache_bytes=20000` → `errors: [] elapsed 0.01 {'hits': 639, 'misses': 377, 'bytes': 19760, 'evictions': 312}`,
  and every value equalled the value computed by a fresh engine with caching disabled.

### Why
- Note 6 asks for shares and counters a test can assert on; a hang would be a far worse failure than an error.

### What worked
- The stress run produced no exceptions, no deadlocks, and identical values with and without the cache.

### What didn't work
- Nothing failed in this step.

### What I learned
- `hits + misses` does not equal lookups: a joined in-flight computation is neither. That is deliberate; the counters
  measure work done and work served, not requests.

### What was tricky to build
- Measuring parallelism honestly: the test asserts that an operation over two slow inputs finishes in less than 0.36s
  while each input sleeps 0.2s, which is tolerant enough for a loaded machine but would fail loudly if inputs ran one
  after the other (0.4s+).

### What warrants a second pair of eyes
- Whether `E_CYCLE` should be reachable through `Engine.evaluate` at all, or whether re-entrant operation bodies
  should be declared out of scope.

### What should be done in the future
- N/A

### Code review instructions
- `gridflow/engine.py`: `_Inflight.__init__`/`owner`, the `not mine` branch of `_eval`, `_count_run`.
- Validate: `python3 -m unittest discover -s tests`.

## Step 8: Final check

I re-read the public interface against TASK.md, ran a smoke script that uses only the documented names, and ran the
whole suite several times to make sure the timing and concurrency tests are not flaky.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Confirm the deliverable matches the required interface and that the suite is stable.

**Inferred user intent:** A finished, verified submission.

### What I did
- Smoke script using `Engine`, `op`, `source`, `call`, `evaluate`, `runs`, `stats`, `within`, `demo_engine`,
  `EvalError` exactly as documented, verified by hand.
- `python3 -m unittest discover -s tests`, run three times in a row.
- Files created: `gridflow/__init__.py`, `gridflow/errors.py`, `gridflow/graph.py`, `gridflow/operations.py`,
  `gridflow/cache.py`, `gridflow/engine.py`, `gridflow/demo.py`, `tests/test_graph.py`,
  `tests/test_evaluation.py`, `tests/test_cache.py`, `tests/test_within.py`, `tests/test_demo.py`, `DIARY.md`.

### Why
- The final message must state the test count and the last result truthfully.

### What worked
- `Ran 95 tests … OK` on every run; the smoke script printed the expected values
  (`[[10.0, 2.0], [3.0, 40.0]]` for `within`, `{'hits': 1, 'misses': 2, 'bytes': 448, 'evictions': 0}` for `stats`).

### What didn't work
- Nothing failed.

### What I learned
- The interface survives being used naively: a script can rebuild the same chain every round and the second round
  only pays for nodes it has never built.

### What was tricky to build
- N/A

### What warrants a second pair of eyes
- Returning cached values by reference is the chapter's flyweight semantics (and its "never modify a cached value"
  obligation); a caller that mutates `result.value` corrupts the cache for everyone. I copy only on the identity
  short-cut, as note 7 says.

### What should be done in the future
- If callers need to mutate results, add a copy-on-return mode and measure what it costs.

### Code review instructions
- `python3 -m unittest discover -s tests`; then `python3 -c "import gridflow; e=gridflow.demo_engine(); ..."`.

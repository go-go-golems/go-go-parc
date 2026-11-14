# Diary

## Goal

Build `gridflow`, a standard-library Python 3 library for lazy, content-keyed computation over 2D float grids,
applying the Content-Keyed Lazy Graph pattern from `CHAPTER.md`. This diary records the design decisions, what was
built in each phase, the failures met while testing, and the fixes applied.

## Step 1: Read the chapter, the task and the diary format; design the package

I read `CHAPTER.md` (Content-Keyed Lazy Graph), `TASK.md` (the `gridflow` public interface) and `DIARY-FORMAT.md`.
I then mapped every participant of the chapter onto a concrete Python object and wrote down the module split before
writing any code, so that the pattern structure (Node / Builder / Signature / Evaluator / Run memo / Value cache /
In-flight group) is visible in the file layout rather than smeared across one file.

### Prompt Context

**User prompt (verbatim):** "You are a software engineer joining a project. Your working directory contains three files:
- CHAPTER.md: a chapter of a design-pattern book describing the pattern you must apply;
- TASK.md: the software to build, with its required public interface;
- DIARY-FORMAT.md: how to keep your work diary.
Read all three completely first. Keep DIARY.md as you go, one step per phase of work, in that format. Then design, build and test the software in this directory. Work only inside this
directory (do not read or write outside it). Use only the Python 3 standard library. Run your tests and fix what
fails before you finish, and make sure DIARY.md is complete. Your final message must follow the output format at the end of TASK.md."

**Assistant interpretation:** Implement a `gridflow` package whose public API matches `TASK.md` exactly, structured
as a lazy hash-consed graph with content-addressed value cache, plus tests under `tests/`, plus this diary.

**Inferred user intent:** A working, tested library that a reviewer can check against the chapter: nodes interned at
build time, values computed only on demand, keys built from inputs recursively, cached values shared across
requests and never mutated, functions turned into subgraphs instead of being hashed by text.

### What I did
- Read `CHAPTER.md`, `TASK.md`, `DIARY-FORMAT.md` in full.
- Planned this module split: `keys.py` (canonical forms + SHA-256 digests), `nodes.py` (Operation record, Node,
  Builder/interning, placeholder leaf), `cache.py` (Stats, Entry, budgeted LRU ValueCache, InFlight group),
  `evaluate.py` (signatures, run memo, evaluator, EvalContext), `values.py` (freeze/merge/measure grids),
  `engine.py` (Engine, registry, `source`, `call`, `within`, `evaluate`, `runs`, `stats`), `ops.py` (demo operations).

### Why
- `Structure` and `Collaborations` in the chapter name seven participants; giving each a home keeps the mapping
  honest (and the final `pattern_mapping` answer verifiable).
- Implementation notes 1-12 each became a design decision: intern at build (§1), quantised scale in the key and
  used for computing (§2), SHA-256 keys (§3), `identity` short-cut (§7), warnings stored with values (§8), byte
  budget + LRU (§9), single-flight + parallel inputs (§6), no function in a key (§5), `E_PLACEHOLDER` (§5),
  explicit evaluation points (§12).

### What worked
- The interface in `TASK.md` covers the chapter's participants almost one-to-one, so the design fell out quickly.

### What didn't work
- N/A at this step.

### What I learned
- The chapter's `withinMask` sketch ("run the function once at build time against a placeholder, keep the
  subgraph") is the only place where node interning and evaluation cannot be fully separated: the placeholder leaf
  must hash to a *constant* so that two rebuilds of the same `within` pipeline intern to the same node, while the
  binding placeholder -> base node must be a per-evaluation fact. That tension drove the design of `Bindings`.

### What was tricky to build
- N/A at this step (design only).

### What warrants a second pair of eyes
- Whether a single constant-hashed placeholder leaf is safe under nested `within` (my answer: bindings are scoped
  per evaluation and keyed by placeholder node id, so the innermost `within` rebinds).

### What should be done in the future
- Build the modules, then tests.

### Code review instructions
- Start with `TASK.md` and `CHAPTER.md` (Structure table), then check the module split listed above.

## Step 2: Keys, grid values, nodes and the interning builder

I set out to give every call a stable structural key and to intern equal calls into one node, since that is the
first half of the pattern (chapter's "building" sketch, notes 1 and 3). I wrote `keys.py`, `values.py`,
`result.py` and `nodes.py`.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Build the content-addressing foundation: canonical argument text, wide digests,
immutable grid values, the Node record and the interning Builder.

**Inferred user intent:** Equal calls must be one node, identical scripts must rebuild the same graph, and no key
may ever depend on a function's source text.

### What I did
- `gridflow/keys.py`: `canonical()` (type-tagged, sorted-dict, `float.hex()` exact floats), `digest()`
  (SHA-256, note 3), `quantize_scale()` (4 decimals, note 2).
- `gridflow/values.py`: `freeze_grid` (validate rectangular grid -> tuple of tuples), `to_grid` (fresh copy out),
  `grid_bytes` (8 bytes/cell + 128 overhead), `merge_mask` (the `within` merge).
- `gridflow/result.py`: `Result(value, warnings, scale, node, signature, cached)`.
- `gridflow/nodes.py`: `Operation` record (fn, version, identity), `Node` (kind, op, args, inputs, hash, id),
  `Builder` with `intern_source`, `intern_op`, `intern_within` and the single global placeholder leaf.
- Node hashes exclude the operation *version* and the evaluation scale: nodes are interned independently of how
  they will be evaluated; both belong to the signature.

### Why
- CHAPTER note 1: hash the bound arguments in canonical form or two spellings of one call become two nodes.
- CHAPTER note 3: 256-bit keys. The builder additionally keeps each node's canonical fingerprint and salts a
  digest collision instead of merging two different nodes (a 256-bit collision is impossible in practice, but a
  silent wrong value is unreportable, so the extra check costs nothing).
- CHAPTER note 11: a grid source has no cheaper identity than its content, so a source's key is a hash of its
  content and two equal sources are one node -- more portable than goja-cv's path+size+mtime.

### What worked
- Interning: `eng.source([[1,2],[3,4]]) is eng.source([[1.0,2.0],[3.0,4.0]])` -> True.
- `src.call('gain', k=2.0)` built twice is the same node object.

### What didn't work
- N/A at this step.

### What I learned
- `float.hex()` is the only stable, exact canonical float form available in the standard library (`repr` is
  round-trip stable but I did not want to depend on that).

### What was tricky to build
- The placeholder's node hash must be a *constant* (a unique per-call hash would stop identical `within`
  pipelines from interning) while its *meaning* is per evaluation.  I resolved this in `evaluate.Bindings`
  (Step 4), not here: the node stays constant, the binding is an evaluation-time fact.

### What warrants a second pair of eyes
- `canonical()` accepts a `Node` by its hash; that means a node passed as an *argument* (not as an input) keys
  by structure. No demo operation needs this, but it is a deliberate hole in the "inputs only" rule.

### What should be done in the future
- Value cache, single-flight group, then the evaluator.

### Code review instructions
- Read `gridflow/keys.py` then `gridflow/nodes.py`; check `intern_op`'s fingerprint string includes op name,
  canonical args and input hashes in order.

## Step 3: The byte-budgeted value cache and the in-flight group

Next I wrote `gridflow/cache.py`: `Stats` counters, `Entry` (value + warnings + size + cost), `ValueCache` with a
byte budget and two eviction policies, and `InFlight`, a single-flight group keyed by signature.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Provide chapter participants "Value cache" and "In-flight group" with the
behaviours notes 6, 8 and 9 require.

**Inferred user intent:** Cached values carry their warnings, memory is bounded with an eviction policy that is a
setting, and two concurrent requests for one value compute it once.

### What I did
- `ValueCache(budget, stats, policy)` with `get`/`put`/`clear`, `nbytes`, pinned entries, LRU and
  `greedy_dual_size` (priority `age + cost / size`).
- `put` returns `False` for a value larger than the whole budget, so the evaluator can report its warnings
  immediately (note 8).
- `InFlight.once(key, fn)`: first caller computes and publishes value or exception, others wait on a
  `threading.Condition`; a re-entrant request for the key the same thread is computing raises `EvalError`
  instead of deadlocking.

### Why
- Note 9: "Budget the cache and treat the eviction policy as a setting." Two policies are offered, both cheap to
  measure with `eng.stats()["evictions"]`.
- Note 8: warnings live in the `Entry`, so serving a cached value can replay them.
- Note 6: single flight keyed by signature.

### What worked
- Budget, eviction and pinned sources behave as intended in the smoke runs.

### What didn't work
- First draft of `_evict_one` for GreedyDual-Size contained a leftover `max(...)` assignment before the
  `min(...)` one; removed it so the lowest priority is evicted.

### What I learned
- Pinning sources outside the cap (goja-cv's rule) matters here too: without it, a small `cache_bytes` would
  evict the source after every step and re-freeze the same grid, which looks like a cache bug in tests.

### What was tricky to build
- Making "value too large to cache" observable: `put` must tell the caller it did not store, otherwise warnings
  raised by an uncached computation would be dropped silently on the next request.

### What warrants a second pair of eyes
- The GreedyDual-Size priority is a simplification (no inflation term). Fine for a setting that only needs to be
  measurable, but not a faithful GDS implementation.

### What should be done in the future
- Evaluator and engine wiring (Step 4).

### Code review instructions
- `gridflow/cache.py`: `ValueCache.put`, `_evict_one`, `InFlight.once`.

## Step 4: The evaluator (signatures, run memo, identity, placeholder) and the engine

I wrote `gridflow/evaluate.py` (signatures, `RunMemo`, `EvalContext`, `Evaluator`) and `gridflow/engine.py`
(registry, `source`, `call`, `within`, `evaluate`, `runs`, `stats`, executor).

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Wire the participants together so that a node is computed at most once per
signature, inputs are evaluated in parallel, warnings replay, and functions become subgraphs.

**Inferred user intent:** Correct caching semantics under repetition, scale changes, re-registered operations and
`within`.

### What I did
- `Evaluator._signature`: recursive key over node hash, op name + version, quantised params and input signatures,
  memoised per `(node id, bindings)`.
- `Evaluator._eval`: run memo -> value cache -> single flight -> compute; hits/misses counted here.
- `Evaluator._compute_op`: identity short-cut before running the op (note 7), `EvalContext` for `scale`/`warn`,
  `freeze_result` validation, warnings stored with the entry.
- `Evaluator._eval_many`: inputs of a node with several inputs are evaluated in a `ThreadPoolExecutor`, with a
  thread-local flag so a worker never nests submissions into the same pool (no deadlock).
- `Evaluator._resolve`: follows placeholder bindings so a `within` nested inside a `within` binds the placeholder
  to the outer base instead of itself.
- `Engine`: `op`, `source`, `build_call`, `within`, `evaluate`, `runs`, `stats`, `close`/context manager.

### Why
- Chapter Collaborations step 2-4 and notes 2, 5, 6, 7, 8, 9, 12.
- Note 12: `evaluate` is the only evaluation point, and reading a placeholder's "value" is `E_PLACEHOLDER`.

### What worked
- One-pass pipelines, cache hits across requests, identity, `within`, nested `within`.

### What didn't work
- Nested `within` first raised `RecursionError: maximum recursion depth exceeded while calling a Python object`
  in `_signature` (the placeholder line `signature = self._signature(base, bindings)`), because a `within`
  whose base *is* the placeholder rebound the placeholder to itself (`{placeholder: placeholder}`), looping
  forever. Fixed by resolving the base through the current bindings before binding it (`Evaluator._resolve`).

### What I learned
- The chapter's `withinMask` sketch hides one real obstacle: the placeholder leaf is shared by every `within` in
  an engine (it must hash constantly), so the binding must be per evaluation and must be resolved transitively.
  This is the point where "functions as arguments versus hashability" (Forces) actually bit.

### What was tricky to build
- Keeping signature memoisation keyed by `(node id, bindings key)` so the same inner subgraph object can carry
  different signatures in different `within` calls; the run memo is keyed by signature only, so values still
  dedupe.

### What warrants a second pair of eyes
- Parallel input evaluation shares one `RunMemo` across threads; the memo lock is never held during
  computation, but a reviewer should confirm no path holds it across a blocking call.
- `EvalContext.warn` appends to a plain list; a worker thread that runs the op is the only writer, so it is safe
  only because the op's own frame owns the list.

### What should be done in the future
- Demo operations (Step 5), then tests.

### Code review instructions
- `gridflow/evaluate.py` top to bottom, then `gridflow/engine.py` `within`/`build_call`.

## Step 5: Demo operations

I added `gridflow/ops.py` with `add`, `gain`, `blur`, `threshold` and `demo_engine()`, and exported the public
names from `gridflow/__init__.py`.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Register the four demo operations the task requires, with the documented
neutrality rule for `gain` and a scale-dependent `blur`.

**Inferred user intent:** A ready-to-use engine so the pattern's cache behaviour can be demonstrated and tested
without every user writing operations first.

### What I did
- `add(k=0.0)`, `gain(k=1.0, identity: k == 1)`, `threshold(t=0.0)`, `blur(radius=1.0, identity: radius == 0)`.
- `blur` computes the effective radius as `round(radius * ctx.scale)` on an integral image with border-clipped
  windows; `ctx.scale` is the quantised scale, so the value matches the key it is stored under (note 2).
- Unknown keyword arguments are rejected with a `TypeError` naming the operation, instead of being silently
  ignored and then hashing into the key.

### Why
- TASK.md's required demo operations; note 2 (scale in the key *and* in the computation); note 7 (identity).
- Rejecting unknown args keeps keys honest: a misspelt argument would otherwise be part of a key that never
  affects the value.

### What worked
- Values verified by hand: `gain k=2` on `[[1,2],[3,4]]` -> `[[2,4],[6,8]]`; `blur radius=1` -> all 5.0;
  `threshold t=2.5` -> `[[0,0],[1,1]]`; `gain k=1` -> 0 runs.

### What didn't work
- N/A at this step.

### What I learned
- Making `blur`'s radius shrink with the scale is the cheapest honest way to show that an evaluation parameter
  belongs in the key: at scale 1 and 0.5 the same node has two different values and two different keys.

### What was tricky to build
- The box mean needed to be fast enough to look "expensive" in tests but stay deterministic: an integral image
  with clipped windows does both, and uses only the standard library.

### What warrants a second pair of eyes
- `_check_args` runs *after* `_number` in each demo op, so a typo plus a valid `k` raises, but a typo alone may
  first raise about the missing argument. Cosmetic only.

### What should be done in the future
- Tests.

### Code review instructions
- `gridflow/ops.py`: `_box_mean` (window clipping) and the two `identity` hooks.

## Step 6: Tests, one file per concern

I wrote a test suite under `tests/` before touching the implementation again, so the failures would tell me where the
pattern was wrong rather than where my smoke script was.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Cover every promise of `TASK.md` and every note-rule of `CHAPTER.md` that the code
claims to implement, then run `python3 -m unittest discover -s tests`.

**Inferred user intent:** Evidence that the pattern actually holds: interning, laziness, cache reuse across
requests, keys that include scale/version/inputs, warnings replay, `within`, parallelism, eviction.

### What I did
- `tests/test_building.py` (18 tests): source identity, interning, argument canonicalisation, laziness, graph
  inspection, build errors.
- `tests/test_evaluation.py` (27 tests): demo values, run counts, cache across requests, scale and quantisation,
  warnings (raised, stored, replayed, subtrees, copies), failures, immutability, version bumps.
- `tests/test_cache.py` (13 tests): budget, eviction, recompute-after-eviction, uncacheable values, sources outside
  the budget, both policies, run-memo dedupe, key precision, deep keys.
- `tests/test_within.py` (20 tests): mask semantics, build-once, no function text in keys, interning, cross-request
  hits, subgraph keyed by base, subgraph shared between masks, `E_PLACEHOLDER`, nesting, shape mismatch.
- `tests/test_concurrency.py` (8 tests): single flight under two and four threads, parallel vs sequential inputs,
  wide fan-in, lifecycle.
- `tests/test_pattern.py` (8 tests): the chapter's three-round story, masked touch-up, deep chains, signature
  sensitivity, exports.
- `tests/test_ops.py` (11 tests): `blur` compared against a naive independent box filter, radius shrink by scale,
  argument validation, warnings through `within`.

### Why
- Every test names the chapter rule it guards, so a reviewer can map test -> note.
- The `blur` reference implementation is written independently (no integral image) to catch indexing bugs.

### What worked
- The suite found four real defects plus a handful of my own arithmetic mistakes in test expectations.

### What didn't work
- First full run: `python3 -m unittest discover -s tests` -> `FAILED (failures=11)` in 102 tests. Exact snippets:
  `AssertionError: ValueError not raised`,
  `AssertionError: 1 != 2`,
  `AssertionError: 0 != 2`,
  `AssertionError: None == None`,
  `AssertionError: Lists differ: [[5.0]] != [[4.0]]`,
  `AssertionError: 1 != 31`.
- Later: `AssertionError: Lists differ: [] != ['masked region is flat']`, then after the first fix
  `AssertionError: Lists differ: ['masked region is flat', 'masked region is flat'] != ['masked region is flat']`.
- A 300-node chain raised `RecursionError maximum recursion depth exceeded in comparison`.

### What I learned
- Three of the eleven failures were mine (expecting a sum of 4 where 5 was right, calling a cross-engine check on
  the wrong engine, expecting two cache hits where the root hit stops the walk). Distinguishing my errors from the
  library's took reading the chapter again: "a value used twice in one request is found without touching the shared
  cache" implies the root hit never descends.

### What was tricky to build
- Testing warning replay: the first attempt only covered one node. The interesting case is a *parent* served from
  the cache whose child's warning was raised earlier, which is exactly the case the naive implementation gets
  wrong.

### What warrants a second pair of eyes
- Timing-based parallelism tests (`< 0.27 s` for two 0.15 s inputs) are inherently load-sensitive. They passed on
  this machine; on a heavily loaded one they may need generous margins.

### What should be done in the future
- Fix the defects the suite found (Step 7).

### Code review instructions
- `python3 -m unittest discover -s tests`; then read one test per file to see the mapping to chapter notes.

## Step 7: Fixes after the failing tests

I worked through the failures in the order the suite reported them.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Make the suite pass without weakening the pattern.

**Inferred user intent:** A correct implementation, not a suite bent to match a bug.

### What I did
1. `Result.signature` was always `None`: `Evaluator.run` never set `root_signature`. Fixed by computing the root
   signature (memoised) at the start of `run`.
2. `eng.runs(node)` stayed 0 for an operation that raised: `count_run` was called only after the operation
   returned. Moved the increment before the call (note 6: runs count invocations so a test can assert what was
   recomputed).
3. Warning replay stopped one level up: a `within` node served from the cache returned `[]` although its subgraph
   had warned. Fixed by storing, with every entry, the union of its inputs' warnings and its own
   (`Evaluator._combine`), so serving any cached value replays the whole subtree's warnings (note 8).
4. That fix then produced each warning twice (once for the inner signature, once for the parent). Fixed by
   de-duplicating the request's warning list by message in `Evaluator._report`: "once per evaluation".
5. Deep chains raised `RecursionError` (signatures and evaluation both recurse once per level). Added
   `Engine._graph_depth`, an iterative longest-path computation, and `Engine._ensure_recursion_room`, which raises
   `sys.setrecursionlimit` to `10 * depth + 500` and never lowers it (so a concurrent request cannot have the room
   taken away). A 3000-node chain and a 200-deep `within` now evaluate.
6. My own test expectations were corrected where the library was right (see Step 6).
7. Fixed two leftovers found by reading the diff: a stray no-op line in `Node.__init__` and a duplicated
   `max(...)` assignment in `ValueCache._evict_one`.

### Why
- Each fix is anchored in a chapter rule: 1-2 in Collaborations/note 6, 3-4 in note 8 ("a warning appears on the
  first request and silently disappears on every cached one" -- my version of that bug was one level up), 5 in
  Consequences (recursion is an implementation detail, not a property of the caller's graph).

### What worked
- `python3 -m unittest discover -s tests` -> `Ran 113 tests in 0.703s / OK` after the fixes.
- Deep graph check: `eng.evaluate()` of a 3000-node chain returns `[[3001.0]]`.

### What didn't work
- The first version of the warning-union fix (snapshotting the request's warning list length before evaluating
  inputs) was order-dependent: which warnings a parent stored depended on whether a sibling had already reported
  them. Replaced it with the order-independent rule "inputs' entries, then own warnings".

### What I learned
- Note 8's rule has to be pulled *up* the graph, not just applied at the node: warnings must live where the value
  lives, and a value's warnings are "everything its computation reported", which includes its inputs'
  computation.
- The chapter's "structural keys against output keys" force did not bite here, but the recursion issue shows a
  related trap: any recursive engine must own its stack budget.

### What was tricky to build
- Making warning de-duplication right in both directions: per signature (so a value served twice in one request
  warns once) *and* per message (so a parent's copy of a child's warning does not double up). The two rules
  together give "each distinct message appears once per evaluation".

### What warrants a second pair of eyes
- `_combine` makes every cache entry carry its subtree's warnings. If an operation produces a large number of
  distinct warnings, entries grow; the byte accounting does not count warning bytes. Acceptable at this scale, but
  worth a look.
- `_ensure_recursion_room` mutates a process-global limit. It only raises it and derives the value from the graph
  depth, but a reviewer should confirm they are happy with that.

### What should be done in the future
- Count warning bytes in `grid_bytes`, or cap the number of warnings stored per entry.
- Consider the "mask is all zeros -> the node is the base" key rule from note 4; deliberately not done, because it
  would make `within` sometimes return a node of a different kind.

### Code review instructions
- `git diff` equivalent: `gridflow/evaluate.py` (`run`, `_report`, `_combine`, `_compute_within`, `_compute_op`)
  and `gridflow/engine.py` (`evaluate`, `_graph_depth`, `_ensure_recursion_room`). Re-run the suite after any
  change there.

## Step 8: Final check

I ran the whole suite repeatedly, exercised the public interface exactly as `TASK.md` words it, cleaned the byte-code
caches out of the tree, and closed the diary.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Confirm the deliverable: package + tests + complete diary, all inside this directory,
standard library only.

**Inferred user intent:** Nothing left failing, nothing left undocumented, and a final message in the required JSON
shape.

### What I did
- `python3 -m unittest discover -s tests` five times in a row: `Ran 113 tests in 0.70s / OK` every time (no
  flakiness from the thread and timing tests).
- Manual interface walk-through: `Engine(cache_bytes=10_000_000)`, `eng.op(...)` with `version`/`identity`,
  `eng.source`, `node.call`, `eng.evaluate(...).value/.warnings`, `eng.runs`, `eng.stats`, `eng.within`,
  `gridflow.demo_engine().operations()` -> `['add', 'blur', 'gain', 'threshold']`.
- Extras checked: empty grid, single row, `inf`/`nan` cells, raw-grid mask, nested and placeholder-based bases, a
  3000-node chain, a 200-deep `within`, `cache_bytes=0`, `policy="greedy_dual_size"`, context-manager use.
- Removed `__pycache__` directories; `grep`-checked that only the standard library is imported
  (`hashlib`, `itertools`, `threading`, `time`, `sys`, `types`, `concurrent.futures`).

### Why
- TASK.md requires the tests to be run and to pass, and the diary to be complete.

### What worked
- Everything above; the 113 tests cover each participant and each implementation note that the code claims.

### What didn't work
- Nothing outstanding at this step.

### What I learned
- The parts of the chapter that cost the most thought were the ones about what is *not* in the key (functions,
  scale quantisation, the mask vs the subgraph) -- they are one-line rules in the chapter and real design
  constraints in the code.

### What was tricky to build
- Nothing new at this step; the difficulty was concentrated in `within` bindings (Step 4), warning propagation
  (Step 7) and stack depth (Step 7).

### What warrants a second pair of eyes
- The three review points raised earlier: the global recursion-limit raise, warnings stored per entry (unbudgeted
  bytes), and the load-sensitivity of the two timing tests.

### What should be done in the future
- Add output-hash verification for early cutoff (Variations: "Verifying keys with early cutoff") if masked edits
  turn out to recompute avoidably, as the lab's measurements in note 10 suggest).
- Count warning bytes in the cache budget; consider a persistent cache keyed by the same signatures (note 11 shows
  what such a cache would need from source identity).

### Code review instructions
- `python3 -m unittest discover -s tests` from this directory; then read `gridflow/__init__.py` (participant map),
  `gridflow/nodes.py` (Node/Builder), `gridflow/evaluate.py` (signatures + evaluator), `gridflow/cache.py`
  (budget + single flight), `gridflow/engine.py` (public surface), `gridflow/ops.py` (demo operations).

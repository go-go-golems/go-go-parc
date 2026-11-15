# Diary

## Goal

Build `gridflow`, a standard-library-only Python 3 library that turns grid operation calls into interned, lazily
evaluated nodes with a content-keyed, byte-budgeted value cache, following Chapter 3 (content-keyed lazy graph).
This diary records the design decisions, the build order, and every failing test with its exact error text.

## Step 1: Reading and design

I read `CHAPTER.md`, `TASK.md` and `DIARY-FORMAT.md` completely, then wrote down the participant list from the chapter
against the interface the task demands, so that every required name has a home before any code exists.

### Prompt Context

**User prompt (verbatim):** "You are a software engineer joining a project. Your working directory contains three files:
- CHAPTER.md: a chapter of a design-pattern book describing the pattern you must apply;
- TASK.md: the software to build, with its required public interface;
- DIARY-FORMAT.md: how to keep your work diary.
Read all three completely first. Keep DIARY.md as you go, one step per phase of work, in that format. Then design, build and test the software in this directory. Work only inside this
directory (do not read or write outside it). Use only the Python 3 standard library. Run your tests and fix what
fails before you finish, and make sure DIARY.md is complete. Your final message must follow the output format at the
end of TASK.md."

**Assistant interpretation:** Implement the library described in `TASK.md` using the pattern of `CHAPTER.md`, with
tests under `tests/`, a diary in the required format, and a JSON final message.

**Inferred user intent:** A working, tested, pattern-faithful implementation whose structure can be audited against the
chapter's participants and implementation notes.

### What I did
- Read `CHAPTER.md` (Content-Keyed Lazy Graph), `TASK.md` (gridflow) and `DIARY-FORMAT.md`.
- Sketched the module split: `gridflow/errors.py`, `gridflow/canonical.py`, `gridflow/engine.py`, `gridflow/demo.py`,
  `gridflow/__init__.py`.
- Mapped participants: Node/Builder/Source/Signature/Evaluator/Run memo/Value cache onto `engine.py` classes;
  the in-flight group is left out (single caller, no async runtime).

### Why
- Chapter "Solution" and "Structure" fix the shape: intern at build time by canonical args + input hashes, key values
  by a signature over node hash/version/quantised params/input signatures, cache frozen values under a byte budget.
- Note 4 says a 256-bit SHA-256 signature is cheap and needs no collision handling, so node hashes and signatures are
  SHA-256 hex strings over canonical spellings.
- Note 9: the in-flight group is only needed with concurrent callers; gridflow evaluates inputs in order, so it is
  omitted (the chapter's "Smallest form" variation, plus the run memo and function arguments it does not have).

### What worked
- The chapter's participant table mapped one-to-one onto the required public names, except `within`, which the chapter
  calls "function arguments turned into a subgraph" (note 6); `eng.within(node, mask, build)` is that mechanism.

### What didn't work
- N/A (no code yet).

### What I learned
- The task's `identity(args)` hook is the chapter's "neutral call returns its input's value, uncached" path (note 7),
  which is why `runs` must not count a neutral node: its operation never runs.
- Sources need a content hash rather than an mtime key, because the task offers grids, not files (note 3 applies to
  files; here content is the whole identity).

### What was tricky to build
- Nothing built yet. The one design tension noted: `build(placeholder)` must not be evaluated at build time, so
  `within` needs a placeholder node whose evaluation is an error (note 6) plus per-node substitution with memoization.

### What warrants a second pair of eyes
- Whether re-registering an operation under the same name and version must invalidate existing cached keys. Decision:
  a per-registration revision enters the node hash, so a replaced operation produces new nodes and cannot serve stale
  values (note 3). A reviewer should confirm this does not surprise callers who re-register identical operations.

### What should be done in the future
- Build `errors.py` and `canonical.py` next, then the engine core, then `within`, then demo operations, then tests.

### Code review instructions
- N/A for this step; start at `gridflow/engine.py` once it exists.

## Step 2: Errors, canonical form, frozen grids

Before any graph existed I built the two pieces the builder leans on: an error hierarchy that separates build-time
refusals from evaluation failures, and a canonical spelling for every value that may reach a key.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Lay the foundation of the pattern: "refuse any argument that has no canonical form"
needs a refusal type, and "intern nodes by a hash of the operation, its canonical arguments" needs one spelling per
value.

**Inferred user intent:** A library where equal calls really are one node and where non-data arguments fail loudly
instead of silently serving stale values.

### What I did
- Created `gridflow/errors.py`: `GridflowError`, `ArgumentError(GridflowError, TypeError)`,
  `UnknownOperation(GridflowError, LookupError)`, `EvalError(GridflowError)` with an `.op` attribute, and
  `PlaceholderError(EvalError)`.
- Created `gridflow/canonical.py`: `canonical()`, `freeze_grid()`, `thaw_grid()`, `grid_bytes()`, `digest()`.

### Why
- Note 1 is explicit that hashing the bound arguments in canonical form is what makes two spellings of a call one
  node, and that identity-keyed or printed function arguments served stale values in three of five experimental
  builds; `canonical()` therefore refuses `function`, `object` and anything unknown with `E_ARG`.
- Note 7: values must be stored in a form nothing can write to, so `freeze_grid()` returns tuples of tuples of floats
  and `thaw_grid()` is the only way out (used once, at a request).
- Note 4: SHA-256 (`digest()`) is wide enough that collision handling is unnecessary.
- `ArgumentError` also subclasses `TypeError` so that passing a function where data belongs behaves like an ordinary
  Python type error for callers who do not know gridflow's names.

### What worked
- `canonical([[1, 2]])` and `canonical(((1.0, 2.0),))` produce the same text, so equal *content* hashes alike; ints
  too large for an exact float keep an exact `i...` spelling instead of silently colliding.
- `-0.0` collapses to `0.0`, so `add(k=-0.0)` and `add(k=0.0)` intern as one node.

### What didn't work
- N/A.

### What I learned
- Grid validation had to live in `freeze_grid()` rather than in each demo operation: an operation that returns a
  ragged or non-numeric grid must be reported as *its* failure, with its name in the message, which is easiest to do
  centrally in the evaluator.

### What was tricky to build
- Keeping one spelling for numbers: `True` is an `int` in Python, so booleans are tested first; and ints that a float
  cannot hold exactly are spelled exactly rather than coerced, which would have made `k=2**53` and `k=2**53+1` the
  same key.

### What warrants a second pair of eyes
- `canonical()` allows grids to appear *inside* arguments (a list of numbers is canonical). That is deliberate: a
  small constant grid is data, not a function argument, and must hash. Confirm no test expects the opposite.

### What should be done in the future
- The node table, builder, signature, evaluator and cache next.

### Code review instructions
- Read `gridflow/canonical.py` top to bottom: `canonical()` for the acceptance rules, `freeze_grid()` for grid
  validation. Validate with `python3 -c "import gridflow; print(gridflow.canonical"...` once the engine exists.

## Step 3: Nodes, builder, sources, signatures, evaluator, cache

This is the pattern itself: `Node`, `Engine._build` (builder + interning), `Engine.source`, `Engine._signatures`,
`Engine._eval` (memo, cache, identity short-cut, freeze, store) and `Engine._store` (byte budget, LRU).

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Build the graph half and the value half of the pattern against the required interface:
`op`, `source`, `call`, `evaluate`, `runs`, `stats`.

**Inferred user intent:** A library whose laziness, sharing and cache hits can be observed directly (`runs`, `stats`)
and audited against the chapter's participants.

### What I did
- Created `gridflow/engine.py` with `Result`, `Operation`, `Node`, `_Ctx`, `_Entry`, `Engine`, `_quantise()`.
- Registered operations carry a per-registration `revision` that enters the node hash, so replacing an operation
  cannot serve a value computed by the old implementation (note 3).
- `Engine._signatures()` walks the graph iteratively (bottom-up) so that a deep pipeline does not exhaust the stack
  before evaluation starts; `Engine._eval()` recurses over inputs, which is fine because the graph is a DAG in order.
- The run memo (`memo` in `evaluate`) maps signature to `(value, warnings)` for the duration of one request, so a
  diamond's shared input is evaluated once even if the value cache evicts it mid-request.
- Neutral nodes (`identity(args)` true) evaluate only their first input, return its frozen value and are *not* cached;
  `eng.runs()` for such a node stays 0 because the operation never ran.
- `stats()` reports exactly `hits`, `misses`, `bytes`, `evictions`; `misses` counts actual computations.

### Why
- Chapter "Collaborations" 1-4 and the Sketch's `intern`/`signature`/`evaluate` pseudocode drove the split. Note 2
  drove `_quantise()` being applied at `evaluate()` and the quantised value being what `ctx.scale` returns, so the key
  and the work never disagree.
- Note 5 ("leave out of the key what cannot affect the value") is why a source's signature is its own content hash
  rather than a hash including the scale: content does not depend on scale.
- Note 8 is why each cache entry stores the warnings of its whole subgraph: a hit on a parent serves none of its
  inputs, so the parent's entry must carry their warnings; duplicate input signatures are reported once (a diamond
  should not replay one warning twice).
- Note 10 is why `_store()` evicts *before* inserting and refuses values larger than the whole budget, and why the
  node table is deliberately not bounded (the chapter says the budget bounds values, not the graph).
- Note 9 is why there is no in-flight group: evaluation is in-order in one thread, so single-flight would be dead
  weight.

### What worked
- Smoke run: `gain(k=2).call('add', k=1)` built twice through different spellings is the *same* node (`a is b` true),
  the first `evaluate` missed twice, and the second `evaluate` hit once with `runs == 1`.
- Neutral `gain(k=1)` returned its input's grid with `runs == 0`.

### What didn't work
- Nothing failed yet; the first real failures are recorded in the testing steps.

### What I learned
- Signatures must be computed for the *whole* reachable subgraph before evaluation, not lazily per node, because the
  neutral short-cut skips inputs and would otherwise leave a child's signature uncomputed. Computing them up front is
  cheap (hashing only) and keeps `_eval` free of signature recursion.

### What was tricky to build
- Telling the two copies apart: the cache stores frozen tuples, `Result.value` is a fresh list-of-lists from
  `thaw_grid`, and the neutral path returns the *frozen* input value to its parent while the request still thaws it.
  That is exactly note 7's arrangement, and it is easy to break by thawing too early.

### What warrants a second pair of eyes
- The `revision` field in the node hash means re-registering an operation invalidates its nodes even at the same
  version. That is the safe direction (no stale values), but a reviewer should confirm it does not break an expected
  test of node identity across re-registration.
- Warning de-duplication is per unique input signature plus first-occurrence de-duplication inside one operation run;
  two *distinct* nodes that raise the same text will both report it.

### What should be done in the future
- Function arguments (`within` + substitution), demo operations, then the test suite.

### Code review instructions
- Start at `Engine._build` (interning), then `Engine._signatures` (key construction), then `Engine._eval` (memo ->
  cache -> neutral -> inputs -> run -> freeze -> store), then `Engine._store`/`_evict_until` (budget). Run
  `python3 -m unittest discover -s tests` after the tests exist.

## Step 4: Function arguments (`within`), substitution, demo operations

A builder that takes a function cannot have its argument hashed, so `within` runs it once against a placeholder and
re-interns the result with the real input substituted -- the chapter's answer to "functions as arguments against
hashability".

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Implement `eng.within(node, mask, build)` plus the demo operations `add`, `gain`,
`blur`, `threshold` in `gridflow.demo_engine()`.

**Inferred user intent:** Masked local edits that share nodes and cache entries with the same pipeline written
without a mask, and a demo engine that exercises scale-dependent work.

### What I did
- `Engine.within()` builds `inner = build(placeholder)`, substitutes with `_substitute()` (memoized per node hash,
  re-interning only along changed paths), and interns an internal `within` op over `(node, mask, substituted)`.
- Placeholder node is one constant-hash singleton per engine; evaluating it raises `PlaceholderError` (`E_PLACEHOLDER`)
  so an escaped placeholder is an error, never a silent value (note 6).
- `_within_fn()` blends `inner` where the mask is non-zero, else `base`, and raises `ValueError` on a shape mismatch --
  which the evaluator wraps into an `EvalError` naming `within`.
- Created `gridflow/demo.py` and `gridflow/__init__.py` (public exports).

### Why
- Note 6: the placeholder is bound at build time, not at evaluation, because that is what lets
  `within(mask, i => i.gain(2))` share nodes and entries with `gain(k=2)`; the variation that binds at evaluation is
  the one the chapter reports recursing forever on nested calls and losing the sharing.
- Note 4/"Solution": the mask is an ordinary input node, so the masked result is keyed by the mask's signature too.
- Demo `blur` reads `ctx.scale` (quantised) so that a smaller scale shrinks its radius proportionally -- a
  scale-dependent operation whose scale is in both the key and the work.
- Demo `gain` supplies `identity=lambda args: k == 1` so the neutral path is exercised by the demo engine itself.
- Blur is two prefix-sum passes (O(cells)) rather than a naive window mean, because the chapter's whole premise is
  that computations are expensive and the cache, not the operation, should decide what runs.

### What worked
- Smoke run: `eng.within(img, mask, lambda h: h.call('blur', radius=1))` gave `[[2.5, 2.0], [3.0, 2.5]]` for a 2x2
  input with a diagonal mask.

### What didn't work
- N/A at this point.

### What I learned
- Substitution must memoize on the *original* node hash; without it a diamond in the builder's subgraph is walked
  exponentially, and with a shared placeholder a nested `within` in `build` would be re-substituted repeatedly.

### What was tricky to build
- `_substitute` has to recognise the placeholder by identity (`node is hole`), not by hash, and has to leave leaves
  alone (sources have no inputs to rewrite). Returning the original node when no child changed keeps the node table
  small and keeps `a is a` sharing for the unmodified part of the graph.

### What warrants a second pair of eyes
- The internal `within` op is deliberately *not* in `self._ops`, so a user cannot call it by name, while its error
  messages still read `operation 'within' failed`.
- A builder that ignores the placeholder yields a constant subgraph; that is legal and tested.

### What should be done in the future
- Write the tests now (core, cache, scale, warnings, within, demo, errors), run them and fix what fails.

### Code review instructions
- `Engine.within` -> `Engine._substitute` -> `_within_fn` in `gridflow/engine.py`, then `gridflow/demo.py`. Validate by
  building the same pipeline directly and through `within` and comparing `eng.runs()`.

## Step 5: First test suite, and the two expectations it corrected

I wrote the test suite phase by phase (build, evaluate, cache, scale, within, errors, demo, api) and ran it. Two
tests failed, both because my *expectations* were wrong, not the code -- worth recording exactly, since a wrong test is
as much a failure as a wrong implementation.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Cover every clause of the required interface with a test, run
`python3 -m unittest discover -s tests`, and fix what fails.

**Inferred user intent:** Evidence, not claims: tests that pin laziness, interning, cache hits, quantisation, warning
replay, eviction and refusals.

### What I did
- Created `tests/test_build.py`, `tests/test_evaluate.py`, `tests/test_cache.py`, `tests/test_scale.py`,
  `tests/test_within.py`, `tests/test_errors.py`, `tests/test_demo.py`, `tests/test_api.py`.
- Ran `python3 -m unittest discover -s tests`: 79 tests, 2 failures.

### Why
- Each chapter note that imposes an obligation got a test: note 1 (interning/refusal), note 2 (quantise before key and
  work), note 5 (source key = content), note 6 (placeholder substitution), note 7 (frozen store, copy at request,
  neutral not cached), note 8 (warnings replayed from the entry), note 10 (budget and eviction), note 11 (explicit
  evaluation point: a built node has no value).
- `tests/test_api.py` adds a seeded brute-force reference for `blur` (40 random grids x radii x scales), because a
  prefix-sum filter is easy to get subtly wrong.

### What worked
- 77 of 79 passed on the first run, including interning, sharing across "programs", warnings replayed from cache,
  eviction, deep pipelines (150 nodes) and the masked-sharing tests.

### What didn't work
- `python3 -m unittest discover -s tests` reported:
  `FAIL: test_replacing_an_operation_changes_future_nodes (test_build.NodeShapeTests)` ->
  `AssertionError: Lists differ: [[100.0]] != [[200.0]]`.
  Cause: my replacement implementation was `lambda ins, args, ctx: [[cell * 100.0 ...]]`, which ignores `k`, so
  `gain(k=2.0)` over `1.0` is `100.0`, not `200.0`. The code was right (new node, new implementation); the expectation
  was wrong.
- `FAIL: test_blur_radius_one_gives_a_box_mean (test_demo.DemoOperationTests)` ->
  `AssertionError: Lists differ: [[2.25, 1.5, 2.25], [1.5, 1.0, 1.5], [2.25, 1.5, 2.25]] != [[1.0, 1.0, 1.0], ...]`.
  Cause: I expected a mean of the whole grid, but a *clamped* box mean at the border averages only the cells that
  exist: a corner's window is 2x2 (9/4 = 2.25), an edge's is 2x3 (9/6 = 1.5), the centre's 3x3 (9/9 = 1.0).

### What I learned
- The chapter's forces are visible in test results: laziness (a built node has `runs == 0` and `stats()['bytes'] == 0`)
  and sharing (a second script on the same engine adds zero misses) are directly observable, which is what note 11's
  "make evaluation points explicit" buys.
- Boundary clamping in `blur` is a semantic choice I had to make and then pin: window arithmetic at the border is the
  most likely disagreement between my demo op and a caller's assumption.

### What was tricky to build
- The masked-sharing test needed `node.inputs[2]` to *be* the directly built node (`assertIs`), which only holds if
  `_substitute` re-interns rather than rebuilding. Writing the test first made the substitution contract explicit
  (note 6: "re-interning each node on the path").

### What warrants a second pair of eyes
- `test_demo.test_blur_radius_shrinks_with_scale` asserts that `radius=4` at scale 0.5 equals `radius=2` at scale 1 on
  a 5x5 grid; both clamp to the whole grid in the centre cell, which makes the assertion weaker than it looks. The
  scale test in `test_scale.py` uses radius 2 on a 5x5 grid instead, where the radii really differ.

### What should be done in the future
- Review the evaluator's eviction arithmetic, which is the one place where an off-by-one costs cache entries.

### Code review instructions
- Read the tests in the order they were written: `test_build.py`, `test_evaluate.py`, `test_cache.py`, `test_scale.py`,
  `test_within.py`, `test_errors.py`, `test_demo.py`, `test_api.py`. Run
  `python3 -m unittest discover -s tests -v`.

## Step 6: Review of the eviction path finds an over-eviction bug

A read-through of `Engine._store` and `Engine._evict_until` found an arithmetic error that no test caught, because the
eviction tests I had written used budgets that hid it.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Verify the byte-budget logic against note 10 ("a size-aware policy must evict before
inserting") rather than trusting a green test run.

**Inferred user intent:** A cache that keeps as much as the budget allows, since over-eviction silently throws away
work the chapter exists to save.

### What I did
- Changed `self._evict_until(self._cached_bytes + size)` to `self._evict_until(size)` in `Engine._store`.
- Added `tests/test_cache.py::EvictionTests::test_eviction_is_minimal_not_greedy`: six 200-byte entries into a
  1000-byte budget must evict exactly one and end at exactly 1000 bytes.
- Removed a doubled `canonical()` call in `Engine.source`, renamed shadowed loop variables in `Engine._eval`, and added
  the `within()` builder callable check.

### Why
- `_evict_until(needed)` tests `self._cached_bytes + needed > self._cap`, so passing `cached + size` made it test
  `2*cached + size > cap`: it evicted roughly twice as many entries as needed. Note 10 asks for a size-aware policy
  that evicts *before* inserting; evicting far more than asked is the opposite failure and is invisible in `runs`
  counts, since values are still correct.

### What worked
- The new test failed against the old code path in the sense that it could not have passed before the fix: with the
  old arithmetic, six 200-byte entries in a 1000-byte budget ended at 200 bytes with 3 evictions, not 1000 bytes with 1.
- Full suite after the fix: 88 tests, OK.

### What didn't work
- The bug was originally camouflaged by my own test: `test_small_budget_evicts_and_still_returns_correct_values` used a
  300-byte budget holding a single entry, where over- and correct eviction are indistinguishable. No error text to
  record here: the suite was green while the code was wrong.

### What I learned
- Counter-based assertions (`evictions == 1`, `bytes == 1000`) are what pin an eviction policy; asserting only
  "evictions > 0" and "bytes <= cap" hides both over-eviction and under-eviction.
- Reading the code against the chapter's note found what tests missed, which is exactly what the diary's "what
  warrants a second pair of eyes" section is for.

### What was tricky to build
- The arithmetic is easy to get backwards because `_evict_until` both reads and mutates the same accumulator. The
  contract is now stated in the docstring: "evict least-recently-used entries before inserting `needed` bytes", i.e.
  `needed` is the *incoming* size, not the post-insert total.

### What warrants a second pair of eyes
- `_store` returns early (does not cache) when a single value exceeds the whole budget, so its warnings are reported
  immediately instead of being replayed (note 8). That is intended, but a reviewer should check the interaction with
  `stats()['bytes']`, which then stays below the budget while nothing is reusable.

### What should be done in the future
- A GreedyDual-Size policy as a setting, as note 10 suggests, once real workloads can be measured.

### Code review instructions
- `Engine._store` and `Engine._evict_until` in `gridflow/engine.py`, then
  `tests/test_cache.py::EvictionTests`. Validate with `python3 -m unittest discover -s tests`.

## Step 7: Final check

A last pass: full suite from a clean state, a performance sanity run, and a check that the public surface matches
`TASK.md` name for name.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Re-run everything, confirm the interface, and make sure the diary is complete.

**Inferred user intent:** A finished deliverable whose claims are backed by a command's output.

### What I did
- `python3 -m unittest discover -s tests`: `Ran 88 tests in 0.014s -- OK`.
- Sanity run: a 200x200 grid, `blur(radius=5).gain(k=2)`. First evaluation 0.033 s; the same chain written again
  from scratch 0.0002 s with zero extra misses, then `within(...)` over a checkerboard mask 0.044 s, then a
  3000-node chain evaluated correctly (`3000.0`).
- Verified `gridflow/__init__.py` exports `Engine`, `demo_engine`, `Node`, `Result`, `Operation` and the error types,
  and that `Engine(cache_bytes=...)`, `op`, `source`, `call`, `evaluate`, `runs`, `stats`, `within` match `TASK.md`.

### Why
- Note 10's point that the budget bounds values and not the graph: a long session is expected to grow the node table,
  so a 3000-node chain must still work; it does, because signatures are computed bottom-up and the recursion limit is
  raised once at import.

### What worked
- 88 tests green, including the seeded brute-force `blur` reference over 40 random grids, the node-sharing tests, the
  eviction-arithmetic test, and the masked-substitution tests.

### What didn't work
- Nothing failing at this point.

### What I learned
- The second script's cost (0.0002 s) is the pattern working as advertised: the *only* work is signature hashing.

### What was tricky to build
- Nothing new in this step; the tricky work was already recorded in steps 3, 4 and 6.

### What warrants a second pair of eyes
- Recursion: evaluation recurses once per graph level, so a pipeline of tens of thousands of nodes would still hit the
  interpreter's stack before the raised limit helps. An iterative evaluator would remove the bound, at the cost of
  clarity.
- The node table and the source grids it pins are never released (note 10 says the budget does not bound the graph);
  a long-lived session needs a release rule, which is out of scope here.

### What should be done in the future
- A cache policy setting (LRU/GreedyDual-Size), a node-table release rule, and optional parallel input evaluation with
  an in-flight group, as notes 9 and 10 describe, if concurrency ever enters the picture.

### Code review instructions
- Start at `gridflow/engine.py` (`Engine._build`, `Engine._signatures`, `Engine._eval`, `Engine._store`,
  `Engine.within`), then `gridflow/demo.py`, then the tests. Validate with
  `python3 -m unittest discover -s tests`; the suite needs no network and no dependencies.

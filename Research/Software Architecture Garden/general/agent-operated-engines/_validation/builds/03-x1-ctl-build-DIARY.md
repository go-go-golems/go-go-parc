# Diary

## Goal

Build `gridflow`, a standard-library-only Python 3 library for lazy, cached evaluation of small 2D float grids, and
record design, build, test and fix steps in this diary.

## Step 1: Read the task, the diary format, and design the engine

I read `TASK.md` and `DIARY-FORMAT.md` completely, then sketched the architecture before writing any code: an
interned node graph (structure -> node, so equal sources and equal sub-pipelines are the same node), a byte-budgeted
LRU cache keyed by (node key, scale), a per-node run counter, and an `EvalError` that always names the operation that
failed. I also decided that warnings must be cached together with values so that a cache hit returns the same warning
list a cold run would.

### Prompt Context

**User prompt (verbatim):** "You are a software engineer joining a project. Your working directory contains two files:
- TASK.md: the software to build, with its required public interface;
- DIARY-FORMAT.md: how to keep your work diary.
Read both completely first. Keep DIARY.md as you go, one step per phase of work, in that format. Then design, build and test the software in this directory. Work only inside this
directory (do not read or write outside it). Use only the Python 3 standard library. Run your tests and fix what
fails before you finish, and make sure DIARY.md is complete. Your final message must follow the output format at the end of TASK.md."

**Assistant interpretation:** Implement the `gridflow` package exactly as specified by the "Required public interface"
section of TASK.md, with tests under `tests/` run via `python3 -m unittest discover -s tests`, keep a stepwise diary,
and end with a single JSON object in a fenced block.

**Inferred user intent:** A reviewer wants to see a correct, well-factored implementation of a lazy/caching compute
engine plus evidence (tests, diary, tradeoffs) that the engineering process was deliberate.

### What I did
- Read `TASK.md` (public interface, demo ops, output format) and `DIARY-FORMAT.md` (diary skeleton).
- Listed the working directory: only the two markdown files existed; Python 3.10.3 is available.
- Designed the module split: `grid.py` (validation/normalisation), `cache.py` (byte-budgeted LRU + stats),
  `ops.py` (operation records), `node.py` (interned nodes), `engine.py` (evaluation, `Result`, `Context`),
  `demo.py` (`demo_engine()`), re-exported from `gridflow/__init__.py`.

### Why
- TASK.md requires the cache to be described by `stats()` with `hits`/`misses`/`bytes`/`evictions`, which means the
  cache must own its own accounting, so it is its own module rather than inline logic in the engine.
- "Two sources with equal content are the same node" plus "how many times that node's operation actually ran" pushes
  toward interning nodes by a structural key: interning makes identity and counting unambiguous without extra logic.

### What worked
- The interface maps cleanly onto six small modules; no circular imports are needed if `Node` only calls back into
  `Engine` through methods.

### What didn't work
- N/A (no code executed yet).

### What I learned
- The scale-dependent `blur` radius means the evaluation scale must be part of the cache key, otherwise a blurred
  node evaluated at scale 1 would be served for scale 0.5. TASK.md does not say this explicitly; it follows from
  "`ctx.scale` is the evaluation scale" plus "at a smaller scale the radius shrinks proportionally".

### What was tricky to build
- Nothing built yet. The tricky design point identified on paper: `build` in `within(node, mask, build)` needs a
  placeholder node that evaluates to `node`'s value, so the sub-pipeline can be expressed in the same graph and be
  cached normally. I chose a dedicated internal identity operation as the placeholder.

### What warrants a second pair of eyes
- Whether caching warnings with entries (and propagating the aggregate upwards) is the semantics a caller expects
  when re-evaluating a cached subtree.

### What should be done in the future
- Implement the modules, then write tests for laziness, interning, caching, eviction, scale-keying, `within`, and the
  four demo operations.

### Code review instructions
- Start with `gridflow/engine.py::Engine._eval` (the evaluation/caching core) and `gridflow/engine.py::Engine.within`.
- Validate with `python3 -m unittest discover -s tests` once tests exist.

## Step 2: Build the package (grid, cache, ops, node, engine, demo)

I implemented the whole library as six modules plus the package `__init__`, then ran a smoke script that built a
small pipeline on a 2x2 grid and checked values, cache counters, `within`, and the two error paths.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Turn the Step 1 design into working code with the exact public names from TASK.md.

**Inferred user intent:** A reviewer should be able to import `gridflow`, register operations, build pipelines and
get cached, scale-aware results with clear errors.

### What I did
- `gridflow/errors.py`: `EvalError` (evaluation failures, always naming an operation) and `GridError(ValueError)`.
- `gridflow/grid.py`: `normalize_grid` (rectangularity/numeric validation, immutable tuple-of-tuples), `copy_grid`,
  `grid_shape`, `grid_nbytes` (8 bytes/cell), `freeze`/`args_key` (hashable argument keys), `scaled_radius`.
- `gridflow/cache.py`: `LRUCache` keyed by `(node key, scale)`, byte budget, hit/miss/eviction counters, entries that
  hold value *and* warnings.
- `gridflow/ops.py`: `Operation` records with `fn`, `version`, `identity` and a per-registration `gen`.
- `gridflow/node.py`: interned `Node` with `call()`, structural `source_key`/`call_key`.
- `gridflow/engine.py`: `Engine` (registry, interning, `_eff_key`, `_eval`, `_apply`, `runs`, `stats`, `within`,
  scale validation), `Context`, `Result`, internal ops `__placeholder__` and `__within__`.
- `gridflow/demo.py`: `add`, `gain` (neutral at `k == 1`), `blur` (clipped box mean, radius shrunk by `ctx.scale`),
  `threshold`; `demo_engine(cache_bytes=...)`.
- Smoke-tested from `python3 -` (heredoc): values, `runs`, `stats`, `within` and both `EvalError` messages were
  correct — e.g. `EvalError: operation 'add' failed: TypeError: argument 'k' must be a number, got 'x'`.

### Why
- Interning every node by structural key makes "two sources with equal content are the same node" fall out
  automatically and lets `runs(node)` be a plain dict lookup.
- A separate *effective* key layer (recomputed from the current registry revision) means re-registering or
  re-versioning an operation invalidates exactly the affected cache entries and run counters, instead of silently
  serving results produced by the old function.
- Caching warnings with the value keeps `Result.warnings` deterministic: a cache hit must report what a cold run
  would have reported.

### What worked
- All smoke checks passed first time: cached re-evaluation gave `{'hits': 1, ...}` with `runs` still 1, and neutral
  `gain(k=1)` produced the input with `runs == 0`.

### What didn't work
- N/A this step; the only correction while writing was making the "missing operation" token in `_make_call` and in
  `_eff_key` agree (both are now `("<missing>", name, 0)`) so nodes built before their operation exists still key
  consistently.

### What I learned
- Normalising grids to immutable tuples lets identity/neutral nodes and cache hits share value objects safely;
  the mutable copy is only made at the `evaluate` boundary.

### What was tricky to build
- The effective-key layer: a plain build-time key would make a node built before its operation was registered
  permanently broken. I solved it by deriving the key at evaluation time from the current registration (memoised per
  node, invalidated by a registry revision counter).

### What warrants a second pair of eyes
- `_eval` short-circuits neutral nodes by returning the first input's value without evaluating remaining inputs —
  fine for a "neutral" op, but worth confirming it matches expectations.
- `within` evaluates the sub-pipeline on the whole grid and blends afterwards (see tradeoffs).

### What should be done in the future
- Write the unittest suite under `tests/` and run it.

### Code review instructions
- Read `gridflow/engine.py` (`_eff_key`, `_eval`, `_apply`) first, then `gridflow/demo.py::op_blur`.
- Validate: `python3 -c "import gridflow; gridflow.demo_engine()"`.

## Step 3: Write the unittest suite and run it (first run failed)

I wrote three test modules — `tests/test_engine.py` (graph/laziness/evaluation/scale/runs/identity/errors/warnings/
registry), `tests/test_cache.py` (stat counters, sharing, eviction, budget validation) and `tests/test_demo.py`
(demo ops, blur radius scaling, `within`) — then ran the whole suite with the command from TASK.md.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Cover every requirement of the public interface with focused tests and run them with
`python3 -m unittest discover -s tests`.

**Inferred user intent:** The library must be demonstrably correct, and failures must be shown and fixed.

### What I did
- Created `tests/test_engine.py`, `tests/test_cache.py`, `tests/test_demo.py` (89 tests in total at this point).
- Ran `python3 -m unittest discover -s tests -v`.

### Why
- TASK.md names the exact test command, so the suite is discoverable by `unittest` with no extra packages.

### What worked
- 81 of 89 tests passed immediately, including the tricky ones (cache hits, scale-keyed caches, identity
  short-circuit, `within` masking, warning propagation through cache hits).

### What didn't work
- `python3 -m unittest discover -s tests -v` ended with:
  `Ran 89 tests in 0.201s` / `FAILED (failures=6, errors=2)`.
- Error: `test_shared_subpipeline_is_evaluated_once` — `gridflow.errors.EvalError: operation 'add' is not registered`
  (I used a bare `Engine()` and then called `add`).
- Error: `test_equal_sources_are_the_same_node` — `gridflow.errors.GridError: source: row 0 is not a list or tuple
  (got int)` (I wrote `eng.source((1, 2))`, which is not a grid of rows).
- Failure: `test_inner_operation_failure_is_named` — `AssertionError: "'bad'" not found in "operation 'add' is not
  registered"` (again `add` was not registered).
- Failure: `test_non_neutral_arguments_run_the_operation` — `AssertionError: 0 != 1` (I asserted on the call log of
  the *other* helper operation).
- Failure: `test_version_bump_invalidates_cached_results` — `AssertionError: 1 != 2` (run counters were keyed by
  effective key, so a version bump started a fresh counter).
- Failure: `test_blur_radius_two_sees_further` — `AssertionError: 2.7777777777777777 not less than 0.0` (my expected
  blur values were arithmetically wrong).
- Failure: `test_within_build_receives_a_placeholder_with_the_base_values` — `AssertionError: Lists differ:
  [[1.0, 0.0], [1.0, 4.0]] != [[1.0, 2.0], [1.0, 4.0]]` (wrong expectation: the mask selects the *sub*-pipeline).
- Failure: `test_within_result_is_cached` — `AssertionError: 2 != 1`.

### What I learned
- Seven of the eight problems were wrong test expectations, not library bugs — which is itself informative: the
  library semantics (mask selects the sub-pipeline, run counters, `Engine()` registering nothing) behaved as designed.
- The one genuine design question was `runs()` after a version bump; see Step 4.

### What was tricky to build
- `test_within_result_is_cached` failed because the *cold* evaluation of a `within` node already produces a hit: the
  base grid is reachable twice (directly and through the placeholder), so its second lookup is a legitimate cache
  hit. The test now compares hits before/after a warm evaluation instead of assuming a cold count of zero.

### What warrants a second pair of eyes
- Whether the wrong-expectation cases (blur arithmetic, mask direction) are really the semantics a reviewer expects.

### What should be done in the future
- Fix the failing tests and the `runs()` keying decision, then re-run.

### Code review instructions
- `python3 -m unittest discover -s tests -v` reproduces everything above.

## Step 4: Fix the failures and re-run

I corrected the seven wrong test expectations, switched the run counter to be cumulative per node object, and
re-ran the suite.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Make the suite green without weakening what it checks.

**Inferred user intent:** Trustworthy tests and a library whose observable semantics are coherent.

### What I did
- Code change in `gridflow/engine.py`: run counts are stored per node (`node.run_count`) instead of per effective
  key, so `eng.runs(node)` is cumulative for that node across re-registrations; `_apply` no longer needs the
  effective key.
- Test fixes: `demo_engine()` instead of `Engine()` where `add` is used; `eng.source(((1, 2),))`; assert on the
  operation's own call log; corrected blur arithmetic (`25/4` corner case was wrong: a radius-1 corner window on a
  5x5 grid does not reach the centre, radius 2 averages over 9 cells); corrected `within` expectations to
  `[[1.0, 0.0], [1.0, 4.0]]`; compare hit counts before/after a warm evaluation; fixed the `combine` expectation to
  `[[5.0, 7.0]]`.

### Why
- TASK.md's wording "how many times that node's operation actually ran" reads as a property of the node, not of one
  registration version, so cumulative counting is the least surprising choice.

### What worked
- `python3 -m unittest discover -s tests` → `Ran 89 tests in 0.179s` / `OK`.

### What didn't work
- One intermediate run still failed with `AssertionError: Lists differ: [[5.0, 7.0]] != [[3.0, 5.0]]` for
  `test_shared_subpipeline_is_evaluated_once`; the combine arithmetic in the expectation was wrong (it is
  `(1+1)+(1+2)`), not the engine.

### What I learned
- Writing tests against hand-computed grid arithmetic is error-prone; the fixes were all in the expectations.

### What was tricky to build
- Nothing beyond the above; the counter change was a two-line edit once the keying question was settled.

### What warrants a second pair of eyes
- `runs()` semantics for nodes evaluated at several scales: they add up (`2`), which matches "how many times the
  operation actually ran".

### What should be done in the future
- Add a few robustness tests (long chains, tuple outputs, source snapshotting) and tidy the internals.

### Code review instructions
- `gridflow/engine.py::Engine.runs` and `Engine._apply`; then re-run the suite.

## Step 5: Tidy the internals and extend the suite to 95 tests

I removed the two engine-level side tables (`_eff_keys`, `_runs`) in favour of per-node fields, wrapped long lines,
and added robustness tests: source snapshotting, op functions returning tuples, a 60-operation chain, rejection of
non-node extra inputs, per-operation context isolation, and warnings coming from inside a `within` sub-pipeline.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Make the implementation easier to review without changing public behaviour, and close
gaps in coverage.

**Inferred user intent:** A maintainable library, not just a passing one.

### What I did
- `gridflow/node.py`: `Node` gained `_key_revision`, `_cached_key` and `run_count` slots; removed the unused
  `effective_key()` experiment (the effective key belongs to the engine, which owns the registry).
- `gridflow/engine.py`: `_eff_key` memoises on the node, `runs()` reads `node.run_count`, `MISSING_MARKER`
  replaces the tuple constant, long lines wrapped.
- `tests/test_engine.py`, `tests/test_demo.py`: five new tests (source snapshot, tuple output, 60-op chain,
  extra-input type check, context isolation, `within` sub-pipeline warnings).
- Verified a 200x200 pipeline: cold evaluation 0.199 s, ten cached evaluations 0.0062 s, `stats()` shows 1.28 MB held.

### Why
- Keeping derived state on the node removes a whole class of `id()`-keyed dictionary bugs and makes the memo
  invalidation (`_key_revision` vs `Engine._revision`) explicit at the place it is used.

### What worked
- `python3 -m unittest discover -s tests` → `Ran 95 tests in 0.181s` / `OK`; the doctest in
  `gridflow/__init__.py` also passes (`TestResults(failed=0, attempted=4)`).

### What didn't work
- A `python3 -m doctest gridflow/__init__.py` invocation raised `ImportError: attempted relative import with no known
  parent package`; running the doctest through the imported module
  (`python3 -c "import doctest, gridflow; print(doctest.testmod(gridflow))"`) works, which is the supported way.

### What I learned
- Cache hits are dominated by copying the result out (`evaluate` returns a defensive copy), which is exactly the
  cost the design intends to pay to keep cached values immutable.

### What was tricky to build
- Nothing failed here; the only judgement call was deleting the `Node.effective_key()` helper because it would have
  forced `Node` to ask the engine about operation tokens.

### What warrants a second pair of eyes
- Long pipelines are evaluated recursively (`_eval` and `_eff_key` recurse once per level); 60 levels are fine, a
  few thousand levels would hit Python's recursion limit.

### What should be done in the future
- If pipelines ever get very deep, convert `_eval`/`_eff_key` to iterative traversals.

### Code review instructions
- Diff-relevant files: `gridflow/node.py` (slots) and `gridflow/engine.py` (`_eff_key`, `runs`, `_apply`).
- Validate: `python3 -m unittest discover -s tests`.

## Step 6: Settle the scale-dependent blur radius rule and prune dead API

While reviewing the blur semantics against TASK.md ("radius in grid cells at scale 1; at a smaller scale the radius
shrinks proportionally") I changed the radius rule from round-half-up to truncation of `radius * scale`, added a
floating-point epsilon, pruned unused cache helpers, and tightened two docstrings.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** The radius at a smaller scale must actually shrink, including for small radii, and the
module surface should contain only what is used.

**Inferred user intent:** Behaviour that matches the plain reading of the specification, and a code base a reviewer
can read without wondering about unused methods.

### What I did
- `gridflow/grid.py::scaled_radius`: `int(math.floor(radius * scale + 1e-9))` (was `floor(r*s + 0.5)`), documented
  that radius 1 at scale 1/2 collapses to 0 (no-op) and that the epsilon protects against
  `10 * 0.3 == 2.9999999999999996`.
- `gridflow/cache.py`: removed unused `peek`, `clear`, `reset_stats`, `__contains__`, `__len__`, `nbytes`; added a
  `bool` guard on the budget type.
- `gridflow/node.py`: docstrings for `Node` and `Node.call` now state that the definition is immutable and that the
  engine keeps memoised key / run count on the node.
- Two new tests: `test_blur_shrinks_proportionally_equals_a_smaller_radius` (radius 2 at scale 0.5 == radius 1 at
  scale 1) and `test_blur_radius_one_collapses_to_no_blur_at_half_scale`.

### Why
- With round-half-up, a radius-1 blur was identical at scale 1 and scale 0.5, which contradicts "at a smaller scale
  the radius shrinks proportionally". Truncation makes the proportional shrink visible for every radius.
- Verified the mapping directly: `[(1,1.0,1),(1,0.5,0),(2,0.5,1),(4,0.5,2),(10,0.3,3),(4,0.25,1)]`.

### What worked
- `python3 -m unittest discover -s tests` → `Ran 97 tests in 0.208s` / `OK`, and the new proportionality test passes.

### What didn't work
- Nothing failed in this step.

### What I learned
- Binary floating point would silently drop a radius for inputs like `radius=10, scale=0.3` without the epsilon.

### What was tricky to build
- The judgement call itself: rounding modes for a scaled integer radius are not specified by TASK.md, so I chose the
  literal truncation and documented it here and in the docstring.

### What warrants a second pair of eyes
- Whether "shrinks proportionally" should have a floor of 1 (never disable a blur at coarse scale) instead of
  allowing radius 0.

### What should be done in the future
- If a consumer needs a floored radius, make the rounding policy a parameter of `op_blur`.

### Code review instructions
- `gridflow/grid.py::scaled_radius` and `gridflow/demo.py::op_blur`; then
  `python3 -m unittest tests.test_demo -v`.

## Step 7: Final check

I re-ran everything from a clean state (byte-code caches deleted) and verified the delivered tree.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Confirm the required command passes, the package imports cleanly, the tree contains only
what it should, and the diary is complete.

**Inferred user intent:** Ship a green, self-contained library with an auditable trail.

### What I did
- `find . -name "__pycache__" -type d -exec rm -rf {} +`
- `python3 -m unittest discover -s tests -v` → `Ran 97 tests in 0.184s` / `OK` (43 in `tests/test_engine.py`,
  14 in `tests/test_cache.py`, 40 in `tests/test_demo.py`).
- `python3 -c "import doctest, gridflow; print(doctest.testmod(gridflow))"` →
  `TestResults(failed=0, attempted=4)`.
- `python3 -m compileall -q gridflow tests` → clean.
- Verified the tree: `gridflow/{__init__,cache,demo,engine,errors,grid,node,ops}.py` and
  `tests/{test_cache,test_demo,test_engine}.py`.

### Why
- TASK.md mandates the `unittest discover` command and standard library only; both hold (imports are `math`,
  `numbers`, `collections`, `typing` and the package itself).

### What worked
- Everything: 97/97 tests, 4/4 doctests, compilation clean.

### What didn't work
- N/A.

### What I learned
- The final state has no third-party imports and no network use, so it runs anywhere CPython 3.8+ runs.

### What was tricky to build
- N/A in this step; the tricky parts are documented in Steps 2, 4 and 6.

### What warrants a second pair of eyes
- The `within` implementation computes the sub-pipeline on the whole grid and blends afterwards, so `runs()` counts one
  sub-pipeline execution even when only a few cells are selected.
- `runs()` counts are cumulative per node object, so re-registering an operation and re-evaluating keeps adding.
- Radius rounding for `blur` at reduced scale is truncation (Step 6).

### What should be done in the future
- Optional: a `clear_cache()` / `reset_stats()` public method, an iterative evaluator for very deep pipelines, and
  thread-safety if the engine is ever shared between threads.

### Code review instructions
- Public entry points: `gridflow/__init__.py`; core logic: `gridflow/engine.py`; demo maths: `gridflow/demo.py`.
- Validate: `python3 -m unittest discover -s tests` (expect `Ran 97 tests ... OK`).

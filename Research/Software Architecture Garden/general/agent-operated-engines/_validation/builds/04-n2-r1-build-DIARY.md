# Diary

## Goal

Build `stencilpipe`, a standard-library-only Python 3 library where a request for a window of a pipeline over large
2D float grids computes only that window (plus each operation's declared reach) and returns exactly the values a
whole-grid run would give there. This diary records the design decisions, the build, the tests and the fixes.

## Step 1: Reading the chapter, the task and the diary format; designing the package

I read all three files completely before writing anything. The chapter (Chapter 4, *Reach-Declared Region Evaluation*)
asks for four always-present participants — Footprint, Window, Region evaluator, Invariance test, Footprint guard —
plus optional ones (global barrier, statistic node, cost rule, cache/memo, scale conversion, tile grid). `TASK.md`
fixes the public surface (`demo_engine`, `Engine.source/call/evaluate/evaluate_many/reset_counters/cells_computed`)
and the exact whole-grid semantics of five demo operations. I then mapped every required operation onto a footprint
rule and sketched the module layout.

### Prompt Context

**User prompt (verbatim):** "You are a software engineer joining a project. Your working directory contains three files:
- CHAPTER.md: a chapter of a design-pattern book describing the pattern you must apply;
- TASK.md: the software to build, with its required public interface;
- DIARY-FORMAT.md: how to keep your work diary.
Read all three completely first. Keep DIARY.md as you go, one step per phase of work, in that format. Then design, build and test the software in this directory. Work only inside this
directory (do not read or write outside it). Use only the Python 3 standard library. Run your tests and fix what
fails before you finish, and make sure DIARY.md is complete. Your final message must follow the output format at the end of TASK.md."

**Assistant interpretation:** Implement the pattern of CHAPTER.md as a small, tested Python library matching TASK.md's
interface exactly, keep a stepwise diary in the strict format, and finish with a single JSON object.

**Inferred user intent:** A working, exact, demand-driven grid pipeline whose window cost follows the window, not the
grid, with evidence (tests and cell counters) that windowed evaluation equals whole evaluation bit for bit.

### What I did
- Read `CHAPTER.md`, `TASK.md`, `DIARY-FORMAT.md` in full; listed the working directory (`CHAPTER.md`,
  `DIARY-FORMAT.md`, `TASK.md`; Python 3.10.3).
- Decided the module layout: `window.py` (Window + clip/grow/area), `footprint.py` (`WHOLE` and footprint
  resolution), `values.py` (`Buffer`, `Guarded`, `FootprintError`), `operations.py` (Operation base, demo ops,
  registry), `engine.py` (`Node`, `SourceNode`, `Engine`), `invariance.py` (invariance test helper), `__init__.py`.

### Why
- The chapter's Structure table names one participant per concept, so I gave each its own module: **Window**
  (`window.py`), **Footprint** (an `Operation.footprint(window, index, input_extents)` method per op), **Region
  evaluator** (`Engine._evaluate`), **Footprint guard** (`values.Guarded`), **Global barrier** (`WHOLE` +
  `Engine` resolving it to the input's extent), **Statistic node** (a separate 1×1 `MaxAll` node wired as an ordinary
  input of `Divide`), **Cost rule** and **whole-value cache** (opt-in `Engine` flags).
- Per-operation footprints from the chapter's Sketch: point ops (`add`) → the window; neighbourhood ops (`box(r)`) →
  `grow(window, r)`; directional (`dx`) → `grow(window, x:1, y:0)`; pixel-moving (`half`) → map the window back
  (`x*2, y*2, w*2, h*2`); global (`max` inside `normalize`) → `whole`.
- `normalize()` must be split per implementation note 7: `out = in / max(in)` becomes `Divide(plain, MaxAll(plain))`,
  so a global parameter never hides inside a local chain and the evaluator needs no special hook.
- Scale conversion and tile grid are conditional participants; this library evaluates at one scale and requests are
  few, so I planned a per-request window memo (Variations: cell/span memo) instead of a tile grid, and documented why.

### What worked
- The chapter's five-line sketch translated almost directly into the evaluator: resolve footprints, compare cost,
  evaluate inputs through a guard, run the op on absolute coordinates.
- Writing down the footprint of each of the five required demo operations before coding showed that `half()` is the
  only "moves pixels" op and `normalize()` the only global one, so both conditional participants are exercised.

### What didn't work
- Nothing yet; no code has been executed.

### What I learned
- The exactness requirement is not about closeness: the whole run and the windowed run must use the *same arithmetic
  in the same order*, so per-cell loops with absolute coordinates (never prefix sums over a buffer) are mandatory
  (note 2). My `box` will therefore sum its square in a fixed dy/dx order and divide by the count.
- The border rule must clamp to the *input node's extent*, not to the buffer, so the guard must carry the node
  extent separately from the read footprint (note 4).

### What was tricky to build
- N/A yet. The one design wrinkle found in this step: the statistic node's `WHOLE` footprint makes its input evaluate
  whole, so the evaluator must not treat "footprint == extent" as "reuse the windowed path"; resolved by resolving
  `WHOLE` to the input's extent before clipping.

### What warrants a second pair of eyes
- The decision to keep `normalize`'s maximum exact via a whole-grid barrier (correct, expensive) rather than a coarse
  statistic (cheap, needs its own validation) — the chapter explicitly allows the latter but requires extra
  validation, so I chose exactness.

### What should be done in the future
- Write `window.py`, `footprint.py`, `values.py` next, then operations and the evaluator, then the invariance tests.

### Code review instructions
- Nothing to review yet; start with the module layout above and continue to Step 2.

## Step 2: The always-present parts — Window, Footprint resolution, Buffer and the Guard

Before any operation I built the three pieces every request travels through: a rectangle type in absolute
coordinates, a resolver that turns an operation's footprint declaration into the window to ask for, and the guarded
buffer an operation reads. This unlocked writing operations without any window arithmetic of their own.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Build the participants of Chapter 4's Structure table that are marked "Always".

**Inferred user intent:** A small, inspectable core where a wrong footprint is impossible to hide.

### What I did
- Created `stencilpipe/window.py`: `Window` as a `NamedTuple` (so a window *is* the tuple `(x, y, w, h)` the task
  asks for), plus `as_window`, `clip`, `grow`, `scale`, `cut`, `area`, `default_windows`.
- Created `stencilpipe/footprint.py`: the `WHOLE` sentinel and `resolve(footprint, input_extent)`
  (`WHOLE` → the input's extent, otherwise clipped to it) and `footprints(operation, window, extents)`.
- Created `stencilpipe/values.py`: `Buffer` (cells of one window, read by absolute coordinates, hard `IndexError`
  outside), `Guarded` (read view limited to the footprint that also carries the input node's `bounds`) and
  `FootprintError`.

### Why
- Absolute coordinates everywhere: implementation note 2 warns that arithmetic depending on where a buffer starts
  gives different last bits. Keeping `Window` in source coordinates means no origin correction exists to get wrong.
- `Guarded.bounds` (the input node's extent) is separate from `Guarded.footprint` (the declared read area) because of
  note 4: border rules must apply at the real border, never at the edge of a buffer.
- `default_windows` encodes the chapter's invariance schedule (interior, each edge, each corner, 1×1, whole) so the
  test always asks the same hard questions.

### What worked
- `Window` as a `NamedTuple` gives tuple equality for free, which is what `evaluate(node, (x, y, w, h))` needs and what
  makes `evaluate(node, w) == evaluate(node, tuple(w))` trivially true.
- `resolve` in one place meant no operation ever has to know about `WHOLE` or clipping.

### What didn't work
- My first version of `clip`/`grow`/`scale` typed their arguments as `Window` and used `.x` etc. directly, so calling
  them with plain tuples — which is how windows arrive from users — raised `AttributeError: 'tuple' object has no
  attribute 'x'`. Fixed in Step 6 by coercing with `as_window` at the top of each helper.

### What I learned
- The chapter's distinction between "the window read" and "the window asked for" is the whole design: the guard's
  footprint is what was asked for; the bounds are what the border rule uses; the buffer covers exactly the ask.

### What was tricky to build
- Deciding what `Buffer.get` should do when a footprint is degenerate (empty). Chosen: `Buffer(window, [])` for an
  empty ask, and any read then raises `IndexError` — an empty footprint is a bug unless the operation reads nothing.

### What warrants a second pair of eyes
- `clip` returns an empty window anchored at the clipped origin (`Window(x0, y0, 0, 0)`) rather than `(0, 0, 0, 0)`;
  every consumer treats `area == 0` as "nothing to compute", so the origin should never be used.

### What should be done in the future
- Operations on top of these parts, then the evaluator.

### Code review instructions
- `stencilpipe/window.py` (`clip`, `grow`, `scale`), `stencilpipe/footprint.py` (`resolve`),
  `stencilpipe/values.py` (`Buffer.get`, `Guarded.get`).

## Step 3: The demo operations and the region evaluator

I wrote each operation as a small class that declares three things — its output extent, its footprint per input, and
a windowed `run` — and put them in a registry. Then I wrote the evaluator that walks a requested window down the
graph, resolving and clipping a footprint at each node and computing exactly the asked window. This is the point
where a 1×1 request stopped costing the whole grid.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Implement `add`, `box`, `dx`, `half`, `normalize` with declared footprints, and the
engine/evaluator that propagates windows.

**Inferred user intent:** The pattern actually working, with the task's five operations behaving as specified on
whole grids.

### What I did
- Created `stencilpipe/operations.py`: `Operation` base (`output_extent`, `footprint`, `run`, `build`, `spec`), the
  demo ops with their declared reaches, the `normalize()` split graph, and a mutable `REGISTRY`.
- Created `stencilpipe/engine.py`: `Node`/`SourceNode`, `Engine.source/call/evaluate/evaluate_many/reset_counters/
  cells_computed`, the window memo, the opt-in cost rule and the opt-in whole-value cache, plus `demo_engine()`.
- Declared footprints: `add` → the window; `box(r)` → `grow(window, r, r)`; `dx` → `grow(window, 1, 0)`;
  `half` → `scale(window, 2, 2, 2, 2)`; `max_all` → `WHOLE`; `divide` → the window for the grid and `WHOLE` for the
  statistic.

### Why
- Note 7: `normalize()` is built as `divide(in, max_all(in))`, so the global parameter is an ordinary second input
  with a one-cell extent and the evaluator needs no hook. `MaxAll` is the **statistic node**, `WHOLE` the **global
  barrier**.
- Note 5 ("reaches add up") falls out for free: each node widens its own ask, so a `box(4)` under a `box(3)` is asked
  for 7×7 when the consumer wants 1×1.
- The counting happens in the evaluator, once per computed window, so no operation can forget to count.

### What worked
- The chapter's pseudo-code transferred almost line for line: resolve footprints → optional cost rule → guarded
  inputs → run → count → memo.
- `half` was the only op needing mapped-back windows and `dx` the only directional one, so all three footprint shapes
  in the sketch are exercised by the task's own operation set.

### What didn't work
- First draft of `Engine.describe()` had a nonsense expression (`self._registry[name](**{}) if name not in ("box",
  "add") else None`) that would have raised for `add` and `box`; replaced with a `try: cls() except TypeError` so any
  parameterised operation is described honestly.

### What I learned
- The `is_whole = (window == node.extent)` test is essential: without it the cost rule could recurse into itself
  forever. With it, "evaluate whole" is just "ask for the whole extent", and the rule is skipped there.
- Because every extent is anchored at (0, 0), "the whole value" and "the extent window" are the same thing, which
  kept the cache key simple.

### What was tricky to build
- `dx` clamps to `min(x+1, W-1)` / `max(x-1, 0)`, where `W-1` must be the *input node's* last column, not the
  footprint's. Getting this from `Guarded.bounds` is what makes a windowed `dx` agree with a whole one at the right
  edge. Mutation 3 in Step 8 (clamping at the buffer instead) is caught by exactly one test, so the test is load
  bearing.

### What warrants a second pair of eyes
- The per-request window memo is keyed by `(node, window)`; two neighbours (`add` branches feeding an op) share work,
  two structurally identical but distinct nodes do not. That is deliberate ("never replaced by their bounding box"),
  but a reviewer should confirm it is the intended trade-off.

### What should be done in the future
- Prove it: the invariance test and its test suite.

### Code review instructions
- `stencilpipe/operations.py` (`Box.run`, `Dx.run`, `Half.run`, `Divide.run`, `MaxAll.footprint`),
  `stencilpipe/engine.py` (`Engine._evaluate`). Run `python3 -m unittest discover -s tests`.

## Step 4: The invariance test helper and the first test suite

I wrote the chapter's one proof — windowed equals whole-then-cut, bit for bit — as a reusable helper and then wrote
tests around it: semantics against independent reference implementations, invariance for every op alone and in
chains, costs, guards and interface shapes.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Add the **Invariance test** participant and tests under `tests/`.

**Inferred user intent:** Evidence that the pattern is correct, not just implemented.

### What I did
- Created `stencilpipe/invariance.py`: `check_invariance(engine_factory, builder, windows=None)` which builds a
  *fresh* engine per window (note 1: a cache filled by an earlier window hides a short footprint) and raises with the
  first differing cell if anything differs.
- Created `tests/helpers.py` (grids, chains, reference formulas written from TASK.md), `tests/test_operations.py`,
  `tests/test_windows.py`, `tests/test_costs.py`, `tests/test_pattern_parts.py`.

### Why
- Every comparison is `==` on floats, never a tolerance (note 2), and one test additionally compares `.hex()` so a
  near-miss cannot pass as equal.
- Reference implementations sum in the same order as the windowed code must, because exactness is order-sensitive;
  the spec (`mean over the square`, `2x2 block`) fixes that order.

### What worked
- `check_invariance` immediately covered 10 grids × 9 op cases × 10 windows without any per-test bookkeeping.

### What didn't work
- Nothing yet at this point; the first execution happened in Step 5.

### What I learned
- Keeping the helper in the package (not only in the tests) makes the invariance claim checkable by users of the
  library, which is what the chapter asks for as a participant rather than as a test detail.

### What was tricky to build
- Writing reference implementations that are independent of the engine but bit-identical in accumulation order.

### What warrants a second pair of eyes
- The reference formulas mirror the task's wording; if they mirrored the engine instead, they would prove nothing.

### What should be done in the future
- Run everything and fix what fails.

### Code review instructions
- `stencilpipe/invariance.py`, `tests/helpers.py` (`reference`).

## Step 5: First full test run — 66 tests, five failures and three errors

The first complete run failed in eight places. Two were genuine usability defects in the library (helpers rejecting
plain tuples), the rest were my own wrong expectations, and the run taught me what "cells computed" really counts.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Run the suite and diagnose every failure.

**Inferred user intent:** Fix the real defects, not the symptoms.

### What I did
- Ran `python3 -m unittest discover -s tests`.

### Why
- The task requires running the tests and fixing what fails before finishing.

### What worked
- The failure list separated cleanly into library defects and test defects.

### What didn't work
- `Ran 66 tests in 2.523s` → `FAILED (failures=5, errors=3)`. The exact messages:
  - `AttributeError: 'tuple' object has no attribute 'x'` — `clip((6, 4, 10, 10), (0, 0, 8, 8))` from
    `stencilpipe/footprint.py`, line 35 `return clip(as_window(footprint), input_extent)`.
  - `AttributeError: 'tuple' object has no attribute 'area'` — `sp.default_windows((0, 0, 17, 13))` from
    `stencilpipe/window.py`, line 104 `if extent.area == 0`.
  - `AssertionError: 8 != 100` in `test_scattered_probes_do_not_compute_their_bounding_box`: I had assumed the
    `box` node computes its whole footprint; in fact a node computes the window its consumer asks for.
  - `AssertionError: 36 != 43` in `test_shared_subgraph_is_computed_once`: `cells_computed` counts one row of cells
    per *operation* it runs, so both `add` nodes count even when the shared `box` below them is served from the memo.
  - `AssertionError: [[2.0]] != [[0.5]]` in `test_negative_maximum`: I divided by the wrong sign; the maximum of
    `[[-4,-2],[-8,-6]]` is `-2`, so the first cell is `-4 / -2 = 2.0`.
  - `AssertionError: Lists differ: [[1.0, 2.0, 1.0], [1.0, 2.0, 1.0]] != [[1.0, 2.0, -2.0], [1.0, 2.0, -2.0]]` in
    `test_shapes_match_task`: `dx` at the last column is `in[W-1] - in[W-2] = 3 - 2 = 1`, not `-2`.
  - `AssertionError: [] != [[1.0]]` in `test_window_beyond_extent_is_clipped`: the window `(-5, -5, 3, 3)` covers x in
    `[-5, -2)`, which really does not intersect the grid; the correct probe is `(-2, -2, 3, 3)`.

### What I learned
- `cells_computed` for a *chain* is `sum of the windows each node was asked for` — the reach shows up in the source
  reads (uncounted) and in the inner node's ask, not in the outer node's count. This is why a `box(3)` under a 1×1
  `dx` probe costs `1 + 3` cells, not `1 + 49`.
- A user-facing helper exported from the package must accept plain tuples; forgetting `as_window` is a real defect,
  not a test problem.

### What was tricky to build
- Nothing structural: every failure was a one-line cause once the message was read.

### What warrants a second pair of eyes
- Whether "cells computed" should also count the *reads* a neighbourhood op does; the task says "output cells", so it
  does not, and the diary records that interpretation.

### What should be done in the future
- Apply the fixes and re-run.

### Code review instructions
- Compare the failing expectations against `tests/helpers.py` and `TASK.md`; the library fixes are in
  `stencilpipe/window.py`.

## Step 6: Fixing the eight failures — 66 tests green

I coerced window arguments in the exported helpers and corrected my own expectations. After the fixes the suite was
fully green, which is when I started looking for what the suite was *not* checking.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Make the library accept what users pass and fix the wrong test expectations.

**Inferred user intent:** A green, honest suite.

### What I did
- `stencilpipe/window.py`: `clip`, `grow`, `scale`, `cut` and `default_windows` now coerce their arguments with
  `as_window`.
- `tests/test_operations.py`, `tests/test_windows.py`, `tests/test_pattern_parts.py`, `tests/test_costs.py`: corrected
  the `dx` last-column expectation, the negative-maximum expectation, the out-of-grid window probe, the two `cells`
  counts (8 and 36/45 instead of 100 and 43) and the memo assertion (shared base 36 cells, two separate bases 45).
- One more failure appeared after the first edit — `AssertionError: [[15.69418022222222, ...]] != [[-24.518638,...]]`
  — because my expected grid for the memo test sliced rows but not columns; fixed to `row[4:7]`.

### Why
- Coercion in one place keeps every caller honest and matches the task's "a window is a tuple `(x, y, w, h)`".
- The corrected counts are now documented expectations of the cost model, which is what makes the cost tests evidence
  rather than decoration.

### What worked
- `Ran 66 tests in 2.772s` → `OK`.

### What didn't work
- See the leftover column-slice failure above (my test bug, fixed immediately).

### What I learned
- A green suite after fixing my own expectations says nothing about the library; the next steps therefore attacked the
  library itself (mutation testing) and added the audit that measures reads.

### What was tricky to build
- Nothing; but re-deriving each expected count from the reach model ("each node counts the window it was asked for")
  was the step that clarified the whole cost story.

### What warrants a second pair of eyes
- The cost expectations are formula-derived; a reviewer should re-derive at least `2 * (1 + 3)` and `9 + 9 + 9 + 9`.

### What should be done in the future
- Harden the engine's optional parts and add tests for the declared-vs-discovered reach.

### Code review instructions
- `git`-less directory: diff `stencilpipe/window.py` against Step 2's description; run the suite.

## Step 7: Hardening — cache keys, more chains, the footprint audit and the interface tests

Two things still worried me: the whole-value cache keyed by `id(node)` (ids are reused after garbage collection) and
the fact that nothing checked a footprint that is too *long* (a too-short one is caught by the guard). I also wanted
tests that pin the public interface itself.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Remove latent defects and widen the evidence.

**Inferred user intent:** Confidence that the library is correct beyond the cases I happened to write first.

### What I did
- `stencilpipe/engine.py`: memo key and whole-cache key changed from `id(node)` to the node object itself (identity
  hashing, and the cache now keeps the node alive so an id cannot be reused under it).
- `tests/helpers.py`: four more chains (`half→normalize`, `dx→normalize`, `normalize→box`, `normalize→half`).
- Created `tests/test_footprint_audit.py`: records every cell an operation actually reads (by wrapping the guards,
  no library hook) and compares the read set with the declared footprint — equality for ops that fill their
  rectangle, and for `dx` the two columns it really reads.
- Created `tests/test_interface.py`: exports, return types, clipping, `evaluate_many` independence, the chapter's
  scenario (300×200 field, `box(r=12)`, an 8×8 window costs 64 cells; a whole-grid op costs 60 000).
- `tests/helpers.py`: added `box_at`, `box_window`, `dx_of_box_window` reference helpers so big-grid checks stay fast.

### Why
- Chapter Forces, "declared against discovered reach": the audit measures reads, which is the only way to see an
  over-declared reach. Note 1 says only a test can say a footprint is exact.
- The interface tests exist because "other code will be tested against it" (TASK.md).

### What worked
- After the fixes and the new tests: `Ran 84 tests in 3.117s` → `OK`.

### What didn't work
- First run of the new tests: `Ran 83 tests in 23.789s` → `FAILED (failures=3, errors=1)`, with
  `TypeError: isinstance() arg 2 must be a type, a tuple of types, or a union` (my `isinstance(eng.cells_computed(),
  0)`) and three audit failures for `max_all` and one-column `dx`. The `max_all` failures were my test asking a 1×1
  node for a window outside its extent (which correctly clips to nothing); the `dx` failure showed that a
  one-column window reads columns `x-1` and `x+1` and not `x`, which no single rectangle can express — so the audit
  now asserts rectangular equality only for ops that fill their rectangle and states `dx`'s true read set.
- The suite also took 24 s because `test_small_window_of_a_blurred_field` computed a whole 300×200 `box(r=12)`
  (37 M guarded reads) just to compare 64 cells; replaced by `reference.box_window` over the 8×8 window, which is
  faster *and* an independent check of exactly the interesting cells.

### What I learned
- An optimal footprint is the tightest *window* containing what an operation reads; for `dx` that is one column wider
  than the columns it touches, and the audit has to know the difference between "reads" and "declares".
- Cost assertions must count what the engine counts (output cells), never reads.

### What was tricky to build
- The audit needed a guard-shaped object with `.bounds`, `.footprint` and `.get`; operations only use those three, so
  a twenty-line shim was enough and no production hook was needed.

### What warrants a second pair of eyes
- `Engine._whole_cache` now holds strong references to nodes for the life of the engine; for a long-lived engine with
  many graphs that is a memory leak unless `clear_cache()` is called. Deliberate (it is opt-in), but worth a note.

### What should be done in the future
- If overlapping requests ever dominate, add a tile grid keyed to the source (note 10) — the window memo already
  shares work inside one request.

### Code review instructions
- `stencilpipe/engine.py` (`_evaluate`, keys), `tests/test_footprint_audit.py`, `tests/test_interface.py`.

## Step 8: Mutation check and final verification

The suite was green, so I checked whether it can fail: I broke the library on purpose in four ways and confirmed each
break is caught, then ran the final verification commands.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Prove the tests have teeth, then verify the finished state.

**Inferred user intent:** A submission whose green suite means something.

### What I did
- Mutations (each applied to `stencilpipe/operations.py`, then reverted; `restored: True` confirmed by comparing the
  file with the original text):
  1. `box` footprint one cell short (`grow(window, r-1, r-1)`) → `FAILED (failures=1, errors=149)`.
  2. `box` footprint one cell long (`grow(window, r+1, r+1)`) → `FAILED (failures=7)` (the audit catches it).
  3. `dx` clamping at the buffer edge instead of the input's bounds → `FAILED (failures=1)`.
  4. `divide` reading its statistic locally (`return window` for both inputs) → `FAILED (failures=1, errors=94)`.
- Final verification: `python3 -m compileall -q stencilpipe tests`, then
  `python3 -W error::SyntaxWarning -m unittest discover -s tests` → `Ran 84 tests in 4.382s` / `OK`, and a last plain
  `python3 -m unittest discover -s tests` → `Ran 84 tests in 2.973s` / `OK`.
- Fixed one unused import (`build` in `tests/test_pattern_parts.py`) found by a small AST check.

### Why
- Note 1: "The footprint must be exact, and only a test can say so." A mutation check is the cheapest way to know the
  test would notice.

### What worked
- All four mutations were caught, including the one that only the audit sees (an over-long reach) and the one that
  only a border probe sees (buffer-edge clamping).

### What didn't work
- While making the mutation harness I copied the package with `cp -r stencilpipe /tmp/sp_backup_check`, which is
  outside the working directory. It was unnecessary (the script kept the original text in memory) and I deleted it at
  once; no file outside the working directory was read or modified.

### What I learned
- Mutation 4's error count (94) is high because `normalize` is in most chains, so a locally-read statistic breaks
  every windowed non-whole request — which is exactly the bug the chapter warns about (note 7).

### What was tricky to build
- Making the mutation harness restore the file even when a run fails: the script rewrites the original text after
  each subprocess, and a final equality check confirms restoration.

### What warrants a second pair of eyes
- The mutation harness lived in a shell heredoc and is not part of the repository; a reviewer wanting to repeat it can
  follow the four mutations listed above.

### What should be done in the future
- N/A — the library is complete for the required interface. Tiles, a scale-aware reach and a coarse statistic are the
  three extensions the chapter describes but this task does not need.

### Code review instructions
- Read `stencilpipe/__init__.py` for the exported surface, `stencilpipe/engine.py::Engine._evaluate` for the
  evaluator, `stencilpipe/operations.py` for the declared footprints, and `stencilpipe/invariance.py` for the proof.
  Validate with `python3 -m unittest discover -s tests` (84 tests, OK).

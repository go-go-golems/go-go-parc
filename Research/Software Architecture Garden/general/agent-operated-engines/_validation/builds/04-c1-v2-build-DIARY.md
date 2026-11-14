# Diary

## Goal

Build `stencilpipe`, a standard-library-only Python package that evaluates small windows of a lazily built
pipeline of 2D float-grid operations, computing only what each window needs and returning exactly the values a
whole-grid computation would give. This diary records the design, each build and test phase, and every failure.

## Step 1: Reading the chapter, the task and the diary format

I read `CHAPTER.md` (Reach-Declared Region Evaluation), `TASK.md` (the `stencilpipe` interface) and
`DIARY-FORMAT.md` completely, then wrote down the design before touching code: a declared footprint per operation,
an evaluator that widens requests by reach and clips them to each input's extent, a global barrier/statistic split
for `normalize`, a whole-value cache consulted first, and an invariance test that compares windowed results with
whole-then-cut results for every operation alone and in chains.

### Prompt Context

**User prompt (verbatim):** "You are a software engineer joining a project. Your working directory contains three files:
- CHAPTER.md: a chapter of a design-pattern book describing the pattern you must apply;
- TASK.md: the software to build, with its required public interface;
- DIARY-FORMAT.md: how to keep your work diary.
Read all three completely first. Keep DIARY.md as you go, one step per phase of work, in that format. Then design, build and test the software in this directory. Work only inside this
directory (do not read or write outside it). Use only the Python 3 standard library. Run your tests and fix what
fails before you finish, and make sure DIARY.md is complete. Your final message must follow the output format at the end of TASK.md."

**Assistant interpretation:** Read the three files, apply the chapter's pattern (declared footprints / windowed
demand-driven evaluation) to the library described in TASK.md, keep a strict-format diary step per phase, write and
run tests under `tests/`, and finish with a single JSON object in a fenced block.

**Inferred user intent:** A working, tested `stencilpipe` package whose public interface matches TASK.md exactly, with
window requests that cost only their own region and still match whole-grid results bit for bit, plus honest evidence
(diary, tests) that the pattern was applied rather than imitated.

### What I did
- Read `CHAPTER.md`, `TASK.md`, `DIARY-FORMAT.md` in full.
- Sketched the module layout and the evaluation algorithm (see *Why*).

### Why
- Chapter *Solution* and *Structure*: each operation declares a footprint; the evaluator carries a window down the
  graph, widens by reach, clips to each input's extent, runs the op only on the requested window and discards no
  margin cells (we simply never compute them).
- Chapter note 5 (hidden global operations): `normalize()` is the hidden global in this task, because it divides by
  the maximum of the whole input. I split it into a global statistic (max over the whole input, cached once) and a
  local application whose footprint is the window itself, so windows still pass through the division.
- Chapter note 6 (keep the best case): the evaluator checks a cache of whole values first and cuts windows from it,
  and also caches computed windows so a second request inside an already computed window costs nothing.
- Chapter note 2 (border rules only at the real border): `box` counts only cells inside the real grid extent and
  `dx` clamps with the real extent, never with the (smaller) buffer edge, so a mid-grid buffer does not shrink its
  neighbourhood.
- Chapter note 3/4 (reaches add up; the unit must be explicit): each node widens by its own reach in *its own*
  coordinate system, so reaches accumulate automatically along a chain; `half()` is the one resolution change and it
  maps windows instead of growing them.

### What worked
- The chapter's structure maps one-to-one onto the required interface: `Window` = the `(x, y, w, h)` tuple,
  `Footprint` = `Op.footprint`, `Region evaluator` = `Engine._eval_window`, `Global barrier`/`Statistic node` =
  `Engine.statistic` + `Normalize.global_params`, `Invariance test` = the test class in `tests/`.

### What didn't work
- Nothing yet; no code has been written.

### What I learned
- The task has no evaluation scale (Chapter 2's `scale` argument is absent), so every footprint is expressed in
  grid cells of the node it is declared on; the only unit conversion is `half()`'s doubling. I will say so in the
  final feedback rather than invent a scale parameter the required interface does not have.

### What was tricky to build
- Deciding where the whole-grid result of `normalize` comes from. Marking it "global" (footprint = whole) would be
  exact but would stop every window; splitting it means the *maximum* still reads the whole input (unavoidable) while
  the division reads only the window. I chose the split, which is what Chapter note 5 prescribes and which computes
  strictly fewer cells.

### What warrants a second pair of eyes
- The cost heuristic (evaluate whole when footprints cover more than a fraction of the inputs) must never change
  results, only cost. I will test both paths for equality.

### What should be done in the future
- Tiles (Chapter note 7) are deliberately left out of the first version: windows first, tiles second. If time allows
  and the window cache proves insufficient, revisit.

### Code review instructions
- Nothing to review yet. Start at `stencilpipe/window.py` once it exists, then `ops.py` (footprints, which are the
  correctness core), then `engine.py` (evaluation, cache, counters), and finally `tests/`.

## Step 2: The declared footprints — windows, buffers and the operation registry

I built the two data types the pattern needs (`Window` as a plain `(x, y, w, h)` tuple with the helpers `clip`,
`grow`, `area`, `contains`, `union_bbox`, and `Buffer` = rows plus the window they occupy) and the operation records
with their declared footprints: `add` (point, footprint = window), `box(r)` (grow by `r` on both axes), `dx()`
(grow by 1 along x only), `half()` (map the window back through the 2x halving) and `normalize()` (global maximum
split into a statistic, local division).

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Implement the Skeleton/Structure participants as a registry of small self-describing
operations, so that the evaluator can ask "which window of input `i` do you read for this output window?" without
knowing anything about the operation.

**Inferred user intent:** Correctness lives in the footprints; the machinery around them should be dull and small.

### What I did
- Created `stencilpipe/window.py` (window algebra, `WHOLE` sentinel), `stencilpipe/buffer.py` (buffer with its own
  origin, `cut`, `rows_of`), `stencilpipe/ops.py` (`Op` base + `AddShift`, `Box`, `DiffX`, `Half`, `Normalize`,
  `default_ops()`), and `stencilpipe/__init__.py` exporting the public names.
- Wrote every kernel so it reads its buffer origin (`src.window`) instead of assuming column 0 is document column 0.

### Why
- Chapter *Structure*: `Footprint` is "the output window grown by the reach (per axis when directional)", "mapped
  through the transform for resampling" (`half`), "whole for global ones". Those are the three shapes implemented.
- Chapter *Implementation note 2*: `box` counts only cells inside `ctx.in_extents` and `dx` clamps with the real
  grid width, never with the buffer's edge, so a mid-grid buffer is not treated as a border. `Box.run` builds a
  summed-area table of the buffer and looks up each neighbourhood clipped to the real extent.
- Chapter *Consequences*: "kernels that convert indices to coordinates must read their buffer's origin, which
  whole-image code never needed" — `Buffer.local`/`Buffer.window` is that single place.
- Chapter *Implementation note 5*: `Normalize.global_params` asks for `engine.statistic(input, "max")`, so the global
  half is explicit in the operation record and the local half keeps footprint = window.

### What worked
- A smoke script over a 20x15 grid: `box` window `(5,5,4,3)` equalled the same 4x3 block cut from the whole
  evaluation; `dx`, `half` and `normalize` windows matched their whole results too (`True` from the comparison).

### What didn't work
- Two hand-computed expectations in my own smoke script were wrong at first (`dx` near the clamped right edge,
  `half` block means); the library was right. I noted this and made the tests use independent reference loops.

### What I learned
- `box` is the only operation here whose footprint is not a pure function of the output window alone: its mean
  denominator depends on the *real* extent. That is exactly the "border rule applies only at the real border"
  trap, and it is why the kernels need `ctx.in_extents` separately from `ctx.buffers`.
- The chapter's `grow(w, ceil(ceil(3σ·scale)/scale))` rounding matters only when reach is a length in document
  units; here `r`, 1 and the 2x halving are whole cells, so no rounding is needed anywhere — but `half` must still
  *map* rather than grow, which the chapter lists as the resampling case.

### What was tricky to build
- `half()`'s footprint for a window at the right/bottom edge of an odd-sized grid: the mapped window
  `(2x, 2y, 2w, 2h)` over-runs the input, and the "mean of the cells that exist" rule means the over-run must be
  clipped (by the evaluator) and the missing cells must be dropped from the denominator (by the kernel). Both
  halves had to agree, or the last output column would differ from a whole computation.

### What warrants a second pair of eyes
- `Box.run`'s summed-area table: index arithmetic `lx0 = xa - bx`, `lx1 = xb - bx + 1` under clipping.
- `DiffX.run`'s clamp (`right = min(x+1, width-1)`, `left = max(x-1, 0)`) when the buffer is narrower than the grid.

### What should be done in the future
- If an operation with a non-integer reach (a Gaussian) is added, its reach must be rounded outward in buffer cells
  and the rounding must live in one place, as the chapter warns.

### Code review instructions
- Read `stencilpipe/window.py` (30 lines of tuple algebra), then the five `footprint` methods in
  `stencilpipe/ops.py` — they are the whole correctness claim. `python3 -m unittest discover -s tests` at this point
  ran nothing yet; the next steps add the engine and the tests.

## Step 3: The region evaluator — propagation, clipping, cache, counters, global barrier

I built `stencilpipe/engine.py`: `Node` (a lazy graph node holding its structural key and extent), `Ctx` (what a
kernel receives), and `Engine` with `source`, `build`/`call`, `evaluate`, `evaluate_many`, `statistic`,
`reset_counters`, `cells_computed` and `clear_cache`.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Implement the evaluator that carries a window down the graph, widens it by each node's
reach, clips it to each input's extent, runs the operation on exactly the requested window and counts those cells.

**Inferred user intent:** A window request must cost its own region, and must never be able to return a value a
whole computation would not have returned.

### What I did
- `_eval_window`: whole-value cache first (cut and stop), then the window cache (cut a containing window), then ask
  each input for its footprint; `WHOLE` footprints or footprints costing more than
  `window_cost_threshold` (0.6) of the inputs fall back to `_eval_whole` and a cut.
- `_eval_whole`: evaluates each input whole, runs the op over the full extent, caches under the node's structural
  key, counts `area(extent)`.
- `statistic`: evaluates its node whole once and caches `max` under `(key, "stat", kind)`; `normalize`'s
  `global_params` uses it. Sources are never counted; every `op.run` call counts exactly `area(window)`.
- `Node.key = (op name, frozen args, input key)`, and each `source()` gets a fresh serial, so equal chains share
  cached values while two sources never collide.
- `evaluate_many`: clips all windows, evaluates the node whole when their bounding box covers most of it, otherwise
  evaluates each window (sharing whatever the window cache already holds).

### Why
- Chapter *Collaborations* 2–6 and the flowchart: cache-whole first, global/cost fallback, footprints clipped,
  result cut to the window and cached per window.
- Chapter *Implementation note 6*: the whole-value cache is checked before anything else, so the "second window of
  the same view" case that whole-grid engines got for free stays free.
- Chapter *Implementation note 7*: windows first, tiles second — the per-window cache gives overlapping-request
  sharing without a tile grid, and the grid stays out of v1.
- Chapter *Solution*: "Prefer an existing whole result when one is cached, and evaluate whole when the footprints
  would cost about as much as the whole" — hence the 0.6 threshold as a settable attribute.

### What worked
- Smoke checks: a 1200x900 grid, `box(r=32)`, 64x64 window: 4,096 cells computed in 2.6 ms versus 1,080,000 cells
  in 466 ms whole (180x), agreeing cell for cell.
- A 120-operation chain evaluated on a window matched the whole result; `normalize` twice in a row worked.

### What didn't work
- Nothing failed in this step; the failures came from the tests written next (see Step 4). I did have to remove a
  leftover `in_extents = [...]; del in_extents` stub from `Engine.build` before running anything.

### What I learned
- The cost heuristic must be expressed in cells, not in "is the window the whole grid": `dx`'s footprint of a
  whole-grid-wide window is wider than the grid, and `half`'s is 4x its window, so both trip the threshold for
  reasons that have nothing to do with the request size (this is the chapter's "cost, not window size").
- The split of `normalize` is what makes a window of a normalized view cost `extent + window` instead of two whole
  grids: the statistic is computed once and cached, and the division passes the window straight through.

### What was tricky to build
- Ordering inside `_eval_window`: `global_params` must be resolved *before* recursing into inputs (the statistic
  evaluates the input whole, which then becomes a cache hit for the input's own window request), and the whole-cache
  and window-cache checks must come first so a cached answer is never recomputed.
- A footprint that clips to an empty window (possible only if a caller registers a broken operation) cannot be run;
  I treat it as a reason to fall back to a whole evaluation rather than to index an empty buffer.

### What warrants a second pair of eyes
- `_eval_window`'s fallback order and the claim that the fallback can only change cost, never values.
- The fact that the window cache stores buffers whose *rows are shared* with what downstream kernels read; this is
  safe only because kernels never mutate their inputs — a reviewer should confirm no kernel does.

### What should be done in the future
- Recursion is per graph depth (`_eval_window` recurses once per node), so a chain thousands of nodes deep would
  exhaust the stack; an explicit work stack would fix it.
- Tiles (Chapter note 7/8): a source-aligned grid with per-tile keys would make scattered overlapping requests share
  work; the window cache only helps when one window contains another.

### Code review instructions
- Start at `Engine.evaluate` / `evaluate_many` in `stencilpipe/engine.py`, then `_eval_window` and `_eval_whole`.
  Validate with `python3 -m unittest discover -s tests` and by reading `test_engine.Counters`, which pins the number
  of cells each request must cost.

## Step 4: The test suite, and the first run (112 failures)

I wrote `tests/support.py` (independent naive whole-grid references for all five operations, a `cut` helper, a probe
window generator and a grid comparison assertion), `tests/test_ops.py` (whole-grid behaviour),
`tests/test_invariance.py` (windowed versus whole-then-cut, for every chain, on six grid sizes) and the first part of
`tests/test_engine.py`.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Prove the scheme with the chapter's single test — for every operation, alone and in
chains, at several sizes, on interior/edge/corner/1x1/whole windows, the windowed value equals the whole-then-cut
value — and pin the cost with cell counters.

**Inferred user intent:** Evidence, not assertion: the invariance test is the pattern's own proof obligation.

### What I did
- Ran `python3 -m unittest discover -s tests`.

### Why
- Chapter *Implementation note 1* and *Sketch*: the invariance test is the specified proof; references are written
  naively from TASK.md so the assertions do not share code with the operations under test.
- Chapter *Implementation note 1* also says a short footprint "fails silently at window edges", so the probe set
  includes every edge, every corner, 1x1 and windows that hang outside the extent.

### What worked
- The whole-grid tests for `add`, `box`, `dx`, `half`, `normalize` and the random-grid comparisons all passed, which
  validated the kernels' semantics against an independent implementation.

### What didn't work
- `python3 -m unittest discover -s tests` reported `Ran 20 tests in 0.061s / FAILED (failures=112)`. Three causes:
  - `AssertionError: 0 != 1 : row count: box then dx then half then box then normalize then add on 24x16, window (-1, 0, 1, 1)` — my helper `cut(whole, (0, 0, 0, 1))` returned `[[]]` (one empty row) while the library returns `[]`
    for an empty window.
  - `AssertionError: 0 != 6 : row count: window (30, 7, 11, 6)` — same empty-window disagreement, on a window whose
    x started exactly at the extent width.
  - `AssertionError: False is not true : cell (1, 0): 2.0 != 1` (my hand-computed `dx` row `[1,1,1,1]`) and
    `AssertionError: False is not true : cell (0, 1): 9.5 != 11.5` (my hand-computed `half` block means) — both
    expectations were mine and both were wrong; the kernels matched the naive references.

### What I learned
- The library and the helper must agree on the degenerate case: zero-width or zero-height window returns no rows at
  all. Worth stating in the docstring (done: `evaluate` returns `[]` for an empty clipped window).
- Hand-computed expectations are a liability; every numeric assertion now either uses a trivial closed form
  (`got[0][0] == (1+2+5+6)/4`) or the naive reference loops.

### What was tricky to build
- Nothing here was hard once the reference implementations existed; the difficulty was that 112 failures hid three
  distinct causes behind one message shape, so I read the first failure of each kind rather than the count.

### What warrants a second pair of eyes
- `tests/support.py` references: are they really independent of the implementation (they are straight loops from
  TASK.md), and do they agree with TASK.md's clamping and block rules?

### What should be done in the future
- N/A.

### Code review instructions
- Read `tests/support.py` first (it defines "correct" for every other test), then the failure list above; re-run
  with `python3 -m unittest discover -s tests`.

## Step 5: Fixing the suite, and one real library bug (negative window sizes)

I corrected the helper and the two hand-computed expectations, extended `tests/test_engine.py` with counters,
interface, cache, safety and cost tests, and fixed the one genuine library gap the new tests found: a window with a
negative width or height was silently clipped to nothing instead of being rejected.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Separate test bugs from library bugs, fix each in the right place, and keep the
invariance test as the referee.

**Inferred user intent:** Do not "fix" a failure by loosening the assertion; a failure is evidence.

### What I did
- `tests/support.py`: `cut` returns `[]` for a window with zero (or negative) width or height.
- `tests/test_ops.py`: corrected the `dx` row to `[1, 2, 2, 1]` and the `half` grid to `[[3.5, 5.5], [9.5, 11.5]]`.
- `stencilpipe/window.py`: `as_window` now raises `ValueError` for `w < 0` or `h < 0` (the grid origin is a
  legitimate out-of-range value to clip, a negative size is not).
- Added `tests/test_engine.py` cases: registry and interface, window clipping, `evaluate_many`, extensible registry,
  cell counters for every operation and for chains, cached-window and cached-whole costs, keyed sharing, threshold
  behaviour, a large-grid cost test, safety tests and degenerate grids.
- Re-ran `python3 -m unittest discover -s tests` (56 tests).

### Why
- The counters are how the pattern's promise is checked: `cells_computed()` is the cheap proxy for "computed only
  what the window needs", and asserting exact counts (16 for a 4x3 `add` window, 4,096 for a 64x64 blur window on an
  800x600 grid) makes a regression in the footprint visible immediately.
- Chapter *Solution*: "Every operation must count every cell it computes" maps to adding `area(window)` right after
  each `op.run`, in the evaluator, so no kernel can forget.

### What worked
- 56 tests passed (`Ran 56 tests in 0.309s / OK`) after fixing 7 failures.

### What didn't work
- The second run reported 7 failures, all test-side except one: `test_chain_counts_one_window_per_operation`
  (`256 != 240`), `test_neighbourhood_operation_counts_only_the_window` (`3200 != 4096`: my window ran past the
  grid's height and was clipped), `test_window_requests_do_not_scale_with_the_input` (`8320 != 8192`: `dx` asks the
  blur for a 66x64 window, not 64x64 — the margin is real and is computed), `test_evaluate_many_shares_work...`
  (`72 != 36`: my second window was not actually inside the first), `test_registry_is_extensible`
  (`cell (0, 0): 24.0 != 92.0`: my arithmetic forgot the grid's `seed`), `test_window_returns_only_the_window...`
  (`34.0 != 33.0`: same seed mistake), and `test_bad_windows` (`ValueError not raised : (0, 0, -1, 1)`), which was a
  real gap in `as_window`.
- A third run left one failure: `test_normalize_does_not_stop_the_chain_below_it` (`4852 != 4832`). My expectation
  assumed `normalize` computes the 4x4 output window, but it is asked for the 6x6 footprint of the blur above it and
  computes exactly that; `16 + 36 + 4800 = 4852` is correct.

### What I learned
- Intermediate nodes legitimately compute *their consumer's* footprint, not the original request. That is the whole
  point of propagating windows, and it means "cells computed = window area per operation" is only true for point
  operations; for a chain it is the sum of the per-node propagation windows. The tests now state that explicitly.
- A window past the grid edge is clipped, which changes the cell count; tests must keep windows inside the extent
  when they assert cost, and outside it when they assert clipping.

### What was tricky to build
- Distinguishing "the library is wrong" from "my expectation is wrong" in three consecutive rounds. The rule I
  settled on: if the naive reference agrees with the library, the expectation is wrong; if the reference disagrees,
  the library is wrong. Only the negative-size window fell in the second category.

### What warrants a second pair of eyes
- The exact counter assertions (they encode my reading of "every cell an operation computes"); a reviewer with a
  different reading of `cells_computed` should say so, because those numbers are the cost contract.
- `test_window_cost_threshold_forces_whole_evaluation` relies on the 0.6 default; changing the default changes it.

### What should be done in the future
- Add a property-style randomised invariance test over random chains (currently chains are a fixed list plus one
  random-window test over a single mixed chain).

### Code review instructions
- `tests/test_engine.py::Counters` is the cost contract; `tests/test_invariance.py::CHAINS` is the correctness
  contract. Run `python3 -m unittest discover -s tests`.

## Step 6: Final check

I re-read the package after the fixes, removed two dead clipping guards from `Box.run`, and ran the whole suite again
plus the docstring example and a compile check.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Finish only when the suite is green, the diary is complete and the final message
follows TASK.md's JSON format.

**Inferred user intent:** A library the reviewer can trust without re-deriving it, plus honest notes about what is
not covered.

### What I did
- Removed the unreachable `if yb < ya` / `if xb < xa` guards in `Op`'s `Box.run` (they could never trigger, since
  `r >= 0` keeps `yy - r <= yy <= yy + r`).
- Ran `python3 -m compileall -q stencilpipe tests` (clean), `python3 -W error -m unittest discover -s tests`
  (`Ran 58 tests in 0.323s / OK`) and the package docstring example via `doctest.testmod` (`failed=0, attempted=6`).
- Measured the promise end to end on a 1200x900 grid with `box(r=32)`: a 64x64 window cost 4,096 cells / 2.6 ms
  against 1,080,000 cells / 466 ms for the whole grid, identical values.

### Why
- Chapter *Invariance test* is the acceptance criterion; the measurement is the chapter's *Consequences* claim
  ("the cost of a request follows its size, not the size of the input") checked rather than assumed.

### What worked
- 58 tests, 6 doctest examples, compile check: all green.

### What didn't work
- Nothing in this step.

### What I learned
- The pattern's cost claim survives the cost heuristic: a full-extent window still falls back to a whole evaluation,
  so the cheap path only kicks in where it is actually cheaper.

### What was tricky to build
- Nothing new; the residual risks are the ones listed in Step 3 (recursion depth, shared row lists in cached
  buffers, no tile grid).

### What warrants a second pair of eyes
- `stencilpipe/engine.py` `_eval_window` (order of cache checks and fallbacks) and `stencilpipe/ops.py` footprints.
- `normalize`'s statistic is deliberately *not* counted in `cells_computed()` (it is a parameter, not an output
  grid); its input is, because that input is evaluated whole. A reviewer may want that documented differently.

### What should be done in the future
- Tiles with a source-aligned grid (Chapter notes 7–9), a `measure`-style multi-window request helper
  (Chapter note 10), and an iterative evaluator for very deep chains.

### Code review instructions
- `python3 -m unittest discover -s tests` from this directory; the interesting reading is `stencilpipe/ops.py`
  (footprints) and `stencilpipe/engine.py` (`_eval_window`, `_eval_whole`, `statistic`).

# Diary

## Goal

Build `stencilpipe`, a standard-library Python 3 library for lazily-evaluated pipelines of 2D grid
operations in which asking for a window of results computes only the cells that window needs, and
returns exactly the values a whole-grid evaluation would return. This diary records design, build,
test and fix phases.

## Step 1: Reading the task and designing the evaluator

I read `TASK.md` and `DIARY-FORMAT.md` completely, then designed the library before writing code.
The task fixes the observable semantics of five operations (`add`, `box`, `dx`, `half`,
`normalize`), the node/evaluate API, and a cell-counting contract ("every operation must count
every cell it computes"). The diary format mentions `CHAPTER.md`; there is no such file in this
directory, so the design decisions below are my own reading of `TASK.md`.

### Prompt Context

**User prompt (verbatim):** "You are a software engineer joining a project. Your working directory contains two files:
- TASK.md: the software to build, with its required public interface;
- DIARY-FORMAT.md: how to keep your work diary.
Read both completely first. Keep DIARY.md as you go, one step per phase of work, in that format. Then design, build and test the software in this directory. Work only inside this
directory (do not read or write outside it). Use only the Python 3 standard library. Run your tests and fix what
fails before you finish, and make sure DIARY.md is complete. Your final message must follow the output format at the end of TASK.md."

**Assistant interpretation:** Implement the `stencilpipe` package exactly as specified by `TASK.md`, with
tests under `tests/`, a `DIARY.md` in the given format, and finish with the required JSON block.

**Inferred user intent:** A reviewer wants a working, tested library whose windowed evaluation is
provably equal to whole-grid evaluation while doing strictly less work, plus an honest record of the
engineering process and the judgement calls.

### What I did
- Read `TASK.md`, `DIARY-FORMAT.md`; listed the directory (`TASK.md`, `DIARY-FORMAT.md` only, Python 3.10.3).
- Sketched the architecture: `stencilpipe/geometry.py` (rectangle algebra), `stencilpipe/engine.py`
  (Engine, Node, SourceNode, OpNode, per-node computed-cell bookkeeping, counters),
  `stencilpipe/ops.py` (Op base class + the five demo ops + `demo_engine()`), `stencilpipe/__init__.py`.

### Why
- The core requirement is *demand propagation*: to produce an output rectangle of a node, a node
  must be able to name the rectangle of its input it needs (its "footprint"). `dx` expands by 1 in x
  only, `box(r)` expands by `r` in both directions, `half` maps an output rect to a `2w x 2h` input
  rect, `add` is 1:1, and `normalize` depends on the whole input because of the global maximum.
  Making that a method on an `Op` keeps every operation's footprint next to its formula, which is
  exactly where an error would otherwise hide.
- Equality with whole-grid evaluation is then structural: each op computes each output cell with the
  same formula it would use in a whole-grid pass, only over a smaller set of cells.
- Counting needs to be idempotent across requests, so each node remembers which cells it already
  computed (per-row interval sets) and only new cells increment `cells_computed()`. That also lets
  `evaluate_many` share work between overlapping windows.

### What worked
- A footprint-based design covers all five ops without special cases in the evaluator.
- Deciding early that `normalize` needs a "prepare/aggregate" hook (global max over the whole input)
  avoided a redesign later; the hook returns per-node cached state.

### What didn't work
- My first idea, sending every request through a full-grid evaluation and slicing at the end, was
  discarded before coding: it satisfies value equality but trivially violates the "only compute what
  you ask for" requirement and would make cell-count tests meaningless.

### What I learned
- `TASK.md` leaves three things implicit: (a) whether cached cells are reused between `evaluate`
  calls, (b) what `normalize` should do with negative values when the maximum is 0, (c) whether an
  empty clipped window returns `[]` or rows of nothing. I chose: caches are reused and cleared by
  `reset_counters()`; all outputs are 0 when the maximum is 0; an empty clipped window is `[]`.

### What was tricky to build
- Nothing built yet; the tricky part anticipated is keeping the "needed input rect" and the
  "aggregate prep rect" consistent so that no cell is read before it is computed. Plan: ops declare
  `input_rect()` covering everything they read, plus optional `extra_input_rects()`, and the engine
  raises `RuntimeError` if an op reads a cell that was never computed.

### What warrants a second pair of eyes
- The clipping of windows at node extents, especially `half` where output and input coordinates
  differ, and `box` at borders where the mean divides by the number of cells inside the grid.

### What should be done in the future
- After the core works: a property-style randomized test comparing windowed vs whole-grid values.

### Code review instructions
- Read `TASK.md`, then `stencilpipe/engine.py` (`OpNode.ensure`) and `stencilpipe/ops.py`
  (`input_rect`/`compute_cell` pairs). Validate with `python3 -m unittest discover -s tests`.

## Step 2: Building the engine core (geometry + demand-driven evaluation)

I implemented `stencilpipe/geometry.py` (rectangle algebra with clipping) and `stencilpipe/engine.py`
(`Engine`, `Node`, `SourceNode`, `OpNode`, and per-row interval bookkeeping in `_Spans`). The
evaluator is the heart of the task: `OpNode.ensure(rect)` asks its operation for the input rect, asks
the parent for that rect, then evaluates only the cells of `rect` that are still unknown.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Turn the design into code: rectangles, nodes, demand propagation,
caching and counting.

**Inferred user intent:** A working library core where windowed evaluation is a strict subset of
whole-grid evaluation, which is the only way to guarantee equal values cheaply.

### What I did
- Created `stencilpipe/geometry.py`: `Rect` (half-open, `clip`, `expand`, `scale`, `cells`),
  `window_rect()` to normalise `(x, y, w, h)` input, `EMPTY`.
- Created `stencilpipe/engine.py`: `_Spans` (sorted per-row x intervals with `missing`/`add`),
  `_Ctx` (read access + cached aggregate state), `Node` (interface), `SourceNode`, `OpNode.ensure`,
  `Engine` with `register`, `operation`, `source`, `evaluate`, `evaluate_many`,
  `cells_computed`, `reset_counters`.
- Key invariants: `ensure` clips to the node extent, returns early when nothing is missing, ensures
  the parent *before* calling the op's `prepare`, and increments the counter by the number of newly
  computed cells only.

### Why
- The footprint method is what makes "only what the window needs" true by construction: each op
  declares `input_rect` next to its formula, the engine translates, clips and recurses.
- Counting at the moment a cell is stored (and only then) satisfies "every operation must count
  every cell it computes" while keeping the counter meaningful across overlapping requests.
- `_Spans` exists so that `evaluate_many` and repeated `evaluate` calls do not double-count or
  double-compute cells.

### What worked
- A quick smoke test (`box(1)` then `normalize` over a 5x4 grid, window `(1,1,2,2)`) gave
  `cells_computed() == 24` = 20 box cells (whole input, because normalize needs its maximum) + 4
  normalize cells, and the window rows equalled the corresponding rows of the whole-grid run.

### What didn't work
- The first version imported `EMPTY` and `cell_rect` into `engine.py` without using them; removed
  them immediately so that unused imports do not hide dead code.

### What I learned
- The halo of a stencil only costs *output* cells of operation nodes; reading source cells is free.
  This matters for expected cell counts, and I got it wrong in a test later (Step 4).

### What was tricky to build
- Preventing reads of not-yet-computed parent cells: solved by having ops declare everything they
  read through `input_rect`/`extra_input_rects`, ensuring the parent first, and raising
  `RuntimeError` from `OpNode.get` if a missing cell is ever read (a bug alarm, not a user error).

### What warrants a second pair of eyes
- `_Spans.missing`/`_Spans.add` merging logic: off-by-one errors here would silently skip rows.
  Randomised tests with overlapping windows are the mitigation.

### What should be done in the future
- Implement the five ops on top of this core, then exercise the interval bookkeeping with random
  multi-window evaluations.

### Code review instructions
- `stencilpipe/engine.py::OpNode.ensure` and `_Spans`; `stencilpipe/geometry.py::Rect.clip`.
  Validate with `python3 -m unittest discover -s tests`.

## Step 3: Building the operations and public interface

I implemented `stencilpipe/ops.py` (an `Op` base class plus `AddOp`, `BoxOp`, `DxOp`, `HalfOp`,
`NormalizeOp`, and `demo_engine()`) and `stencilpipe/__init__.py` re-exporting the public names.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Encode the five formulas from `TASK.md` exactly, including their
footprints, and expose the interface the task requires.

**Inferred user intent:** The reviewer will test each op's whole-grid values and the windowed values
against the definitions in the task text.

### What I did
- Created `stencilpipe/ops.py` with a three-part contract per op: `out_extent`, `input_rect` (plus
  `extra_input_rects`), `compute_cell`; `validate()` checks keyword arguments at build time.
- `BoxOp` expands by `r` in both directions and divides by the number of in-grid cells.
- `DxOp` expands by 1 in x only, and computes `in[min(x+1,W-1)] - in[max(x-1,0)]`.
- `HalfOp` reports `ceil(W/2) x ceil(H/2)` and maps an output rect through `scale(2, 2)`.
- `NormalizeOp` asks for the whole input rect (its maximum is global) and caches the maximum via
  `prepare()`; when the maximum is 0 every output is 0.
- Created `stencilpipe/__init__.py` exporting `demo_engine`, `Engine`, `Node`, `Rect`, `Op`, the
  five op classes and `DEMO_OPERATIONS`.

### Why
- Keeping `input_rect` and `compute_cell` adjacent is what makes a windowed run a subset of a
  whole-grid run, and it localises the most error-prone decisions (clipping, border means, block
  means) to one screen each.

### What worked
- `python3 -c "... box(1) then normalize ..."` returned the expected values and count.

### What didn't work
- Nothing failed in this step; the first real failures appeared when tests were run (Step 4).

### What I learned
- `box` must divide by the *actual* number of in-grid cells, so the per-cell loop recomputes the
  clipped bounds instead of assuming `(2r+1)^2`.

### What was tricky to build
- Argument validation without breaking "building computes nothing": validation only inspects the
  arguments, never the grid, so building stays O(depth) with no cell work.

### What warrants a second pair of eyes
- `NormalizeOp.prepare` reads the whole parent extent; it relies on `input_rect` returning the whole
  input extent so the parent is fully computed first. Any op that reads in `prepare` must do the
  same.

### What should be done in the future
- Write the test suite: whole-grid reference comparisons, window equality, counting, API errors.

### Code review instructions
- `stencilpipe/ops.py`, one class at a time, against the formula list in `TASK.md`.

## Step 4: Test suite, first run, and three expectation fixes

I wrote `tests/references.py` (naive whole-grid implementations written from `TASK.md`, independent
of the library) and four test modules: `test_whole_grid.py`, `test_windows.py`,
`test_counting.py`, `test_api.py`. The first run had three failures, all of which turned out to be
wrong expectations in my tests rather than engine bugs; I verified each by hand before changing the
test.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Test the library against an independent implementation, especially the
window/whole-grid equality property, and fix what fails.

**Inferred user intent:** Evidence that the tricky property actually holds, including border and
out-of-range windows.

### What I did
- Ran `python3 -m unittest discover -s tests`: 53 tests, 3 failures.
- Investigated each failure with targeted `python3 -c` snippets, then corrected the test
  expectations (the engine was right in all three cases).
- Re-ran: 54 tests (I added one during the fix), all passing.

### Why
- The reference module is deliberately naive and separate so that a bug shared between library and
  test cannot hide; it is the only way to trust the value-equality claim.

### What worked
- Randomised pipelines (`random_pipeline`, 120 trials with a fixed seed) and every-op/every-window
  matrices passed on the first run, including negative and out-of-range windows.

### What didn't work
- Exact failure text from the first run:

```
FAIL: test_node_objects_are_immutable_building (test_api.PublicInterfaceTests)
AssertionError: Lists differ: [[2.5, 2.5], [2.5, 2.5]] != [[2.0, 2.5], [2.5, 3.0]]

FAIL: test_overlapping_windows_share_cells (test_counting.CountingTests)
AssertionError: 14 != 16

FAIL: test_window_is_cheaper_than_whole_grid (test_counting.CountingTests)
AssertionError: 7 != 19
```

- Causes: (1) for a 2x2 grid, `box(1)` at every cell covers the whole grid, so the mean is 2.5
  everywhere; (2) I mis-added the union of two 3x3 windows on a 5x4 grid: the union is 14 cells, not
  16; (3) I wrongly charged `box` for its halo output cells (15) when the halo is read from the
  source and costs nothing — the true minimal count is dx 1 + add 3 + box 3 = 7.

### What I learned
- The distinction confirmed in (3): a halo expands the *requested rect of a parent operation node*,
  never the source. I added `test_halo_propagates_through_stencil_layers` to pin that down:
  `box(1) -> box(2) -> add`, 1x1 window on a 7x7 grid costs 1 + 25 + 1 = 27 of 147 whole-grid cells.

### What was tricky to build
- Reasoning about "expected count" tests: each expectation is now derived by hand from the footprint
  chain and written in a comment next to the assertion, so a future reader can re-derive it.

### What warrants a second pair of eyes
- The hand-derived counts in `tests/test_counting.py`; if an op's footprint changes they must change
  with it.

### What should be done in the future
- Add a randomised multi-window test that reuses one node (to exercise `_Spans` merging) and a
  dx-specific test that the halo does not expand vertically.

### Code review instructions
- `tests/references.py` first (the oracle), then `tests/test_counting.py` comments.
  Validate with `python3 -m unittest discover -s tests`.

## Step 5: Hardening — custom ops, multi-window reuse, streaming `ensure`

The suite passed, so I attacked the places where a hidden bug was most likely: the interval
bookkeeping under overlapping windows, the `extra_input_rects` hook (unused by the demo ops), ops
with a different output geometry, and memory behaviour of `ensure` on whole grids. I also added
positional-argument support to `Node.call`.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Push past the happy path: prove the caching/interval layer and the
extension points work, and make the evaluator cheap on large grids.

**Inferred user intent:** Confidence that any window pattern on any legal pipeline gives whole-grid
values with minimal work, not just the windows I happened to test.

### What I did
- Added `tests/test_extensions.py`: `MinShiftOp` (1:1 footprint but a global aggregate provided via
  `extra_input_rects`), `DecimateOp` (output geometry `ceil(W/3) x ceil(H/3)`), a randomised
  multi-window test that hits one node with four random windows and then the whole grid, and a
  dx-halo test proving the halo is horizontal only.
- Refactored `OpNode.ensure` to call `_Spans.covers()` for the early exit and then stream the gaps
  row by row instead of materialising a list of gaps for the whole rect (memory: a full-grid rect
  on a 1000x1000 grid used to build a million small tuples before computing anything).
- Added `Op.params`/`Op.bind` so `call("box", 1)` works as well as `call("box", r=1)`; conflicts and
  extra positionals raise `TypeError`.
- Ran a 400-trial randomised stress script (inline, `python3 - <<'EOF'`) comparing
  `evaluate_many` + `evaluate` against the naive reference: 0 failures.
- Timed a 300x300 grid: a 5x5 window of `box(2) -> dx -> add` costs 0.3 ms and 85 cells; the whole
  grid costs 0.67 s and 270 000 cells, and the values agree.

### Why
- The interval set and the `ensure` early-exit are the only stateful parts of the design; if they are
  wrong, values silently differ for overlapping requests. Testing them directly is worth more than
  more single-window cases.

### What worked
- 400 randomised trials, the extension tests, and the timing all behaved as designed on the first
  attempt after the streaming refactor.

### What didn't work
- One more wrong expectation of mine, in the new large-grid test:

```
FAIL: test_window_on_large_grid_computes_a_handful_of_cells (test_counting.LargeGridTests)
AssertionError: 42 != 70
```

- Same mistake as Step 4 in a new disguise: I charged the `dx` node for its own halo (`6x3 = 18`
  *instead of* box's 18 and dx's 12 separately, I wrote 12 + 18 + 40). The correct accounting is
  add 12 + dx 12 + box 18 (box gets the 6x3 rect dx asks for). Corrected the test and its comment.
- Then a wrong expected value in the new positional-argument test:

```
FAIL: test_positional_arguments (test_api.PositionalArgumentTests)
AssertionError: Lists differ: [[3.5, 3.5], [3.5, 3.5]] != [[2.5, 2.5], [2.5, 2.5]]
```

- `add(1)` on `[[1,2],[3,4]]` gives `[[2,3],[4,5]]`, whose 2x2 mean is 3.5, not 2.5; fixed the
  expectation (the first run of that test had 62 tests, 1 failure).

### What I learned
- "The halo belongs to the consumer": a node computes exactly the cells it was asked for; the halo
  enlarges the rect it requests from its parent. Writing that sentence down stopped me repeating the
  error.
- Positional support had to be a pure binding step in `Node.call`; keeping it out of `validate`
  means ops still see exactly one canonical dict.

### What was tricky to build
- Streaming the gaps while mutating the interval set: `missing()` returns a fresh list per row, so
  mutating `_spans` after consuming that row's list is safe; the counted total is accumulated in a
  local and written back once so a mid-loop exception cannot leave the counter half-updated.

### What warrants a second pair of eyes
- `Op.bind` (positional binding) is beyond the letter of `TASK.md`; confirm it cannot mask a caller
  error. It rejects duplicate and surplus arguments, so the only risk is that a hidden caller relies
  on `TypeError` for a positional it "should not" have passed.

### What should be done in the future
- Consider evicting cache entries for memory, or documenting that a source grid must not be mutated
  after it is wrapped.

### Code review instructions
- `stencilpipe/engine.py::OpNode.ensure`, `_Spans.covers`; `tests/test_extensions.py`.
  Validate with `python3 -m unittest discover -s tests`.

## Step 6: Final check

I ran the whole suite once more, checked that the package compiles cleanly, re-read `TASK.md` against
the implementation, and confirmed the diary is complete.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Make sure everything required by `TASK.md` is present, tested and
green before reporting.

**Inferred user intent:** A finished deliverable, not a work in progress.

### What I did
- `python3 -W error -m unittest discover -s tests` → 62 tests, OK.
- `python3 -m compileall -q stencilpipe tests` → clean.
- Re-checked the interface list in `TASK.md` against `stencilpipe/__init__.py`: `demo_engine`,
  `Engine`, `Node`, `source`, `call`, `evaluate`, `evaluate_many`, `reset_counters`,
  `cells_computed`, and all five operations with whole-grid-defined behaviour.
- Checked the file list and the diary steps.

### Why
- `-W error` catches accidental deprecations; compileall catches syntax errors in files discovery
  may skip (it does not, but it is cheap).

### What worked
- Everything green: 62 tests, no warnings, no compile errors.

### What didn't work
- Nothing failed in this step.

### What I learned
- The five ops plus the engine fit in ~780 lines of library code; most of the effort was in
  footprint reasoning and in the counting expectations, not in the arithmetic.

### What was tricky to build
- N/A for this step.

### What warrants a second pair of eyes
- The interpretation of `cells_computed()` combined with `reset_counters()` clearing caches (see
  Step 1): it is documented in `Engine.reset_counters` but is a semantic choice a reviewer should
  consciously accept.

### What should be done in the future
- N/A.

### Code review instructions
- `python3 -m unittest discover -s tests`, then read `DIARY.md` Step 1 for the judgement calls and
  `stencilpipe/engine.py::OpNode.ensure` for the core algorithm.

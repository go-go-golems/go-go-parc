# Diary

## Goal

Build `stencilpipe`, a standard-library Python 3 library that evaluates pipelines over large 2D float grids
demand-driven: a request for a window computes only that window plus each operation's declared reach, and returns
bit-for-bit what a whole-grid computation would return there. This diary records the design, each build step, the
tests, and every failure and fix.

## Step 1: Reading the chapter, the task and the diary format

I read `CHAPTER.md`, `TASK.md` and `DIARY-FORMAT.md` in full before touching any code. The chapter describes
reach-declared region evaluation: every operation declares, per input, the input window it reads for an output
window; an evaluator propagates windows down the graph, widening, mapping back or taking the whole extent, clipped
at each node; a guard cuts every input (sources included) to its footprint and raises on reads outside; global
parameters are split into a statistic node wired in as an ordinary input of a local operation; exactness is proven
by comparing windowed results with the same window cut from a whole computation, bit for bit, on a fresh engine.

### Prompt Context

**User prompt (verbatim):** "You are a software engineer joining a project. Your working directory contains three files:
- CHAPTER.md: a chapter of a design-pattern book describing the pattern you must apply;
- TASK.md: the software to build, with its required public interface;
- DIARY-FORMAT.md: how to keep your work diary.
Read all three completely first. Keep DIARY.md as you go, one step per phase of work, in that format. Then design, build and test the software in this directory. Work only inside this
directory (do not read or write outside it). Use only the Python 3 standard library. Run your tests and fix what
fails before you finish, and make sure DIARY.md is complete. Your final message must follow the output format at the end of TASK.md."

**Assistant interpretation:** Implement the `stencilpipe` package exactly as `TASK.md` specifies, using the pattern
in `CHAPTER.md` (declared footprints, window propagation, a footprint guard, a statistic node for the global max in
`normalize`), with tests under `tests/`, and keep this diary in the strict format.

**Inferred user intent:** A correct, exact, tested library that demonstrates the chapter's pattern in real code, with
evidence in the diary that the pattern's pitfalls (short reaches, hidden globals, buffer-origin-dependent arithmetic)
were handled.

### What I did
- Read `CHAPTER.md` (reach-declared region evaluation), `TASK.md` (public interface of `stencilpipe`), `DIARY-FORMAT.md`.
- Inspected the directory: only those three files; Python 3.10.3 available.

### Why
- The chapter's Solution, Structure and implementation notes define the architecture I must follow; `TASK.md` fixes
  the public API and the operations whose whole-grid behaviour must be preserved.

### What worked
- The required operations map cleanly onto the pattern: `add` is a point op (footprint = window), `box(r)` a
  neighbourhood op (reach `r` on both axes), `dx` a directional op (reach 1 on x only), `half` an op that moves
  pixels (window mapped back by ×2), and `normalize` a local op hiding a global parameter (the whole-grid maximum).

### What didn't work
- Nothing yet.

### What I learned
- `normalize` is exactly the chapter's "hidden global" trap (implementation note 7): the whole-grid maximum must be
  a separate statistic node, otherwise a window would divide by that window's maximum.

### What was tricky to build
- Nothing yet; the first real decision is how to keep whole and windowed runs on one arithmetic path so exactness is
  structural rather than accidental.

### What warrants a second pair of eyes
- My reading that `normalize`'s maximum is global (not per-window) is the single most important interpretation.

### What should be done in the future
- Design the module layout and the Region/guard API before writing operations.

### Code review instructions
- Compare the planned participants (Footprint, Window, Region evaluator, Invariance test, Footprint guard, Global
  barrier, Statistic node) against the chapter's Structure table.

## Step 2: Design

I designed the package around one rule: a whole evaluation and a windowed evaluation must run the *same* operation
code over the *same* values. Whole evaluation is just "evaluate with the whole extent as the window", so exactness is
structural (the same per-cell formula, reading absolute coordinates, with no prefix sums or buffer-origin-dependent
arithmetic) instead of something to babysit. Four modules: `geometry.py` (Window helpers, the `WHOLE` footprint
sentinel, and `Region`, the footprint guard), `ops.py` (the five demo operations plus the internal `MaxStat`),
`engine.py` (lazy `Node` graph, registry builders, `Engine.<|endoftext|>eval`), and `__init__.py` (public exports).

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Same as Step 1: apply the chapter's pattern to the API in TASK.md, with exact
whole-grid semantics for every window.

**Inferred user intent:** A small, readable library whose structure visibly mirrors the chapter's participants, plus
tests that prove the invariance and count the work.

### What I did
- Sketched the module layout and the data types: windows are plain `(x, y, w, h)` tuples; a footprint is a window or
  `WHOLE`; a computed value is a `Region` (trimmed rows + absolute origin + the node's full extent + a label).
- Decided the evaluator protocol: `op.output_size(input_extents)`, `op.footprint(window, index, extent)`,
  `op.run(regions, window, count)`.
- Decided to implement the chapter's *smallest form*: footprints, a recursive evaluator that widens at each node, the
  guard, the exact invariance test, one statistic node -- no tiles, no cell memo, no cost rule, no scale conversion.

### Why
- One arithmetic path: implementation note 2 warns that prefix sums (or any buffer-origin-dependent order) break
  exact equality; whole == "window is the extent" removes the whole class of bugs.
- `Region` as the only way operations read: note 3 requires every read be guarded, sources included, so a short
  reach raises at once.
- `normalize`'s maximum is global (note 7), so it becomes `divide(image, max(image))` with the maximum as an
  ordinary second input of a *local* operation; the evaluator needs no hook and windows still pass through.
- `cells_computed` counts *output* cells per operation as TASK.md defines; footprints (input reads) are not counted.

### What worked
- The protocol fits all five operations: point (`add`), neighbourhood (`box`), directional (`dx`), pixel-moving
  (`half`), and local-with-global-parameter (`normalize`).
- `half` needs the *whole input extent* to know whether `2x+1` exists, so `Region` carries `extent`, not only the
  window.

### What didn't work
- Nothing yet (design phase).

### What I learned
- The chapter's optional participants are genuinely optional here: the only cache worth keeping is the statistic's
  exact whole value, and per-cell cost is low enough that a cost rule would only break the cell counts.

### What was tricky to build
- Nothing yet; the sensitive point is that `box`'s border rule must clip to the *input extent*, not to the region's
  edge, which is why the region carries the extent.

### What warrants a second pair of eyes
- Whether counting the statistic's single cell is the intended reading of "every operation must count every cell it
  computes".

### What should be done in the future
- Write the geometry and guard first, then operations, then the evaluator.

### Code review instructions
- Read `stencilpipe/geometry.py` (`Region`) and `stencilpipe/engine.py` (`Engine._eval`) first; they are the pattern.

## Step 3: Building the window/footprint primitives and the guard

I wrote `stencilpipe/geometry.py`: `as_window`, `is_empty`, `whole_window`, `clip_window`, `grow_window`,
`cut_grid`, the `WHOLE` sentinel, `FootprintError`, and `Region`. `Region` holds rows already trimmed to its window,
the absolute origin `(x0, y0)`, the full `extent` of the node that produced it, and a label used in error messages.
All reads go through `get`, `slice_row` or `sum_row`, which convert absolute coordinates and raise `FootprintError`
outside the window.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Implement the Window, Footprint-marker and Footprint guard participants.

**Inferred user intent:** A guard that makes a one-pixel-short reach fail loudly, with messages that say which input
and which footprint.

### What I did
- Created `stencilpipe/geometry.py`.
- `clip_window` clips to `(0, 0, w, h)`, collapsing windows that fall outside to empty; `grow_window` grows per axis
  without clipping (the evaluator clips); `WHOLE` marks a global read.
- `Region.__init__` validates that the rows returned by an operation match the requested window, catching shape bugs.

### Why
- CHAPTER.md Structure: *Window*, *Footprint*, *Footprint guard* are "Always" participants; note 3 requires cutting
  every input, sources included.
- Absolute-coordinate reads are what let one operation body serve both whole and windowed evaluation (note 2).

### What worked
- The guard doubles as a development tool: any operation that reads too far fails on the first offending window.

### What didn't work
- Nothing here.

### What I learned
- Carrying `extent` on the region is what makes `box`'s in-grid-only border rule and `half`'s existence test correct
  at the edge of a window (note 4: border rules apply only at the real border).

### What was tricky to build
- Trimming rows for the source (`[list(row[x0:x1]) ...]`) instead of keeping the whole grid: it keeps every
  operation's buffer the size of its footprint, so an unguarded direct row access cannot even see the rest.

### What warrants a second pair of eyes
- `slice_row` allows an empty slice at the right edge; check that is never used to sneak past the guard.

### What should be done in the future
- The operations, using only `get`/`slice_row`/`sum_row`.

### Code review instructions
- `stencilpipe/geometry.py`; check `clip_window` edge cases and `Region.get`/`slice_row` bounds.

## Step 4: Building the demo operations with declared footprints

I wrote `stencilpipe/ops.py` with an `Operation` base class and `Add`, `Box`, `Dx`, `Half`, `Normalize`, plus the
internal `MaxStat` that supplies `Normalize`'s global maximum. `Box` sums row slices from `y-r..y+r` and
`max(0, x-r)..min(W, x+r+1)`, dividing by the number of cells that exist; `Dx` reads clamped neighbours along x;
`Half` maps its output window back by ×2 and checks `2x+1 < whole width`; `Normalize` reads `m` from its second
(statistic) input once and divides.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Give each operation a declared footprint and make each compute exactly the requested
window from guarded inputs.

**Inferred user intent:** The chapter's central claim demonstrated on the task's five operations, including a
directional reach (`dx`) and a pixel-moving footprint (`half`).

### What I did
- Created `stencilpipe/ops.py`.
- Footprints: `add` -> window; `box(r)` -> `grow_window(window, r, r)`; `dx` -> `grow_window(window, 1, 0)` (x only);
  `half` -> `(2x, 2y, 2w, 2h)`; `normalize` -> window for input 0 and `WHOLE` for input 1; `MaxStat` -> `WHOLE`.
- All sums accumulate row by row and left to right, so results never depend on where the buffer starts.
- `MaxStat` uses `max(row)` per row for speed; its arithmetic is a max, so comparison order does not change bits.

### Why
- The chapter's Sketch gives exactly these footprint shapes; note 5 (reaches add along a chain) is handled by the
  evaluator widening at each node, not by any plan.
- Note 2: no prefix sums anywhere, so windowed and whole arithmetic are identical.

### What worked
- Every operation body is the same for whole and windowed evaluation; a window only chooses the region handed in.

### What didn't work
- Nothing yet (operations alone were correct; my test expectations were the problem, see Step 6).

### What I learned
- `box`'s border rule needs the input extent, not the region window; `half`'s does too.

### What was tricky to build
- `Dx` at the right grid edge reads `W-1` again (clamped); the footprint grown by 1 on x covers it, and clipping to
  the input extent makes reads at the border legal without a special case.

### What warrants a second pair of eyes
- `Normalize`'s `m == 0` branch: all cells become `0.0`; confirm that matches "0 stays 0 if m is 0" and is stable in
  windows.

### What should be done in the future
- The lazy graph and evaluator.

### Code review instructions
- `stencilpipe/ops.py`; compare each `footprint` against the reads in `run` and against CHAPTER.md's Sketch.

## Step 5: Building the graph, evaluator and registry

I wrote `stencilpipe/engine.py` (`Node`, `Engine`, builders, `demo_engine`) and `stencilpipe/__init__.py`. `Node`
holds an operation and its inputs, derives its extent from metadata only (so building computes nothing), and exposes
`call(name, **args)`. `Engine._eval` clips the request window to the node's extent, checks the whole-value cache for
nodes that declare `cache_whole` (only `MaxStat`), asks each input for its footprint and clips it to that input's
extent, evaluates each input on exactly that window, relabels the region for guard messages, runs the operation and
counts cells; `WHOLE` footprints make an input evaluate whole and stop the request there.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Implement the Region evaluator, the statistic node wiring and the public API.

**Inferred user intent:** A request for a window must pull only that window plus margins, exactly, and be countable.

### What I did
- Created `stencilpipe/engine.py` and `stencilpipe/__init__.py` (exports `demo_engine`, `Engine`, `Node`,
  `Operation`, the operation classes, `Region`, `FootprintError`, `WHOLE` and the window helpers).
- `_build_normalize` creates `MaxStat` over the primary input and wires it as input 1 of `Normalize`.
- Windows: `evaluate(node, window=None)`; `evaluate_many` evaluates each window on its own.
- Counters: `reset_counters()` and `cells_computed()`; `run` reports its output cells through a callback.
- Custom registries: `Engine(builders)` so tests can register a deliberately short-footprint operation.

### Why
- Chapter Collaborations 1-3 and 6; the cache-first branch only for the statistic (note 9), no cost rule (note 8),
  no tiles (note 10).
- Mapping a grid with no columns to extent `(0, 0)` keeps degenerate inputs answerable (`[]`).

### What worked
- `evaluate` whole vs window share the entire path below `_eval`'s clipping, so the only difference is the window.

### What didn't work
- Nothing at import time; the first test run exposed test-side issues (Step 6).

### What I learned
- Relabelling input regions (`"... as input 0 of box(r=2)"`) makes guard failures much easier to read.

### What was tricky to build
- Choosing what `cells_computed` counts: output cells of each operation, per TASK.md. The consequence is that a
  point consumer asks its producer for exactly its own window, so a blur's reach shows up only when a consumer *has*
  a reach. I had to correct my own tests for this (Step 9).

### What warrants a second pair of eyes
- The cache branch: it exists only for `cache_whole` nodes and is written before the empty-window branch, so a
  cached statistic answers a sub-window correctly.

### What should be done in the future
- The test suite: references, invariance, globals, cost, guard, API.

### Code review instructions
- `stencilpipe/engine.py`: `Engine._eval` line by line against CHAPTER.md's flowchart.

## Step 6: First test run: whole-grid behaviour against independent references

I wrote `tests/support.py` (naive reference implementations of every operation from TASK.md, window helpers,
`probe_windows`, random chain generation) and `tests/test_operations.py`, then ran
`python3 -m unittest discover -s tests`.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Verify the library against formulas written independently from it before testing
windowing.

**Inferred user intent:** Confidence that "whole" means what TASK.md says, since every window claim is relative to it.

### What I did
- Created `tests/support.py` and `tests/test_operations.py`; ran the suite.

### Why
- The invariance test only compares against the library's own whole run, so an independent reference is needed to
  catch a wrong whole-grid definition.

### What worked
- `add`, `dx`, `normalize` matched exactly; extents (`half` of 7x5 -> 4x3) matched.

### What didn't work
- Three failures. `test_box` and `test_half` differed in the last bits because my reference adds cell by cell while
  the library adds row sums:
  `AssertionError: ... 0.30333...333334 ... != ... 0.30333...333333` and
  `0.65 != 0.6499999999999999`. `test_normalize_with_negative_maximum` had a wrong expectation: the library returned
  `[[4.0, 2.0], [1.0, 8.0]]` (dividing by max `-1.0`) and I had written `[[2.0, 1.0], [0.5, 4.0]]`.

### What I learned
- TASK.md fixes the mean's value but not its summation order, so a reference may legitimately differ in the last
  bit; the invariance requirement is about window vs whole of the same implementation, which must be exact.

### What was tricky to build
- Deciding to compare against references with `math.isclose(rel_tol=1e-12)` while keeping window-vs-whole comparisons
  exact. A tolerance everywhere would hide exactly the bug the chapter warns about, so it is confined to reference
  tests.

### What warrants a second pair of eyes
- Confirm the reference tests are the only place with a tolerance.

### What should be done in the future
- Fix the expectation, add the tolerance helper, then write the invariance tests.

### Code review instructions
- `tests/support.py` (`ref_*`, `assert_grids_close`) and `tests/test_operations.py`.

## Step 7: Fixing reference comparisons, then the invariance test

I added `assert_grids_close` to `tests/support.py`, used it for `box`/`half` reference tests, and corrected the
negative-maximum expectation. Then I wrote `tests/test_invariance.py`: every operation alone, after a blur, before a
blur, a deep mixed chain, 25 random chains, and special windows -- all with a fresh engine and a freshly built graph
per window, compared for exact equality with the same window cut from the whole result.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Apply CHAPTER.md's central proof obligation.

**Inferred user intent:** Evidence that every operation's footprint is exact, including directional and
pixel-moving ones and chained reaches.

### What I did
- Edited `tests/support.py` and `tests/test_operations.py`; created `tests/test_invariance.py`; ran the suite.

### Why
- Note 1: test every operation at the largest arguments used, alone and in chains, on fresh engines (a cache filled
  earlier can hide a short footprint), on interior, edge, corner, 1x1 and whole windows.

### What worked
- After the tolerance fix, the reference tests passed; the invariance matrix passed once the helper bug below was
  fixed.

### What didn't work
- 225 errors of the form
  `TypeError: cannot unpack non-iterable NoneType object` at `tests/support.py` line 87, from `probe_windows`
  including `None` (the whole extent) which my `cut` helper did not handle.

### What I learned
- `probe_windows` must include `None` (whole request) to test that a whole request equals a whole evaluation, so
  `cut(..., None)` needs a meaning.

### What was tricky to build
- Nothing deep; `cut` now returns a copy of the whole grid for `None`, using the same clipping rule as the library so
  overhanging and negative windows are comparable.

### What warrants a second pair of eyes
- The random-chain test uses grids up to 12x10 with `box(r=5)`; confirm the window set covers the corners of reduced
  (`half`) extents too (`probe_windows` uses the result extent, so yes).

### What should be done in the future
- Test the global statistic explicitly.

### Code review instructions
- `tests/test_invariance.py`: `check()` is the whole proof; note the fresh engine per window.

## Step 8: Testing the hidden global and its cache

I wrote `tests/test_global.py`: the window must divide by the whole grid's maximum (and differ from the window's own
maximum), two zooms must agree on a cell, the statistic is computed once and cached, a global barrier evaluates its
input whole, `m == 0`, negative maxima, and fresh engines start cold.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Prove that `normalize` is not accidentally window-local (the chapter's note 7 trap).

**Inferred user intent:** The same cell must look identical in two zooms, which is only true if the statistic is
global.

### What I did
- Created `tests/test_global.py`; ran the suite.

### Why
- Note 7: an unmarked global uses the window's percentile (here, maximum), so the same speck looks different in two
  zooms; splitting it keeps the application local and exact.

### What worked
- The window result matched the whole-cut result and differed from dividing by the window's own maximum; the cache
  made the second window cost only its own cells.

### What didn't work
- `test_global_barrier_computes_its_input_whole` failed:
  `AssertionError: 39 != 35`. My arithmetic had forgotten that the blur is computed twice: once on the requested
  window (4 cells) for the application, and once whole (30 cells) for the statistic, then the 4 application cells
  and 1 maximum cell.

### What I learned
- A global parameter costs one whole run of its input, which the chapter accepts ("a global operation stops the
  request at its own input and reads it whole"); the application still costs only its window.

### What was tricky to build
- Naming the statistic node with its input's label ("max of box(r=1)") so the barrier cost is traceable in errors.

### What warrants a second pair of eyes
- Whether the statistic's single cell should be counted at all; it is, because TASK.md says every operation counts
  every cell it computes.

### What should be done in the future
- Test that cost follows the window and that windows are never merged into a bounding box.

### Code review instructions
- `tests/test_global.py`; cross-check `_build_normalize` in `stencilpipe/engine.py`.

## Step 9: Testing cost accounting and correcting my own model of it

I wrote `tests/test_cost.py`: sources count nothing, whole vs window counts, chains where a consumer's reach widens
a producer's window, reaches adding along a chain, `half`, `normalize` with its cached statistic, `evaluate_many`
cost, and a small request on a 300x200 grid.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Show that the number of computed cells follows the request, not the grid.

**Inferred user intent:** Measurable evidence for the chapter's Motivation (a 64-pixel window must not cost the
whole scan).

### What I did
- Created `tests/test_cost.py`; ran the suite.

### Why
- TASK.md requires `cells_computed` and the chapter's Consequences claim cost follows request size.

### What worked
- `half` and `normalize` counts came out as expected (4 and 4+1, then 4 on the cached second window).

### What didn't work
- Three failures, all from my own misunderstanding of what is counted:
  `AssertionError: 32 != 52` for `box(r=1)` under `add` (a point consumer does not widen its producer's window, so
  box computes 4x4, not 6x6); `AssertionError: 102 != 272` for `box(2)` under `box(3)` (the inner box's output
  window is the outer window grown by the *outer* reach only, 10x9, plus the outer's 4x3); and
  `AssertionError: 96 != 168` for the 300x200 request (box computes exactly the 8x6 window because `add` is a point
  operation; 48 + 48 = 96).

### What I learned
- `cells_computed` counts *output* cells, so it exhibits the widening of *producers' output windows*, not the input
  area read. A producer's own reach shows up in the source read (guarded, not counted) or in a chain under a
  consumer with a reach. To demonstrate reaches adding, use a chain with two consumers that have reaches, e.g.
  `dx -> box(1) -> box(2)`: the window asked of `dx` is the request grown by 2+1.

### What was tricky to build
- Rewriting the tests to assert the true arithmetic (`4*3 + 8*7 + 10*9 = 158`) instead of weakening the assertions,
  and keeping the "far-apart windows are not merged into a bounding box" check (8 cells vs the 200-cell bounding
  box).

### What warrants a second pair of eyes
- Whether the test suite makes clear that the reach's *input* cost is tracked by the guard, not the counter.

### What should be done in the future
- Add guard tests for short footprints, and API tests for clipping.

### Code review instructions
- `tests/test_cost.py`; the comments state which node computes which window.

## Step 10: Guard tests and public-API tests

I wrote `tests/test_guard.py` (a `ShortBox` whose declared reach is one short, a `GreedyAdd` that peeks one cell
outside its window, direct `Region` bounds tests) and `tests/test_api.py` (clipping, degenerate windows, argument
checking, unknown names, aliasing, empty grids, stability of repeated requests).

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Prove the guard catches short footprints (note 3) and pin the public interface.

**Inferred user intent:** A wrong reach must fail loudly, and the API must behave as TASK.md describes at the edges.

### What I did
- Created `tests/test_guard.py` and `tests/test_api.py`; ran the suite.

### Why
- Note 3: guard every read, sources included; a short reach must fail at once instead of shifting edge values.
- TASK.md: windows are clipped to the node's extent.

### What worked
- `ShortBox` raises `FootprintError` whose message names the source and the declared footprint; `GreedyAdd` raises
  for one cell outside a 2x2 window; border windows of `box(r=4)` need no margin outside the grid.

### What didn't work
- `test_windows_are_clipped_to_the_extent` failed with
  `[[14.0, 15.0], [19.0, 20.0]] != [[11.0, 12.0], [16.0, 17.0]]` -- I had miscomputed my own test grid
  (`grid[y][x] = 5y + x`). `test_empty_grid` failed with `Lists differ: [[]] != []` for `source([[]])`: a row with no
  columns still produced one row. `test_window_rows_have_the_window_size` failed with `1 != 2` because the window
  (1,1,2,2) on a 3x2 `half` result clips to 1x1.

### What I learned
- A grid with zero columns should have extent `(0, 0)` whatever its row count, otherwise "empty" is ambiguous.

### What was tricky to build
- The fix was in the library, not the test: `Node.extent` for a source now derives `(width, len(grid) if width else
  0)`.

### What warrants a second pair of eyes
- The `Region` direct tests assert `FootprintError` is a `RuntimeError`; check that is the intended public base.

### What should be done in the future
- A final full run, plus a check of the diary.

### Code review instructions
- `tests/test_guard.py`, `tests/test_api.py`; `Node.extent` in `stencilpipe/engine.py`.

## Step 11: Final check

I re-ran the whole suite, compiled every module, and read the diary against `DIARY-FORMAT.md`. All 55 tests pass.
I also replaced `MaxStat`'s per-cell comparison loop with `max(row)` per row (same result, much faster on large
inputs) and removed an unused import from `tests/support.py`; the suite still passes.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Finish with a green suite, a complete diary, and the required JSON message.

**Inferred user intent:** A build that can be trusted without re-reading every test: exact windowed results, guarded
reads, honest cost accounting.

### What I did
- Ran `python3 -m unittest discover -s tests` (55 tests, OK) and `python3 -m compileall stencilpipe tests`.
- Re-read `DIARY.md` for format completeness.
- Optimised `MaxStat.run` to `max(row)` per row and removed the unused `random` import from `tests/support.py`;
  re-ran the suite (55 tests, OK).

### Why
- The final message must follow `TASK.md`'s format only after the tests pass and the diary is complete.
- `MaxStat` reads the whole input of a chain, so a C-level row maximum matters for real use (chapter Motivation:
  memory and time on large scans).

### What worked
- Everything green: references, invariance including random chains, global statistic and cache, cost accounting,
  guard, API.

### What didn't work
- No failures in the final run.

### What I learned
- `cells_computed` is a good proxy for output work but not for input reads; the guard is what enforces reads. The
  chapter's note 6 (scale conversion) and note 10 (tiles) did not apply: one scale, and windows are computed on
  their own.

### What was tricky to build
- Keeping the "no cost rule" decision honest: a whole run could occasionally be cheaper for a huge window, but adding
  one would make `cells_computed` and the invariance story harder to reason about, and the chapter calls it optional.

### What warrants a second pair of eyes
- `Normalize`'s `m == 0` semantics and the decision to count the statistic's one cell are the two places where the
  spec allowed interpretation.

### What should be done in the future
- If overlapping requests become common, add the chapter's tile grid or per-cell memo; if more scales appear, declare
  reaches in source pixels and convert in one place (note 6).

### Code review instructions
- Run `python3 -m unittest discover -s tests`; read `stencilpipe/engine.py:Engine._eval` and
  `stencilpipe/ops.py:Operation.footprint` together with `tests/test_invariance.py`.

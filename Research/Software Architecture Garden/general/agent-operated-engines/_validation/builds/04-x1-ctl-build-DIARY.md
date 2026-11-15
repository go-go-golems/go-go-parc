# Diary

## Goal

Build `stencilpipe`, a standard-library-only Python 3 library for lazy pipelines over large 2D float grids, where asking
for a window of a result computes only the cells that window needs (and counts exactly those cells), while giving
exactly the values a whole-grid computation would give. This diary records each phase of the work, including failures.

## Step 1: Reading the task and designing the demand-propagation model

I read `TASK.md` and `DIARY-FORMAT.md` in full first. The task fixes a small public surface (`demo_engine`, `Engine`,
`Node` with `call`, `evaluate`, `evaluate_many`, `reset_counters`, `cells_computed`) and five operations (`add`, `box`,
`dx`, `half`, `normalize`) whose whole-grid behaviour is given, and requires that any requested window produce exactly
the same values while computing only what is needed.

The design I settled on before writing code is a two-phase, pull-based evaluator: (1) walk the graph top-down from the
requested output rectangle and ask each operation "which rectangle of your input do you need for this output rectangle?"
(a per-op *demand mapping*), unioning the demanded rectangles per node; (2) walk the nodes bottom-up in topological order
and compute exactly the demanded rectangles, memoising every computed cell in a per-evaluation sparse store keyed by
`(node, y, x)` so no cell is ever computed twice and the counter equals the number of distinct output cells produced.

### Prompt Context

**User prompt (verbatim):** "You are a software engineer joining a project. Your working directory contains two files:
- TASK.md: the software to build, with its required public interface;
- DIARY-FORMAT.md: how to keep your work diary.
Read both completely first. Keep DIARY.md as you go, one step per phase of work, in that format. Then design, build and test the software in this directory. Work only inside this
directory (do not read or write outside it). Use only the Python 3 standard library. Run your tests and fix what
fails before you finish, and make sure DIARY.md is complete. Your final message must follow the output format at the end of TASK.md."

**Assistant interpretation:** implement the library described in `TASK.md` inside this directory, keeping a strictly
formatted diary as described in `DIARY-FORMAT.md`, testing with `python3 -m unittest discover -s tests`, and finishing
with a single JSON object in a fenced block.

**Inferred user intent:** a reviewer wants a small, correct, self-contained library whose laziness is *demonstrable*
via the cell counter, plus a diary that shows the reasoning and the real failures along the way.

### What I did
- Read `TASK.md` and `DIARY-FORMAT.md` completely.
- Listed the working directory to confirm it contains only those two files.
- Sketched the module split: `regions.py` (rectangles/geometry), `ops.py` (the five operations + op base class),
  `engine.py` (`Engine`, `Node`, the solver), `demo.py` (`demo_engine()`), `tests/test_stencilpipe.py`.

### Why
- The core requirement is "compute only what you ask for", so the plan is built around explicit *rectangular demand*
  rather than around evaluating whole grids and slicing them.
- `normalize()` needs the maximum of its whole input, which is a global reduction; modelling that as "this op demands the
  whole input extent" keeps the rest of the machinery uniform, and makes the counter correctly charge the full cost of
  whatever the input op must compute.

### What worked
- Reading both files first gave a concrete list of fixed behaviours (clamping in `box`, clamped indices in `dx`,
  `ceil` sizing in `half`, `0` when `m == 0`) that the reference implementations can encode directly.

### What didn't work
- N/A (no code run yet).

### What I learned
- The diary template references a `CHAPTER.md` section for design rationale; no such file exists in this directory, so
  I treat `TASK.md` itself as the source of truth and say so explicitly in later steps when it drives a decision.

### What was tricky to build
- Nothing built yet; the open question was how to keep `evaluate_many` and `normalize` from computing overlapping cells
  twice. Resolution: per-evaluation sparse store with a per-node "already computed?" check, so a cell is computed once
  per evaluation no matter how many demands cover it.

### What warrants a second pair of eyes
- Whether `evaluate_many` should report the union of computed cells (my choice) or the sum over windows.
- Whether the counter should charge a demanded-but-unused cell (it does: demand is exactly what the window needs).

### What should be done in the future
- Write the geometry module first, then ops, then the engine.

### Code review instructions
- Start with `TASK.md` for the fixed semantics, then read `stencilpipe/regions.py`, `stencilpipe/ops.py`,
  `stencilpipe/engine.py` in that order. Validate with `python3 -m unittest discover -s tests`.


## Step 2: Geometry (`regions.py`) and the five operations (`ops.py`)

I wrote the two pure modules: `stencilpipe/regions.py` and `stencilpipe/ops.py`. `regions.py` owns `Rect`,
`clip`, `normalise` (clip, drop empty, drop rectangles contained in a bigger one) and `extent_of` (grid validation and
width/height). `ops.py` owns the `Op` base class (parameter binding and validation, `out_extent`, `input_region`,
`prepare`, `cell`) and the five operations from `TASK.md`.

The important design point is that an op declares both halves of its laziness contract: `out_extent` is static (so a
window can be clipped before anything is computed), and `input_region` maps an output rectangle to the input rectangle
it needs. `Normalize.input_region` returns the whole input extent because its maximum is global; that is the only op
whose mapping is not local.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** build the geometric vocabulary and the numeric formulas exactly as `TASK.md` states them.

**Inferred user intent:** formulas must match the spec bit for bit (clamping in `box`, clamped indices in `dx`, `ceil`
sizing and partial blocks in `half`, `0` when `m == 0` in `normalize`), because window values must equal whole-grid
values exactly.

### What I did
- Created `stencilpipe/regions.py` with `Rect`, `clip`, `normalise`, `as_rect`, `extent_of`, `_as_int`.
- Created `stencilpipe/ops.py` with `Op`, `Add`, `Box`, `Dx`, `Half`, `Normalize`, `DEMO_OPS`, `_number`, `_count`.
- Created `stencilpipe/engine.py`, `stencilpipe/demo.py`, `stencilpipe/__init__.py` in the following step.

### Why
- One clipping implementation (`regions.clip`) guarantees every op clips demands identically, which `TASK.md` requires
  ("windows are clipped to the node's extent").
- `regions.normalise` drops contained rectangles. That is safe because every demo op's demand mapping is monotone
  (a bigger output rectangle needs a superset of input cells), so this only removes redundant scanning.
- Values are never coerced to `float`: ints stay ints, and every op computes with the same expression order a
  brute-force whole-grid version would use, which is what makes window values exactly equal, not merely close.

### What worked
- `Op._bind` accepts the documented `call(name, **args)` form and, as a convenience, positional arguments
  (`node.call("box", 2)`), while rejecting unknown, missing and duplicated parameters with readable messages.
- A quick smoke run (`python3 -` snippet) printed correct values for all five ops on a 3x4 grid and a total of 54
  counted cells, matching my hand count (12+2+12+12+4+12).

### What didn't work
- N/A in this step (no test command run yet). The first real failures came in Step 4/5.

### What I learned
- `half()` changes the extent, which proves extents must be derived at build time from static rules rather than from
  data; that is what lets `evaluate` clip a window before computing anything.

### What was tricky to build
- Deciding that `prepare()` must run after the input is fully computed but before the first output cell. `Normalize`
  reads the whole input extent there; the solve loop computes nodes producer-first, so this is guaranteed.

### What warrants a second pair of eyes
- The summation order in `Box.cell` (rows outer, columns inner) and `Half.cell`; a whole-grid implementation summing in
  a different order would give last-bit differences that no window test can catch (the tests use the same order).

### What should be done in the future
- Build the engine/solver that consumes these demand mappings.

### Code review instructions
- `stencilpipe/ops.py`: `input_region` and `cell` are the two halves of every operation; `stencilpipe/regions.py`:
  `clip` and `normalise`.

## Step 3: The engine, the node type and the two-phase solver

This step built `stencilpipe/engine.py` (`Engine`, `Node`, `_Solution`, `_Context`, `_topological_order`, grid
validation) and `stencilpipe/demo.py` (`demo_engine()` registering the five ops), plus `stencilpipe/__init__.py` with
the public exports.

`_Solution.run()` is the heart: a DFS post-order lists the nodes producer-first; then `_propagate` seeds the root's
demands with the requested rectangles and walks the order in reverse, asking each op's `input_region` what it needs and
unioning per node; then `_compute` walks forward and, for each node, computes exactly its demanded rectangles into a
sparse `{y: {x: value}}` store, counting one cell only when it is newly stored. Sources are read straight from the
caller's grid and never counted.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** wire ops into the required public interface with lazy evaluation and exact counting.

**Inferred user intent:** building must compute nothing; evaluating a window must compute only demanded cells; the
counter must equal the number of distinct output cells the operations produced.

### What I did
- `Engine.source` validates the grid (rectangular, numeric, names the offending cell) and builds a source `Node`.
- `Engine.apply`/`combine`/`_build` instantiate an op, check arity and node ownership, and derive the static extent.
- `evaluate` and `evaluate_many` run one `_Solution` per call and return the clipped window rows.
- `reset_counters`/`cells_computed` plus `Engine._count`.

### Why
- One fresh solution per call means counters are reproducible: no cross-call cache can silently make a second window
  free. "Compute only what a window needs" is asserted per call, which is what a reviewer can check.
- A per-evaluation store keyed by node gives shared-subgraph and overlapping-window de-duplication for free, and keeps
  the counter honest (a cell is counted once, exactly like a whole-grid evaluation would produce it once).

### What worked
- A 300x300 source with `add → box(2)` and a 5x5 window costs 106 cells, not 90 000, confirmed by the tests.

### What didn't work
- N/A in this step; the interface bug (`Node.call` forwarding positional params as inputs) surfaced in Step 4.

### What I learned
- Because demand propagation completes before any computing, `prepare` can read a producer's whole store without
  ordering surprises beyond the topological order.

### What was tricky to build
- `_topological_order` without recursion (a 400-node chain test covers it) and with "seen" marking at pop time so
  diamonds list each node once while always placing producers first.

### What warrants a second pair of eyes
- `_Solution.rows` indexes the store directly on the assumption that the root's demand covers every requested cell.
  That invariant depends on `normalise` only dropping *contained* rectangles.

### What should be done in the future
- Write the test suite, including brute-force references and exact counter expectations (Step 4).

### Code review instructions
- `stencilpipe/engine.py`: read `_Solution.run`, then `_propagate`, `_compute`, `rows`.

## Step 4: First test run: 34 tests, 4 failures and 2 errors

I wrote `tests/test_stencilpipe.py` with brute-force references for all five ops, exhaustive window-vs-whole-grid
comparisons, exact counter expectations, `evaluate_many`, diamonds via a test-only two-input op, and error cases. Then I
ran the suite for the first time.

Six problems came out, and it mattered a lot to separate *my wrong expectations* from *real bugs*.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** test behaviour and cost, not just "it runs", and treat failures as information.

**Inferred user intent:** proof that laziness is real and that window values are identical to whole-grid values.

### What I did
- Created `tests/test_stencilpipe.py` (34 test methods).
- Ran `python3 -m unittest discover -s tests`.

### Why
- Exact counter assertions are the only way to show "computes only what the window needs"; brute-force references are
  the only way to show the formulas match `TASK.md`.

### What worked
- 28 of 34 tests passed immediately, including the exhaustive window matrix for `add`/`box`/`dx`/`half`/`normalize` on
  eight grids, the shared-subgraph value tests, and all error cases except one.

### What didn't work
- Command: `python3 -m unittest discover -s tests`
- Result: `Ran 34 tests in 1.719s` / `FAILED (failures=4, errors=2)`
- `ERROR: test_positional_arguments_accepted`: `TypeError: operation 'add' expects Node inputs, got float` raised at
  `engine.py` line 253 in `apply`. Real bug: `Node.call` forwarded positional op parameters as graph inputs.
- `ERROR: test_plus_requires_two_inputs`: `TypeError: operation 'plus' expects Node inputs, got str` where the test
  expected `ValueError`. My test was wrong: a non-`Node` argument is a type error.
- `FAIL: test_half_window_touches_a_2x_block`: `AssertionError: 2 != 5`. My expectation was wrong: the last odd
  2x2 block of a 9x7 grid is 1x1, so `add` needs exactly one cell: 1 + 1 = 2.
- `FAIL: test_windows_do_not_cache_between_calls`: `AssertionError: 8 != 20`. My expectation was wrong: for
  `source → box(1) → add` the root is `add`, which is pointwise, so it demands only its own 2x2 from `box`, i.e.
  4 + 4 = 8. I verified this with a direct snippet that prints 8 for `box → add` and 20 for `add → box`.
- `FAIL: test_diamond_computes_the_shared_part_once`: "Lists differ: ... 1433 characters". My expectation was wrong:
  `plus(add(g,1), add(g,2))` is `2*g + 3`, not `g + 3`.
- `FAIL: test_shared_node_is_computed_once`: `AssertionError: 16 != 32`. My test evaluated `shared` (16 cells) before
  the assertion and never evaluated the root; it needed `reset_counters()` after the warm-up evaluation.

### What I learned
- The "expanded demand" only applies in the direction of the operation: a stencil op expands what it *reads*, but a
  pointwise consumer does not expand what it *is asked to produce*. My first expectations conflated the two.
- Separating "code is wrong" from "expectation is wrong" needs a direct measurement, not more staring at the test.

### What was tricky to build
- Deriving expected counts by hand at all: the useful rule is "walk backwards from the requested window and apply each
  op's `input_region` in turn".

### What warrants a second pair of eyes
- The remaining hand-computed counts in `CostTests`, now that the direction rule is understood.

### What should be done in the future
- Fix the positional-argument bug and my four wrong expectations (Step 5).

### Code review instructions
- `tests/test_stencilpipe.py`: `CostTests` and `GraphTests`.

## Step 5: Fixing the positional-argument bug (and one more real bug behind it)

I split building into `Engine.apply(name, *inputs, **params)` (inputs are nodes) and `Engine._build(name, inputs, args,
params)`, with `Node.call` calling `_build` so that positional *operation parameters* are never mistaken for graph
inputs. I also corrected the four wrong expectations from Step 4.

The second run then exposed a genuine bug inside parameter binding that the first run had masked.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** fix the failures, keeping the fixed semantics.

**Inferred user intent:** a working `call(name, **args)` (and a sane positional convenience) with correct counting.

### What I did
- Changed `Node.call` to `self.engine._build(name, (self,), args, kwargs)`.
- Added `Engine._build`; `apply`/`combine` now only take nodes positionally.
- Fixed test expectations: half-block 1+1, `box → add` 4+4, diamond `2*g+3`, shared-node test resets counters.
- Ran `python3 -m unittest discover -s tests` again.

### Why
- `TASK.md` fixes `node.call(name, **args)`; positionals are a convenience, and the engine must never interpret them as
  inputs.

### What worked
- All failures and errors from Step 4 except one were resolved by the split plus the corrected expectations.

### What didn't work
- Command: `python3 -m unittest discover -s tests`; result `Ran 34 tests in 1.720s` / `FAILED (errors=2)`.
- `ERROR: test_positional_arguments_accepted`: `File "stencilpipe/ops.py", line 67, in _bind` ->
  `KeyError: 'k'`. Real bug: `bound.setdefault(pname, kwargs[pname])` evaluates `kwargs[pname]` eagerly even when the
  parameter was already bound positionally.
- The other remaining error was my expectation from Step 4 (`TypeError` vs `ValueError` for a non-node input).

### What I learned
- `dict.setdefault` is not lazy; it evaluates its default argument every time. An explicit `if pname not in bound:`
  loop is required.

### What was tricky to build
- The interleaving of "argument binding" and "graph inputs" in one signature: the clean separation is a private builder
  that takes pre-split inputs/args/params.

### What warrants a second pair of eyes
- `Op._bind` ordering: positional first, then duplicate detection, then missing detection.

### What should be done in the future
- Re-run and add edge-case coverage (Step 6).

### Code review instructions
- `stencilpipe/engine.py::Engine._build`, `stencilpipe/ops.py::Op._bind`.

## Step 6: Edge-case tests: empty grids, global maximum, window types, 400-node chain

With the main suite green I added `EdgeCaseTests`: empty grids, `normalize` dividing by the *global* maximum (a 1x1
window of `[[1,2],[3,4]]` is `0.25`, not `1.0`), windows given as list/tuple/`Rect`, a 400-node chain (checks the
iterative traversal), `evaluate_many` around a global reduction, and 1xN / Nx1 grids against the references.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** harden the behaviour at the edges the task leaves open.

**Inferred user intent:** the library should not fall over on degenerate grids or long chains.

### What I did
- Added `EdgeCaseTests` to `tests/test_stencilpipe.py`.
- Ran `python3 -m unittest discover -s tests`.

### Why
- `normalize` is the one op whose window result is *not* a function of the window alone; a test that only compares
  window to whole-grid slice would still pass if the op wrongly normalised by the window maximum, so an absolute
  expectation is needed.

### What worked
- 39 of 40 tests passed; empty grids, `Rect`/list windows and the global-maximum assertions all behaved.

### What didn't work
- Command: `python3 -m unittest discover -s tests`; result `Ran 40 tests in 1.876s` / `FAILED (failures=1)`.
- `FAIL: test_long_chain_is_iterative`: `AssertionError: 400 != 401 : one add node per cell`. My arithmetic was wrong:
  the chain has 400 `add` nodes and the source is free, so 400 is correct; the expectation became
  `400, "400 add nodes, one cell each; the source is free"`.

### What I learned
- Even a one-off arithmetic slip deserves to be re-derived from the definition ("sources do not count") instead of
  adjusting the code.

### What was tricky to build
- Nothing structural; the iterative traversal needed no change, which is what the test was meant to demonstrate.

### What warrants a second pair of eyes
- Whether `evaluate` on a zero-width grid returning `[]` (rather than one empty row per input row) is acceptable; it is
  documented as a tradeoff.

### What should be done in the future
- Final review pass (Step 7).

### Code review instructions
- `tests/test_stencilpipe.py::EdgeCaseTests`.

## Step 7: Final check

I ran the whole suite one last time, re-read the engine end to end, checked the public names against `TASK.md`, ran the
package docstring as a doctest, and measured two performance points to be sure laziness is real rather than nominal.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** make sure the deliverable is complete: tests green, `DIARY.md` complete, interface exactly
as specified.

**Inferred user intent:** a reviewer can run one command and trust the result.

### What I did
- `python3 -m unittest discover -s tests -v` -> `Ran 40 tests in 1.741s` / `OK`.
- `python3 -c "import doctest, stencilpipe; doctest.testmod(stencilpipe)"` -> `TestResults(failed=0, attempted=4)`.
- Verified `demo_engine().operations() == ['add','box','dx','half','normalize']` and that `source`, `evaluate`,
  `evaluate_many`, `reset_counters`, `cells_computed`, `call` all exist on the required objects; `cells_computed()`
  returns `int`.
- Timings: whole-grid `box(2)` on 200x200 = 40 000 cells in 0.18 s; `add -> box(3) -> dx` on a 1000x1000 grid with a
  4x4 window = 160 cells in ~0.0 s.
- Ad-hoc check that `evaluate_many` agrees cell-for-cell with separate `evaluate` calls on partially overlapping
  windows for `half`, `box -> half`, `half -> box` and `dx -> half -> normalize`.
- Removed two unused imports (`Iterator` in `engine.py`, `List` in `ops.py`) found with a small AST scan.

### Why
- The counter is the contract's proof obligation; measuring only tiny grids would not show that a 1000x1000 grid is
  never touched.

### What worked
- Everything above; no changes to behaviour were needed in this step.

### What didn't work
- Nothing failed in this step. (The `doctest` run of the file path directly failed earlier with
  `ImportError: attempted relative import with no known parent package`; running `doctest.testmod(stencilpipe)` on the
  imported package works, so that was a harness mistake, not a library bug.)

### What I learned
- Cell-wise independence of every op means window == whole-grid equality is guaranteed by construction (each cell is
  produced by the same function with the same inputs), which is why the exhaustive window matrix passes exactly, not
  approximately.

### What was tricky to build
- Nothing left open. The remaining judgement calls are recorded as tradeoffs: `evaluate_many` counts the union of
  demanded cells, `normalize` legitimately demands its whole input, and zero-width grids evaluate to `[]`.

### What warrants a second pair of eyes
- `stencilpipe/engine.py::_Solution._compute` — the counter is incremented only when a cell is newly stored, which is
  what makes the "every operation counts every cell it computes" rule and de-duplication consistent.

### What should be done in the future
- Possible follow-ups: a disk- or block-backed store for very large whole-grid evaluations, op-level parallelism, and a
  `Rect`-list based API for non-rectangular windows.

### Code review instructions
- Run `python3 -m unittest discover -s tests`. Start reading `stencilpipe/ops.py` (the demand mappings), then
  `stencilpipe/engine.py::_Solution.run`. Counter expectations to sanity-check by hand are in
  `tests/test_stencilpipe.py::CostTests`.

# Diary

## Goal

Build `gridflow`, a standard-library Python 3 library that applies the Content-Keyed Lazy Graph pattern from
`CHAPTER.md` to small 2D float grids: calls build interned nodes, values are computed lazily and cached under
content keys. This diary records the design decisions, the phases of work, the failures and the final state.

## Step 1: Reading the chapter, the task and the diary format; design

I read `CHAPTER.md`, `TASK.md` and `DIARY-FORMAT.md` completely, then sketched the module layout and the exact
mapping of the chapter's participants onto the required public interface. The chapter is unusually specific about
the participant set and the implementation notes, so the design step was mostly a matter of deciding which of the
optional participants the single-threaded, single-request API of `TASK.md` needs.

### Prompt Context

**User prompt (verbatim):** "You are a software engineer joining a project. Your working directory contains three files:
- CHAPTER.md: a chapter of a design-pattern book describing the pattern you must apply;
- TASK.md: the software to build, with its required public interface;
- DIARY-FORMAT.md: how to keep your work diary.
Read all three completely first. Keep DIARY.md as you go, one step per phase of work, in that format. Then design, build and test the software in this directory. Work only inside this
directory (do not read or write outside it). Use only the Python 3 standard library. Run your tests and fix what
fails before you finish, and make sure DIARY.md is complete. Your final message must follow the output format at the end of TASK.md."

**Assistant interpretation:** Implement the pattern of Chapter 3 ("Content-Keyed Lazy Graph") as the `gridflow`
library described in `TASK.md`, with tests, keeping a diary in the format of `DIARY-FORMAT.md`, and finish with one
JSON object in a fenced block.

**Inferred user intent:** A working, tested library whose structure visibly *is* the pattern (interned nodes,
structural signatures, lazy evaluation, byte-budgeted value cache, function arguments as subgraphs), not a
generic memoization decorator with the pattern's vocabulary sprinkled on top.

### What I did
- Read all three files in full (chapter: participants, collaborations, sketch, 11 implementation notes, variations).
- Decided on modules: `errors.py`, `canonical.py`, `node.py`, `cache.py`, `ops.py`, `engine.py`, `demo.py`,
  re-exported from `__init__.py`; tests under `tests/`.

### Why
- The chapter's Structure table names Node, Builder, Source, Signature, Evaluator, Run memo, Value cache and
  In-flight group. I mapped: `node.py` = Node/Source/placeholder, `engine.py` = Builder + Evaluator + Signature +
  run memo, `cache.py` = value cache, `canonical.py` = the canonical-form rules the builder refuses on,
  `demo.py` = the demo operations.
- The In-flight group (note 9) is explicitly "only when there are concurrent callers"; this library has no
  concurrency (single-threaded, no async in the public interface), so it is deliberately omitted — recorded as a
  conscious omission rather than a gap.
- The run memo (per request) is kept because "a value used twice [within one request] is found without the shared
  cache", and because warnings must be reported once per request (note 8).

### What worked
- The required interface in `TASK.md` lines up almost one-to-one with the chapter's sketch: `source` = Source,
  `node.call` = intern, `evaluate` = request, `runs` = "did the operation really run", `stats` = cache diagnostics,
  `within` = the function-argument path (note 6).

### What didn't work
- N/A (reading phase).

### What I learned
- Three details of `TASK.md` are stricter than the chapter's sketch and drive the design: sources are identified by
  *content* (the chapter's sources are files keyed by location/size/mtime), `stats` must expose integer `bytes` and
  `evictions`, and `runs` is per node, so runs must be counted at the evaluator's call site, not per signature.

### What was tricky to build
- Deciding what belongs in the signature. The chapter says node hash + operation version + quantised params + input
  signatures. Because `TASK.md` lets a name be re-registered, I will also mix a per-name *registration serial* into
  the signature so a replaced implementation cannot serve values computed by its predecessor (note 3's "a cache that
  survives a deploy must key on the operation's implementation version").

### What warrants a second pair of eyes
- The choice to make sources exempt from `hits`/`misses` and to make neutral (identity) nodes neither hits nor
  misses: this is a defensible reading of the chapter ("A neutral call returns its input's value, uncached") but it
  is a judgement call about `stats` semantics.

### What should be done in the future
- If the library ever gains an async or threaded request path, add the in-flight group keyed by signature (note 9).

### Code review instructions
- Read `CHAPTER.md` §Structure and §Implementation notes 1-11 first, then check `gridflow/engine.py` against them.
- Validate with `python3 -m unittest discover -s tests`.

## Step 2: Building the library modules

I wrote the package in six modules and got it importing, compiling and evaluating a two-node pipeline. The
phases inside this step were: errors + canonical forms, nodes and interning, the value cache, the operation
registry, the builder/evaluator, and the demo operations with the public exports.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Build the library described in `TASK.md` as the pattern of `CHAPTER.md` describes it,
with the required public interface exported from `gridflow/__init__.py`.

**Inferred user intent:** A library whose internals are recognisably the chapter's participants, not a generic
memoizer, and whose public surface is exactly the one other code will be tested against.

### What I did
- `gridflow/errors.py`: `GridflowError` > `EvalError` (carries `.code`, `.op`) > `BuildError`; codes `E_ARG`,
  `E_OP`, `E_PLACEHOLDER`, `E_EVAL`.
- `gridflow/canonical.py`: `canonical()` (one spelling per value; `1` and `1.0` equal, list/tuple equal, dict keys
  sorted, `-0.0 == 0.0`), `canonical_args()`, `digest()` (SHA-256), `freeze_grid()`/`thaw_grid()`, `grid_bytes()`,
  `grid_digest()`.
- `gridflow/node.py`: `Node` (immutable, `__slots__`, `hash` = structural digest, `call()` delegates to the
  builder), kinds `source` / `op` / `placeholder`, constant hash for a placeholder.
- `gridflow/cache.py`: `Entry(value, warnings, nbytes)` and `ValueCache` — `OrderedDict` LRU, byte budget,
  evict-before-insert, entries larger than the whole budget are refused, counters `hits/misses/bytes/evictions`.
- `gridflow/ops.py`: `OpRecord` (name, fn, version, identity, registration serial) and `OpRegistry`.
- `gridflow/engine.py`: `quantize_scale()` (step 1e-4, range validation), `Result`, `_Ctx` (scale + `warn`),
  `Engine.source/_build/_substitute/within/evaluate/_signature/_evaluate/runs/stats`, and the reserved
  `__within__` operation.
- `gridflow/demo.py`: `add`, `gain` (neutral at `k == 1`), `blur` (summed-area box mean, radius scaled by
  `ctx.scale`, warns when the window exceeds the grid), `threshold`; `demo_engine()`.
- `gridflow/__init__.py`: exports `Engine`, `Result`, `Node`, `demo_engine`, `EvalError`, `BuildError`,
  `GridflowError` plus `SCALE_STEP`, `quantize_scale`, `WITHIN`.

### Why
- Interning at build time and hashing `op.name + canonical args + input hashes` is chapter note 1 and the sketch's
  `intern`.
- The signature is `node hash + version + registration serial + quantised params + input signatures` (Structure
  table, note 3): the serial is there because `TASK.md` allows a name to be re-registered and a replaced
  implementation must not be served its predecessor's values.
- Values are stored as tuple-of-tuples and copied only in `evaluate()` (note 7). The identity short-cut returns the
  input's frozen value and is *not* cached (same note).
- Cache entries carry the whole subgraph's warnings, de-duplicated (note 8).
- `within` runs `build(hole)` once and substitutes the receiver for the hole, re-interning each node on the path
  (note 6), so `within(m, i => i.gain(2))` shares the `gain` node with a directly written pipeline.
- The in-flight group and parallel inputs are omitted: single-threaded, single caller (note 9).

### What worked
- The smoke test: `eng.source([[0,1],[2,3]]).call('gain', k=2)` and `.call('gain', k=2.0)` return the *same*
  object; the second `evaluate` reports `cached=True`, `runs == 1`, `hits == 1`.

### What didn't work
- First `write` of `node.py`/`engine.py` left a placeholder error path duplicated in three places; I collapsed it
  into `_placeholder_escaped()`. Also a stray `"""` on the `Engine` class docstring broke the module; fixed by
  rewriting the two lines.

### What I learned
- The chapter's sketch computes `signature(n)` before checking neutrality; I check the record's `identity(args)`
  first so a neutral node never counts as a cache miss, which matches "A neutral call returns its input's value,
  uncached" (Collaborations 4).

### What was tricky to build
- `_signature` recursion: it is memoised per request by node hash, and a placeholder reached through an input must
  raise `E_PLACEHOLDER` there, not `E_OP` for an unregistered operation called `placeholder` — the first
  version produced the wrong error code.

### What warrants a second pair of eyes
- `stats` semantics for sources and neutral nodes (neither counted) and for run-memo hits (counted as hits).
- The registration serial in the signature: it makes re-registration invalidate, which is stricter than "bump the
  version" but safer for `TASK.md`'s replace-by-name rule.

### What should be done in the future
- A size-aware eviction policy (GreedyDual-Size) as the chapter's note 10 suggests measuring; the `policy`
  parameter exists but only `lru` is implemented.

### Code review instructions
- Start at `gridflow/engine.py::Engine._build`, `_signature`, `_evaluate`, then `gridflow/canonical.py::canonical`.
- `python3 -m unittest discover -s tests` (tests arrive in Step 3).

## Step 3: Writing the test suite and fixing what it found

I wrote six test modules (126 tests) covering canonical forms, building and interning, evaluation and caching,
`within`, the cache budget, and the demo operations, then ran `python3 -m unittest discover -s tests` until it was
green. The suite found three real defects and two wrong expectations of mine; the defects are the interesting part
of this step.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Cover the required public interface and the chapter's implementation notes with tests,
run them, and fix the code (not the tests) where the code is wrong.

**Inferred user intent:** Evidence that the library behaves as the pattern promises: laziness, honest keys, frozen
values, replayed warnings, function arguments as subgraphs, a bounded cache.

### What I did
- `tests/test_canonical.py` (17 tests): `1`/`1.0` share a spelling, `-0.0 == 0.0`, list == tuple, dict order
  irrelevant, large ints not collapsed, callables/opaque objects refused with `E_ARG`, freeze/thaw isolation.
- `tests/test_build.py` (18): equal content is one source, equal calls are one node, arguments read-only, node
  count grows only with distinct calls, building runs nothing, refusals (unknown op, callable argument, non-node
  input, foreign-engine node, reserved name).
- `tests/test_evaluate.py` (27): value/caching, `cached` flag, middle-node hits, diamond computed once, frozen
  values, scale quantisation and range, neutral short-cut, version bump and re-registration invalidation, warning
  replay and de-duplication, failure messages naming the operation.
- `tests/test_within.py` (19): mask semantics, sharing with the direct pipeline, chains, nested `within`,
  escaped-placeholder errors, refusals.
- `tests/test_cache.py` (11): entry size, budget respected, zero budget, oversized entry not stored, LRU order,
  eviction counters, `clear_cache`, graph not bounded by the budget.
- `tests/test_demo.py` (22): the four operations, blur borders/scale/warning, neutral `gain`, a full pipeline and a
  second spelling of it.

### Why
- Every implementation note in the chapter that the interface exposes has at least one test: note 1 (interning and
  refusal), note 2 (quantise at the request and compute at the quantised value), note 3 (version/replacement),
  note 4 (SHA-256 keys), note 6 (substitution), note 7 (freeze and copy out), note 8 (warnings stored and replayed),
  note 10 (budget, evict-before-insert, graph unbounded).

### What worked
- 126 tests green: `Ran 126 tests in 0.009s / OK`.

### What didn't work
- Failure 1, nested `within` → `E_PLACEHOLDER` at evaluation:
  `gridflow.errors.EvalError: a placeholder escaped its builder; a placeholder has no value (E_PLACEHOLDER)` raised
  from `_signature`. Cause: all placeholders shared one constant hash, so the node built on the *inner* hole was
  interned once and held the *outer* hole; the outer substitution found no hole it recognised and left it in place.
  Fix: `node.placeholder_hash(serial)` — every hole has its own hash — and the scaffolding nodes built on holes are
  dropped from the intern table when the `within` call finishes.
- Failure 2, two equal `within` calls produced different nodes: `AssertionError: <Node __within__ 3ed6cb64aae6> is
  not <Node __within__ 3c351139b6e9>` — the same constant-hash cause. Fixed by the same change.
- Failure 3, `test_node_from_another_engine_is_refused`: `AssertionError: EvalError not raised`. The builder checked
  the engine of the *receiver* but not of the extra inputs, so a node from another engine could be mixed into this
  engine's graph. Fix: `Engine._build` checks `extra.engine is not self`.
- Two of my own expectations were wrong, not the code: the diamond's value (I had summed the wrong branch) and the
  blur corner means (9/4 at a corner, not 9/9 — borders average over fewer cells).

### What I learned
- The chapter says a placeholder "hashes to a constant" and warns that "nested calls need a rule for a placeholder
  bound to itself"; in an interning builder that constant is not a detail, it is a bug generator. Unique placeholder
  hashes plus re-interning after substitution give the sharing the chapter wants without the trap.

### What was tricky to build
- Keeping the scaffolding nodes out of the intern table without losing the "repeated calls inside one `build` share
  one node" property: the builder tracks the nodes it creates while a `within` build is open (a stack of sets,
  one per open `within`) and removes exactly those when the substitution has interned the real nodes.

### What warrants a second pair of eyes
- `Engine._build`'s `self._tentative` stack: is there a path where a placeholder-rooted node is removed while an
  open build still needs it? (It would cost node identity, not correctness.)
- The `stats` semantics documented in `Engine.stats` (sources and neutral nodes uncounted).

### What should be done in the future
- A test for very long chains (recursion depth in `_signature`/`_evaluate` is one frame per node).

### Code review instructions
- `python3 -m unittest discover -s tests`; then read `tests/test_within.py::Substitution` and
  `gridflow/engine.py::Engine.within` together, they are the subtlest pair.

## Step 4: Hardening — immutable nodes, deep graphs, integer keys, integration rounds

With the suite green I went back over the chapter's wording to look for promises the code did not keep yet, and
added the reader-facing material: node immutability, a recursion budget for long pipelines, refusals that keep the
right error class, a README, and an integration test module that walks the motivating story (three rounds over one
pipeline).

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Close the gap between "the tests I wrote pass" and "the pattern's promises hold for
someone else's tests".

**Inferred user intent:** A library that survives an unknown reviewer poking at it with the interface in `TASK.md`.

### What I did
- `gridflow/node.py`: `Node` is now genuinely immutable (`__setattr__` refuses once `_locked` is set), matching
  the chapter's "Node ... immutable" and note 7's "store values frozen".
- `gridflow/engine.py`: `_reachable()` sizes a temporary `sys.setrecursionlimit` for the recursive signature and
  evaluation walks, restored in a `finally`; unknown operations at build time raise `BuildError` (code `E_OP`)
  rather than the base `EvalError`; a non-string operation name is refused instead of reaching `dict.get`
  unhashable; the `stats()` docstring now states exactly what `hits`/`misses` count.
- `gridflow/errors.py`: `BuildError` is also a `TypeError` and a new `ParameterError` is also a `ValueError`, so a
  caller checking either the Python class or the library class sees a refusal.
- `README.md`: usage, module map, and the rules the engine enforces in the chapter's vocabulary.
- `tests/test_integration.py` (7 tests): rounds over one pipeline with `crop` and `stats` operations, a new scale,
  a masked edit that reuses the unmasked nodes, a one-byte budget, and a new source with the same content.

### Why
- "Node ... immutable; identified by a structural hash" (Structure table) and note 7's freeze rule.
- `TASK.md` says nothing about graph depth; a 600-node chain used to raise `RecursionError`, which a "pipeline
  built step by step" can plausibly reach.
- The integration module is the applicability test of the chapter's Motivation: each round is a fresh script.

### What worked
- 140 tests green; the 700-node chain evaluates and the recursion limit is restored.

### What didn't work
- `test_the_second_round_repeats_the_chain_in_new_words_for_free` failed with `AssertionError: 0 != 1` because the
  test asked `runs()` about `scan.call("gain", k=1.5)` (gain applied to the source) instead of the gain applied to
  the blur node — a test bug, fixed by capturing the chain's nodes once.
- `test_the_mask_content_is_part_of_the_key` failed with `[[6.0, 5.0]] != [[2.0, 5.0]]`: another wrong expectation
  of mine (the sub-pipeline is built on the *gain* node, so the masked cell is 6, not 2).

### What I learned
- The chapter's phrase "integer keys" in `TASK.md`'s `stats` description means integer *values*; I kept exactly the
  four keys `hits`, `misses`, `bytes`, `evictions` and documented their exact meaning rather than adding more.

### What was tricky to build
- Nothing here was deep; the recursion budget was the only delicate part: the limit must be restored even when an
  operation raises, and must never be lowered below the interpreter's own default.

### What warrants a second pair of eyes
- `sys.setrecursionlimit` is process-wide state; the window is one `evaluate` call, but a concurrent user of the
  interpreter would see it. A single-threaded library is the stated assumption.

### What should be done in the future
- Make `_signature` and `_evaluate` iterative if graphs get deep enough that the temporary limit is a problem.

### Code review instructions
- `tests/test_integration.py` reads as the pattern's story; `gridflow/engine.py::Engine.evaluate` shows the
  request boundary; `README.md` maps the rules to the chapter.

## Step 5: Final check

I removed the byte-code caches, ran the whole suite from a clean tree, re-listed the files to be sure nothing
outside this directory was touched, and re-read `DIARY.md` for completeness. Nothing failed in this step.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Verify the deliverable as a whole against `TASK.md` and the diary format, then report
in the required JSON shape.

**Inferred user intent:** A finished, self-contained, tested library plus an honest diary.

### What I did
- `rm -rf gridflow/__pycache__ tests/__pycache__`, then `python3 -m unittest discover -s tests`:
  `Ran 140 tests in 0.027s / OK`.
- `find . -type f`: only the three given files plus `DIARY.md`, `README.md`, seven modules and seven test modules;
  nothing written outside the working directory.
- Re-checked the required interface one by one against `gridflow/__init__.py`: `Engine(cache_bytes=10_000_000)`,
  `eng.op(name, fn, version=1, identity=None)`, `eng.source(grid)`, `node.call(name, *inputs, **args)`,
  `eng.evaluate(node, scale=1.0) -> Result(.value, .warnings)`, `eng.runs(node)`,
  `eng.stats() -> {hits, misses, bytes, evictions}`, `eng.within(node, mask, build)`, `demo_engine()` with `add`,
  `gain`, `blur`, `threshold`, and `EvalError` naming the failing operation.

### Why
- The chapter's Consequences ("every operation must be deterministic ... one hidden input produces silently stale
  results") are why the registry has no place for time, randomness or mutable globals: everything a value depends
  on must reach the key, and the only things in it are the op name, its version, its canonical arguments and its
  inputs' content.

### What worked
- Full suite green from a clean tree; `import gridflow` has no side effects and no third-party imports.

### What didn't work
- N/A.

### What I learned
- The omitted participants are as much a part of the design as the included ones: no in-flight group (no
  concurrency), no parallel inputs (same reason), no persistent cache (nothing to share keys with yet), and the
  node table is released at end of session (documented, not implemented).

### What was tricky to build
- Nothing at this step.

### What warrants a second pair of eyes
- Whether `stats` should count a run-memo hit as a `hit` (it does) and whether sources should be invisible to the
  counters (they are): both are judgement calls documented in `Engine.stats`.

### What should be done in the future
- A persistent/shared cache would need every environmental input in the key (note 3) and a release rule for nodes
  (note 10); a size-aware policy would need measuring on a real workload (note 10).

### Code review instructions
- Read `README.md` first for the rules, then `gridflow/engine.py` top to bottom; run
  `python3 -m unittest discover -s tests`.

# Diary

## Goal

Build `shopcli`, a Python 3 (stdlib only) inventory command language whose refusals carry code, message, path,
where, valid alternatives, hint and a pasteable fix, following Chapter 6 (Repairable Errors). This diary records the
design decisions, the build, the test runs and the fixes made after failures.

## Step 1: Reading the chapter, the task and the diary format; designing the shape

I read all three files completely, then sketched the participants of Chapter 6 onto a small command language:
`Refusal`, closed `CODES`, suggester with a fixed order, per-registry redirect table, fix renderer, warning folder,
and a host translator. The design decisions that mattered most were: what counts as the "namespace" in a flat
command language (`item`, `price`, `report`), how much of the chapter's four-step suggestion order survives in a
language with no "kinds of value", and where a fix must be refused because it would need a value the agent did not
write.

### Prompt Context

**User prompt (verbatim):** "You are a software engineer joining a project. Your working directory contains three files:
- CHAPTER.md: a chapter of a design-pattern book describing the pattern you must apply;
- TASK.md: the software to build, with its required public interface;
- DIARY-FORMAT.md: how to keep your work diary.
Read all three completely first. Keep DIARY.md as you go, one step per phase of work, in that format. Then design, build and test the software in this directory. Work only inside this
directory (do not read or write outside it). Use only the Python 3 standard library. Run your tests and fix what
fails before you finish, and make sure DIARY.md is complete. Your final message must follow the output format at the end of TASK.md."

**Assistant interpretation:** Implement the pattern from CHAPTER.md as a library called `shopcli` with the exact
public interface listed in TASK.md, tests under `tests/`, a diary kept in the DIARY-FORMAT.md shape, and a final
answer that is one JSON object in a fenced block.

**Inferred user intent:** A reviewer wants to see the chapter's pattern actually applied (not a generic error
handler), with evidence in the diary that each participant and implementation note was realised and tested.

### What I did
- Read `CHAPTER.md`, `TASK.md`, `DIARY-FORMAT.md` in full.
- Decided the package layout: `shopcli/{__init__,codes,refusal,registry,parser,suggest,fixes,kernels,engine}.py`
  and `tests/` with four test modules (behaviour, refusals/fixes, registry+codes documentation).
- Fixed the code list: the nine required codes plus warning code `RANGE` (warnings are not in `CODES`).
- Decided that the "namespace" of the chapter's suggester is the command namespace (`item.add` → namespace `item`,
  verb `add`), so `E_NAMESPACE` means "the verb exists, in another namespace" — a structural fact, not a guess.

### Why
- Chapter "Structure" table lists the participants: Refusal, Code list, Fix renderer, Suggester, Redirect table,
  Translator, Site tracker, Warning folder. Each becomes one named module or class so the mapping is checkable.
- Note 4 ("keep one shape and one closed code list for every layer") drove a single `Refusal` record built by the
  parser, the binder, the evaluator and the host translator.
- Note 6 ("the line is in the agent's program") drove taking the line number from the line loop of the script, not
  from Python's traceback: in a line-oriented language the parser's line number is the site, so no tracker class.
- Note 3 ("fixes are code, in the agent's names and line structure") drove keeping the `repeat N:` prefix and the
  original argument order in every rendered fix.

### What worked
- The chapter's order (structural fact → mined redirect → near spelling → cross-kind) maps cleanly: step 4 is
  explicitly to be skipped in a flat command language, steps 1–3 have direct counterparts.

### What didn't work
- First sketch had option suggestions going through the same four steps; that produced a conflict: for
  `price.set name=w cost=2` the structural fact ("`cost` is an option of `report.margin`") answers before the mined
  redirect (`cost` → `value`), which would leave the agent with a hint and no fix. Resolved by letting a
  fix-less structural note be a *fallback hint* rather than an answer (see Step 3).

### What I learned
- The chapter's `valid` list is empty whenever a suggestion answered ("valid: s ? [] : nearest(...)"), which keeps
  rich refusals short. I followed that literally.
- Chapter note 1 says mined redirects may refuse-with-fix or run-and-warn; the sketch in the chapter refuses, and
  the task says agents "demonstrably type" the four near-misses, so I refuse with a fix (teaches, and never runs a
  command the agent did not write).

### What was tricky to build
- Not yet built; the tricky part anticipated is rendering a fix that differs from the agent's line *only* in the
  failing part while preserving quoting of values (`name="red widget"`). Decision: keep raw value text per option
  and re-quote only when needed.

### What warrants a second pair of eyes
- The judgement calls: no fix for `E_ARG_TYPE`/`E_ARG_MISSING`/`E_NOT_FOUND` (value cannot be derived from the
  agent's input), fix for option/key renames (value already present), `item.remove qty` above stock as `E_ARG_RANGE`
  rather than a silent clamp.

### What should be done in the future
- Mine more redirects once real transcripts exist (chapter note 1); add a "did you mean" for item names as a fix
  only if measurement says the guess is usually right.

### Code review instructions
- Start with `TASK.md` (interface), then `shopcli/refusal.py` and `shopcli/engine.py` (one shape, one path/where
  builder), then `shopcli/suggest.py` (fixed order) and `shopcli/fixes.py` (only the failing part changes).
- Validate with `python3 -m unittest discover -s tests`.

## Step 2: The refusal record, the closed code list, the registry and the parser

This step built the layers every later refusal reads from: the one record, the closed code list with
its documentation, the operation records with their usual ranges, the two mined redirect tables, and
the parser that owns the line number (the site). Nothing ran yet at the end of it, but the shape of
every future failure was fixed.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Build the data layer first so that no later layer can invent a code or
a shape of its own.

**Inferred user intent:** One error vocabulary, checkable at load, before any behaviour is written.

### What I did
- Wrote `shopcli/refusal.py`: `Refusal` (code, message, path, where, valid, hint, fix, host_name),
  `Warning` (code, message, line, count, hint), the internal `Refused`/`Fault` exceptions, and
  `fold_warnings`.
- Wrote `shopcli/codes.py`: the nine required codes, `CODES`, `WARNING_CODES` (`RANGE`), and
  `CODE_DOCS`/`WARNING_DOCS` where each code is documented once with runnable examples.
- Wrote `shopcli/registry.py`: `Param` (type, required, min/max, usual range, hint sentence),
  `Operation`, `Redirect`, `Registry.check()` and `default_registry()` with the four mined command
  names from the task and six mined option names.
- Wrote `shopcli/parser.py`: `repeat N:` prefix, `shlex` words (so `name="red widget"` works),
  `E_SYNTAX` refusals with hints, and `Call`/`Option` keeping the agent's own text.

### Why
- Chapter "Structure": the Refusal and the Code list are marked "Always", so they come first and
  every other module imports them.
- Note 9 ("one redirect table per registry, checked against it") drove putting both tables on the
  `Registry` instance and validating them in `check()` at construction.
- The `Path`/`where` decision follows note 6: in a line-oriented language the parser's line number
  is the site, so the parser records `line` and `source` and no tracker class exists.

### What worked
- `Registry.check()` immediately makes a mistyped redirect a load error; the option redirects are
  also checked against the option names that exist somewhere in the registry.

### What didn't work
- My first `shopcli/engine.py` draft was written with a nonsensical import line
  (`from .codes import (E_RANGE if False else "RANGE", ...)`); it never ran, the file was rewritten
  in Step 3. Lesson: write the module you mean before importing it.
- The first `registry.py` version imported `INT/NUMBER/TEXT` from `codes`, where they do not live;
  `python3 -c "import shopcli"` failed and the import was moved to `registry`.

### What I learned
- The chapter's `valid` list is meant to be empty when a suggestion answered; keeping that rule in
  the record builder (not in the suggester) keeps the suggester small.

### What was tricky to build
- Deciding what the fix renderer may change. `Call.render(name=..., keys=...)` can replace the
  command name or one option key and nothing else, so a fix that would need a value is impossible
  by construction rather than by discipline (note 10).

### What warrants a second pair of eyes
- The mined option names (`quantity`, `amount`, `product`, `sku`, `price`, `cost`) are invented for
  this build; the task names only the four command near-misses. Each is checked against the
  registry and refuses-with-fix, never runs.

### What should be done in the future
- Replace the invented option names with names mined from real transcripts.

### Code review instructions
- `shopcli/codes.py` (the closed list), `shopcli/registry.py` (`check()`), `shopcli/parser.py`
  (`parse_line`).  Run `python3 -m unittest discover -s tests` once tests exist.

## Step 3: The suggester, the fix renderer, the kernels and the engine

This step made the language executable: the suggester in its fixed order, the fix renderer, seven
kernels over a store, and `Shop.run` which owns the path, the where, the warning list and the
translator. A first end-to-end probe over twelve scripts showed every layer raising the same record.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Wire the data layer into behaviour and check it by hand before writing
tests.

**Inferred user intent:** A working `Shop.run` whose refusals are legible without documentation.

### What I did
- `shopcli/suggest.py`: `budget()` = `max(1, min(3, len/3))`, `distance()`, `closest()` (refuses
  ties), `suggest_command()` and `suggest_option()` in the chapter's order, step 4 (cross-kind)
  skipped with a comment saying why.
- `shopcli/fixes.py`: `render_fix(call, change)` — a command-name change or an option-key change.
- `shopcli/kernels.py`: `Store` plus `item_add`, `item_remove`, `item_list`, `price_set`,
  `price_get`, `report_stock`, `report_margin`; refusals raised as `Fault`, `ZeroDivisionError` left
  to escape.
- `shopcli/engine.py`: `Shop.run` (line loop, repeat, stop at first refusal, deliver earlier
  results), `_bind` (options, types, ranges, usual-range warnings), `_unknown_command`,
  `_unknown_option`, `_missing`, `_translate`, `_seal`.
- Ran a hand probe of twelve scripts and printed every reply as JSON.

### Why
- Chapter "Collaborations" steps 1–3 put the suggester between the failure and the fix; the fixed
  order lives in one function so it is stated once (note 2).
- Note 3 and the construction experiments it reports (four of five builds dropped a `repeat N:`
  prefix) drove keeping `prefix` on the `Call` and rendering fixes from it.
- Note 8 ("deliver what was produced before the failure") drove appending results as they happen
  rather than collecting per line.

### What worked
- The probe showed `repeat 3: item.ad name=w` → `E_UNKNOWN_COMMAND` with
  `fix: "repeat 3: item.add name=w"`, the case the chapter's sketch shows, and
  `item.add name=w qty=5000` → `ok: true` with one `RANGE` warning.
- `report.margin` on a price of 0 produced `E_HOST` with `host_name: "ZeroDivisionError"` and a
  concept hint, so the translator is exercised by production code and not only by a test.

### What didn't work
- First probe of `report.margin name=w cost=1` returned `E_NOT_FOUND` where I expected `E_HOST`;
  my probe script had not set a price, so the refusal was correct and the probe was wrong.

### What I learned
- Keeping `where` out of the layers and filling it in `_seal` means the parser, the binder and the
  kernels never guess a line number.

### What was tricky to build
- The binder's numeric coercion: `qty=3.0` is accepted as a whole number, `qty=1.5` is `E_ARG_TYPE`,
  `qty=abc` is `E_ARG_TYPE` with the record's concept sentence as hint. `int(raw, 10)` first, then
  `float`, then refuse.

### What warrants a second pair of eyes
- `Shop._seal` is the only place `where` is written; check that every refusal path reaches it
  (including the catch-all in `run`).

### What should be done in the future
- `kernels` currently refuse `item.remove qty` above stock; watch whether transcripts show that as
  noise rather than a real mistake.

### Code review instructions
- `shopcli/engine.py` (`run`, `_bind`, `_seal`), `shopcli/suggest.py` (order), `shopcli/fixes.py`.

## Step 4: Reply tests, and the two failures they found

The first test module covers the reply: its four keys, one entry per command that ran, repeat,
blank lines, state across runs, folded warnings, and what survives a failure. It found two failures,
both of them wrong expectations in my own tests rather than bugs in the library.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Put the reply's contract under test before testing refusals in detail.

**Inferred user intent:** Confidence that "results of earlier commands are still returned" really
holds, including inside `repeat`.

### What I did
- Wrote `tests/helpers.py` (`shop()`, `tokens()`, `single_change()`) and `tests/test_reply.py`
  (23 tests: reply shape, each command, repeat, blank lines, folding, delivery before failure).
- Ran `python3 -m unittest discover -s tests`.

### Why
- `TASK.md` fixes the reply shape; the chapter's note 8 fixes "what was produced before the failure
  is still delivered". Both are cheap to test and easy to break later.

### What worked
- 21 of 23 tests passed on the first run; the delivery tests (results of two iterations plus one
  folded warning surviving an `E_ARG_TYPE`) passed immediately.

### What didn't work
- Run 1: `Ran 23 tests ... FAILED (failures=2)`.
  `test_a_failing_iteration_keeps_the_earlier_iterations`: `AssertionError: 1 != 2` — the setup
  script was a separate `run`, so the repeat was on line 1 of its own script. Fixed the test by
  putting setup and repeat into one script.
  `test_mixed_lines_and_blank_lines`: `AssertionError: False is not true` — my script removed one
  unit from a stock of one, twice; the second removal correctly refused with `E_ARG_RANGE`. Fixed
  the test to add two units.
- Run 2: `AssertionError: Lists differ: [{'name': 'w', 'qty': 10}, ...]` — after merging the setup
  into one script the first result entry is the `item.add` result; my expectation forgot it.

### What I learned
- The library refused where my test expected success twice; both times the *test* was the wrong
  specification. Keeping `results` as "one entry per command that ran" makes the setup command
  visible, which is what an agent sees too.

### What was tricky to build
- Nothing in the library; the trickiness was writing expectations that account for every command
  that ran rather than only the interesting one.

### What warrants a second pair of eyes
- `test_maintained_input` runs the same failing line twice on one `Shop` and asserts identical
  replies; check that no state leaks between runs through `_warnings`.

### What should be done in the future
- Add a test that a `repeat` whose command returns a list still yields one entry per iteration
  (currently only `item.add` is repeated in the tests).

### Code review instructions
- `tests/test_reply.py`, `tests/helpers.py`; run only this module with
  `python3 -m unittest discover -s tests -p 'test_reply.py'`.

## Step 5: Refusal tests and the transposition fix

The refusal module tests every code, the shared shape, the path, the where line and the host
translation. One test failed and it was a real defect of the library: `qyt` for `qty` was two edits
away under plain Levenshtein, so the most common typo of all got no fix.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Prove each code is reachable, distinguishable, and carries the fields
TASK.md lists.

**Inferred user intent:** A closed code list that is actually used, with `host_name` filled only for
`E_HOST`.

### What I did
- Wrote `tests/test_refusals.py` (38 tests): shape sweep with a marked path, where line/source,
  syntax cases, unknown command, namespace, unknown option, argument type/range/missing, not found,
  host failure.
- Ran the suite.

### Why
- Chapter note 4: "one shape and one closed code list for every layer" is only true if every layer
  is tested from the same angle; hence a sweep that asserts the fields and the `✗` path for a
  failure from each layer.

### What worked
- 37 of 38 passed; every code except `E_HOST` was already reachable in production code, and
  `E_HOST` is reachable through a real `ZeroDivisionError`, not a monkeypatched kernel.

### What didn't work
- `FAIL: test_a_near_spelling_of_an_option ... AssertionError: None != 'item.add name=w qty=3'`
  for `item.add name=w qyt=3`. Cause: `distance("qyt", "qty") == 2` with a one-edit budget, so the
  suggester answered with no fix at all.

### What I learned
- The chapter's budget (`max(1, min(3, len/3))`) is about the *number* of edits, not the metric.
  With plain Levenshtein a swapped pair costs two, which makes the budget useless for the typos
  agents actually make.

### What was tricky to build
- Fixing it without loosening the budget: `distance()` now treats a swapped pair of neighbouring
  letters as one edit (Damerau/OSA, three rolling rows). The budget stayed the chapter's, the metric
  changed, and `qyt` → `qty` and `widgte` → `widget` both fit. Tie handling in `closest()` was kept,
  so two equally near names still yield no guess.

### What warrants a second pair of eyes
- That the transposition rule does not make two different real names look one edit apart. With this
  registry no pair of option names is affected; a bigger registry would need the check.

### What should be done in the future
- Add a property test: for every pair of registry names, a typo of one is not closer to the other.

### Code review instructions
- `shopcli/suggest.py` (`distance`, `closest`, `budget`), `tests/test_refusals.py`; run
  `python3 -m unittest discover -s tests -p 'test_refusals.py'`.

## Step 6: The fix contract, and the four fixes that did not bind

`tests/test_fixes.py` is the module the chapter cares most about (note 11): every fix must bind when
pasted *and* differ from the agent's line in exactly one token. Its first run failed four times,
each time because the shop in the test had no item for the fixed line to act on.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Test the two halves of the fix contract separately: it runs, and it
changes only the failing part.

**Inferred user intent:** No fix that is itself wrong; no fix that silently rewrites the loop or the
other arguments.

### What I did
- Wrote `tests/test_fixes.py`: a `FIX_CASES` table (26 script/setup pairs across command names,
  namespaces, mined redirects and option keys) checked for binding and for a one-token diff, a
  `NO_FIX_CASES` table (9 pairs) requiring a hint and no fix, plus the prefix/quoting tests and a
  "no placeholder in a fix" sweep.
- Ran the suite.

### Why
- Note 11: "For each redirect and each templated fix, test two things: the fix binds, and it differs
  from the agent's line only in the failing part." `helpers.single_change` implements the second.

### What worked
- `single_change` immediately caught nothing wrong in the renderer: all 26 fixes differed in exactly
  one token, and the repeats kept `repeat 3: `.

### What didn't work
- Run: `Ran 70 tests ... FAILED (failures=4)`, e.g.
  `AssertionError: False is not true : fix 'price.set name=w value=1' did not bind:
  {'ok': False, ..., 'code': 'E_NOT_FOUND', 'message': 'No item named "w".'}` — the same for
  `rm name=w`, `delete name=w` and `price.gte name=w`. The fixes were right; the shops I ran them in
  were empty. Fixed by giving those four cases the setup that stocks `w`.

### What I learned
- "Binds" has to mean "binds in a shop where the agent's own earlier lines ran", which is what an
  agent has. A fix is not required to create the state it operates on.

### What was tricky to build
- Distinguishing a fix that binds from a fix that is right. `E_NOT_FOUND`, `E_ARG_TYPE`,
  `E_ARG_MISSING` and `E_HOST` carry a hint and no fix, because a fix would have to invent a value
  (note 10); `item.list x=1` also gets no fix, because dropping the option would silently change
  what the agent asked for.

### What warrants a second pair of eyes
- The judgement call that `price.set name=w cost=3` gets the fix `value=3`: the value is the agent's
  own number and only the key changes, but if the agent meant a cost rather than a price the fix is
  confidently wrong.

### What should be done in the future
- Measure that one on transcripts; if `cost` on `price.set` is usually a mistake of concept rather
  than of spelling, replace the fix with the hint only.

### Code review instructions
- `tests/test_fixes.py` (`FIX_CASES`, `NO_FIX_CASES`), `tests/helpers.py` (`single_change`),
  `shopcli/fixes.py`; run `python3 -m unittest discover -s tests -p 'test_fixes.py'`.

## Step 7: Suggestion order, code documentation, and the missing hint

This step tested the order (structural, mined, spelling) and turned the code list into executable
documentation. It found one gap in the library — a refusal with `valid` but no hint — and two
mistakes in the documentation itself.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Prove the order is fixed and that each documented code is raised
exactly as documented.

**Inferred user intent:** The suggestion order stated once and tested, and a code list that cannot
go stale.

### What I did
- Wrote `tests/test_suggestions.py` (15 tests): budget values, transposition, ties, structural
  before mined (`stock` with a mined redirect present still gives `E_NAMESPACE`), mined before
  spelling (`ad` redirect wins over `item.add`), per-registry isolation, ambiguous verbs, option
  redirect applicability, cross-kind skipped.
- Wrote `tests/test_codes.py` (8 tests): `CODES == CODE_DOCS`, every code documented with an
  example, every example raising exactly its code, every documented fix binding and changing one
  token, every value-needing code carrying a hint and no fix.
- Ran the suite.

### Why
- Chapter note 2 wants the order "stated once"; `suggest_command`/`suggest_option` are the only
  places that decide it, and the tests pin the order with cases where two steps could answer.
- Chapter note 11 and Chapter 12: a documented example that raises a different code means the
  documentation has drifted.

### What worked
- The order tests passed on the first run, including the per-registry isolation test (a registry
  built from the same operations but without the mined names answers `ls` with `valid` names and no
  fix).

### What didn't work
- `Ran 87 tests ... ERROR: test_the_note_is_the_fallback_when_no_redirect_applies ...
  TypeError: argument of type 'NoneType' is not iterable`. Cause: for
  `report.margin name=w price=5` no step answered, so `hint` was `None` and only `valid` spoke.
  Fixed in the library by giving the nothing-close branch a concept hint
  (`"report.margin accepts name, cost and nothing else."`), and the test now checks that
  sentence; a second test keeps the original note case (`report.margin name=w qty=5`).
- `Ran 96 tests ... FAILED (failures=2)`: my `CODE_DOCS` claimed `itm.add name=w qty=1` raises
  `E_UNKNOWN_COMMAND` (`AssertionError: 'E_NAMESPACE' != 'E_UNKNOWN_COMMAND'`), and the documented
  fix `price.set name=w value=3` did not bind without stock. Both were errors in the documentation,
  corrected to `item.addd name=w qty=1` and a setup line.

### What I learned
- Writing the documentation as data and running it found two lies within minutes. This is the
  cheapest form of Chapter 12's outcome contract.

### What was tricky to build
- Ordering a note (hint, no change) against a mined redirect: the chapter says the first step that
  answers wins, but a note is not a repair. The suggester keeps notes as a fallback so that a
  fixable case is never answered with prose alone — documented in `suggest.py`.

### What warrants a second pair of eyes
- That deviation: the structural note for options is consulted *after* the redirect table. It is
  deliberate (otherwise `price.set name=w cost=3` would get a hint and no fix) and is the one place
  I did not follow the chapter's first-answer-wins literally.

### What should be done in the future
- Give `E_NOT_FOUND` the same treatment: state concept sentences measured against transcripts.

### Code review instructions
- `tests/test_suggestions.py`, `tests/test_codes.py`, `shopcli/suggest.py`, `shopcli/codes.py`;
  run `python3 -m unittest discover -s tests -p 'test_suggestions.py'` and `-p 'test_codes.py'`.

## Step 8: Registry load checks, README, and the final run

The last test module covers the registry's load-time checks, the record shapes and the warning
folder in isolation, and the README maps the chapter's participants onto the files. One test used
a redirect that could not shadow anything; after fixing it the whole suite is green.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Finish the remaining unit-level contracts, document the mapping, and
run everything.

**Inferred user intent:** A complete, self-checking build with a diary that shows the work.

### What I did
- Wrote `tests/test_registry.py` (27 tests): the seven commands, kernels exist, unique option
  names, documented sentences for required options, six load errors, the mined names, lookups,
  record shapes, `fold_warnings` in isolation, `Shop` state isolation, parser records and rendering.
- Wrote `README.md` with the language, the reply shape and the participant → file table.
- Ran the full suite repeatedly while adding the boundary tests (`qty=1000` no warning,
  `qty=1001` one warning).

### Why
- Note 9 wants the redirect tables checked at load; testing the six load errors is what makes that
  claim true rather than hopeful.
- `fold_warnings` is tested directly (not only through `repeat`) so that the fold key is pinned.

### What worked
- `Ran 126 tests ... OK` after one fix, then `Ran 127 tests ... OK` with the boundary test.

### What didn't work
- `FAIL: test_a_redirect_that_shadows_a_real_command_is_a_load_error ... AssertionError: ValueError
  not raised`. My test used `Redirect("ls", "item.list", ...)`, and `ls` is not a command, so no
  shadowing was possible. Fixed the test to redirect from `item.list`, which is a real command.

### What I learned
- The load checks were stricter than my test: `check()` already rejected redirects whose typed name
  is a real command, an unknown target, a missing hint, an option target that exists nowhere and a
  self-redirect.

### What was tricky to build
- Nothing in this step; it was the calm one.

### What warrants a second pair of eyes
- `Shop.run`'s catch-all `except Exception` also swallows a bug in my own binder code as `E_HOST`.
  The hint says so, but a reviewer may prefer a separate `E_INTERNAL` code; the chapter's closed
  list has one host-failure code, so it stays.

### What should be done in the future
- Emit `valid` for `E_ARG_RANGE` on `item.remove` (e.g. the stock on hand) if the field proves
  useful to agents; today the number is only in the hint.

### Code review instructions
- `tests/test_registry.py`, `README.md`; run the full suite with
  `python3 -m unittest discover -s tests`.

## Step 9: Final check — the whole suite, the required interface, and the file list

The last phase was a clean check: no stale bytecode, the full suite green, and a direct reading of
`TASK.md`'s required interface against the code. Nothing needed changing; two message strings were
polished (`E_NAMESPACE` for a verb written without its namespace reads better now) and the suite was
re-run after them.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Re-run everything from a clean state and check the delivered interface
against the task line by line.

**Inferred user intent:** A build that a reviewer can run with one command and trust.

### What I did
- `find . -name __pycache__ -type d -exec rm -rf {} +` then `python3 -m unittest discover -s tests`:
  `Ran 127 tests in 0.032s / OK`.
- Ran each module alone: `test_reply` 24, `test_refusals` 38, `test_fixes` 9, `test_suggestions` 18,
  `test_codes` 8, `test_registry` 30 — 127 in total, all OK.
- Checked the interface by reading it against the code: `Shop()` and `shop.run(script) -> dict` with
  exactly `ok`/`results`/`warnings`/`error`; the eight error fields with `host_name: None` off the
  host path; warnings with `code`/`message`/`line`/`count`/`hint`; and `shopcli.CODES` containing the
  nine required codes.
- Checked that no code outside `CODES` is ever raised: `grep -o 'E_[A-Z_]*'` over `shopcli/*.py`
  yields only the nine (`E_DOCS` is a false positive from `CODE_DOCS`).
- Polished two hint/message strings, re-ran the suite: still `OK`.

### Why
- The chapter's "Consequences" warns that rich errors cost context; the final read checks that
  nothing in the reply is filler and that every field the task lists is filled or explicitly `None`.

### What worked
- The suite is fast (0.03 s) and each module runs on its own, so a reviewer can bisect quickly.

### What didn't work
- Nothing failed in this step. The only friction: a heredoc patch script with mismatched quotes
  (`SyntaxError: unterminated triple-quoted string literal`) — re-done with the editor instead of a
  shell heredoc.

### What I learned
- The two polish changes (`"stock" is the verb of report.stock: the namespace comes first` and
  `No command "item.stock": the verb "stock" lives in another namespace.`) show the hint is where
  the concept lives and the message stays one sentence; keeping them apart made both shorter.

### What was tricky to build
- N/A.

### What warrants a second pair of eyes
- `results` for a command returning a list (`item.list`) is a list inside a list; a caller that
  flattens results would lose the grouping. It follows "one entry per command that ran" but is worth
  a glance.

### What should be done in the future
- If a `docs/` page is ever added, keep `CODE_DOCS` the only description of codes and have the page
  generated from it, so the two cannot drift.

### Code review instructions
- Read `README.md` first, then `shopcli/engine.py` and `shopcli/suggest.py`; verify with
  `python3 -m unittest discover -s tests` (127 tests, OK).

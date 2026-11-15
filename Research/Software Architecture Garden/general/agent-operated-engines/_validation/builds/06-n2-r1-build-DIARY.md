# Diary

## Goal

Build `shopcli`, a standard-library-only Python 3 inventory command language whose every failure is a structured,
repairable refusal (code, message, path, where, valid alternatives, hint, paste-ready fix), following the Repairable
Errors pattern in `CHAPTER.md`. This diary records each phase, the decisions, and every failure I hit.

## Step 1: Reading the chapter, the task and the diary format; design

I read `CHAPTER.md`, `TASK.md` and `DIARY-FORMAT.md` completely, then sketched the module layout and the mapping
between the pattern's participants and the code before writing a line of implementation. The key design decision
was to make the refusal a single record produced by one builder, with the suggester ordered exactly as the chapter
prescribes and the fix rendered by splicing spans in the agent's original source line.

### Prompt Context

**User prompt (verbatim):** "You are a software engineer joining a project. Your working directory contains three files:
- CHAPTER.md: a chapter of a design-pattern book describing the pattern you must apply;
- TASK.md: the software to build, with its required public interface;
- DIARY-FORMAT.md: how to keep your work diary.
Read all three completely first. Keep DIARY.md as you go, one step per phase of work, in that format. Then design, build and test the software in this directory. Work only inside this
directory (do not read or write outside it). Use only the Python 3 standard library. Run your tests and fix what
fails before you finish, and make sure DIARY.md is complete. Your final message must follow the output format at the end of TASK.md."

**Assistant interpretation:** Implement the pattern from `CHAPTER.md` in a small library called `shopcli` that
satisfies the interface in `TASK.md`, with tests under `tests/` runnable via `python3 -m unittest discover -s tests`,
and a diary kept in the exact shape of `DIARY-FORMAT.md`.

**Inferred user intent:** A reviewer wants to see whether the chapter's pattern is applied faithfully and
mechanically (participants, ordered suggester, no invented values in fixes, closed code list) in real, tested code.

### What I did
- Read all three files end to end (chapter 6 "Repairable Errors", the shopcli task, the diary format).
- Designed the package layout: `shopcli/{__init__,codes,refusal,registry,suggest,parsing,agenda}.py`-style modules,
  with `shop.py` holding the `Shop`, the command handlers, the translator and warning folding.
- Fixed the semantics of the seven commands, the store, `repeat N:` handling, warning rule (`RANGE` above qty 1000),
  and the code list (`E_SYNTAX`, `E_UNKNOWN_COMMAND`, `E_NAMESPACE`, `E_UNKNOWN_OPTION`, `E_ARG_TYPE`,
  `E_ARG_RANGE`, `E_ARG_MISSING`, `E_ARG_DUPLICATE`, `E_NOT_FOUND`, `E_HOST`).
- Decided the suggester order: (1) same verb in another namespace → `E_NAMESPACE`, (2) mined redirect table
  (`rm`, `delete`, `ls`, `inventory`), (3) near spelling inside the edit budget `max(1, min(3, len//3))` applied to
  the differing segment, (4) skipped — the chapter says a flat command language must skip the cross-kind step.
- Decided that a fix is rendered by splicing the failing token's source span, so a `repeat N:` prefix and untouched
  arguments survive verbatim, and that a fix is only emitted when it binds (command exists, keys known, values
  type-check).

### Why
- Chapter "Solution" and the `suggest`/`renderFix` sketch fix both the suggestion order and the refusal fields.
- Implementation note 1 (mine redirects, refuse with a fix) made `rm/delete/ls/inventory` refusals rather than
  silent aliases.
- Implementation notes 2, 3 and 10 decided the budget, the span-splicing fix renderer, and "hint and no fix,
  never an invented value".
- Implementation note 9 decided that the redirect table lives on the registry instance and is validated against it
  at load.

### What worked
- The chapter's sketch translated almost one-to-one onto the task's command table; the `repeat 3: item.ad name=w`
  example maps directly onto `E_UNKNOWN_COMMAND` with a fix that keeps the prefix.

### What didn't work
- Nothing run yet; this step was reading and design only.

### What I learned
- The chapter's `E_UNKNOWN_METHOD` has no counterpart in the task's required codes (`E_UNKNOWN_COMMAND` is the
  required code), so the sketch's `s?.code or E_UNKNOWN_METHOD` becomes `s?.code or E_UNKNOWN_COMMAND`.
- `E_NAMESPACE` needs a flat-language meaning: the chapter's example is a nested member (`img.mask.luminance`).
  I chose the structural analogue: a bare verb (`add`, `remove`, `list`, `set`, `get`, `stock`, `margin`) or a
  verb written under the wrong namespace (`price.list`) — both are facts about the registry, not guesses.

### What was tricky to build
- Nothing yet; the tricky parts are anticipated: span-preserving fixes and keeping `host_name` correct.

### What warrants a second pair of eyes
- Whether `E_NAMESPACE` for a wrong namespace (`price.list` → `item.list`) is a fair reading of the chapter, or
  whether it should be `E_UNKNOWN_COMMAND` with a near-spelling suggestion.

### What should be done in the future
- Build the modules, then tests, then re-read the chapter's implementation notes against the finished code.

### Code review instructions
- Start with `CHAPTER.md` "Solution" + `suggest` sketch, then `TASK.md`'s interface, then this diary's design
  decisions; nothing is implemented yet.

## Step 2: Building the package — refusal, codes, registry, suggester, parser, shop

I built the library bottom-up: the closed code list first, then the refusal/warning record, then the registry with
its per-instance redirect table, the ordered suggester, the span-preserving parser, and finally the shop with the
fix renderer, the host translator and the warning folder. Smoke-running it against the chapter's own example
immediately showed that my first binding check was stricter than the chapter's promise.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Write the package that implements the design from Step 1, then check it against the
chapter's examples before writing the test suite.

**Inferred user intent:** The code must produce exactly the refusals and fixes the pattern describes, not merely
"some" error.

### What I did
- Created `shopcli/codes.py` (CODES, CODE_DOCS, CODE_EXAMPLES, WARNING_CODES, WARNING_EXAMPLES),
  `shopcli/refusal.py` (Refusal, Warning, Suggestion, fold_warnings), `shopcli/registry.py` (Option, Command,
  Redirect, Registry with load-time validation), `shopcli/suggest.py` (levenshtein, edit budget, ordered suggester),
  `shopcli/parsing.py` (Token/Argument/ParsedLine with source spans, LineProblem), `shopcli/commands.py` (the seven
  handlers, REDIRECTS, build_registry) and `shopcli/shop.py` (Shop.run, binding, fix rendering, translator).
- Created `shopcli/__init__.py` re-exporting the public surface and `README.md` documenting commands and codes once.
- Ran `python3 - <<'EOF' ... shopcli.Shop().run(...)` over 20 scripts by hand (every code, every redirect, the repeat
  examples, warnings, the zero-price margin).

### Why
- The chapter's `Refusal` sketch (code, message, path, where, valid, hint, fix, hostName) became the dataclass; the
  `suggest`/`renderFix` sketch became `suggest.py` and `Shop.render_change`.
- Implementation note 9 (table per registry, checked at load) became `Registry.__init__` raising `ValueError` when a
  redirect targets a command the registry does not have.
- Implementation note 3 (rewrite only the failing part, keep the prefix) became splicing at a token span instead of
  re-rendering the line from parsed parts.
- Implementation note 10 (never invent a value) became `fix=None` for every type/missing/duplicate failure.

### What worked
- `repeat 3: item.add name=w qty=1`, all seven commands, quoted names with spaces, folding of
  `repeat 2: item.add name=w qty=2000` into one RANGE warning with `count=2`, and the four redirects all behaved.
- The E_HOST translation produced `host_name="ZeroDivisionError"` with a concept hint about the zero price.

### What didn't work
- `repeat 3: item.ad name=w` came back with `"fix": null`, although the chapter's sketch promises
  `fix: "repeat 3: item.add name=w"`. Cause: `Shop._binds` also required the *required* options to be present, so the
  candidate `repeat 3: item.add name=w` was rejected for missing `qty`.
- A first version of `suggest.py::_closest_command` had a redundant, unreadable `if` with an embedded negated
  conjunction; I rewrote it (bare verb charges no namespace distance; a real namespace must be within budget).
- `items.add` produced the ungrammatical hint `"'add' is not a items command"`.

### What I learned
- The chapter's sketch is a better specification than my instinct here: a fix repairs *one* thing. A line that
  still needs an argument will come back as `E_ARG_MISSING` with its own hint, which is the next repair step, not a
  reason to withhold the command fix.
- `E_NAMESPACE` needed a decision the chapter leaves to the reader in a flat language: a *bare* verb (`add`) and a
  *typo'd* namespace (`items.add`) are structural facts; a *real but different* namespace (`price.list`) is not, and
  rewriting it to `item.list` would be exactly the confident wrong fix the chapter warns about.

### What was tricky to build
- The fix renderer. Rendering `fix` by re-joining parsed pieces loses the agent's spacing and quoting; I instead
  record `Token.start/end`, `Argument.key_end` and `Argument.value_start` in the parser and splice the replacement
  into `parsed.source`. That is why `repeat 2:item.add` (no space after the colon) and `name="red widget"` survive
  a fix untouched.
- Keeping one shape across layers: parser failures are `LineProblem`, command failures `CommandFailure`, host
  failures raw Python exceptions; all three become `Refusal` in `Shop._refusal` so no caller sees two vocabularies.

### What warrants a second pair of eyes
- `E_ARG_RANGE` on `item.remove name=w qty=9` when only 5 are in stock offers `fix: "item.remove name=w qty=5"`.
  The value is read from the store, not invented, and it is the only quantity the shop can accept — but it is still
  a fix that changes the number the agent wrote.
- `price.list` is refused as `E_UNKNOWN_COMMAND` with `valid` names and no fix; a reviewer may prefer `E_NAMESPACE`.

### What should be done in the future
- Tests, then a review pass against every implementation note.

### Code review instructions
- Read `shopcli/shop.py::Shop.run` and `render_change`, `shopcli/suggest.py::suggest_command`, then
  `shopcli/registry.py::Registry.__init__`; run the hand-checked scripts from `README.md`.

## Step 3: Writing the test suite and running it for the first time

I wrote 139 tests across eight modules — commands, reply shape, one test per code plus the awkward cases, the
suggester's order, fix properties, warnings, the code catalogue (executable documentation), the registry and the
parser — and ran `python3 -m unittest discover -s tests`. Three failed, and two of the three were my tests being
wrong rather than the code.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Cover the required interface, every code and every pattern promise with tests, run
them, and fix what fails.

**Inferred user intent:** Honest evidence that the pattern's promises hold: codes raised, fixes binding, warnings
folded, suggestions ordered.

### What I did
- Created `tests/test_commands.py`, `tests/test_reply_shape.py`, `tests/test_error_codes.py`,
  `tests/test_suggestions.py`, `tests/test_fixes.py`, `tests/test_warnings.py`, `tests/test_catalogue.py`,
  `tests/test_registry.py`, `tests/test_parsing.py`.
- `tests/test_fixes.py` checks two properties per fix: it binds (the fixed line runs) and it changes exactly one
  token, with everything before and after that token identical (compared via token spans, not just string equality).
- Ran `python3 -m unittest discover -s tests`.

### Why
- The task's interface list became `test_reply_shape` (exact key sets, `path[-1]` starting with ✗, `where` line and
  source, `host_name` only for `E_HOST`, JSON-serialisable).
- Implementation note 11 ("test codes and fixes") became `test_catalogue` (every documented code raises exactly that
  code) and `test_fixes` (the fix binds and differs only in the failing part).
- Implementation note 2 (suggestion order) became `test_suggestions.OrderTest` with a small custom registry where a
  redirect and a near-spelling compete with a structural fact.

### What worked
- 136 of 139 tests passed on the first run, including the whole fix-property table and the folding tests.

### What didn't work
- `python3 -m unittest discover -s tests` reported three failures:
  `FAIL: test_text_where_an_integer_belongs ... AssertionError: 'whole number' not found in 'qty counts whole units,
  e.g. qty=3; pick the number yourself, rounding it would change what you asked for.'`,
  `FAIL: test_zero_price_margin_is_a_translated_host_failure ... AssertionError: 'ZeroDivisionError' not found in
  'report.margin failed inside Python: division by zero.'`, and
  `FAIL: test_verb_under_the_wrong_real_namespace ... AssertionError: 'E_UNKNOWN_COMMAND' != 'E_NAMESPACE'`.
- `tests/test_reply_shape.py` had a syntax error on first write — `python3 -m py_compile tests/test_reply_shape.py`
  printed `File "tests/test_reply_shape.py", line 130 ... SyntaxError: unmatched ')'` — because I had truncated one
  closing parenthesis while patching a line; fixed with `sed -i ''`. A second fenced-output mistake of mine (a
  stray `and False` assertion in `tests/test_suggestions.py`) was removed at the same time.

### What I learned
- The message of a host failure is the host's own message ("division by zero"); the class name belongs in
  `host_name` only — my test, not the code, was wrong (chapter's `translate`: `message: hostError.message`).
- I had written two contradictory expectations for `price.list` in two different test files, which forced the
  decision recorded in Step 2.

### What was tricky to build
- Asserting "only the failing part changed" without a tautology. Comparing common prefixes and suffixes proves
  nothing (any two strings share some); tokenising both lines and requiring exactly one differing token at the same
  position, with identical text before and after that token, does.

### What warrants a second pair of eyes
- `tests/test_fixes.py::test_each_fix_binds` prepares a fresh shop per case; a fix that depends on state built by
  the failing line itself (rather than the prelude) would slip through.

### What should be done in the future
- Fix the three failures and re-run.

### Code review instructions
- Run `python3 -m unittest discover -s tests`; read `tests/test_fixes.py` first for the fix contract, then
  `tests/test_suggestions.py` for the order.

## Step 4: Fixing the three failures and re-running

I fixed the one real defect (the `whole number` wording) and corrected the two wrong expectations, then re-ran the
suite until it was green. All 139 tests passed.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Make the failing tests pass without weakening the contract they check.

**Inferred user intent:** A green suite means the promises are actually met, not that the tests were loosened until
they agreed with the code.

### What I did
- `shopcli/shop.py::Shop._arg_type`: integer hint changed to "qty is a whole number of units, e.g. qty=3; pick the
  number yourself, rounding it would change what you asked for."
- `tests/test_error_codes.py::HostTest`: asserts `host_name == "ZeroDivisionError"` and `"division by zero" in
  message` (the host's own message), instead of expecting the class name inside the message.
- `tests/test_error_codes.py::NamespaceTest`: `price.list` now expects `E_UNKNOWN_COMMAND`, `fix is None` and
  `"item.list" in valid`, with a comment stating why (a real but unrelated namespace is not a typo).
- Re-ran `python3 -m unittest discover -s tests`.

### Why
- Chapter's `translate` sketch: `message: hostError.message`, `hostName: hostError.class`. The test had contradicted it.
- Chapter's "Suggestion against misdirection": a fix must be right, not merely close; `price.list` → `item.list`
  changes the concept.
- Chapter's warning about confident wrong fixes justifies the extra hint wording ("pick the number yourself").

### What worked
- `python3 -m unittest discover -s tests` → `Ran 139 tests in 0.019s` / `OK`.

### What didn't work
- Nothing failed after these three changes; the remaining work was hardening, not repair.

### What I learned
- Two of three failures were specification errors in my tests. It is worth writing the expected refusal in prose
  (code + hint meaning) before writing the assertion, so the chapter decides, not the implementation.

### What was tricky to build
- Nothing new; the fixes were one-line changes once the decision was made.

### What warrants a second pair of eyes
- `E_ARG_TYPE` for `qty=1.5` says "rounding it would change what you asked for" — true for money, arguable for
  units. A reviewer may want a shorter hint.

### What should be done in the future
- Harden the repeat grammar and prune unused imports, then do the final pass.

### Code review instructions
- Diff `shopcli/shop.py::_arg_type` and the two test methods; then run the suite.

## Step 5: Hardening — the repeat limit, the robustness sweep, and the remaining edge tests

A random-input sweep over `Shop.run` was meant to prove that no weird line escapes as a Python exception. It found
the opposite: a huge `repeat` count exhausted memory and the process was killed. I added a documented limit, then
re-ran the sweep until it was clean.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Before declaring the work done, try to break it with malformed input; every failure
must still be a refusal, never a crash.

**Inferred user intent:** A library that other code is tested against must be total: any string in, one reply out.

### What I did
- Ran a 40-script hand list plus 4000 random lines built from the language's own alphabet through `Shop.run`.
- `python3 - <<'EOF' ... Shop().run(...) ... EOF` was killed: `/bin/bash: line 37: 58215 Killed: 9  python3 -`
  (the line `repeat 999999999999999999999: item.list` tried to build ~1e21 results).
- Added `MAX_REPEAT = 10000` in `shopcli/parsing.py`, refused with `E_ARG_RANGE` (message names the limit, hint says
  to split the run, no fix because the right count is not derivable), exported it from the package, and documented
  it in `shopcli/codes.py` (`E_ARG_RANGE` doc) and `README.md`.
- Re-ran the sweep with 6000 random lines and the pathological scripts: `robustness sweep done, crashes: 0`.
- Added tests: repeat above the limit is refused (`tests/test_error_codes.py`), repeat at the limit runs 10000 times,
  `parse_line` refuses 10001 and accepts 10000 (`tests/test_parsing.py`), a structural fix is dropped when it would
  not bind (`add name=widget qti=1`), and option-key typos with a good and a bad value
  (`tests/test_suggestions.py`).
- Ran the module doctests through a new `tests/test_catalogue.py::DocstringTest`.

### Why
- Chapter "Errors against warnings": refusing is safe and blocks work; silently capping the count would change what
  the agent asked for. So the limit is a refusal, not a silent truncation.
- Chapter implementation note 10: the correct repeat count is not in the agent's input, so a hint and no fix.

### What worked
- The sweep now reports zero crashes over 6000 random lines, and every error path still ends with `✗ ...`.
- Doctests of all six modules pass (`TestResults(failed=0, attempted=3)` for `shopcli.shop`).

### What didn't work
- The first sweep was killed by the OS (`Killed: 9`, exit code 137) instead of producing a traceback, because the
  process ran out of memory; I had to run the pathological case in isolation to confirm the cause.
- `pytest`-style expected failures do not exist in `unittest`; I used `assertRaises` and explicit
  `except Exception` reporting in the throwaway sweep script instead.

### What I learned
- "Total function" is part of the pattern's promise, not an extra: if `run` can raise, the agent gets a Python
  traceback instead of a refusal, and the whole shape is lost.
- A limit that the reply explains is an API fact; a limit the code enforces silently is a bug.

### What was tricky to build
- Choosing the limit: the warning-fold test already uses `repeat 500`, and an agent may legitimately batch a few
  thousand commands, so 10000 keeps normal use and still bounds the reply. The value is a module constant
  (`shopcli.MAX_REPEAT`), so a host can see it.

### What warrants a second pair of eyes
- 10000 results per line is still a large reply; a reviewer may want the limit to apply to the whole script rather
  than to one line.

### What should be done in the future
- A whole-script budget, and possibly a `E_LIMIT` code of its own instead of reusing `E_ARG_RANGE`.

### Code review instructions
- `shopcli/parsing.py` (MAX_REPEAT and the repeat branch), `shopcli/codes.py` E_ARG_RANGE doc, `README.md`
  "The language", and `tests/test_error_codes.py::ArgumentRangeTest`.

## Step 6: Final check — clean run, review against the chapter's notes, diary completeness

I removed the generated `__pycache__` directories, ran the whole suite one last time, re-checked every implementation
note in the chapter against the code, and confirmed that the diary has one step per phase. Nothing needed repair in
this step; it is the closing verification.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Finish with a green test run, a complete diary, and an honest statement of what was
built and which parts of the pattern were applied.

**Inferred user intent:** Evidence, not claims: a runnable suite, no leftover failures, and a diary a reviewer can
follow from reading to final check.

### What I did
- `rm -rf shopcli/__pycache__ tests/__pycache__`.
- `python3 -m unittest discover -s tests` → `Ran 150 tests in 0.045s` / `OK`.
- `python3 -m py_compile shopcli/*.py tests/*.py` → `compile ok`.
- Doctests of all seven modules: `failed: 0` in each.
- Reviewed the chapter's participant table and implementation notes 1–11 against the code, and re-read `DIARY.md`
  for the required sections in each step.

### Why
- The task asks for run tests, fixed failures and a complete diary; this step is that check, and it is where the
  pattern mapping for the final report is confirmed: Refusal (`refusal.py`), code list (`codes.py`), fix renderer
  (`Shop.render_change`), suggester (`suggest.py`), redirect table (`registry.Redirect` + `commands.REDIRECTS`),
  translator (`Shop._translate` / `_host_hint`), site tracker (`parsing.py` spans and line numbers), warning folder
  (`refusal.fold_warnings`).

### What worked
- Suite green at 150 tests, doctests green, byte-compilation clean.
- Every required code is exercised by `CODE_EXAMPLES` and by at least one test that asserts the situation that
  causes it, so `E_ARG_DUPLICATE` and the repeat limit are not dead letters.

### What didn't work
- Nothing failed in this step. The earlier failures (steps 2–5) are recorded where they happened.

### What I learned
- The chapter's smallest form would have been enough (refusal, code list, fix renderer, spelling suggester); the
  translator, redirect table and warning folder each earned their place in this task: the zero-price margin, the
  four typed names, and the folded `repeat 500:` warning.
- Chapter 6 says `E_UNKNOWN_METHOD`; the task's closed list needs `E_UNKNOWN_COMMAND`. One code list, renamed, worked
  without changing the shape.

### What was tricky to build
- Nothing new in this step.

### What warrants a second pair of eyes
- `E_ARG_RANGE` carries three different repairs (negative qty, remove-more-than-stock, repeat limit); the code is one
  but the hints differ. A reviewer should check the hints still make each repairable without docs.

### What should be done in the future
- If real transcripts existed, mine option redirects (`count`/`amount` → `qty`, `item` → `name`) the way the chapter
  mines method redirects, and measure the RANGE warning before keeping it.

### Code review instructions
- Run `python3 -m unittest discover -s tests` (expect `Ran 150 tests ... OK`), then read `README.md` for the code
  list, then `shopcli/shop.py`, `shopcli/suggest.py`, `shopcli/parsing.py` in that order.

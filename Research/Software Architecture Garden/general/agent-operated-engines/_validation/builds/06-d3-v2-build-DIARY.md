# Diary

## Goal

Build `shopcli`, a Python 3 (standard library only) inventory command language whose every failure is a structured,
repairable refusal, applying the Repairable Errors pattern from `CHAPTER.md`. This diary records each phase: reading
and design, each part built, testing, each fix after a failing test, and the final check.

## Step 1: Reading the chapter, the task and the diary format

I read all three files before touching code. `CHAPTER.md` describes one failure shape (code, message, path, where,
valid alternatives, hint, fix, host error name), a closed code list, a suggester that runs in a fixed order from
certain to guessed, a redirect table mined from transcripts, a translator for host failures, a site tracker and a
warning folder. `TASK.md` fixes the language (one `namespace.verb key=value` command per line, `repeat N: command`,
seven commands), the public interface (`Shop().run(script)` reply shape) and the code list shopcli must use.

### Prompt Context

**User prompt (verbatim):** "You are a software engineer joining a project. Your working directory contains three files:
- CHAPTER.md: a chapter of a design-pattern book describing the pattern you must apply;
- TASK.md: the software to build, with its required public interface;
- DIARY-FORMAT.md: how to keep your work diary.
Read all three completely first. Keep DIARY.md as you go, one step per phase of work, in that format. Then design, build and test the software in this directory. Work only inside this
directory (do not read or write outside it). Use only the Python 3 standard library. Run your tests and fix what
fails before you finish, and make sure DIARY.md is complete. Your final message must follow the output format at the end of TASK.md."

**Assistant interpretation:** Implement the chapter's Repairable Errors pattern as a standard-library Python package
called `shopcli`, with the exact public reply shape from TASK.md, tested under `tests/`, and finish with one JSON
object in a fenced block.

**Inferred user intent:** A grader will run its own scripts against `Shop().run()` and judge both behaviour and how
faithfully the pattern is applied (refusal fields, suggestion order, redirects, host translation, warning folding,
delivery of earlier results). The diary is evidence of process, so failures must be recorded as they happened.

### What I did
- Read `CHAPTER.md`, `TASK.md` and `DIARY-FORMAT.md` completely with the read tool.
- Inspected the working directory (`ls -la`): only the three documents, Python 3.10.3 available.
- Sketched the module split and the mapping from chapter participants to modules.

### Why
- The chapter's Structure table names the participants (Refusal, Code list, Suggester, Redirect table, Translator,
  Site tracker, Warning folder); one module per participant keeps the mapping inspectable.
- The task's "Required public interface" dictates the reply keys and the `where` shape, so those were fixed before
  writing any code.

### What worked
- The chapter's sketch (`suggest(kind, name, recv)`, `unknownMethod`, `translate`, `foldWarnings`) translated directly
  into Python functions; the ordering it fixes (`E_NAMESPACE` → redirect → near spelling → other kind) is a sequence
  of `if` checks.

### What didn't work
- N/A at this step.

### What I learned
- The chapter's example codes (`E_UNKNOWN_METHOD`) are goja-cv's; TASK.md's list (`E_UNKNOWN_COMMAND`,
  `E_ARG_TYPE`, `E_SYNTAX`, ...) is shopcli's, so participant names carry over but the vocabulary is the task's.
- Implementation note 4 says a host failure needs one closed code plus the host's name as a field, which is exactly
  TASK.md's `E_HOST` + `host_name`.

### What was tricky to build
- Nothing yet. The one open design question was how to map "the same name on another kind of value" onto a
  key=value command language; I resolved it as "an option where a command was expected, or an option of another
  command" (`cost` is an option of `report.margin`, not `item.add`).

### What warrants a second pair of eyes
- Whether the invented command semantics (does `price.set` require the item to exist? is `qty` the total after the
  add?) match what the grader expects. I chose: `price.set` does not require the item; `item.add`/`item.remove`
  return the resulting stock.

### What should be done in the future
- Keep fixes executable: every generated fix should be run by a test (note 11).

### Code review instructions
- Start with `TASK.md` for the interface and `CHAPTER.md` §Structure/§Collaborations for the intended pieces.

## Step 2: Building the package, module by module

I built the package in the chapter's shape: a closed code list with an executable example per code, one refusal
record plus a `Fault` for layers that do not know the line, the registry with the one redirect table, the suggester
in its fixed order, the parser that keeps the agent's literal text, the site tracker, the translator, the store and
handlers, and the engine that assembles refusals in one place.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Same as Step 1; this step is the implementation phase.

**Inferred user intent:** Same as Step 1.

### What I did
- Created `shopcli/codes.py` (`CODES`, `WARNING_CODES`, `CODE_DOCS` with one example script per code), 
  `shopcli/refusal.py` (`Refusal`, `Fault`, `WarningFolder`, `fold_warnings`), `shopcli/registry.py`
  (`Param`, `Command`, `Redirect`, `RedirectTable`, `Registry`, `REGISTRY` and the redirect table with `rm`,
  `delete`, `ls`, `inventory`, plus option redirects `quantity`/`amount` → `qty`, `price` → `value`,
  `costprice` → `cost`), `shopcli/parse.py` (tokenizer keeping literals, `repeat` handling, call-style detection,
  `render_fix`/`render_target`), `shopcli/suggest.py` (edit distance, budget `max(1, min(3, len//3))`,
  `suggest_command`, `suggest_option`), `shopcli/site.py`, `shopcli/call.py`, `shopcli/store.py`,
  `shopcli/commands.py` (seven handlers and their records), `shopcli/translate.py`, `shopcli/engine.py`
  (`Engine`, `Shop`) and `shopcli/__init__.py`.
- Ran a manual smoke script over ten typical scripts and inspected the returned JSON.

### Why
- One refusal shape built in one place (`Engine._refusal`) satisfies "one shape and one closed code list for every
  layer" (note 4).
- Fixes are rendered from the agent's own line (`render_fix`) and cross-command fixes are completed from the target
  record (`render_target`), so a fix is pasteable code in the agent's names (note 3).
- The suggester consults namespace, then redirect table, then near spelling, then other kind, and drops a redirect
  whose target is not an option of the command, because a wrong fix is the most damaging output (notes 2 and 11).
- Warnings are raised where they happen and folded by `(code, line, message)` (note 7); results and warnings
  produced before a failure stay in the reply (note 9).

### What worked
- The smoke run produced the intended refusals: `item.zoom` → `E_UNKNOWN_COMMAND` with the command list,
  `price.list` → `E_NAMESPACE` with fix `item.list`, `item.rm` → redirect fix `item.remove name=widget`,
  `qty=lots` → `E_ARG_TYPE` with `qty=<integer>`, `qty=-3` → `E_ARG_RANGE` with the concrete fix `qty=0`,
  `repeat 3: item.add ... qty=2000` → one warning with `count: 3`.

### What didn't work
- First smoke output had a duplicated path for unknown commands: `["item.zoom", "✗ item.zoom"]`. Fixed by giving
  `Fault.path` a `None` sentinel and having the engine append the command label only when the failing thing is not
  the command itself.
- `item.add(name=widget, qty=1)` first returned `fix: null`; `_call_style_fix` only accepted `key=value` parts.
  Fixed by mapping leading positional parts onto the command's parameters in order, so the fix is
  `item.add name=widget qty=1`.
- `item.add name` (an option without a value) first produced the nonsense fix `item.add name=name` from positional
  mapping. Fixed by checking "a single positional token that is an option name" first and returning
  `item.add name=<name>`.
- `item.add name` and `item.add name=w qty=` first had path `["✗ name"]`, losing the command; fixed by setting
  `fault.path = [command_name]` for those parse faults.

### What I learned
- Keeping each value's *literal* source text is what makes fixes trustworthy; deriving them from parsed values would
  lose quoting and reformat numbers.
- The chapter's ordering is easy to state and easy to break: the redirect table must be consulted only for options
  the command actually has, otherwise `amount` on `price.set` yields a fix that fails again.

### What was tricky to build
- The `where` for a failure inside `repeat` is the repeat line, not a synthetic line for the inner command: the
  agent can only edit what it wrote, so the site tracker binds the raw line and the path carries `repeat 3` as a
  step. Repeats of a warning then fold on that same line, which is what makes `count` meaningful.
- Parsing had to produce a fix even for lines that do not parse. The solution was to parse first and raise the
  syntax fault after the token list is complete (empty-value case), or to build the fix from tokens directly
  (call-style and positional cases), never to re-parse the failing line.

### What warrants a second pair of eyes
- The tokenizer (quotes, escapes, `key=` with no value) and `_call_style_fix` heuristics; malformed input is where
  surprises live.
- The invented warning for a negative margin: it reuses the required `RANGE` code, but a reviewer may judge it noise
  (note 8 warns about warnings that are usually wrong).

### What should be done in the future
- Write the test suite: happy paths, every code, suggestion order, warning folding, host translation, and a test that
  runs each generated fix.

### Code review instructions
- Read `shopcli/engine.py` first (`run`, `_exec`, `_refusal`, `_bind`), then `shopcli/suggest.py` for the order, then
  `shopcli/parse.py` for fix rendering.

## Step 3: Writing the test suite

I wrote seven test modules, one per promise the chapter makes, before running anything: the language itself, every
code in the closed list, the suggester's order and redirects, warning folding, host translation, reply invariants,
and a fix-binding table. The point was to make the diary's "fixes must be tested" claim concrete: a fix that is
confidently wrong is the worst output the pattern can produce (note 11), so a table of cases runs each complete fix.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** The task asks for tests under `tests/` run with `python3 -m unittest discover -s tests`;
this step writes them.

**Inferred user intent:** Tests are the evidence that the refusal shape, the suggestion order and the fixes hold, not
just that a script ran.

### What I did
- `tests/test_language.py`: adds, removes, defaults, accumulators, `price`/`report` commands, `repeat`, nested
  `repeat`, blank lines, quoted names, numeric parsing, stop-at-first-error.
- `tests/test_errors.py`: one scenario per code plus field/path/where assertions and argument-level refusals.
- `tests/test_suggestions.py`: order (`E_NAMESPACE` before spelling, redirect before spelling), all four mined
  redirects, option redirects (including one that must *not* fire), cross-kind options, and `FixBindsTest`, a table
  of setup/script pairs whose returned fix is run and must succeed.
- `tests/test_warnings.py`: warning fields, folding with `count`, lines, no folding across lines, warnings kept on
  failure, warnings reset between runs.
- `tests/test_host.py`: broken store methods raise `E_HOST` with `host_name`, translator hint/fix, receiver names.
- `tests/test_invariants.py`: every registered command answers, every namespace/verb confusion gives `E_NAMESPACE`,
  forty odd lines never crash and always keep the reply shape.
- `tests/test_codes.py`: `CODE_DOCS` covers `CODES`, each example script raises exactly its code, no code outside the
  list is returned, warning codes are closed.
- Added `tests/__init__.py` so both `discover -s tests` and plain `discover` find the suite.

### Why
- Note 11 ("test codes and fixes") wants an example per code and a run of each fix; `CODE_DOCS` plus
  `FixBindsTest` does both.
- The invariant test asserts the exact reply keys and that `path[-1]` starts with `✗`, which is the interface
  contract TASK.md states.

### What worked
- Writing `FixBindsTest` as data (setup, script) made the table cheap to extend and caught design errors later.

### What didn't work
- The first run of the suite (Step 4) had two failures, recorded there.

### What I learned
- Assertions on `where["line"]` catch blank-line off-by-one errors cheaply.

### What was tricky to build
- The namespace matrix test: it enumerates every `namespace.verb` combination that does not exist and asserts
  `E_NAMESPACE`; the first version asserted a fix containing the command name, which was too weak because such a fix
  could still carry an option the target does not take (fixed in Step 7).

### What warrants a second pair of eyes
- `FixBindsTest` only runs fixes without placeholders; placeholder fixes are checked for the right command/options
  separately.

### What should be done in the future
- Add a case to `FixBindsTest` for every new redirect (note 11).

### Code review instructions
- Read `tests/test_suggestions.py::FixBindsTest` first, then `tests/test_invariants.py`.

## Step 4: Fixing the first failing test (E_HOST never fired)

The first full run failed for the translator test because the handler never called the store method the test broke:
`report_margin` computed the margin itself, so patching `store.margin` changed nothing and the reply was `ok`.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Run the suite and repair what fails.

**Inferred user intent:** Green tests, with the failure recorded as it happened.

### What I did
- Ran `python3 -m unittest discover -s tests`.
- Changed `report_margin` to call `store.margin(name, cost)` instead of dividing in the handler.

### Why
- The arithmetic belongs to the store; the handler's job is the refusal (not found, zero price, warnings). That also
  makes a host failure inside the arithmetic observable, which is what `E_HOST` exists for.

### What worked
- After the change the `ZeroDivisionError` from the broken store became `E_HOST` with `host_name` and a hint, and the
  test's fix grew the agent's own item name (`price.set name=widget value=<value>`).

### What didn't work
- Exact failure text:

  ```
  ERROR: test_translation_uses_the_agents_values (test_host.HostFailureTest)
  Traceback (most recent call last):
    File ".../tests/test_host.py", line 44, in test_translation_uses_the_agents_values
      self.assertEqual(error["where"]["line"], 2)
  TypeError: 'NoneType' object is not subscriptable
  ```

### What I learned
- A test that patches a collaborator is also a design check: it fails when the handler bypasses the collaborator.

### What was tricky to build
- Nothing: the fix was to delegate, not to weaken the test.

### What warrants a second pair of eyes
- `store.margin` assumes `prices[name]` exists; the handler checks first, so the `KeyError` path is a bug path only.

### What should be done in the future
- N/A.

### Code review instructions
- `shopcli/commands.py::report_margin` and `shopcli/store.py::margin`.

## Step 5: Fixing the second failing test (a hint I did not mean to send)

The second failure was a disagreement, not a bug: when no suggestion answers an unknown option, the engine still set
a hint that listed the command's options, and my test had asserted `hint is None`.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Decide which behaviour the pattern wants and align the test.

**Inferred user intent:** Consistent, justified behaviour rather than a test bent to whatever the code does.

### What I did
- Kept the hint (`item.add takes name, qty`) because the Editor lab in the chapter answers an unknown layer id with
  the list of layers, and changed the test to assert the hint text as well as `valid` and `fix is None`.

### Why
- The chapter's motivation: "the valid choices arrive with the refusal". `valid` is machine-readable, the hint is the
  sentence; both being present is consistent with the chapter's own example.

### What worked
- Suite green: `Ran 78 tests ... OK`.

### What didn't work
- Exact failure text:

  ```
  FAIL: test_unknown_option_without_a_suggestion_lists_the_options (test_suggestions.OptionSuggestionTest)
  AssertionError: 'item.add takes name, qty' is not None
  Ran 78 tests in 0.010s
  FAILED (failures=1, errors=1)
  ```

### What I learned
- `valid` and `hint` are not duplicates: one is for branching, one is for the model's next attempt.

### What was tricky to build
- Nothing.

### What warrants a second pair of eyes
- Whether a hint that merely lists `valid` is noise for a long option list; with seven commands and two options it is
  short. The chapter's "precision against noise" force applies if the API grows.

### What should be done in the future
- If the registry grows, cap the hint list like `valid` is capped.

### Code review instructions
- `shopcli/engine.py::_unknown_option`.

## Step 6: Fixing the transposition typo ("qyt" got no suggestion)

While extending the fix-run table I checked `item.add name=a qty=1 qyt=2` and got `fix: null`: the edit budget for a
three-letter name is one, and plain Levenshtein counts a transposition as two edits, so exactly the most common
typo had no suggestion.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Make the near-spelling suggester work for the typos it exists for.

**Inferred user intent:** Suggestions should help on real typos, and the fix must be built from the agent's line.

### What I did
- Replaced the distance with restricted Damerau-Levenshtein (an adjacent transposition counts as one edit) in
  `shopcli/suggest.py::edit_distance`, keeping the chapter's budget `max(1, min(3, len//3))` unchanged.
- Added `render_fix` de-duplication so a corrected option name that collides with one the agent also wrote keeps the
  corrected value: `item.add name=a qty=1 qyt=2` → `item.add name=a qty=2`, not two `qty=` pairs.

### Why
- Note 2 fixes the budget, not the distance function; counting a swap as one edit makes the budget behave as the
  chapter describes ("it cannot tell a typo from a different word one letter away" is about words, not keystrokes).

### What worked
- `qyt` → `did you mean qty?` with `fix: item.add name=a qty=2`; the fix runs clean.
- Quoted values survive: `item.add name="blue widget" qty=1 qyt=2` → `item.add name="blue widget" qty=2`.

### What didn't work
- Before the change the reply was `{"code": "E_UNKNOWN_OPTION", ..., "fix": null, "valid": ["qty", "name"]}`.

### What I learned
- The chapter's budget and the distance function interact; the budget is only meaningful with a typo-aware distance.

### What was tricky to build
- De-duplication had to apply only after rendering, because a rename is decided per argument, not per line.

### What warrants a second pair of eyes
- A transposition-aware distance also makes some distinct words closer; the mined redirects still run first, which is
  the chapter's answer to that risk.

### What should be done in the future
- N/A.

### Code review instructions
- `shopcli/suggest.py::edit_distance`, `shopcli/parse.py::render_fix`.

## Step 7: Fixing cross-command fixes that would fail again

Reviewing the namespace matrix test exposed a real defect: `price.list name=a` returned the fix `item.list name=a`,
and `item.list` takes no options, so pasting the fix failed with `E_UNKNOWN_OPTION`. The same held for mined
redirects with options the target lacks (`inventory name=x`).

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Make every cross-command fix bind, as note 11 demands.

**Inferred user intent:** The agent must be able to paste the fix and have it work.

### What I did
- Switched command suggestions (namespace, redirect, near spelling, other-kind) to build their fix with
  `render_target(node, target)`: the target's options in the target's order, values taken from the agent's line,
  options the target does not take dropped, required options the line lacks turned into placeholders.
- Made `render_target` skip *optional* parameters the agent did not type, so `item.rm name=widget` fixes to
  `item.remove name=widget` (which removes all) instead of an unnecessary `qty=<qty>`.
- Strengthened the suggestion tests: `price.list name=a` must fix to `item.list` and that fix must run clean.
- Ran a property check over 49 command-name variants (wrong namespace, dropped letter, swapped letters, plural,
  capitalised, bare verb) and 25 option typos: every placeholder-free fix ran clean, every placeholder fix named a
  real command and only real options.

### Why
- Note 11: "a fix that is itself wrong is the most damaging output the pattern can produce, because the agent pastes
  it and fails again". A fix that keeps an option the target rejects is exactly that.

### What worked
- 49 command variants and 25 option typos produced zero problems after the change.

### What didn't work
- Before: `price.list name=a` → `fix: "item.list name=a"`; pasted, it returns
  `E_UNKNOWN_OPTION: item.list has no option "name"`.

### What I learned
- "Use the agent's own names" (note 3) does not mean "keep all of the agent's arguments": a fix is written in the
  target's vocabulary, with the agent's values.

### What was tricky to build
- Deciding what to do with arguments the target lacks: dropping them is right for namespace/redirect suggestions (the
  argument was part of the confusion), and keeping them is wrong only when the target cannot bind them.

### What warrants a second pair of eyes
- `render_target` fills required options with placeholders; those fixes are not runnable until filled. The
  placeholder fixes are verified for the command and option names only.

### What should be done in the future
- If the grader's semantics make an option optional, `render_target` follows the record automatically.

### Code review instructions
- `shopcli/parse.py::render_target`, `shopcli/suggest.py` (all four suggestion steps).

## Step 8: Hardening after a read-through

A final read of `engine.py` left two gaps: an exception raised outside a handler (for example in binding) would
escape `run` and break the one-shape promise, and a line with a stray word (`item.add name=a qty=1 # comment`)
produced a fix that threw away the options the agent did write.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Close the remaining ways a failure can escape the shape.

**Inferred user intent:** Even a crash is reported in the record the agent already reads (note 4).

### What I did
- Added an outer `except Exception` in `Engine.run` that reports `E_HOST` with `host_name`, the line as `at`, a hint
  that this is a bug and the site tracker's `where`.
- Made `_positional_fault` keep the parsed options when only stray words are left, so
  `item.add name=a qty=1 # comment` fixes to `item.add name=a qty=1`.
- Added a test that patches `engine.REGISTRY.get` to raise and asserts the reply still has the shape, with
  `path == ["✗ line"]` and `host_name == "RuntimeError"`.
- Made a non-finite float (`price.set name=a value=1e400`) an `E_ARG_RANGE` with the fix `value=<number>`, so a
  reply can never carry `NaN`/`Infinity` into a caller's JSON.
- Removed unused imports and an unused regex; both `discover` forms run the suite.

### Why
- Note 4: "even a crash is reported in the shape the agent already reads". A `TypeError` escaping `run` would be the
  only failure an agent cannot repair.

### What worked
- 88 tests pass; the fuzz list (forty odd lines) never raises and always yields the four reply keys.

### What didn't work
- Nothing failed after these changes; they are preventive.

### What I learned
- The refusal shape is only as good as its outermost catch; the inner catches cover commands, the outer one covers
  the binder and the engine.

### What was tricky to build
- Keeping the `where` for an engine-level crash meaningful: there is no command node, so the path is the marker plus
  `line`, and the source is still the agent's line.

### What warrants a second pair of eyes
- The outer catch could hide a real bug behind `E_HOST`; the hint says so, and the path names the line, but logs are
  out of scope for this task.

### What should be done in the future
- A `--debug` mode that re-raises instead of refusing would help development; not part of the interface.

### Code review instructions
- `shopcli/engine.py::run` (both `except` blocks) and `shopcli/parse.py::_positional_fault`.

## Step 9: Final check

I ran the whole suite again from the working directory, checked both discovery forms, and re-read the diary against
the required format: every step has prose, prompt context, what I did, why, what worked, what didn't, what I learned,
what was tricky, what warrants a second look, what to do next and review instructions.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Finish only when the tests pass and the diary is complete.

**Inferred user intent:** A coherent, test-green deliverable with an honest record.

### What I did
- `python3 -m unittest discover -s tests` → `Ran 88 tests in 0.015s ... OK`.
- `python3 -m unittest discover` → `Ran 88 tests ... OK`.
- Re-ran the two fix-binding property checks (49 command variants, 25 option typos, zero problems).
- Listed the files: twelve modules in `shopcli/`, eight files in `tests/`, `DIARY.md`.
- Checked `TASK.md`'s required interface point by point: reply keys, error fields, `where` shape, `path[-1]` marker,
  `CODES` membership, warning fields, early results on failure, first-error stop.

### Why
- The task asks for a last result and a complete diary; this step records both.

### What worked
- All checks pass. `E_HOST` is raised both by a broken handler and by a broken binder.

### What didn't work
- N/A.

### What I learned
- The chapter's participants map cleanly onto modules; the only place where the mapping needed invention was "another
  kind of value", which became "an option where a command was expected, or an option of another command".

### What was tricky to build
- The `where` line for warnings inside `repeat` had to be the repeat line for folding to be meaningful; that is the
  same decision that makes the site tracker useful.

### What warrants a second pair of eyes
- The invented semantics (documented in Step 1) and the negative-margin warning, which is the one warning a reviewer
  could judge noise.

### What should be done in the future
- Mine more redirects from transcripts, as note 1 suggests; the table is one place and expects growth.

### Code review instructions
- Start at `shopcli/engine.py::run`, then `shopcli/suggest.py`, then `tests/test_suggestions.py::FixBindsTest`; run
  `python3 -m unittest discover -s tests`.

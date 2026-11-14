# Diary

## Goal

Build `shopcli`, a Python 3 (stdlib only) inventory command language for agents in which every failure (and every
warning) carries a repairable, structured refusal as described in `CHAPTER.md`. This diary records the design
phases, each part I built, the tests I ran, and every failure I fixed.

## Step 1: Reading the chapter, the task and the diary format; design

I read `CHAPTER.md` (Repairable Errors), `TASK.md` (shopcli) and `DIARY-FORMAT.md` completely before writing code, then
sketched the module layout and the refusal pipeline. The design maps each participant of the chapter onto one place in
the code, and fixes the order in which suggestions are produced (structural fact first, then mined redirect, then near
spelling, then the same name on another kind) so that the whole library speaks one vocabulary.

### Prompt Context

**User prompt (verbatim):** "You are a software engineer joining a project. Your working directory contains three
files:
- CHAPTER.md: a chapter of a design-pattern book describing the pattern you must apply;
- TASK.md: the software to build, with its required public interface;
- DIARY-FORMAT.md: how to keep your work diary.
Read all three completely first. Keep DIARY.md as you go, one step per phase of work, in that format. Then design,
build and test the software in this directory. Work only inside this
directory (do not read or write outside it). Use only the Python 3 standard library. Run your tests and fix what
fails before you finish, and make sure DIARY.md is complete. Your final message must follow the output format at the
end of TASK.md."

**Assistant interpretation:** Implement `shopcli` in this directory, keeping a phase-by-phase diary in the strict format,
using only the standard library, with tests under `tests/`, and finish with a single JSON object in a fenced block.

**Inferred user intent:** A working, tested library whose failures are self-repairing in the shape the chapter
prescribes, plus evidence (diary, tests) that the pattern — not just the feature list — was applied.

### What I did
- Read `CHAPTER.md`, `TASK.md`, `DIARY-FORMAT.md` in full.
- Planned the package layout:
  - `shopcli/codes.py` — the closed code list, each code documented once;
  - `shopcli/refusal.py` — `Refusal` and `Warning` value objects (one shape for every layer);
  - `shopcli/registry.py` — self-describing command records (namespace, verb, options with kinds, ranges, examples);
  - `shopcli/handlers.py` — the seven commands, which raise refusals through the context;
  - `shopcli/store.py` — the inventory state;
  - `shopcli/suggester.py` — redirect table, namespace/cross-kind/near-spelling suggester, edit distance;
  - `shopcli/translator.py` — host-exception → refusal translator;
  - `shopcli/fixes.py` — rebuilds a pasteable command line from the agent's own tokens;
  - `shopcli/language.py` — tokenizer, `repeat N:` parsing, the call site (line + source);
  - `shopcli/session.py` — `Shop`, site tracker, warning folder, execution.
- Wrote this diary step.

### Why
- Chapter "Structure" names the participants (Refusal, Code list, Suggester, Redirect table, Translator, Site tracker,
  Warning folder); giving each one a module keeps the vocabulary single-sourced (implementation note 4 and 10).
- "path", "where" and "host_name" must exist on *every* failure, so refusals are built through one factory
  (`Refusal.of`) that also guarantees the last path element starts with `✗` (note 5).
- Suggestion order is fixed in one function (note 2): occurrences in another namespace (`E_NAMESPACE`), mined
  redirects (`rm`, `delete`, `ls`, `inventory`), near spelling within `max(1, min(3, len//3))`, then the same name on
  another kind.

### What worked
- The command table in `TASK.md` maps cleanly onto registry records: one record per command with per-option kind,
  optionality, minimum and example value; the example value doubles as the material for a pasteable fix.

### What didn't work
- Nothing yet; no code has run.

### What I learned
- The chapter's JS-specific vocabulary (`E_UNKNOWN_METHOD`, `img.zoom`) has to be re-expressed for a CLI: the
  "kind" is the namespace (`item`, `price`, `report`), the "method" is the verb, and the agent's "program line" is a
  script line. `repeat N:` is the only place where one line runs a command many times, which is exactly where warning
  folding (note 7) must show up.
- The chapter says "the same name inside a namespace" for `E_NAMESPACE`; for a flat `ns.verb` grammar the faithful
  analogue is "this verb belongs to a different namespace" (`item.stock` → `report.stock`).

### What was tricky to build
- Deciding what `path` means for a line-oriented language: a script is a sequence, not a pipeline, so the chain is
  the enclosing `repeat` + iteration + the failing step. I chose `["repeat 3", "iteration 2", "✗ item.add …"]` and, for
  failures that happen inside a lookup (`report.margin` → price), the failing sub-step gets the `✗`
  (`["report.margin …", "✗ price.get(name=widget)"]`).
- `valid` for a missing argument: I list the missing option names there, because those are the alternatives the agent
  must now supply.

### What warrants a second pair of eyes
- The `E_HOST` path: `shopcli`'s own commands are deterministic, so host errors only arise from user-registered
  commands or corrupted state. A reviewer should check that `E_HOST` still produces the full refusal shape (host name
  kept as a separate field, per note 4).

### What should be done in the future
- Mine more redirects once real transcripts exist (note 1); this build only ships the four names `TASK.md` gives.

### Code review instructions
- Start at `shopcli/session.py` (`Shop.run` → `_execute`), then `shopcli/suggester.py` for the suggestion order, and
  `shopcli/handlers.py` for the per-command hints and fixes. Validate with
  `python3 -m unittest discover -s tests -v`.

## Step 2: Building the parts (codes, refusal, registry, store, fixes, suggester, translator, language, handlers, session)

I wrote the whole library in this step, module by module, in the order the refusal travels: the closed code list first,
then the one refusal shape, then the command records, the store, the fix builder, the suggester with its redirect
table, the translator, the parser (which owns the site), the handlers, and finally `Shop` which assembles the reply.
A first smoke run of a happy-path script and of `repeat 3:` already produced the expected `results`.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Build the library that Step 1 designed, keeping every failure in one shape.

**Inferred user intent:** Working code, not a sketch: the seven commands, the nine error codes and the RANGE warning,
all reaching the agent through `Shop.run`.

### What I did
- Created `shopcli/codes.py`, `refusal.py`, `registry.py`, `store.py`, `fixes.py`, `suggester.py`, `translator.py`,
  `language.py`, `handlers.py`, `session.py`, `__init__.py`, plus `README.md` documenting the reply shape, the code
  table and the suggestion order.
- Ran `python3 -c "from shopcli import Shop; ..."` on a happy-path script and on `repeat 3: item.add name=bolt qty=5`:
  both `ok: true`, with one result entry per executed command.
- Ran every bad script I could think of through `shop.run` and pasted the refusals into the review below.

### Why
- One module per chapter participant (Structure table) keeps one vocabulary: codes in `codes.py`, the record shape in
  `refusal.py`, suggestions in exactly one function in `suggester.py` (note 2), host failures in `translator.py`.
- `Refusal.of` marks the last path step with `✗`, so no builder can forget it (note 5).
- Fixes are rebuilt from the agent's own raw tokens (`fixes.rebuild`), so `item.add name=w qtty=2` becomes
  `item.add name=w qty=2` rather than a generic template (note 3).
- `E_HOST` keeps the closed code and puts the Python exception's own name in `host_name` (note 4).

### What worked
- The pattern paid off immediately on the four mined names: `ls` -> `item.list`, `rm`/`delete` -> `item.remove`,
  `inventory` -> `report.stock`, each with a hint that names the concept and a fix that is a whole line.
- `item.stock` -> `E_NAMESPACE` with `fix: report.stock` reproduces the chapter's `img.luminance -> img.mask.luminance`
  behaviour with a namespace instead of a sub-node.

### What didn't work
- A first draft of the registry record for `report.margin` contained a stray `name2` option (a typo while writing the
  command table), which would have made `report.margin` accept a phantom option. I removed it before running anything:
  the record is the only source of `valid`, `signature` and `template`, so a wrong record poisons every hint.

### What I learned
- An example value that is a *name* cannot be used to fill a missing option: `rm` alone must not become
  `item.remove name=widget`, because pasting it would mutate or fail on an item the agent never mentioned. Fixes now
  render `<name>` placeholders for missing text options and example values only for numbers.
- The chapter's `E_UNKNOWN_METHOD` for "same name on another kind" has no single analogue here: for a command the
  other kind is another namespace (that is `E_NAMESPACE`), and for an option it is another command's option, which
  I report under `E_UNKNOWN_OPTION` to stay on the required closed list.

### What was tricky to build
- Deciding what belongs in `path`. For a flat script the chain is short, so a plain failure has one step (the command),
  a failure inside `repeat` adds `repeat N` and `iteration K` in front, and a failure raised by a sub-lookup inside a
  command (`report.margin` asking for the price) puts the `✗` on the sub-step: `["report.margin name=w cost=4",
  "✗ price.get(name=w)"]`. That mirrors `open(scan.tif) → exposure → ✗ gaussian`.
- Keeping the warning folding honest: warnings are keyed by `(code, line, message)`, so `repeat 500: item.add
  name=w qty=5000` becomes one warning with `count: 500`, while the same command on two lines stays two warnings.

### What warrants a second pair of eyes
- `_coerce` decides between `E_ARG_TYPE` and `E_ARG_RANGE`: `qty=1.5` and `qty=nan` are type errors, `qty=-1` is a
  range error, and `qty=1e400` (which parses to `inf`) is rejected as a type error. A reviewer should confirm that
  split reads naturally to an agent.

### What should be done in the future
- Split `session.py` (roughly 400 lines) if more commands are added; the executor and the refusal builders could move
  to their own module.

### Code review instructions
- Read `shopcli/session.py::Shop._execute` next to `shopcli/suggester.py::Suggester.suggest_command`: the first decides
  *which* code is raised, the second decides the hint and the fix. Then run the smoke script from `README.md`.

## Step 3: First full test run — 77 tests, 6 failures

I wrote four test modules (`test_language.py`, `test_refusals.py`, `test_suggestions.py`, `test_warnings.py`,
`test_codes.py`) and ran the suite. Most of the surface held; six assertions failed and each one taught me something
about the pattern's edge cases rather than about Python.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Test every code, every refusal field, the suggestion order and the folding, then repair
what fails.

**Inferred user intent:** Evidence that the pattern holds under test, including that shipped fixes actually run.

### What I did
- Wrote the five test modules (78 test methods after the last addition).
- Ran `python3 -m unittest discover -s tests`.

### Why
- Chapter note 11 asks for two things a test can check: every code is raised by an example, and every fix, when run,
  binds. `tests/test_codes.py` does both, so a wrong fix fails the suite instead of the agent.

### What worked
- All refusal-shape assertions (keys, `✗` marker, `where`, `valid`, `hint`, `fix`, `host_name`), all warning
  assertions and the whole census of codes passed on the first run.

### What didn't work
- `python3 -m unittest discover -s tests` reported `FAILED (failures=6)`, including:

  ```
  FAIL: test_every_fix_is_a_runnable_line (test_codes.FixRunsTests) (script='rm name=widget')
  AssertionError: False is not true : fix 'item.remove name=widget' for 'rm name=widget' failed:
  {'code': 'E_NOT_FOUND', 'message': 'no item named "widget".', ...}
  ```
  ```
  FAIL: test_every_fix_is_a_runnable_line (test_codes.FixRunsTests) (script='item.add name')
  AssertionError: '<' unexpectedly found in 'item.add name=<name> qty=2' : 'item.add name' produced a placeholder fix
  'item.add name=<name> qty=2'
  ```
  ```
  FAIL: test_every_fix_is_a_runnable_line (test_codes.FixRunsTests) (script='item.add.extra name=w qty=1')
  AssertionError: unexpectedly None : 'item.add.extra name=w qty=1' has no fix
  ```
  ```
  FAIL: test_syntax_word_without_value (test_refusals.CodeTests)
  AssertionError: 'key=value' not found in 'item.add takes name (string), qty (whole number), e.g. item.add
  name=<name> qty=2'
  ```

### What I learned
- Two of the failures were *test* mistakes, not library mistakes: a fix may be the right line and still fail because
  the state it assumes is missing (`item.remove name=widget` with an empty shop). The fix must be right code, not
  necessarily a command that succeeds in a shop that never had `widget`; the test now sets the item up first.
- One failure was a real hole: a name with two dots produced `E_SYNTAX` with `fix: null`, although the valid command
  was right there in the string (`item.add` + `.extra`). That is exactly the kind of refusal the chapter calls
  useless: it says no without saying how.

### What was tricky to build
- The "every fix runs" test forced a policy decision: fixes may contain `<name>` placeholders only where the system
  cannot know a name. The test now runs every fix that has no placeholder and asserts that the placeholder ones name
  the missing option.

### What warrants a second pair of eyes
- The preconditions in `tests/test_codes.py::FIXABLE` encode what each fix assumes about the shop's state; a reviewer
  should check they are the natural preconditions and not fitted to the implementation.

### What should be done in the future
- Consider giving each `Suggestion` an expected precondition so the "fix binds" test can be generated instead of
  hand-listed.

### Code review instructions
- `tests/test_codes.py` is the executable documentation: `EXAMPLES` covers every code, `FIXABLE` covers the fixes.
  Run `python3 -m unittest discover -s tests -v` and look at the subTest names.

## Step 4: Repairing the six failures

I fixed the four distinct problems behind the six failures: the state assumptions in the fix test, the placeholder
policy (already implemented, but the E_SYNTAX hint did not say `key=value`), and a real gap — a name with too many
dots got no fix at all. After the edits the suite was green.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Fix what the failing tests exposed, not the tests' wording.

**Inferred user intent:** A suite that is green for the right reasons.

### What I did
- `shopcli/suggester.py`: added `suggest_split`, which cuts a too-dotted name back to a real command
  (`item.add.extra` -> `item.add`) and rebuilds the fix from the agent's tokens.
- `shopcli/session.py`: `_execute` now asks `suggest_split` first when the name has more than one dot; the E_SYNTAX
  hint for a word without `=` now ends with "every option is key=value".
- `tests/test_codes.py`: `rm name=widget`, `delete name=widget` and the cross-command option case now run a setup line
  that creates the item; `item.add name` moved to the placeholder test.
- `tests/test_refusals.py`: `test_syntax_two_dots` now asserts the fix `item.add name=a qty=1`.

### Why
- Chapter "Forces": a suggestion that is confidently wrong costs more than silence; but *no* suggestion when the
  answer is literally inside the typed string is the failure mode the pattern exists to remove.

### What worked
- `python3 -m unittest discover -s tests` -> `Ran 77 tests ... OK`.

### What didn't work
- Nothing in this step; the first attempt at the `_namespace_hint` rewrite (Step 5) failed to apply because the
  `oldText` did not match — a reminder that edits must quote the file exactly.

### What I learned
- Placeholders and runnable fixes are two different promises; the tests should state which one each fix keeps, and now
  they do.

### What was tricky to build
- `suggest_split` must prefer the longest prefix that is a real command, or `item.add.extra` would be cut to `item`
  (not a command) before reaching `item.add`. It walks the cut points from longest to shortest and stops at the first
  hit.

### What warrants a second pair of eyes
- `suggest_split` runs before `suggest_command` for dotted names with two dots; if a future command name legitimately
  contains a dot, the order would need revisiting.

### What should be done in the future
- N/A

### Code review instructions
- Look at `Suggester.suggest_split` and the two lines in `Shop._execute` that call it; then run
  `python3 -c "from shopcli import Shop; print(Shop().run('item.add.extra name=a qty=1')['error'])"`.

## Step 5: Hardening — a hostile-input sweep and a wrong namespace hint

Before calling the work done I swept the library with badly formed scripts, looking for two things the tests cannot
check by construction: an exception escaping `run` instead of becoming a refusal, and a hint that is confidently
wrong. The sweep found no escapes but one wrong hint, which I fixed.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Try to break the one guarantee that matters — that every failure, from any layer,
arrives in the same shape — and repair whatever breaks it.

**Inferred user intent:** A library whose error surface is uniform, not just its happy path.

### What I did
- Ran a 4000-script random sweep (`python3 - <<PY ... PY`) mixing unknown commands, bad options, `nan`, `1.5`,
  negative numbers, unquoted values with spaces, unterminated quotes, empty lines and malformed `repeat` directives.
  Result: `escaped: 0`, and the eight reachable codes plus the full error shape on every failure.
- Spot-checked failures inside `repeat`: `repeat 3: item.zzz` and `repeat 3: report.margin name=w cost=1`.
- Found and fixed the bad hint: `item.zzz` reported `"item" is not a namespace: the namespaces are item, price,
  report.` — `item` *is* a namespace. `Shop._namespace_hint` now checks the namespace in the registry first and
  answers `item has: add, remove, list; a command is namespace.verb.`
- Removed two unused helpers (`Registry.commands_in`, `Shop.clear`) so nothing in the package is unreachable.
- Let the redirect table answer case variants (`LS`, `item.RM`) as well as exact names, and dropped a dead
  `if self.registry.get(name) is None` guard in `Suggester.suggest_command`.
- Added `test_known_namespace_lists_its_verbs`.

### Why
- Chapter "Forces": "a nearest-name suggestion helps when it is right and costs more than silence when it is
  confidently wrong". A hint that contradicts the registry is the worst case, because the agent trusts it.
- Note 4: one shape for every layer is only true if nothing leaks; the sweep is the cheapest proof.

### What worked
- 4000 malformed scripts produced zero escaped exceptions and only closed-list codes.
- Folding survived the sweep: no warning was ever emitted with a code outside `WARNING_CODES`.

### What didn't work
- `python3 -c "from shopcli import Shop; print(Shop().run('item.zzz')['error']['hint'])"` printed
  `"item" is not a namespace: the namespaces are item, price, report. A command is namespace.verb, e.g. item.add
  name=widget qty=2.` — wrong, and it made the `valid` list contradict the `hint`.
- An `edit` call failed with `Could not find the exact text in shopcli/session.py` because my `oldText` had rewrapped
  lines; I re-read the file and re-applied with the exact text.

### What I learned
- The flat language hides a class of bug the chapter does not mention: because `namespace.verb` is split with
  `partition`, every "unknown" branch must ask the registry whether the *namespace* exists before saying it does not.
  Suggestions about kinds and namespaces are the easiest hints to get wrong.

### What was tricky to build
- Making the fallback hint distinguish three cases with one shape: a bare name (`add`), a known namespace with an
  unknown verb (`item.zzz`), and an unknown namespace (`foo.bar`); each needs different words but the same fields.

### What warrants a second pair of eyes
- `Suggester.suggest_command` now has four ordered steps plus case handling; a reviewer should check the precedence
  of `E_NAMESPACE` against the redirect table, since `item.rm` could arguably be either.

### What should be done in the future
- Turn the random sweep into a committed test (deterministic seed) so the invariant "nothing escapes" stays checked.

### Code review instructions
- `shopcli/session.py::_namespace_hint` and `shopcli/suggester.py::suggest_command`; verify with
  `python3 -c "from shopcli import Shop; [print(s, Shop().run(s)['error']['hint']) for s in ('add','item.zzz','foo.bar')]"`.

## Step 6: Final check

The last pass: run the suite the way `TASK.md` prescribes, confirm the public interface against the list in
`TASK.md`, and check every chapter participant is present in code. Everything is green and the interface matches.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Nothing new to build; verify and close out.

**Inferred user intent:** A finished deliverable with a complete diary and one JSON summary.

### What I did
- `python3 -m unittest discover -s tests` -> `Ran 78 tests in 0.058s` / `OK` (14 language, 28 refusal, 21 suggestion,
  7 warning, 8 code/fix tests).
- `python3 -m compileall -q shopcli` -> clean; the interpreter here is Python 3.10.3.
- Re-checked the required interface one field at a time: `Shop()`, `shop.run(script) -> {"ok", "results",
  "warnings", "error"}`, stop at the first error with earlier results kept, `error` with all eight keys, `path[-1]`
  starting with `✗`, `where` as `{"line", "source"}`, `shopcli.CODES` containing the nine required codes, warnings with
  `{"code", "message", "line", "count", "hint"}` and `code == "RANGE"`.
- Re-checked the chapter's participants against the modules and wrote the mapping into the final message.

### Why
- The task's own commands are the contract; running them verbatim is the only check that counts.

### What worked
- All 78 tests pass; the interface list from `TASK.md` is satisfied without any special-casing for the tests.
- The refusal for the chapter's motivating case now exists in this language's terms: `item.stock` answers with
  `hint: "'stock' lives in the report namespace, not item: write report.stock."` and `fix: "report.stock"`.

### What didn't work
- Nothing in the final pass.

### What I learned
- The parts of the pattern that are cheap and durable are the redirect table and the code list; the expensive part is
  the per-error hint, which is exactly what the chapter says drifts unless it is tested — `tests/test_codes.py` is the
  only thing keeping the 30-odd hints and fixes honest.

### What was tricky to build
- Keeping `valid` and `hint` from contradicting each other. Every refusal builder now derives `valid` from the same
  registry records the hint text is derived from (nearest-first, capped at eight).

### What warrants a second pair of eyes
- `handlers.py` decides the business rules (price required for `report.margin`, no over-removal, no orphan prices) and
  the codes those rules raise; a reviewer should confirm the code choice for each (E_ARG_RANGE vs E_NOT_FOUND).

### What should be done in the future
- Mine real transcripts for more redirects and measure the `RANGE` warnings on them (notes 1 and 8): the qty > 1000
  warning is defined by the task, the negative-margin warning is my addition and unmeasured.

### Code review instructions
- Run `python3 -m unittest discover -s tests -v`; then read `README.md`, `shopcli/session.py::Shop.run` and
  `shopcli/refusal.py::Refusal.of` in that order — the three files explain the whole contract.

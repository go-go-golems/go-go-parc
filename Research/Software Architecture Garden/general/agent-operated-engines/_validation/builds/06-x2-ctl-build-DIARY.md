# Diary

## Goal

Build `shopcli`, a standard-library-only Python 3 package whose `Shop().run(script)` executes a tiny
inventory command language and, when a line fails, returns an error document rich enough (`path`, `where`,
`valid`, `hint`, verified `fix`) that an agent can repair its script without a second round trip. This diary
records the design, the build, the tests and every failure I hit on the way.

## Step 1: Reading the brief and designing the package

I read `TASK.md` and `DIARY-FORMAT.md` completely, then designed the package before writing code. The task
leaves a few shapes open (what a `results` entry looks like, what `host_name` names, how `fix` should be
produced), so I wrote down a decision for each before building, and they drove the module split.

### Prompt Context

**User prompt (verbatim):** "You are a software engineer joining a project. Your working directory contains two files:
- TASK.md: the software to build, with its required public interface;
- DIARY-FORMAT.md: how to keep your work diary.
Read both completely first. Keep DIARY.md as you go, one step per phase of work, in that format. Then design, build and test the software in this directory. Work only inside this
directory (do not read or write outside it). Use only the Python 3 standard library. Run your tests and fix what
fails before you finish, and make sure DIARY.md is complete. Your final message must follow the output format at the end of TASK.md."

**Assistant interpretation:** Build the `shopcli` library described by `TASK.md` in this directory: a parser,
seven commands, aliases, structured self-repairing errors and warnings, plus a stdlib test suite that runs under
`python3 -m unittest discover -s tests`, and a diary in the exact `DIARY-FORMAT.md` shape.

**Inferred user intent:** A reviewer wants to see a working, tested implementation whose error documents are
genuinely self-repairing (not just descriptive), with the reasoning and the failures visible in the diary.

### What I did
- Read `TASK.md` (language, commands table, required error/warning keys, required codes) and `DIARY-FORMAT.md`.
- Inspected the directory (`ls -la`, `python3 --version`): only the two markdown files, Python 3.10.3.
- Decided the module layout: `shopcli/errors.py` (codes + `CommandError`), `shopcli/syntax.py` (tokenizer,
  scalar parsing, line/repeat parsing), `shopcli/suggest.py` (did-you-mean), `shopcli/store.py` (data),
  `shopcli/commands.py` (handlers), `shopcli/catalog.py` (command table), `shopcli/engine.py` (`Shop`),
  `shopcli/__init__.py` (public surface), `shopcli/__main__.py` (manual REPL over stdin).
- Decided the open shapes: one `results` entry per command *execution* shaped exactly like the TASK.md "Result"
  column (so `item.add` yields `{"name", "qty"}` and `item.list` yields a list); `warnings` aggregated per
  `(code, message, line)` with `count` = how many times it fired; `host_name` = the Python exception class name
  for `E_HOST` and the hosting command name otherwise; `path` = `["script", "line N", <repeat segments>,
  <command>, "✗ <offending text>"]`.

### Why
- The brief's core requirement is "every error must carry what the agent needs to fix its script without
  reading documentation"; that only works if messages/hints/valid/fix are produced from the same command
  table, hence `catalog.py` as the single source of truth and validation living next to it in `engine.py`.

### What worked
- The design settled quickly; the commands table maps one-to-one onto `Command.options` with kinds
  (`string`/`integer`/`number`), required flags and minimums, which covers every validation rule in TASK.md.

### What didn't work
- N/A in this step (no code written yet).

### What I learned
- TASK.md requires `E_ARG_RANGE` and a soft "usual range" warning for the same `qty` argument, so the two
  concepts must be kept apart: `< 0` is an error, `> 1000` is a `RANGE` warning that does not stop execution.

### What was tricky to build
- Nothing yet; the tricky part was choosing interpretations for `results`/`host_name`/`count`, which are
  recorded under "unclear" at the end.

### What warrants a second pair of eyes
- The interpretation of `results` entries (flat, table-shaped) versus wrapping each in `{"command", "result"}`.

### What should be done in the future
- Write the test suite covering the language, the error codes and the claim that every `fix` runs.

### Code review instructions
- Start with `shopcli/catalog.py` (the specification) and `shopcli/engine.py` (`Shop.run`), then the tests.

## Step 2: Building the library (errors, syntax, store, commands, catalog, engine)

I built the package bottom-up: the error vocabulary, the line grammar, the store, the handlers, the catalogue
and finally the engine that ties them together. The engine also owns the two features that make the errors
self-repairing: option-aware repair of structural mistakes, and verification of every generated `fix` against a
clone of the store.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Implement the designed package with the public interface from TASK.md.

**Inferred user intent:** A library that another test suite can import and drive (`shopcli.Shop`, `shopcli.CODES`)
that behaves correctly for both happy paths and every required error code.

### What I did
- `shopcli/errors.py`: `CODES`, `WARNING_CODES`, marker `✗`, `CommandError` with `prepend()` (for `repeat`
  segments), `at()` and `to_dict()` (builds `path`/`where`, guarantees the last path element starts with `✗`).
- `shopcli/syntax.py`: `split_tokens` (whitespace split that respects quotes, raises `E_SYNTAX` on an
  unbalanced quote), `parse_scalar` (`int` → `int`, finite `float` → `float`, else the raw text; quoted values
  stay strings), `unquote`, `split_pair`, `parse_line` (handles `repeat N: ...` with `E_SYNTAX` for a bad count,
  and returns a `ParsedCommand` that records stray/badkey/duplicate tokens as `Problem`s instead of raising),
  `last_wins` for duplicate-option repairs.
- `shopcli/suggest.py`: `did_you_mean` (difflib), `quote_value`, `join_names`.
- `shopcli/store.py`: `Store` with `items`/`prices`, `set_stock` (zero stock means "not stocked"), `clone()`.
- `shopcli/commands.py`: the seven handlers; `item.add` warns on `qty > 1000` or a resulting stock `> 1000`;
  `item.remove` defaults to "all", errors with `E_ARG_RANGE` when removing more than is in stock and proposes
  `qty=<current>`; `price.get`/`report.margin` raise `E_NOT_FOUND` when no price is set.
- `shopcli/catalog.py`: `Option`/`Command` dataclasses, the seven commands, `ALIASES`
  (`rm`/`delete` → `item.remove`, `ls` → `item.list`, `inventory` → `report.stock`), `NAMESPACES`,
  `REPEAT_USUAL_MAX = 100`, `commands_in`/`verbs_in`/`resolve_alias`.
- `shopcli/engine.py`: `_Warnings` (aggregation with `count`), `_Call` (handler facade: `fail`, `warn`, `at`,
  `replace`), `Shop.run` (line loop, stops at the first error, keeps earlier results and warnings, safety net
  that converts any escaped exception into `E_HOST`), `_run_text` (repeat handling with nested `repeat ×N`
  path segments), `_resolve` (exact name, alias, dotted namespace/verb, bare verb, fuzzy suggestions),
  `_check_syntax`/`_stray`/`_positional`/`_bad_key`/`_duplicate` (option-aware `E_SYNTAX` repairs, including
  `item.add apple 5` → `item.add name=apple qty=5` and `item.add name apple qty=1` → `item.add name=apple qty=1`),
  `_build_args`/`_coerce`/`_unknown_option`/`_missing` (`E_UNKNOWN_OPTION`, `E_ARG_TYPE`, `E_ARG_RANGE`,
  `E_ARG_MISSING`), `_host_error` (`E_HOST`, `host_name` = exception class, special hint for margin-by-zero)
  and `_finalize`/`_fix_runs` (every non-`None` `fix` is replayed against a cloned store; if it fails, `fix`
  becomes `None`).
- `shopcli/__init__.py` exports `Shop`, `CODES`, `WARNING_CODES`, `CommandError`, `ALIASES`, `COMMAND_NAMES`,
  `NAMESPACES`, `REPEAT_USUAL_MAX`, `MARK`. `shopcli/__main__.py` runs stdin as a script and prints JSON.
- Smoke-tested by hand with `python3 - <<'PY'` snippets printing `json.dumps(reply)` for ~30 scripts.

### Why
- `fix` verification is the strongest form of "the error repairs itself": a `None` fix means "no mechanical
  repair exists", and a non-`None` fix is guaranteed to run from the current store state, so the agent can paste
  it immediately. Verifying against a `Store.clone()` keeps the real inventory untouched.
- Structural problems are detected in the parser but reported in the engine, because only the engine knows the
  resolved command's real option names, and the hint/`fix` should use them (e.g. `item.list foo` says
  "takes no options" instead of a generic message).

### What worked
- The happy paths and all required codes produce sensible documents on the first smoke run; hand checks showed
  `item.add name=apple qtty=2` → `E_UNKNOWN_OPTION` with `fix: item.add name=apple qty=2`, `itm.add ...` →
  `E_NAMESPACE` with a working `fix`, `price.set value=0` + `report.margin` → `E_HOST` with
  `host_name: "ZeroDivisionError"`, and `repeat 200:` → a `RANGE` warning while still running 200 times.

### What didn't work
- First smoke run: `item.fly name=x` produced `hint: "did you mean 'item.list'?"` from a full-name fuzzy match
  (the `fix` was then correctly discarded because it would not run). Command:
  `python3 -c "import shopcli; print(shopcli.Shop().run('item.fly name=x')['error'])"`.
  Error text seen: `"hint": "did you mean 'item.list'? option: item.list name=x"`, `"fix": null`.
  Fix: dropped the full-name fallback from `_dotted_suggestion` — an unknown verb inside a known namespace is
  only suggested from that namespace's verbs/aliases.
- First smoke run: `item.add =x` produced the confusing message `'' is not a usable option name in '=x'`
  (empty key). Fix: moved bad-key detection into the engine (`_bad_key`) which distinguishes "missing option
  name before '='" from a genuinely unusable key name.
- A `python3 -` patch script silently failed to replace `_positional` (old text did not match the file), so
  `item.add apple` still returned `fix: null`. Detected with
  `python3 -c "import shopcli; print(shopcli.Shop().run('item.add apple')['error']['fix'])"` printing `None`.
  Fix: re-read the function with `sed -n '/def _positional/,/def _bad_key/p'` and replaced it with the `edit`
  tool using the exact current text.

### What I learned
- `difflib.get_close_matches` is eager: `"item.fly"` vs `"item.list"` scores ≈0.7, so fuzzy matching has to be
  applied per namespace with the verb only, not to whole dotted names.
- Warnings are easy to lose track of inside `repeat`; aggregating by `(code, message, line)` and incrementing
  `count` gives the natural `count: 3` for `repeat 3: item.add ... qty=2000`.

### What was tricky to build
- Ordering the checks so the *most useful* error wins: resolution (`E_NAMESPACE`/`E_UNKNOWN_COMMAND`) before
  structural (`E_SYNTAX`), structural before unknown options, options before types, types before ranges,
  ranges before missing arguments. Getting `item.add name apple qty=1` to yield `name=apple` (using the
  following bare token as the value, inserted at its original position) required recording token indices in
  `Problem` and rebuilding the pair list with `_pairs_with`.

### What warrants a second pair of eyes
- `_host_error` sets `valid: []`; every other code fills `valid`. TASK.md only says `valid` is a list.
- `host_name` is the exception class for `E_HOST` and the command name elsewhere — a deliberate, documented
  compromise between two readings of the field.
- The `repeat` count warning (`> 100`) is my own choice; TASK.md only defines the usual range for `qty`.
- Deleting the item row when stock reaches 0 (so `item.list` no longer shows it) is an interpretation.

### What should be done in the future
- Write the unittest suite (`tests/`) covering interface shape, every command, every code, warnings and the
  "every fix runs" property, then fix whatever fails.

### Code review instructions
- Read `shopcli/catalog.py`, then `Shop.run` → `_run_text` → `_run_command` → `_check_syntax`/`_build_args` →
  `_finalize`/`_fix_runs` in `shopcli/engine.py`. Validate with:
  `python3 -c "import shopcli; print(shopcli.Shop().run('item.add name=apple qty=abc')['error'])"` and
  `printf 'item.add name=apple qty=3\nreport.stock\n' | python3 -m shopcli`.

## Step 3: Writing the test suite and running it the first time

I wrote five test modules covering the public shape, the language, every required error code, warnings, and the
"every fix runs" property, then ran them. The first run had exactly one failure, caused by my own assertion
rather than the library.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Write tests under `tests/` that exercise the whole contract, run them with
`python3 -m unittest discover -s tests`, and fix whatever fails.

**Inferred user intent:** Evidence that the library behaves as TASK.md says, not just that it imports.

### What I did
- `tests/test_interface.py` (11 tests): `CODES` contents/format, reply keys, error keys, warning keys, empty and
  blank scripts, state persistence across `run` calls, `items`/`prices` views being copies, `TypeError` for a
  non-`str` script.
- `tests/test_language.py` (26 tests): new totals from `item.add`, zero-adds staying unstocked, partial and
  full `item.remove`, sorted `item.list`, `report.stock`, `price.set`/`price.get` type preservation,
  `report.margin` with and without stock, multiple lines in order, blank lines, `repeat` (3, 0, nested,
  case-insensitive spacing), quoted names, quoted numbers staying strings, `+4` and `2.0` parsing, case-insensitive
  command names, numeric names as text, and all four aliases (including aliases carrying the same arguments).
- `tests/test_errors.py` (35 tests): every code, with assertions on `code`, `path[-1]` starting with `✗`,
  `where.line`/`where.source` exactness, `valid`/`hint` presence, and the specific repair for each case.
- `tests/test_warnings.py` (9 tests): `qty > 1000`, resulting stock `> 1000`, in-range silence, warning does not
  stop the script, `count` aggregation through `repeat 3:`, warnings surviving a later error, two distinct
  warnings, `repeat 0`, and a huge `repeat`.
- `tests/test_repair.py` (10 tests): a 35-case battery asserting that any non-`None` `fix` actually runs, that at
  least two thirds of failures offer one, that verifying a fix leaves the store untouched, that every error
  document has all eight keys and a non-empty hint, and five "round trip" narratives.
- Ran `python3 -m py_compile tests/*.py` (compiled) and then
  `python3 -m unittest discover -s tests -v`.

### Why
- The `fix` property test is the cheapest way to keep the "self-repairing" promise honest: generating a plausible
  string is easy, generating one that runs is not.
- Codes are tested one per test so a reviewer can see the mapping from TASK.md's table to the implementation.

### What worked
- 88 of 89 tests passed on the first run, including the whole repair battery and all warning aggregation.

### What didn't work
- One failure:
  ```
  FAIL: test_text_where_a_number_is_needed (test_errors.TestArgumentTypes)
  ...
    self.assertTrue(any("qty=abc" == segment for segment in error["path"]))
  AssertionError: False is not true
  ```
  The assertion was wrong, not the library: the path segment is `"✗ qty=abc"` (the marker prefixes the offending
  text), so `==` could never match.

### What I learned
- Testing the error *documents* needs to assert on suffixes/prefixes (`endswith("qty=abc")`,
  `startswith("✗")`) because every marked path segment carries the `✗` marker.

### What was tricky to build
- Writing the fix-property test needed per-case setup scripts (`item.add name=apple qty=5` before
  `item.remove name=apple qty=50`) because several repairs are state dependent; the test replays the setup, runs
  the broken line, then runs the returned `fix` on the same shop, which mirrors what an agent would do next.

### What warrants a second pair of eyes
- The property test runs the `fix` on the *same* shop after the failure; that is correct because a failed line
  applies nothing, but it would break if a handler ever mutated state before raising.

### What should be done in the future
- Fix the failing assertion, re-run, and then fuzz the parser for crashes.

### Code review instructions
- `python3 -m unittest discover -s tests -v`; start with `tests/test_repair.py` (the promise) and
  `tests/test_errors.py` (the codes).

## Step 4: Fixing the failing assertion

A one-line test fix: compare with `endswith` instead of `==`, then re-run the suite.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Repair the failing test and confirm the suite is green.

**Inferred user intent:** A suite that runs clean, with any failure actually understood before being changed.

### What I did
- Edited `tests/test_errors.py`:
  `self.assertTrue(any("qty=abc" == segment for segment in error["path"]))` became
  `self.assertTrue(error["path"][-1].endswith("qty=abc"))`.
- Re-ran `python3 -m unittest discover -s tests` → `Ran 89 tests in 0.011s` / `OK`.

### Why
- The library was right; changing the library to satisfy a wrong assertion would have broken the `✗` marker
  requirement in TASK.md ("its last element starts with ✗").

### What worked
- Suite green in one edit.

### What didn't work
- The library had already passed the fuzz-free portion; no further failures appeared.

### What I learned
- Assertions about `path` must account for the marker prefix.

### What was tricky to build
- N/A (single assertion).

### What warrants a second pair of eyes
- Nothing beyond the marker convention.

### What should be done in the future
- Fuzz the engine to make sure no input escapes as an unhandled exception.

### Code review instructions
- `git diff` of `tests/test_errors.py`, then `python3 -m unittest discover -s tests`.

## Step 5: Fuzzing, polish and the final check

With the suite green I fuzzed 4000 random scripts built from command fragments to prove the engine never crashes
and always returns a well-formed reply, then tidied imports and re-ran everything.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Prove robustness beyond the hand-written cases and leave the tree clean and green.

**Inferred user intent:** Confidence that arbitrary agent input yields a structured, repairable error rather than
a traceback.

### What I did
- Ran an inline fuzz harness (`python3 - <<'PY'` with `random.seed(7)`, fragments like `item.add`, `name=`,
  `"`, `repeat 2:`, `qty=-1`, `#c`) over 4000 scripts: zero crashes, every reply had exactly
  `{ok, results, warnings, error}`, every error had exactly the eight keys, every `code` was in
  `shopcli.CODES`, every `path[-1]` started with `✗`, and every warning had exactly the five warning keys.
- Removed two unused typing imports from `shopcli/commands.py` (found with a small `ast` scan over
  `shopcli/*.py` and `tests/*.py`).
- Adjusted `valid` so each code lists what is genuinely acceptable there: option names for
  `E_UNKNOWN_OPTION`/`E_ARG_MISSING`, command names for `E_UNKNOWN_COMMAND`, namespaces for `E_NAMESPACE`,
  existing names for `E_NOT_FOUND`, and `<kind word> + concrete examples` for `E_ARG_TYPE`/`E_ARG_RANGE`.
- Re-ran `python3 -m unittest discover -s tests` → `Ran 89 tests in 0.012s` / `OK`, and
  `python3 -m shopcli` on a mixed script (repo demo: `item.add`, `price.set`, `repeat 2: item.add`,
  `report.stock`, `item.list`, `report.margin` → `{"items": 2, "units": 11}` and `margin: 0.6`).

### Why
- TASK.md's cost argument ("each failed attempt costs the agent a round trip") means an unhandled exception is
  as bad as a wrong answer, so the `E_HOST` safety net had to be demonstrated, not assumed.

### What worked
- The fuzz run produced zero problems, including for inputs such as `=x`, unbalanced quotes, `repeat :` and
  duplicate options.

### What didn't work
- Nothing failed in this step. Two smaller things were fixed before the fuzz: `item.fly` used to be answered with
  a misleading "did you mean item.list" (full-name fuzzy match), and `item.add =x` used to say
  `'' is not a usable option name`; both now produce option-aware messages.

### What I learned
- `python3 -m unittest discover -s tests` puts the working directory on `sys.path`, so `import shopcli` in the
  tests works without packaging.

### What was tricky to build
- Keeping the `fix` verification from recursing: `_fix_runs` builds a throwaway `Shop`, sets `_dry_run = True`
  and runs the candidate line there, so a failing candidate produces an error document whose own `fix` is *not*
  re-verified (depth is capped at one) and the real store is untouched.

### What warrants a second pair of eyes
- Interpretation calls that a reviewer may want to check against their own reading of TASK.md: `item.add` returns
  the new total; zero stock removes the row; `results` entries are the table's Result documents (not wrapped);
  `host_name` is the exception class for `E_HOST` and the command name otherwise; `E_HOST.valid` is `[]`.
- `price.set` accepts a name that is not stocked (prices and stock are independent), and `report.margin`
  therefore only needs a price.

### What should be done in the future
- If a consumer wants results correlated with lines, add an extra top-level key (e.g. `trace`) rather than
  changing `results`; and consider capping very large `repeat` counts.

### Code review instructions
- Run `python3 -m unittest discover -s tests` (89 tests, OK) and try a broken script through
  `python3 -m shopcli`; then read `Shop.run` → `_finalize`/`_fix_runs` in `shopcli/engine.py` to see the
  verification guarantee, and `shopcli/syntax.py` for the tokenizer.

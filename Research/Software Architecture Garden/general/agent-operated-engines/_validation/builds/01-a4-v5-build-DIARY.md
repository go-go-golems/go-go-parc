# Diary

## Goal

Build `hubreg`, the action registry of a home-automation hub, applying Chapter 1 (Self-Describing Operation
Registry): one record per device action, with the assistant's tool schemas, the app's controls, the hub's
argument checking, the refusals, help and the walk all reading those records. This diary records each phase,
including the failures and their exact error text.

## Step 1: Reading the chapter, the task and the diary format

I read `CHAPTER.md`, `TASK.md` and `DIARY-FORMAT.md` completely before writing anything. The chapter's structure
table maps almost one-to-one onto the task: Operation record → a dict with `name`, `on`, `args`, `fields`,
`samples`, `run`, `flags`, `redirects`; Argument spec → the arg dicts; Registry → `Registry`; Binder → `bind`;
Diagnoser → `Refusal`; Describer → `tool_schemas()`/`controls()`/`help()`; Walker → `walk()`.

### Prompt Context

**User prompt (verbatim):** "You are a software engineer joining a project. Your working directory contains three
files: - CHAPTER.md: a chapter of a design-pattern book describing the pattern you must apply; - TASK.md: the
software to build, with its required public interface; - DIARY-FORMAT.md: how to keep your work diary. Read all
three completely first. Keep DIARY.md as you go, one step per phase of work, in that format. Then design, build and
test the software in this directory. Work only inside this directory (do not read or write outside it). Use only
the Python 3 standard library. Run your tests and fix what fails before you finish, and make sure DIARY.md is
complete. Your final message must follow the output format at the end of TASK.md."

**Assistant interpretation:** Apply the chapter's pattern (not merely a passing resemblance) to a Python 3
standard-library library plus CLI for home-automation actions, with the exact public interface TASK.md lists, tests
under `tests/`, and a diary in the mandated format.

**Inferred user intent:** A small, correct, well-factored implementation whose structure visibly follows the
chapter — one record per action, all consumers reading it, registration refusing bad records, refusals that
repair — with evidence (tests, diary, final JSON) that it works.

### What I did
- Read the three files with `read`.
- Sketched the module split: `errors`, `argtypes`, `record`, `binding`, `diagnose`, `describe`, `walker`,
  `registry`, `demo`, `cli`, `__main__`.

### Why
- CHAPTER.md "Structure" and "Sketch" name the participants and their duties; keeping one module per participant
  keeps the consumers outside the core (implementation note 6) and makes the pattern mapping in the final message
  literal rather than rhetorical.
- The chapter's binder/diagnoser split matters: the binder produces a `Failure`, the diagnoser turns it into a
  `Refusal` with `valid`/`nearest`/`fix`. `TASK.md` only exposes the `Refusal`, so the `Failure` type can stay
  internal.

### What worked
- The chapter's pseudo-code translated directly: `bind` order (unknown keys first, then per-spec, then hook),
  `explain(failure, registry)`, `contextLine`/`help`, and the walker loop.

### What didn't work
- Nothing yet at this phase.

### What I learned
- Where the chapter and the task disagree, the task wins, and the gap is narrow: the task's record has `fields`
  as a flat list of names (the chapter's `fields(boundArgs)` is a function) and no `expand` (the chapter's
  composite operations), so this registry is implementation-only, one record per `(on, name)`.
- The chapter's `usual`/`usual_hint` pair is not in the task's ArgSpec list, but the task does require
  `RANGE` warnings, which only make sense with a usual range — so the spec accepts `usual`/`usual_hint` as the
  optional keys that produce those warnings.

### What was tricky to build
- Deciding how strict `register` should be. The chapter (note 1) says goja-cv checks structure but not defaults
  inside limits, and calls that a mistake. I therefore validate both, plus sample binding, and accept that some
  records a careless plug-in writes are refused.

### What warrants a second pair of eyes
- The task's record schema is the contract; anything I accept beyond it (`usual`, `usual_hint`, `validate`) is an
  extra. A reviewer should confirm the extras do not break a caller that only uses the documented keys.

### What should be done in the future
- If the hub grows composite actions (chapter note 10), add `expand` as the alternative to `run`.

### Code review instructions
- Start with `hubreg/record.py` (validation) and `hubreg/binding.py` (order of checks), then `hubreg/registry.py`
  for how the consumers hang off the store.

## Step 2: Records, argument types and registration

I built `hubreg/errors.py` (the three exception families plus the warning type and every code as a constant),
`hubreg/argtypes.py` (number, string, bool, enum as small objects with `accepts`/`json_schema`/`render`, and
`register_type` so a domain can add a type without touching the core), and `hubreg/record.py` (a `Spec`, a
`Record`, and `build_record`, which refuses malformed and inconsistent records).

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Implement the operation record and argument spec as validated data, not as
docstrings or annotations, so every consumer has one thing to read.

**Inferred user intent:** Registration is the first gate: a bad record must fail before any call, with a code the
caller can read.

### What I did
- Wrote `hubreg/errors.py`, `hubreg/argtypes.py`, `hubreg/record.py`.
- Structural checks: dict-ness, unknown keys, missing keys, callable `run`, `fields` unique names, flags types,
  duplicate argument names, required-after-optional, typed arguments, non-empty `doc`, non-empty `samples`.
- Semantic checks: default accepted by its type and inside the hard limits, `min <= max`, `usual` inside the
  limits and not reversed, `usual_hint` present exactly when there is a usual range, enum `values` non-empty and
  unique with a default among them, option redirects pointing at a declared argument and not at themselves.

### Why
- Chapter notes 1, 3 and 9: strictness is the point; a default outside the limits or a redirect to nowhere is a
  mistake that otherwise reaches agents silently.
- Note 6: types are pluggable objects with accept/describe duties, so the binder never learns about degrees,
  percentages or colour names.

### What worked
- `Spec.accepts`, `Spec.range_error` and `Spec.outside_usual` gave the binder a three-line inner loop, and the same
  predicates are what registration uses for defaults — one definition, two callers.

### What didn't work
- First run of the test suite hit `NameError: name 'E_BAD_SAMPLE' is not defined` in `record.py` (I had used the
  code without importing it), and the record/spec string checks picked their error code from a `where != key`
  heuristic, so an empty record `doc` was reported as `E_BAD_ARG` instead of `E_BAD_RECORD`. Fixed by importing the
  code and by passing the code to `_string` explicitly.

### What I learned
- The chapter warns that its own example does not check defaults and redirects; doing so costs little and caught
  two of my own test fixtures immediately.

### What was tricky to build
- `bool` is an `int` in Python. The number type must reject `True`/`False`, otherwise `quiet=true` passed to a
  numeric argument would bind as 1 — exactly the silent coercion chapter note 3 forbids.

### What warrants a second pair of eyes
- The rule "an argument takes a default **or** is optional, not both" is my reading of the chapter's `default?`
  and `optional` fields. It is a judgement call; it makes `optional` mean "may be absent, then None".

### What should be done in the future
- If a second consumer needs per-type rendering for a UI widget, add a `widget` duty to `ArgType` rather than a
  branch in `describe.py`.

### Code review instructions
- `hubreg/record.py::build_record` and `_build_spec`; run `python3 -m unittest tests.test_records`.

## Step 3: Binder, diagnoser, describer, walker, registry

I built the runtime half: `hubreg/binding.py` (`bind_record` → `Call` or `Failure`), `hubreg/diagnose.py`
(`explain` builds a `Refusal` from a failure and the registry), `hubreg/describe.py` (context line, help, controls,
tool schema, and the formatting helpers the other modules share), `hubreg/walker.py`, and `hubreg/registry.py`,
which stores records and is the only place that keeps a list of actions.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Keep every consumer a reader of the registry, and make the check order and the
refusal content come out of the same record fields.

**Inferred user intent:** Checking, help, refusals and tests cannot disagree, because there is nothing to disagree
about.

### What I did
- Binding order: lookup → unknown options → per-spec (supplied, default, optional, missing) → type → hard limits →
  usual-range warning (only when supplied) → cross-argument hook.
- Diagnoser per code: `E_UNKNOWN_ACTION` (valid names on that kind, nearest, action redirect), `E_UNKNOWN_OPTION`
  (valid option names, nearest, option redirect), `E_ARG_TYPE` (enum values and nearest value), `E_ARG_RANGE`
  (clamped fix), `E_ARG_MISSING` (valid alternatives and a `name=<type>` fix), plus `E_CONFIRM` with the same call
  confirmed as the fix.
- Describer: `context_line` (short form), `help_text` (full), `controls` (one dict per argument, exactly the keys
  TASK.md lists), `tool_schema` (JSON-serialisable, with unit, minimum/maximum, default, enum, usual range).
- Walker: help, tool schema and controls rendered for every record, redirects checked, then every sample bound and
  run with `confirmed=True`, and the result compared with the declared fields.
- Registry: `register`, `finalize` (cross-record redirect checks), `lookup`/`get`/`names`/`kinds`/`records`,
  `bind`, `run`, `tool_schemas`, `controls`, `help`, `walk`, `needs_confirmation`.

### Why
- Note 2: unknown keys before missing arguments, so `temp` gets "renamed: use target" rather than "target is
  missing"; defaults never warn; hard limits refuse and usual ranges warn.
- The chapter's Collaborations step 3: the diagnoser reads the same record as the binder, so the valid list is
  never a second list.
- `finalize` exists because an action redirect may point at an action another plug-in registers later (note 1:
  cross-record checks run once registration is complete, not record by record).

### What worked
- The demo registry walked clean on the first attempt after the tuple-key fix, and the CLI printed refusals that
  name the renamed option and the clamped value.

### What didn't work
- `python3 -c "import hubreg; reg = hubreg.demo_registry(); reg.names('thermostat')"` failed with
  `ValueError: too many values to unpack (expected 2)` — I had keyed `_records` by the string `"kind.name"` but
  unpacked keys as `(kind, name)`. Fixed by keying on the `(on, name)` tuple.
- A second bug of the same family: `register` tested `built.action in self._records`, which is always false for a
  tuple key, so nothing was ever refused as `E_DUPLICATE`. Fixed to test `(built.on, built.name)`.

### What I learned
- The chapter's `fields(boundArgs)` is more expressive than the task's flat list; I kept the flat list (task wins)
  and made `run` refuse a result whose keys are not exactly the declared fields, which is the check the walker
  would otherwise be the only place to make.
- A result mismatch is a plug-in bug, not a caller error, so it raises `ResultError`, not `Refusal`.

### What was tricky to build
- Making warnings travel with the call instead of a log (Collaborations 4): `Call.warnings` is a list of
  `BindingWarning(code, message, arg)`, and the CLI copies it into the reply it prints.

### What warrants a second pair of eyes
- `Registry.run` validates the result against `fields`; a lenient reading of the task would allow a plug-in to
  return extra keys. I chose strictness, and `walk()` reports the same mismatch as a problem.
- `needs_confirmation` accepts either the bare action name or `kind.name` in `confirm_required`, because TASK.md
  says "action names" without saying which form.

### What should be done in the future
- A `validate()` on the demo plug-ins' cross-argument rules would exercise the hook in production code, not only in
  tests.

### Code review instructions
- `hubreg/binding.py::bind_record` for the order, `hubreg/diagnose.py::explain` for the refusal content,
  `hubreg/registry.py::run` for confirmation and result checking.

## Step 4: First test suite (records and binding) and the fixes it forced

I wrote `tests/helpers.py` plus `tests/test_records.py` and `tests/test_bind.py` — 63 tests over registration
structure, argument specs, samples, redirects, defaults, unknown options, types, limits, usual-range warnings, the
cross-argument hook and the shape of a `Refusal`.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Test the two gates the pattern puts in front of every call: registration and binding.

**Inferred user intent:** Evidence that a bad record cannot be registered and a bad call cannot be bound, and that
every refusal carries a repair.

### What I did
- Ran `python3 -m unittest discover -s tests -t tests`.
- Added `sample_for()` to `tests/helpers.py`, which derives a sample that binds from the record's own argument
  specs, so a test that is about (say) an option redirect does not have to hand-write a valid sample.

### Why
- Note 5: put the sample arguments in the record so registration can require them; my test fixtures proved the rule
  works by failing without samples.

### What worked
- After the fixes the suite was green: `Ran 63 tests in 0.003s / OK`.

### What didn't work
- First run: `FAILED (failures=4, errors=15)`. Fifteen errors were all the same shape, e.g.
  `hubreg.errors.RecordError: device.ping: sample 0 {} does not bind: E_ARG_MISSING: device.ping requires 'target'
  (number); it is missing` — my fixtures registered records with required arguments and no samples. Fixed with
  `helpers.sample_for`.
- `AssertionError: 'E_BAD_ARG' != 'E_BAD_RECORD'` for an empty record doc (the `_string` heuristic above).
- `AssertionError: None != 'device.ping'` in `test_unknown_action`: a nearest name was found but no fix was offered,
  because `difflib` scores `pign` against `ping` at 0.75 and I had set the fix threshold at 0.8. Lowered the
  threshold to 0.7 with the score written down in a comment.
- `AssertionError: RecordError not raised` for two tests, both caused by the tuple-key dedupe bug in `register`.

### What I learned
- A registration gate changes how test fixtures are written: every fixture record now needs a sample, and the
  helpers should derive one rather than each test inventing one.

### What was tricky to build
- Balancing "redirect beats nearest" against "nearest is still useful". The chapter is explicit that a registered
  redirect wins and that both are shown when they differ, but it says nothing about a typo with no redirect. My
  rule: show the nearest name always, and offer it as the fix only when it is nearly the same word.

### What warrants a second pair of eyes
- The 0.7 similarity threshold is a heuristic; the chapter gives none.

### What should be done in the future
- Generate limit and redirect tests from the records themselves (a loop over `registry.records()`), which is
  possible because every limit lives in a spec.

### Code review instructions
- `tests/test_bind.py::RangeTest` for the "defaults never warn, supplied values do" rule; run
  `python3 -m unittest discover -s tests -t tests`.

## Step 5: The remaining tests (running, consumers, walk, demo, CLI) and the redirect fix they forced

I wrote `tests/test_run.py`, `tests/test_consumers.py`, `tests/test_walk.py`, `tests/test_demo.py` and
`tests/test_cli.py`, so the suite now covers every public entry point including the command line through
`subprocess`.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Every member of the required interface needs a test that would fail if the member
stopped reading the records.

**Inferred user intent:** Confidence that the assistant's schemas, the app's controls, the hub's validation, the
refusals, the help, the walk and the CLI all behave as TASK.md describes.

### What I did
- Added the five test modules; the suite went from 63 to 138 tests.
- Ran `python3 -m unittest discover -s tests -t tests` repeatedly and fixed what failed.

### Why
- TASK.md names the consumers explicitly; each one gets its own assertions rather than a single smoke test.
- Tests for `E_CONFIRM` cover both sources of the requirement (the host set and the record flag), because the
  chapter says the host decides and the record cannot lower it.

### What worked
- The CLI tests drive the real `python3 -m hubreg` entry point, so `describe`, `call`, the refusal exit code (1) and
  the usage exit code (2) are all checked end to end.
- `test_the_demo_registry_walks_clean` passed as soon as the registry keyed on tuples.

### What didn't work
- `python3 -m unittest discover -s tests -t tests` reported `FAILED (failures=8, errors=44)`; the shared cause was
  my own new check in `Registry.finalize`:

  `hubreg.errors.RecordError: thermostat.set_temperature: action redirect 'set_temp' points at the same action`

  I had refused a record whose redirect target equalled the record's own name — but that is precisely how a rename
  is written: the action that *was* called `set_temp` is now `set_temperature`, so the record for
  `set_temperature` carries `{"set_temp": "set_temperature"}`. The inconsistent case is a registered action that
  redirects *its own* name away, so the check now refuses `wrong == right` or `wrong == record.name`.
- `AssertionError: Lists differ: ['ping', 'ping'] != ['ping', 'pang']` — my walk test pointed two records at one
  closure that always appended `"ping"`.
- `AssertionError: Lists differ: ['pang', 'ping'] != ['ping', 'pang']` — `records()` is ordered by
  (device kind, action name), so the walk visits `pang` first. The test now states that order.
- `ModuleNotFoundError: No module named 'helpers'` when I ran `python3 -m unittest tests.test_walk`; the documented
  command (`discover -s tests`) puts `tests/` on the path, so the helpers import works there.

### What I learned
- A cross-record check must be written from the record's point of view: the record *is* the redirect target. The
  chapter says "rename with a redirect from the old name" without saying which record stores it; the natural home
  is the new record, and my first check assumed the opposite.

### What was tricky to build
- Testing a `Refusal` from the CLI without inventing output: the CLI prints `{"refusal": {...}}` and exits 1, the
  same shape the diagnoser builds, so the tests read the four fields the task requires (`code`, `message`, `valid`,
  `nearest`, `fix`) exactly as the library exposes them.

### What warrants a second pair of eyes
- `tests/test_cli.py` shells out to `sys.executable -m hubreg` from the project root; it will not work if the
  package is later installed without the tests running from the source tree.

### What should be done in the future
- Add a test that runs `describe` and `walk` against a deliberately broken registry to prove the CLI surfaces
  problems (currently the CLI always uses the demo registry).

### Code review instructions
- `tests/test_run.py::ConfirmTest`, `tests/test_consumers.py::ToolSchemaTest`, `tests/test_cli.py::CallTest`.

## Step 6: Agreement, pluggable types, and the consistency checks of the final review

The last phase was a review of the chapter against the code: I added `tests/test_argtypes.py` (a domain type
registered from outside the core) and `tests/test_agreement.py` (the consumers must agree, record by record), and
tightened three consistency rules in `record.py`.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Close the gaps the chapter's implementation notes name but the earlier steps had not
covered: pluggable argument types (note 6), "any other list of operations found outside the registry is a bug"
(Solution), and record consistency checks (note 1).

**Inferred user intent:** The pattern must be visible in the structure, not only in the behaviour.

### What I did
- `tests/test_argtypes.py`: registers a `colour` type with `accepts`/`json_schema`/`render` through
  `hubreg.register_type`, uses it in a record and checks binding, the tool schema (`pattern`), controls, help and
  the walk.
- `tests/test_agreement.py`: for every record, one tool description, one control per argument, bounds identical to
  the spec's, help naming the action, and a source scan proving the core and the consumers never name an action.
- Three new registration checks: hard limits and usual ranges belong to a `number` argument only, and an option
  redirect may not use a key that is already a declared argument.
- Suite: `Ran 154 tests in 0.491s / OK`.

### Why
- Note 6 asks for pluggability *before* the types multiply; the test proves a new type needs no change to the
  binder or to any consumer.
- The Solution's strongest claim is that there is no second list of operations; the source scan is a crude but
  direct check of it.
- A `usual` range on a string would silently never warn (`outside_usual` needs a number), which is exactly the
  silent-ignorance failure the chapter's Motivation describes.

### What worked
- All 154 tests pass with the command from TASK.md (`python3 -m unittest discover -s tests`), and the CLI demos
  behave: `describe` prints four tool descriptions, `call thermostat set_temperature target=30` prints a `RANGE`
  warning with the result, `call door lock_door` refuses with `E_CONFIRM` and a `confirmed=true` fix.

### What didn't work
- Nothing failed in this step; the three new checks were added with their tests in the same edit and the suite stayed
  green. (The only friction was the first version of the source scan in `test_agreement.py`, which used
  `getattr(hubreg, "__dict__", None) or __import__(...)` and could not work; it now imports the six core modules and
  scans them with `inspect.getsource`.)

### What I learned
- Making the demo records richer (an `enum` with `values`, a `usual` range with a hint, option redirects) was what
  made the consumer tests meaningful; a registry of four one-argument actions would have proved little.

### What was tricky to build
- Choosing how much to refuse at registration. The chapter wants defaults inside limits and redirects that exist;
  it does not say whether limits on a string argument are refused. I refuse them, and the diary records that as a
  judgement.

### What warrants a second pair of eyes
- The source scan in `test_agreement.py` would produce a false alarm if a consumer's docstring happened to quote an
  action name in single quotes.
- `Registry` accepts the optional keys `usual`, `usual_hint` and `validate` beyond the record schema in TASK.md;
  a reviewer should confirm that is welcome and not a contract drift.

### What should be done in the future
- Generate the limit and redirect tests from the records (a loop over `records()` plus each spec's `min`/`max`),
  which note 5 recommends and which this project does only by hand.

### Code review instructions
- `tests/test_agreement.py`, `tests/test_argtypes.py`, and `hubreg/record.py` (the checks near `low`/`high`/`usual`
  and the redirect loop) — then run `python3 -m unittest discover -s tests` and
  `python3 -m hubreg call thermostat set_temperature target=30`.

## Step 7: Polish of the messages, one-sided limits, and the final run

A last pass over the wording: the range refusal and the help used to print `-inf`/`inf` for an argument with only
one limit, which reads like a leak of the implementation. `describe.limits_phrase` now says "at least 3" or "at most
3", and both the help and the `E_ARG_RANGE` refusal use it. I also pinned two behaviours with tests that were
previously only implied: a `None` default is refused (it is not a value of any type), and a hook may return a plain
string, which becomes a refusal with code `E_HOOK`.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Make the generated text worth reading for an agent, and make sure every behaviour the
code has is one a test asserts.

**Inferred user intent:** No rough edges in what the assistant and the app actually see.

### What I did
- Added `limits_phrase` to `hubreg/describe.py` and used it in `help_text` and in `diagnose._arg_range`.
- Removed the now-unused import of `limited` from `hubreg/diagnose.py`.
- Added three range tests and two hook/default tests.
- Final run: `python3 -m unittest discover -s tests` → `Ran 159 tests in 0.552s / OK`; `python3 -m hubreg walk`
  prints `{"problems": []}`; `python3 -m hubreg describe` prints four tool descriptions; removed the
  `__pycache__` directories the runs created.

### Why
- Note 2 separates hard limits from usual ranges "both in the declared unit"; the rendered message should show the
  limits that exist and nothing invented.
- The chapter's `validate` hook is part of the record ("a hook for rules that span arguments"), so both of its
  documented shapes (dict and string) need a test.

### What worked
- The refusals now read `argument 'level' of device.ping is 1, outside the hard limits at least 3; fix: level=3`.

### What didn't work
- Nothing failed in this step.

### What I learned
- The chapter says nothing about hooks' return shape; I support "None means ok, a dict means a coded failure, a
  string means a message", which keeps a plug-in from needing to import the refusal types.

### What was tricky to build
- Keeping the message helpers in one module: the binder builds the `RANGE` warning, the diagnoser builds refusals
  and the describer builds help, and all three need the same unit and limit rendering, so those helpers live in
  `describe.py` and the other two import them.

### What warrants a second pair of eyes
- `SamplesTest`-level strictness means a plug-in author who passes `"default": None` gets a refusal; a reviewer may
  prefer to treat it as "optional".

### What should be done in the future
- N/A

### Code review instructions
- `hubreg/describe.py::limits_phrase`, `hubreg/diagnose.py::_arg_range`, then
  `python3 -m unittest discover -s tests`.

## Step 8: The TASK.md contract as a test, and the closing check

I added `tests/test_interface.py`, which asserts the contract in TASK.md member by member: the exports, the
`Registry` and `run` signatures, `Call`'s four attributes, the warning shape, `Refusal`'s five attributes,
`RecordError.code`, and `walk()` returning dicts with `action` and `problem`. The point is that a later change to the
package cannot quietly drop an attribute one of the three consumers depends on.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** "Other code will be tested against it" means the interface itself deserves a test, not
only its behaviour.

**Inferred user intent:** The library is safe to build on: the names and shapes TASK.md promises are the names and
shapes it has.

### What I did
- Wrote `tests/test_interface.py` (10 tests) and ran the suite: `Ran 169 tests in 0.456s / OK`.
- Removed the `__pycache__` directories, re-ran the CLI (`call light dim level=80`, `help scene run_scene`,
  `describe`, `walk`) and confirmed the outputs above.
- Checked the diary: seven earlier steps plus this one, each with every section the format asks for.

### Why
- TASK.md's interface list is the only specification another program sees; asserting it in the suite is cheaper than
  discovering a missing attribute at integration time.

### What worked
- `inspect.signature` checks pin the parameter names and the `confirmed=False` default without invoking anything.

### What didn't work
- My first version of `test_the_package_exports_the_required_names` contained a leftover no-op expression
  (`self.assertIsInstance(...) if False else None`); replaced with a plain export assertion before running.

### What I learned
- Writing the interface test last still found a wart: the package exported more than TASK.md requires
  (`Spec`, `BindingWarning`, the code constants). I kept them, because a plug-in author needs the codes and the
  warning type, and documented them in `__init__.py`'s `__all__`.

### What was tricky to build
- Nothing structural; the difficulty is only in deciding which extras are worth exporting. The rule I used: export
  what a plug-in or a consumer must name to use the pattern (record and spec shapes, argument types, codes,
  warnings), not internals such as `Failure`.

### What warrants a second pair of eyes
- `_check_result` in `hubreg/registry.py` treats a record with an empty `fields` list as "any keys allowed" while
  non-empty `fields` must match exactly; a reviewer should confirm that reading of the task's `fields` key.

### What should be done in the future
- If a second, overloading flavour of an action is ever needed, the chapter's "Overload sets" variation says the
  lookup should return candidates and the binder should pick; that is a change to `lookup`, `bind` and the
  diagnoser together, not a new key in a record.

### Code review instructions
- `tests/test_interface.py` and `hubreg/__init__.py`; validate with `python3 -m unittest discover -s tests`
  (169 tests, last result OK) and `python3 -m hubreg describe | python3 -m json.tool`.

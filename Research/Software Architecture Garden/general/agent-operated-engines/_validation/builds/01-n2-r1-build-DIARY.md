# Diary

## Goal

Build `hubreg`, the action registry of a home-automation hub — one record per action drives the binder, refusals,
the assistant's tool schemas, the mobile app's controls, help, confirmation and a walker test — and record here what
I read, designed, built, broke and fixed, one step per phase.

## Step 1: Reading the chapter, the task and the diary format; sketching the design

I read `CHAPTER.md`, `TASK.md` and `DIARY-FORMAT.md` completely, then sketched the module layout before writing any
code. The chapter's participants map almost one-to-one onto modules, so I chose that layout deliberately: records
and specs as validated value objects, a registry that stores them and answers every consumer's question, a binder
that never rewrites a call, a diagnoser that turns a failure into a refusal with a fix, a describer for the three
renderings (context line, full help, tool schemas, controls) and a walker that exercises every record.

### Prompt Context

**User prompt (verbatim):** "You are a software engineer joining a project. Your working directory contains three files:
- CHAPTER.md: a chapter of a design-pattern book describing the pattern you must apply;
- TASK.md: the software to build, with its required public interface;
- DIARY-FORMAT.md: how to keep your work diary.
Read all three completely first. Keep DIARY.md as you go, one step per phase of work, in that format. Then design, build and test the software in this directory. Work only inside this
directory (do not read or write outside it). Use only the Python 3 standard library. Run your tests and fix what
fails before you finish, and make sure DIARY.md is complete. Your final message must follow the output format at the end of TASK.md."

**Assistant interpretation:** Implement the "Self-Describing Operation Registry" pattern as a stdlib-only Python
package `hubreg` with the exact public interface listed in TASK.md, four demo plug-ins, a test suite under `tests/`,
and a diary kept phase by phase in the given format.

**Inferred user intent:** A build that demonstrates the pattern faithfully — every consumer (binder, help, tool
schemas, controls, walker) reads the same records — with a working test suite and an honest record of the process.

### What I did
- Read all three files fully (CHAPTER.md 25 KB, TASK.md, DIARY-FORMAT.md).
- Checked the interpreter: `python3 --version` → `Python 3.10.3`.
- Designed this layout, one module per participant plus a demo and a CLI:

  | Module | Participant / role |
  | --- | --- |
  | `hubreg/errors.py` | the shared vocabulary: `RecordError`, `Refusal`, `Warning`, `ResultError`, internal `Failure` |
  | `hubreg/argtypes.py` | `ArgType` + the four built-in types (number, string, enum, bool) with keys/accepts/check/example/parse/describe |
  | `hubreg/spec.py` | `ArgSpec` building and validation |
  | `hubreg/record.py` | `OpRecord` building and validation |
  | `hubreg/call.py` | `Call` (record + bound args + warnings) |
  | `hubreg/registry.py` | storage, structural + cross-record validation, confirmation policy, result check |
  | `hubreg/binder.py` | raw call → `Call` or `Failure`, never a rewrite |
  | `hubreg/diagnoser.py` | `Failure` → `Refusal` with valid names, nearest, fix |
  | `hubreg/describer.py` | context line, full help, tool schemas, app controls |
  | `hubreg/walker.py` | exercises every record and reports problems |
  | `hubreg/demo.py` | `demo_registry()` with the four required plug-ins |
  | `hubreg/__main__.py` | `describe`, `call`, plus `help`/`walk` conveniences |
  | `hubreg/nonrecord.py` | the enumerated exceptions (CLI verbs, globals) that cannot be records |

- Planned the binding order from the chapter's sketch: unknown action → unknown option (before missing) → per-spec
  default/optional/missing → type → limits → usual-range warning (supplied values only) → cross-argument hook.

### Why
- Chapter "Structure" and the mermaid diagram put the registry in the middle with binder, diagnoser, describer and
  walker as arrows out of it; one module per participant makes "any other list of operations found outside the
  registry is a bug" checkable by reading one directory.
- Implementation note 2 fixes the order (unknown keys before missing arguments) and the usual-range rules; note 3
  forbids coercion and silent defaults; note 4 says redirects only ever become a fix; note 5 puts samples in the
  record so registration can require them; note 11 makes confirmation one answer asked by every consumer.

### What worked
- The chapter is explicit enough that the module boundaries and the bind order were decided before coding.

### What didn't work
- N/A at this point (nothing run yet).

### What I learned
- The task's record shape has no `returns` kind and no positional `position` field, so two chapter features are out
  of scope: result *fields* stand in for a result kind, and every call is keyword-only. The chapter's
  "required positional after optional" structural check therefore has no analogue here; I will validate the parts
  that do apply and note the omission.

### What was tricky to build
- Nothing built yet. The one design tension I have to resolve while building: `bind` must raise `Refusal` per
  TASK.md while the chapter has the binder return a `Failure` and the diagnoser build the `Refusal`. I keep both:
  the binder module returns `Failure`, `Registry.bind` hands it to the diagnoser and raises the `Refusal`, so the
  chapter's collaboration (binder → diagnoser) survives inside the required interface.

### What warrants a second pair of eyes
- Whether `confirm_required` should be keyed by bare action name, `kind.name`, or both; I plan to accept both so a
  host policy cannot silently miss its target.

### What should be done in the future
- Build the modules in the planned order, tests alongside.

### Code review instructions
- Nothing to review yet; the design table above is the thing to challenge. Validate later with
  `python3 -m unittest discover -s tests`.

## Step 2: The core — records, types, registry, binder, diagnoser, describers, walker, demo, CLI

I wrote the package in the planned order: errors, argtypes, spec, record, call, binder, diagnoser, describer,
registry, walker, demo, nonrecord, `__main__`. Registration validates structure and, once all modules have
registered, what spans records. Binding follows the chapter's sketch exactly. Then I ran a manual smoke test of the
demo registry: catalogue, help, a bind with a usual-range warning, a run, and `walk()`.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Build the modules, then exercise them against the four required demo plug-ins.

**Inferred user intent:** Compiling, runnable code that already shows every participant at work before the formal
test suite exists.

### What I did
- Created `hubreg/errors.py` (RecordError, Refusal, Warning, ResultError, TypeProblem, Failure), `argtypes.py`
  (ArgType with `keys`/`accepts`/`check`/`example`/`parse`/`describe` and the number/string/enum/bool types),
  `spec.py`, `record.py`, `call.py`, `binder.py`, `diagnoser.py`, `describer.py`, `registry.py`, `walker.py`,
  `demo.py`, `nonrecord.py`, `__main__.py`, `__init__.py`.
- Ran `python3 -c "from hubreg import demo_registry; ..."` printing the catalogue, one full help text, a bind of
  `target=30`, its run and `walk()`.
- Ran the CLI by hand: `python3 -m hubreg describe`, `python3 -m hubreg call thermostat set_temperature target=30`,
  `python3 -m hubreg call door lock_door`.

### Why
- CHAPTER.md "Structure" and its mermaid diagram decide the module boundaries; "Collaborations" 2–7 decide the call
  paths; the Sketch decides the order inside `bind` (unknown action → unknown option → missing/type/limit → usual
  warning → hook).
- Implementation notes 2, 3, 4, 5, 9 and 11 drove: unknown keys before missing arguments; no coercion; redirects
  only ever offered as `fix`; samples in the record; a one-entry-point diagnoser; the enumerated non-record list;
  one confirmation answer asked by run, help, context line and tool schema.

### What worked
- `walk()` returned `[]` on the first run of the demo registry, and the manual CLI calls printed exactly the result
  and refusal shapes I wanted, including `E_CONFIRM` with a fix.

### What didn't work
- First smoke run showed fixes naming the *hard minimum*: `call thermostat.set_temperature(target=5)` for an
  unknown action. The example came from `spec.min`. I changed `NumberType.example` to prefer the default, then the
  midpoint of the usual range, then a limit, so fixes now say `target=20`.
- Earlier draft of `spec.py` checked a default against a stand-in probe object that had no limits, so
  `default=120` with `max=100` passed. Fixed by building the `ArgSpec` first and checking the default against the
  real spec; `tests/test_records.py::test_default_outside_the_limits_is_refused` now pins it.
- `describer.help_text` was written with a leftover dead conditional expression; rewritten to a plain signature
  line. The tool-schema description joined a doc ending in "." with ". " and produced "Celsius.. unit", fixed by
  stripping the trailing full stop before joining.

### What I learned
- The chapter's warning about "one record, many consumers" bit immediately: the same fix string is produced by the
  diagnoser for both `E_UNKNOWN_ACTION` and `E_UNKNOWN_OPTION`, so improving `argtypes.render_call` improved both
  at once — the payoff the chapter promises.
- A numeric `valid` list is meaningless; only enum checks can populate `Refusal.valid` for value failures. I left
  the numeric `valid` empty and put the clamped value in `fix` instead (the chapter's `check.valid` is optional).

### What was tricky to build
- `Registry.finalize()` calls the binder, and the binder asks the registry to look records up, so finalize could
  re-enter itself. Solved with a `_finalizing` guard in `_ensure_finalized()`; a failed finalize leaves
  `_finalized` false so the next consumer retries (that is what makes "a redirect to an action registered later"
  work).
- `bind` must raise `Refusal` (TASK.md) while the chapter has the binder return a `Failure` that the diagnoser
  explains. Solved by keeping `binder.bind` returning `Call | Failure` and having `Registry.bind` explain and raise.

### What warrants a second pair of eyes
- `record.py` refuses unknown record keys. That is strictness the chapter favours, but a plug-in with an extra
  annotation key would be refused; worth checking against other plug-ins.
- The walker's usual-range probe is skipped silently when a cross-argument hook refuses the probe value; that is
  deliberate but hides a case.

### What should be done in the future
- Write the test suite module by module and add a CLI test; then re-read the four demo records against TASK.md.

### Code review instructions
- Start at `hubreg/registry.py` (`register`, `finalize`, `bind`, `run`, `check_result`) and `hubreg/binder.py`;
  then `hubreg/walker.py`. Validate with `python3 -m unittest discover -s tests` and
  `python3 -m hubreg walk`.

## Step 3: Tests for records and binding (and the first failing run)

I wrote `tests/test_records.py` (every structural and semantic registration rule) and `tests/test_binding.py`
(defaults, unknown action/option, redirects, types, limits, usual-range warnings, the hook, refusal attributes).
Then I ran the suite from the working directory.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Pin the registration rules and the binder's order with tests, then make them pass.

**Inferred user intent:** A test suite that would catch the mistakes the chapter names (silent defaults, coerced
types, redirects that run) rather than only the happy path.

### What I did
- Created `tests/test_records.py` (32 tests) and `tests/test_binding.py`.
- Ran `python3 -m unittest discover -s tests`.

### Why
- Implementation note 1 (structural and semantic record checks), note 2 (unknown keys before missing arguments,
  hard limits versus usual ranges, defaults never warn), note 3 (nothing falls back silently) and note 4 (a
  redirect is only ever offered) each became at least one test.

### What worked
- The registration tests found no code bugs; the rules I had written in `spec.py`/`record.py` matched the tests, and
  the duplicate-argument, default-outside-limits and usual-range-inside-limits rules all fired on the first try.

### What didn't work
- `python3 -m unittest discover -s tests` reported three errors, all in my own fixtures, not in the library:

  ```
  hubreg.errors.RecordError: E_BAD_SAMPLES: light.dim: sample 0 {} does not bind: light.dim requires the argument 'target' (number C); required: target; Target.
  ```

  The helper record I reused still carried `samples=[{}]` after I replaced its arguments with a required one.
  Fixed by giving those three fixtures samples that satisfy their arguments.

### What I learned
- The chapter's insistence that samples live in the record pays off immediately: the broken fixtures were caught
  before any test logic ran, by the same code path users take.
- But it also showed the cost of checking samples at finalize: a test that only wants a tool schema cannot use a
  record whose sample is stale. I kept the check at finalize for this step and revisited it in Step 6.

### What was tricky to build
- Testing "unknown option before missing argument" needed a record with a required argument and no default; the
  first version of that test hit the sample check instead, which is how the fixture bug surfaced.

### What warrants a second pair of eyes
- `test_a_redirect_to_an_action_registered_later_passes` asserts that the *second* bind raises something that is
  not a `RecordError`; it documents the retry-after-register behaviour of `finalize` but reads obliquely.

### What should be done in the future
- Add the run/confirmation, consumer, walker, demo and CLI tests.

### Code review instructions
- Read `tests/test_records.py` and `tests/test_binding.py`; run `python3 -m unittest discover -s tests`.

## Step 4: Tests for running, confirmation and the three consumers

Next I covered the runner (`tests/test_run.py`) and the consumers (`tests/test_consumers.py`): tool schemas, app
controls, help, the context line, the reference, and one test that adds a new record and checks it reaches every
consumer untouched.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Prove that confirmation is one answer and that the catalogues are generated, not
written.

**Inferred user intent:** Confidence that the assistant, the app and the hub cannot disagree about an action.

### What I did
- Created `tests/test_run.py` (15 tests) and `tests/test_consumers.py` (18 tests).
- Ran the suite: 90 tests, all passing.

### Why
- Implementation note 11 (a host-decided flag has one answer, asked by every consumer) is tested from both sides:
  `Registry(confirm_required=...)` without a record flag, a record flag alone, and a record flag that tries to
  *lower* host policy.
- Collaboration 6 (two lengths: standing context and full help) is tested with the one-line context and a full
  reference.
- The "one source" test adds a fan action and asserts it appears in schema, controls, help, context, reference and
  the walk without editing any consumer.

### What worked
- The consumers already agreed because they all call the same `describer` functions over the same records; the
  tests passed first time, including JSON round-tripping of schemas and controls.

### What didn't work
- Nothing failed in this step. The only surprise was that `help()` on an argumentless action prints
  `Arguments: none` and `Confirmation: required` on two separate lines; the test asserts both strings, so it is
  pinned.

### What I learned
- Result checking belongs in `Registry.run` *and* in the walker through the same `check_result`; writing
  `test_extra_result_field_is_a_resulterror` made it obvious that the record author's fault must not be reported
  as a caller's `Refusal`.

### What was tricky to build
- Nothing in this step; the interesting question was where `x-needs-confirmation` lives. I put it on the tool
  schema, in the help confirmation line and in the context line's `[needs confirmation]` suffix, all from
  `registry.needs_confirm`.

### What warrants a second pair of eyes
- The tool-schema key names (`input_schema`, `x-unit`, `x-usual`, `x-result-fields`) are my choice; TASK.md only
  requires "an input schema with types, units and ranges".

### What should be done in the future
- Walker, demo and CLI tests.

### Code review instructions
- `tests/test_run.py`, `tests/test_consumers.py`; run `python3 -m hubreg describe` and compare with
  `reg.tool_schemas()`.

## Step 5: Walker tests, and the two walker bugs they found

`tests/test_walker.py` exercises the walker itself: a clean demo, a wrong result field, a missing field, an
implementation that raises, a leaky runner that skips the confirmation gate, an `E_CONFIRM` without a fix, and a
forgiving registry that follows a redirect.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Make sure the walker actually reports the problems it claims to look for, not just
that `walk()` returns `[]` on the demo.

**Inferred user intent:** A test of the test-walker (the chapter's "the walker proves less than it seems").

### What I did
- Created `tests/test_walker.py` and ran `python3 -m unittest discover -s tests`.

### Why
- Implementation note 5: "write the result check once", "one happy-path call per record does not exercise limits,
  redirects, warnings or optional arguments; generate those probes from the records".
- The false "safe" description test follows note 11's construction experience, using `unittest.mock.patch` to make
  the describer lie about confirmation.

### What didn't work
- First run: `Ran 100 tests ... FAILED (failures=1, errors=1)`.

  ```
  FAIL: test_walk_catches_a_result_with_an_unexpected_field
  AssertionError: 2 != 1
  ```

  The walker reported the same broken result twice: once from `_check_samples` and once from `_check_confirm`,
  which ran the action again and turned the `ResultError` into "unconfirmed run failed". Fixed by making
  `_check_confirm` ignore `ResultError` (already reported) and report only confirmation problems.

  ```
  ERROR: test_walk_catches_an_implementation_that_raises
  RuntimeError: device unplugged
  ```

  `_check_samples` caught only `Refusal` and `ResultError`, so an action that throws escaped the walker. Fixed by
  catching `Exception` there and reporting it as the action's fault; `_check_confirm` catches exceptions too.

- An earlier version of the "lying describer" test subclassed `Registry.tool_schemas`, which the walker never calls
  (it calls `describer.tool_schema` directly), so the test asserted nothing. Replaced with `mock.patch.object` on
  `hubreg.describer.tool_schema`.

### What I learned
- The walker must be tested like any other consumer; my first version silently let exceptions through, exactly the
  "walker proves less than it seems" risk the chapter names.

### What was tricky to build
- Distinguishing problems the caller causes (refusals) from problems the record author causes (results, throws):
  the walker now reports both, but only `ResultError`/exceptions are the author's.

### What warrants a second pair of eyes
- `_outside_usual` picks `high + 1` or `low - 1`; if the usual range fills the hard limits the probe is skipped,
  so such a record's warning path is untested by the walk.

### What should be done in the future
- Demo and CLI tests, and a final read of the demo records against TASK.md.

### Code review instructions
- `hubreg/walker.py` (generated probes) and `tests/test_walker.py`; run `python3 -m hubreg walk`.

## Step 6: Demo, CLI, interface, non-record and type tests, plus the changes review forced

The last test files cover the four demo plug-ins against TASK.md, the command line in a subprocess, the exact public
interface TASK.md promises, the enumerated non-record list, and the pluggable argument-type table. Writing and
reviewing them forced four design changes, all recorded below.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Close the remaining surface (demo shapes, CLI, exported names, non-records, custom
types) and make the system behave sensibly at the edges those tests reach.

**Inferred user intent:** A library whose promised interface is what it says, with no consumer able to disagree with
another.

### What I did
- Created `tests/test_demo.py`, `tests/test_cli.py` (subprocess calls to `python3 -m hubreg`), `tests/test_interface.py`,
  `tests/test_nonrecord.py`, `tests/test_types.py`, and `tests/__init__.py` so plain `python3 -m unittest discover`
  also finds the suite.
- Changed `RecordError` to carry one code, `E_BAD_RECORD`, with the narrower reason in `.detail` (the chapter's
  `register` refuses `E_BAD_RECORD`; TASK.md only promises `.code` is a string).
- Removed the sample-binding check from `Registry.finalize()`: a record with a stale sample can still be described
  and called, and `walk()` reports the sample as a problem. Only redirect targets are checked across records now.
- Added case-only near-miss fixes (a case difference is offered as `fix`, never followed), guarded
  `closest_name`/`_unknown_option` against non-string keys, accepted `confirm_required=None`, and fixed a
  `ResourceWarning` from an unclosed file in the non-record test.
- Added `README.md` with the participant-to-module map.

### Why
- TASK.md's own list of codes (`E_UNKNOWN_ACTION`, `E_UNKNOWN_OPTION`, `E_ARG_TYPE`, `E_ARG_RANGE`,
  `E_ARG_MISSING`) is about calls; the chapter gives records one code. Splitting the two vocabularies keeps
  refusals predictable for callers and detailed for plug-in authors.
- Implementation note 5 requires samples in the record; nothing there says a stale sample must make the action
  undescribable. Reporting it from the walker is more useful and keeps `tool_schemas()` working for a plug-in whose
  test data is behind.
- Note 4: "a redirect or a case-insensitive match is never followed, only offered as the fix" — the case-only fix
  makes that literal for names that differ only in case.
- Note 6: the type table lives in the registry; `tests/test_types.py` proves a plug-in type works in one registry
  and leaks into none.

### What worked
- All five new files passed after the library changes; `python3 -m hubreg describe|call|help|walk` all behave and
  the CLI prints warnings on stderr while keeping stdout valid JSON.

### What didn't work
- `python3 -m unittest discover` found 0 tests before `tests/__init__.py` (`Ran 0 tests in 0.000s`). The task's
  command (`-s tests`) worked, but adding the empty `__init__.py` makes both work.
- `tests/test_nonrecord.py` first raised `ResourceWarning: unclosed file
  <_io.TextIOWrapper name='.../hubreg/registry.py'>` because I used bare `open(...).read()`; replaced with
  `Path(...).read_text()`.
- After normalising the record code, eight record tests failed with `AssertionError: 'E_BAD_RECORD' != 'E_BAD_SPEC'`;
  updated them to assert `.code == "E_BAD_RECORD"` and `.detail`.
- `test_a_sample_that_does_not_bind_fails_at_finalize` became wrong when the sample check moved to the walker; it is
  now `test_a_sample_that_does_not_bind_is_a_walk_problem` and asserts the problem dict.

### What I learned
- The one-code-for-records rule makes the caller-facing list small. It also showed that a custom argument type is
  genuinely one file plus one registry argument — the consumer code needed no change at all.
- A `.detail` field on `RecordError` is worth it: the message alone is enough for the author, but tests and the CLI
  can distinguish a bad default from a bad redirect.

### What was tricky to build
- Keeping the walker's probes meaningful for a plug-in type it has never heard of: `_wrong_type_value` falls back to
  an `object()`, which every type refuses, so the probe still works. The same fallback keeps the walker from
  switching on type names.

### What warrants a second pair of eyes
- Dropping the finalize-time sample check is a deliberate deviation from the chapter's `finalize()` sketch; the
  trade-off (describable-but-stale plug-ins versus failing before any call) should be reviewed.
- `tests/test_nonrecord.py` reads the package source to prove no module outside `demo.py` names an action; if the
  demo actions are renamed, the list in that test must change too.

### What should be done in the future
- A real plug-in loading path (import a module, call its `records()`), and per-action redirect tables fed from
  observed transcripts (Chapter 13).

### Code review instructions
- `tests/test_cli.py` and `tests/test_interface.py` are the fastest way to see the promised interface exercised;
  `tests/test_types.py` shows the pluggable-type seam. Run `python3 -m unittest discover -s tests`.

## Step 7: Final check — the whole suite, the CLI, and the diary

I ran the full suite again from a clean tree (no `__pycache__`), exercised every CLI verb one last time, and read
`DIARY.md` back for format and completeness. Nothing failed, so this step has no fixes to record.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Verify the delivered state end to end and make sure the diary matches the work.

**Inferred user intent:** A finished build with a green suite, working commands and an honest, complete diary.

### What I did
- `python3 -m unittest discover -s tests` → `Ran 154 tests ... OK`.
- `python3 -m hubreg describe` → four tool schemas in JSON (`thermostat.set_temperature`, `light.dim`,
  `door.lock_door`, `scene.run_scene`).
- `python3 -m hubreg walk` → `[]`; `python3 -m hubreg call scene run_scene scene=morning` → `{"scene": "morning"}`;
  `python3 -m hubreg call door lock_door` → `E_CONFIRM` exit 1; `python3 -m hubreg call door lock_door --confirm`
  → `{"locked": true}`; `python3 -m hubreg call thermostat set_temperature target=30` → result on stdout, the
  `RANGE` warning on stderr.
- Removed `__pycache__` directories; listed the tree (13 package modules, 10 test modules, `README.md`, `DIARY.md`).
- Re-read the diary top to bottom.

### Why
- The task asks for the tests to be run and fixed before finishing, and for the diary to be complete; this step
  checks both rather than assuming them.

### What worked
- The suite is green, every demo action walks clean, and every refusal the CLI prints names a fix or the valid
  names.

### What didn't work
- Nothing failed in this step.

### What I learned
- The end-to-end CLI output is the cheapest proof that the three consumers agree: `describe` and `help` are
  generated from the same records the `call` path binds against, and `walk` re-derives the probes from them.

### What was tricky to build
- Nothing new. The one recurring tension remained the record-versus-call error vocabulary, resolved in Step 6 with
  `E_BAD_RECORD` for records and TASK.md's five codes for calls.

### What warrants a second pair of eyes
- Whether refusing unknown *record* keys and requiring `samples` is the right strictness for a plug-in API; both are
  defensible readings of CHAPTER.md and both could surprise a third-party plug-in author.
- Whether the tool-schema key names should follow a particular convention (TASK.md does not say).

### What should be done in the future
- Load plug-ins from real modules, collect redirects from real transcripts (Chapter 13), and add a
  `python3 -m hubreg reference` command for the long catalogue.

### Code review instructions
- Start at `hubreg/registry.py` and `hubreg/binder.py`, then `hubreg/walker.py`; the four demo records are in
  `hubreg/demo.py`. Validate with `python3 -m unittest discover -s tests`, `python3 -m hubreg walk` and
  `python3 -m hubreg describe`.

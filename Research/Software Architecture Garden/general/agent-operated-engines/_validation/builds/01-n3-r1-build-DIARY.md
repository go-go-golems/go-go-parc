# Diary

## Goal

Build `hubreg`, the action registry of a home-automation hub (Python 3, standard library only), applying the
"self-describing operation registry" pattern of CHAPTER.md: one record per action drives binding, refusals, tool
schemas, app controls, help and the registry walk. This diary records each phase, each failure and each fix.

## Step 1: Reading the chapter, the task and the diary format; designing the module split

I read CHAPTER.md (the pattern: operation record, argument spec, registry, binder, describer, diagnoser, walker,
pluggable argument types, flags, hooks, redirects), TASK.md (the required `hubreg` public interface plus four demo
actions) and DIARY-FORMAT.md. I then designed the file split so that every participant of the chapter is a separate
module and nothing outside the registry keeps a list of actions.

### Prompt Context

**User prompt (verbatim):** "You are a software engineer joining a project. Your working directory contains three files:
- CHAPTER.md: a chapter of a design-pattern book describing the pattern you must apply;
- TASK.md: the software to build, with its required public interface;
- DIARY-FORMAT.md: how to keep your work diary.
Read all three completely first. Keep DIARY.md as you go, one step per phase of work, in that format. Then design, build and test the software in this directory. Work only inside this
directory (do not read or write outside it). Use only the Python 3 standard library. Run your tests and fix what
fails before you finish, and make sure DIARY.md is complete. Your final message must follow the output format at the end of TASK.md."

**Assistant interpretation:** Implement a small library and CLI, `hubreg`, whose single source of truth is a table of
action records; every consumer (binder, describer, diagnoser, walker, CLI) must read that table; write tests and run
them; keep the diary in the prescribed format; finish with one JSON object.

**Inferred user intent:** A working, tested application of the chapter's pattern that a reviewer can check against the
chapter's participants and implementation notes — not a generic library that merely mentions the pattern.

### What I did
- Read all three files completely (CHAPTER.md 25 KB, TASK.md, DIARY-FORMAT.md).
- Planned the modules: `errors.py` (RecordError, Refusal, Failure, Warning), `nearness.py` (nearest-name search),
  `argtypes.py` (per-registry argument type table), `registry.py` (validation, storage, one answer per question),
  `binder.py` (call → Call + warnings), `diagnoser.py` (Failure → Refusal), `describer.py` (context line, help, tool
  schemas, controls), `result.py` (the one result check), `walker.py` (exercises every record), `demo.py`,
  `manual.py` (the visible list of non-record operations), `__main__.py` (CLI).

### Why
- The chapter's Structure table lists participants that only pay off when they are separate consumers of one
  registry ("the registry sits in the middle; every arrow out of it is a consumer that would otherwise keep its own
  copy"). A single-file library would hide whether the consumers really read the records.
- Implementation note 6: argument types must own everything type-specific and the type table must live on the
  registry, not in a module, so `argtypes.py` contains classes and `Registry` owns the `dict`.

### What worked
- The mapping of TASK's record dict onto the chapter's `OpRecord`/`ArgSpec` was direct; TASK's `fields` list replaces
  the chapter's `returns: Kind` plus `fields(boundArgs)`.

### What didn't work
- Nothing yet; this step was reading only.

### What I learned
- TASK's interface has no `finalize()`, no `expand` (composite actions) and no positions, so those parts of the
  chapter must either be carried internally (cross-record checks) or deliberately dropped and written down.

### What was tricky to build
- Deciding where the "argument type" boundary sits for TASK's four types (`number`, `string`, `enum`, `bool`): which
  spec keys each type allows, and that `values` is only meaningful for `enum`.

### What warrants a second pair of eyes
- Whether dropping `expand` (composite records) and positional arguments is acceptable for the hub, or whether a
  reviewer reads the chapter as requiring them.

### What should be done in the future
- If the hub grows composite actions (a "good night" scene = several locks and lights), give them records with an
  `expand` key rather than a second list of actions.

### Code review instructions
- Start with `hubreg/registry.py`, then read outward to the consumers. Validate with
  `python3 -m unittest discover -s tests`.

## Step 2: The failure vocabulary and the argument types

I built the two foundations everything else speaks in: the error classes and the per-registry table of argument
types.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Give the binder and the diagnoser one internal failure value, one caller-facing
refusal, one plug-in-facing record error, and one warning type; then give every argument type everything
type-specific so the binder never switches on a type name.

**Inferred user intent:** The refusals, the help and the tool schemas must be produced from the same data, so the
vocabulary has to be shared rather than reinvented per consumer.

### What I did
- `hubreg/errors.py`: `RecordError(code, message, where)`, `Refusal(code, message, valid, nearest, fix)` with
  `as_dict()`, `Warning(code, message, option)`, and the internal `Failure` the binder returns.
- `hubreg/nearness.py`: `closest(word, options)` — case-insensitive exact match, else `difflib` at cutoff 0.6.
- `hubreg/argtypes.py`: `Problem`, `ArgType` base (`allowed_keys`, `accepts`, `check`, `outside_usual`, `example`,
  `parse`, `describe`, `phrase`), and `Number`, `String`, `Enum`, `Bool`, plus `builtin_types()`.

### Why
- CHAPTER.md, implementation note 6: "every build with pluggable types still switched on `number` and `enum` by name
  for which spec keys apply ... So the type also names its spec keys, gives an example and parses text."
- `outside_usual` lives on the type because the usual range means different things per type (a number range, a
  character count); putting the comparison in the binder would have put type knowledge back in the core.

### What worked
- `Number.example` walking `usual` first, then the hard limits, produced repairs a caller can paste
  (`set_temperature(target=16)`).
- `Enum.check` reusing `closest` gave "use 'morning'" for "mornin" for free.

### What didn't work
- The first draft of `Number.phrase` had a stray leftover list expression and duplicated the unit
  (`number from 0 to 100%, usual 10 to 90% in %`); I removed the dead line and then removed the second unit suffix
  from `describer._arg_help`, which was adding it again.

### What I learned
- A usual range on a string is a length range; without `outside_usual` the binder would have compared `str` with
  `int` and crashed on the first such record.

### What was tricky to build
- Deciding which spec keys each type allows. `redirects`, `optional`, `default`, `unit`, `doc`, `name`, `type` are
  base keys; `min`/`max`/`usual`/`usual_hint` belong to numbers and strings, `values` to enums only. Registration
  refuses a key a type does not name, so a `values` on a number cannot be silently ignored.

### What warrants a second pair of eyes
- The cutoff 0.6 produces a suggestion for "level"/"labels" (0.545 is below it, so fine) but it does produce
  suggestions that are plain wrong for very short names; the redirects, not the edit distance, carry the
  measured near-misses, which is the chapter's position.

### What should be done in the future
- A `colour` or `box` type is now one new class plus one `add_type` call; no consumer changes.

### Code review instructions
- `hubreg/argtypes.py` first (numbers, strings, enums, bools), then `hubreg/errors.py`. Validate with
  `python3 -m unittest discover -s tests`.

## Step 3: The registry — record validation and one answer per question

I wrote the registry: it validates a record when it is registered, checks what spans records at `finalize()`, stores
one record per (device kind, action name), and answers the questions every consumer asks.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Registration must refuse both structural and semantic mistakes, and the cross-record
checks (redirect targets, samples that bind) must run once all plug-ins have registered.

**Inferred user intent:** A wrong record should fail before any call, not produce plausible wrong behaviour later.

### What I did
- `hubreg/registry.py`: `Registry(confirm_required=())` with `self.types` (per instance), `register`, `finalize`,
  `record_for`, `get`, `all_records`, `keys`, `kinds`, `action_names`, `action_redirect`, `option_redirect`,
  `needs_confirm_record`, `needs_confirm`, `bind`, `run`, `reply`, `tool_schemas`, `tool_schema`, `controls`,
  `help`, `context_line`, `context_lines`, `walk`, `add_type`.
- Structural checks: record keys, name/kind, callable `run`, callable `validate`, result field names, unique typed
  arguments, samples present and dict-shaped, known flags, named redirects, and (on) uniqueness.
- Semantic checks: default passes its type's `accepts` and `check` (so a default outside the hard limits is
  refused), `min <= max`, `usual` is a pair with `low <= high` inside the hard limits.
- Cross-record checks at `finalize()`: redirect targets exist, a redirect does not shadow a real action, no
  conflicting redirects, and every sample binds.

### Why
- CHAPTER.md, implementation note 1: goja-cv "does not check that a default lies within the limits or that a
  redirect points at an existing operation, and such mistakes reach agents before anyone notices. Both kinds of
  check belong to the pattern."
- Note 11: `needs_confirm_record` is the single answer the runner and every describer ask; host policy raises the
  flag and a record cannot lower it.

### What worked
- Lazy `finalize()`: TASK.md's interface has no `finalize` in the public surface, so every consumer calls
  `_ensure_finalized()`; a broken redirect therefore fails at the first `bind`, `tool_schemas` or `walk`, and
  `finalize()` stays available for plug-ins that want it at start-up.
- A record whose redirect target is registered later is accepted, because the check runs at the end, not per
  record.

### What didn't work
- My first normalisation put `"default": spec.get("default", _MISSING)` into every stored spec, which made
  `"default" in spec` true everywhere and would have turned every argument into an optional one with a `<no
  default>` value. I replaced it with an explicit conditional assignment.

### What I learned
- TASK.md's record dict has no `expand` (composite actions) and no argument positions, so two of the chapter's
  structural checks ("both or neither of an implementation and an expansion", "a required positional argument after
  an optional one") have nothing to check here. I kept the first as a comment in the message for a missing `run`
  and dropped the ordering rule, because without positions the declaration order has no meaning.

### What was tricky to build
- Avoiding infinite recursion between `finalize()` and the binder: `finalize` calls `binder.bind`, which uses
  `registry.record_for` (no finalize) rather than `Registry.bind` (which finalizes). A `_finalizing` guard covers the
  rest.

### What warrants a second pair of eyes
- Whether refusing unknown record keys is too strict for third-party plug-ins that carry their own metadata; I
  chose strictness because a typo in `sampels` would otherwise silently disable the walk.

### What should be done in the future
- If two records should be allowed to share a name on one kind (overload sets in the chapter's Variations), the
  lookup has to return candidates and the binder has to choose; today the key is (kind, name) and registration
  refuses a duplicate.

### Code review instructions
- `hubreg/registry.py`, `register`/`_check_record`/`_check_arg_spec` and then `finalize`. Validate with
  `python3 -m unittest discover -s tests`.

## Step 4: The binder — a call becomes checked arguments plus warnings

I wrote the binder that turns a raw argument dict into a `Call` with defaults filled and warnings attached, or into
a `Failure` for the diagnoser.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Check unknown names before missing arguments, never coerce a wrong type to a zero
value, never let a default warn, and never rewrite the call.

**Inferred user intent:** An agent that typed a near-miss should get the repair, and a plausible-looking but wrong
run must be impossible.

### What I did
- `hubreg/binder.py`: `Call(record, args, warnings)` with `.record_name`, `.on`, `.args`, `.warnings`;
  `bind(reg, on, name, raw)`; `_hook_failure` for the cross-argument hook.
- Order: unknown action → unknown options (first in insertion order) → per argument (supplied, default, optional,
  missing) → `accepts` → `check` → usual-range warning → the hook.

### Why
- Chapter note 2: "Check unknown keys before missing arguments, so a near-miss (`temp` for `target`) gets its
  repair"; note 3: "Nothing falls back to a default silently."
- The hook returns "in the diagnoser's vocabulary" (Structure table), so a dict with `code`/`message`/`valid`/`fix`
  or a plain string both become an `E_ARG_RANGE` refusal—no third error dialect.

### What worked
- Binding `level=0` keeps `0`; a `"21"` string for a number is `E_ARG_TYPE`, not 21.

### What didn't work
- Nothing failed in this step; the failures this code caused appeared in the test phase (a hook that refuses the
  sample makes `finalize()` refuse the record, which is correct but I had not expected it in a test).

### What I learned
- Warnings must be built from the spec (`usual_hint`) rather than phrased generically, or the caller learns nothing
  from them.

### What was tricky to build
- The usual-range warning text includes the type's phrase, so "outside the usual range 16 to 24 (number from 5 to
  35 °C, usual 16 to 24 °C)" repeats itself; it is redundant but never wrong, and the type keeps ownership of the
  wording. A reviewer may want it shortened.

### What warrants a second pair of eyes
- `Call` keeps a reference to the stored record, so a plug-in that mutates its record after binding changes a bound
  call's semantics. Copying the record per call would be safer but would break identity checks.

### What should be done in the future
- If the hub ever accepts positional calls, `bind` must refuse a value given both positionally and by name
  (`ARG_DUPLICATE`), which the chapter's sketch requires and TASK.md's dict-only interface cannot express.

### Code review instructions
- `hubreg/binder.py` is one function and one class; read it after `registry._check_arg_spec`.

## Step 5: The diagnoser — every refusal names the intended call

I wrote the diagnoser: one entry point from a `Failure` to a `Refusal`, using the same record the binder used.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Read the record for the valid names, the nearest name and the declared redirect, and
return a refusal whose fix is the call to make instead.

**Inferred user intent:** A refusal that only says "unknown option" sends the agent back to the documentation; one
that names the intended call does not.

### What I did
- `hubreg/diagnoser.py`: `explain(reg, failure)` dispatching to `_unknown_action`, `_unknown_option`, `_missing`,
  `_arg_type`, `_arg_range`, `_hook`.
- Fixes are produced by `describer.call_skeleton`, so `unknown option temp` becomes
  `set_temperature(target=16)` and `E_CONFIRM` becomes `lock_door(confirmed=true)`.
- A declared redirect wins over the nearest name, and the message shows both ("did you mean 'run_scene'? call
  run_scene(scene=morning) (the nearest existing name is ...)").

### Why
- CHAPTER.md, Collaborations 3 and implementation note 4: "A redirect never rewrites a call; it only gives the
  refusal a fix naming the intended call."
- Codes are exactly the five TASK.md lists (plus `E_CONFIRM` from `run`), so a caller can branch on them.

### What worked
- `closest("Dim", ["dim"])` finds the case-only difference and the message adds "action names are case-sensitive,
  did you mean 'dim'?" — offered, never followed.

### What didn't work
- My first expectation in a test was `set_temperature(target=21)`; the code produced `target=5` because the repair
  value is the type's example (the usual low, or the hard minimum). The code was right and the test wrong; I fixed
  the test, but it is a sign the example could prefer a *middle* value of the usual range when there is one.

### What I learned
- `difflib` does not consider "temp" close to "target" (ratio 0.4), which is exactly why the chapter insists that
  redirects come from measured near-misses instead of a guess.

### What was tricky to build
- Producing a *corrected value* for an out-of-range argument (not just a phrase): `Problem.value` carries the
  clamp (35 for 99) or the nearest enum value, so the fix is pasteable.

### What warrants a second pair of eyes
- The unknown-kind case returns `E_UNKNOWN_ACTION` with `valid=[]` and the known kinds in the message; a caller
  that wants to branch on kinds has to read the message.

### What should be done in the future
- If refusals are rendered for a UI, `Refusal.as_dict()` is already the wire format; nothing else needs to change.

### Code review instructions
- `hubreg/diagnoser.py` together with `hubreg/describer.py`'s `call_skeleton`.

## Step 6: The describer — the second consumer

I wrote the describer: context line, full help, tool schema and app controls, all rendered from the same record,
all asking the registry the confirmation question.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Three consumers with three lengths from one source: JSON tool descriptions for the
assistant, one control dict per argument for the app, and a full help text on request.

**Inferred user intent:** Neither the assistant nor the app may keep its own idea of what an action accepts.

### What I did
- `hubreg/describer.py`: `first_sentence`, `fmt_value`, `call_skeleton`, `field_names`, `context_line`,
  `help_text`, `_arg_help`, `tool_schema`, `controls`.
- Tool schema: `{name: "kind.action", kind, action, description, requires_confirmation, input_schema}` with
  `properties` from each type's `describe` (type, unit, minimum/maximum, enum, default, usual range and hint) and
  `required` from the record.

### Why
- Structure table: the describer is "Always: it is the second consumer" — the registry only pays off once a second
  reader exists.
- Note 11: two of three chapter builds rendered tool schemas from the record's flag and told the assistant a
  host-guarded action was safe; here `requires_confirmation`, the description suffix, the help line and the context
  line all call `needs_confirm_record`.

### What worked
- `help light dim` shows units, hard limits, the usual range with its hint, the default and the known near-misses.
- The app controls have exactly the seven keys TASK.md lists, with `values` only for enums.

### What didn't work
- The help line printed "in %" twice (once from the type's phrase, once from `_arg_help`). Fixed by deleting
  `_unit_note` and the extra suffix.

### What I learned
- `first_sentence` needs to handle "°C." — the splitting on ". " works because of the space.

### What was tricky to build
- Deciding what `unit` means in a JSON schema: `minimum`/`maximum` are in the declared unit, and `unit` is
  metadata, because units are converted only at evaluation (Chapter 2), which this hub does not do.

### What warrants a second pair of eyes
- Tool names use `kind.action`; MCP servers often forbid dots in tool names. If the assistant's host rejects dots,
  a sanitised `kind__action` with the real name in the description would be needed.

### What should be done in the future
- A `controls()` rendering for a value-dependent widget (a slider with the usual range shaded) only needs the keys
  already present.

### Code review instructions
- `hubreg/describer.py`; compare `tool_schema` with `help_text` for the same record and check they cannot disagree.

## Step 7: The walker — the test that walks the registry

I wrote the walker that exercises every record: describers, samples, generated probes for limits, wrong types,
enum values and usual ranges, declared near-misses, and confirmation agreement.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** One happy-path call per record proves little; the probes must be generated from the
records, and a broken record must be reported, not raised.

**Inferred user intent:** Adding an action must be hard to do incorrectly — the walk fails when the record and its
behaviour disagree.

### What I did
- `hubreg/walker.py`: `walk(reg)`, `catalogue_problems(reg)`, `describe_problems`, `sample_problems`,
  `argument_problems`, `redirect_problems`, plus the probe helpers.
- Problems are dicts with `action` and `problem` (and `detail` when there is a refusal to quote).
- `hubreg/result.py`: the one `check_result(record, args, result)` used by both `run` and the walker.

### Why
- Chapter note 5: "One happy-path call per record does not exercise limits, redirects, warnings or optional
  arguments; generate those probes from the records. Put the samples in the record, so registration can require
  them."
- Note 5 also: "Write the result check once; if `run` also checks results, it calls the same function and reports a
  mismatch as the operation's fault."

### What worked
- The demo catalogue walks clean (`[]`), and the probes did find a real class of bug when I broke a type on
  purpose (a `Number` subclass whose `check` returns None).

### What didn't work
- I wrapped the walk in a bare `except Exception` twice and swallowed the difference between a `Refusal` (caller
  error) and a `RecordError` (record error); the current code catches `RecordError` separately so a broken
  `fields()` is reported as a record fault.

### What I learned
- The walk cannot catch a limit that a record never declared: probes are generated from the record, so a missing
  `min` produces no probe. My first test for "a softened limit is reported" was therefore wrong (see Step 9).

### What was tricky to build
- Probes must not use values that trip an unrelated rule: the base argument dict is built from required arguments'
  examples, and each probe overrides exactly one argument.

### What warrants a second pair of eyes
- `walk` runs confirmed for actions that need confirmation, deliberately (it exercises behaviour, not the
  security gate), and separately checks that the unconfirmed run was refused with `E_CONFIRM`.

### What should be done in the future
- Property-style probes (random values inside and outside each limit, many samples) would go beyond one call per
  record without changing the pattern.

### Code review instructions
- `hubreg/walker.py` and `hubreg/result.py`; run `python3 -m hubreg walk` and `python3 -m unittest discover -s tests`.

## Step 8: The demo plug-ins, the visible exception list and the command line

I wrote the four demo plug-ins as records, the one list of operations that are not records, and the CLI.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** TASK.md fixes four demo actions with exact names, units, limits and result fields; the
CLI needs `describe` and `call`, and the package needs `hubreg.demo_registry()`.

**Inferred user intent:** A runnable demonstration that the catalogue is the only list of actions.

### What I did
- `hubreg/demo.py`: `THERMOSTAT_SET_TEMPERATURE`, `LIGHT_DIM`, `DOOR_LOCK_DOOR`, `SCENE_RUN_SCENE`,
  `demo_records()`, `demo_registry()` (host policy `confirm_required=("lock_door",)` *and* the record's own
  `flags={"confirm": True}`).
- `hubreg/manual.py`: `MANUAL_OPERATIONS = ()` and `HOST_COMMANDS`, the one visible list of things that are not
  records, so the claim "the registry is the catalogue" is testable.
- `hubreg/__main__.py`: `describe [--kind]`, `call <kind> <action> key=value ... [--confirm]`, `help [kind [action]]`,
  `context [--kind]`, `walk`; values parsed with the declared types; result as JSON on stdout, refusal as JSON with
  exit 1, warnings on stderr, `RecordError` with exit 2.
- `hubreg/__init__.py` exporting `Registry`, `RecordError`, `Refusal`, `Call`, `Warning`, `demo_records`,
  `demo_registry`.

### Why
- Note 9: keep the parts that cannot be records in one visible list with a test; note 11: the door's confirmation
  must be visible to the tool schema, the help and the context line, which all ask `needs_confirm_record`.
- The demo redirects (`set_temp` → `set_temperature`, `brightness` → `dim`, `temp` → `target`, `name` → `scene`) are
  the chapter's "observed near-misses", declared in the records so the refusal can name the intended call.

### What worked
- `python3 -m hubreg walk` prints `[]`, so the demo catalogue is self-consistent.
- `python3 -m hubreg call thermostat set_temperature temp=40` answers with the intended call
  `set_temperature(target=16)` and exit 1.

### What didn't work
- My first `python3 -m hubreg describe` was fine, but `help light dim` printed the unit twice
  (`number from 0 to 100%, usual 10 to 90% in %`); the duplication came from `_arg_help`.

### What I learned
- TASK.md says "a security action the host requires confirmation for" — the demo therefore demonstrates *host
  policy*, and the record's own flag is a second, independent source, which is exactly the combination note 11 asks
  for ("host policy may raise a flag; a record cannot lower it").

### What was tricky to build
- `parse_arguments` has to look a spec up before the binder sees the value, but an unknown key must still reach the
  binder so the diagnoser can offer the redirect; the CLI passes the raw text for unknown keys and lets `bind`
  refuse.

### What warrants a second pair of eyes
- The CLI exits 1 on a refusal and prints the refusal JSON to stdout. A caller might prefer refusals on stderr;
  stdout keeps both cases parseable with the same code.

### What should be done in the future
- A real hub would register plug-ins discovered from disk; `Registry.register` plus `finalize()` is already the
  contract they need.

### Code review instructions
- `hubreg/demo.py` and `hubreg/__main__.py`; try `python3 -m hubreg describe`, `... call door lock_door`,
  `... call door lock_door --confirm`, `... help scene run_scene`.

## Step 9: The test suite, and the five failures it found

I wrote tests under `tests/` for registration, binding, running, the consumers, the walker, the types, the demo
actions, the result check and the CLI, and ran `python3 -m unittest discover -s tests` repeatedly.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Test the interface TASK.md specifies plus the chapter's invariants; run the suite and
fix what fails before finishing.

**Inferred user intent:** Evidence, not claims: the final message must say how many tests were written and the last
result.

### What I did
- `tests/support.py` (record/spec builders, `refusal`, `record_error` helpers) and eight test modules:
  `test_registration.py`, `test_bind.py`, `test_run.py`, `test_consumers.py`, `test_walk.py`, `test_types.py`,
  `test_demo.py`, `test_cli.py` (subprocess), later `test_result.py`.

### Why
- Each module mirrors one participant, so a reviewer can see which invariant each test protects; the CLI tests run
  the real command as a subprocess because TASK.md specifies the command line as part of the interface.

### What worked
- 180 tests, `OK`, in about 0.7 s.

### What didn't work
- **1.** `test_a_plain_string_from_a_hook_is_a_refusal` errored with
  `hubreg.errors.RecordError: E_BAD_RECORD: sample 0 does not bind: these two do not fit` — the hook refused the
  record's own sample, and `finalize()` refused the record. Correct behaviour, wrong test: I made the hook refuse
  only when `low > high`.
- **2.** The same test then failed with `AssertionError: expected a Refusal, none was raised`, because I still bound
  `low=2, high=8`. Bound `low=8, high=2`.
- **3.** `test_a_sample_that_stops_binding_is_reported` errored with
  `hubreg.errors.RecordError: E_BAD_RECORD: sample 0 does not bind: dim: level must be a number, got str bright; for
  example dim(level=1)`. I had mutated the stored record *before* the first `finalize()`, so the cross-record check
  (not the walker) caught it. Fixed by finalizing in `setUp` before tampering.
- **4.** `test_a_softened_limit_is_reported` failed with `AssertionError: False is not true : []`: after deleting
  `min` from the stored spec the walker reported nothing, because it generates probes *from the record* and a record
  that never declared a minimum produces no below-minimum probe. The test premise was wrong; I replaced it with a
  type that ignores its limits (`class LooseNumber(Number): check -> None` registered with `add_type`), which the
  walker does catch ("below its minimum: was accepted but should have been refused (E_ARG_RANGE)").
- **5.** `test_the_describers_say_the_fields_vary` failed with
  `AssertionError: 'depend on the arguments' not found in 'device.measure(detail)\nreturns: fields that depend on the
  bound arguments...'` — the help says "bound", the context line does not; I corrected the assertion.

### What I learned
- Registration-time checks and walk-time checks overlap but are not the same: anything about a *single* record is
  caught at registration, so the walker's job is the probes (behaviour against the declaration) — that is the
  chapter's "the walker proves less than it seems".

### What was tricky to build
- Tampering tests needed a finalized registry, otherwise the very checks under test fire earlier than the assertion
  expects.

### What warrants a second pair of eyes
- The CLI tests depend on `cwd=ROOT` and `sys.executable`; they are the slowest tests (about 0.6 s of the 0.7 s
  total) but they are the only place the command line is exercised.

### What should be done in the future
- Add a test that runs `python3 -m hubreg walk` against a deliberately broken plug-in module, to show the command
  line's non-zero exit for problems.

### Code review instructions
- Start with `tests/test_registration.py` and `tests/test_bind.py`; run `python3 -m unittest discover -s tests -v`.

## Step 10: A consistency pass — what the consumers must agree on

I re-read every module asking one question per line: "which consumer would disagree, and is that disagreement
caught?" The pass tightened three things and closed two gaps.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** The chapter's promise is "checking, help and refusals agree by construction"; a
consistency pass is what proves the promise rather than asserting it.

**Inferred user intent:** No second source of truth anywhere, including in small places like a unit printed twice or
a result field nobody declares.

### What I did
- Callable `fields`: the chapter's `fields(boundArgs)`. `check_result` already accepted a callable, `describer`
  now has `field_names(record)` and renders "fields depend on the bound arguments" for the help and the context
  line, and `Registry.run` turns a `fields()` that raises into `E_RESULT` (the record's fault).
- `Registry.walk` now starts with `walker.catalogue_problems(reg)`: one tool description per registered action, no
  duplicate tool names — checks that span the catalogue rather than one record.
- The walk also reports a record that ran *without* the confirmation the registry says it needs.
- `_check_record` now requires a non-empty `doc` and a `fields` key: a record that cannot be described or whose
  result cannot be checked is refused at registration, as the chapter refuses "a record with no result kind".
- Wording: `characters(count)` singularises ("at least 1 character"), and the usual-range warning no longer repeats
  the type's whole phrase (`target=30 is outside the usual range 16 to 24 °C; most rooms...`).
- Removed dead code found on the way (`_NOT_GIVEN`, `ENUM_LIKE`, `_unit_note`, an unused `bits` list).

### Why
- Note 1: registration must check "a record with no result kind"; note 11: the describer and the runner must ask the
  registry the same question; note 5: the result check is one function shared by `run` and the walker.

### What worked
- `python3 -m unittest discover -s tests` stayed green through the pass (180 tests), and `python3 -m hubreg walk`
  still prints `[]`.

### What didn't work
- Adding the `doc`/`fields` requirements broke nothing in the suite, but it is the one place where I chose
  strictness over leniency: both keys are in TASK.md's record, so a record without them is malformed rather than
  minimal. A plug-in author gets a precise message instead of a `degraded` rendering.

### What I learned
- The riskiest leniency was `fields` defaulting to `[]`: it would have made a result return check "must be empty",
  which fails at run time with a message about the plug-in. Refusing at registration is clearer.

### What was tricky to build
- Making "fields depend on the arguments" render in *all* describers without any of them calling the record's
  `fields()` (there are no bound arguments at description time). `field_names` returns None for the callable case
  and every renderer has one branch for it.

### What warrants a second pair of eyes
- `Registry.record_for` deliberately does not finalize, and the CLI's `parse_arguments` uses it before `bind`
  finalizes. A caller who uses `record_for` alone can see a record before the cross-record checks; that is why it is
  documented as "does not finalize" and the public `get` refuses unknown actions.

### What should be done in the future
- `catalogue_problems` is the natural home for further cross-record checks (for example "every unit used is known
  to the app's control set").

### Code review instructions
- Diff-by-eye: `hubreg/result.py`, `describer.field_names`, `walker.catalogue_problems`, and the `_check_record`
  doc/fields rules. Then rerun the suite.

## Step 11: Matching the demo plug-ins to TASK.md exactly

While reading TASK.md once more against `hubreg/demo.py` I found that I had added an argument TASK.md does not
document: `light.dim` had a `fade` bool and a usual range of 10–90%. Both are plausible for a hub, but TASK.md lists
the demo actions' arguments exactly, and an extra argument changes the app's controls, the tool schema's properties
and the warnings an assistant sees.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** The demo plug-ins must be the four actions TASK.md names, with the documented arguments
and result fields; extra arguments belong in tests, not in the deliverable.

**Inferred user intent:** Anything another program is tested against must match the specification exactly.

### What I did
- Removed the `fade` argument and the `level` usual range from `LIGHT_DIM`, and its third sample became
  `{"level": 100}`. The record redirects (`set_level`, `brightness` → `dim`) stayed: they never change an accepted
  call, they only improve a refusal.
- Updated `tests/test_consumers.py`, `tests/test_cli.py` and `tests/test_demo.py`, and added
  `test_the_demo_declares_only_the_documented_arguments`.

### Why
- TASK.md is the interface other code is tested against; the chapter's pattern is about one source of truth, and the
  specification of the demo catalogue is that source for the demo.

### What worked
- `python3 -m unittest discover -s tests` → `Ran 181 tests`, `OK`; `python3 -m hubreg walk` → `[]`.

### What didn't work
- Two CLI tests failed with `AssertionError: 'light.dim(level, fade)' not found in "light.dim(level)\nreturns:
  {level}..."` and `'dim(level, fade)' not found in 'dim(level) -> {level}: ...'` — exactly the drift the chapter
  warns about, caught by the help text. Both assertions were updated to `level` only.

### What I learned
- The bool type and the optional-without-default case are now demonstrated only by the tests; that is the right
  trade, because the demo catalogue is specified by TASK.md while the type system is specified by the chapter.

### What was tricky to build
- Deciding which additions are safe. Redirects, docs and usual hints only appear in refusals and help; arguments,
  fields and flags are part of the call contract and must match the specification.

### What warrants a second pair of eyes
- `door.lock_door` carries both the host policy (in `demo_registry`) and the record's own `confirm` flag. TASK.md
  says "the host requires confirmation"; keeping both means the demo stays confirmed even if someone builds a
  `Registry()` by hand, which I judge desirable for a security action.

### What should be done in the future
- If a richer demo is wanted (bools, hooks, a value-dependent result), add it as a fifth plug-in rather than by
  changing the four documented ones.

### Code review instructions
- `hubreg/demo.py` against TASK.md's "Demo plug-ins to include" list, then the three updated test modules.

## Step 12: Final check

I ran the whole suite, the walk and the command line one last time, and read the diary back for completeness.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Confirm the deliverable: tests pass, `walk()` is empty, the CLI works, the diary has
one step per phase, and the final message follows TASK.md's JSON format.

**Inferred user intent:** A finished, verified piece of work.

### What I did
- `python3 -m unittest discover -s tests` → `Ran 181 tests`, `OK`.
- `python3 -m hubreg walk` → `[]` (exit 0).
- `python3 -m hubreg describe` → four tool descriptions (`door.lock_door`, `light.dim`, `scene.run_scene`,
  `thermostat.set_temperature`).
- `python3 -m hubreg call ...` for success, near-miss, out-of-range, warning, missing argument, unknown action and
  confirmation.

### Why
- TASK.md requires the tests to be run and fixed before finishing, and the diary to be complete.

### What worked
- Everything above; about 3 900 lines of code and tests in total, standard library only (`json`, `argparse`, `difflib`,
  `subprocess` for the CLI tests).

### What didn't work
- No remaining failures. The only failing things in this work are recorded in Steps 9 and 10.

### What I learned
- The chapter's structure table mapped cleanly onto files; the two participants I did not build (`expand` for
  composite actions and positional arguments) are the two whose absence is visible in this build.

### What was tricky to build
- Nothing at the end; the end state is the result of the fixes above.

### What warrants a second pair of eyes
- `Registry.run` raises `RecordError` (not `Refusal`) when a plug-in's action raises or returns the wrong fields: a
  hub operator sees a plug-in fault, not a caller refusal. Confirm that is the intended split for the mobile app.

### What should be done in the future
- Composite actions (`expand`), positional arguments with `ARG_DUPLICATE`, and a plug-in discovery loop are the
  three obvious next steps; none of them changes the consumers.

### Code review instructions
- `python3 -m unittest discover -s tests`, then `python3 -m hubreg walk`, then read `hubreg/registry.py` outward.

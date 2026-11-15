# Diary

## Goal

Build `labelbook`, a Python-3 standard-library ledger for labels proposed by people, agents and detectors, applying
the Lineage Ledger pattern of `CHAPTER.md`: every label stamped with provenance, every decision an appended event
folded into current state, lineage queries both ways (what made this, what did this make), and stamped exports.
This diary records each phase, including failures with their exact commands and error text.

## Step 1: Reading the chapter, the task and the diary format

I read `CHAPTER.md`, `TASK.md` and `DIARY-FORMAT.md` completely before touching code, then sketched the module layout
against the chapter's participant table. The hard constraints from `TASK.md` are the exact public interface of
`Ledger` plus file-based persistence under one directory; everything else is mine to shape. The chapter's "Sketch"
and its eleven implementation notes supplied the shape: a required provenance value, one stamper, a schema file beside
the data, one maker matcher, append-only decision events with a sequence number, and one fold that owns the status
vocabulary.

### Prompt Context

**User prompt (verbatim):** "You are a software engineer joining a project. Your working directory contains three files:
- CHAPTER.md: a chapter of a design-pattern book describing the pattern you must apply;
- TASK.md: the software to build, with its required public interface;
- DIARY-FORMAT.md: how to keep your work diary.
Read all three completely first. Keep DIARY.md as you go, one step per phase of work, in that format. Then design, build and test the software in this directory. Work only inside this
directory (do not read or write outside it). Use only the Python 3 standard library. Run your tests and fix what
fails before you finish, and make sure DIARY.md is complete. Your final message must follow the output format at the end of TASK.md."

**Assistant interpretation:** Implement the `labelbook` package exactly to the interface in `TASK.md`, using the
Lineage Ledger pattern from `CHAPTER.md`, with tests under `tests/`, a phase-by-phase diary, and a final JSON summary
in the format given at the end of `TASK.md`.

**Inferred user intent:** A reviewer wants to see whether the chapter actually transfers to code: does the build
stamp provenance on every creating path, keep decisions append-only and fold them once, match makers in one place,
survive several writers, write the schema beside the data, and bind exports to their content.

### What I did
- Read all three files in full (`CHAPTER.md` 11 sections incl. the sketch and notes 1-11).
- Listed the directory: only the three inputs were present.
- Planned seven modules: `errors`, `schema`, `storage`, `provenance`, `events`, `fold`, `ledger`, plus `__init__`.

### Why
- The chapter's participant table (Provenance record, Stamper, Schema, Lineage queries, Decision event, Decision log,
  Fold, Locked append) maps one-to-one onto modules, so each participant has one home and reviewers can find it.
- `TASK.md` demands JSON-lines files under one directory; that decides the storage layer and makes persistence a
  matter of re-reading, not caching.

### What worked
- The chapter's sketch is close enough to Python to transcribe: `Provenance`, `Artefact`, `Event`, `ItemState`,
  `fold`, `matches`, `sourceOf`, `madeBy`, `acceptance`, `export`.

### What didn't work
- Nothing yet in this phase.

### What I learned
- The chapter is explicit that the two halves (stamping, decision log) are separable, but `TASK.md` needs both, so
  the build keeps the decision log as a first-class module rather than an option.

### What was tricky to build
- Deciding how to meet both "`inputs` is a list of file paths" (TASK.md) and "record a content hash" (note 11)
  without guessing which the hidden tests check. I resolved it during design: an `Input` value that *is* the path
  string (so it compares equal to a plain path and serialises as one) while also carrying `sha256`, `exists`, `size`
  and `mtime` as attributes and via `entry["sha256"]`.

### What warrants a second pair of eyes
- The `Input` str-subclass is a deliberate compatibility trick; a reviewer should confirm it does not surprise
  anyone reading `source_of` output.

### What should be done in the future
- Build the storage layer first, because both stamping and the log depend on it.

### Code review instructions
- Start with `CHAPTER.md` "Structure" and "Sketch", then compare with the planned module list.

## Step 2: Building the provenance core, schema, storage, fold and facade

I built the whole library in one pass, bottom-up: storage primitives, schema, provenance and matcher, events, fold,
then the `Ledger` facade and package exports. A smoke script exercised add/decide/state/source_of/made_by/acceptance/
export/audit and a second `Ledger` on the same directory, and everything came back as intended on the first run.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Write the modules so each chapter participant is one clearly named place, with the
public interface from `TASK.md` on `Ledger`.

**Inferred user intent:** Working code now, reviewed for pattern fidelity later.

### What I did
- `labelbook/errors.py`: `LedgerError(ValueError)` plus refusals with `hints` (`UnknownMakerKind`, `UnknownDecision`,
  `MissingActor`, `MissingNewLabel`, `UnknownLabel`, `NotSerializable`).
- `labelbook/schema.py`: `FOLD_VERSION`, `CODE_VERSION`, `MAKER_KINDS`, `DECISIONS`, `STATUS_OF`, `DECIDED`,
  `ACCEPTING`, and the `SCHEMA` dict with field definitions and units.
- `labelbook/storage.py`: `now_iso`, `describe_input` (sha256 + size + mtime), `atomic_write` (temp + fsync +
  `os.replace`), `read_jsonl` with problems, `append_jsonl_locked` (single `os.write` on `O_APPEND` under `flock`,
  record built inside the lock), `next_seq`.
- `labelbook/provenance.py`: `Input`, `Provenance` (required kind/maker/inputs/version/time), `stamp()`, `matches()`
  as the only reader of maker fields.
- `labelbook/events.py`: `Event` with `seq`, `check_decision`, `check_actor`.
- `labelbook/fold.py`: `Artefact`, `ItemState`/`LiveDecision`, `Problem`, `fold()` transcribed from the sketch,
  `status_counts`, `acceptance_share`.
- `labelbook/ledger.py`: `Ledger` with schema-on-open, `add_label`, `decide`, `state`, `source_of`, `made_by`,
  `acceptance`, `acceptance_report`, `unstamped`, `audit`, `export`, `verify_export`, plus `read_export`.
- `labelbook/__init__.py`: the required exports plus the pattern's values and helpers.
- Ran a smoke script creating labels, deciding, exporting and reopening; output matched expectations.

### Why
- Note 1: `Artefact` has no constructor without provenance; `add_label` is the only label-creating path and it
  stamps; `export` is a creating path too and stamps a sidecar.
- Note 3: `undo` marks the latest live decision undone, order comes from `seq` allocated inside the lock, never clocks.
- Note 5: one `fold` owns `STATUS_OF`, `DECIDED`, `ACCEPTING`; unknown decisions become `Problem`s, not rejections.
- Note 6: `made_by`, `acceptance` and the export's `exclude` all go through `matches`.
- Note 7: random `uuid4` ids, and `seq` computed from the highest `seq` *inside* `flock`.
- Note 9: `schema.json` is written atomically on first open and creation checks `makerKinds` against the file.
- Note 10: the export sidecar carries `contentHash`, `carries` (label ids and their makers) and `foldVersion`.

### What worked
- Smoke run: `add_label` → `state` pending; `source_of` showed kind/maker/hash/time; `inputs` compared equal to the
  plain path list while `inputs[0]["sha256"]` gave the hash; `made_by(kind="detector", model="spck")` matched;
  `acceptance("kind")` returned `{'detector': 1.0, 'person': 0.0}`; the export held only the accepted row and
  `verify_export` returned `stamped: True` with matching hashes; reopening the directory gave equal state.

### What didn't work
- One self-caught bug before running: `decide` first validated the decision against the module-level `DECISIONS` and
  then tried to re-raise with the schema's list, which would have raised nothing. I replaced that branch with a
  direct `UnknownDecision(..., self.decisions)`. No test had been run yet, so no command output to quote.

### What I learned
- The chapter's sketch transcribes almost line for line if the values are dataclasses; the only real invention
  needed was `Input` and the export sidecar's `carries`.
- `TASK.md` says nothing about refusing unknown maker kinds or labels; I chose to refuse with `ValueError`
  subclasses because note 2 and note 5 warn that silent drops make later queries miscount.

### What was tricky to build
- Locked append: `flock` alone is enough between processes, but reading and writing on the same descriptor requires
  `lseek(0)` for the read while `O_APPEND` still puts the write at the end. I also hold a module-level
  `threading.RLock` so threads in one process serialise before touching the descriptor, and the "next seq" is
  computed from the records read under the lock.

### What warrants a second pair of eyes
- `acceptance()` omits maker values that have no decided labels (a share of nothing is not a number); confirm the
  intended semantics against `TASK.md` wording.
- `state()` returns exactly the three keys `TASK.md` names, so equality assertions hold; richer data lives in
  `fold_state()`.

### What should be done in the future
- Write the test suite: interface, undo laws, reference-model comparison on random sequences, unknown decision
  reporting, persistence, concurrency, export stamping.

### Code review instructions
- Read `labelbook/fold.py` first (the laws live there), then `labelbook/ledger.py` (`add_label`, `decide`,
  `acceptance`, `export`) and `labelbook/provenance.py` (`matches`). Run the smoke path with
  `python3 -c "import labelbook"` and then the tests once written.

## Step 3: First run of the interface test suite (one failure)

I wrote `tests/test_labelbook.py` (42 tests) covering the `TASK.md` contract: adding labels, refusals, the four
decisions, the label in force, `state`, `source_of`, `made_by`, `acceptance`, export rows and sidecar, persistence and
the schema file. I ran the suite and one test failed: my schema assertion looked for the word "definition" among the
field definitions, but the schema stored each field as a bare `(definition, unit)` tuple, so the word never appeared.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Encode every promise of `TASK.md` as an executable check, including the parts the task
states only in prose (statuses, export content, persistence).

**Inferred user intent:** Confidence that the public interface behaves as documented before adding pattern-law tests.

### What I did
- Created `tests/test_labelbook.py` with `TestAddingLabels`, `TestDeciding`, `TestStateQueries`, `TestLineage`,
  `TestAcceptance`, `TestExport`, `TestPersistenceAndSchema`.
- Ran `python3 -m unittest discover -s tests -v`.

### Why
- Note 1 ("make stamping impossible to forget", "count unknowns") and note 9 ("enforce each list of allowed values at
  creation") are only visible through tests of refusals, so the suite asserts the error messages name the allowed
  kinds and decisions.
- The chapter's motivation (81 %, 47 %, 20 % acceptance by band) became a test that builds exactly those bands.

### What worked
- 41 of 42 tests passed on the first run, including hashing of inputs, exclusion of a faulty source from an export,
  and sidecar tamper detection.

### What didn't work
- `python3 -m unittest discover -s tests -v` reported:

```
FAIL: test_the_schema_is_written_beside_the_data (test_labelbook.TestPersistenceAndSchema)
...
AssertionError: 'definition' not found in '{"event.actor": ["who decided; a pseudonymous id or role if policy forbids names", "actor id"], ...}'
```

### What I learned
- The schema was data-shaped enough to test but not self-describing: a reader had to know positionally which element
  was the definition and which the unit. Note 2 in the chapter ("definitions and units of stored fields") argues for
  naming them.

### What was tricky to build
- Deciding what `acceptance()` should do for a maker value that has no decided labels. A share of nothing is not a
  number, so those values are omitted; the test `test_pending_labels_are_not_decided` pins that choice down.

### What warrants a second pair of eyes
- Whether omitting undecided sources from `acceptance()` is the semantics a reviewer expects from `TASK.md`.

### What should be done in the future
- Make the schema fields self-describing, then add the pattern-law suite.

### Code review instructions
- Run `python3 -m unittest discover -s tests -v`; the failing test is the schema one at the end of
  `tests/test_labelbook.py`.

## Step 4: Fixing the schema to carry named definitions and units

I changed `labelbook/schema.py` so each field is an object with named `definition` and `unit` keys, generated from one
`_FIELD_DEFINITIONS` table, and added the export fields (`export.contentHash`, `export.carries`) that the sidecar
actually writes. The failing test then passed and the whole interface suite was green.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Fix the schema shape rather than weaken the test, because the test encoded a real
requirement from the chapter.

**Inferred user intent:** A schema another tool can read without positional guessing.

### What I did
- Edited `labelbook/schema.py`: `_FIELD_DEFINITIONS` holds `(definition, unit)` pairs; `SCHEMA["fields"]` is built as
  `{name: {"definition": ..., "unit": ...}}`; added the two export fields.
- Re-ran `python3 -m unittest discover -s tests`: 42 tests, OK.

### Why
- Note 9: "Write the schema beside the data ... Fields, units, definitions, allowed values". Named keys make the file
  readable by another tool (the same reason `contentHash` is a named key in the sidecar).

### What worked
- `json.dumps(SCHEMA["fields"]["label"])` gives `{"definition": "the label in force: ...", "unit": "label"}` and the
  full suite passed.

### What didn't work
- Nothing after the change.

### What I learned
- Keeping the field table in one place means the schema file and the in-code defaults cannot drift; `_read_schema`
  merges a file written by another tool over the defaults without dropping `fields`.

### What was tricky to build
- Nothing beyond the mechanical rewrite; the risk was leaving stale tuple references in the tests, which the rerun
  ruled out.

### What warrants a second pair of eyes
- Whether the extra `export.*` fields belong in the same `fields` map or in a separate section; I kept one map for
  simplicity.

### What should be done in the future
- Add the pattern-law tests: undo laws, reference-model comparison, unknown decisions, legacy records, concurrency.

### Code review instructions
- `labelbook/schema.py` top-to-bottom; then `python3 -m unittest discover -s tests`.

## Step 5: Pattern-law suite and several-writer stress

I wrote `tests/test_pattern.py` (21 tests) that pin the chapter's laws rather than the interface: correct-then-accept
keeps the correction, undoing a correction restores the previous one, accept/reject/undo leaves the label accepted,
undo with nothing to undo is reported, a random-sequence comparison against an independent reference model, order by
`seq` even when the file order differs, unknown decisions and orphan events reported not guessed, legacy unstamped
records counted, one matcher for ensembles, versioned derived numbers, and eight threads plus four processes writing
one log. All 63 tests passed, and a separate stress run with four processes writing 200 labels each kept all 800
labels and 800 distinct sequence numbers.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Test the invariants the chapter says construction builds broke (note 4: four of five
builds broke the first law; note 7: `max + 1` ids lost a third of 400 labels).

**Inferred user intent:** Evidence that this build did not fall into those traps.

### What I did
- Created `tests/test_pattern.py`: `TestFoldLaws`, `TestUnknownsAreReported`, `TestMatcher`, `TestSeveralWriters`,
  `TestDerivedNumbersAreVersioned`, plus a `ReferenceModel` class that replays decisions independently.
- Ran `python3 -m unittest discover -s tests -v`: 63 tests, OK.
- Ran a stress script (four forked processes, 200 labels and 200 decisions each) and inspected the result.

### Why
- Note 4 demands "test it as laws ... against a small reference model on random sequences".
- Note 3: undo pops the latest live decision, and order comes from a sequence number, so a test writes the events in
  the wrong file order on purpose.
- Note 5: unknown decisions are reported, never folded as rejections; the test asserts the label stays `pending` and
  does not appear in `acceptance()`.
- Note 7: ids are random and `seq` is allocated inside `flock`, so concurrent writers must not collide.

### What worked
- All 63 tests passed on the first run of the new file.
- Stress run output:

```
counts [200, 200, 200, 200]
labels 800 unique seqs 800 max seq 800
all accepted True
problems []
```

### What didn't work
- Nothing in this step; the one earlier failure was fixed in Step 4.

### What I learned
- The fold is easiest to test when it is a pure function over `(artefacts, events)`; the `Ledger` only feeds it from
  files, which made the reference-model comparison direct.
- The thread test passes partly because of the module-level `RLock`; the process test is the real exercise of
  `flock`, and only the process test would catch a lock that is per-process rather than per-file.

### What was tricky to build
- The out-of-file-order test: writing `seq` 3, 1, 2 to the log and asserting the final status is `rejected` (reject
  at 1, accept at 2, undo at 3) proves the fold sorts by `seq`; a clock-ordered or file-ordered fold would report a
  "nothing to undo" problem instead.
- Random laws: the reference model stores decisions as mutable three-element lists and computes status and label from
  the live entries, a deliberately different formulation from the fold's `LiveDecision`/`ItemState` pair.

### What warrants a second pair of eyes
- The `Input` str-subclass and the `acceptance()` omission rule are the two places where `TASK.md` was ambiguous.
- `decide()` validates the label id before appending; the fold still reports orphan events written by other tools.

### What should be done in the future
- Consider a compaction/archive path if logs grow (chapter "Consequences"); not needed at this size.

### Code review instructions
- `tests/test_pattern.py` `TestFoldLaws` and `TestSeveralWriters`; validate with
  `python3 -m unittest discover -s tests -v`.

## Step 6: Housekeeping and the final check

I moved the tests' temporary ledgers inside this work directory (they had used the system temporary directory), removed
four now-unused imports from `ledger.py`, ran `compileall`, the full suite again, and an end-to-end smoke that
exercises a correction, an undo and a rejection over two sources and then exports. The export contained only the
accepted label and its sidecar verified.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Finish with a clean tree, everything passing, and the evidence captured in this diary.

**Inferred user intent:** A build a reviewer can run without surprises outside the working directory.

### What I did
- Tests now create their temp ledgers with `tempfile.TemporaryDirectory(dir=<tests dir>, prefix="_tmp-")`, so nothing
  is written outside the working directory; cleanup is automatic and `tests/` is clean after the run.
- Removed unused imports (`Input`, `PENDING`, `SCHEMA`, `STATUS_OF`) from `labelbook/ledger.py`; an AST scan over
  `labelbook/*.py` now reports no unused imports.
- Ran `python3 -m compileall -q labelbook tests` → `compileall ok`.
- Ran `python3 -m unittest discover -s tests` → `Ran 63 tests in 1.201s / OK`.
- Ran an end-to-end smoke inside `_smoke/` (removed afterwards): detector label accepted, agent label corrected then
  undone then rejected, export with a verifying sidecar, `audit()` reporting `unstamped: 0`, `problems: []`.

### Why
- The instructions say to work only inside this directory and to use only the standard library; keeping temp data
  inside honours the first, and the import scan keeps the second honest.
- Note 2 ("a path that forgets the stamp makes artefacts every query silently drops") is the reason `audit()` and
  `unstamped()` exist and are exercised at the end rather than left as decoration.

### What worked
- Everything above: 63 tests OK, clean compile, smoke output as expected:

```
verify True [{'item': 't1', 'label': 'dust'}]
audit {'foldVersion': 'labelbook-fold/1', 'artefacts': 2, ..., 'unstamped': 0, 'problems': []}
```

### What didn't work
- Nothing failed in this step.

### What I learned
- The chapter's warning that "every new creating path is a chance to forget" applied even here: `export` needed its
  own `stamp(...)` call and its own sidecar, and the smoke test is what proves it happens.

### What was tricky to build
- Nothing new; the remaining risk is semantic, not mechanical (see the two ambiguities below).

### What warrants a second pair of eyes
- `ledger.state()` returns exactly `{"item", "label", "status"}`; richer per-label state (decisions, origin) is only
  reachable through `fold_state()`, so a caller wanting history must use the latter or `events()`.
- `export(path)` writes a sidecar next to the file; a caller that asserts a directory listing will see one extra file.

### What should be done in the future
- An `archive()`/compaction step and an `import_legacy()` helper that stamps old rows with `kind: unknown` explicitly
  (the fold already treats missing provenance that way and `unstamped()` counts it).

### Code review instructions
- Run `python3 -m unittest discover -s tests` (63 tests). Read `labelbook/fold.py`, `labelbook/ledger.py`,
  `labelbook/provenance.py` in that order, then `tests/test_pattern.py`. DIARY.md records the one mid-build failure
  in Step 3.

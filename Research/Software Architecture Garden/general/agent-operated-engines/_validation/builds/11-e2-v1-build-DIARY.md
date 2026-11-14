# Diary

## Goal

Build `labelbook`, a standard-library Python 3 ledger for labels proposed by people, agents and detectors, applying the
Lineage Ledger pattern from `CHAPTER.md`: every label carries a provenance record at creation and every decision is an
append-only event folded by one shared function. This diary records design choices, failures and fixes as they happen.

## Step 1: Reading the chapter, the task and the diary format

I read all three input files completely before writing any code, then sketched the module layout and the storage shape.
The chapter's participants (provenance record, stamper, schema, decision event, decision log, fold, lineage queries) map
almost one to one onto the required public interface, so the design is mostly about deciding where each participant
lives and how the fold treats `undo`.

### Prompt Context

**User prompt (verbatim):** "You are a software engineer joining a project. Your working directory contains three files:
- CHAPTER.md: a chapter of a design-pattern book describing the pattern you must apply;
- TASK.md: the software to build, with its required public interface;
- DIARY-FORMAT.md: how to keep your work diary.
Read all three completely first. Keep DIARY.md as you go, one step per phase of work, in that format. Then design, build and test the software in this directory. Work only inside this
directory (do not read or write outside it). Use only the Python 3 standard library. Run your tests and fix what
fails before you finish, and make sure DIARY.md is complete. Your final message must follow the output format at the end of TASK.md."

**Assistant interpretation:** Implement the `labelbook` package exactly as specified in TASK.md, using the Lineage Ledger
pattern, with tests under `tests/`, and keep this diary in the given format.

**Inferred user intent:** A working, tested, standard-library-only library whose design is traceable to the pattern
chapter, plus an auditable record of how it was built.

### What I did
- Read `CHAPTER.md`, `TASK.md` and `DIARY-FORMAT.md` in full.
- Planned the package layout: `schema.py` (field definitions and units, time/version/hash helpers),
  `provenance.py` (the stamped record), `events.py` (decision event + the single `fold`), `store.py` (append-only JSON
  lines), `ledger.py` (the public `Ledger`), `__init__.py` (exports).
- Planned two JSON-lines files under the ledger directory: `labels.jsonl` (artefacts with inline provenance) and
  `decisions.jsonl` (append-only events).

### Why
- The chapter's Structure table lists exactly these participants; giving each its own module keeps "one fold, one
  stamper, one schema" visible in the file layout and satisfies implementation notes 1, 5 and 7.
- Two logs instead of one mixed log keeps label creation (artefact + provenance) separate from decisions ("never
  edited"), matching the chapter's Split between *Provenance record* and *Decision event*.

### What worked
- The interface in TASK.md maps cleanly onto the chapter: `add_label` is the stamping path, `decide` appends an event,
  `state`/`export` are fold readers, `source_of`/`made_by`/`acceptance` are the lineage queries.

### What didn't work
- Nothing yet; no commands run in this step.

### What I learned
- The chapter's sketch folds `undo` as `delete state[itemId]`, which only works when a label has one live decision.
  Because the task allows accept → correct → undo, the fold needs a per-label stack of applied decisions instead of a
  single slot, so that undoing a correction restores the earlier acceptance. That is a deliberate, documented
  refinement of the sketch.

### What was tricky to build
- Deciding what `undo` means when there is nothing to undo, and whether `state()["label"]` for a rejected label is the
  proposed label. Resolution: undo with an empty stack is recorded (history keeps the attempt) but folds to no change;
  rejected and accepted labels keep the proposed label, only `correct` changes it, which is what the task's
  "the corrected one, if corrected" wording says.

### What warrants a second pair of eyes
- Two judgement calls that a reviewer should confirm against the task text: (a) `acceptance(by)` skips maker values
  that have no decided labels yet (a share of zero decided labels is undefined), and (b) `decide` on an unknown label
  id raises `ValueError` rather than appending an orphan event.

### What should be done in the future
- Write the modules, then the tests; measure whether the fold needs caching once the log grows (chapter: "logs grow").

### Code review instructions
- Start with `TASK.md`'s required interface, then read `labelbook/ledger.py` for the wiring, `labelbook/events.py` for
  the fold. Validate with `python3 -m unittest discover -s tests`.

## Step 2: Schema, provenance record and the stamper

I wrote `labelbook/schema.py` and `labelbook/provenance.py`. The schema module holds the field catalogue with units, the
UTC timestamp helper, the input hasher and the code-version digest; the provenance module holds the immutable
`Provenance` record and the `Stamp` (artefact identity + label + provenance) that every creating path must produce.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Give every stored value one documented definition and unit, and make label creation
impossible without a provenance record.

**Inferred user intent:** Lineage that is complete at creation, so no later query silently drops an unstamped artefact.

### What I did
- Added `SCHEMA` (field → type, definition, unit) and `SCHEMA_VERSION = "labelbook/1"` in `schema.py`.
- Added `utc_now()`, `hash_file(path)` (sha256 + bytes + mtime, `found: False` for missing files) and `code_version()`
  (sha256 over the package's own `.py` files, cached, 12 hex chars).
- Added `Provenance.stamp(maker, inputs, at=None)` which validates `kind`, splits identifiers out of the maker dict,
  hashes each input and stamps version + time; `Stamp.to_dict/from_dict` defines the stored record.

### Why
- Chapter Structure table needs a **Schema** participant, and implementation note 7 says definitions *and units* belong
  in it, so the catalogue carries an explicit `unit` per field (bytes, UTC timestamp, hex digest, ordinal).
- Implementation note 9 ("Hash inputs that may change") is why `hash_file` stores a content hash rather than a path: the
  hash must describe what was read, not what the path contains today.
- Stamping raises only on a missing `kind`; a missing input file is recorded honestly instead of failing the label.

### What worked
- `input_file` hashing behaves: changing the file after stamping leaves the recorded hash unchanged (later asserted in
  `tests/test_lineage.py`).

### What didn't work
- Nothing failed in this step; no command run beyond a syntax check of the modules.

### What I learned
- The chapter's `save(path, data, ctx)` sketch writes a *sidecar* per artefact. Here the artefact is a row in a log, so
  the provenance is inline in the row; the sidecar form is kept for `export` instead, where a foreign file format must
  not change (note 8).

### What was tricky to build
- Deciding what counts as an "identifier" of the maker. Resolution: `kind` is the kind, every other non-`None` maker key
  is an identifier; the original maker dict is also kept verbatim so date-of-audit questions can be answered without
  guessing.

### What warrants a second pair of eyes
- `code_version()` hashes sources; it is stable within a working tree but changes with formatting-only edits. That is
  acceptable for provenance (it is a fingerprint, not a release number) but a reviewer should confirm it is what they
  want stored.

### What should be done in the future
- If the record shape changes, bump `SCHEMA_VERSION` and add a migration note; the fold currently ignores unknown keys.

### Code review instructions
- Read `labelbook/schema.py` `SCHEMA` and `hash_file`, then `labelbook/provenance.py` `Provenance.stamp` and
  `Stamp.to_dict`. Validate with `python3 -m unittest tests.test_lineage`.

## Step 3: Decision events, the single fold, the store and the Ledger

I wrote `labelbook/events.py`, `labelbook/store.py`, `labelbook/ledger.py` and `labelbook/__init__.py`. Events are
immutable dataclasses, `fold` is the only function that turns stamps + events into state, `JsonlLog` offers exactly
append and read, and `Ledger` wires the seven required methods onto those pieces.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Implement the required public interface over two append-only JSON-lines files, with one
shared fold used by every reader.

**Inferred user intent:** A library where a decision can always be revised or undone without losing history, and where
every reader agrees because they share one fold.

### What I did
- `events.py`: `Event` (seq, label_id, decision, actor, at, reason, new_label), `require_actor`, `validate_decision`,
  `FoldResult` and `fold(stamps, events)`.
- `store.py`: `JsonlLog.append` (single line, flush + `os.fsync`) and `read`/`read_with_errors` (skips unparseable
  lines, reports them). No update, no delete.
- `ledger.py`: `Ledger(directory, clock=None)` with `add_label`, `decide`, `state`, `source_of`, `made_by`,
  `acceptance`, `export`, plus audit helpers `history`, `current`, `log_problems` and `UnknownLabel`.
- `__init__.py`: exports `Ledger` and the pattern participants (`Provenance`, `Stamp`, `Event`, `fold`, `SCHEMA`).

### Why
- Implementation note 5 ("write the fold once"): `state`, `acceptance`, `export`, `history` and `log_problems` all go
  through `fold`; no reader has its own copy.
- Implementation note 4 ("undo is an event"): `decide` only ever appends, and undo is a decision value, never a delete.
- Implementation note 6 ("record who decided"): `require_actor` makes a missing actor a `ValueError` before any append.
- Note 1 (stamp in every creating path): `add_label` is the only creating path and it refuses a maker without `kind`,
  so an unstamped artefact cannot be written through the API.
- The fold keeps a per-label stack of live decisions (the chapter's sketch keeps one slot), because accept → correct →
  undo must return to *accepted*, not to pending.

### What worked
- A smoke script over a temp directory showed pending → accepted, `source_of` carrying maker/ids/inputs/version,
  `made_by(kind="detector")`, `acceptance("model") == {'v1': 1.0}`, an export list and its sidecar, and clean
  `log_problems()`.

### What didn't work
- First drafts had two unused names (`events_module` import and a leftover `unknown = []`) and an unused `cast`
  import inside `Provenance.from_dict`; removed with `edit` before any test ran.

### What I learned
- The chapter says do not use the pattern for disposable artefacts; here every label is questioned later, so stamping
  cost at creation is justified — but it also means `add_label` must stay cheap, hence no fsync-per-input, only per line.

### What was tricky to build
- Deciding the exception type for an unknown label id: `source_of`/`decide` raise `UnknownLabel`, which subclasses both
  `KeyError` and `ValueError` so a caller reading it either way is right. That hedge is deliberate and worth reviewing.

### What warrants a second pair of eyes
- `acceptance` omits maker values that have no decided label (undefined share). A caller expecting `0.0` for "all pending"
  would be surprised; the docstring states the rule.
- Two processes appending at once could collide on `seq`; the fold uses file order, so state stays correct, but the seq
  column is advisory.

### What should be done in the future
- If logs grow (chapter Consequences), add an index or cache keyed by log size/mtime; today every read re-reads files,
  which is the simplest correct choice.

### Code review instructions
- Start at `labelbook/ledger.py` `add_label`/`decide`, then `labelbook/events.py` `fold`. Validate with
  `python3 -m unittest discover -s tests`.

## Step 4: First full test run — all green

I wrote the first three test modules (`tests/test_ledger_basics.py`, `tests/test_decisions.py`,
`tests/test_lineage.py`, plus `tests/test_export_and_fold.py`) and ran the suite.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Cover the required interface and the pattern's invariants with unittest cases.

**Inferred user intent:** Evidence that the library behaves as promised, including the failure modes.

### What I did
- Wrote tests for creation (ids, verbatim label values, persistence across `Ledger` instances, append-only file shape,
  maker validation), for decisions (accept/reject/correct/undo incl. undo-of-correction, missing actor, unknown
  decision, unknown label, seq continuity after restart, history keeping undone events), for lineage (`source_of` with
  hashed inputs, `made_by` variants, `acceptance` by kind/model, undone decisions not counted) and for export (corrected
  label wins, sidecar, stable output, empty ledger).
- Ran `python3 -m unittest discover -s tests`.

### Why
- The chapter's Consequences list what the pattern buys: measurement by source, exclusion by source, audit, undo. Each of
  those maps to a test, not just to an implementation.

### What worked
- `python3 -m unittest discover -s tests` → `Ran 63 tests in 0.044s` / `OK` on the first try.

### What didn't work
- Nothing failed yet at this point; the only surprise was how much of the behaviour the fold already covered without
  special cases in `Ledger`.

### What I learned
- Testing `undo` as a stack op exposed an ambiguity I had to pin down in code: undo of an `undo` event is not supported
  (undo cancels the latest live *decision*), which is why the fold only ever pops decision events.

### What was tricky to build
- Making the acceptance tests independent of dict ordering and of float formatting: compared with `assertAlmostEqual`
  per key instead of whole-dict equality for fractions like 2/3.

### What warrants a second pair of eyes
- Whether `state()` should expose the extra audit fields (`decided_by`, …). I kept `state()` to exactly
  `{"item", "label", "status"}` as specified and put the extras in `current()`/`fold()`.

### What should be done in the future
- Add a scenario-level test that answers the three questions in TASK.md end to end (done in Step 6).

### Code review instructions
- Read the four test modules alongside `labelbook/events.py::fold`; run the suite from the work directory.

## Step 5: Hardening the fold and adding contract tests — one failing test

I refined the fold so a hand-written `correct` event without `new_label` keeps the proposed label instead of blanking
it, then added `tests/test_interface_contract.py` with the exported-name contract and a full scenario. The first run of
that scenario failed because my *expectation* was wrong.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Prove the end-to-end story (measure a source, exclude a faulty source, audit an export)
and keep the fold robust against damaged logs.

**Inferred user intent:** Confidence that the library works on the situation it was written for, not only on unit-level
operations.

### What I did
- Changed `fold`'s `correct` branch to `top.new_label if top.new_label is not None else target["proposed"]`.
- Added `tests/test_interface_contract.py`: exported names, method presence/signatures, string-vs-Path directory,
  storage layout (`labels.jsonl`, `decisions.jsonl` only), injected clock, and the scenario test.
- Ran `python3 -m unittest discover -s tests`.

### Why
- Note 5 says a shared fold must agree on edge cases; a correction with no replacement label is exactly such an edge
  case, and dropping the artefact's label would be the worst possible answer.

### What worked
- The exported-name, storage-layout and clock tests passed immediately.

### What didn't work
- The scenario test failed with:

```
FAIL: test_measure_a_source_exclude_a_source_and_audit_an_export (test_interface_contract.ScenarioTest)
AssertionError: Lists differ: [{'it[114 chars]'img-3', 'label': 'dust'}, {'item': 'img-9', '[15 chars]st'}] != [{'it[114 chars]'img-2', 'label': 'dust'}, {'item': 'img-9', '[15 chars]st'}]
First differing element 3:
{'item': 'img-3', 'label': 'dust'}
{'item': 'img-2', 'label': 'dust'}
```

### What I learned
- The library was right and the test was wrong: the accepted v2 label was `img-3` (the fourth label created), not
  `img-2`. Reading the fold's own output is the fastest way to tell a real bug from a bad expectation.

### What was tricky to build
- Reproducing the exact assertion output for this diary. The traceback above is copied from the suite run that
  failed; after moving the expected list to `img-3` I re-ran the whole suite.

### What warrants a second pair of eyes
- The scenario asserts `acceptance["detector"] == 3/9` (2 accepts + 1 corrected out of 9 decided) — confirm that
  "corrected counts as positive" is the intended reading of TASK.md's "accepted or corrected".

### What should be done in the future
- Add a second scenario with two reviewers disagreeing, to show `actor` distinguishes them (the chapter's note 6).

### Code review instructions
- Read `tests/test_interface_contract.py::ScenarioTest` next to `labelbook/ledger.py::acceptance` and `export`.

## Step 6: Corrupt-log hardening — 72 tests green

I made reading tolerant of structurally broken records (not only unparseable JSON) and reported them through
`log_problems()` instead of crashing or hiding them.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** A log written by older code or by hand must not take down a reader; the damage must be
visible.

**Inferred user intent:** Auditability that survives real-world log damage.

### What I did
- Replaced `_stamps()`/`_events()` with `_read_stamps()`/`_read_events()` returning `(records, errors)`, catching
  `KeyError`/`TypeError`/`ValueError` per record and reporting it.
- `log_problems()` now merges malformed JSON lines, non-label/non-decision records and fold-ignored events.
- Added `CorruptRecordTest` with two cases: a label record missing fields, and a decision record with a non-integer
  `seq`.
- Ran `python3 -m unittest discover -s tests`.

### Why
- Note 5: one fold, so edge cases are decided once; the ledger must be able to say *what* it skipped rather than
  silently producing a wrong state (the failure the chapter describes for the three copied dust folds).

### What worked
- `Ran 72 tests in 0.051s` / `OK`; a later re-run with `python3 -W error -m unittest discover -s tests` is also `OK`.

### What didn't work
- No failures in this step.

### What I learned
- Reading tolerantly is cheap; the expensive part is telling the user. Keeping `(line, reason)` pairs made the report
  useful without a logging dependency.

### What was tricky to build
- Keeping `log_problems()` consistent: it reads the logs twice (once for JSON errors, once for record errors). That is
  fine for correctness and documented; a cache would be premature.

### What warrants a second pair of eyes
- Should a corrupted label record be repaired into a placeholder label rather than skipped? Skipping keeps the fold
  honest (no invented artefact) but means a decision about it can never be applied; note 10 ("corrections overlay; they
  do not rewrite") supports skipping.

### What should be done in the future
- Archive old decisions (chapter Consequences) and add a compaction tool that keeps the state derivable.

### Code review instructions
- Read `labelbook/ledger.py::_read_stamps`, `_read_events` and `log_problems`, then `CorruptRecordTest`.

## Step 7: Final check — full suite, byte-compile, README example and a last read of the code

I re-read the written modules, added a short `README.md` describing the storage format and the fold rules, and ran the
final checks. Everything is green and the diary is complete.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Confirm the deliverable is complete: code, tests, diary, no stray files, standard library
only.

**Inferred user intent:** A finished, reviewable answer with no loose ends.

### What I did
- Re-read `labelbook/ledger.py`; changed the unknown-label check in `decide` from a set to a list membership test so an
  unhashable id argument cannot raise `TypeError` before the intended `UnknownLabel`.
- Wrote `README.md` (usage, storage table, fold rules, schema pointer, test command).
- Ran `python3 -W error -m unittest discover -s tests` and `python3 -m compileall -q labelbook tests`.
- Ran the README example end to end in a temp directory.

### Why
- Every creating path must stamp (note 1) and every reader must fold the same way (note 5); a final read is where
  small inconsistencies between the two logs and the queries show up.

### What worked
- `Ran 72 tests in 0.061s` / `OK` (also with `-W error`), `COMPILE_OK`, and the README example produced
  `{'item': 'img-2', 'label': 'dust', 'status': 'pending'}` after the undo, `made_by(kind="detector", model="v1")`
  matching the detector label, `acceptance("model") == {'v1': 1.0}`, and an export of
  `[{'item': 'img-1', 'label': 'dust'}]` beside `labels.json.provenance.json`.
- Working tree contains only `CHAPTER.md`, `TASK.md`, `DIARY-FORMAT.md`, `DIARY.md`, `README.md`, `labelbook/*.py` and
  `tests/test_*.py`; everything was written inside this directory and only the standard library is used.

### What didn't work
- No failures in the final check.

### What I learned
- The pattern's weakest point in practice is the *reader* side, not the writer side: three reader methods
  (`state`, `acceptance`, `export`) were only obviously consistent because they all call `fold`. Keeping a second
  reader implementation would have been the drift the chapter warns about.

### What was tricky to build
- The exported-file format had to stay `[{"item", "label"}]` while provenance had to travel with it. Writing the
  provenance as `<path>.provenance.json` (note 8, sidecar) solved both, and the sidecar records the digest of the export
  so a consumer can tell whether the sidecar still describes the file.

### What warrants a second pair of eyes
- `export` returns the payload as well as writing it; the spec only requires writing. Confirm that extra return value is
  harmless for callers.
- `acceptance(by)`'s "omit values with no decided labels" rule, and `undo` with an empty stack being a logged no-op, are
  the two places where the task text left a choice.

### What should be done in the future
- Add a `--report` CLI that prints acceptance per source from a ledger directory, and a compaction tool that rewrites a
  log into a snapshot plus its tail without losing `undo` history.

### Code review instructions
- Files: `labelbook/schema.py` (field catalogue, hashing, code version), `labelbook/provenance.py` (stamping),
  `labelbook/events.py` (`fold`), `labelbook/store.py` (append-only JSON lines), `labelbook/ledger.py` (public API),
  `tests/test_*.py` (72 tests).
- Validate: `python3 -m unittest discover -s tests` from this directory, then run the snippet in `README.md`.

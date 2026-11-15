# Diary

## Goal

Build `labelbook`, a standard-library Python library that stamps every label with its provenance (a person, an agent
or a detector), keeps decisions as an append-only event log folded into state, and answers lineage queries
(`source_of`, `made_by`, `acceptance`) plus a stamped export. This diary records the design, each build step, the
failures and the fixes.

## Step 1: Reading the chapter, the task and the diary format; designing the ledger

I read `CHAPTER.md`, `TASK.md` and `DIARY-FORMAT.md` completely, then wrote down the shape of the library before
touching code. The chapter's Solution maps almost one-to-one onto the required interface, so the design is mostly a
matter of deciding which files hold which participant and where each invariant is enforced.

### Prompt Context

**User prompt (verbatim):** "You are a software engineer joining a project. Your working directory contains three files:
- CHAPTER.md: a chapter of a design-pattern book describing the pattern you must apply;
- TASK.md: the software to build, with its required public interface;
- DIARY-FORMAT.md: how to keep your work diary.
Read all three completely first. Keep DIARY.md as you go, one step per phase of work, in that format. Then design, build and test the software in this directory. Work only inside this
directory (do not read or write outside it). Use only the Python 3 standard library. Run your tests and fix what
fails before you finish, and make sure DIARY.md is complete. Your final message must follow the output format at the end of TASK.md."

**Assistant interpretation:** Implement the "Lineage Ledger" pattern as a Python package `labelbook` with the exact
public interface listed in `TASK.md`, persistence as JSON lines under one directory, tests under `tests/`, and a
diary in the strict format of `DIARY-FORMAT.md`. The final answer must be a single JSON object in a fenced block.

**Inferred user intent:** The requester wants evidence that I can apply a pattern from a book chapter faithfully to a
concrete specification — provenance stamping, an append-only decision log with a single fold, lineage queries through
one matcher, and a bound sidecar — with tests that prove the fold's laws and the concurrency invariant.

### What I did
- Read CHAPTER.md (Structure, Collaborations, Sketch, 11 implementation notes), TASK.md and DIARY-FORMAT.md.
- Designed the module split, listed below, and the on-disk layout under one ledger directory:
  `schema.json` (schema beside the data), `labels.jsonl` (stamped artefacts, append-only), `decisions.jsonl`
  (events with a `seq`), `exports.jsonl` (audit of exports), `ledger.lock` (the lock file).
- Decided the vocabulary lives in one place (`schema.py`): `STATUS_OF`, `DECISIONS`, `DECIDED`, `ACCEPTING`,
  `FOLD_VERSION`.

### Why
- Chapter "Structure" names the participants; each becomes one module or one function so no reader re-implements a
  piece: `provenance.py` = Provenance record + Stamper, `schema.py` = Schema + fold vocabulary, `folding.py` = Fold +
  lineage matcher, `storage.py` = locked append + atomic write, `ledger.py` = the Ledger facade and its queries.
- Implementation note 5 ("write the fold once, and let it own the vocabulary") forces the status vocabulary into the
  fold's module, not into the queries; note 6 ("match makers in one place") forces one `matches()` used by `made_by`,
  `acceptance` and the export's exclude list; note 9 ("write the schema beside the data") forces `schema.json`.

### What worked
- The chapter's sketch is executable line by line, so the interface in TASK.md fell out of it: `create` → `add_label`,
  `decide` → `decide`, `fold` → `state`/`_fold`, `sourceOf`/`madeBy`/`acceptance` → `source_of`/`made_by`/`acceptance`,
  `export` → `export`.

### What didn't work
- No failures yet; this step produced no code.

### What I learned
- The chapter is explicit that the two halves are separable, but TASK.md needs both: provenance stamping (labels are
  compared by source) and the decision log (accept, reject, correct, undo over rounds).
- `TASK.md` restricts maker kinds to person/agent/detector while the chapter also names program and preset; the
  export is itself a creating path made by a program, so I keep the chapter's five kinds in the schema and use
  `program` for the export stamper, with `unknown` reserved for artefacts that predate the pattern.

### What was tricky to build
- Choosing where an export's provenance lives: labelling the export as a label artefact would pollute `state()` and
  `acceptance`, so the export is stamped in its sidecar (kind, maker, inputs with hashes, content hash, carries) and
  recorded in an append-only `exports.jsonl` audit trail instead of `labels.jsonl`.

### What warrants a second pair of eyes
- The decision to append an event for an unknown label id and report it as a fold problem (chapter-conformant)
  rather than raising: a caller could silently lose a decision if it ignores `problems()`.

### What should be done in the future
- Build storage and schema next, then the stamping path, then the fold and queries, then export, then tests.

### Code review instructions
- Nothing to run yet. Start with `labelbook/schema.py` and `labelbook/folding.py` once they exist, then `tests/`.

## Step 2: Storage and the schema beside the data

I wrote `labelbook/storage.py` (atomic writes, one-write appends under a lock, tolerant JSON-lines reading, a
sequence-number tail reader) and `labelbook/schema.py` (the schema dict written once as `<dir>/schema.json`, plus the
status vocabulary the fold owns).

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Provide the two foundations the rest of the pattern needs: records must never be seen
half-written and the allowed values must live in a file beside the data.

**Inferred user intent:** A ledger another tool can read, and a schema that keeps code and data in step.

### What I did
- Created `labelbook/storage.py`: `atomic_write_bytes`/`atomic_write_json` (temp file + `os.replace` + `fsync`),
  `file_lock` (`fcntl.flock`, with an `O_CREAT|O_EXCL` fallback), `append_line` (one `os.write` on an `O_APPEND`
  descriptor), `read_jsonl` (returns records *and* problems), `last_seq` (tail read, full-scan fallback).
- Created `labelbook/schema.py`: `SCHEMA` with `maker_kinds`, `decisions`, `statuses`, `status_of`, `decided`,
  `accepting`, `fold_version`, `code_version`, a `fields` map with a `definition` and a `unit` per field, `files`,
  `policy` and `notes`; `ensure_schema` (never overwrites), `load_schema`, `allowed_kinds`, `allowed_decisions`,
  `policy`.
- Wrote the schema vocabulary once and imported it everywhere else: `STATUS_OF`, `DECISIONS`, `DECIDED`,
  `ACCEPTING`, `FOLD_VERSION`.

### Why
- Note 7 ("several writers need atomic appends and collision-free ids") needs the lock and one-write append in place
  before any writer exists; note 9 ("write the schema beside the data [...] enforce each list of allowed values")
  needs the lists to be readable from the file the checks use; note 5 needs one definition of decided/accepting.

### What worked
- `atomic_write_bytes` and `append_line` are small enough that every later write path uses them.
- Reading the allowed kinds from `schema.json` means a user can extend the list by editing the file, and the
  creation check follows: one source, no drift.

### What didn't work
- First attempt at nested locking in `decide` (`with _locked(...)` around `append_line(..., lock_path=...)`) would
  have deadlocked, because `flock` on a second descriptor of the same file in the same process blocks. Fixed by
  giving `append_line` an optional `lock_path=None` meaning "the caller already holds the lock", so the sequence
  number and its record are written inside one critical section.
- `python3 -m unittest discover -s tests -t .` failed with
  `ImportError: Start directory is not importable: '.../tests'` because I passed an explicit top-level directory and
  `tests/` has no `__init__.py`; the task's command `python3 -m unittest discover -s tests` works and is what I use.

### What I learned
- The chapter's `lastSeq` idea plus a lock is easy to get wrong in the *nesting* rather than in the algorithm.
- A schema that only lives in code is invisible to the other tools that read `labels.jsonl`; the file version also
  documents units (`acceptance` is a fraction of decided labels, `seq` is an integer starting at 1).

### What was tricky to build
- `last_seq` must survive a partially written final line (a reader can catch an append in flight): the tail read
  tries the last kilobytes, skips a possibly truncated first line of the chunk, and falls back to a full scan.

### What warrants a second pair of eyes
- The Windows `O_CREAT|O_EXCL` fallback is untested here (POSIX only); stale markers after a crash would block.

### What should be done in the future
- Stamp artefacts, then append decisions.

### Code review instructions
- Read `labelbook/storage.py` (`append_line`, `file_lock`, `last_seq`) and `labelbook/schema.py` (`SCHEMA`,
  `ensure_schema`). Validate with `python3 -m unittest discover -s tests` (tests `test_schema_storage.StorageTest`,
  `SchemaBesideDataTest`).

## Step 3: The stamper and the creating path (`add_label`)

I added `labelbook/provenance.py` (the one stamping call, input hashing, legacy provenance) and the first half of
`labelbook/ledger.py` (`Ledger.add_label`, reading, and the schema accessors).

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Make provenance a required argument of the artefact constructor so no label can exist
without a maker, and hash the inputs it read.

**Inferred user intent:** "What made this?" must be answerable for every label, including ones made before the
pattern existed (counted, not hidden).

### What I did
- `labelbook/provenance.py`: `stamp(maker, inputs, allowed_kinds)` requiring a dict maker with a `kind` from the
  schema (raising `ValueError` naming the allowed kinds), `hash_inputs`/`hash_file` recording `ref`, `sha256`,
  `algorithm`, `size`, `mtime`, `exists`, `legacy_provenance()` for kind `unknown`, `code_version()`, `now_iso()`.
- `labelbook/ledger.py`: `Ledger.__init__` (directory, schema, empty logs, lock), `add_label(item, label, maker,
  inputs=())` → id, `artefacts()`, `label_ids()`, `source_of`, `unstamped()`, `audit()`, `_normalise_artefact`
  (records without provenance read back as `unknown`).
- Created the ledger files eagerly so the directory is readable before the first decision.

### Why
- Note 1 ("make stamping impossible to forget"): provenance is not optional in `add_label`, legacy records get
  `kind: unknown`, and `unstamped()` counts them; note 11 ("hash inputs that may change"): each input carries a
  sha256, not just a path.

### What worked
- `add_label` encodes the record before writing, so a non-serialisable label raises `TypeError` and leaves the log
  untouched (tested).
- A missing input file is recorded with `exists: false` rather than raising: lineage must show what was unreadable.

### What didn't work
- `test_ledger_files_are_json_lines_under_one_directory` failed with
  `AssertionError: 'decisions.jsonl' not found in ['labels.jsonl', 'ledger.lock', 'schema.json']`; fixed by creating
  empty `labels.jsonl`, `decisions.jsonl` and `exports.jsonl` in `Ledger.__init__`.

### What I learned
- The chapter's "no constructor without provenance" is cheap to enforce in Python by making the stamper the only
  writer of the label record.

### What was tricky to build
- Normalising old records: a line without `provenance` must still fold (so `state()` shows it) while `source_of`
  reports `unknown` — the record is not rewritten, only read as unstamped.

### What warrants a second pair of eyes
- `source_of` returns both `at` and `time` (the task says "time", the chapter says `at`); confirm no caller needs
  exactly one key.

### What should be done in the future
- Build the decision append and the fold.

### Code review instructions
- Read `labelbook/provenance.py:stamp` and `labelbook/ledger.py:add_label`; run the `test_labels` module.

## Step 4: The decision log and the one fold

I wrote `labelbook/folding.py` (the fold, `ItemState`, the maker matcher, the acceptance query) and `Ledger.decide` /
`state` / `problems`, so decisions are appended as events and current state is derived, never stored.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Append-only events ordered by sequence number, with `undo` as an event and one fold
that owns statuses, the label in force and what counts as decided/accepting.

**Inferred user intent:** Corrections and undos must be revisable without losing history, and every reader (training,
scoring, review, export) must get the same answer.

### What I did
- `labelbook/folding.py`: `fold(artefacts, events) -> (states, problems)` implementing `undo` (mark the latest live
  decision undone, keep it), status from the last live decision (`pending` when none), label in force = last live
  correction's `new_label` else the original; problems for unknown artefacts, unknown decisions, undos with nothing
  to undo, events without `seq`, duplicate ids; `matches`/`field_value` (one maker matcher); `acceptance` and
  `acceptance_counts`; `ItemState` dataclass.
- `Ledger.decide(label_id, decision, actor, reason=None, new_label=None)`: validates the decision against the
  schema's list, refuses a missing actor (`ValueError`), requires `new_label` for `correct`, assigns `seq` inside the
  lock and appends in one write.
- `Ledger.state()` returns only `{"item", "label", "status"}` per id, deep-copied; `Ledger.problems()`,
  `Ledger.fold()`, `Ledger.acceptance_report(by)` (shares, counts, `fold_version`).

### Why
- Note 3 ("undo is an event, and order is a sequence number"): the fold sorts by `seq`, never by the clock.
- Note 4 ("define the label in force, and test it as laws"): corrections overlay; status comes from the last live
  decision; accept/reject/undo leaves the earlier decision in force.
- Note 5 ("write the fold once, and let it own the vocabulary"): `STATUS_OF`, `DECIDED`, `ACCEPTING` live in
  `schema.py` and are imported by the fold and the queries; unknown decisions are reported, not folded as rejections.
- Note 6 ("match makers in one place"): `matches()` is used by `made_by`, `acceptance` and the export's exclude list.

### What worked
- Two small layers (append, then fold) made the laws testable directly: `fold()` takes plain dicts, so random event
  sequences can be checked against a naive reference model without touching the disk.
- `problems()` surfaced the chapter's "report, never guess" case cleanly (an injected `escalate` event changes no
  state; `undo` with nothing to undo leaves the label pending).

### What didn't work
- `AttributeError: 'function' object has no attribute 'acceptance_counts'` from `labelbook/ledger.py`: `from . import
  fold as fold_module` resolved to the *package attribute* `labelbook.fold`, which `labelbook/__init__.py` had bound
  to the fold *function*. Fixed by importing `acceptance_counts as _acceptance_counts` from `.fold` directly, and by
  not keeping a module alias at all.

### What I learned
- A package that exports a function named like its own submodule shadows the module for later `from . import`
  statements; importing names directly is safer.
- `state()` deep-copying matters: without it, a reader that mutates the returned label would corrupt the next call's
  view.

### What was tricky to build
- The interaction of `undo` with history: an undo must pop the latest *live* decision and keep the popped one in
  `decisions` marked `undone` (with `undone_by: seq`), so a later reader can still see what was reversed; the status
  and label are then recomputed from the live remainder.

### What warrants a second pair of eyes
- `decide()` appends an event for an unknown label id and reports it as a fold problem (chapter-conformant) instead
  of raising; a caller that ignores `problems()` would lose a decision silently.
- `acceptance()` omits maker values with no decided label (the share is undefined) and exposes the counts separately;
  confirm that is the intended reading of "for each value ... the share of decided labels".

### What should be done in the future
- Lineage queries end-to-end, then the stamped export.

### Code review instructions
- Read `labelbook/folding.py:fold` and `labelbook/ledger.py:decide`. Validate with
  `python3 -m unittest discover -s tests` (modules `test_decisions`, `test_fold_laws`).

## Step 5: Lineage queries and the stamped export

I finished `labelbook/ledger.py` with `made_by`, `acceptance`, `export`, `verify_export`, `read_export` and the
`exports.jsonl` audit trail, then wrote the package `__init__.py`.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Answer the queries both ways through one matcher, and treat the export as a creating
path whose sidecar names its content hash and the labels it carries.

**Inferred user intent:** Measure each source, exclude a faulty source wholesale, and audit any exported label.

### What I did
- `made_by(**query)` filters artefacts through `matches`; `acceptance(by)`/`acceptance_counts(by)`/
  `acceptance_report(by)` group decided labels by a maker field through the same matcher.
- `export(path, ctx=None, exclude=())`: folds, keeps `accepted` and `corrected` with the label in force, writes the
  JSON list atomically, then writes `<path>.provenance.json` with kind/maker/inputs (hashed ledger files)/
  `fold_version`/`statuses`/`contentHash` (`sha256:...`)/`carries` (per label id: item, label, kind, maker), and
  appends an `exports.jsonl` audit record.
- `exclude` accepts label ids and/or provenance queries, so "exclude everything one faulty source made" goes through
  the same matcher; `verify_export` refuses a missing sidecar or one whose recorded hash differs from the bytes.
- `labelbook/__init__.py` exports `Ledger` plus the vocabulary and helpers.

### Why
- Note 10 ("bind a sidecar to its content, and to the labels it carries"): the sidecar stores the sha256 of the exact
  bytes and the export's `carries` list names each label id and its maker — the two things construction builds left
  out.
- Note 1 ("exports and reports are creating paths too"): the export is stamped, recorded in `exports.jsonl`, and its
  provenance names the ledger files it read.
- Note 6: the exclude list and `made_by` share `matches`.

### What worked
- Export uses the fold's `current` label, so a corrected label exports the correction and an undone correction
  exports the original (both tested).
- Staleness is detectable by construction: appending one byte to the export makes `verify_export` raise.

### What didn't work
- Nothing failed in this step, but I deliberately kept the export out of `labels.jsonl`: stamping it as a label
  artefact would have made it appear in `state()` and changed `acceptance()` percentages. It is stamped in its
  sidecar and in `exports.jsonl` instead.

### What I learned
- Writing the sidecar after the data means a crash in between leaves an export with no sidecar — which readers treat
  as unstamped, exactly the chapter's rule; the reverse order would be worse (a sidecar naming absent bytes).

### What was tricky to build
- `export` has to keep the fold as its only source of truth for what is exportable (`ACCEPTING`), while the sidecar
  must describe the *rows actually written* (after exclusions), so `carries` is built from the filtered rows.

### What warrants a second pair of eyes
- A relative export path is resolved against the current directory, not the ledger directory; confirm callers expect
  that.
- `carries` records the label in force at export time as well as the maker; a label corrected *after* the export
  makes the sidecar a historical record, which is intended but worth stating.

### What should be done in the future
- Tests for every claim above, including the fold's laws on random sequences and multi-writer appends.

### Code review instructions
- Read `labelbook/ledger.py:export`, `_export_provenance`, `verify_export`; run `test_export`.

## Step 6: Writing the test suite and running it

I wrote seven test modules under `tests/` covering the interface, the pattern's invariants, the fold's laws on random
sequences, the sidecar binding and multi-writer appends, then ran them with the command the task names.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Prove each claim: provenance is stamped and hashed, decisions are appended and folded
by laws, queries go through one matcher, the export sidecar is bound to its bytes and carries makers, and concurrent
writers lose nothing.

**Inferred user intent:** Tests that fail when the pattern is broken, not tests that merely execute the code.

### What I did
- `tests/_path.py`: puts the project root on `sys.path` and exposes `ROOT` for subprocess tests.
- `tests/test_schema_storage.py`: schema written beside the data, not overwritten, units/definitions present,
  `maker_kinds` and the anonymous-actor policy enforced *from the file*, atomic write, tolerant JSON-lines reading,
  `last_seq` tail read, the on-disk file layout.
- `tests/test_labels.py`: stamping (kind, maker, sha256 inputs, size, time, code version), id uniqueness, a second
  `Ledger` sees the same state, non-serialisable labels refused before any write, legacy lines counted by
  `unstamped()`, `source_of` raising `KeyError`.
- `tests/test_decisions.py`: accept/reject/correct/undo semantics, the correction kept when accepted later, undo of a
  correction restoring the previous one, undo with nothing to undo reported, `ValueError` for a missing actor and an
  unknown decision, `correct` without `new_label`, append-only log shape and `seq` continuing across instances, an
  unknown decision injected into the log not guessed as a rejection, and the public signatures of `add_label`/`decide`.
- `tests/test_fold_laws.py`: the four laws plus 400 random decision sequences compared with a naive reference model
  (a list the undo pops), multi-label random sequences with shuffled event order, and problems changing no state.
- `tests/test_lineage.py`: `made_by` with one and several keys, a faulty source's rejected label still listed,
  `acceptance` by `kind` and by `model` (0.75 detector, 1.0 agent incl. a corrected label), pending labels excluded,
  undo returning a label to pending, `acceptance_counts`, `acceptance_report` carrying `fold_version`, `state`
  returning exactly `item`/`label`/`status` and not leaking mutable state.
- `tests/test_export.py`: only accepted/corrected exported with the label in force, sidecar kind/maker/inputs/
  `fold_version`, `contentHash` equal to the sha256 of the bytes, `carries` naming label ids and their makers,
  modification and a deleted sidecar both detected, exclusion by provenance query and by id, the `exports.jsonl`
  audit record, empty export, and export after an undo.
- `tests/test_concurrency.py`: 4 subprocesses × 40 labels (all ids unique, no malformed lines, `seq` exactly 1..40)
  and 8 threads × 25 labels+decisions in one process.

### Why
- Note 4 ("test it as laws"): the reference model catches the exact mistake the chapter warns about ("correct then
  accept keeps the correction") without hard-coding internals.
- Note 7 ("ids allocated as max+1 [...] lost a third of 400 labels to four concurrent writers"): the subprocess test
  reproduces that setup and asserts `seq` is a permutation of `1..N` and every id survived.

### What worked
- Running `python3 -m unittest discover -s tests` gave a real failure immediately (the missing `decisions.jsonl`),
  which is the kind of failure I wanted, and 76 tests pass consistently across repeated runs.

### What didn't work
- First run of the suite (before the eager-log creation fix):
  `FAIL: test_ledger_files_are_json_lines_under_one_directory` with
  `AssertionError: 'decisions.jsonl' not found in ['labels.jsonl', 'ledger.lock', 'schema.json']`.
- Two of my own test files did not even parse on first write (`SyntaxError` from a missing parenthesis in
  `test_concurrency.py` and a missing `ROOT` name in `tests/_path.py`); fixed before the first suite run.

### What I learned
- Writing the random-law test first made the fold simpler: every extra rule had to be expressible in the reference
  model, which is exactly the "one fold" discipline of note 5.

### What was tricky to build
- Making the concurrency test meaningful: it had to run in *separate processes* (threads alone would not expose a
  `max+1` bug across processes), pass the project root through `PYTHONPATH`, and read the raw log afterwards to
  assert there is not a single malformed line or repeated `seq`.

### What warrants a second pair of eyes
- The process test relies on `fcntl.flock` on the platform running the tests; on a filesystem without advisory locks
  it would not prove the invariant.

### What should be done in the future
- Add a test that reads the log while another process is mid-append (partial last line) if this ever runs on a
  network filesystem.

### Code review instructions
- Start with `tests/test_fold_laws.py` (laws + reference model) and `tests/test_concurrency.py`; run
  `python3 -m unittest discover -s tests`.

## Step 7: Fixes after failing runs

Each failure below was fixed and the suite re-run to green. Two were real defects in the library, two were my own
mistakes in the plumbing and in the tests.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Fix what fails, keep the fix visible, and make sure the failure cannot come back.

**Inferred user intent:** A clean, repeated-green test run and a record of what went wrong.

### What I did
- Fix 1 (library): created the JSON-lines logs eagerly in `Ledger.__init__`.
- Fix 2 (library): removed the nested `flock` in `decide` by letting `append_line(..., lock_path=None)` mean "the
  caller holds the lock", so `seq` and its record are written inside one critical section.
- Fix 3 (library): renamed `labelbook/fold.py` to `labelbook/folding.py` so no module name collides with the
  exported `fold()` function; updated `ledger.py`, `__init__.py`, `schema.py` comments and the diary.
- Fix 4 (library): `hash_inputs` accepts a single path (str or `os.PathLike`) as one input instead of raising, and
  `decide` keeps a caller-supplied `new_label` on non-`correct` events (the fold ignores it there; no information is
  thrown away).
- Fix 5 (tests): added `ROOT` to `tests/_path.py` for the subprocess test, closed a missing parenthesis in
  `test_concurrency.py`, and used the task's runner command.

### Why
- A log that does not exist until the first decision makes an empty ledger look broken to any other tool (the test
  that failed asserted the documented on-disk layout from the schema's `files` map).
- Two `flock` acquisitions on the same file from the same process deadlock; the sequence-number assignment must not
  be a second acquisition.

### What worked
- After the fixes: `python3 -m unittest discover -s tests` → `Ran 76 tests ... OK`, repeated three times in a row
  with identical results.

### What didn't work
- Exact failures seen, in order:
  1. `AttributeError: 'function' object has no attribute 'acceptance_counts'` (smoke script), caused by
     `from . import fold as fold_module` resolving to the package's exported `fold` function.
  2. `ImportError: Start directory is not importable: '/.../work/tests'` when I ran
     `python3 -m unittest discover -s tests -t .`; the task's command without `-t` works because `tests/` is not a
     package.
  3. `FAIL: test_ledger_files_are_json_lines_under_one_directory ... AssertionError: 'decisions.jsonl' not found in
     ['labels.jsonl', 'ledger.lock', 'schema.json']`.
  4. `SyntaxError: '(' was never closed` in `tests/test_concurrency.py` and
     `ImportError: cannot import name 'ROOT' from '_path'` in the same module — both my own test plumbing errors,
     fixed before the first full run.

### What I learned
- Python package attribute shadowing bites import statements of the form `from . import x` when the package exports a
  name `x`; renaming the module is a clearer fix than aliasing at each import.
- Eagerly creating empty append-only files is a cheap way to make the layout self-describing.

### What was tricky to build
- The deadlock fix had to keep *both* invariants: one write per record and a sequence number no two writers share.
  Moving the lock out one level and passing `lock_path=None` keeps a single acquisition while `last_seq` + append
  stay atomic together.

### What warrants a second pair of eyes
- `append_line(lock_path=None)` is an unlocked path by design; a future caller could use it outside a lock. It is
  documented, and only `decide` (which holds the lock) uses it.

### What should be done in the future
- Consider a `lint`/`type` check step (the repo uses only the standard library, so none is wired in).

### Code review instructions
- Diff review points: `labelbook/ledger.py` (`__init__`, `decide`), `labelbook/storage.py:append_line`,
  `labelbook/provenance.py:hash_inputs`. Run `python3 -m unittest discover -s tests`.

## Step 8: Final check

I ran the whole suite, a compile check, and an end-to-end demo with three sources, an undo and an export with an
excluded source, then tidied the directory and completed this diary.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Confirm the library does what the chapter and the task describe, and that the final
message matches the required JSON format.

**Inferred user intent:** A finished, tested deliverable with an honest account of the work.

### What I did
- `python3 -m compileall -q labelbook tests` → no output (clean).
- `python3 -m unittest discover -s tests` → `Ran 76 tests in 0.212s` / `OK`, three consecutive runs.
- End-to-end demo (`Ledger` in a temp dir): detector accepted, agent corrected then accepted, person accepted,
  undone, accepted; `state()` showed the corrected label in force for the agent's label; `source_of` showed maker,
  hashed inputs slot, version and time; `made_by(run="r1")` returned the one label; `acceptance("kind")` and
  `acceptance("conf_band")` returned shares; `export(out, exclude={"kind": "detector"})` wrote two rows and a sidecar
  and left `problems()` empty.
- Removed `__pycache__` directories so only source, tests and the three given files remain.

### Why
- The task asks for tests to be run and fixed before finishing, and for a diary of each phase; the demo checks the
  interface exactly as another program would use it.

### What worked
- All 76 tests pass; the demo output matches the chapter's Collaborations (measure a source, exclude a source, audit
  an export).

### What didn't work
- Nothing at this stage; the last failure was the one recorded in Step 7 (fix 3), before the final run.

### What I learned
- The pattern fits the task tightly: provenance at creation, append-only decisions with one fold, one matcher, and a
  stamped export cover every paragraph of TASK.md without extra machinery.

### What was tricky to build
- Deciding what an export must *not* change: it is stamped (sidecar + `exports.jsonl`) but not added to
  `labels.jsonl`, otherwise exports would appear in `state()` and skew `acceptance()`.

### What warrants a second pair of eyes
- `acceptance()` omits maker values with no decided label; `Ledger.decide()` appends an event for an unknown label
  and reports it as a problem instead of raising. Both are chapter-driven choices that a caller could misread.
- `source_of()["inputs"]` is a list of `{ref, hash, algorithm, size, mtime, exists}` dicts (note 11), not a list of
  plain paths.

### What should be done in the future
- Optional: a small CLI (`python3 -m labelbook audit DIR`) and log archiving for very long logs (chapter
  Consequence "logs grow").

### Code review instructions
- Read in this order: `labelbook/schema.py`, `labelbook/storage.py`, `labelbook/provenance.py`,
  `labelbook/folding.py`, `labelbook/ledger.py`, then `tests/test_fold_laws.py` and `tests/test_concurrency.py`.
  Validate with `python3 -m unittest discover -s tests`.

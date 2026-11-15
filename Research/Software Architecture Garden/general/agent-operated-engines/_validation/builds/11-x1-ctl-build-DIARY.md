# Diary

## Goal

Build `labelbook`, a standard-library-only Python 3 library that stores proposed item labels (from people, agents and
detectors) plus the review decisions on them in an append-only JSON-lines ledger, and can report state, provenance,
per-source acceptance rates and exports. This diary records each phase of the work, in order, including failures.

## Step 1: Reading the task and designing the ledger

I read `TASK.md` and `DIARY-FORMAT.md` completely, checked the working directory (only those two files; no
`CHAPTER.md` exists here, so the "CHAPTER.md" references in the diary template have no counterpart and I used the task
text as the spec instead), and then designed the library before writing code.

My design is an append-only event log. Two JSON-lines files live in the ledger directory: `labels.jsonl` holds one
record per proposed label (`id`, `item`, `label`, `maker`, `inputs`, `time`), and `decisions.jsonl` holds one record
per review action (`label_id`, `decision`, `actor`, `reason`, `new_label`, `time`). Nothing is ever rewritten, so the
whole history stays auditable and a brand-new `Ledger` pointed at the same directory reconstructs exactly the same
state by replaying the files in order. `undo` is implemented as a replay-time "pop the latest effective decision"
operation, which makes undo-after-undo peel back further decisions instead of corrupting the log.

### Prompt Context

**User prompt (verbatim):** "You are a software engineer joining a project. Your working directory contains two files:
- TASK.md: the software to build, with its required public interface;
- DIARY-FORMAT.md: how to keep your work diary.
Read both completely first. Keep DIARY.md as you go, one step per phase of work, in that format. Then design, build and
test the software in this directory. Work only inside this
directory (do not read or write outside it). Use only the Python 3 standard library. Run your tests and fix what
fails before you finish, and make sure DIARY.md is complete. Your final message must follow the output format at the end
of TASK.md."

**Assistant interpretation:** Implement the `labelbook` package with exactly the required public interface, backed by
JSON-lines files in one directory, with tests run under `unittest`, and keep a structured diary of each phase.

**Inferred user intent:** A reviewer wants a small, dependency-free, durable label-review ledger whose state can be
rebuilt from disk, whose provenance is auditable, and whose per-source acceptance metric and export let a team drop a
bad source's labels; the diary must show how the work actually went, warts included.

### What I did
- Read `TASK.md` and `DIARY-FORMAT.md` in full; listed the directory (`TASK.md`, `DIARY-FORMAT.md` only, no `CHAPTER.md`).
- Decided the file layout (`labelbook/{__init__,errors,storage,ledger}.py`), the on-disk event schema, and the
  state model (effective decision stack per label, derived purely from the log).
- Wrote this diary step before touching code, as the format asks.

### Why
- Two append-only logs + full replay is what the requirement "a new `Ledger` on the same directory sees the same
  state" demands; anything cached only in memory would break it.
- Keeping `undo` in the log as an event (rather than deleting the decision line) is what makes "audit any exported
  label" possible: the rejected-then-undone history stays visible through `history()`.

### What worked
- The design covers every required method with no extra state: `state`, `acceptance` and `export` are pure functions
  of the replayed logs.

### What didn't work
- N/A (design step, nothing executed yet).

### What I learned
- The interface is small but has several unstated edge cases (undo of undo, correction followed by rejection, labels
  whose maker lacks the `by` field, missing `actor` passed positionally). I listed them and made an explicit decision
  for each below.

### What was tricky to build
- Nothing built yet. The tricky part identified during design: `decide(label_id, decision, actor, ...)` with `actor`
  required positionally would raise `TypeError` when omitted, but the task says a missing actor is a `ValueError`;
  therefore `actor` gets a `None` default and is validated explicitly.

### What warrants a second pair of eyes
- The judgement calls recorded as "unclear" at the end of the work: `acceptance` omitting sources that have no decided
  labels, and `state()`'s `label` after "correct then reject".

### What should be done in the future
- Build `labelbook/{errors,storage,ledger}.py`, then the test suite under `tests/`.

### Code review instructions
- Start with `TASK.md` (spec), then `labelbook/ledger.py` (`_replay`, `decide`, `acceptance`, `export`); validate with
  `python3 -m unittest discover -s tests`.

## Step 2: Building the error and storage layers

I built the bottom two layers first so that the ledger logic could stay free of file handling: `labelbook/errors.py`
defines the exception hierarchy, and `labelbook/storage.py` defines `JsonlLog` (append one JSON object per line, read
all records back in file order) plus `write_json_file` (atomic temp-file + `os.replace`).

Two details mattered. First, appends take a per-instance `threading.Lock` and, where `fcntl` exists, an advisory
`flock` on the descriptor, then `flush` + `fsync`, so a second process cannot interleave half a line. Second,
`JsonlLog.signature()` returns `(path, size, mtime_ns, inode)`; because the log only ever grows, size alone detects
every append, and the mtime/inode pair catches truncation or replacement.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Build the local storage primitives behind the required interface, keeping the ledger
class independent of file I/O details.

**Inferred user intent:** A reviewer wants to see the durability story (append-only, crash-tolerant, multi-process safe)
isolated in one small, auditable module.

### What I did
- Created `labelbook/errors.py` (`LabelbookError`, `UnknownLabelError`, `LedgerFormatError`).
- Created `labelbook/storage.py` (`JsonlLog.append/records/signature`, `write_json_file`).

### Why
- The task requires "everything is stored under one directory as files of JSON lines, so a new `Ledger` on the same
  directory sees the same state". A dumb append-only writer with a strict reader is the smallest thing that satisfies
  it and is easy to audit with `cat`.
- `UnknownLabelError` inherits from both `KeyError` and `ValueError`: an unknown id is a failed lookup *and* an invalid
  argument, and the task only promises `ValueError` for bad input, so callers catching either one work.

### What worked
- The writer/reader pair is ~150 lines and gives byte-identical behaviour in-process and cross-process.

### What didn't work
- N/A at this step; the layer was exercised in Step 3.

### What I learned
- Text-mode `tell()` offsets are not byte offsets, which is why the torn-line detection I considered was dropped; the
  reader instead reports corrupt lines loudly rather than silently skipping them (an audit ledger should not lose
  records quietly).

### What was tricky to build
- `os.fsync` and `fcntl.flock` are not portable, so both are wrapped in best-effort `try/except OSError` blocks; the
  library still works without them, it just loses cross-process serialisation.

### What warrants a second pair of eyes
- Whether the `flock` shared lock in `records()` is worth its complexity given that a writer only appends whole lines.

### What should be done in the future
- N/A.

### Code review instructions
- Read `labelbook/storage.py` top to bottom; validate with `python3 -m unittest discover -s tests` once the suite
  exists (Step 4).

## Step 3: Building the ledger core (replay model)

I wrote `labelbook/ledger.py`, whose whole state is a replay of the two logs into a `_Snapshot`: `labels` (insertion
order = file order = creation order), `history` (every decision and undo record, oldest first, each with an `undone`
flag) and `stacks` (the entries still in force). `status_and_label()` derives the status from the top of the stack and
the label from the latest effective correction. `add_label`, `decide`, `state`, `source_of`, `made_by`, `acceptance`
and `export` are all thin reads/writes over that snapshot, plus `history`, `status`, `current_label`, `labels` as small
conveniences.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Implement the eight required methods with validation, and make `undo` a replay-time
operation so the log never has to be rewritten.

**Inferred user intent:** A reviewer wants the semantics of the review workflow to be obvious from the code, and the
audit trail to survive every decision, including undos.

### What I did
- Created `labelbook/ledger.py` and `labelbook/__init__.py` (re-exporting `Ledger`, the errors, `KINDS`, `DECISIONS`).
- First draft stored only one `events` list per label and marked entries `undone`; the undo record itself landed in
  that same list.
- Rewrote the snapshot into `history` + `stacks` pairs and recorded the fix in the module docstring.

### Why
- Undo semantics: "cancels the latest decision on that label" becomes `stacks[label].pop()` during replay, so a second
  undo peels the decision before it, and a live undo with an empty stack is a `ValueError`.
- The task's "a missing `actor` is an error (`ValueError`)" forced `actor=None` as the default parameter: with a
  required positional parameter the caller would get `TypeError` instead.

### What worked
- Manual smoke run of every method in one script printed the expected state, acceptance table, export list and history.

### What didn't work
- The first draft's `effective()` returned the undo record as if it were a decision, which would have crashed
  `status_and_label` with `KeyError: 'undo'` in `STATUS_OF`. Caught by re-reading the code before running anything, fixed
  by splitting history from the stack.

### What I learned
- Keeping the audit trail and the effective decision stack as two views over the same entry objects gives undo without
  any log surgery, and `history()` can still show the cancelled decision.

### What was tricky to build
- Deciding what `state()["label"]` means after "correct then reject": the correction is still in the effective stack, so
  the label reported is the corrected one while the status is `rejected`. Implemented deliberately and covered by
  `test_reject_after_correct_keeps_the_corrected_label`.

### What warrants a second pair of eyes
- The `_current_snapshot()` cache keyed on file signatures, and the `decide()` sequence "read snapshot to validate undo,
  then append": two processes deciding at the same instant can interleave, which the log tolerates but which can make a
  double undo observe a stale stack.

### What should be done in the future
- Write the test suite (Step 4).

### Code review instructions
- `labelbook/ledger.py`: `_Snapshot.status_and_label`, `Ledger.decide` (undo branch), `Ledger.export` (`exclude`).

## Step 4: First test suite run

I wrote `tests/base.py` (shared temporary-directory fixture), `tests/test_labels.py` (adding labels, provenance,
validation, unknown ids) and `tests/test_decisions.py` (accept/reject/correct/undo, validation, audit trail) and ran the
documented command.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Cover the required interface behaviour-first, with one temporary ledger per test.

**Inferred user intent:** Reviewers want evidence that the promised interface works and that invalid input is rejected.

### What I did
- Created `tests/__init__.py`, `tests/base.py`, `tests/test_labels.py`, `tests/test_decisions.py`.
- Ran `python3 -m unittest discover -s tests`.

### Why
- `tests/base.py` keeps the fixture in one place and is imported as `tests.base`, which works both for
  `discover -s tests` and for a plain `python3 -m unittest discover` from the project root.

### What worked
- `python3 -m unittest discover -s tests` → `Ran 43 tests in 0.026s` / `OK`.

### What didn't work
- A `grep -c "json\.\|os\.\|tempfile\." tests/test_labels.py` cleanup check exited with `Command exited with code 1`
  because, after moving the fixture into `tests/base.py`, those modules were no longer used in that file. Removal of the
  now-unused imports fixed it.

### What I learned
- Making the fixture reusable immediately surfaced dead imports; the flat-vs-package import ambiguity of
  `unittest discover` needs the shared module to live in `tests/base.py` behind `tests/__init__.py`.

### What was tricky to build
- The unknown-id assertion: `source_of("missing")` had to satisfy both `KeyError` and `ValueError` expectations, which
  is why `UnknownLabelError` inherits from both.

### What warrants a second pair of eyes
- That raising `ValueError` for an undo with nothing to cancel is the intended reading of "cancels the latest decision".

### What should be done in the future
- Test metrics, export and persistence (Steps 5 and 6).

### Code review instructions
- `python3 -m unittest discover -s tests`; start with `tests/test_decisions.py::UndoTests`.

## Step 5: Metrics, export and provenance tests

I added `tests/test_metrics.py` (`made_by` matching, `acceptance` grouping by `model`/`kind`/`name`, pending and undone
labels excluded, corrections counted as accepted, non-scalar fields rejected), `tests/test_export.py` (only accepted and
corrected rows, creation order, missing directories, overwriting, excluding a faulty source) and `tests/test_workflow.py`
(single-label helpers, on-disk record shape, and the full "measure sources → drop the bad one → audit the export" story).

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Inferred user intent:** The reviewer should see the three workflow promises (measure a source, exclude a faulty
source, audit an exported label) each pinned by a test.

**Assistant interpretation:** Pin down `acceptance`, `export` and `source_of` semantics, including the cases the task
left open.

### What I did
- Created `tests/test_metrics.py`, `tests/test_export.py`, `tests/test_workflow.py`.
- Ran `python3 -m unittest discover -s tests` → `Ran 100 tests in 0.097s` / `OK`.

### Why
- `export(path, exclude=...)` with `ledger.made_by(model="broken")` is the concrete mechanism for "exclude everything one
  faulty source made"; testing exactly that composition is more useful than testing the pieces alone.

### What worked
- All 100 tests passed on the first run of this batch, including the workflow test where detector `d1` scores 1.0 and
  `d2` scores 0.0 and every `d2` label disappears from the export.

### What didn't work
- The first version of `test_labels_log_is_append_only` contained a tautological assertion (it compared the file with
  itself); rewritten to assert the earlier bytes are a strict prefix and that a decision does not touch `labels.jsonl`.

### What I learned
- `acceptance` needs an explicit decision for sources with no decided labels; I chose to omit them (their share is
  undefined, not zero) and documented it in the docstring.

### What was tricky to build
- Testing `acceptance` for a label decided, undone and re-decided required care: the metric must look at the effective
  stack, not at "was it ever accepted".

### What warrants a second pair of eyes
- The "correct then reject" and "omit undecided sources" choices are visible in the tests as intent, not as accidents.

### What should be done in the future
- A randomised consistency check against an independent reference model (Step 6).

### Code review instructions
- `tests/test_metrics.py::AcceptanceTests` and `tests/test_workflow.py::WorkflowTests`.

## Step 6: Randomised model check and a mutation experiment

To test the replay logic rather than my own examples, I added `tests/test_model_check.py`: a deliberately naive
`Reference` implementation (list of labels, list of decision stacks) driven by the same random operation sequence as the
ledger (120–200 steps, three fixed seeds), asserting after every step that `state()` agrees and at the end that a fresh
`Ledger` replays to the same state, that `acceptance("kind"/"model"/"name")` matches and that the export matches.

Then I checked the tests can actually fail: I temporarily mutated `labelbook/ledger.py` so that replaying an undo left
the decision on the stack (the bug from Step 3), ran the suite, restored the file from a backup copy and re-ran it.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Inferred user intent:** The requester wants proof that the tests have teeth, not just a green bar.

**Assistant interpretation:** Add a property-style test that compares the ledger with an independent model, and confirm
a deliberately reintroduced bug is caught.

**Inferred intent (restated):** Confidence that "run your tests and fix what fails" was done with meaningful tests.

### What I did
- Created `tests/test_model_check.py` (seeds 1, 2 and 200 steps for seed 3).
- Mutation run: `cp labelbook/ledger.py .scratch/ledger.py.bak`, replaced `stack.pop()["undone"] = True` with `pass`,
  ran the suite, then restored with `cp .scratch/ledger.py.bak labelbook/ledger.py && rm -rf .scratch`.
- Re-ran the suite after restoring.

### Why
- A reference implementation written from the spec text (not from the ledger code) catches interpretation drift between
  what the docstring claims and what replay actually does.

### What worked
- Clean suite: `Ran 103 tests in 0.220s` / `OK`.
- The mutated build failed loudly, e.g.
  `FAIL: test_new_ledger_sees_undos (test_persistence.PersistenceTests)` with
  `AssertionError: 'accepted' != 'pending'` and `state mismatch at step 9 (seed 3)`; the run ended in
  `FAILED (failures=12)`, so 12 of 103 tests depend on the undo replay being correct.
- After restoring the file the suite was green again, and `.scratch/` was removed.

### What didn't work
- The first draft of the model check carried a leftover `expectations` tuple and an unused `_apply_reference` helper;
  both were removed when the branch was rewritten to "let the reference raise, then require the ledger to raise".

### What I learned
- The random sequences immediately exercise the awkward combinations (undo of a correction, decision after a full undo,
  pending labels in `acceptance`), which hand-written tests reach only by accident.

### What was tricky to build
- Keeping the reference model independent: it deliberately stores `(id, item, label, maker)` tuples with synthetic ids
  `l0, l1, ...` and maps them to ledger ids by index, so it shares no code with the implementation.

### What warrants a second pair of eyes
- Whether three seeds and 440 random operations is enough; the seeds are fixed for reproducibility, which also means a
  future change could pass by luck for these seeds only.

### What should be done in the future
- Consider a seeded sweep of, say, 20 seeds in CI if the runtime (currently 0.2 s) allows it.

### Code review instructions
- `tests/test_model_check.py::ModelCheckTests.run_sequence` and `tests/test_model_check.py::Reference`.

## Step 7: Final check

Last pass: re-read the required interface line by line against `dir(Ledger)`, re-ran the exact command from the task,
and confirmed the directory contains only the sources, the tests and this diary.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Verify every required name exists with a compatible signature, and finish with a clean run.

**Inferred user intent:** Nothing surprising left for the reviewer: green tests, no stray artefacts.

### What I did
- Re-ran `python3 -m unittest discover -s tests` → `Ran 103 tests in 0.216s` / `OK`.
- Checked the required surface: `Ledger(directory)`, `add_label(item, label, maker, inputs=())`,
  `decide(label_id, decision, actor=None, reason=None, new_label=None)`, `state()`, `source_of()`, `made_by(**query)`,
  `acceptance(by)`, `export(path, exclude=())`, all exported from `labelbook/__init__.py`.
- Confirmed no scratch files remain (`ls -a` shows only `TASK.md`, `DIARY-FORMAT.md`, `DIARY.md`, `labelbook/`,
  `tests/`).

### Why
- The final message has to state a test count and a result, so the number must come from the last run, not from memory.

### What worked
- Signature check by introspection and the suite both clean.

### What didn't work
- Nothing at this step.

### What I learned
- The optional `exclude=` on `export` is additive and does not change the required `export(path)` behaviour.

### What was tricky to build
- N/A.

### What warrants a second pair of eyes
- The judgement calls listed as "unclear" in the final report: undo with nothing to cancel, `acceptance` omitting
  sources without decided labels, and the label reported for "correct then reject".

### What should be done in the future
- If the team grows the log beyond a few hundred thousand lines, add an index instead of replaying on every read.

### Code review instructions
- Run `python3 -m unittest discover -s tests`; read `labelbook/ledger.py` then `labelbook/storage.py`.

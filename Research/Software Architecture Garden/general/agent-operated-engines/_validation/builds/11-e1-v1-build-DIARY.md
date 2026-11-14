# Diary

## Goal

Build `labelbook`, a standard-library-only Python library in which every proposed label carries its provenance (maker,
inputs with hashes, version, time) and every reviewer decision is appended to a log that one shared fold turns into
current state. This diary records the phases, the tests and the failures along the way.

## Step 1: Reading the chapter, the task and the diary format; designing the ledger

I read `CHAPTER.md`, `TASK.md` and `DIARY-FORMAT.md` in full before writing anything. The chapter's shape is a lineage
ledger: a provenance record stamped at creation (kind of maker, ids, inputs with hashes, version, time), an
append-only decision log whose events are never edited, one shared `fold` that every reader uses, and the two-way
lineage query (`sourceOf` / `madeBy`) plus aggregates such as acceptance by source. The task pins the public
interface: `Ledger(directory)`, `add_label`, `decide`, `state`, `source_of`, `made_by`, `acceptance`, `export`, with
state persisted as JSON-lines files so a fresh `Ledger` on the same directory sees the same state.

I designed the storage as three files in the ledger directory: `labels.jsonl` (creation records, append-only),
`events.jsonl` (decision events, append-only) and `schema.json` (field names, definitions and units, written once —
chapter note 7). Decisions are folded with a pure module-level function `fold(labels, events)` that is the single
implementation used by `state()`, `acceptance()` and `export()` (chapter note 5). `undo` pops the latest effective
decision from a per-label stack rather than deleting the whole item, so an undo after a correction goes back to
"accepted", not to "pending" — the log stays intact and nothing is lost (notes 3, 4, 10).

### Prompt Context

**User prompt (verbatim):** "You are a software engineer joining a project. Your working directory contains three files:
- CHAPTER.md: a chapter of a design-pattern book describing the pattern you must apply;
- TASK.md: the software to build, with its required public interface;
- DIARY-FORMAT.md: how to keep your work diary.
Read all three completely first. Keep DIARY.md as you go, one step per phase of work, in that format. Then design, build and test the software in this directory. Work only inside this
directory (do not read or write outside it). Use only the Python 3 standard library. Run your tests and fix what
fails before you finish, and make sure DIARY.md is complete. Your final message must follow the output format at the end of TASK.md."

**Assistant interpretation:** Implement the `labelbook` library described in `TASK.md` using the Lineage Ledger
pattern from `CHAPTER.md`, with tests under `tests/`, a step-by-step `DIARY.md`, and a final JSON report.

**Inferred user intent:** The requester wants a working, tested implementation that visibly applies the chapter's
pattern — provenance stamped at creation, append-only decisions, one fold, lineage queries both ways — and evidence in
the diary that the pattern was understood rather than merely named.

### What I did
- Read all three input files completely.
- Sketched the file layout (`labels.jsonl`, `events.jsonl`, `schema.json`), the record shapes and the fold semantics on
  paper before writing code.
- Decided the decision log semantics: `accept`/`reject`/`correct` push an effective decision, `undo` pops the most
  recent one; current status is derived from the top of the stack.

### Why
- Append-only files plus a pure fold is exactly the chapter's Solution section, and it makes a second `Ledger` on the
  same directory see identical state without any shared process memory.
- Keeping `schema.json` separate applies implementation note 7 (definitions and units live in a schema, not only in
  code comments).

### What worked
- The chapter's Structure table mapped almost one-to-one onto modules and methods, so the design took one pass.

### What didn't work
- N/A at this step.

### What I learned
- The chapter's fold sketch (`undo` deletes the item entry) is weaker than its own prose ("cancels the latest
  decision"), which matters as soon as a correction follows an accept. I chose the stack semantics and will document
  and test it.

### What was tricky to build
- Nothing built yet; the tricky part was pinning where `undo` lands, described above.

### What warrants a second pair of eyes
- Whether "accepted or corrected" counts as one class in `acceptance()`; I read the task's "(decided = accepted,
  corrected or rejected)" as: numerator = accepted + corrected.

### What should be done in the future
- Write the module, then the test suite, then run and fix.

### Code review instructions
- Start with `labelbook/ledger.py` (`fold`, `Ledger.add_label`, `Ledger.decide`); validate with
  `python3 -m unittest discover -s tests`.

## Step 2: Storage, schema and the stamper

I wrote `labelbook/ledger.py` with the three JSON-lines files, the `SCHEMA` document written to `schema.json` on first
use (and never rewritten), and the provenance half of the pattern: `stamp()` (the Stamper every creating path calls),
`describe_input()` (path + sha256 + size + mtime, or `missing: true` when the file is gone) and `Ledger.add_label()`.
`add_label` validates the maker, stamps it, appends one record to `labels.jsonl` and returns the id `lbl-000001`-style,
so a second `Ledger` on the same directory picks up the same state. `labelbook/__init__.py` re-exports the public
names.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Build the creation side of the ledger: append-only label records with provenance and a
schema that defines every stored field.

**Inferred user intent:** Nothing may enter the ledger unstamped, and the stored values must be self-describing.

### What I did
- Created `labelbook/ledger.py` (constants, `SCHEMA`, `stamp`, `describe_input`, JSON-lines helpers, `Ledger`).
- Created `labelbook/__init__.py` exporting `Ledger`, `fold`, `stamp`, `describe_input`, `DECISIONS`,
  `DECIDED_STATUS`, `MAKER_KINDS`, `SCHEMA`, `CODE_VERSION` and the file-name constants.
- `Ledger.__init__` creates the directory and writes `schema.json` only when it does not exist.

### Why
- Chapter note 1 (stamp in every creating path): `add_label` is the single creating path and it always calls
  `stamp()`.
- Chapter note 7 (definitions and units in the schema): `schema.json` lists each field with its meaning, plus `units`
  for size (bytes), timestamps (ISO-8601 UTC with `Z`) and `acceptance` (a share in [0, 1]).
- Chapter note 9 (hash inputs that may change): inputs are recorded with sha256, size and mtime, not by path alone.

### What worked
- Writing the schema as data (`SCHEMA`) meant the file on disk and the documentation cannot drift.
- Ids are sequential per directory (`lbl-000007`), which makes logs human-readable and audits easy to follow.

### What didn't work
- My first version of `add_label` built the `maker` field twice (once from the raw maker, once from the stamp), which
duplicated `inputs`/`at`/`version` inside the maker dict. I replaced it with one clear construction from `kind` plus
the maker ids before running anything.

### What I learned
- The chapter is right that the stamper must be one helper: the duplicated-field slip above is exactly the kind of
  thing that happens when each path assembles its own provenance.

### What was tricky to build
- Deciding what to do when an input path cannot be read. Dropping it silently would produce a record that misleads an
  auditor, so the entry keeps the path and sets `missing: true`, `sha256: null`.

### What warrants a second pair of eyes
- `describe_input` accepts either a path or a dict with extra keys; a reviewer should confirm that extra keys cannot
  overwrite `sha256`/`size`/`mtime` (they are filtered out, then applied last — verify).

### What should be done in the future
- Add `decide`, `state`, the fold and the queries.

### Code review instructions
- `labelbook/ledger.py`: `SCHEMA`, `stamp`, `describe_input`, `Ledger.add_label`.
- `python3 -m unittest tests.test_ledger.TestCreation` (once the suite exists).

## Step 3: Decisions, the one fold, both lineage queries and export

I added `Ledger.decide()` (append-only events with `actor`, `reason`, `new_label`, `seq`, `at`), the module-level
`fold()`, and the readers that all call it: `state()`, `acceptance(by)` and `export(path)`. Lineage queries go both
ways — `source_of(label_id)` (maker, inputs with hashes, time, version) and `made_by(**query)` (ids whose maker matches
every key, with list values meaning any-of). `history()` and `audit()` expose the trail for a single label, and
`export()` writes the rows plus a provenance sidecar naming the code version and hashed ledger files it read.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Complete the interface in `TASK.md`: decisions with undo, folded state, lineage queries
both ways, acceptance by source, export of accepted and corrected labels.

**Inferred user intent:** Reviewers and measuring tools must share one reading of the log, and decisions must be
revisable without losing history.

### What I did
- Implemented `fold(labels, events)`; `state()` is literally `dict(fold(...))`.
- `decide` validates: actor required (ValueError), decision in `DECISIONS` (ValueError), `correct` needs `new_label`
  (ValueError), unknown label id raises `KeyError`.
- `acceptance(by)` counts accepted+corrected over decided, per maker field value.
- `export` writes `[{"item", "label"}]` for accepted and corrected labels, plus `<path>.provenance.json`.

### Why
- Chapter note 5 (write the fold once): `state`, `acceptance` and `export` have no second implementation; there is one
  function and a test asserting `state() == fold(labels(), events())`.
- Notes 3 and 4 (keep rejections, undo is an event): rejections stay as `rejected` status and feed the denominator;
  `undo` is appended like any other event.
- Notes 6 and 10 (record who decided; corrections overlay): every event carries `actor`, and a correction is an event
  on top of the original proposal — `labels.jsonl` is never touched.
- Note 8 (sidecar): the export file stays a plain JSON list of rows, so the export's own provenance goes beside it.

### What worked
- Modelling `undo` as "pop the latest effective decision" made accept → correct → undo land on `accepted` with the
  original label, with no special cases in the fold.

### What didn't work
- N/A at this step; the failure came in the tests (Step 5).

### What I learned
- The chapter's fold sketch (`undo` deletes the item) and its prose ("cancels the latest decision") disagree; the
  prose is the better rule and the stack implements it for free.

### What was tricky to build
- `acceptance` had to hash non-string maker values (a band given as a number or a dict) so they can be dict keys;
  `_hashable()` JSON-encodes containers.

### What warrants a second pair of eyes
- The numerator choice (accepted + corrected) and the exclusion of pending labels from the denominator; also whether
  labels whose maker lacks the `by` field should be silently skipped (I skip them).

### What should be done in the future
- Write the test suite covering every public method, error path and fold edge case.

### Code review instructions
- `labelbook/ledger.py`: `fold`, `Ledger.decide`, `Ledger.acceptance`, `Ledger.export`.

## Step 4: Writing the test suite

I wrote `tests/test_ledger.py`: 38 tests in seven classes (`TestCreation`, `TestDecisions`, `TestLineage`,
`TestAcceptance`, `TestExport`, `TestFoldAndSchema`, `TestModuleSurface`), a 39th following in Step 6. Ledger directories are created under
`tests/_tmp` with `tempfile.mkdtemp(dir=...)` and removed in `tearDown`, so the tests never write outside the working
directory. The tests cover ids and persistence, every status, undo in three positions, all error paths, provenance
with and without real input files, `made_by` filtering (including list values), acceptance rates, export rows and
sidecar, malformed log lines, and the shared fold.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Cover the required interface and the pattern's edge cases with stdlib `unittest`.

**Inferred user intent:** Evidence that the library behaves as promised, including where the fold could disagree with a
second implementation.

### What I did
- Created `tests/test_ledger.py` with 38 tests and a base case class handling temp directories.
- Deliberately wrote tests for malformed log lines, unknown decisions and a hand-edited correction without
  `new_label`, because chapter note 5 names exactly those as places where independent folds drift.

### Why
- Chapter note 5 and the "Consequences" section: the fold's edge cases are the risk, so they are tested against the
  one implementation.

### What worked
- 37 of 38 tests passed on the first run.

### What didn't work
- First run: `python3 -m unittest discover -s tests -v` gave
  `FAIL: test_fold_ignores_malformed_lines_and_unknown_decisions` with
  `AssertionError: Lists differ: [] != [{'label_id': 'lbl-000001', 'decision': 'vandalise'}, {'label_id': 'lbl-000404', 'decision': 'accept'}]`
  (37 tests passed, 1 failed).

### What I learned
- The failure was in the test's assumption, not the library: `events()` is the log reader and drops only lines that
  are not JSON objects, while the *fold* is what rejects unknown decisions and unknown labels. Fix recorded in Step 5.

### What was tricky to build
- Keeping the tests inside the working directory: `tempfile.mkdtemp(dir=TMP_ROOT)` where `TMP_ROOT` is
  `tests/_tmp`, instead of the default `/tmp`.

### What warrants a second pair of eyes
- Whether `events()` should also filter semantically invalid events (see Step 5 decision).

### What should be done in the future
- Fix the failing test's expectation and re-run.

### Code review instructions
- `tests/test_ledger.py`, class `TestFoldAndSchema` for the log-robustness tests.

## Step 5: Fixing the failing log-robustness test

The failure was a mismatch between what I asserted and what the code should do. I changed the test to assert the
split responsibility explicitly: `events()` returns every well-formed JSON object (so a hand-edited log stays visible
for an auditor), and `state()`/`fold()` ignore unknown decisions and events for unknown labels. After the edit,
`python3 -m unittest discover -s tests` reported `Ran 38 tests in 0.026s` / `OK`.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Fix the one failing test and keep the design honest rather than bending the library to a
wrong assertion.

**Inferred user intent:** A green suite whose assertions describe intended behaviour.

### What I did
- Rewrote the assertions in `test_fold_ignores_malformed_lines_and_unknown_decisions` to check the log reader and the
  fold separately.
- Re-ran `python3 -m unittest discover -s tests`.

### Why
- Chapter note 5: the fold must not guess at an unknown decision or a malformed line; the log reader's job is only to
  drop lines it cannot parse at all, so the audit view does not hide a suspicious hand edit.

### What worked
- `Ran 38 tests in 0.026s` — `OK`.

### What didn't work
- The first version of the assertion (`self.assertEqual([], self.ledger.events())`) was wrong, quoted in Step 4.

### What I learned
- Making the reader and the fold have separate, stated responsibilities is what keeps an auditor able to see a bad
  log line while the state stays correct.

### What was tricky to build
- Nothing structural; only the distinction had to be written down in the test and in the `fold` docstring.

### What warrants a second pair of eyes
- `decide()` computes `seq` as `len(events()) + 1`, so a hand-edited log shifts the numbering; confirm that is
  acceptable (I chose visible numbering over tamper-proof numbering).

### What should be done in the future
- N/A.

### Code review instructions
- `labelbook/ledger.py: fold` docstring and `Ledger.events`; `tests/test_ledger.py: TestFoldAndSchema`.

## Step 6: Final check — full run, compile check and a scenario walk-through

I tidied `_version()` (module-level `sys` import), added one defensive guard in `stamp()` (a single path passed instead of a list is treated as one input rather than a sequence of characters) with a 39th test for it, then ran the suite again (`Ran 39 tests in 0.025s`, `OK`),
`python3 -m compileall -q labelbook tests` (clean) and a short scenario script in a temporary directory inside the
working directory. The scenario labelled 12 tiles from one agent in three confidence bands, accepted 4/5, 1/3 and 1/4,
and printed `{'high': 0.8, 'mid': 0.333, 'low': 0.25}` — acceptance by source band, which is the chapter's motivating
measurement — plus an export of 6 rows with its provenance sidecar.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Verify the whole thing end to end and make sure the diary is complete.

**Inferred user intent:** A finished, working deliverable with a diary that can be audited.

### What I did
- Ran `python3 -m unittest discover -s tests` → `Ran 39 tests in 0.025s` / `OK`.
- Ran `python3 -m compileall -q labelbook tests` → no output (clean).
- Ran an ad-hoc scenario script in `tempfile.mkdtemp(dir=".")`, then deleted the directory.
- Confirmed the ledger directory holds `labels.jsonl`, `events.jsonl`, `schema.json` and the export plus
  `out.json.provenance.json`.
- Removed `__pycache__` and `tests/_tmp` so only source files remain.

### Why
- The task asks for tests to be run and fixed before finishing, and the pattern's value only shows in a realistic
  measurement question (chapter, Motivation: 81 %, 47 %, 20 % acceptance by confidence band).

### What worked
- 39/39 tests pass; acceptance rates and export counts matched a hand calculation (high 4/5 = 0.8, mid 1/3, low 1/4).

### What didn't work
- N/A at this step.

### What I learned
- The whole measurement reduced to `acceptance("band")` because origin was stamped per label and rejections were kept
  as decisions — exactly the chapter's claim in "What made three things possible".

### What was tricky to build
- Nothing at this step; the scenario confirmed that filter (`made_by`) and measure (`acceptance`) use the same maker
  dict, so a faulty source can be found and excluded wholesale.

### What warrants a second pair of eyes
- Concurrent appends from two processes are not locked; two simultaneous `decide` calls could interleave a partial
  line (fold tolerates it by skipping, but a lock would be better).

### What should be done in the future
- Optional file locking for concurrent writers; archive/compact old event logs; a `reject_all(**query)` convenience for
  wholesale exclusion.

### Code review instructions
- Read `labelbook/ledger.py` top to bottom (schema → stamper → fold → ledger), then `tests/test_ledger.py`.
- Reproduce with `python3 -m unittest discover -s tests` from the working directory.

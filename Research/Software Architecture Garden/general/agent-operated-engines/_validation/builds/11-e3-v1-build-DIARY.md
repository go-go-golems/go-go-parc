# Diary

## Goal

Build `labelbook`, a standard-library-only Python 3 library that stores labels produced by people, agents and
detectors as provenance-stamped artefacts and reviewer decisions as an append-only log folded into current state, so
each source can be measured, excluded by origin, and every export audited. This diary records each phase of that
work, including failures.

## Step 1: Reading the chapter, the task and the diary format, then designing

I read `CHAPTER.md`, `TASK.md` and `DIARY-FORMAT.md` completely, then designed the module layout and the storage
format before writing code. The chapter's participants (provenance record, stamper, schema, decision event/log,
fold, lineage queries) map cleanly onto a package with one module each, so the mapping is visible in the file tree
instead of buried inside one class.

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

**Assistant interpretation:** Implement the `labelbook` library exactly as `TASK.md` specifies (the listed public
interface, JSON-lines files under one directory), applying the Lineage Ledger pattern from `CHAPTER.md`, with tests
run via `python3 -m unittest discover -s tests`, a diary in the strict format, and a final JSON report.

**Inferred user intent:** The requester wants a small, auditable, reproducible reference implementation that shows
the pattern actually applied — provenance stamped at creation, decisions appended and never edited, one shared fold —
verified by a real test suite, plus honest notes on where the chapter was unclear.

### What I did
- Read all three files in full (`read`), and listed the working directory: only the three markdown files exist.
- Designed the storage layout: `labels.jsonl` (provenance-stamped label records), `decisions.jsonl` (append-only
  decision events), `exports.jsonl` (export audit events), `schema.json` (field names, units, definitions).
- Designed the module split: `schema.py`, `provenance.py` (stamper + hashing + code version), `events.py` (event
  helpers + JSONL append/read), `fold.py` (the single fold), `ledger.py` (public `Ledger`), `__init__.py` (exports).
- Decided the semantics questions the chapter leaves open (see "What was tricky to build").

### Why
- "Stamp in every creating path, not in one" (note 1) and "write the fold once" (note 5) argue for a dedicated
  stamper module and a dedicated fold module rather than inline code in `Ledger`.
- Note 7 ("put definitions and units in the schema") argues for a real `schema.py` plus a written `schema.json`
  in the ledger directory, and a `schema` version field on every record.
- Note 9 ("hash inputs that may change") argues for recording `sha256`, size and mtime per input, not just a path.
- Note 6 ("record who decided") makes `actor` mandatory on every event, which is also what `TASK.md` requires.

### What worked
- The chapter's structure table gave a direct file plan; no redesign was needed after reading `TASK.md`.
- `TASK.md`'s interface list is precise about return shapes for `state()` (exactly `item`, `label`, `status`), which
  fixed an early idea of returning richer dicts there.

### What didn't work
- Nothing failed in this step; no commands were run beyond `ls` and `python3 --version` (Python 3.10.3, so I must
  avoid 3.11+ syntax such as `typing.Self` or `except*`).

### What I learned
- The chapter's sketch fold (`undo` deletes the item's state) and `TASK.md`'s wording ("`undo` cancels the latest
  decision on that label") disagree: the sketch would send `accept` → `correct` → `undo` back to `pending`, the task
  wants it back to `accepted`. The task wording wins; the fold must be a per-label stack of decisions.
- The chapter says readers fold the log themselves, which conflicts with note 5; I resolved it by making `fold.py`
  the only implementation and having `state()`, `acceptance()`, `export()` and `decide()`'s undo check all call it.

### What was tricky to build
- Not built yet, but the design problem identified: `state()` must reflect undo correctly, so the fold cannot be
  "last event wins" — it must pop on `undo`, and `decide(..., "undo")` must validate against the same fold rather
  than a second interpretation of the log.

### What warrants a second pair of eyes
- The undo-as-stack choice (versus the sketch's undo-as-delete) and the hedged error type for unknown label ids,
  which I plan to make both a `KeyError` and a `ValueError` because `TASK.md` does not say which one is expected.

### What should be done in the future
- Build the package modules, then the tests, then run them.

### Code review instructions
- Start with `CHAPTER.md` "Structure" and "Implementation notes", then read `labelbook/fold.py` and
  `labelbook/ledger.py`; validate with `python3 -m unittest discover -s tests`.

## Step 2: Building the package (schema, stamper, events, fold, ledger)

I wrote the five modules plus the package `__init__.py`: `schema.py` holds field names, units and definitions and
is mirrored to `schema.json` inside every ledger directory; `provenance.py` is the only stamper; `events.py` builds
events and appends them to JSON-lines files with `fsync`; `fold.py` is the single fold; `ledger.py` exposes
`Ledger` with `add_label`, `decide`, `state`, `source_of`, `made_by`, `acceptance`, `export` (plus `history`,
`records`, `events`). Storage is never cached in memory, so a second `Ledger` on the same directory sees the same
state.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Turn the design into working code, with the pattern's participants each in their own
place, before writing the test suite.

**Inferred user intent:** A working library first, so the tests test something real rather than being written
against a paper design.

### What I did
- Created `labelbook/schema.py`: `SCHEMA_VERSION = "labelbook/1"`, `FIELDS` (one entry per stored field with
  `type`, `unit`, `definition`), `FILES` (what each JSON-lines file holds), `schema()` returning a deep copy.
- Created `labelbook/provenance.py`: `stamp(maker, inputs)`, `validate_maker`, `describe_input` (sha256 + size +
  mtime, `missing` flag for absent paths), `hash_file`, `code_version()` (sha256 over the package `*.py`, cached),
  `utc_now()` / `timestamp_of()` (ISO-8601 UTC with `Z`), `MAKER_KINDS`.
- Created `labelbook/events.py`: `DECISIONS`, `make_event`, `append_jsonl` (append, flush, fsync),
  `read_jsonl` (missing file = empty log, malformed lines skipped).
- Created `labelbook/fold.py`: `fold_stacks`, `fold`, `status_of`, `label_value`, `current_state` — the only
  interpreter of the log in the package.
- Created `labelbook/ledger.py`: `Ledger` with `add_label`, `decide`, `state`, `source_of`, `made_by`,
  `acceptance`, `export`, `history`, `records`, `events`, `path_of`, plus `UnknownLabelError(KeyError, ValueError)`.
- Created `labelbook/__init__.py` exporting the public names.
- Ran a smoke script over a temporary ledger directory (add two labels from a detector and an agent, accept one,
  correct then undo the other, print `state`, `source_of`, `made_by`, `acceptance`, `export`).

### Why
- Note 1 ("stamp in every creating path"): `add_label` is the one creating path in this library, and it calls
  `stamp()` rather than assembling provenance inline, so any future creating path (an import tool, a preset apply)
  reuses the same stamper.
- Note 3 ("keep rejected suggestions as decisions"): rejections are ordinary events, so `acceptance()` can divide by
  decided labels; nothing filters rejections out of the log.
- Note 4 ("undo is an event"): `decide(..., "undo")` appends an `undo` event; no line is ever edited or removed.
- Note 8 ("use a sidecar when the artefact's format must not change"): `export` writes the plain JSON list the task
  requires plus a `<path>.provenance.json` sidecar and an `exports.jsonl` event, so the exported table stays
  readable by scripts that only want rows while remaining auditable.
- Note 10 ("corrections overlay; they do not rewrite"): a correction is an event; the proposed label stays in
  `labels.jsonl` and `state()` derives the corrected value, so exported rows and the original proposal can both be
  inspected.

### What worked
- The module split kept `ledger.py` readable: every query is a two-line composition of `records()`, `events()` and
  `current_state()`.
- `describe_input` recording `missing: True` with a null hash turned out to be useful in the tests: a vanished
  input is provenance, not a crash.

### What didn't work
- (Step 3 records the first real failure; the smoke script in this step ran only after a fix described below.)
- First run of the smoke script failed:
  `python3 - <<'PY' ... labelbook.Ledger ... PY` →
  `AttributeError: 'function' object has no attribute 'current_state'` at `labelbook/ledger.py:182` in `state()`.
  Cause: `ledger.py` did `from . import fold as fold_module`, but `__init__.py` had rebound the package attribute
  `fold` to the *function* `labelbook.fold.fold`, so the submodule lookup returned the function. Fixed by importing
  the names directly (`from .fold import current_state, fold_stacks`) and calling them unqualified.

### What I learned
- A package attribute and a submodule with the same name fight each other. Because I wanted both "the fold function"
  and "the fold module" to be reachable, I later renamed the package-level alias to `fold_events`
  (`labelbook.fold.fold` and `labelbook.fold_events` both work, `import labelbook.fold as m` still yields the
  module).
- The chapter says every reader should fold the log, and `TASK.md` demands `state()`, `acceptance()` and `export()`
  agree; routing all three through `current_state()` was cheap and removed the drift risk the chapter warns about.

### What was tricky to build
- Undo semantics: `undo` cancels the latest decision, so the fold keeps a stack per label and pops on `undo`. A
  corrected label that is undone therefore falls back to the *previous* decision (`accepted`), not to `pending`;
  `decide(..., "undo")` checks the same stack (`fold_stacks`) and raises `ValueError` when there is nothing to undo.
- Unknown label ids: `TASK.md` does not say whether `decide`/`source_of` should raise `KeyError` or `ValueError`.
  I derived `UnknownLabelError` from both and overrode `__str__`, so a caller catching either is correct.

### What warrants a second pair of eyes
- `acceptance(by)` skips labels whose maker lacks the field `by`; the denominator is decided labels only. Both
  choices are stated in the docstring but are the kind of thing a reviewer should confirm against intent.
- `code_version()` hashes the package sources, which makes every record's `version` change whenever the library is
  edited; that is the point, but it means test fixtures cannot hard-code it.

### What should be done in the future
- Write the tests under `tests/` and run them; check every requirement in `TASK.md` has one.

### Code review instructions
- Read `labelbook/fold.py` first (the only log interpreter), then `labelbook/ledger.py` (`add_label`, `decide`,
  `acceptance`, `export`), then `labelbook/provenance.py` (`stamp`, `describe_input`). Validate with
  `python3 -m unittest discover -s tests -v`.

## Step 3: Writing the test suite, running it, and fixing what failed

I wrote `tests/test_ledger.py` with 61 tests in seven groups: stamping, decisions, undo, the pure fold,
lineage queries, export, storage robustness, and one end-to-end review scenario. All test data is created inside
the repository (`.tmp-tests/<random>`), never in the system temp directory, and removed in `tearDown`. The first
run had two problems (one error, one failure), both fixed; the suite now passes.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Prove the required interface behaves as `TASK.md` says, including the awkward parts
(undo, per-source acceptance, export contents, state sharing between ledgers), by running real tests and fixing
failures rather than asserting correctness.

**Inferred user intent:** A suite that would catch the classic failures of this pattern: a missed stamp, an edited
log line, a second divergent fold, an export that leaks rejected or pending labels.

### What I did
- Created `tests/test_ledger.py` (61 tests): provenance fields and hashes, missing inputs, changed input → changed
  hash, maker copied not shared, validation of item/label/maker/inputs; accept/reject/correct/undo; `actor`
  required (`None`, `""`, `42`, and omission → `TypeError`); unknown decision; `correct` without `new_label`;
  `new_label` with `accept`; unknown label raising both `KeyError` and `ValueError`; the log growing with earlier
  lines byte-identical; `source_of`; `made_by` by one/many keys, no match, empty query; `acceptance` by confidence
  band (8/10, 5/10, 2/10 → 0.8, 0.5, 0.2), corrections counting as accepted, pending excluded, undo reverting the
  rate, missing field skipped; `export` contents, sidecar, export log, empty export, audit trail back to source;
  malformed and unknown-decision log lines skipped; duplicate label lines; two labels on one item; nested
  directory creation; `state()` keys exactly `item`, `label`, `status`; an end-to-end three-round review with a
  faulty source excluded via `made_by`.
- Ran `python3 -m unittest discover -s tests -v`.
- Fixed the two problems below, then re-ran, then added two more tests (`bad inputs are an error`, per-record
  `schema` version) after hardening `stamp()` against non-iterable `inputs`.

### Why
- The chapter's "Consequences" list (every creating path must stamp; logs grow; results must be reproducible) and
  the "Forces" (mutable state against history) name exactly the failure modes worth pinning down in tests.
- `TASK.md` says "a new `Ledger` on the same directory sees the same state", so several tests construct a second
  `Ledger` instead of trusting the in-memory object.

### What worked
- 59 of 61 tests passed on the first run, and the whole suite finishes in about 0.07 s.
- The pure-fold tests (`FoldTest`) pin the edge cases the chapter warns about (unknown decision, missing
  `new_label`, blank `label_id`, junk entries) without needing a directory.
- Final state: `Ran 61 tests ... OK`.

### What didn't work
- First run: `python3 -m unittest discover -s tests -v` →
  1 error and 1 failure out of 59 tests.
  - `ERROR: test_schema_is_written_with_units (test_ledger.StampingTest)` — my test bug: the test called
    `self.lines("labels.jsonl")` in a test that added no label:
    `FileNotFoundError: [Errno 2] No such file or directory: '.../.tmp-tests/ledger-2bv61hkl/labels.jsonl'`
    (at `tests/test_ledger.py:158`). Fixed by splitting it into a schema-content assertion and a new test
    `test_every_record_carries_its_schema_version` that adds a label and a decision first.
  - `FAIL: test_three_rounds_of_review_measure_each_source (test_ledger.EndToEndTest)` —
    `AssertionError: 5 != 4` (at `tests/test_ledger.py:561`). My arithmetic in the assertion was wrong, not the
    code: 3 agent labels (one corrected) + 1 surviving detector label + 1 person label = 5 rows. Fixed the
    expected count and replaced the misleading comment.
- Hardening pass: `self.ledger.add_label(..., inputs=5)` raised a bare `TypeError` from `tuple(inputs)` inside
  `stamp()`; `TypeError` is not what the rest of the library raises for bad arguments, so `stamp()` now converts it
  to `InvalidProvenance(ValueError)`.

### What I learned
- Writing the tests exposed an ambiguity I had guessed at: `made_by()` with no query returns every label, which is
  the natural reading of "matches every key of `query`" and useful for `len(made_by())`-style checks; a test now
  pins it.
- The task's export rule ("accepted and corrected") makes corrections count as accepted for `acceptance()` too;
  had I followed the chapter's looser "acceptance by confidence band" wording alone, corrections could have been
  counted as rejects and halved the measured agent rate.
- The chapter's sketch of the fold would have failed the undo tests (`accept` → `correct` → `undo` must return to
  `accepted`), which confirms the task wording, not the sketch, has to drive the implementation.

### What was tricky to build
- Getting `undo` to be both an appended event and a state reversal took three tests (`undo_returns_label_to_pending`,
  `undo_cancels_only_the_latest_decision`, `undo_twice_undoes_two_decisions`) before I was sure the stack fold was
  the right shape; a "delete the label's state" fold passes the first test and fails the second.
- Keeping the export auditable without breaking the required format: the row list stays `[{"item", "label"}]`, and
  lineage goes into the sidecar plus `exports.jsonl`, so the file another script reads is unchanged.

### What warrants a second pair of eyes
- The acceptance denominator (decided labels only) and the treatment of corrections as accepted — a domain
  reviewer should confirm both, since the chapter's gold-label example counted acceptance per suggestion, not per
  current state.
- `decide(..., "undo")` raises when there is nothing to undo; if the team prefers a no-op, that is a one-line change
  in `Ledger.decide`.

### What should be done in the future
- If a second reader (a scoring script, an export tool) appears, it should import `labelbook.fold`'s `current_state`
  rather than re-implementing the fold; note 5's warning is exactly this.

### Code review instructions
- Run `python3 -m unittest discover -s tests -v`; the interesting tests are `FoldTest` (pure fold edge cases),
  `UndoTest`, `LineageQueryTest.test_acceptance_*` and `ExportTest.test_export_is_stamped_with_a_sidecar`.

## Step 4: Final check — interface, clean run, no stray files

Last pass: confirm every name and signature in `TASK.md` exists exactly, re-run the suite on a clean tree, and make
sure nothing outside this directory was touched and no temporary files were left behind.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Verify the deliverable against the required interface list, and leave the directory
containing only source, tests and the diary (plus the three given markdown files).

**Inferred user intent:** Confidence that the library can be imported and driven by other code without surprises,
and that the work is self-contained.

### What I did
- Printed every required signature with `inspect.signature`; all match `TASK.md`:
  `Ledger(directory)`, `add_label(item, label, maker, inputs=())`, `decide(label_id, decision, actor, reason=None,
  new_label=None)`, `state()`, `source_of(label_id)`, `made_by(**query)`, `acceptance(by)`,
  `export(path, actor=None)` (the extra optional `actor` only stamps the export event).
- Removed `__pycache__` directories and the `.tmp-tests` scratch directory, then ran
  `python3 -B -m unittest discover -s tests` → `Ran 61 tests in 0.125s / OK`.
- Listed the tree: `labelbook/{__init__,events,fold,ledger,provenance,schema}.py`, `tests/test_ledger.py`,
  `DIARY.md`, plus the three supplied markdown files.

### Why
- The section "Required public interface (other code will be tested against it)" is a contract; signature drift is
  the one failure a passing test suite of my own would not catch.
- `-B` keeps the final tree free of bytecode, and all test data stayed inside `.tmp-tests` (removed afterwards),
  honouring "work only inside this directory".

### What worked
- The suite passes on a clean tree, with no network access, no third-party imports (only `datetime`, `functools`,
  `hashlib`, `json`, `os`, `pathlib`, `copy`, `tempfile`, `shutil`, `sys`, `unittest`).

### What didn't work
- No failures in this step.

### What I learned
- The `export(path, actor=None)` signature is a superset of the required one; that is the only place I extended the
  contract, and it is keyword-compatible with a call like `export("out.json")`.

### What was tricky to build
- N/A at this point; the tricky parts (undo as a stack, one shared fold, hashing inputs) were settled in Steps 2–3.

### What warrants a second pair of eyes
- `Ledger.__init__` creates the directory and writes `schema.json`; a reviewer should confirm that writing the
  schema beside the data is acceptable rather than pollution.
- Logs grow without bound (the chapter's own consequence); archiving old `decisions.jsonl` lines would need a
  watermark that this version does not have.

### What should be done in the future
- Add an optional `since` watermark or log rotation for long-lived batches, and a small CLI (`python3 -m labelbook`)
  that prints `acceptance` by source if the team wants one; neither is required by `TASK.md`.

### Code review instructions
- `python3 -B -m unittest discover -s tests` should print `OK` with 61 tests; then read `labelbook/fold.py` and
  `labelbook/ledger.py`, and `tests/test_ledger.py::EndToEndTest` for the whole flow.

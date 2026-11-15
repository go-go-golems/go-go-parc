# Diary

## Goal

Build `labelbook`, a standard-library-only Python 3 library that stamps every proposed label with its provenance
(person, agent or detector), records review decisions as an append-only event log, and derives current label state by
folding that log — so a team can measure each source, exclude one source's work, and audit any export. This diary
records each phase of design, building, testing and fixing.

## Step 1: Read the chapter, the task and the diary format; design the split

I read CHAPTER.md, TASK.md and DIARY-FORMAT.md in full, then fixed the module split and the concrete file layout before
writing any code. The chapter's participants map onto one module each, which keeps the "one fold, one matcher, one
stamper" rules physically visible rather than merely documented.

The on-disk design: a `schema.json` written beside the data, an append-only `labels.jsonl` (artefacts with required
provenance), an append-only `decisions.jsonl` (events ordered by a sequence number assigned inside the file lock), and
an `exports.jsonl` for export artefacts, plus a `<file>.provenance.json` sidecar per export bound to the file by a
content hash.

### Prompt Context

**User prompt (verbatim):** "You are a software engineer joining a project. Your working directory contains three files:
- CHAPTER.md: a chapter of a design-pattern book describing the pattern you must apply;
- TASK.md: the software to build, with its required public interface;
- DIARY-FORMAT.md: how to keep your work diary.
Read all three completely first. Keep DIARY.md as you go, one step per phase of work, in that format. Then design, build and test the software in this directory. Work only inside this
directory (do not read or write outside it). Use only the Python 3 standard library. Run your tests and fix what
fails before you finish, and make sure DIARY.md is complete. Your final message must follow the output format at the end of TASK.md."

**Assistant interpretation:** Implement the "Lineage Ledger" pattern from CHAPTER.md as the `labelbook` package with the
exact public interface listed in TASK.md, standard library only, tests under `tests/`, and a complete diary.

**Inferred user intent:** A reviewer wants to see the pattern applied faithfully (stamping at every creating path, an
append-only decision log, a single shared fold owning the status vocabulary, one maker matcher, locked appends and
schema beside the data) in code that passes its own tests and survives inspection against the chapter's implementation
notes.

### What I did
- Read all three files completely with the `read` tool.
- Decided the module layout before writing code:
  - `labelbook/schema.py` — field definitions, allowed maker kinds, decisions, status/fold vocabulary, schema file writer.
  - `labelbook/storage.py` — atomic write, single-write append under a file lock, JSON-lines reader.
  - `labelbook/provenance.py` — `stamp()` (the one stamper), input hashing, maker validation, ids, timestamps.
  - `labelbook/model.py` — `Artefact` (+ tolerant parsing of legacy lines without provenance).
  - `labelbook/fold.py` — `ItemState` and `fold()`, the only place that turns events into state.
  - `labelbook/lineage.py` — `field_value()` / `matches()` and the queries that use them (`source_of`, `made_by`,
    `acceptance`).
  - `labelbook/exporting.py` — stamped save + sidecar with content hash, and a reader that rejects a stale sidecar.
  - `labelbook/ledger.py` — the `Ledger` facade, the only public entry point.
  - `tests/` — API tests, fold law tests against a reference model, concurrency tests, export/sidecar tests.
- Planned the diary to be appended one step per phase, as the format demands.

### Why
- CHAPTER.md "Structure" lists exactly: provenance record, stamper, schema, lineage queries, decision event, decision
  log, fold, locked append. One module per participant makes each rule auditable; implementation notes 5 and 6
  ("write the fold once", "match makers in one place") are only checkable if those two functions have one home.
- TASK.md fixes the storage as "JSON lines under one directory", which decides the log design and makes a second
  `Ledger` on the same directory see the same state.
- Implementation note 10 (sidecar bound by content hash, and naming the labels it carries) plus note 1 (exports are
  creating paths too) decided the export design.

### What worked
- The chapter and the task agreed on the model (labels, decisions, fold, queries), so the interface in TASK.md maps
  one-to-one onto the chapter's sketch; no API invention was needed.
- Keeping the export in its own log (`exports.jsonl`) avoids polluting `state()`, which TASK.md defines as label id →
  `{item, label, status}` only.

### What didn't work
- N/A at this step (nothing executed yet).

### What I learned
- The chapter's `create(item, value, ctx)` returns an `Artefact`; the task's `add_label` returns only the id, so the
  artefact record needs a `to_record()`/`parse()` pair rather than being the return value.
- The chapter's fold reports two classes of problems (event for unknown artefact, undo with nothing to undo, unknown
  decision) that must not raise during a read: `state()` has to stay total and `problems()` must expose them.

### What was tricky to build
- Deciding where a sequence number is allocated. Implementation note 3 and 7 say "order by a sequence number, not the
  clock" and "ids assigned inside the lock", so `decide()` must read the log and append inside one lock scope; reading
  outside the lock would let two writers pick the same `seq`.

### What warrants a second pair of eyes
- `acceptance(by)` for maker values with zero decided labels: the chapter's formula divides by `count(decided)`, so a
  value with no decided labels needs a policy. I chose to include it with `0.0` rather than omit it.

### What should be done in the future
- Build the modules in the order schema → storage → provenance → fold → lineage → export → ledger, then tests.

### Code review instructions
- Start with `labelbook/ledger.py` for the public contract, then `labelbook/fold.py` and `labelbook/lineage.py` for the
  two shared functions, then `labelbook/storage.py` for the lock. Validate with
  `python3 -m unittest discover -s tests`.

## Step 2: Build the foundations — schema, storage, provenance, fold, lineage

I wrote the five modules that carry the chapter's invariants: the schema document written beside the data, atomic
writes plus locked single-write appends, the one stamper, the one fold, and the one maker matcher. Each allowed-value
list in the schema is checked at creation, and the fold is the only code that maps a decision to a status.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Implement the non-public building blocks first so the public `Ledger` is only wiring.

**Inferred user intent:** Every later query should read state through one fold and match makers through one function,
so reviewers can check the chapter's notes in one file each.

### What I did
- `labelbook/schema.py`: `MAKER_KINDS`, `LABEL_MAKER_KINDS`, `DECISIONS`, `STATUS_OF`, `DECIDED`, `ACCEPTING`,
  `FOLD_VERSION`, a `build_schema()` document with field definitions and units, `ensure_schema()` (writes only when
  missing), `load_schema()`, and `check_maker_kind()` / `check_decision()` which raise `ValueError`.
- `labelbook/storage.py`: `atomic_write()` (temp file + `os.replace`), `file_lock()` (`flock` plus a thread lock,
  Windows fallback), `append_record()` (one `os.write` with `O_APPEND` and `fsync`), `read_records()` (reads under the
  same lock), `append_under_lock()` (reads the log, builds the record, appends, all in one lock scope).
- `labelbook/provenance.py`: `new_id()` (uuid4 hex), `now_utc()`, `code_version()`, `hash_file()` (sha256 + size +
  mtime), `normalise_inputs()`, `normalise_maker()` (validates `kind`), `stamp()` (the one stamper),
  `unknown_provenance()`, `stamp_program()`.
- `labelbook/folding.py`: `ItemState` and `fold()` returning `(states, problems)`; order by `seq`; `undo` marks the
  latest live decision undone; status from the last live decision; label in force = last live correction else original.
- `labelbook/lineage.py`: `field_value()`, `matches()`, `source_of()`, `made_by()`, `acceptance()`, `exclude_from()`.
- `labelbook/model.py`: `Artefact` (provenance is a required constructor argument), `ExportArtefact`, tolerant
  `parse()` that turns a line without provenance into `kind: unknown`.

### Why
- CHAPTER.md "Structure" participants map one-to-one onto these modules; "Collaborations" 3–5 and implementation
  notes 1, 4, 5, 6, 7, 9, 11 are enforced here rather than documented only.
- Note 9: the schema goes into a file next to the log and every list of allowed values is checked at creation, so
  `kind: "oracle"` and `decision: "escalate"` are refused by the writer but still *reported* by the fold if they
  arrive in the log from elsewhere.
- Note 3: `seq` is not a timestamp; the fold sorts by `seq` so tests can shuffle events and still get the same state.
- Note 11: inputs are hashed by content, not recorded as a bare path.

### What worked
- `append_under_lock()` gives the sequence number and the append a single lock scope, which is exactly what note 7
  asks for, without a second read outside the lock.
- The fold's problem list already covers the three chapter cases (unknown label, undo with nothing to undo, unknown
  decision) with no guessing, and returns the fold version with each problem.

### What didn't work
- The first draft of `provenance.py` had an unbalanced brace in `unknown_provenance()`; it was corrected before the
  first run (a smoke import then compiles cleanly).
- My first design exported the fold from `labelbook/fold.py`; see Step 3 for why that name had to change.

### What I learned
- Reading a log while holding the same exclusive lock the writers use is the cheap way to make appends and reads
  consistent without an fsync-per-line protocol: the write is one `os.write`, the read cannot see half a record.
- A fold that returns `(states, problems)` instead of raising keeps `state()` total, which TASK.md's interface needs
  (it must always answer, even with a corrupt or legacy log).

### What was tricky to build
- Making provenance genuinely unskippable. `Artefact.__init__` raises if the provenance record has no `kind`, so a
  creating path that forgets to stamp fails immediately, and `Artefact.parse` can only produce `kind: unknown` for
  data that was already written — which `Ledger.unstamped()` counts (note 1).

### What warrants a second pair of eyes
- `file_lock()` holds an exclusive lock even for reads. Correct but not fast; with a large log every `state()` call
  locks. Acceptable for the task's size, and it removes a class of half-read records.
- The thread lock is per lock-file path inside one process; `flock` covers other processes. A forked child that
  inherits a lock file descriptor would still be serialised by the kernel, not by the parent's `threading.Lock`.

### What should be done in the future
- Wire the public `Ledger` on top, then write the tests that pin these laws.

### Code review instructions
- Read `labelbook/folding.py::fold` and `labelbook/lineage.py::matches` first; then check that every `kind`/`decision`
  written by `ledger.py` passes through `schema.check_*`.

## Step 3: Build the Ledger facade and the stamped export

I wired `Ledger` (add_label, decide, state, source_of, made_by, acceptance, export) over the modules of Step 2, and
made the export a creating path of its own: plain JSON rows for other tools, plus a sidecar bound to the bytes by a
content hash and carrying the ids and makers of the labels it exports.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Implement the exact public interface in TASK.md, keeping every write behind the stamper
and the log, and stamping exports too.

**Inferred user intent:** Other code can be tested against `labelbook.Ledger` directly, and an auditor can answer
"what made this?" for a label and for an exported file.

### What I did
- `labelbook/ledger.py`: `Ledger(directory)` creates the directory, writes `schema.json` if missing, and lazily reads
  `labels.jsonl`, `decisions.jsonl`, `exports.jsonl` on every call so a second `Ledger` sees the same state.
  `add_label` stamps then appends; `decide` validates the decision, the actor and `new_label`, checks the label exists,
  then allocates `seq` inside `append_under_lock`; `state()` maps the fold to `{id: {item, label, status}}`;
  `source_of`, `made_by`, `acceptance` delegate to `lineage.py`; `export(path, exclude=())` writes the rows, the
  sidecar and an export artefact.
- `labelbook/exporting.py`: `save_stamped()` and `load_stamped()` — a missing, unreadable or hash-mismatched sidecar
  makes the reader treat the file as unstamped.
- `labelbook/__init__.py`: exports `Ledger`, `Artefact`, `ItemState`, `fold`, `FOLD_VERSION`, the vocabulary constants,
  `load_stamped`/`save_stamped` and the stamper.
- Smoke-run of the whole API in a temp directory.

### Why
- Note 1 ("Exports and reports are creating paths too") and note 10 ("A derived file's sidecar also names whose work it
  carries") drove the export design; TASK.md's "JSON list of `{"item", "label"}`" ruled out inline provenance, which is
  exactly the sidecar case the chapter describes.
- Note 8: `decide` refuses a missing or blank actor, and the schema's `policy.anonymous` is `false` so the rule is
  visible to other tools.
- The export artefact lives in `exports.jsonl`, not in `labels.jsonl`, so TASK.md's `state()` contract stays label-only.

### What worked
- One smoke run showed the full flow: pending → accepted/rejected, `source_of` with hashed inputs, `made_by(kind=...)`,
  `acceptance("kind")`, an export with rows, a sidecar whose `carries` names each exported label's maker, and an empty
  problem list.

### What didn't work
- Exact command: `python3 -c "..."` (smoke run of the API) failed with
  `AttributeError: 'function' object has no attribute 'fold'` at `labelbook/ledger.py`, line 134 (`folding.fold(...)`).
  Cause: `labelbook/__init__.py` exported the *function* `fold`, which shadowed the submodule attribute `labelbook.fold`,
  so `from . import fold as fold_module` bound the function.

### What I learned
- Exporting a name that equals a submodule name silently changes what `from . import <name>` returns. The fix was to
  rename the module to `labelbook/folding.py` and keep exporting the function `fold` from the package.
- `state()` and `acceptance()` must not include export artefacts, otherwise "share of decided labels" would silently
  count exports as pending labels.

### What was tricky to build
- Binding the sidecar to the content: the hash must be taken over the exact bytes written, so `save_stamped()` hashes
  the text once, writes it, then writes the sidecar with that hash; `load_stamped()` re-hashes the file and returns
  `(data, None)` on any mismatch. Verified by rewriting the file in a test and seeing the sidecar ignored.

### What warrants a second pair of eyes
- `export(exclude=...)` accepts either an iterable of label ids or a maker query dict (`{"kind": "agent"}`); the dict
  path goes through `lineage.exclude_from`, which uses the same matcher. If a caller passes a bare string, it would be
  iterated as ids — worth a type check if this API is used widely.
- `decide()` re-reads the whole label log to check the id exists; fine at this scale, a per-directory id set would be
  the lazy fix.

### What should be done in the future
- Write the tests: interface, fold laws against a reference model, export/sidecar, concurrency.

### Code review instructions
- `labelbook/ledger.py`: `add_label` (stamping), `decide` (validation then `seq` under lock), `export` (stamp + sidecar).
  Validate with `python3 -m unittest discover -s tests`.

## Step 4: Write the tests, then run them and record the first failure

I wrote four test modules covering the public interface, the fold's laws against an independent reference model,
export/sidecar binding, and four concurrent writer processes. The first full run had one failure, in the concurrency
test's own expectation, not in the library.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** TASK.md wants tests under `tests/` run with `python3 -m unittest discover -s tests`, with
failing tests fixed before finishing.

**Inferred user intent:** Evidence that the interface behaves as specified and that the chapter's laws (undo,
corrections, replay, no shared ids, no stale sidecars) actually hold.

### What I did
- `tests/test_api.py` (23 tests): ids unique and pending on creation; statuses for accept/reject/correct; undo chains;
  every validation error (`ValueError` for unknown decision, missing blank/None actor, `correct` without `new_label`,
  `new_label` on accept, unknown label id, unknown maker kind, missing `kind`, non-dict maker); `source_of` fields and
  sha256 of an input file; `made_by` with one and several keys; `acceptance` excluding pending and undone decisions;
  persistence through a second `Ledger` (including `seq` continuing at 2); append-only log (old bytes are a prefix of
  the new file, no `undone` persisted); schema contents and not rewritten on reopen; unknown decision and ghost label
  reported as problems; legacy line without provenance counted by `unstamped()`.
- `tests/test_fold_laws.py` (11 tests): the four named laws, `undo` keeping history, order by `seq` not arrival,
  replay equality, 120 random sequences compared field by field against a second plain implementation, and a random
  sequence mixing unknown labels and an unknown decision.
- `tests/test_export.py` (9 tests): only accepted/corrected rows with exactly `{item, label}`; sidecar hash equals the
  sha256 of the file bytes; `carries` names each label's maker; export inputs hashed; export absent from `state()`;
  deleted sidecar and stale sidecar both read as unstamped; `exclude` by id and by source; empty ledger; undone
  acceptance not exported.
- `tests/test_concurrency.py` (2 tests): 4 forked processes × 25 labels, then 4 processes × 10 decisions, checking all
  100 ids are distinct and all `seq` values are `1..40`; plus a check that no line is torn.
- Ran `python3 -m unittest discover -s tests`.

### Why
- Note 4 asks for exactly this kind of test ("a small reference model on random sequences"); note 7 asks for the
  several-writers test; note 10 asks for the stale-sidecar case.
- Testing errors as `ValueError` matches TASK.md's explicit "A missing `actor` is an error (`ValueError`)".

### What worked
- 42 of 43 tests passed on the first run, including all the fold laws and the concurrency test's id/seq checks.
- The reference model caught nothing on the first run, which is the point: it is cheap insurance for later edits.

### What didn't work
- Exact command: `python3 -m unittest discover -s tests`, failure:
  ```
  FAIL: test_concurrent_writers_keep_every_label_and_every_sequence_number (test_concurrency.ConcurrencyTest)
  AssertionError: Items in the first set but not the second:
  'pending'
  Ran 43 tests in 0.112s
  FAILED (failures=1)
  ```
  The worker decided only on the first 10 of its 25 labels, so 60 labels were legitimately still `pending` and my
  assertion had wrongly demanded only `accepted`/`rejected`.

### What I learned
- The library behaviour was right and the test expectation was wrong: a status assertion on a partially reviewed
  ledger has to count statuses, not just compare the set.

### What was tricky to build
- Making the multi-process test share one directory: `multiprocessing.get_context("fork")` keeps the worker function
  importable and shares `sys.path`, so the child can build its own `Ledger` on the same files; the test skips when
  `os.fork` is unavailable.

### What warrants a second pair of eyes
- The concurrency test relies on process scheduling; it passed five repeated runs, but it is probabilistic by nature.
  A stress variant with more writers and repeated runs could be run before trusting the lock under load.

### What should be done in the future
- Fix the assertion and rerun the whole suite several times to catch flakiness.

### Code review instructions
- Run `python3 -m unittest discover -s tests -v` and read `tests/test_fold_laws.py::reference` — it is the second
  implementation the fold is checked against.

## Step 5: Fix the failing assertion and rerun the suite

I replaced the status-set assertion with counts (60 pending, 20 accepted, 20 rejected) and reran the suite five times
to check for flakiness in the concurrent test.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Fix what fails, keep the tests meaningful, then re-verify.

**Inferred user intent:** A green suite that a reviewer can trust, with the failure recorded rather than hidden.

### What I did
- Edited `tests/test_concurrency.py` to count statuses and to assert `statuses.count("pending") == len(ids) - len(flat)`,
  `accepted == len(flat) // 2`, `rejected == len(flat) // 2`, plus `problems() == []` and
  `acceptance("kind") == {"detector": 0.5}`.
- Ran `python3 -m unittest discover -s tests` five times: `Ran 43 tests ... OK` each time.
- Ran `python3 -m compileall -q labelbook tests` → `COMPILED`, and grepped the package imports to confirm only the
  standard library (`json`, `os`, `uuid`, `hashlib`, `tempfile`, `threading`, `fcntl`, `time`, `copy`, `dataclasses`,
  `contextlib`, `datetime`, `typing`) is used.

### Why
- A test that asserts a wrong expectation teaches nothing; counting statuses checks the same behaviour precisely and
  keeps the "only decided labels are exported/by acceptance" law visible.

### What worked
- Suite green five times in a row, including the fork-based concurrency test, and the package compiles cleanly.

### What didn't work
- N/A at this step.

### What I learned
- Counting statuses in the concurrency test also documents how much of the ledger is undecided, which makes the
  `acceptance == 0.5` assertion obvious rather than magic.

### What was tricky to build
- Nothing structural; the fix was a two-line change in the test plus recomputing the expected counts from
  `DECISIONS_PER_WRITER`.

### What warrants a second pair of eyes
- `acceptance()` returns `0.0` (not "absent") for a maker value whose labels are all pending; a reviewer may prefer
  omission. The choice is stated in the schema (`decided`/`accepting` lists) and in the docstring.

### What should be done in the future
- If the ledger grows, replace the full-log fold per query with a cached fold keyed on the last applied `seq`, and
  archive old decision logs (chapter, Consequences: "Logs grow").

### Code review instructions
- `tests/test_concurrency.py::test_concurrent_writers_keep_every_label_and_every_sequence_number` for the counts; run
  the whole suite with `python3 -m unittest discover -s tests`.

## Step 6: Review pass, three more tests, README, and the final run

I read the whole package again against the chapter, fixed two latent issues I found on the way (a read-order that
could report a phantom "event for unknown label" while another process writes, and a maker identifier named `version`
being shadowed by the stamp's own version), removed the helpers nothing used, and added a README. The suite is now 46
tests and green.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Make sure the finished code is coherent, documented and green, and that the diary is
complete before the final answer.

**Inferred user intent:** A reviewer opening the directory can see the pattern in the code, run one command, and get a
green suite.

### What I did
- `labelbook/ledger.py`: added `_snapshot()` (read events, then artefacts) and made `fold()`, `acceptance()` and
  `export()` fold one snapshot each; folded `export`'s exclude handling into one branch; simplified the export artefact
  id allocation.
- `labelbook/lineage.py`: `field_value()` now prefers a maker identifier over a stamp field with the same name
  (`version`, `at`), so a maker's own model/guideline version can be queried; removed the unused `fold_state` alias.
- `labelbook/model.py`: `Artefact` is a plain class with an explicit `__init__` that refuses a missing provenance record
  (relying on `@dataclass` keeping a hand-written `__init__` worked but was too subtle to keep); removed two unused
  status helpers.
- `labelbook/provenance.py`: removed an unused clock helper and its import.
- `labelbook/folding.py`: removed an unused vocabulary helper.
- Added `tests/test_api.py`: nested-directory construction, positional `decide(...)` with `new_label`, and maker
  identifier versus stamp field precedence — 46 tests in total.
- Wrote `README.md`: usage, the file layout under the ledger directory, the rules the code enforces and the test
  command.
- Ran the full suite, `python3 -m compileall -q labelbook tests`, and removed the `__pycache__` directories.

### Why
- Reading events before artefacts is the chapter's "one writer against several" concern applied to readers: a decision
  only ever refers to a label written before it, so the later read cannot miss it, and `problems()` stops reporting
  phantom unknown labels under concurrent writers.
- Note 6 says the matcher is the one place that reads maker fields, so the identifier-versus-stamp-field precedence
  belongs there and nowhere else.
- A README stating "no artefact without provenance" and the locked-append rule makes the pattern reviewable without
  reading every module.

### What worked
- `python3 -m unittest discover -s tests` → `Ran 46 tests in 0.113s / OK`, including the fork-based concurrency test
  and the random-sequence reference-model test.
- The precedence fix kept every earlier test green, so the query semantics for `kind`/`model`/`run`/`name` are unchanged.

### What didn't work
- N/A at this step (no failing command after the Step 5 fix).

### What I learned
- A hand-written `__init__` inside a `@dataclass` silently survives, because `dataclasses` never overwrites an existing
  attribute — correct but surprising; an explicit class says what it means.
- The chapter's "readers against writers" force is not only about folding in one place: the *order* two logs are read
  in decides whether a concurrent write shows up as a problem.

### What was tricky to build
- Keeping `state()` total while a decision log may contain junk: every branch of the fold either applies an event or
  appends a problem with the event and `foldVersion`, and nothing raises, so `state()`, `acceptance()` and `export()`
  all keep working on a corrupt log.

### What warrants a second pair of eyes
- `fold()` reads both logs on every query; with a large log this is the first thing to cache (keyed on the last applied
  `seq`). The behaviour is correct today, the cost is not bounded.
- `export(exclude={"kind": ...})` treats a dict as a maker query and a string as an iterable of ids; a string passed by
  mistake would be iterated character by character.

### What should be done in the future
- Add a cached fold and decision-log archiving when the log grows; consider `LOCK_SH` for reads to let concurrent
  `state()` calls run in parallel.

### Code review instructions
- `labelbook/ledger.py` (public contract), `labelbook/folding.py` (the fold and the vocabulary),
  `labelbook/lineage.py` (`field_value`/`matches` and the three queries), `labelbook/storage.py` (the lock and the
  single append). Validate with `python3 -m unittest discover -s tests`; 46 tests should pass.

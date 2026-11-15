# Diary

## Goal

Build `jailfs`, a standard-library-only Python 3 package that gives agent-written programs exactly one writable
directory plus read-only roots, with every path resolved through operating-system root-relative, no-follow file
operations; this diary records the design decisions, the failures and the fixes.

## Step 1: Reading the chapter, the task and the diary format

I read `CHAPTER.md`, `TASK.md` and `DIARY-FORMAT.md` in full before writing anything. The chapter is Chapter 8,
"Contained Workspace": one writable root, read-only roots that must not overlap it, a locator that maps an agent's
path to (root, relative name) *lexically*, a root handle that walks the path one component at a time with `dir_fd=`
and `O_NOFOLLOW`, a writer that creates a random name exclusively and renames it into place, plus optional shadow,
opened-set and loader participants.

### Prompt Context

**User prompt (verbatim):** "You are a software engineer joining a project. Your working directory contains three files:
- CHAPTER.md: a chapter of a design-pattern book describing the pattern you must apply;
- TASK.md: the software to build, with its required public interface;
- DIARY-FORMAT.md: how to keep your work diary.
Read all three completely first. Keep DIARY.md as you go, one step per phase of work, in that format. Then design, build and test the software in this directory. Work only inside this
directory (do not read or write outside it). Use only the Python 3 standard library. Run your tests and fix what
fails before you finish, and make sure DIARY.md is complete. Your final message must follow the output format at the end of TASK.md."

**Assistant interpretation:** Implement the `jailfs` package and its tests exactly as `TASK.md` specifies, applying
the pattern and implementation notes of `CHAPTER.md`, keeping a phase-by-phase diary.

**Inferred user intent:** A working, tested library whose containment survives the five holes the chapter lists
(symlink escape, overwriting an opened input, planted temporary names, an alternative loader, a repeated root flag),
with evidence in the diary that each fix is really tested.

### What I did
- Read the three input files end to end; listed the working directory (`CHAPTER.md`, `DIARY-FORMAT.md`, `TASK.md`).
- Checked the environment: Python 3.10.3, Darwin (macOS), so `os.open(..., dir_fd=..., O_NOFOLLOW)` and
  `os.stat(..., dir_fd=..., follow_symlinks=False)` are available; `os.Root`/`openat2` are not, which is exactly the
  "walk one component at a time from the root's directory handle" case in implementation note 1.

### Why
- The pattern's participants (start-up check, roots, locator, root handle, writer, shadow check, opened set, loader)
  are needed parts of the required interface: `absolute paths must lie inside a root` needs the locator;
  `read` of a relative name needs the lookup order; `save` needs the writer plus the two optional checks; `load` is
  the one loader; `names()` needs the writable root handle.

### What worked
- The chapter's sketch maps almost one-to-one onto the required interface, so the design was quick to fix:
  `Workspace` = start-up check + roots; a private `Root` (given/real path + directory fd) = root handle;
  `Location(root, rel)` = locator result; `_write_atomic` = writer; `_opened`/`_written` = opened set;
  `_shadowed` = shadow check; `load` = loader; `_batch_saved` = per-run duplicate check.

### What didn't work
- N/A in this step (no code run yet).

### What I learned
- Python's standard library has no `os.Root`, so containment must be built from `os.open`/`os.stat` with `dir_fd=` and
  `O_NOFOLLOW`; the chapter says so explicitly and warns against string checks as a fallback.

### What was tricky to build
- Deciding the shape of the locator: the chapter requires the agent's path *never* to be resolved (`realpath`), only
  normalised lexically, while the roots are resolved once at start-up. That means absolute paths must be matched
  against *both* the root's given spelling and its resolved spelling — planned as a lexical, longest-prefix match over
  `(root.given, root.real)` for every root.

### What warrants a second pair of eyes
- The lookup order decision for a relative name that is a link inside the writable root: I will refuse immediately
  instead of falling through to the read roots, so an agent cannot use the writable root as a trampoline.

### What should be done in the future
- Write the package (`jailfs/errors.py`, `jailfs/workspace.py`, `jailfs/__init__.py`), then the tests, then the
  mutation checks of implementation note 11.

### Code review instructions
- Start with `jailfs/workspace.py`: `Workspace.__init__` (start-up check), `_locate_write`/`_absolute_parts`
  (locator), `_walk_dirs`/`_open_file` (root handle), `_write_atomic` (writer). Validate with
  `python3 -m unittest discover -s tests`.

## Step 2: Building the package — roots, locator, handle, writer

I wrote the package: `jailfs/errors.py` (the `Refused` exception with `code` and `fix`), `jailfs/workspace.py`
(the workspace itself) and `jailfs/__init__.py` (the exported names). The design follows the chapter's Structure
table almost term for term: `Workspace.__init__` is the start-up check, `Root` is the root handle (given spelling,
resolved spelling, one directory fd), `Location(root, rel)` is the locator result, `_walk_dirs`/`_open_file` are the
root-relative walk, `_write_atomic` is the writer, `_opened`/`_written` are the opened set, `_shadow_in` is the shadow
check, `load` is the one loader and `_batch_saved` is the per-run duplicate check.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Build the package behind the exact public interface of TASK.md, with containment enforced
by the kernel and every refusal carrying a code and a fix.

**Inferred user intent:** An interface another code base can be tested against (`Workspace`, `read`, `save`, `load`,
`names`, `batch`, `Refused` with `code`/`fix`) that actually contains agent programs.

### What I did
- Created `jailfs/errors.py`: `E_ACCESS`, `E_NOT_FOUND`, `E_DUPLICATE`, `E_SHADOW`, and `Refused(code, message, fix)`
  whose `str()` is `"CODE: message (fix: ...)"`; an unknown code is a `ValueError`.
- Created `jailfs/workspace.py`:
  - `Root(path, writable)`: `given = os.path.abspath(path)`, `real = os.path.realpath(given)`, and a lazily opened
    directory fd (`O_RDONLY | O_DIRECTORY | O_NOFOLLOW | O_CLOEXEC`) — links resolved once, at start-up.
  - `Workspace.__init__`: refuses a list/tuple `root`, refuses `reads` given as a bare string, refuses a missing or
    non-directory root/read root, then refuses overlapping roots (writable↔read both directions, and read↔read) by
    comparing *resolved* paths component-wise.
  - `_normalise`: lexical only — collapses `.`/empty components, pops on `..`, refuses a climb above the root,
    refuses a path that names the root itself, refuses NUL bytes. The agent's path is never `realpath`ed.
  - `_absolute_parts`: lexical longest-prefix match of `os.path.normpath(path)` against `(root.given, root.real)` for
    every root; outside everything is `E_ACCESS` with a fix naming the roots and `reads=[DIR]`.
  - `_walk_dirs`: opens each directory component relative to the previous fd with `O_NOFOLLOW | O_DIRECTORY`, so the
    kernel refuses `..`, links and escapes; with `create=True` it `os.mkdir(..., dir_fd=...)`s missing parents and
    re-opens them without following a link.
  - `read`: candidate list is `[writable, read1, read2, ...]` for a relative name (one candidate for an absolute
    one); a `E_NOT_FOUND` falls through to the next root, any other refusal (`E_ACCESS` from a link, a directory, a
    non-regular file) stops the lookup immediately; a successful read adds `(st_dev, st_ino)` to `_opened`.
  - `save`: `_locate_write` (writable root only, `E_ACCESS` for a read root), then `_inspect_target` (link →
    `E_ACCESS`, directory → `E_ACCESS` with a fix naming `rel/labels.json`, non-regular → `E_ACCESS`), then
    `E_DUPLICATE`, then `E_SHADOW`, then the opened-set check, then `_write_atomic`.
  - `_write_atomic`: create `.jailfs-tmp-<hex>` with `O_CREAT | O_EXCL | O_NOFOLLOW` in the target's own directory
    (a planted file or link is skipped, never followed), write, `fsync`, close, `os.rename(..., src_dir_fd=...)`,
    then `lstat` the result and add its identity to `_written`.
  - `load`: extension check (`.py`/`.js`), then `read()` (so it goes through the locator and joins the opened set),
    then UTF-8 decoding.
  - `names`: recursive `os.listdir(fd)`/`os.stat(dir_fd=..., follow_symlinks=False)` walk from the writable root's
    handle; directories, links, fifos and devices are never listed.
  - `batch()`: context manager that swaps in a fresh set of saved names (nestable, restored in `finally`).
- Created `jailfs/__init__.py` exporting `Workspace`, `Refused`, the four codes, `Location`, `Root`,
  `LOAD_EXTENSIONS`, `TEMP_PREFIX`, `CODES`.
- Smoke-tested by hand: save into a nested new directory, read from both roots, a shadowed save, `load`, and a `..`
  climb, all refused or served as intended.

### Why
- CHAPTER implementation note 1: Python has no `os.Root`, so the walk one component at a time from the root's
  directory handle with `dir_fd=` and `O_NOFOLLOW` is the containment. No string check is used as a fallback.
- Note 2: roots resolved once; absolute agent paths matched lexically against both spellings so a `/var` →
  `/private/var` root is reachable under either name while every link *below* the root is still seen by the walk.
- Note 3: roots kept disjoint at start-up (a nested read root would be writable through a relative save).
- Note 4: exclusive, random temporary name plus rename; a hard link to an input cannot carry a write because rename
  replaces a name and leaves the old inode alone.
- Note 5: identities, not names; the written exemption is taken *after* the rename so a session may re-save its own
  output; hard-linked files are not refused.
- Note 6: the shadow check compares the *resulting relative name*, so absolute and `sub/../` spellings are caught.
- Note 7: `load` is the only loader; there is no `require`-like attribute on `Workspace`.
- Note 8: a list/tuple root is refused with a fix that names `reads=[DIR]` — the Python form of "`--root` once".
- Note 9: `Location.label` shows a writable-root file by its relative name and a read-root file by its absolute name,
  and refusals use it.
- Note 10: refusals are reported in the fixed order shape → access → duplicate → shadow → replacing an opened file.

### What worked
- The whole interface fell out of the chapter's sketch; the smoke test passed on the first run for save/read/load,
  the shadow refusal and the `..` refusal.

### What didn't work
- Nothing failed in this step: the hand-written smoke script printed
  `['out/a.json']`, `b'{}' b'ro' b'ro'`, `E_SHADOW | choose another name: ...`, `print(1)` and
  `E_ACCESS E_ACCESS: '../x' climbs above the root (...)`.

### What I learned
- `O_NOFOLLOW` only applies to the last component of the path passed to `open`, which is exactly why the chapter
  insists on opening every component separately; a single `os.open(root_path + "/" + rel)` would follow an interior
  link. The component walk is not a stylistic choice, it is the fix.
- `rename`-over-a-name also made me re-read note 5: the link refusal is about the *agent's view* (and clear
  refusals), not only about containment — after the fact the mutation check in Step 5 proved it.

### What was tricky to build
- Deciding what a relative name that is a link inside the writable root does: falling through to the read roots would
  let an agent use the writable root as a trampoline and would also make a refusal depend on lookup order, so any
  non-`E_NOT_FOUND` refusal from a candidate root stops the lookup. The same rule keeps a directory in the writable
  root from silently falling through to a file of the same name in a read root.
- Keeping `fds` bookkeeping right in `_walk_dirs`: every exit path closes what it opened (verified later by a
  descriptor-count probe in Step 6).

### What warrants a second pair of eyes
- `_absolute_parts` picks the *longest* matching base across all roots and both spellings; with disjoint roots this
  is unambiguous, but the reasoning deserves a review.
- `_shadow_in` treats "cannot tell" (e.g. a link in the read root's parent chain) as `False`; the read would refuse
  that name anyway, but the code path is worth a look.

### What should be done in the future
- Write the tests: one module per area, with temporary directories only.

### Code review instructions
- `jailfs/workspace.py`: read `__init__` → `_normalise`/`_absolute_parts` → `_walk_dirs`/`_open_file` →
  `save`/`_inspect_target`/`_write_atomic` → `load`/`names`/`batch` in that order. Validate with
  `python3 -m unittest discover -s tests`.

## Step 3: Writing the tests

I wrote `tests/harness.py` (a temporary tree with `work`, `read1`, `read2` and an `outside` directory, plus
`assertRefused(code, fn, ...)` which also requires a non-empty `fix`) and five test modules: `test_startup.py`,
`test_read.py`, `test_save.py`, `test_holes.py` (the chapter's five holes as regression tests) and `test_edges.py`.
The first full run had three failures in my own test code, recorded in Step 4.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Cover the interface and every hole the chapter names, using temporary directories, and
run the suite with `python3 -m unittest discover -s tests`.

**Inferred user intent:** Tests that would catch a regression of any of the five holes, not tests that merely execute
the happy path.

### What I did
- `tests/harness.py`: `setUp` creates `<tmp>/{work,read1,read2,outside}` (all resolved with `realpath`), a
  `Workspace`, and registers `close()`/cleanup; helpers `put`, `get`, `link`, `exists`, `assertRefused`.
- `tests/test_startup.py` (21 tests): list/tuple root refused with a fix naming `reads=`, bare-string `reads`,
  missing/non-directory roots, read root inside writable root, writable inside read, same directory twice, nested and
  duplicate read roots, overlap through a symlinked spelling, `pathlib.Path` roots, symlinked root reachable by its
  real spelling, `describe()`, closed-workspace refusals, idempotent `close()`.
- `tests/test_read.py` (42 tests): lookup order (writable first, then read1, then read2), absolute paths inside each
  root, absolute outside, the root itself, climbs, interior `..`, directory/non-regular shapes, five link cases
  (in-root, to a read root, dangling, symlinked parent, absolute spelling), `names()` recursion/sorting/links,
  `load()` from each root, extension, link, outside-root, non-UTF-8 and opened-set cases.
- `tests/test_save.py` (40 tests): creation, parents, replacement, empty bytes, bytearray/memoryview, text refused,
  absolute save, no temporary leftovers, read-only root, outside, climbs, directory, file-as-parent, link cases, hard
  link, duplicate/batch cases, shadow cases (relative, absolute, `sub/../`), opened-set cases, ordering.
- `tests/test_holes.py` (23 tests): one class per hole of the chapter's table, plus a boundary sweep of twelve
  adversarial paths and an "ordinary work still works" case.
- `tests/test_edges.py` (added right after the first run, then extended; 19 tests): fifos, lexical prefix pitfalls (`work2` vs `work`, `work-other`), permission
  refusals (skipped as root), shadow granularity, `Refused` formatting, and the macOS `/var` → `/private/var` root
  spelling.
- Ran `python3 -m unittest discover -s tests`; 124 tests, three failures in test code (Step 4).

### Why
- The chapter's Motivation table lists five holes; each gets its own class so it can be mutated individually
  (note 11: "Check each test, not a group").
- Temporary directories only, as TASK.md requires; every test also asserts that the escape target outside the roots
  was not created or not modified.

### What worked
- The harness made the adversarial cases short: planting a dangling link or a symlinked parent is three lines, so the
  sweep covers twelve paths cheaply.

### What didn't work
- See Step 4: three of the first 124 tests failed, two because of bugs in the test code and one because of a wrong
  expectation about a trailing slash.

### What I learned
- A trailing slash is not a directory test in this design: `_normalise` drops empty components, so `"work.json/"`
  reads the file. That is consistent (the agent's path is lexical) and was worth removing from the sweep rather than
  special-casing in the library.

### What was tricky to build
- Testing planted temporary names deterministically. The random name has to be made predictable without weakening the
  library, so the tests patch `jailfs.workspace._random_name` with a `side_effect` list whose first value is the
  planted name and whose later values are free ones.

### What warrants a second pair of eyes
- The fifo tests: `O_NONBLOCK` keeps the read from blocking, but on a platform without `mkfifo` they skip silently.

### What should be done in the future
- Implementation note 11: verify each regression test goes red without its fix.

### Code review instructions
- `tests/harness.py` first, then `tests/test_holes.py` (the claims about holes) and `tests/test_save.py` (the
  refusal order). Run `python3 -m unittest discover -s tests -v`.

## Step 4: First full run fails — three failures, all in the tests

`python3 -m unittest discover -s tests` ran 124 tests with 1 failure and 2 errors. All three were in test code, but
each taught me something about the interface.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Run the suite, read every failure, fix the cause (in the library when the library is
wrong, in the test when the test is wrong).

**Inferred user intent:** A green suite that is green for the right reasons.

### What I did
- Ran `python3 -m unittest discover -s tests` and read the three tracebacks.
- Fixed `Case.put` usage in `tests/test_holes.py`, gave the patched `_random_name` a full list of attempts, replaced
  the trailing-slash sweep case, then re-ran.
- Added `tests/test_edges.py` afterwards; that run had one failure (`test_a_read_root_whose_name_prefixes_the_writable_root`),
  which I fixed by testing `"<root>2"` instead — a directory that shares a string prefix with the root but is not a
  root.

### Why
- Each fix restores the property the test claims to test rather than weakening the assertion.

### What worked
- After the first fixes: `Ran 139 tests ... OK`. After the edge-case fix: `Ran 145 tests ... OK`.

### What didn't work
- Exact failure 1 (test code):
  `ERROR: test_a_planted_regular_file_is_never_reused (test_holes.Hole3PlantedTempNameTest) ... TypeError: Case.put()
  takes from 3 to 4 positional arguments but 5 were given` — I had passed `(root, "out", "planted", b"planted")`
  where the helper takes `(directory, name, data)`.
- Exact failure 2 (test code):
  `ERROR: test_every_attempt_refused_is_a_refusal_not_an_escape ... File ".../unittest/mock.py", line 1165, in
  _execute_mock_call result = next(effect) / StopIteration` — the writer retried more often than the three planted
  names I gave the mock.
- Exact failure 3 (wrong expectation):
  `FAIL: test_sweep (test_holes.BoundarySweepTest) (method='read', args=['work.json/']) ... AssertionError: Refused
  not raised` — the lexical locator drops the empty component, so `"work.json/"` names the file `work.json`.
- Exact failure 4 (my own edge test was wrong):
  `FAIL: test_a_read_root_whose_name_prefixes_the_writable_root (test_edges.LexicalPrefixTest) ... AssertionError:
  Refused not raised` — I had made `"<root>-reads"` a *read root* in that workspace, so reading inside it was
  legitimately allowed; the test proved nothing.

### What I learned
- A test that asserts a refusal must be checked against the *reason* for the refusal; failure 4 was a vacuous test
  that would have passed for the wrong reason had I written the assertion differently. That is exactly the trap
  implementation note 11 warns about, and it is why Step 5 exists.
- The refusal message and the code (not just "something was refused") are what make a test meaningful.

### What was tricky to build
- `assertRefused` requires a code *and* a non-empty `fix`; the wrong-code cases (e.g. `E_SHADOW` where `E_ACCESS` was
  expected) surfaced as clear diffs instead of "some refusal happened".

### What warrants a second pair of eyes
- `tests/test_holes.py::BoundarySweepTest` asserts `self.assertFalse(self.exists("/tmp/jailfs-escape.json"))` — it
  writes nothing, but a reviewer should confirm the path is never created by a mutated build either.

### What should be done in the future
- Mutation-check every regression test.

### Code review instructions
- `git diff`-free project: compare `tests/test_holes.py` (Hole3, BoundarySweep) and `tests/test_edges.py`
  (LexicalPrefixTest) with Step 3's description. Validate: `python3 -m unittest discover -s tests`.

## Step 5: Mutation checks — five tests were vacuous, and that changed the fix I was testing

I wrote `tools/mutation_check.py` (implementation note 11): it copies `jailfs/` and `tests/` into a temporary
directory, requires every named test to pass unmutated, then deletes one fix at a time and requires *each* named test
to go red on its own. The first run reported five vacuous tests and two mistakes in my anchors; fixing them meant
changing the library's test setup *and* one test's expectation, and it exposed a real redundancy in the design.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** For every fix in the library, find the test that goes red when the fix is removed, one
test at a time; a test that stays green is a vacuous test.

**Inferred user intent:** Believable regression coverage — evidence, not assertion, that the boundary is defended.

### What I did
- `tools/mutation_check.py`: 14 mutations (delete the not-a-plain-file refusal; write in place instead of renaming;
  hole 1 as found — both at once; drop `O_EXCL`; drop the opened-set check; drop the shadow check; drop the duplicate
  check; drop the disjoint-roots check; resolve the agent's path with `realpath`; follow links in the component walk;
  accept a list of roots by keeping the last one; match only the resolved root spelling; drop the regular-file check
  on reads; drop the climb check). Each names the tests that must go red; the script runs them one by one and fails
  if any stays green, and it also fails if a mutation anchor does not occur the expected number of times.
- First run: `46 checks, 5 failures`, all `VACUOUS`, plus `mutation anchor ... found 3 times ..., expected 2`.

### Why
- Note 11 is explicit: "Twice, goja-cv's first test for a hole passed without it ... Check each test, not a group".

### What worked
- After the fixes: `48 checks, 0 failures` — 24 named tests green in the baseline, each red under its mutation.

### What didn't work
- Exact text: `mutation anchor '                             os.O_RDONLY | _O_DIRECTORY | _O' found 3 times in
  jailfs/workspace.py, expected 2` — the `_collect` walk has that line too, so the expected count is 3.
- Exact text: `mutation anchor '        if not _stat.S_ISREG(st.st_mode):' found 2 times in jailfs/workspace.py,
  expected 1` — the 8-space anchor is a substring of the 16-space line in `_open_file`; I extended both anchors to two
  lines each.
- Five vacuous tests, exactly as note 11 predicts:
  - `test_save_onto_an_in_root_link_is_refused`, `test_save_onto_a_dangling_link_creates_nothing_outside`,
    `test_holes...test_a_link_to_a_read_root_input_cannot_be_written_through` stayed green when I deleted only the
    `S_ISLNK` refusal, because the `not S_ISREG` refusal right after it refuses symlinks anyway. The honest mutation
    is to delete the whole "not a plain file" refusal, which is what the code now says explicitly.
  - `test_holes...test_save_through_a_dangling_link_creates_nothing_outside` stayed green when I deleted the link
    refusal but kept the rename. That is not a test bug — it is the chapter's note 5 in action: with exclusive
    creation plus rename, the write cannot reach the link's target even if the refusal is gone. So the mutation for
    hole 1 must restore the old design (no plain-file refusal *and* a write in place), which is now mutation `m03`,
    and it goes red.
  - `test_the_same_via_the_absolute_path_of_the_link` stayed green under the `realpath` mutation because the link
    pointed into a *read* root, so resolving it produced an "inside a read-only root" refusal — the right code for
    the wrong reason. I moved that test under the plain-file mutation and made the `realpath` mutation rely on the
    two tests whose link targets are *inside* the writable root.
- Two of the five vacuous cases turned out to be confounded by the shadow check: the link tests used the name
  `labels.json`, which also exists in the read root, so deleting the link refusal produced `E_SHADOW`. I renamed the
  link targets to `tile.json` (not present in a read root) and added
  `test_a_link_is_refused_before_the_shadow_check`, which pins the refusal order of note 10 (access before shadow).

### What I learned
- Redundancy between the link refusal and the regular-file refusal is fine for the agent (the message names the
  link) but it hides which fix a test pins. Naming the mutation after the *behaviour* ("not a plain file") rather
  than after one line made the tests honest.
- The chapter's claim that the opened-file set is about the agent's view, not containment, is testable: the dangling
  link and hard link tests stay green when only the refusal is deleted but the rename stays, and go red when the
  write is done in place. That is the strongest evidence in the whole suite that the writer's shape matters.

### What was tricky to build
- Making a mutation restorable enough to run "each test on its own": the copy-per-mutation plus
  `python3 -m unittest tests.mod.Class.method` (with a temporary `tests/__init__.py` in the copy so the module is
  importable, and the `try: from harness import Case / except ImportError: from tests.harness import Case` fallback in
  every test module) keeps the real suite dependency-free.

### What warrants a second pair of eyes
- Whether `m09` ("resolve the agent's path") is the most faithful mutation of note 2; a reviewer could also mutate
  `Root.given` to `real`, which `m12` does.
- The baseline requires 24 specific tests to be green; adding a test to a mutated class does not automatically join a
  mutation, which is a maintenance risk.

### What should be done in the future
- Re-run `python3 tools/mutation_check.py` whenever a fix in `jailfs/workspace.py` changes shape, and add a mutation
  for any new fix.

### Code review instructions
- `tools/mutation_check.py` (`MUTATIONS` list: each tuple is name → textual mutation → the tests that must go red).
  Validate: `python3 tools/mutation_check.py` (about 1 s per mutation).

## Step 6: Final check — descriptor probe, full suite, review

I re-read `jailfs/workspace.py` against the chapter's eleven implementation notes, ran a descriptor-count stress
probe (the component walk opens fds on every call), and re-ran the suite and the mutation check from a clean start.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Leave the project in a state where one command shows everything green, with no leaks
and no unhandled exceptions.

**Inferred user intent:** Confidence that the delivered library is correct and tested, not just written.

### What I did
- Stress probe: 500 iterations of save/read/read-from-read-root/load/two refused reads/two refused saves/names; printed
  `fds before: 6 after: 6`.
- `python3 -m unittest discover -s tests` → `Ran 145 tests ... OK`.
- `python3 tools/mutation_check.py` → `baseline: 24 named tests checked, 0 problems` and `48 checks, 0 failures`.
- Final re-read of the refusal order, the fd bookkeeping in `_walk_dirs`/`_open_file`/`_lstat_in_root`/`_collect`, and
  the temporary-file error path (`unlink` on any exception, `EEXIST`/`ELOOP` retried up to 64 times).

### Why
- Note 1's walk opens and closes fds on every operation, so a leak would show up as `EMFILE` under a long agent run,
  not as a wrong answer.
- Note 10's fixed refusal order is only meaningful if every refusal happens in that order on every path, so it is the
  last thing to verify by reading.

### What worked
- No descriptor growth, no unclosed files, no `OSError` escaping the public API in any test (every OS error is mapped
  through `_refuse_oserror`), and both commands green.

### What didn't work
- Nothing failed in this step.

### What I learned
- The `_opened`/`_written` sets are only as good as the identity taken after the rename; taking it inside
  `_write_atomic` after `os.rename` (rather than before) is what makes "re-save your own output" work while a file
  read from the writable root stays protected.

### What was tricky to build
- Nothing new in this step; the tricky parts were the locator's spelling match (Step 2) and the vacuous tests
  (Step 5).

### What warrants a second pair of eyes
- `names()` walks the writable root recursively with no depth limit; a very deep tree of directories planted by a
  program is not bounded (no file count, no depth). A reviewer may want a cap.
- `Workspace` keeps one directory fd per root for the session and never re-validates that the root path still points
  at the same inode; a root directory deleted and re-created mid-session is not noticed. The fd keeps the *old*
  directory contained, which is the safe direction, but `ws.root` would then name a different directory.

### What should be done in the future
- If an agent runtime needs it: a documented cap on `names()` (depth/count), and a `save_many`-style batch that
  reports several refusals at once in the chapter's fixed order (today only the first is reported, as in goja-cv).

### Code review instructions
- Read `jailfs/errors.py`, then `jailfs/workspace.py` in file order; run
  `python3 -m unittest discover -s tests` and `python3 tools/mutation_check.py`. `DIARY.md` Steps 4 and 5 record the
  exact failures and the exact error text of every fix.

# Diary

## Goal

Build `jailfs`, a standard-library Python package that gives agent-written programs confined file access: one writable
directory plus read-only dataset directories, with every refusal raised as a `Refused` error carrying a machine-readable
`code` and an actionable `fix`. This diary records the design decisions, the build steps, the failures met while
testing, and how each failure was fixed.

## Step 1: Reading the task and designing the jail

I read `TASK.md` and `DIARY-FORMAT.md` completely, then designed the library before writing code. The core decision was
to treat *every* link below a root as hostile: all lookups and writes walk down from an already-trusted root directory
descriptor with `openat`-style calls and `O_NOFOLLOW`, so a link planted earlier in the writable directory can never
redirect a read or a write outside the roots, not even in a race.

### Prompt Context

**User prompt (verbatim):** "You are a software engineer joining a project. Your working directory contains two files:
- TASK.md: the software to build, with its required public interface;
- DIARY-FORMAT.md: how to keep your work diary.
Read both completely first. Keep DIARY.md as you go, one step per phase of work, in that format. Then design, build and test the software in this directory. Work only inside this
directory (do not read or write outside it). Use only the Python 3 standard library. Run your tests and fix what
fails before you finish, and make sure DIARY.md is complete. Your final message must follow the output format at the end of TASK.md."

**Assistant interpretation:** Implement the `jailfs` package exactly as specified in `TASK.md` (Workspace, Refused,
read/save/load/names/batch and the four error codes), with tests under `tests/`, running them until green, and keep a
diary in the strict format of `DIARY-FORMAT.md`.

**Inferred user intent:** A trustworthy sandbox primitive for an agent runtime: agent programs must be able to do
useful work with datasets and helper code while being structurally unable to corrupt or exfiltrate anything outside
their writable directory, and every denial must tell the agent what to do instead.

### What I did
- Read `TASK.md` and `DIARY-FORMAT.md` (both short, read in full).
- Listed the working directory: only the two markdown files were present.
- Sketched the module layout: `jailfs/errors.py` (Refused + codes), `jailfs/fsops.py` (descriptor-relative,
  no-follow filesystem primitives), `jailfs/workspace.py` (the Workspace policy layer), `jailfs/__init__.py`
  (public exports), plus `tests/`.
- Decided the refusal codes and the precedence order used by `save`.

### Why
- The task is a security boundary, so the design is driven by `TASK.md`'s refusal list: outside the roots, through a
  link, a read-only root, or replacing a file this session read. There is no `CHAPTER.md` in this directory, so
  `TASK.md` was the only design authority; where it was silent I recorded a guess (see below).
- Splitting low-level `openat` primitives from policy keeps each function small enough to review for escape bugs.

### What worked
- The layout maps one-to-one onto the required interface, so the public API can stay tiny (`Workspace`, `Refused`).
- Standard-library support for `dir_fd` on `os.open`/`os.stat`/`os.mkdir`/`os.replace` covers everything needed.

### What didn't work
- Nothing failed in this step; no commands beyond `ls` were run.

### What I learned
- `TASK.md` does not say which code a construction-time refusal should use; the code list has no config code, so
  `E_ACCESS` is the only coherent choice.
- macOS temp directories sit behind the `/var -> /private/var` link, so roots must be `realpath`-ed once at
  construction or every containment test would be wrong.

### What was tricky to build
- Nothing built yet. The tricky part identified in design is that `save` must not write *through* an existing inode:
  a hard link inside the writable root pointing at a dataset file would leak a write into the dataset even though the
  path is inside the root. Plan: refuse links at the final component and write via exclusive temp file + `os.replace`
  by name (which replaces the directory entry, never the shared inode).

### What warrants a second pair of eyes
- The precedence among `E_ACCESS` (read file), `E_SHADOW` and `E_DUPLICATE` when several rules could fire for the
  same `save` call.
- Whether refusing *all* link traversal (even links that stay inside a root) is too strict.

### What should be done in the future
- Implement `errors.py`, then `fsops.py`, then `workspace.py`, then the tests.

### Code review instructions
- Start with `TASK.md` for the contract, then read `jailfs/workspace.py` (policy) and `jailfs/fsops.py` (mechanism).
- Validate with `python3 -m unittest discover -s tests`.

## Step 2: The refusal type and the descriptor-level primitives

I built the bottom two layers first: `jailfs/errors.py` (the `Refused` exception and the four codes) and
`jailfs/fsops.py` (every filesystem call the package is allowed to make). Keeping all `os` calls in one module means the
security-relevant code is about 250 lines that can be audited on its own.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Implement the error contract (`code`, `fix`) and the low-level, symlink-hostile
filesystem helpers the `Workspace` policy will be built on.

**Inferred user intent:** Every denial must be a single exception type a runtime can pattern-match on, and no code path
may ever resolve a path in a way that a planted link can redirect.

### What I did
- Created `jailfs/errors.py`: `E_ACCESS`, `E_NOT_FOUND`, `E_DUPLICATE`, `E_SHADOW`, `ALL_CODES`, and `Refused(code,
  message=None, fix=None, path=None)` with `__str__`/`__repr__` built from those attributes.
- Created `jailfs/fsops.py`: `as_text_path`, `split_relative`, `is_within`, `open_file_at`, `path_exists_at`,
  `open_parent_for_write`, `write_atomic`, plus the private `_open_child_dir`/`_walk_dirs` walkers.
- Every walk starts at a `realpath`-ed root and opens one component at a time with `dir_fd` + `O_NOFOLLOW`; the code
  never passes a multi-component path to `open`.
- Saves write an exclusive temp file (`O_CREAT|O_EXCL|O_NOFOLLOW`, random name) and `os.replace` it over the target
  name with `src_dir_fd`/`dst_dir_fd`, so no existing inode is ever written through, and the temp file is unlinked on
  any failure.

### Why
- `TASK.md` requires exactly four codes and a `fix` string; `Refused` is the only channel for refusals.
- The `openat` + `O_NOFOLLOW` approach is what makes "through a link" a *structural* refusal rather than a `realpath`
  comparison that a concurrent rename could defeat.
- Temp-file-then-rename is the only way to make a save safe against hard links: `rename` replaces a directory entry
  and leaves every other name for that inode untouched.

### What worked
- `os.open`, `os.stat`, `os.mkdir`, `os.unlink` and `os.replace` all accept `dir_fd`/`src_dir_fd`/`dst_dir_fd` on this
  platform, so descriptor-relative walking needed no fallbacks.
- Error classification via a follow-up `lstat` distinguishes "missing", "regular file in the way" and "symbolic link"
  on both macOS (ENOTDIR for `O_NOFOLLOW|O_DIRECTORY` on a link) and Linux (ELOOP), without weakening the `open`.

### What didn't work
- Nothing failed in this step; the primitives were exercised by hand only through Step 3.

### What I learned
- `rename` does not follow a link in the destination position, which is exactly the property needed for a safe save.
- `os.fchmod` lets a replacement file keep the permissions of the file it replaces; otherwise a save would silently
  reset a `0640` file to the umask default.

### What was tricky to build
- File-descriptor lifetimes. Every early return (`missing path`, `not a regular file`) has to close the descriptor of
  the directory it was walking, or a long agent run leaks descriptors. The final shape uses `_walk_dirs` returning the
  holding descriptor and `try/finally` blocks that close exactly once; `open_parent_for_write` uses a `done` flag so
  the descriptor is closed only when ownership was not transferred.

### What warrants a second pair of eyes
- The `finally` blocks in `open_file_at`/`_walk_dirs`: confirm no path double-closes or leaks a descriptor.
- `write_atomic`'s cleanup path when `os.write` fails half-way.

### What should be done in the future
- Build the `Workspace` policy layer on top of these primitives.

### Code review instructions
- Read `jailfs/fsops.py` top to bottom; every `os.*` call with a name argument must carry `dir_fd` and `O_NOFOLLOW`.
- Sanity check with `python3 -c "import jailfs.fsops"` and the full suite.

## Step 3: The Workspace policy layer

I built `jailfs/workspace.py` and `jailfs/__init__.py`: construction validation, the read search path, path
normalisation, shadowing, batch duplicate tracking, read protection, and `names()`.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Put the required public interface (`Workspace`, `Refused`) on top of the primitives,
implementing the exact lookup order and the four refusal codes.

**Inferred user intent:** An API small enough for an agent to use blindly, whose defaults are safe and whose errors
name the next step.

### What I did
- `Workspace.__init__`: refuses list/tuple/set/dict roots with `E_ACCESS`, resolves the root and every read directory
  with `realpath`, requires them to be existing directories (`E_NOT_FOUND` otherwise), de-duplicates reads keeping
  order, and refuses writable/read-only overlap in either direction with `E_ACCESS`.
- `read`/`load`: relative names are looked up in the writable root, then each read directory in order; absolute names
  are normalised lexically and must fall inside the longest matching root. Both record the real path and the
  `(st_dev, st_ino)` identity of the file they return.
- `save`: validates the destination, applies `E_SHADOW` / `E_DUPLICATE` / read-protection checks in a documented
  order, then writes through `fsops.write_atomic`.
- `names()`: recursive `os.scandir` over the writable root, skipping links and directories, returning sorted
  `/`-separated relative names.
- `batch()`: a re-entrant context manager that keeps one set of saved names per run and clears it on exit, including
  when the agent program raises.
- `jailfs/__init__.py` exports `Workspace`, `Refused` and the four codes.

### Why
- `TASK.md` fixes the search order ("writable root, then read directories in order") and the absolute-path rule; the
  longest-prefix match is needed because a read directory may be nested under another configured root.
- Read protection is session-wide (the `Workspace` instance), because `TASK.md` says "a file this session read" and
  describes a batch separately as "one agent program's run".

### What worked
- The interface matches `TASK.md` one-to-one, and the policy layer needed no `os` calls of its own beyond `scandir`.

### What didn't work
- My first draft of `workspace.py` had `_check_reads` as a `staticmethod` that referred to a class attribute
  `_in_progress_root` that was never set, so the overlap check could never see the writable root. I found this by
  rereading the file before running anything and rewrote `_check_reads` as an instance method that uses `self._root`;
  no command was run against the broken draft.

### What I learned
- Path *policy* and path *mechanism* are cleanly separable: the policy layer only ever decides "which root and which
  components", and the walker guarantees those components cannot be links.

### What was tricky to build
- The absolute-path rule. `os.path.normpath` is applied before containment so `/root/../etc/passwd` is compared as
  `/etc/passwd` and refused, while `/root/sub/../file.txt` still resolves inside the root. Containment uses a
  separator-aware prefix test, so a sibling named `root-elsewhere` is not treated as inside `root`.
- Deciding that a link met in the writable root during a *relative* lookup is a hard `E_ACCESS` rather than "fall
  through to the next read directory": falling through would silently answer a different question than the agent
  asked, which hides the probe instead of reporting it.

### What warrants a second pair of eyes
- The refusal precedence in `save` (documented in its docstring): path checks, then `E_SHADOW`, then `E_DUPLICATE`,
  then read-protection/link/directory checks.
- `names()` uses ordinary `scandir` on the real root path; confirm that skipping links there cannot hide a file the
  API can still read.

### What should be done in the future
- Write the test suite and let it challenge these decisions.

### Code review instructions
- Start at `Workspace.save` (policy order) and `Workspace.read`/`_absolute_target` (containment).
- Run `python3 -m unittest discover -s tests` once the tests exist.

## Step 4: Tests and the first failing run

I wrote three test modules (98 tests in total: `tests/test_workspace.py`, `tests/test_security.py`, with shared
fixtures in `tests/support.py`) and ran them. The first run had three failures and one error; three were mistakes in
the tests themselves and one was a real ordering question.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Cover the required interface plus the boundary probes the task describes, run the suite,
and fix what fails.

**Inferred user intent:** Evidence that the jail actually holds, not just that the happy path works.

### What I did
- `tests/support.py`: a `JailTestCase` that builds a temporary `base/` with `root/`, `data/`, `lib/` and `outside/`
  (all `realpath`-ed), plus `put`, `content` and a `refused(code, func, ...)` helper that also asserts `fix` is a
  non-empty string.
- `tests/test_workspace.py`: construction refusals, round-trips, parent creation, Unicode and bytes paths, search
  order, absolute paths, `names()`, `load()`, `batch()` semantics, and the `Refused` contract.
- `tests/test_security.py`: traversal, links to datasets/outside/inside, linked directories, dangling links, links
  inside read directories, read-only roots, shadowing, hard links, read protection, and a "planted state" scenario.
- Ran `python3 -m unittest discover -s tests -v` (95 tests at that point).

### Why
- `TASK.md` explicitly warns that agents probe boundaries and that files in the writable directory may be links
  planted earlier, so the security module mirrors that story instead of only testing the four codes.

### What worked
- 91 of 95 tests passed on the first run, which showed the walker and policy agreed on the common paths.

### What didn't work
- `python3 -m unittest discover -s tests -v` reported `Ran 95 tests in 0.089s` / `FAILED (failures=3, errors=1)`.
  - `ERROR: test_writable_root_wins_over_read_directories (test_workspace.TestReadSearchPath)` —
    `jailfs.errors.Refused: E_SHADOW: 't.csv' already exists in the read-only directory '.../data' (fix: pick a
    different name; the dataset copy stays read-only)`. My test tried to `save` a name that already existed in a
    read directory, which `E_SHADOW` correctly forbids; the writable-root shadowing behaviour is only observable for
    files that are already in the writable root. Fixed by planting `root/t.csv` directly with the test's `put`
    helper instead of using `save`.
  - `FAIL: test_links_planted_before_the_session_are_all_refused (test_security.TestPlantedState)` —
    `AssertionError: 'E_SHADOW' != 'E_ACCESS'` for `save("train.csv")` where a planted link `root/train.csv` pointed
    at `data/train.csv`. Both refusals are true. I kept `E_SHADOW` for the name collision (the message "pick a
    different name" is the one that unblocks the agent) and documented the precedence in `save`'s docstring; the test
    now asserts `E_SHADOW` for that one name and `E_ACCESS` for the pure link cases.
  - `FAIL: test_multiple_roots_are_refused_at_construction_not_later (test_workspace.TestConstruction)` —
    `AssertionError: 'one writable' not found in 'create one Workspace per writable directory and pass datasets in
    reads='`. A test assertion that was too literal; relaxed it to check for the word "writable".
  - `FAIL: test_overlapping_roots_are_refused (test_workspace.TestConstruction)` — `AssertionError: 'E_NOT_FOUND' !=
    'E_ACCESS'`. The test passed a non-existent sub-directory as the root, so the missing-directory refusal fired
    before the overlap refusal; the test now creates the directory first.

### What I learned
- The `E_SHADOW` vs `E_ACCESS` overlap is genuinely ambiguous in `TASK.md`; whichever fires, the refusal is correct,
  so the choice should be documented rather than guessed at silently.
- Testing through the public API means a test can accidentally trigger a *different* correct refusal; fixtures that
  write directly to the roots are needed to observe precedence.

### What was tricky to build
- The "planted state" fixture: a previous session leaves a link named exactly like a dataset file, a link to a dataset
  directory, and a link to a file outside every root. The test asserts all reads and writes through them refuse, that
  the dataset and the outside directory are byte-identical afterwards, and that ordinary saves still succeed.

### What warrants a second pair of eyes
- Whether `E_SHADOW` should win over a final-component symlink, as it now does when both are true.

### What should be done in the future
- Harden the two remaining gaps found while writing the tests: trailing-separator saves and hard-linked targets.

### Code review instructions
- Run `python3 -m unittest discover -s tests -v`; the three modules are independent and each class maps to one rule.

## Step 5: Hardening after writing the tests

While writing the boundary tests I found three gaps between "safe" and "obviously safe", and closed them: a save whose
path ends in `/`, a save that would replace a hard-linked file, and absolute paths that spell a root the way it was
configured (`/var/...`) rather than the way it really is (`/private/var/...`). One test then failed for an instructive
reason and was fixed.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Turn the safe-but-silent behaviours into explicit refusals, and make sure the jail works
with the path spellings a real runtime hands out.

**Inferred user intent:** No surprising silent action near a boundary, and no false refusals that would make the
library unusable on the host platform.

### What I did
- `save` now refuses a path ending in a separator with `E_ACCESS` ("ends with a separator and names a directory") for
  both relative and absolute spellings, instead of silently creating the file `sub`.
- `save` now refuses to replace an existing file with `st_nlink > 1` (`E_ACCESS`, "is a hard link: another name
  shares this file, possibly a dataset"). Read protection is checked first so the more specific "file this session
  read" message still wins for files the session handed out.
- `Workspace` now records, for the writable root and every read directory, both the configured spelling
  (`os.path.abspath`) and the real path, and `_absolute_target` picks the longest matching spelling and then walks
  from the *real* root with `O_NOFOLLOW`. A root that is itself a link (the macOS `/var` situation) is therefore
  usable under either spelling while links below the root are still refused.
- Updated `save`'s docstring to spell out the precedence order and added tests for each new refusal.

### Why
- `TASK.md` says a save writes inside the writable root and that a link is `E_ACCESS`; hard links are the one link
  kind a path check cannot see, so they need an explicit inode check.
- The macOS spelling problem is not in `TASK.md` but would have made absolute paths unusable for any caller using
  `tempfile.mkdtemp()`; the fix keeps the boundary intact because only the trusted root prefix is alias-matched.

### What worked
- `Ran 98 tests in 0.086s` / `OK` after the trailing-separator and hard-link changes.
- A direct smoke test of the macOS case: `Workspace(tempfile.mkdtemp())` followed by
  `ws.read(os.path.join(d, "a.txt"))` and `ws.read(os.path.join(os.path.realpath(d), "a.txt"))` both returned `b'x'`,
  where before the alias change the `/var/...` spelling would have been refused.

### What didn't work
- `python3 -m unittest discover -s tests` reported `Ran 98 tests in 0.088s` / `FAILED (failures=1)`:
  `FAIL: test_hard_link_to_an_unread_dataset_file_is_refused (test_security.TestReadProtection)` —
  `AssertionError: 'E_SHADOW' != 'E_ACCESS'` / `: unexpected refusal: Refused(code='E_SHADOW', message="'costly.csv'
  already exists in the read-only directory '.../data' ...")`. The test hard-linked the dataset file under the *same*
  name, so the (also correct) shadow refusal fired first. Fixed by hard-linking it under a different name
  (`shortcut.csv`), which is the case that actually needs the inode check; the test now passes and the dataset is
  verified byte-identical.

### What I learned
- Each new refusal rule needs a test whose only trigger is that rule, otherwise a neighbouring rule masks it.
- The refusal precedence in `save` is now: path validity (including trailing separator) -> shadow -> batch duplicate
  -> read protection -> hard link -> link/directory in the way. It is written down in the docstring so a reviewer does
  not have to reverse-engineer it.

### What was tricky to build
- Alias matching without weakening the jail: the alias is only used to compute the *relative* remainder of the path;
  the walk that actually touches the file starts at the real root and still opens every component with `O_NOFOLLOW`.
  A test (`test_alias_spelling_does_not_allow_links_below_the_root`) proves that passing
  `<linkroot>/peek.csv`, where `peek.csv` is a link planted inside the root, is still `E_ACCESS`.

### What warrants a second pair of eyes
- The `st_nlink > 1` refusal: it is stricter than `TASK.md` literally requires and could refuse a legitimate
  replacement of a multiply-linked file inside the writable root.
- `_absolute_roots` alias matching when a caller supplies both spellings for two different roots.

### What should be done in the future
- If the runtime ever needs to rewrite a read file, it must construct a new `Workspace` (a new session); there is no
  unlock API, by design.

### Code review instructions
- Read `Workspace.save` (ordering), `Workspace._absolute_target` and the alias construction in `__init__`.
- Validate with `python3 -m unittest discover -s tests` (expect 100 tests) and the macOS smoke test above.

## Step 6: Final check

I ran the complete validation once more from a clean interpreter, confirmed the file inventory, and verified that the
diary covers every phase.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Finish by proving the suite is green, the tree contains only the intended files, and the
diary is complete in the required format.

**Inferred user intent:** A deliverable that can be trusted without re-running the work from scratch.

### What I did
- `python3 -m compileall -q jailfs tests` -> `COMPILE_OK` (no syntax errors, no stray imports).
- `python3 -m unittest discover -s tests` -> `Ran 100 tests in 0.094s` / `OK` (64 in `tests/test_workspace.py`,
  36 in `tests/test_security.py`).
- `find` on the tree confirmed only `jailfs/{__init__,errors,fsops,workspace}.py`, `tests/{support,test_workspace,
  test_security}.py`, `DIARY.md` and the two supplied markdown files.
- Re-read `DIARY.md` against `DIARY-FORMAT.md`: every step has all twelve sections, failures are quoted verbatim with
  the command that produced them.

### Why
- `TASK.md` requires the tests to be run and fixed before finishing, and the diary to be complete.

### What worked
- Full suite green on the first run of this step; no cleanup needed beyond confirming there are no leftovers.

### What didn't work
- Nothing failed in this step.

### What I learned
- No new insight; the earlier steps had already flushed out the ordering questions.

### What was tricky to build
- Nothing new was built in this step.

### What warrants a second pair of eyes
- The one deliberately conservative rule (`st_nlink > 1`) and the documented `E_SHADOW`-before-link precedence, since
  both are places where `TASK.md` allows more than one correct answer.

### What should be done in the future
- If the runtime needs `unlink`, `rename` or directory listing of read roots, they should be added with the same
  descriptor-walk treatment rather than by broadening the existing methods.

### Code review instructions
- Start with `jailfs/__init__.py` for the exported surface, then `jailfs/workspace.py`, then `jailfs/fsops.py`.
- Validate with `python3 -m unittest discover -s tests`; expect `Ran 100 tests` and `OK`.

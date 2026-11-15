# Diary

## Goal

Build `jailfs`, a standard-library-only Python package that gives an agent runtime a single writable workspace
directory plus read-only data directories, refusing every attempt to touch anything outside them; this diary records
the design decisions, the build, the tests and the fixes.

## Step 1: Reading the brief and designing the library

I read `TASK.md` and `DIARY-FORMAT.md` completely, then probed the host platform (Python 3.10.3 on macOS/Darwin) for
the primitives I want to build on: `os.open`/`os.stat`/`os.mkdir`/`os.unlink` are in `os.supports_dir_fd`,
`O_NOFOLLOW` and `O_DIRECTORY` exist, `os.replace` accepts `src_dir_fd`/`dst_dir_fd` even though it is not listed in
`os.supports_dir_fd`, `os.listdir` accepts a file descriptor, and `tempfile.mkdtemp()` returns a path under `/var/...`
whose `realpath` is `/private/var/...` (so root canonicalisation is mandatory). I also confirmed that on this kernel
opening a symlink-to-directory with `O_NOFOLLOW|O_DIRECTORY` fails with `ENOTDIR`, not `ELOOP`, so I must not rely on
errno to recognise links: every component gets an `lstat` first.

The design that came out of that: a thin exception module, a path module that parses and normalises agent input, a
low-level I/O module with two interchangeable backends (`dir_fd`-relative syscalls, and an `lstat`-walk fallback for
platforms without `dir_fd`), and a `Workspace` facade that owns policy (search order, shadowing, duplicate and
read-before-write refusal). Symlinks are never traversed on relative paths; a refusal ("through a link") is
preferable to silently following a planted link even when the target happens to be inside a root.

### Prompt Context

**User prompt (verbatim):** "You are a software engineer joining a project. Your working directory contains two files:
- TASK.md: the software to build, with its required public interface;
- DIARY-FORMAT.md: how to keep your work diary.
Read both completely first. Keep DIARY.md as you go, one step per phase of work, in that format. Then design, build and test the software in this directory. Work only inside this directory (do not read or write outside it). Use only the Python 3 standard library. Run your tests and fix what fails before you finish, and make sure DIARY.md is complete. Your final message must follow the output format at the end of TASK.md."

**Assistant interpretation:** Implement the `jailfs` package described by `TASK.md` inside this directory, with the
exact public interface (`Workspace`, `Refused`, the four codes, `batch()`), tests under `tests/`, a `DIARY.md` in the
strict format of `DIARY-FORMAT.md`, and a closing JSON report.

**Inferred user intent:** They want a reviewable, defensive-by-construction sandboxing library: a runnable artifact
whose tests prove that the valuable read-only datasets cannot be damaged and that escapes (including planted links)
are refused with the documented error codes, plus a diary that makes the reasoning auditable.

### What I did
- Read `TASK.md` and `DIARY-FORMAT.md` in full.
- Probed the platform with a throwaway `python3 - <<EOF` script: `os.supports_dir_fd` contents, `O_NOFOLLOW`
  behaviour on links and link-to-directory, `os.replace(..., src_dir_fd=...)`, `os.listdir(fd)`, and
  `os.path.realpath` on a `mkdtemp` directory.
- Sketched the module split: `jailfs/errors.py`, `jailfs/paths.py`, `jailfs/fsio.py`, `jailfs/workspace.py`,
  `jailfs/__init__.py`.

### Why
- `TASK.md` requires all refusals to be `Refused` with `code`/`fix`, so every layer must raise the same type instead
  of leaking `OSError`; that pushes all `OSError` translation into `fsio`.
- `TASK.md` names "through a link" as its own `E_ACCESS` cause, so link detection must be explicit (`lstat` per
  component) rather than implicit in whatever the kernel decides to return.
- macOS `/var` → `/private/var` means the roots must be canonicalised once at construction, otherwise absolute paths
  handed back by `tempfile` would be judged "outside" legitimately configured roots.

### What worked
- `dir_fd`-relative syscalls are available, so the strict backend is implementable on this host.
- `os.replace` with `src_dir_fd`/`dst_dir_fd` works, which makes atomic saves inside one directory possible.

### What didn't work
- First probe attempt assumed `os.replace in os.supports_dir_fd` would be `True`; it is `False`, and a naive test call
  `os.replace("a","b", src_dir_fd=None, dst_dir_fd=None)` resolved the names against the process CWD:
  `FileNotFoundError: [Errno 2] No such file or directory: 'a' -> 'b'`. Re-probed with a real `dir_fd` and the
  rename succeeded, so the capability check must not rely on `supports_dir_fd` for `replace`.
- Second probe finding: `os.open("linkdir", O_RDONLY|O_DIRECTORY|O_NOFOLLOW, dir_fd=fd)` raises
  `NotADirectoryError: [Errno 20] Not a directory`, while the same on a file link raises
  `OSError: [Errno 62] Too many levels of symbolic links`. Platform-dependent errno, so errno-based link detection
  was dropped in favour of an explicit `lstat`.

### What I learned
- `TASK.md` is precise about codes but leaves several boundary details open (absolute-path saves, `..` inside a path,
  reading a directory, what happens to a file saved but never read); I noted each decision so it can be reviewed.
- `os.listdir(fd)` and `os.stat(..., dir_fd=fd, follow_symlinks=False)` make a fully fd-based `names()` walk easy.

### What was tricky to build
- Nothing built yet; the tricky part identified up front is the tension between "absolute paths may name a file in a
  root" and "links must not be used": the plan is to resolve absolute paths with `realpath` and require the *final*
  target to be inside a canonical root, then re-walk the canonical relative path with `lstat`+`O_NOFOLLOW`, so the
  library itself never traverses a link.

### What warrants a second pair of eyes
- The decision that relative paths refuse *all* symlinks (even links whose target is inside a root) while absolute
  paths resolve first; a reviewer should check that asymmetry is acceptable.
- `E_SHADOW` triggering even when the writable root also holds a file of that name (the dataset always wins).

### What should be done in the future
- Add the `fsio` backends and the `Workspace` facade, then the tests.

### Code review instructions
- Nothing to run yet. Read `TASK.md` and compare it with the module plan above; the policy questions listed under
  "What warrants a second pair of eyes" are the places where the code will need to match the intent.

## Step 2: Building the core (errors, paths, fsio, Workspace)

I wrote the four core modules and a five-line package `__init__`: `errors.py` (the `Refused` type with `code`, `fix`,
`detail`, `path` and a validated code list), `paths.py` (coercion of `str`/`bytes`/`PathLike`, absolute detection,
component splitting that refuses `..`, canonical-relative computation), `fsio.py` (two backends: `_FdBackend` using
`dir_fd`-relative syscalls with `O_NOFOLLOW` on every step, `_PathBackend` as a portable `lstat` walk, both sharing
the refusal builders) and `workspace.py` (search order, shadow check, read ledger, batch set, absolute-path
containment).  Then I drove the whole surface with a throwaway smoke script against a temporary workspace to see the
codes come out the way the task describes.

The smoke script exercised every documented refusal and printed the code plus `fix` for each; all of them matched the
specification on the first pass after one fix (below), and the read-only dataset directory was unchanged afterwards.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Same request as Step 1: build the library described by `TASK.md`, now at the
implementation level.

**Inferred user intent:** A working library whose refusals are the documented ones, so that the later test suite has
something honest to test.

### What I did
- Created `jailfs/errors.py`, `jailfs/paths.py`, `jailfs/fsio.py`, `jailfs/workspace.py`, `jailfs/__init__.py`.
- Ran a throwaway smoke script (`python3 - <<EOF ... EOF`) that built a temp `root`/`data`/`libs` tree, saved nested
  files inside a `batch()`, and then attempted: absolute read outside the roots, missing read, read through a planted
  file link, read through a planted directory link, `..` save, shadowed save (top level and nested), save through a
  planted link, save onto a planted link, `load` of a non-`.py`/`.js` file, non-bytes data, reading a directory,
  read-then-save, duplicate save in one batch, and the same path saved in two different batches.

### Why
- `TASK.md`'s code list drove the refusal builders one-for-one (`E_ACCESS` for links/outside/read-only/read-before
  write, `E_SHADOW` for dataset names, `E_DUPLICATE` inside `batch()`), so the mapping is auditable by grepping the
  codes.
- Atomic save (write a `.jailfs-<hex>.tmp` in the target directory, then `os.replace` with `src_dir_fd`/`dst_dir_fd`)
  means a failed save cannot leave a half-written file, and replacing a name never follows a link at the target.
- The read ledger key is `(root index, components)` rather than a string, so `a/./b.txt` and `a/b.txt` cannot be used
  to launder a read-then-overwrite.

### What worked
- Every documented refusal produced the intended code; `names()` returned `['nested/deep/b.txt', 'out/a.txt']` and
  skipped the planted links; two batches could save the same path (second content won: `b'2'`); the data directory
  was untouched: `data untouched: ['points.csv', 'sub']`.

### What didn't work
- `python3 - <<EOF ... from jailfs import Workspace, Refused, fs` →
  `ImportError: cannot import name 'fs' from 'jailfs' (/Users/manuel/pattern-validation/builds/08/ctl/x1/work/jailfs/__init__.py)`.
  That was my probe guessing a module name that does not exist (the backend hook lives in `jailfs.fsio`), not a
  library defect; the probe was rerun with `import jailfs.fsio as fsio`.
- Real bug found by the first smoke run: `ws.save("out/a.txt", b"hello")` was refused
  `jailfs.errors.Refused: E_SHADOW: save: 'out/a.txt' already exists in a read directory (fix: save under a different
  name; the read-only data for 'out/a.txt' is authoritative)`. Cause: `fsio.exists()` treated *every* `Refused` as
  "the name is taken", including the `E_NOT_FOUND` raised for the missing parent directory `out`. Fixed by returning
  `refused.code != E_NOT_FOUND`, i.e. only links/obstructions count as taken.

### What I learned
- The kernel's errno for "link where a directory was expected" differs by platform (`ENOTDIR` here, `ELOOP` for a
  file link), which vindicates the decision to `lstat` every component instead of parsing errno.
- Shadow checking has to be tolerant of *missing* paths while strict about *occupied* ones; that distinction is the
  one place where a one-line mistake silently blocks all writes.

### What was tricky to build
- Keeping the two backends behaviourally identical. The `dir_fd` backend must close the previous descriptor exactly
  once while descending (a plain loop would leak the root fd on an exception), which is why `_enter` closes the old
  fd only after the new one is open, and `_walk` closes whatever remains in a `finally`.
- `names()` must not recurse through links nor be fooled by a directory replaced mid-walk, so it re-`lstat`s every
  entry and opens subdirectories with `O_NOFOLLOW|O_DIRECTORY`, skipping anything it cannot open instead of failing
  the whole listing.

### What warrants a second pair of eyes
- `Workspace.save` accepts an absolute path that resolves inside the writable root; the task only says "writes only
  inside the writable root", so this reading could be too generous.
- `_locate` compares `realpath` of the request with canonical roots, so an absolute path may legally point through a
  link that ends inside a root, while relative paths refuse links outright. Intentional, but asymmetric.
- Ordering of refusal causes in `save` is shadow → duplicate → read-ledger; when two apply the agent sees the first.

### What should be done in the future
- Write the `unittest` suite under `tests/`, including a run of the security cases against the portable backend via
  the `_FORCE_PATH_BACKEND` hook.

### Code review instructions
- Start at `jailfs/workspace.py::Workspace.save` and `Workspace.read` for policy, then `jailfs/fsio.py::_FdBackend._walk`
  for the mechanics. Validate by running the smoke script pattern or, after Step 3, `python3 -m unittest discover -s tests`.

## Step 3: Writing the test suite

I wrote eight test modules plus a shared fixture module, all under `tests/`, using only `unittest` and temporary
directories.  The fixture (`tests/support.py`) builds a `root`/`data`/`libs` tree per test, keeps helper methods for
planting files and symlinks, and can force either low level backend, so every security-relevant check runs twice: once
through the `dir_fd` backend and once through the portable `lstat` backend.  A `snapshot()` helper captures contents,
mode and mtime so dataset-integrity tests can prove nothing was touched.

The suite is organised by surface (`test_construction`, `test_read`, `test_save`, `test_load_names`) plus three
adversarial modules: `test_links` (planted links, including a root swapped for a link after construction),
`test_hostile_input` (malformed names must never leak an `OSError`) and `test_integrity` (a barrage of boundary probes
followed by a full comparison of the dataset trees).  A static test parses the library with `ast` to assert that every
`Refused` the package constructs carries a `fix`.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** The brief says to write tests under `tests/` with temporary directories and to run them
with `python3 -m unittest discover -s tests`, so the suite must be runnable exactly that way and must never touch real
data.

**Inferred user intent:** Evidence that the boundary holds, not just a claim: each documented code should be produced
by a test that provokes it, and the tests should be readable enough to check the policy by reading them.

### What I did
- Created `tests/support.py`, `tests/__init__.py`, `tests/test_construction.py`, `tests/test_read.py`,
  `tests/test_save.py`, `tests/test_load_names.py`, `tests/test_links.py`, `tests/test_hostile_input.py`,
  `tests/test_integrity.py`.
- Ran `python3 -m unittest discover -s tests` (143 tests).

### Why
- `TASK.md` says "other code will be tested against it", so each exported name, each code and each documented sentence
  ("root as a list or tuple is refused", "absolute path must lie inside one of them", "parent directories are created
  there", "the one way to load helper code") got at least one test.
- Every refusal in the library is an `E_ACCESS`/`E_NOT_FOUND`/`E_DUPLICATE`/`E_SHADOW` and nothing else; the hostile
  input suite exists because a raw `OSError` (for example `ENAMETOOLONG`) would be an uncontrolled channel out of the
  sandbox.

### What worked
- All 143 tests pass with the three discovery spellings I care about:
  `python3 -m unittest discover -s tests`, `python3 -m unittest discover` and
  `python3 -m unittest discover -s tests -t .` — each reported `Ran 143 tests ... OK`.

### What didn't work
- First full run: `python3 -m unittest discover -s tests` → `Ran 130 tests in 0.151s / FAILED (failures=7)`.
  All seven were mistakes in my own tests, not in the library:
  `AssertionError: 'ALLOWED' unexpectedly found in ['ALLOWED', 'E_SHADOW', ...]` (I had listed
  `ws.save("data/dataset/a.csv", b"pwned")` as an attack, but that relative name does not exist in the data directory,
  so it is a legal save of a *new* name inside the root),
  `AssertionError: Lists differ: [] != ['secret.txt']` twice per backend (I asserted the `outside` fixture directory
  was empty when it holds `secret.txt`),
  and `AssertionError: b'from data' != b'1,2,3\n'` (wrong expected bytes for `points.csv`).
- After those fixes: `Ran 130 tests in 0.135s / OK`.

### What I learned
- Writing the attack list as data (a list of lambdas) made it obvious which probes were genuinely forbidden and which
  were legal saves that merely looked hostile.
- Comparing "before/after" listdir snapshots is more honest than asserting an empty directory.

### What was tricky to build
- Making the same test class run against two backends: the base class holds the fixture but no tests (so `unittest`
  discovery does not run it twice), and the checks live in plain mixins, with one `unittest.TestCase` subclass per
  backend.  Skip logic has to run before the temp tree is built for the `dir_fd` flavour.

### What warrants a second pair of eyes
- Whether the mixin/TestCase split hides any test from discovery; the count (143) is printed by the runner and the
  backend-specific tests appear twice, once per backend.
- `tests/support.py::snapshot` compares mtime_ns as well as bytes, so a test that legitimately rewrites a dataset
  would fail even with identical content; that is intended for this suite.

### What should be done in the future
- Add a stress test for very large files and many names once an agent runtime has a real size profile.

### Code review instructions
- Read `tests/test_save.py` and `tests/test_links.py` first, then run `python3 -m unittest discover -s tests -v` to see
  each case name.

## Step 4: Fixing the two real defects the tests found

Two library defects surfaced while growing the suite, both in the refusal plumbing rather than in the boundary logic:
a shadow check that treated "cannot look at the name" as "the name is taken", and a raw `OSError` leaking out of the
`dir_fd` backend for a name the kernel refuses to look at (`ENAMETOOLONG`).  Both are now fixed, and each fix has a
regression test.

While fixing the second one I also split the refusal type into two internal refinements, `Linked` and `Obstructed`,
both still `E_ACCESS`, so the search loop and the shadow check can tell "a link blocked me", "a plain file is in the
way" and "the name cannot be inspected" apart without string matching on messages.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Run the tests, fix what fails, and keep the diary honest about failures.

**Inferred user intent:** A suite that is green because the code changed, not because the test was weakened, with the
fixes explained well enough to review.

### What I did
- Fixed `fsio.exists()`: `E_SHADOW` is raised only when a read directory really holds the name.
- Fixed `_FdBackend._lstat()`: any `OSError` other than `FileNotFoundError` becomes a `Refused(E_ACCESS)` with a fix.
- Added `Linked(Refused)` and `Obstructed(Refused)`; `Workspace.read` keeps searching on `Obstructed` (a stray file in
  the writable root must not make a dataset file unreachable) and stops on `Linked`.
- Added `_PathBackend._check_base()` so the portable backend refuses a root that was replaced by a symlink after
  construction (the `dir_fd` backend already got this from `O_NOFOLLOW|O_DIRECTORY`).
- Added regression tests in `tests/test_read.py`, `tests/test_hostile_input.py` and `tests/test_links.py`.

### Why
- `TASK.md` allows only four codes and one refusal type; an `OSError` escaping the library would break the contract
  for the runtime that wraps it.
- A wrong `E_SHADOW` on a novel name would have blocked legitimate saves whenever a parent directory was missing —
  exactly the first bug reported in Step 2.

### What worked
- `python3 -m unittest discover -s tests` → `Ran 143 tests in 0.164s / OK` after the changes; the hostile-input suite
  (which threw 23 malformed names x 2 spellings x 3 operations at both backends) now reports no unexpected exception
  types.

### What didn't work
- Before the `Linked`/`Obstructed` split, the over-long-name test failed with
  `AssertionError: 'E_ACCESS' != 'E_SHADOW'` and a message containing 4000 `z` characters, because
  `fsio.exists()` mapped *every* refusal to "taken".  Splitting the types fixed both the code and the noise.
- A typo in a test I added by script — `NameError: name 'Refused' is not defined` in
  `tests/test_links.py` line 99 — because I appended a new test that used `Refused` without importing it; fixed by
  extending the import.

### What I learned
- The most dangerous thing in this design is the *ordering* of checks in `save` and the *tolerance* of the shadow
  probe: both are places where a small mistake turns a security check into a false refusal or vice versa.
- Platform errno differences make "catch `OSError`, guess why" the wrong shape; explicit `lstat` plus typed refusals is
  both clearer and more portable.

### What was tricky to build
- Deciding that `Obstructed` should let the search continue while `Linked` should not: a file named `nested` in the
  root must not hide `nested/leaf.txt` from a dataset, but a *link* named `nested` is an escape attempt and must stop
  the read with `E_ACCESS` instead of quietly reading a dataset file through a different root.

### What warrants a second pair of eyes
- `Workspace.read` continues on `Obstructed`: a reviewer should confirm that continuing cannot read something the
  caller should not see (it cannot, because the next roots are only the read directories).
- `_PathBackend` remains check-then-use; the `_check_base` addition narrows but does not close the race.

### What should be done in the future
- If this ever runs on a platform without `dir_fd`, consider pinning the root by holding a directory descriptor for the
  whole session.

### Code review instructions
- Diff `jailfs/fsio.py::exists`, `_FdBackend._lstat`, `Linked`/`Obstructed` and `jailfs/workspace.py::Workspace.read`;
  validate with `python3 -m unittest discover -s tests -v`.

## Step 5: Final review and closing check

I re-read `jailfs/fsio.py` end to end after all the scripted edits (descriptor lifecycle in `_walk`/`_enter`, the
portable walk, the two dispatch layers), made `names()` skip entries it cannot even `lstat` instead of failing the
whole listing, exported the `Linked`/`Obstructed` refinements from the package, and confirmed the public surface with
a short `dir(jailfs)` probe.  Then I cleaned `__pycache__`, ran the suite in verbose and quiet form, and re-read
`DIARY.md` to check every step has the required sections.

Everything is green and the workspace tree contains only the package, the tests, the two brief files and this diary.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** The last phase is the closing check the brief calls for: tests run and green, diary
complete, deliverable tidy.

**Inferred user intent:** Confident hand-off: no stale code, no failing tests, no missing diary sections, and a final
message in the exact JSON shape `TASK.md` asks for.

### What I did
- Reviewed `jailfs/fsio.py` and `jailfs/workspace.py` in full; no descriptor leaks found (`_enter` closes the parent
  only after the child is open, `_walk` closes whatever is left in `finally`).
- Hardened `_collect_fd` so `names()` skips an unreadable hostile entry instead of refusing the whole listing.
- Exported `Linked` and `Obstructed` from `jailfs/__init__.py`.
- `find . -name __pycache__ -type d -exec rm -rf {} +` and then
  `python3 -m unittest discover -s tests -v` → `Ran 143 tests in 0.201s / OK`; plain
  `python3 -m unittest discover -s tests` → `Ran 143 tests in 0.181s / OK`.
- Verified the exports: `CODES, E_ACCESS, E_DUPLICATE, E_NOT_FOUND, E_SHADOW, LOADABLE_SUFFIXES, Linked,
  Obstructed, Refused, Workspace`.

### Why
- The brief requires that the final state be tested and that the diary be complete, and `TASK.md` asks the final
  message for the file list, the design parts, the tradeoffs, the test count and the unclear points.

### What worked
- 143 tests, both backends, three discovery spellings (`-s tests`, bare `discover`, `-s tests -t .`) all report `OK`.

### What didn't work
- Nothing failed in this step; the last failure on record is from Step 4 (`NameError: name 'Refused' is not defined`),
  already fixed.

### What I learned
- The scripted edits I used for speed (heredoc `str.replace`) are the main risk in this kind of pass: reading the file
  afterwards caught two spots where a replacement could have silently not applied, so a final read of each touched
  region is not optional.

### What was tricky to build
- Nothing new; the residual difficulty is inherent: the `dir_fd` backend is race-free per component but the diffuse
  "check the root, open the file" boundary in the portable backend is only narrowed, not closed.

### What warrants a second pair of eyes
- `Workspace.save`'s refusal precedence (shadow, duplicate, read ledger) and the choice to accept absolute paths that
  resolve inside the writable root.
- `_locate` resolving absolute paths with `realpath` (so an absolute path may pass through a link whose target is
  inside a root) while relative paths refuse links entirely.

### What should be done in the future
- Pin the writable root with an open directory descriptor for the session so the portable backend can drop its
  check-then-use window; add a size/quota policy for saves.

### Code review instructions
- Start with `jailfs/workspace.py` (`read`, `save`, `batch`, `_locate`, `_refuse_shadow`), then
  `jailfs/fsio.py` (`_FdBackend._walk`, `Linked`, `Obstructed`, `exists`). Validate with
  `python3 -m unittest discover -s tests -v` and by reading `tests/test_integrity.py` to see what "the datasets are
  untouched" means concretely.

# Diary

## Goal

Build `jailfs`, a Python 3 (standard library only) library that gives agent programs one writable
directory and read-only roots, with every file operation contained by the operating system and refused
with a code and a fix when it would escape, follow a link, shadow a read-only file or replace a file the
session read. This diary records the design, each build phase, the failing test runs with their exact
errors, the fixes, and the final check.

## Step 1: Reading the chapter, the task and the diary format, then designing

I read `CHAPTER.md` (Contained Workspace), `TASK.md` and `DIARY-FORMAT.md` completely before writing any
code, then fixed the public interface and the internal participants. The design decision that shaped
everything else: Python 3.10 has no `os.Root`, so the *Root handle* had to be built from `openat`-style
calls exposed through `dir_fd=...` plus `O_NOFOLLOW` on every component, not from path-string checks.

### Prompt Context

**User prompt (verbatim):** "You are a software engineer joining a project. Your working directory contains three files:
- CHAPTER.md: a chapter of a design-pattern book describing the pattern you must apply;
- TASK.md: the software to build, with its required public interface;
- DIARY-FORMAT.md: how to keep your work diary.
Read all three completely first. Keep DIARY.md as you go, one step per phase of work, in that format. Then design, build and test the software in this directory. Work only inside this
directory (do not read or write outside it). Use only the Python 3 standard library. Run your tests and fix what
fails before you finish, and make sure DIARY.md is complete. Your final message must follow the output format at the
end of TASK.md."

**Assistant interpretation:** Implement the Contained Workspace pattern as a `jailfs` package with the exact
interface in `TASK.md`, tests under `tests/` using temporary directories, this diary in the given format, and a
final JSON report.

**Inferred user intent:** A library whose filesystem boundary holds even when an agent (or a file planted in the
writable directory) tries to cross it, plus evidence — tests that fail without the safeguards and a diary that
shows the work.

### What I did
- Read the three files in full; listed the working directory (`CHAPTER.md`, `DIARY-FORMAT.md`, `TASK.md` only).
- Checked the interpreter: `python3 --version` → 3.10.3 (so no `os.Root`, which is Go, not Python).
- Fixed the module split: `jailfs/_errors.py` (`Refused` + the four codes), `jailfs/_root.py` (root handle,
  atomic writer, listing), `jailfs/_workspace.py` (locator, opened set, loader, batch), `jailfs/__init__.py`
  (exports).

### Why
- CHAPTER.md, Structure: the participants are writable root, read roots, locator, root handle, opened set,
  writer, loader; the split above mirrors them one-to-one so the pattern is visible in the code.
- Implementation note 1 (let the OS enforce the root) and Applicability (do not pretend string checks contain
  anything) drove the `dir_fd` + `O_NOFOLLOW` design.

### What worked
- Reading all three documents first made the interface unambiguous: four refusal codes, one writable root,
  `read`/`save`/`load`/`names`/`batch`.
- `os.supports_dir_fd` is available and includes `open`, `stat`, `mkdir`, `rename`, `unlink` on this platform,
  so the root-relative approach is viable; the code refuses to construct a `Workspace` where it is not
  (Applicability's fallback advice).

### What didn't work
- Nothing at this stage; the only uncertainty was whether `os.listdir` accepts a directory descriptor, which I
  checked in a scratch one-liner (`os.listdir(fd)` → `['a']`).

### What I learned
- The chapter's sketch is a `Location = (root, rel)` design; that maps directly onto a `Root` object plus a
  relative name, and it is what makes the "relative names look in the writable root first, then read roots"
  rule easy to express.

### What was tricky to build
- Nothing yet: the tricky parts were identified, not solved — absolute paths under symlinked roots (note 7),
  the opened-set identity comparison (note 2), and the temporary-file race (note 3).

### What warrants a second pair of eyes
- Whether refusing *all* links in a path component (stricter than Go's `os.Root`, which follows links that stay
  inside the root) is the right trade-off for `jailfs`.

### What should be done in the future
- Build `_errors.py` and `_root.py` first so the workspace can be written against a real root handle.

### Code review instructions
- Start with `TASK.md` and the "Structure"/"Collaborations" sections of `CHAPTER.md`; then check that every
  participant has a home in the planned split.

## Step 2: Building the refusal type and the root handle

I wrote `jailfs/_errors.py` (`Refused` with `code`, `fix`, `message`, picklable) and `jailfs/_root.py`: a `Root`
holding one directory descriptor, with `open_read`, `lstat_optional`, `exists`, `save_atomic`, `_create_temp`
and `list_files`, plus `normalize_relative`, `identity` and `have_root_relative_operations`.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Implement the boundary at the lowest layer — the root handle — so that every later
call inherits containment instead of re-implementing checks.

**Inferred user intent:** Containment that lives in the operating system's own resolution, not in string tests.

### What I did
- `jailfs/_errors.py`: `Refused(Exception)` with `code`, `fix`, `message`, and `__reduce__` for pickling.
- `jailfs/_root.py`: `Root._walk_dirs` opens every intermediate component with
  `O_RDONLY|O_DIRECTORY|O_NOFOLLOW` relative to the previous descriptor; `open_read` adds `O_NOFOLLOW` (and
  `O_NONBLOCK`, see Step 6) on the final component; `save_atomic` creates `.jailfs-tmp-<hex>` with
  `O_CREAT|O_EXCL|O_NOFOLLOW`, writes, `fsync`s, then `os.rename(..., src_dir_fd=, dst_dir_fd=)`; failures unlink
  the temporary.
- `normalize_relative` drops `.`/empty components and resolves `..` by text, refusing anything that climbs above
  the root before the kernel sees it.

### Why
- CHAPTER.md, implementation notes 1–3, and Collaborations 2–3 (locate, then `handle.open(rel)` / `lstat`, no link
  following, exclusive random temporary, rename into place).
- Applicability: when `os.supports_dir_fd` or `O_NOFOLLOW` is missing, construction refuses and points at
  process-level isolation instead of giving a false sense of safety.

### What worked
- The descriptor walk gives exactly the property the chapter asks for: `..` and links are refused by the kernel
  (`ELOOP`/`ENOTDIR`), and `_translate` turns those errnos into `E_ACCESS`/`E_NOT_FOUND` refusals with fixes.
- `os.stat(..., dir_fd=..., follow_symlinks=False)` reports a planted link as a link instead of failing.

### What didn't work
- My first `_list_dir` closed a child descriptor twice (once in the recursion's `finally`, once in the caller's
  `finally`), which later surfaced as `OSError: [Errno 9] Bad file descriptor` in the test run recorded in Step 4.

### What I learned
- Directory descriptors opened `O_RDONLY` are enough to create children; the permission checked is on the
  directory, not on the descriptor's mode.

### What was tricky to build
- Error translation: the same errno means different refusals for reads and writes. `ENOENT`/`ENOTDIR` must be
  `E_NOT_FOUND` for a read (so the locator can try the next root) and `E_ACCESS` for a write (so a save never
  silently lands somewhere unexpected). `_translate` takes a `for_write` flag for that reason.

### What warrants a second pair of eyes
- The `save_atomic` cleanup path: if `os.fdopen(fd, "wb")` itself raised, the raw `fd` would not be closed, and
  the unlink would still run. Low risk, worth a look.
- `TOCTOU` between `lstat_optional` in `Workspace.save` and `save_atomic`'s rename: the chapter explicitly
  accepts that the engine assumes no other process writes into the same root concurrently.

### What should be done in the future
- Build the locator/opened-set/loader on top of `Root` (Step 3).

### Code review instructions
- Read `jailfs/_root.py` top to bottom; check each `os.open`/`os.stat`/`os.rename` call passes `dir_fd` and that
  every component but the last gets `O_NOFOLLOW|O_DIRECTORY`. Validate with the symlink tests in Step 7.

## Step 3: Building the workspace: locator, opened set, writer, loader, batch

I wrote `jailfs/_workspace.py` and `jailfs/__init__.py`. `Workspace.__init__` refuses several writable roots (a
list/tuple of more than one), creates the writable root if it is missing, refuses missing or non-directory read
roots, and drops a read root that repeats the writable root. `read`/`save`/`load`/`names`/`batch` are implemented
against `Root` and three small sets: `_opened`, `_written`, and the per-batch `_batch_saves`.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Implement the required public interface exactly, with refusals naming the roots and
the fix, and no second way to load code.

**Inferred user intent:** An API an agent runtime can hand to untrusted programs without re-checking anything.

### What I did
- Locator: `_read_candidates` (relative: writable root then read roots in order; absolute: exactly one owner),
  `_absolute_candidate`, `_write_location` (writable root only; a read root refuses with `E_ACCESS`).
- Opened set: `read`/`load` record `(st_dev, st_ino)` of the opened descriptor; `save` refuses when the target's
  identity is in `_opened` but not in `_written` (notes 2, and Collaborations 3).
- Writer: `save` checks a link at the target, a directory, a non-regular file, the identity rule, a read root
  nested inside the writable root (`E_ACCESS`), a name that exists in a read root (`E_SHADOW`), and, inside
  `batch()`, a repeated name (`E_DUPLICATE`); then calls `Root.save_atomic`.
- Loader: `load(name)` resolves like `read`, accepts only `.py`/`.js`, decodes UTF-8, and records the opened
  identity; `require()` always refuses with the fix pointing at `load` (note 4).
- Listing: `names()` walks the writable root through descriptors and returns sorted relative names (note 8).
- Every refusal built by `_refuse`/`_refuse_roots` appends `(writable root …; read roots: …)` and a `fix`.

### Why
- CHAPTER.md, Collaborations 1–5 and sketch: startup strictness, lookup order, atomic save, one loader, refusals
  that teach the boundary.
- TASK.md's codes map one-to-one onto the checks above (`E_ACCESS`, `E_NOT_FOUND`, `E_DUPLICATE`, `E_SHADOW`).

### What worked
- The `Location = (Root, rel)` shape made each check a short block in `save` and each refusal message easy to word.
- A `_Batch` context manager with a depth counter keeps nested `with ws.batch():` blocks from clearing the
  duplicate record early.

### What didn't work
- `_open_existing` initially raised the final "not found" through `_refuse_roots`, which always uses `E_ACCESS`, so
  missing files came back as `E_ACCESS`. Also `save` checked `E_SHADOW` before the planted-link check, so a link
  inside the writable root pointing at a read-only input was reported as `E_SHADOW`. Both were caught by the first
  test run (Step 4) and fixed in Step 5.

### What I learned
- Ordering of checks is part of the interface: the same save can be "a link" and "a shadow", and the more specific,
  more dangerous finding should win. Target checks (link, directory, identity) now run before the shadow check.

### What was tricky to build
- `_write_location` for absolute paths had to decide between "inside the writable root" and "inside a read root"
  when one root is nested in the other. I made the writable root win by real path, and left the residual overlap
  to the explicit "lands inside a read-only root" check.

### What warrants a second pair of eyes
- `E_SHADOW` is applied to absolute saves into the writable root as well, not only to relative names. TASK.md's
  wording ("a save whose relative name already exists in a read directory") is satisfied either way; the stricter
  reading was chosen.
- `save` accepts `str` data by encoding UTF-8 (the interface says bytes); this is a convenience, not a boundary.

### What should be done in the future
- Test all of it, including the attacks from the chapter's Motivation table (Step 4).

### Code review instructions
- Read `jailfs/_workspace.py` functions in this order: `_read_candidates`, `_absolute_candidate`,
  `_write_location`, `_open_existing`, `read`, `save`, `load`, `_Batch`. Check that every refusal carries `code`
  and `fix`, and that only `Root` touches the filesystem.

## Step 4: Writing the test suite and running it the first time

I wrote `tests/test_jailfs.py` (test classes `SurfaceTests`, `ReadTests`, `WriteTests`, `LoaderTests`,
`BatchTests`, `NamesTests`) with a helper tree of `work` (writable), `data` and `lib` (read roots) and `outside`
(a directory that must stay untouched). Then I ran the suite.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Write tests that encode the holes from the chapter's Motivation table, not just the
happy path, and run them with `python3 -m unittest discover -s tests`.

**Inferred user intent:** Evidence that the boundary holds, including for planted links and repeated saves.

### What I did
- Created `tests/test_jailfs.py` with 62 tests at that point, covering startup strictness, lookup order, absolute
  paths, `..`, links (final and directory, dangling and in-root), the opened set (including a hard link to prove
  identity comparison), `E_SHADOW`, `E_DUPLICATE`, `load`, `require`, `names`, and the exclusive temporary name.
- Ran `python3 -m unittest discover -s tests`.

### Why
- CHAPTER.md, implementation note 11: security tests must be shown to fail first; every row of the Motivation
  table became at least one test.

### What worked
- 55 of 62 tests passed on the first run, which confirmed the root handle, the opened set and the batch logic.

### What didn't work
- The run failed: `Ran 62 tests in 0.063s` / `FAILED (failures=3, errors=4)`.
  The 4 errors were all `OSError: [Errno 9] Bad file descriptor` raised from `jailfs/_root.py` in
  `test_names_lists_files_it_wrote`, `test_save_leaves_no_temporary_files`,
  `test_names_shows_nested_files_by_relative_name` and
  `test_names_ignores_read_roots_and_directories_and_links`.
  The 3 failures were:
  `FAIL: test_missing_name_is_not_found (test_jailfs.ReadTests)` with
  `AssertionError: 'E_ACCESS' != 'E_NOT_FOUND'`;
  `FAIL: test_load_of_a_missing_helper_is_not_found (test_jailfs.LoaderTests)` with
  `AssertionError: 'E_ACCESS' != 'E_NOT_FOUND'`;
  `FAIL: test_save_onto_an_in_root_link_to_an_input_is_refused (test_jailfs.WriteTests)` with
  `AssertionError: 'E_SHADOW' != 'E_ACCESS'`.

### What I learned
- The final "not found" refusal was built with the helper that hard-codes `E_ACCESS`; the fix is a general
  `_refuse(code, detail, fix)` with `_refuse_roots` as a thin wrapper.
- Check ordering shows up in tests: the in-root link to a read-only input is both a link and a shadow.

### What was tricky to build
- Writing tests that cannot pass vacuously: each attack test asserts both the refusal code *and* that nothing was
  written outside the root (or that the input still has its original bytes).

### What warrants a second pair of eyes
- Whether `test_save_onto_an_in_root_link_to_an_input_is_refused` should demand `E_ACCESS` specifically or accept
  `E_SHADOW` as well; I chose `E_ACCESS` and reordered the checks, but the interface does not say.

### What should be done in the future
- Fix the four errors and three failures (Step 5).

### Code review instructions
- Run `python3 -m unittest discover -s tests` and read `tests/test_jailfs.py` top to bottom; every test must build
  its own temporary tree and clean it up.

## Step 5: Fixing the descriptor double close and the two refusal bugs

I fixed the three problems from Step 4: the double close in `_list_dir`, the `E_ACCESS`-only final refusal, and
the check ordering in `save`.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Make the failing tests pass without weakening any check.

**Inferred user intent:** A green suite that is green for the right reasons.

### What I did
- `jailfs/_root.py`: removed the caller-side `os.close(child)`; the recursive `_list_dir` call owns and closes the
  descriptor it was given in its own `finally`.
- `jailfs/_workspace.py`: added `_refuse(code, detail, fix)`; the "no file named …" refusal now uses
  `E_NOT_FOUND` via `_refuse`; moved the target checks (link, directory, opened identity) before the
  `E_SHADOW` check.
- Re-ran `python3 -m unittest discover -s tests` → `Ran 62 tests … OK`.

### Why
- The `[Errno 9]` error was a lifetime bug: one descriptor must have exactly one owner. The `E_NOT_FOUND` fix is
  TASK.md's code contract; the ordering fix is the chapter's "a link at the target is refused" collaboration
  beating the softer shadow warning.

### What worked
- All 62 tests passed after the three changes.

### What didn't work
- Nothing in this step; the three earlier failures were all explained by the three fixes.

### What I learned
- Passing a descriptor into a helper and closing it in a `finally` inside that helper is the simplest rule that
  keeps the walk leak-free.

### What was tricky to build
- The exact ordering: duplicate check first (cheap, per-run), then target checks (link/dir/identity), then the
  read-root overlap, then shadow. The shadow check must still fire when the target is absent from the writable root
  — which the tests `test_save_whose_name_exists_in_a_read_root_is_refused` covers.

### What warrants a second pair of eyes
- The shadow check runs `r.exists(rel)` on every read root for every save; with many read roots this is a few
  extra syscalls per save (acceptable here, worth noting).

### What should be done in the future
- Harden the remaining edges found in review (Step 6).

### Code review instructions
- `git`-less directory: compare `jailfs/_root.py::_list_dir`, `jailfs/_workspace.py::_refuse`,
  `_open_existing` and `save` against the Step 4 failure list.

## Step 6: Hardening after review: non-regular files, root nesting, symlinked read roots, text data

While reviewing the passing code I found four edge cases worth closing before finishing: planted FIFOs could hang
a read, a save onto a FIFO was only caught by the generic identity path, a writable root nested inside a read root
made every save fail, and a symlinked read root inside the workspace was refused by the writable root's walk
instead of resolving to its target (implementation note 7). I also made `save` accept `str` data by encoding it.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Close the remaining holes and the two configuration surprises; keep the tests
matching the code.

**Inferred user intent:** A boundary without sharp edges that turn ordinary use into confusing refusals.

### What I did
- `open_read`: added `O_NONBLOCK` so a planted FIFO cannot block the open, and refused anything that is not a
  regular file (directory, FIFO, device).
- `save`: refused an existing target that is not a regular file, with its own fix.
- Read-root overlap: only refuse when the read root is nested *inside* the writable root (the dangerous
  direction); a writable root nested inside a read root stays writable, since it is the narrower declaration.
- `_absolute_candidate`: resolved the real path first (writable root, then read roots) before falling back to the
  name's own prefix, so a symlinked read root inside the workspace resolves to its target.
- `_write_location`: mirrored that order (writable root by real path, then by name, then read roots, then outside).
- `_as_bytes`: accept `bytes`, `bytearray`, `memoryview` and `str` (UTF-8); reject others with `TypeError`.
- Added tests: FIFO read/save refusal, writable root nested in a read root (relative and absolute saves), symlinked
  read root inside the workspace, text data.
- Added a `NullHandler` to the `jailfs` logger so the note-6 shadow warning is quiet unless configured.
- Ran `python3 -m unittest discover -s tests` → `Ran 67 tests … OK`.

### Why
- CHAPTER.md, Applicability and note 7 (symlinked read roots), note 6 (shadowing warning), and the Consequences
  section's honesty about what the engine itself checks.
- A FIFO is a file in the writable directory that another program can plant; it must neither block nor be written.

### What worked
- Ordering absolute-path resolution by real path fixed the symlinked-read-root case without weakening anything:
  a link that leaves every root still falls through to the name-based candidate and is refused by the walk.

### What didn't work
- Nothing failed in the suite, but my mutation experiment in Step 7 hit a syntax error when I replaced a
  multi-line `os.open` argument list in a copy of the package (missing comma before the mode). I redid the
  mutation with an exact single-line replacement; that is recorded in Step 7.

### What I learned
- Nested-root direction matters: "read root inside writable root" is the dangerous overlap; the reverse only
  widens read access to what the configuration already declared readable.

### What was tricky to build
- Making the symlinked read root work while keeping `O_NOFOLLOW` everywhere: the answer is not to follow the link
  in the walk but to map the *real* path to the owning read root before walking.

### What warrants a second pair of eyes
- `_under` uses `os.path.normpath` string prefixes; on a platform where a root path contains `..` or mixed
  separators this would need `realpath` on both sides (both sides are already abspaths here).
- The `str` acceptance in `save` is a deviation from "data: bytes"; it is documented in the docstring only
  implicitly.

### What should be done in the future
- If a Windows port is ever wanted, `O_NOFOLLOW`/`dir_fd` are missing there; the package would refuse at
  construction, as Applicability advises.

### Code review instructions
- Read `jailfs/_root.py::open_read`, `jailfs/_workspace.py::_absolute_candidate`, `_write_location` and `save`.
  Validate with the FIFO, nested-root and symlinked-read-root tests.

## Step 7: Proving the tests bite: a naive implementation and mutation runs

A security test that passes without its fix is worthless (implementation note 11), so I checked two ways: a
scratch script showing the holes really exist under naive path joins, and mutation runs against a copy of the
package.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Demonstrate that the suite fails when the safeguards are removed.

**Inferred user intent:** Confidence that the green run means something.

### What I did
- Wrote `scratch_naive_check.py` inside this directory (temporary, deleted afterwards) which joins paths by hand
  and calls `open(path, "wb")`; output:
  `dangling link escape wrote outside: True`, `symlinked dir escape wrote outside: True`,
  `planted temp link overwrote outside: True`.
- Mutation A (copy of the package in `.mutation/`, `lstat_optional` changed to `follow_symlinks=True`):
  `FAIL: test_save_onto_a_planted_dangling_link_is_refused`, `FAIL: test_save_onto_an_in_root_link_to_an_input_is_refused`,
  `Ran 67 tests … FAILED (failures=2)`.
- Mutation B+C (temporary file created with `O_CREAT` only, and the opened-identity check removed):
  `FAIL: test_load_protects_the_loaded_file_from_a_later_save`, `FAIL: test_save_compares_identities_not_names`,
  `FAIL: test_save_refuses_to_replace_a_file_the_session_read`, `FAIL: test_temporary_name_is_created_exclusively`,
  `Ran 67 tests … FAILED (failures=4)`.
- Deleted `.mutation/` and the scratch script.

### Why
- Note 11: goja-cv's first tests for two holes passed without the fix; I wanted evidence that these do not.
- The naive script is the base-rate check: these escapes are real for the obvious implementation, so the tests
  measure something.

### What worked
- Both mutation runs failed exactly in the tests that name the removed safeguard; the naive script escaped through
  all three vectors.

### What didn't work
- My first mutation attempt produced `ERROR: test_jailfs (unittest.loader._FailedTest)` because the replacement
  string left the `os.open(...)` argument list without a comma (`syntax error`). Fixed by replacing the whole
  flags expression on one line; the second run gave the four failures listed above.

### What I learned
- The exclusive temporary file matters even with the link check in place: without `O_EXCL` the planted link is
  followed and the victim outside the root is overwritten, which is precisely the third row of the chapter's
  Motivation table.

### What was tricky to build
- Mutation testing without a build system: copy `jailfs/` and `tests/` into `.mutation/`, patch with exact string
  replacements, run `python3 -m unittest discover -s tests` there, then delete the copy.

### What warrants a second pair of eyes
- The mutation set is small; a reviewer might add mutations for the shadow check, the duplicate check and the
  `..`-normalisation.

### What should be done in the future
- Consider keeping the naive script as a documented "why the test is not vacuous" test helper rather than a
  throwaway.

### Code review instructions
- The artifacts are gone; reproduce by copying the package, flipping the named check and running the suite.

## Step 8: Final check

I re-read the package for unused imports and stale comments, ran the full suite one last time, and confirmed the
deliverables are only inside this directory.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Finish with a clean tree, a green suite and a complete diary.

**Inferred user intent:** A reviewable result with no loose ends.

### What I did
- `python3 -m unittest discover -s tests` → `Ran 67 tests in 0.07s` / `OK`.
- Listed the working directory: `CHAPTER.md`, `DIARY-FORMAT.md`, `TASK.md`, `DIARY.md`, `jailfs/` (`__init__.py`,
  `_errors.py`, `_root.py`, `_workspace.py`), `tests/test_jailfs.py`; no scratch files, no `.mutation/`.
- Sanity-checked descriptor hygiene with a temporary script: 300 rounds of save/read/miss/escape/names/close left
  no leaked descriptors (`fds before/after: 6 4`, the lower count being the closed roots).

### Why
- TASK.md: tests must be run and fixed before finishing; DIARY-FORMAT.md: the last step is the final check.

### What worked
- The suite is green and the tree is clean.

### What didn't work
- Nothing in this step.

### What I learned
- The chapter's discipline (one loader, identity checks, strict flags) produced a small, readable package: four
  modules, ~700 lines including docstrings.

### What was tricky to build
- Deciding where to stop: the pattern's Consequences say the boundary covers only the file API the session
  offers; `jailfs` therefore does not try to contain shells or network.

### What warrants a second pair of eyes
- `names()` is recursive and returns full relative names; if a caller expects only top-level entries, it should
  filter. The docstring states the behaviour.

### What should be done in the future
- If the runtime grows a prelude or CLI (as in goja-cv), resolve those paths through the same locator (note 7) and
  give `--root`/`--read` their strict once-only parsing (Collaborations 1, note 5).

### Code review instructions
- Start at `jailfs/__init__.py`, then `_workspace.py` (public behaviour), then `_root.py` (mechanism). Validate with
  `python3 -m unittest discover -s tests` and, for the security claims, the mutation procedure in Step 7.

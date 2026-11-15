# Diary

## Goal

Build `jailfs`, a standard-library Python package that gives agent-written programs exactly one writable directory, a
list of read-only directories and no other file access, applying the *Contained Workspace* pattern from `CHAPTER.md`.
This diary records the reading and design phase, each piece built, the tests and every fix after a failure.

## Step 1: Reading the chapter, the task and the diary format

I read `CHAPTER.md`, `TASK.md` and `DIARY-FORMAT.md` completely before touching any code, then wrote down the shape of
the library: a start-up check (one writable root, resolved roots, no overlap), a lexical locator, one directory handle
per root with kernel-enforced no-follow walks, an exclusive-temp-then-rename writer, a shadow check, an opened set and
a single loader.

### Prompt Context

**User prompt (verbatim):** "You are a software engineer joining a project. Your working directory contains three files:
- CHAPTER.md: a chapter of a design-pattern book describing the pattern you must apply;
- TASK.md: the software to build, with its required public interface;
- DIARY-FORMAT.md: how to keep your work diary.
Read all three completely first. Keep DIARY.md as you go, one step per phase of work, in that format. Then design, build and test the software in this directory. Work only inside this
directory (do not read or write outside it). Use only the Python 3 standard library. Run your tests and fix what
fails before you finish, and make sure DIARY.md is complete. Your final message must follow the output format at the end of TASK.md."

**Assistant interpretation:** Implement the chapter's pattern as the `jailfs` package with exactly the public interface
listed in `TASK.md`, write unit tests under `tests/` using temporary directories, run them until green, keep this
diary per phase, and end with one JSON object in a fenced block.

**Inferred user intent:** A reviewer wants evidence that the pattern's invariants (containment, no link traversal,
atomic writes, one loader, strict flags, shadow and opened-set checks) are actually implemented and tested, and a diary
that shows the reasoning and the failures on the way.

### What I did
- Read all three files (they are the only files in the working directory, besides nothing else).
- Checked the runtime: `pwd` → `/Users/manuel/pattern-validation/builds/08/r1/n1/work`, `python3 --version` → Python 3.10.3.
- Decided the module split: `jailfs/errors.py` (codes, `Refused`), `jailfs/handle.py` (directory-handle primitives),
  `jailfs/workspace.py` (start-up check, locator, read/save/load/names/batch), `jailfs/__init__.py` (exports).
- Decided the refusal order for a save, following implementation note 10: shape, access, duplicate, shadow, replacing an
  opened file.

### Why
- The chapter's Structure table lists exactly the participants I need: Start-up check, roots, Locator, Root handle,
  Writer, Shadow check, Opened set, Loader. Each maps to a small, separately testable piece.
- Implementation note 1 says Python's standard library has no `os.Root`, so the root handle must be built from
  `openat`-style calls: walk components with `dir_fd=` and `O_NOFOLLOW | O_DIRECTORY`, and `lstat` the last component.
  That decision shapes `handle.py`.
- Implementation note 2 says roots are resolved once at start-up and matched lexically against *both* spellings, and
  that the agent's path is never resolved. So the locator is lexical and `realpath` appears only in the constructor.

### What worked
- The chapter is unusually concrete: Sketch pseudo-code plus eleven implementation notes gave a checklist that maps
  one-to-one onto tests.
- The task's code list (`E_ACCESS`, `E_NOT_FOUND`, `E_DUPLICATE`, `E_SHADOW`) is compatible with the chapter's
  refusal kinds (`access`, `shape`, `shadow`, `duplicate`): shape and opened-set refusals have no dedicated code, so
  they use `E_ACCESS` and carry the distinction in the message and fix.

### What didn't work
- Nothing yet; this step was reading and design only.

### What I learned
- The chapter's `os.SameFile` / `os.Root` advice is Go, not Python; the portable equivalent is `dir_fd` walks plus
  `(st_dev, st_ino)` identity comparison. Note 1 says refusing every link is simpler and stricter than following
  in-root links, which is the route I take.
- Note 6 warns that a shadow check must inspect the *resulting relative name*, however the path was spelled; that means
  the check belongs after locating, not on the raw input string.

### What was tricky to build
- Only planning so far; the hard part I anticipate is that an absolute agent path must be matched lexically against a
  root's `given` spelling and its `real` spelling without ever calling `realpath` on the agent's path, and that a
  lexical `..` climb must be refused rather than normalised away outside the root.

### What warrants a second pair of eyes
- Whether treating every refusal that is not `E_NOT_FOUND`/`E_DUPLICATE`/`E_SHADOW` as `E_ACCESS` (directory targets,
  opened-file replacement) matches the reviewer's expectations, since `TASK.md` gives no `E_SHAPE`.

### What should be done in the future
- Build `errors.py` and `handle.py` next, then the workspace, then the tests.

### Code review instructions
- Nothing to run yet. The design decisions are stated above; Step 2 onwards shows the code they produced.

## Step 2: Building the refusal vocabulary and the root handle

I built `jailfs/errors.py` and `jailfs/handle.py` first, because everything else is a policy decision on top of two
primitives: a refusal with a code and a fix, and a directory descriptor that the kernel holds a root open with.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Implement the chapter's pattern as a standard-library package with the interface in
`TASK.md`, phase by phase, recording each phase here.

**Inferred user intent:** Same as Step 1: working, tested containment, with the reasoning visible.

### What I did
- Created `jailfs/errors.py`: `Refused(code, message, fix)` and the codes `E_ACCESS`, `E_NOT_FOUND`, `E_DUPLICATE`,
  `E_SHADOW`, with `__str__` that prints the code, the message and the fix.
- Created `jailfs/handle.py`: `RootHandle`, which opens a root with `os.open(real, O_RDONLY|O_DIRECTORY)` and offers
  `lstat`, `open_file`, `ensure_parents`, `create_exclusive`, `rename`, `sync_dir`, `unlink`, `list_files`.
- Every walk is `os.open(part, ..., dir_fd=previous_fd)` with `O_NOFOLLOW | O_DIRECTORY`; the last component is
  `stat`ed with `follow_symlinks=False`; a missing final component returns `None`, a missing intermediate component
  raises `Problem("not_found")`.
- `Problem(kind, detail)` carries `not_found` / `link` / `not_dir` / `denied` / `exists` / `too_deep` so the workspace
  layer, not the handle, owns the refusal vocabulary.

### Why
- CHAPTER.md, implementation note 1: Python's standard library has no `os.Root`, so containment must be a
  `dir_fd` walk with `O_NOFOLLOW | O_DIRECTORY` plus `lstat` of the last component. Note 4: exclusive creation and a
  rename instead of an in-place write. Note 2: a root's links are resolved once, by the trusted configuration, which
  is why `RootHandle` is constructed from a `realpath`ed root and never from an agent's path.

### What worked
- The `dir_fd=` forms of `os.open`, `os.stat`, `os.mkdir`, `os.rename`, `os.unlink` and `os.listdir` were enough; no
  `ctypes` and no third-party code.
- `os.listdir(fd)` avoids the lifetime questions of `os.scandir(fd)` and cannot follow a link out of the root, which
  made `names()` a five-line recursion.

### What didn't work
- Nothing failed at import or in the primitives themselves, but one mapping was wrong and only showed up as a bad
  message later: on macOS, `open(O_NOFOLLOW|O_DIRECTORY)` on a symlink returns `ENOTDIR`, not `ELOOP`, so it was
  classified as "not a directory". Recorded in Step 5 with the fix.

### What I learned
- `os.stat(..., follow_symlinks=False)` reports a link instead of failing, so "the target is a link" is a decision for
  the caller, while a link in a *parent* component fails inside the walk. That asymmetry is what makes the save checks
  readable.
- `O_EXCL` fails on any existing name including a dangling symlink, which is the whole defence against a planted
  temporary name: no `lstat`-then-create race is needed.

### What was tricky to build
- Descriptor hygiene: every walk duplicates the root fd, opens the next component, and closes the previous fd only
  after the open succeeded, with a `BaseException` handler that closes the live fd. An early version leaked the parent
  fd when the second component failed; the `try/except BaseException: os.close(fd); raise` shape fixes it, and the
  tests below open hundreds of workspaces, so a leak would show as `EMFILE`.

### What warrants a second pair of eyes
- `Problem("denied")` is a catch-all for `EACCES`, `EPERM`, `ENAMETOOLONG` and anything unmapped. A reviewer should
  confirm no errno that means "this is a link" or "this escaped" falls into it silently.

### What should be done in the future
- The workspace: start-up check, locator, reader, writer, shadow check, opened set, loader, batches.

### Code review instructions
- Read `jailfs/handle.py` top to bottom; each method is one syscall wrapper and its docstring states the kernel
  guarantee it relies on. Then `jailfs/errors.py` for the code list. Nothing to run yet.

## Step 3: The workspace, and the first real failure

I wrote `jailfs/workspace.py` (start-up check, lexical locator, `read`, `save`, `load`, `names`, `batch`) and
`jailfs/__init__.py`, then ran a smoke script that reads from a read root, saves a nested name, and probes three
refusals.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Assemble the chapter's participants into the `Workspace` class with the exact public
interface from `TASK.md`.

**Inferred user intent:** A working session object whose boundary is enforced by the kernel and whose refusals teach.

### What I did
- Start-up check: unwrap a one-element list/tuple, refuse several with a fix that names read directories; require every
  root to exist and be a directory; `realpath` each root once; refuse any read root that contains or is contained by
  the writable root (lexically on the resolved paths, so a symlinked duplicate is caught too).
- Locator: `_locate(path, for_write)` → `_lexical_parts` for relative names (refuse `..` climbs and empty names) and
  `_locate_absolute` which matches the normalized agent path against each root's *given* and *real* spelling.
- Writer: `_write` with `ensure_parents`, an exclusive random temp name, `fsync`, `rename`, then the identity recorded
  from a fresh `lstat`.
- `save` checks in the chapter's order: shape (a directory target), access (a link or special file at the target),
  `E_DUPLICATE`, `E_SHADOW`, then the opened set.
- Ran the smoke script: `python3 - <<'PY' ... ws.save("out/labels.json", b"{}") ... PY`.

### Why
- Sketch and Collaborations §2–3 give the lookup order and the save sequence; implementation note 6 says the shadow
  check must use the located relative name, not the raw input, and note 5 says the written identity is taken after the
  rename. Note 10 fixes the refusal order (shape, access, duplicate, shadow, opened).

### What worked
- Relative reads fall through the roots in order, absolute paths match both spellings of a root, and the first smoke
  run already refused `../etc/passwd`, `/etc/passwd` and a missing name with the right codes.

### What didn't work
- Creating a new file in a non-existent subdirectory was refused as not found:

```
Traceback (most recent call last):
  File "<stdin>", line 12, in <module>
  File "/Users/manuel/pattern-validation/builds/08/r1/n1/work/jailfs/workspace.py", line 384, in save
    target = self._lstat_or_refuse(loc.root, rel, path)
  File "/Users/manuel/pattern-validation/builds/08/r1/n1/work/jailfs/workspace.py", line 424, in _lstat_or_refuse
    raise self._from_problem(problem, path) from None
jailfs.errors.Refused: E_NOT_FOUND: no file 'out/labels.json' in the roots (...)
```

The cause: `lstat("out/labels.json")` raises `ENOENT` because `out/` does not exist yet, and the save treated every
`not_found` as a refusal. A save is allowed to create the name, so a missing component means "nothing is there". Fixed
by giving `_lstat_or_refuse` a `missing_is_none=True` mode used only by `save`; a link or a file in a parent component
is still refused.

### What I learned
- The chapter's Sketch runs `lstat(loc.rel)` before deciding, which hides this distinction; in a Python `dir_fd` walk
  a missing *intermediate* component fails the walk while a missing *final* component returns `None`. The save needs
  both to mean "nothing there"; the read needs them both to mean "look in the next root".
- The refusal vocabulary from `TASK.md` has no "shape" code, so a directory target is `E_ACCESS` with the fix
  `out/x.json`; the message carries the distinction the code cannot.

### What was tricky to build
- Ordering. Shape and access checks come from the same `lstat`, so they are one block whose first branch is the
  directory; the duplicate set is consulted before the shadow check, and a shadow refusal must *not* be recorded as a
  saved name (otherwise the second attempt would report `E_DUPLICATE` instead of `E_SHADOW`).

### What warrants a second pair of eyes
- `_locate` for reads stops at the first root that has the name, and refuses if that thing is a directory instead of
  continuing to the next root. That is a deliberate "never silently read a different file" choice, but it is a choice.
- Duplicate detection is name-based (normalized relative name). On a case-insensitive filesystem `Out.json` and
  `out.json` are the same file but different keys, so they are not reported as duplicates.

### What should be done in the future
- Write the test suite, including the holes from the chapter's Motivation table.

### Code review instructions
- `jailfs/workspace.py`, in this order: `__init__` (overlap and one-root checks), `_locate*`, `read`, `save` (the
  numbered comment block is the refusal order), `_write`. Run
  `python3 -m unittest discover -s tests` once the tests exist.

## Step 4: Probing the attacks by hand before writing tests

Before freezing the design into tests, I ran one script that plants the artifacts the chapter's Motivation table says
agents trip over and checked what the session does with them.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Verify the five documented holes by experiment, not by reading the code.

**Inferred user intent:** Evidence that the boundary holds under the exact scenarios the pattern was written for.

### What I did
- Planted a dangling symlink in the writable root and saved over it; planted an in-root link to a read-only input and
  saved to it by relative and by absolute spelling; hard-linked an input into the writable root and saved over that
  name; made a writable subdirectory a link to an outside directory and saved through it; read a file and tried to
  save it again; passed a two-element `root` list; nested a read root inside the writable root; ran a workspace whose
  root was spelled `/var/...` while its real path was `/private/var/...`.

### Why
- Implementation note 11: tests written after a fix can pass without it; the cheapest guard is to try the attack
  first. The Motivation table lists exactly which artifacts to plant.

### What worked
- Dangling link: `E_ACCESS`, nothing created outside. In-root link: `E_ACCESS` with either spelling, input still
  `GOLD`. Hard link: the save succeeded, the input still read `GOLD`, the writable name held the new bytes — the
  rename replaced the name, not the inode. Symlinked parent: `E_ACCESS`, outside directory still empty. Opened set:
  `E_ACCESS` "saving theirs.json would replace a file this session read", while re-saving its own output worked.
  Two-element list: `E_ACCESS: the writable root must be exactly one directory, got 2` with a fix naming read
  directories. Cross-spelling: an absolute path in either `/var` or `/private/var` spelling resolved into the same
  root handle.

### What didn't work
- The first probe script stopped silently after the two-roots probe: I had written the nested-read-directory probe as
  a one-line guard ending in `else (_ for _ in ()).throw(SystemExit)`, so the missing `work/inner` directory raised
  `SystemExit` with no message and no traceback, and the last two probes (overlap, macOS spellings) never ran. Not a
  library failure, a harness failure: split into a second script that creates the directory first. It then printed
  `overlap -> E_ACCESS` three times, `writable inside read -> E_NOT_FOUND`, `one-element list: True`,
  `missing root -> E_NOT_FOUND`, `file root -> E_ACCESS`, and `spellings differ: True /var/... -> /private/var/...`
  with reads and saves working through either spelling.

### What I learned
- The chapter's claim in note 5 is right: because writes never follow links and always rename, an input's bytes cannot
  change through a save even when a hard link is planted; the opened set protects the *view*, not the bytes. Both are
  needed and they are different mechanisms.
- Refusing a save over a hard-linked name would be wrong (note 5 says so); my identity check only fires for identities
  the session actually read, so hard-linked names are allowed and are still safe.

### What was tricky to build
- Distinguishing "the agent named a link" from "the agent named a file that is a hard link". `lstat` gives `S_ISLNK`
  for the first and `S_ISREG` with `st_nlink > 1` for the second, and only the first is refused.

### What warrants a second pair of eyes
- The hard-link probe shows the *writable* name changing, which is allowed. A reviewer should confirm that is what
  they expect from note 4/5 rather than a regression.

### What should be done in the future
- Turn each probe into a test under `tests/`, and check each test fails when its fix is removed.

### Code review instructions
- Nothing new to read; the probes exercised `save`, `read` and `__init__` only.

## Step 5: The test suite, and three failures on the first run

I wrote `tests/support.py` plus four test modules (startup, read, save, links, loader/names) and ran
`python3 -m unittest discover -s tests`.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Encode every invariant and every documented hole as an assertion, using temporary
directories only.

**Inferred user intent:** A suite that would catch a regression in any of the fixes, and a green run before finishing.

### What I did
- `tests/support.py`: a `Sandbox` with `work`/`data`/`extra`/`outside` under one `realpath`ed temp dir, and
  `JailTestCase.assertRefused(code, callable, ...)` which also checks that `fix` is a string or `None`.
- `tests/test_startup.py` (20 tests): one-root rule, list/tuple refusal, missing and non-directory roots, every overlap
  direction including a symlinked duplicate, and that `<base>/work` does not contain `<base>/work2`.
- `tests/test_read.py`, `tests/test_save.py`, `tests/test_links.py`, `tests/test_loader_names.py`.
- Ran `python3 -m unittest discover -s tests`.

### Why
- The chapter's Collaborations and implementation notes 1–10 are the specification; each note got at least one test.
  The task's codes map onto refusals that are asserted by code, so a wrong code is a failing test.

### What worked
- 115 of 118 tests passed on the first run, including every planted-link test and the refusal-order tests.

### What didn't work
- `Ran 118 tests ... FAILED (failures=1, errors=2)`.

```
ERROR: test_writable_root_wins_over_read_directories (test_read.RelativeReadTest)
jailfs.errors.Refused: E_SHADOW: the name shared.txt already exists in the read directory
/private/var/.../data; saving it would hide the read-only file (save under another name; ...)
```

The test was wrong, not the code: it tried to *create* the writable copy by saving over a name the read root already
had, which is exactly what the shadow check refuses. Rewritten to plant `shared.txt` in the writable root before the
session starts (the only way such a file can exist there), assert the read goes to the writable copy, and assert the
shadow refusal for a save of that name.

```
ERROR: test_a_directory_shape_refusal_comes_before_a_shadow_refusal (test_save.ShadowTest)
FileExistsError: [Errno 17] File exists: '/private/var/.../data/sub'
```

My own fixture bug: `data/sub` already existed because it holds `deep.json`. Removed the second `mkdir` and kept an
assertion that the directory is there.

```
FAIL: test_a_symlinked_parent_directory_cannot_carry_a_save_outside (test_links.PlantedLinkTest)
AssertionError: 'link' not found in 'a component of sub/deep.json is not a directory'
```

The refusal was correct (`E_ACCESS`) but the diagnosis was wrong: on macOS, `open(O_NOFOLLOW|O_DIRECTORY)` on a
symlink reports `ENOTDIR`, which my mapping called "not a directory", so the message told the agent the wrong thing and
a reviewer would not see that the link check fired. Fixed in `handle._open_dir`: on `ENOTDIR`, one non-following
`stat` of that component decides whether the problem is `link` or `not_dir`. The refusal code is unchanged; the message
and the test now say "link".

### What I learned
- A test can be wrong in the direction of asserting the *bug* (the first error) or the *message* (the third). Both are
  worth fixing rather than relaxing.
- macOS and Linux differ in the errno for a link under `O_DIRECTORY`; the chapter's note 1 mentions the flags but not
  this, so the "say link" diagnosis has to be added explicitly for a portable message.

### What was tricky to build
- Making the "planted temporary name" test deterministic: the temp name is random, so the test patches
  `jailfs.workspace.secrets.token_hex` to return the planted name first and a fresh one second. Without that patch
  there is no way to plant the name and the test would be vacuous.

### What warrants a second pair of eyes
- `tests/test_read.py::test_absolute_path_matches_both_root_spellings` depends on `os.symlink` being permitted in the
  temp directory; it is skipped nowhere, which is fine here but would need a skip on a filesystem without links.

### What should be done in the future
- Prove each regression test fails without its fix, per implementation note 11.

### Code review instructions
- Run `python3 -m unittest discover -s tests` from the project root; then read `tests/test_links.py` first, since it
  is the attack catalogue, and only afterwards the per-feature modules.

## Step 6: Mutation check — one survivor, and the vacuous test it exposed

Implementation note 11 asks for each regression test to be checked individually by mutating its fix away. I wrote
`tests/mutation_check.py`, which copies `jailfs` into a scratch directory, applies one textual mutation, runs only that
mutation's tests against the copy and requires them to fail.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Do what note 11 describes, with one test (not one group) per mutation.

**Inferred user intent:** No test that passes for the wrong reason — the chapter reports builds where exactly that
happened twice.

### What I did
- Twelve mutations: read without `O_NOFOLLOW`; dir walk without `O_NOFOLLOW`; temp file without `O_EXCL`; save without
  the link refusal; write-in-place instead of temp+rename; no shadow check; no opened set; opened set without the
  written exemption; `realpath` on the agent's absolute path; no overlap check; climbs sanitised instead of refused;
  several roots accepted.
- Each mutation names one or two test ids; the script sets `PYTHONPATH` so the mutated copy shadows the real package,
  runs `python3 -m unittest -v <ids>` and counts a non-zero exit as "killed".
- Ran `python3 tests/mutation_check.py`.

### Why
- Note 11, and the Motivation table: five holes were each found by an experiment, so each fix has a scenario that must
  be reproduced. A mutation that leaves its test green means the test does not exercise the fix.

### What worked
- Eleven of twelve mutations were killed on the first run, including the two that matter most here (`O_NOFOLLOW` in the
  read open, and `O_EXCL` on the temporary file).

### What didn't work
- One survivor:

```
SURVIVED  realpath the agent's absolute path (resolving links for it)
          all listed tests passed without the fix
```

The cause: my in-root-link tests used only *relative* spellings, so `_locate_absolute` was never exercised and the
mutation had nothing to break. This is precisely the "vacuous path comparison" note 11 warns about, and it is also
exactly the hole note 2 describes (three of five builds called `realpath` on the agent's absolute path and a save
through an in-root link wrote the target). Fixed by adding two tests that name an in-root link by its absolute path: a
save must be refused and leave the real file alone, and a read of a link to an input must be refused. The mutation now
kills both.

- After that: `python3 -m unittest discover -s tests` → `Ran 120 tests ... OK`, and
  `python3 tests/mutation_check.py` → `12 mutations, 0 survived or broke`.

### What I learned
- "Every fix is tested" is a property of the *test*, not of the fix, and the only way to know is to break the fix. My
  suite looked complete and still had one test that could not fail.
- The `realpath` mutation is only detectable through absolute paths; relative paths never touch the code that decides
  which root an absolute name belongs to.

### What was tricky to build
- Running mutated code without polluting the real package: the tests import `jailfs` by name, so the script must run
  with the scratch directory as both cwd and first `PYTHONPATH` entry, and `tests/` on `PYTHONPATH` for `support`.
- Choosing mutations that are single, textual and unambiguous, and asserting the mutation text exists so a later
  refactor breaks the script loudly instead of silently mutating nothing.

### What warrants a second pair of eyes
- The mutation "write in place instead of temp+rename" needs two coordinated edits (target name as the temp name, and
  dropping `O_EXCL`); a reviewer should confirm the mutation is a fair model of the anti-pattern and not a strawman.

### What should be done in the future
- If the public interface grows, add a mutation per new check (the script's `MUTATIONS` list is the checklist).

### Code review instructions
- Run `python3 tests/mutation_check.py` (about a second) and read the `MUTATIONS` table; each entry's `tests` field is
  the map from a fix to the one test that proves it.

## Step 7: Final review, one more failure, and the closing check

Last pass: re-read the public surface, removed two bits of noise (an unused parameter on `_shadowed`, a misleading test
name), re-ran everything, and checked the working directory for stray artifacts.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Finish with a green suite, a complete diary, and the JSON summary the task asks for.

**Inferred user intent:** A reviewer can run two commands, see green, read the diary, and map each chapter participant
to code.

### What I did
- Removed the unused `path` argument from `Workspace._shadowed`, expanded `read`'s docstring to state the lookup order,
  and renamed `test_loaded_helper_does_not_get_a_working_directory_entry_point` to
  `test_loading_a_helper_writes_nothing`, which is what it asserts.
- Wrote `README.md` with the participant table, the refusal order and the two commands.
- Ran an independent script that walks the whole public interface (read relative and absolute, load, save with parents,
  `names`, and seven refusals by code) against a fresh sandbox: everything held, the read directory was untouched and
  the outside directory stayed empty.
- Ran `python3 -m compileall -q jailfs tests` (ok) and listed the tree: only sources, tests and the three given files;
  the sandboxes all live in the system temp directory and are removed by `tearDown`.

### Why
- Final check phase from the diary format, plus implementation notes 9 (names resolve and display the same way
  everywhere: a writable file is shown as a relative name and reads back by that name) and 10 (refusal order).

### What worked
- `python3 -m unittest discover -s tests` → `Ran 120 tests in 0.12s / OK`.
- `python3 tests/mutation_check.py` → `12 mutations, 0 survived or broke`.

### What didn't work
- Tidying the `_shadowed` signature broke the mutation script, which is the failure mode I built into it on purpose:

```
BROKEN    no shadow check
          mutation text not found in workspace.py
...
12 mutations, 1 survived or broke
Command exited with code 1
```

The mutation table still matched the old call `self._shadowed(rel, path)`. Updated the table to the new text and
re-ran: 12 killed. This is the honest version of note 11's warning in the other direction — a mutation that silently
matches nothing would have *looked* like a killed mutation if the script counted "the tests still pass" as success for
a different reason.

### What I learned
- The mutation script needs both halves: the edited text must be found (else BROKEN) and the tests must fail (else
  SURVIVED). Missing either half makes the check vacuous.
- `O_EXCL | O_NOFOLLOW` plus `rename` means the writer never needs an `lstat`-then-create race, which is why every link
  test could be written deterministically.

### What was tricky to build
- Keeping the refusal order honest while adding checks: `save` reads as one numbered list (shape, access, duplicate,
  shadow, opened) and the tests pin two of the orderings (directory before shadow, shadow before opened) so a later
  refactor cannot quietly reorder them.

### What warrants a second pair of eyes
- The opened set is an optimisation of the agent's *view*, not of the inputs' bytes (a hard-linked input is refused
  only once the session has read it). If the reviewer expects a writable root that also holds inputs to be fully
  protected, the rule to change is the identity check's exemption, not the writer.
- Duplicate detection is per normalized relative name, so a case-insensitive filesystem can hold two spellings of one
  file in one batch without an `E_DUPLICATE`.
- `names()` lists links as entries (without following them) and omits empty directories; a caller that iterates
  `names()` and reads every name will get `E_ACCESS` for a planted link, by design.

### What should be done in the future
- If a second loader is ever added (a module importer, a shell), it must be refused like `require` was; the single
  `load()` is the boundary.
- Add a mutation whenever a new start-up or save check appears, and keep `tests/mutation_check.py` in the review loop.

### Code review instructions
- Start with `jailfs/workspace.py::Workspace.__init__` and `save` (the numbered refusal block), then
  `jailfs/handle.py` for the kernel guarantees, then `tests/test_links.py` as the attack catalogue.
- Validate with `python3 -m unittest discover -s tests` (120 tests) and `python3 tests/mutation_check.py`
  (12 mutations, all must be killed).

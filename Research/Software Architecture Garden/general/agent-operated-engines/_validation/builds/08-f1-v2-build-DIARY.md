# Diary

## Goal

Build `jailfs`, a Python 3 (stdlib only) library that gives agent-written programs one writable directory, several
read-only ones, and no way out: every refusal raises `Refused` with a code and a fix. This diary records the design
decisions, the tests, the failures and the fixes.

## Step 1: Reading the chapter, the task and the diary format; designing the workspace

I read `CHAPTER.md` (Contained Workspace), `TASK.md` and `DIARY-FORMAT.md` completely, then mapped every participant
and implementation note of the chapter onto a module of the library before writing a line of code. The design keeps
the pattern's shape: one directory file descriptor per root, component-by-component `openat` with `O_NOFOLLOW`, an
identity set for "files this session read", an exclusively created random temporary file renamed into place, and one
loader.

### Prompt Context

**User prompt (verbatim):** "You are a software engineer joining a project. Your working directory contains three files:
- CHAPTER.md: a chapter of a design-pattern book describing the pattern you must apply;
- TASK.md: the software to build, with its required public interface;
- DIARY-FORMAT.md: how to keep your work diary.
Read all three completely first. Keep DIARY.md as you go, one step per phase of work, in that format. Then design, build and test the software in this directory. Work only inside this
directory (do not read or write outside it). Use only the Python 3 standard library. Run your tests and fix what
fails before you finish, and make sure DIARY.md is complete. Your final message must follow the output format at the end of TASK.md."

**Assistant interpretation:** The request asks me to (1) read the three documents, (2) apply the chapter's pattern to
the `jailfs` library described in `TASK.md` with exactly the published interface, (3) test it with `unittest` under
`tests/`, (4) keep a diary in the strict format of `DIARY-FORMAT.md`, and (5) answer with a single JSON object.

**Inferred user intent:** A grader wants evidence that the pattern — not merely a plausible-looking file API — was
implemented: kernel-level containment, identity-based overwrite protection, atomic exclusive writes, a single loader,
strict construction flags, and per-run duplicate detection, with tests that fail when a protection is removed.

### What I did
- Read all three documents whole; no files were created before this step.
- Checked the platform capabilities the pattern depends on: `python3 -VV` → `Python 3.10.3 (main, May 5 2023)` on
  `darwin`; `os.supports_dir_fd` contains `open, stat, mkdir, rename, unlink, readlink`; there is no `O_PATH`/`O_SEARCH`.
- Probed symlink behaviour with a scratch script: `os.open(n, O_RDONLY|O_NOFOLLOW, dir_fd=fd)` succeeds for a regular
  file, raises `[Errno 62] Too many levels of symbolic links` for an in-root link and for a link to `/etc/hosts`, and
  `os.rename(tmp, link, src_dir_fd=fd, dst_dir_fd=fd)` replaces the link itself rather than following it.
- Designed the module split below and the refusal messages each layer owns.

Design (module → participant in `CHAPTER.md`):

| Module | Participant |
| --- | --- |
| `jailfs/root.py` (`RootHandle`, `Location`) | Root handle + Locator's output |
| `jailfs/locator.py` | Locator (writable root, read roots, lookup order) |
| `jailfs/identity.py` (`FileId`, `OpenedSet`) | Opened set (read identities, written identities) |
| `jailfs/reader.py` | the read half of the file API, shared by `read` and `load` |
| `jailfs/writer.py` | Writer (shadow, link, directory, opened-file checks; exclusive temp + rename) |
| `jailfs/loader.py` | Loader (one way to load code; `require` refuses everything) |
| `jailfs/workspace.py` | Session facade, `batch()` (per-run duplicate detection), `names()` |
| `jailfs/errors.py` | `Refused` with `code`/`fix` |

### Why
- Note 1 ("Let the operating system enforce the root"): with no `O_PATH`/`openat2` in this Python, the closest
  equivalent is a directory fd per root plus a component-by-component walk where every component is opened with
  `O_NOFOLLOW|O_DIRECTORY`. `..` is resolved lexically inside the locator and never handed to the kernel, links are
  refused by the kernel, and each `openat` is relative to an already-verified directory fd — so nothing can leave the
  root.
- Note 2 ("Compare identities, not names"): the opened set stores `(st_dev, st_ino)` of every file the session opened,
  and saves compare `lstat` identities against it.
- Note 3: temporary files get `.<name>.<16 hex>.jailfs-tmp` names created with `O_CREAT|O_EXCL|O_NOFOLLOW`, retrying
  with a fresh random name on `FileExistsError`.
- Note 4: `load` is the only code path; `require` always refuses with a fix pointing at `load`.
- Note 5: `Workspace(root)` refuses a list/tuple of several directories at construction, naming `reads=` in the fix.
- Note 6: `E_SHADOW` refuses a save whose relative name already exists in a read directory.
- Note 7: read roots are resolved with `os.path.realpath` at construction so that a symlinked read root inside the
  workspace resolves to its target instead of tripping containment; both the given and the resolved spelling are
  accepted for absolute paths.
- Note 8: `Location.display` shows a writable-root file by its relative name and a read-root file by its absolute name.
- Note 10: `E_DUPLICATE` for the same path saved twice inside one `ws.batch()`.

### What worked
- The capability probe: `O_NOFOLLOW` is honoured for both files and directory components on this platform, and
  `rename` is a genuine atomic replace that never follows a link. The pattern's kernel-level backbone is available.
- `os.stat(..., dir_fd=..., follow_symlinks=False)` is supported, so `lstat` works relative to a directory fd.

### What didn't work
- My first `dir_fd` smoke test called `os.open("sub/a.txt", O_RDONLY|O_NOFOLLOW, dir_fd=fd)` on a *regular* file and I
  briefly read the success as "`O_NOFOLLOW` ignored". Retesting with a real symlink showed `[Errno 62]`; the success was
  correct behaviour for a non-link. No code was written on the wrong assumption.

### What I learned
- The chapter's Go-centric advice (`os.Root`, `os.SameFile`, `openat2`) needs translation: Python 3.10 has no `os.Root`,
  so the root handle has to be built from `dir_fd` calls, and identity comparison is `(st_dev, st_ino)`.
- Chapter note 6 explicitly permits *either* refusing shadowing saves *or* warning; I chose refusing (`E_SHADOW`)
  because the task's code list contains `E_SHADOW`, and I will skip read roots that are the writable root or inside it
  (otherwise every second save would look like a shadow).
- The chapter left one thing open: whether an absolute path spelled inside the *writable* root must also pass the shadow
  check. I decided yes — the shadow exists however the name was written — and documented it.

### What was tricky to build
- Nothing built yet; the tricky part was *designing* the order of checks in `save` so that each code is unambiguous:
  duplicate (batch) → shadow (read roots) → link → directory → opened-file identity → parents → exclusive temp →
  rename. The duplicate check runs before the write and the name is only *recorded* after a successful save, so a
  refused save does not poison the run.

### What warrants a second pair of eyes
- The claim that component-wise `O_NOFOLLOW` + lexical `..` removal is equivalent to `os.Root`: a reviewer should look
  for a path shape that reaches outside a root (e.g. `a/../../b`, `a/../..`, absolute spellings with `..`, links at
  intermediate components, links whose target is inside the root).
- `E_SHADOW` semantics for absolute paths into the writable root, and the choice to skip read roots nested in it.

### What should be done in the future
- Step 2: build `errors.py`, `paths.py` and `root.py` and probe them directly before wiring the policy layers.

### Code review instructions
- Read the design table above, then the modules in this order: `errors.py`, `paths.py`, `root.py`, `locator.py`,
  `identity.py`, `reader.py`, `writer.py`, `loader.py`, `workspace.py`.
- Validate with `python3 -m unittest discover -s tests` once tests exist (Step 6).

## Step 2: The root handle, the path splitter and the refusal type

This step built the layers everything else stands on: `Refused` with its four codes, the internal `Missing` signal,
`paths.py` (path text, lexical `..` removal, absolute-prefix containment) and `root.py` (`RootHandle`, `Location`,
`open_root`). The root handle is the chapter's *Root handle*: one directory descriptor per root, and every operation
opened one component at a time with `dir_fd=` and `O_NOFOLLOW`.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Build the containment primitives with the operating system's help, before any policy
(who may write where) is layered on top.

**Inferred user intent:** A reviewer must be able to see that containment is a kernel property, not a string check.

### What I did
- Created `jailfs/errors.py` (`Refused`, `Missing`, `E_ACCESS/E_NOT_FOUND/E_DUPLICATE/E_SHADOW`).
- Created `jailfs/paths.py` (`path_text`, `is_absolute`, `components`, `below`).
- Created `jailfs/root.py` (`RootHandle` with `open_fd`, `lstat`, `mkdirs`, `create_exclusive`, `rename`,
  `unlink`, `list_files`; `Location`; `open_root` for start-up validation).
- Renamed the internal `_label()` to a public `label()` so refusals in other modules can name the root.

### Why
- Implementation note 1: without `os.Root`, the equivalent is a directory fd plus `openat` per component with
  `O_DIRECTORY|O_NOFOLLOW`; `..` is removed lexically before the kernel ever sees the name, so a `..` can cancel a
  component but never climb out.
- Collaborations 5: every refusal from this layer names the root (`writable root /w/run42 (given as /var/...)`) and
  a fix.
- Implementation note 8: `Location.display` shows writable-root files by relative name and read-root files by
  absolute name.

### What worked
- `os.stat(..., dir_fd=..., follow_symlinks=False)`, `os.mkdir(..., dir_fd=)`, `os.rename(..., src_dir_fd=,
  dst_dir_fd=)` and `os.open(..., dir_fd=)` are all available on this Python 3.10.3/darwin, so `lstat`, parents,
  atomic rename and exclusive creation are all root-relative.
- `O_EXCL|O_NOFOLLOW|O_CREAT` turns a planted temporary name into `FileExistsError` instead of a write through a link.

### What didn't work
- `lstat` of `out/labels.json` when `out/` did not exist yet raised the internal `Missing` out of the public API
  (recorded in Step 6 with the traceback).

### What I learned
- Keeping the *policy* (opened set, shadow, duplicates) out of `RootHandle` pays off: the root handle knows only
  "inside the root or refused", so it can be probed by tests directly and reused by reader, writer and `names()`.

### What was tricky to build
- Descriptor lifetimes in the component walk: `_chain` dup's the root fd, then closes the previous fd after each
  successful `openat`, and closes the last one in a `finally`. Getting this wrong leaks one fd per component; the
  test in Step 10 (`test_refusals_do_not_leak_descriptors`) now guards it.

### What warrants a second pair of eyes
- `_chain` relies on `O_NOFOLLOW` for *directories*; a platform where `O_NOFOLLOW` is ignored would silently follow a
  link in the middle of a path. The probe in Step 1 showed `[Errno 62]` here, but this is the portability risk the
  chapter warns about.

### What should be done in the future
- Step 3: locator, opened set and reader on top of this layer.

### Code review instructions
- `jailfs/root.py`: read `_chain` first, then `open_fd`, `lstat`, `mkdirs`, `create_exclusive`, `rename`.
- `jailfs/paths.py`: check `components` (can `..` escape?) and `below` (can `/tmp/ws-other` match `/tmp/ws`?).

## Step 3: Locator, opened set and reader

This step added the chapter's *Locator* and *Opened set*, and the reader that uses both. The locator answers
"which root, which name" (relative: writable root, then read roots in order; absolute: must lie inside a root) and
refuses with messages that name the roots; the opened set records `(st_dev, st_ino)` of everything opened; the
reader tries locations in order, falls through only on "missing", refuses a directory, and notes the identity of
what it opened.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Implement lookup order and identity recording, the two things `read`, `save` and `load`
all share.

**Inferred user intent:** No second implementation of the lookup rules, and identity — not names — decides whether a
file is one the session was given.

### What I did
- Created `jailfs/locator.py` (`Locator.candidates`, `writable_location`, `shadow_roots`, `describe`,
  `read_spellings`) and `jailfs/identity.py` (`FileId`, `OpenedSet`).
- Created `jailfs/reader.py` (`Reader.read`, `Reader.text`).
- Absolute-path matching accepts both the given spelling and the `realpath` of each root (implementation note 7).

### Why
- Implementation note 2: `OpenedSet` stores identities, and `would_replace_opened` is the only name-independent test
  in the library.
- Applicability/Collaborations 3: "the locator looks in the writable root, then each read root".
- Refusals name the roots and the `--read`/`reads=` fix so an agent learns the boundary instead of probing it.

### What worked
- Falling through only on `Missing` means a planted dangling link in the writable root refuses the read instead of
  quietly serving the read-root file of the same name — stricter, and it keeps reads predictable.

### What didn't work
- Nothing failed in this step; the first integration smoke test came after Step 5.

### What I learned
- `realpath`-based root spellings were needed in practice: on this machine the temporary directory is under `/var`,
  which is a symlink to `/private/var`, so a root given as `/var/...` and its real path `/private/var/...` are both
  spellings an agent may use.

### What was tricky to build
- Deciding when a read should fall through: `EACCES`, `ELOOP` and "is a directory" must refuse, not fall through, or
  a link in the writable root could redirect a read to a read root.

### What warrants a second pair of eyes
- `shadow_roots` skips read roots equal to, or inside, the writable root; check that this cannot hide a real shadow.

### What should be done in the future
- Step 4: writer.

### Code review instructions
- `jailfs/locator.py`: `candidates` (order), `writable_location` (read roots are read-only), `below` usage.
- `jailfs/reader.py`: the `try/except Missing: continue` loop.

## Step 4: The writer

The writer is the chapter's `save` sketch, in code: locate into the writable root, duplicate check for the current
run, link/directory/opened-identity checks by `lstat`, parents created inside the root, bytes into an exclusively
created random temporary file, `fsync`, `rename` into place, then record the new identity as written.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** One write path, atomically, that refuses links, directories, read-only names and files
the session read.

**Inferred user intent:** The five holes in the chapter's table must all be closed by construction, not by luck.

### What I did
- Created `jailfs/writer.py` (`Writer.save`, `_refuse_shadow`, `_refuse_protected_target`, `_write_temp`,
  `temp_name`, `_as_bytes`, `_write_all`).
- `save` rejects `str` with a `TypeError` that shows the encode call, and accepts `bytes`-like values.
- Temporary files: `.<name>.<16 hex>.jailfs-tmp`, up to 8 attempts on `FileExistsError`.

### Why
- Implementation note 3 (random, exclusive temporary names), note 6 (`E_SHADOW`), note 10 (`E_DUPLICATE`), note 2
  (identity), and the sketch's rule "rename replaces a name, it never follows a link".
- The duplicate claim is recorded only *after* a successful save, so a refused save does not consume the name.

### What worked
- `os.rename` over an existing name is atomic and replaces a link rather than following it; the check order still
  refuses links up front, so the link is not silently replaced either.

### What didn't work
- The check order was wrong at first: the shadow check ran before the link/identity checks, so a save over a file the
  session read reported `E_SHADOW` instead of `E_ACCESS` (traceback and fix in Steps 7 and 8).

### What I learned
- `E_SHADOW` and "would replace a file this session read" can both apply to the same name; the data-integrity
  refusal must win, otherwise the more important message is hidden.

### What was tricky to build
- Making the temporary name injectable for tests without weakening it: `temp_name` is a module-level function so a
  test can patch it with `mock.patch.object(writer_module, "temp_name", ...)` and plant a link at the exact name.

### What warrants a second pair of eyes
- The window between `lstat` and `rename`: the rename never follows a link, so the worst case is replacing a link
  with a regular file. Confirm that is acceptable for the writable root (the chapter's text implies yes).

### What should be done in the future
- Step 5: loader and session facade.

### Code review instructions
- `jailfs/writer.py`: `save` (order of the four checks), `_write_temp` (exclusive creation, cleanup on failure).

## Step 5: Loader, session facade and package exports

The last build step: `Loader` (the one way to load code, with `require` refusing everything), the `Workspace`
facade with `read`, `save`, `load`, `names`, `batch`, `close` and the strict single-root construction, and the
package exports.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Publish exactly the interface `TASK.md` requires, with one loader and one strict root.

**Inferred user intent:** Other code will be tested against this interface, so the names and refusal codes must be
exactly as specified.

### What I did
- Created `jailfs/loader.py` (`Loader.load`, `load_with_origin`, `Loader.require`), `jailfs/workspace.py`
  (`_one_root`, `_read_roots`, `Batch`, `Workspace`) and `jailfs/__init__.py` (exports `Workspace`, `Refused`,
  `Batch`, `Location`, `CODES`, the four codes).
- `_one_root` accepts a one-element list/tuple and refuses several with the fix
  "--root takes one directory; add read-only directories with --read DIR (reads=[...])".
- `Workspace.close`/context manager close every root handle; a closed workspace refuses with `E_ACCESS`.

### Why
- Implementation notes 4 (one loader) and 5 (strict flags); Variations "read-only session" is reachable by simply
  never saving.
- `E_DUPLICATE` lives in `Batch`, scoped to one `with ws.batch():` block (note 10); nested batches start a new run.

### What worked
- `batch()` yields the workspace, so both `with ws.batch():` and `with ws.batch() as run:` work.

### What didn't work
- After writing `jailfs/__init__.py` I was unsure whether the import block had swallowed the `Location`/`Batch`
  imports, so I applied an edit that replaced the block with itself (a no-op) and then read the file back: the block
  was valid and the imports were in place. Nothing was broken; I record it because the no-op edit was wasted work.

### What I learned
- Loading a `.py` helper and reading a data file must share one reader, otherwise the opened set would miss loaded
  scripts and a save could replace a helper.

### What was tricky to build
- Startup failure cleanup: if a read root is invalid, the writable root's descriptor must be closed, or repeated
  failed sessions leak descriptors (now guarded by `test_a_failed_read_root_closes_the_writable_root`).

### What warrants a second pair of eyes
- `Workspace.save` returns `None`; if calling code wanted the `Location`, that is currently only internal.

### What should be done in the future
- Step 6: integrate and smoke-test the whole package.

### Code review instructions
- `jailfs/workspace.py` (construction, `batch`, `close`), `jailfs/loader.py` (suffix rule, `require`).

## Step 6: First integration smoke test, and the bug it found

Before writing the suite I ran the whole package by hand from the shell: build a workspace, read a read-root file,
save a nested file, load a helper, and provoke four refusals. It found one real bug: `lstat` of a name whose parent
directory did not exist yet let the internal `Missing` signal escape to the caller.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Prove the layers work together (locator + roots + reader + writer + loader) before
investing in the test suite.

**Inferred user intent:** Do not hand in a library that only looks right module by module.

### What I did
- Ran an inline script: `python3 -c "import jailfs, tempfile, os; ..."` creating a writable root and a read root in
  temporary directories, then `ws.read('tile.tif')`, `ws.save('out/labels.json', b'{}')`, `ws.names()`,
  `ws.load('lib.py')`, and refusals for `../etc/passwd`, `save('tile.tif')`, `save('/etc/passwd')`,
  `save(<read root>/x.json)` and a duplicate save inside `with ws.batch():`.
- Fixed `RootHandle.lstat` to catch `Missing` (a missing parent means "nothing is there") and return `None`.

### Why
- The writer calls `lstat` before creating parents, so for a brand-new `out/labels.json` the parent chain does not
  exist yet; that must be "target absent", not an error.

### What worked
- Everything else behaved on the first run: read fell through to the read root, save created `out/`, `names()`
  listed `['out/labels.json']`, `load` returned the helper text, and all four refusals carried a code and a fix.

### What didn't work
- Exact failure before the fix:

```text
Traceback (most recent call last):
  File ".../jailfs/root.py", line 187, in _chain
    nfd = os.open(part, _DIR_OPEN | _NOFOLLOW, dir_fd=fd)
FileNotFoundError: [Errno 2] No such file or directory: 'out'

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File ".../jailfs/workspace.py", line 191, in save
    self._writer.save(path, data, self._current_batch())
  File ".../jailfs/writer.py", line 84, in save
    self._refuse_shadow(loc)  # E_SHADOW
  File ".../jailfs/writer.py", line 116, in _refuse_shadow
    existing = root.lstat(loc.parts, "save")
  File ".../jailfs/root.py", line 213, in lstat
    with self._chain(parts[:-1], action) as dfd:
  File ".../jailfs/root.py", line 189, in _chain
    self._refuse(err, parts, action)
  File ".../jailfs/root.py", line 135, in _refuse
    raise Missing(rel)
jailfs.errors.Missing: out
```

### What I learned
- Internal signals (`Missing`) must be converted at the boundary; a reader may fall through on them, a writer must see
  "absent". Returning `None` from `lstat` on `Missing` covers both callers.

### What was tricky to build
- The symptom was an internal exception type leaking out of a public call for an *ordinary* first save; the cause was
  that the parent chain, not the final component, was what was missing, and `os.stat(name, dir_fd=...)` was never
  reached.

### What warrants a second pair of eyes
- `lstat` swallowing `Missing` must not swallow "the writable root itself disappeared" in a way that hides a real
  failure; Step 10 tests that case (`test_save_into_a_deleted_writable_root_is_not_found`).

### What should be done in the future
- Step 7: write the suite.

### Code review instructions
- `jailfs/root.py` `lstat`; `jailfs/writer.py` `save`.

## Step 7: Writing the suite and running it

I wrote the tests module by module, each file aimed at one force in the chapter: reading and lookup order, writing
and containment, links, loading, the session (batch/names/lifecycle) and construction. Then I ran the whole suite for
the first time.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Turn every hole, rule and note of the chapter into a test, using temporary directories
only.

**Inferred user intent:** A reviewer wants failures, not assertions of correctness.

### What I did
- Created `tests/support.py` (fixture of three temp dirs, `put`/`get` helpers, and `refusal(code, fn, ...)` which also
  checks that every refusal has a code from the list, a non-empty `fix`, and the fix inside `str(exc)`).
- Created `tests/test_read.py`, `tests/test_save.py`, `tests/test_links.py`, `tests/test_load.py`,
  `tests/test_session.py`, `tests/test_roots.py`.
- Ran `python3 -m unittest discover -s tests`.

### Why
- Chapter note 11 and "Consequences": the opened-file and duplicate checks are the engine's own, so they need explicit
  tests; the kernel-level ones need tests that would fail if the code started resolving strings again.
- `fix` inside `str(exc)` encodes Collaborations 5 ("every refusal names the roots and the fix").

### What worked
- 97 of 99 tests passed immediately; the failures were two genuine design/data errors, not typos.

### What didn't work
- Exact output of the first full run:

```text
$ python3 -m unittest discover -s tests
...
FAIL: test_save_refuses_to_replace_a_file_the_session_read (test_save.SaveProtectsWhatWasRead)
AssertionError: 'E_SHADOW' != 'E_ACCESS'
 : expected E_ACCESS, got E_SHADOW: 'tile.tif' already exists in the read-only read-only root
 /private/var/.../data; the save would shadow it, so later reads of that name would return your copy
 (fix: save under another name, or read the read-only copy by its absolute path /private/var/.../data/tile.tif)
...
ERROR: test_absolute_load_of_a_trusted_helper_ignores_a_shadowing_copy (test_load.Load)
TypeError: save() writes bytes, not str; encode the text first, e.g. ws.save('out.json', json.dumps(obj).encode())
----------------------------------------------------------------------
Ran 99 tests in 0.124s

FAILED (failures=1, errors=1)
```

### What I learned
- The shadow check ran before the target's own protection, so a data-integrity refusal was masked by a convenience
  refusal. Also "read-only read-only root" showed that `role` ("read-only root") and the message prefix ("the
  read-only %s") were both saying it.
- My `save()` refuses `str` (correctly, per `TASK.md`'s `data: bytes`), so a test that passed a `str` was a test bug,
  not a library bug.

### What was tricky to build
- Deciding which code wins when two refusals apply to the same save (duplicate, shadow, link, opened file); the order
  is now documented in `writer.py`'s module docstring.

### What warrants a second pair of eyes
- The rewritten test `test_save_refuses_to_replace_a_file_the_session_read` now needs the write root to hold the file
  *and* a read root to hold the same name, to exercise both conditions at once; confirm it still tests what its name
  says.

### What should be done in the future
- Step 8: fix the two failures.

### Code review instructions
- `tests/support.py` `refusal`, then any `test_*.py` file; each test name states the rule it guards.

## Step 8: Fixing what the suite found

Three changes: the writer's check order (target protection before the shadow check), message wording (role and
prefix no longer say "read-only" twice), and two tests rewritten to test the right thing.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Fix the library where it was wrong and the tests where they were wrong, then get to a
green run.

**Inferred user intent:** Failures must be understood, not silenced.

### What I did
- `jailfs/writer.py`: `_refuse_protected_target` now runs before `_refuse_shadow`, with a comment saying why
  (`E_ACCESS` = data integrity, `E_SHADOW` = convenience).
- `jailfs/writer.py` / `jailfs/locator.py`: shadow and read-only messages now say "in the read-only root /data"
  instead of "in the read-only read-only root".
- `tests/test_save.py`: split the protection test into (a) a name held by both roots where the session read the write
  root's copy (now `E_ACCESS`), and (b) saving an absolute name inside a read root (`E_ACCESS`, "read roots are
  read-only").
- `tests/test_load.py`: replaced the impossible "save a shadowing copy, then load it" test with two honest ones: a
  copy planted *outside* jailfs does shadow a relative `load`, and `load` by absolute path is immune; and jailfs
  refuses to create such a copy at all (`E_SHADOW`).

### Why
- Implementation note 6 says a shadow can be refused *or* warned about, so the shadow refusal must not outrank the
  chapter's core invariant ("inputs cannot be modified by a session").
- A test that cannot express its premise must be replaced, not weakened.

### What worked
- After these changes the suite went green: `Ran 100 tests in 0.070s / OK`.

### What didn't work
- Then Step 10's descriptor test failed with `AssertionError: 7 != 4` because the baseline was taken before the
  workspace opened its three root handles (recorded in Step 10).

### What I learned
- `E_SHADOW` makes the note-6 shadow scenario unreachable *through jailfs*; the only way a relative `load` can be
  shadowed is a file planted in the writable root by something else. Both facts are now tested.

### What was tricky to build
- Keeping the two-load-paths test honest while `save` refuses shadows: the fixture had to write the shadowing copy with
  plain `open()` rather than through the workspace.

### What warrants a second pair of eyes
- Whether refusing an absolute save into the writable root whose relative name exists in a read root is desirable; I
  chose consistency with relative saves and documented it in the README.

### What should be done in the future
- Step 9: prove the tests fail without their fixes (note 11).

### Code review instructions
- `jailfs/writer.py` `save` (order), `tests/test_save.py::SaveProtectsWhatWasRead`,
  `tests/test_load.py::Load`.

## Step 9: Proving the tests fail without their fixes (implementation note 11)

Note 11 says a security test that passes without its fix is worthless. I automated the proof: `tools/regression_check.py`
removes one protection at a time from the real sources, runs the tests that guard it, and restores the file.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Show, mechanically, that each guard is load-bearing.

**Inferred user intent:** Evidence that the tests are regression tests, not documentation.

### What I did
- Created `tools/regression_check.py` with seven mutations: link check removed, identity check removed, shadow check
  removed, `O_EXCL`/`O_NOFOLLOW` dropped from `create_exclusive`, `..` silently dropped, the root handle joining one
  string instead of walking with `O_NOFOLLOW`, and "last `--root` wins".
- Each mutation is applied to the file, the guarding tests are run, and the file is restored from a backup in a
  `finally` block.

### Why
- Chapter note 11, verbatim: "Test that a regression test fails without its fix."

### What worked
- Final result — every mutation turns its tests red:

```text
== save no longer refuses a link at the target
   red: FAIL: test_save_refuses_a_dangling_link_target (test_save.SaveOverLinks)
   red: FAIL: test_save_refuses_a_target_that_is_a_link (test_save.SaveOverLinks)
   red: FAIL: test_an_in_root_link_to_an_opened_input_is_refused (test_save.SaveProtectsWhatWasRead)
== save no longer compares file identity against what was read
   red: FAIL: test_a_file_read_from_the_writable_root_is_protected_too
   red: FAIL: test_save_refuses_a_hard_link_to_an_opened_file
   red: FAIL: test_save_refuses_to_replace_a_file_the_session_read
   red: FAIL: test_the_opened_set_survives_batches
== saves no longer refuse to shadow a read-only file
   red: FAIL: test_save_whose_name_exists_in_a_read_root_is_refused
   red: FAIL: test_shadowing_is_refused_for_an_absolute_save_into_the_writable_root
   red: FAIL: test_a_shadowing_copy_cannot_be_saved_in_the_first_place
== temporary files are created with O_CREAT instead of O_EXCL
   red: ERROR: test_a_second_random_name_is_used_when_the_first_is_taken
   red: FAIL: test_a_planted_temporary_name_is_never_written_through
== '..' in a relative name is dropped instead of refused
   red: FAIL: test_leading_dotdot_is_refused
   red: FAIL: test_relative_dotdot_is_refused
== the root handle joins a string instead of walking with O_NOFOLLOW
   red: FAIL: test_absolute_link_to_a_file_inside_the_same_root_is_refused
   red: FAIL: test_dangling_link_is_refused_rather_than_falling_through
   red: FAIL: test_in_root_link_to_outside_file_is_refused
   red: FAIL: test_link_to_a_read_root_file_is_refused
== Workspace keeps the last --root instead of refusing several
   red: FAIL: test_a_tuple_of_two_directories_is_refused
   red: FAIL: test_three_directories_are_refused
   red: FAIL: test_two_directories_as_root_are_refused
   red: FAIL: test_the_read_vector_that_made_the_gold_data_writable_is_refused
   red: ERROR: test_an_empty_list_is_refused
```

### What didn't work
- The first version of the tool was itself a vacuous test. It ran `python3 -m unittest -v test_save.SaveOverLinks`
  from the repository root, where `tests/` is not a package, so every run "failed" with import errors and the tool
  printed success:

```text
== save no longer refuses a link at the target
   red: ERROR: test_save (unittest.loader._FailedTest)
   ok: 2 test(s) fail without this protection
```

  Fixed by running from `tests/` with `PYTHONPATH` set to the repository root, and by treating a `_FailedTest` as a
  problem instead of a red test.

### What I learned
- The `_FailedTest` output is exactly the shape of false confidence note 11 warns about; my own tool reproduced it.

### What was tricky to build
- The identity mutation needed a test that distinguishes names from identity: the hard-link test
  (`os.link(read_only_file, ws/alias.tif)`, then `save('alias.tif')`) fails only when the identity check is gone,
  because the name is not in the opened set and the path is inside the writable root.

### What warrants a second pair of eyes
- Whether the mutation strings stay in sync with the sources; the tool prints `SKIP ... pattern not found` and counts
  it as a failure, so drift is visible.

### What should be done in the future
- Step 10: hardening and boundary tests.

### Code review instructions
- `python3 tools/regression_check.py`; then read `MUTATIONS` and check each mutation is the *only* thing removed.

## Step 10: Hardening and boundary tests

Two test files were added after the first green run: descriptor hygiene and odd names (`test_hardening.py`), and
boundary cases — hard links, vanishing roots, parallel sessions, roots given as links, directory shadowing
(`test_boundaries.py`). One real fix came out of it: a name longer than the filesystem allows surfaced as a raw
`OSError` instead of a `Refused`.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Cover the cases that a long agent run and a hostile directory will produce, not just the
happy path.

**Inferred user intent:** The library must survive real use in a dust pipeline of dozens of agents.

### What I did
- Created `tests/test_hardening.py` (descriptor counts across 250 refusals and saves, names with spaces/unicode/dots,
  a ten-level-deep path, `names()` skipping a linked directory, `0o600`/`0o700` modes, opened set across batches).
- Created `tests/test_boundaries.py` (hard link to an unread input stays intact because rename replaces the *name*,
  reading through a hard link then saving is refused, deleted writable root → `E_NOT_FOUND`, deleted read root →
  `E_NOT_FOUND`, two sessions do not see each other, a writable root given as a link, a directory in the writable root
  does not fall through to a read root, saving below a name that exists as a directory in a read root).
- Added `errno.ENAMETOOLONG` to `RootHandle._refuse` (`E_ACCESS`, fix "use a shorter file name") and a test for it.

### Why
- Chapter Consequences: "Parallel runs cannot interfere with each other's files"; note 9: one writable root per run.
- A `save` that leaks a descriptor or cannot store `naïve.json` is not usable, however safe it is.

### What worked
- The hard-link test showed the design's second line of defence: even if the identity check did not exist, `rename`
  replaces the *name* in the writable root and the read-only file keeps its inode and bytes.

### What didn't work
- `AssertionError: 7 != 4` in `test_refusals_do_not_leak_descriptors`: the baseline was taken before the workspace
  opened its three root handles, so the three extra descriptors were the workspace itself. Fixed by taking the
  baseline after `self.workspace()`.

### What I learned
- `names()` must skip a linked directory rather than walk it; `os.stat(..., follow_symlinks=False)` plus
  `O_NOFOLLOW|O_DIRECTORY` when descending does that, and a link planted between the two calls is skipped, not
  followed.

### What was tricky to build
- Deleting the writable root out from under a live workspace still leaves a valid descriptor for an unlinked
  directory; every operation then fails with `ENOENT`, which the writer converts to `E_NOT_FOUND` ("the writable root
  ... disappeared while saving") rather than a mystery.

### What warrants a second pair of eyes
- The descriptor test uses `/dev/fd` and skips when unavailable; on Linux `/proc/self/fd` would be the equivalent, so
  the guard is `skipTest`, not an assertion.

### What should be done in the future
- Step 11: final check.

### Code review instructions
- `tests/test_hardening.py::Descriptors`, `tests/test_boundaries.py::HardLinks` and `::VanishingRoots`.

## Step 11: Final check

Last pass: re-read the required interface against the code, ran the suite from a clean tree, ran the end-to-end
demonstration an agent runtime would perform, ran the mutation check one final time, and removed the byte-code
caches.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Confirm that the deliverable matches `TASK.md`'s interface, that every test passes, that
the protections are load-bearing, and that the diary is complete.

**Inferred user intent:** A final, verifiable state, plus the JSON report the task asks for.

### What I did
- Checked each required name: `Workspace(root, reads=())`, `ws.read`, `ws.save`, `ws.load`, `ws.names`, `ws.batch`,
  `Refused.code`/`Refused.fix`, and the four codes (`E_ACCESS`, `E_NOT_FOUND`, `E_DUPLICATE`, `E_SHADOW`).
- Ran `python3 -m unittest discover -s tests` → `Ran 125 tests in 0.130s / OK`.
- Ran `python3 tools/regression_check.py` → all seven mutations red, exit 0 (no mutation survived).
- Ran `python3 -m compileall -q jailfs tests tools` → clean.
- Ran an end-to-end demonstration (write root, gold root, helpers root; read, load, save, then five refusals):

```text
read     : b'TIFF'
load     : "def label(t):\n    return t['id']\n"
names    : ['out/labels.json']
escape   : E_ACCESS | fix: relative paths are names inside the workspace; ...
save gold: E_ACCESS | fix: read roots are read-only; save a relative name into the writable root ...
shadow   : E_SHADOW | fix: save under another name, or read the read-only copy by its absolute path ...
duplicate: E_DUPLICATE | fix: save each name once per program run; ...
require  : E_ACCESS | fix: load(name) is the one way to load code, and it resolves names like read()
gold intact: True
```

- Removed `__pycache__` directories so the tree holds only sources, tests, the tool, the README and the diary.

### Why
- The task's interface is what other code will be tested against; the diary format requires this step; note 11
  requires the mutation check to keep passing as the code changes.

### What worked
- Everything above ran clean on the first try at this stage; the only changes in the final pass were editorial
  (README, diary), plus `errno.ENAMETOOLONG` handled in Step 10.

### What didn't work
- Nothing failed in this step.

### What I learned
- The interface fits the chapter without extensions: `batch()` (note 10), `names()` and the four codes are enough;
  `require` is the only extra method, and it exists to make the "one loader" rule visible.

### What was tricky to build
- Sequencing the final pass: the mutation tool rewrites sources, so the clean suite run and the demonstration had to
  come after it (the tool restores every file in a `finally` block; the green suite afterwards confirms it).

### What warrants a second pair of eyes
- Two judgement calls are not forced by the chapter: `E_SHADOW` applies to absolute paths into the writable root as
  well as relative ones, and `E_ACCESS` (not `E_NOT_FOUND`) is the code for a construction-time multi-root refusal.
  Both are documented in `README.md`.

### What should be done in the future
- If the runtime grows a `require`-like second loader or a shell, the boundary has to be re-established at process
  level (chapter, Consequences); a `readdir`-based `names()` variant for very large roots would also be worth it.

### Code review instructions
- Validate with `python3 -m unittest discover -s tests` and `python3 tools/regression_check.py`.
- Read `README.md` for the interface table, then `jailfs/writer.py` (check order) and `jailfs/root.py` (`_chain`) —
  those are the two places where a mistake would silently open a hole.

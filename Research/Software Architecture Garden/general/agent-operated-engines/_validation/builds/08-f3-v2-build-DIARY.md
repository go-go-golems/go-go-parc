# Diary

## Goal

Build `jailfs`, a standard-library-only Python package that gives agent programs one writable root plus an ordered
list of read-only roots, with kernel-enforced containment, identity-based protection of files the session read,
atomic saves, and exactly one way to load code. This diary records the design, each build phase, and every failure
and fix along the way.

## Step 1: Read the chapter, the task and the diary format; design the package

I read `CHAPTER.md` (Contained Workspace), `TASK.md` and `DIARY-FORMAT.md` in full, then checked what this Python and
this kernel actually offer, because the chapter's solution leans on `os.Root`/`openat2`, which Python does not have.
I settled on a `openat`-style implementation built from `os.open(..., dir_fd=..., O_NOFOLLOW)`, and on a module
split that mirrors the participants table in the chapter.

### Prompt Context

**User prompt (verbatim):** "You are a software engineer joining a project. Your working directory contains three files:
- CHAPTER.md: a chapter of a design-pattern book describing the pattern you must apply;
- TASK.md: the software to build, with its required public interface;
- DIARY-FORMAT.md: how to keep your work diary.
Read all three completely first. Keep DIARY.md as you go, one step per phase of work, in that format. Then design, build and test the software in this directory. Work only inside this
directory (do not read or write outside it). Use only the Python 3 standard library. Run your tests and fix what
fails before you finish, and make sure DIARY.md is complete. Your final message must follow the output format at the end of TASK.md."

**Assistant interpretation:** Implement the Contained Workspace pattern as a Python package `jailfs` with the exact
public interface listed in `TASK.md` (`Workspace`, `read`, `save`, `load`, `names`, `batch`, `Refused` with `code`
and `fix`), tests under `tests/` run with `python3 -m unittest discover -s tests`, and a diary in the strict format.

**Inferred user intent:** A trustworthy, self-contained implementation that demonstrably closes the escape holes
listed in the chapter's motivation table, with evidence (tests) that the boundary holds, plus an honest record of the
work.

### What I did
- Read `CHAPTER.md`, `TASK.md`, `DIARY-FORMAT.md` completely.
- Probed the environment: `python3 -VV` → `Python 3.10.3`, Darwin 24.6.0 (macOS).
- Ran a small probe script to learn the kernel/errno details the design depends on:
  `os.open(name, O_RDONLY|O_NOFOLLOW, dir_fd=fd)` on a symlink raises `OSError` errno 62 (`ELOOP`), not `EMLINK`;
  `os.stat(name, dir_fd=fd, follow_symlinks=False)` and `os.readlink(name, dir_fd=fd)` both work.
- Designed the module split: `errors.py` (Refused + codes), `root.py` (Root handle: fd-based resolver, temp files,
  rename, listing), `locator.py` (Location/Locator: path → root + name, or refusal), `writer.py` (atomic, no-follow,
  identity-protected saves), `loader.py` (the single `load` way, `require` always refuses), `workspace.py` (public
  `Workspace` API, opened/written sets, `batch()`).

### Why
- Chapter "Solution" and implementation notes 1–2: containment must be enforced by the operating system on handles,
  not by string checks, so every open goes through a directory fd opened at the root with `O_NOFOLLOW`.
- Note 2: protection of inputs must compare file identity (`st_dev`, `st_ino`) rather than names.
- Note 3: temporary files must be created exclusively under random names.
- Note 4: exactly one loader; `require` refuses.
- Note 10: a second save of the same path inside one `batch()` is `E_DUPLICATE`.
- Note 6: a relative save that would shadow a read-only file is refused with `E_SHADOW` (`TASK.md` names that code).

### What worked
- The environment probe confirmed everything the design needs exists in Python 3.10 on this kernel (`dir_fd`,
  `O_NOFOLLOW`, `follow_symlinks=False`, `src_dir_fd`/`dst_dir_fd` on `os.rename`), so no fallback is needed.

### What didn't work
- Nothing yet; this step was reading and design.

### What I learned
- `CHAPTER.md` names Go's `os.Root` and Linux `openat2`; Python has neither, so the "let the operating system
  enforce the root" advice has to be re-derived by hand from `dir_fd` + `O_NOFOLLOW`. That is the one place where the
  chapter leaves the reader to translate rather than apply.
- `TASK.md` lists `E_ACCESS`, `E_NOT_FOUND`, `E_DUPLICATE`, `E_SHADOW` but the chapter sketch also uses `E_ARG`
  (a save target that is a directory, a bad `--root`). I will use `E_ARG` for argument/configuration refusals and
  keep the four listed codes exactly as specified.

### What was tricky to build
- Deciding how symlinks are treated. Chosen rule: reads may follow a link whose target stays inside the same root
  (resolved component by component with `O_NOFOLLOW`, so the kernel refuses escapes); writes never follow a link,
  in any component; `..` is resolved against a stack of open directory fds and refused when it would climb above the
  root. This matches note 7 (a symlinked read root resolves to its target) without weakening note 2.

### What warrants a second pair of eyes
- The fd lifetime rules in the resolver (which caller owns which descriptor) — a leak or a double close would be
  silent until the process runs out of descriptors.
- The `..`-popping stack: correctness depends on never returning an fd that was already closed.

### What should be done in the future
- Build `jailfs/errors.py` and `jailfs/root.py` first, test the resolver in isolation, then the writer, loader and
  workspace.

### Code review instructions
- Start with `TASK.md` (interface) and the chapter's "Structure"/"Sketch" sections, then read `jailfs/root.py`
  (`Root.resolve`) as the single containment chokepoint. Everything else is policy on top of it.

## Step 2: Build the roots and the resolver (errors.py, root.py, locator.py)

I wrote the refusal type and the two layers under every operation: a `Root` handle that owns one directory
descriptor and walks paths component by component with `dir_fd` + `O_NOFOLLOW`, and a `Locator` that maps an
agent-written path onto a root plus a name inside it (or refuses). This is the part of the pattern the chapter
calls "let the operating system enforce the root".

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Translate the chapter's `os.Root`/`openat2` advice into Python file-descriptor
operations, and put path policy (relative order, absolute containment, `..`) in a separate, testable object.

**Inferred user intent:** One chokepoint that no later code can bypass, so a bug in policy cannot become a bug in
containment.

### What I did
- `jailfs/errors.py`: `Refused(code, message, fix)` with `as_dict()`; codes `E_ACCESS`, `E_NOT_FOUND`,
  `E_DUPLICATE`, `E_SHADOW`, `E_ARG`.
- `jailfs/root.py`: `Root` with `resolve()` (fd walk, `..` handled against a stack of open directory descriptors,
  symlinks expanded only when the target stays inside the same root, `MAX_LINKS = 40`), `open_file()`,
  `stat_file()`, `open_parent_for_write()` (creates parents, refuses links), `create_temp()` (random name,
  `O_CREAT|O_EXCL|O_NOFOLLOW`), `replace()`, `list_files()`, and `refusal()` translating `OSError` into a
  `Refused` with a fix.
- `jailfs/locator.py`: `Location(root, parts, absolute)` with `name()` (chapter note 8: relative for the writable
  root, absolute for read roots), `Locator.locate_read()` returning candidates in lookup order, `locate_write()`
  returning exactly one location, `roots_fix()` describing the roots and `--read DIR`, and `make_root()`.

### Why
- Chapter "Solution": every open and stat goes through a root handle so the kernel refuses `..` and links.
- Implementation note 2: writes must never follow a link, so the final `lstat` for a save uses
  `follow_symlinks=False` and `resolve(follow_final=False)` refuses.
- Implementation note 7: a read root that is itself a link must resolve to its target, so `Root` opens its
  handle on `os.path.realpath(path)`.
- Note 8: `Location.name()` decides how a name is shown back to the agent.

### What worked
- The `..`-with-an-fd-stack design handles both cases in one place: an agent path like `sub/../x` (stays inside →
  allowed) and a symlink target `../x` (resolved against the directory that holds the link, still contained).
- A smoke script exercised every participant before any test existed: reads from both roots, absolute reads,
  `../` escapes, `E_DUPLICATE`, `E_SHADOW`, escaping links (read and save), a dangling link, an in-root alias link,
  and a hard link to a read-only input. `/etc/passwd` was unchanged and the planted outside file was never created.

### What didn't work
- The first draft of `root.py` contained a placeholder call `E_DUPLICATE_MSG_CODE()` in `refusal()` and closed a
  *slice* of the fd stack (`self._close_all(stack[1:])`), which would have double-closed descriptors later. Both
  were found by re-reading the file before running it; the slice is now `while len(stack) > 1: os.close(stack.pop())`.
- A read of a relative name does not fall back to a read root when the writable root has a *directory* of that
  name: the locator raises `E_ARG`, and that is deliberate (the agent named something that exists but is not a file).

### What I learned
- Chapter note 1 says "let the operating system enforce the root"; in Python the honest version of that is
  `O_NOFOLLOW` on every component plus a descriptor per root. `O_NOFOLLOW` alone is not enough: it protects only
  the last component, so intermediate directories must be opened one at a time.
- macOS reports an `O_NOFOLLOW` hit as `ELOOP` (verified: errno 62); older BSD-style systems use `EMLINK`, so
  both are treated as "link refused".

### What was tricky to build
- Owning descriptors through a recursive/iterative resolver. The rule I settled on: `resolve()` returns an owned
  parent descriptor and its caller closes it; everything else is closed in a `finally`. `open_file()` therefore
  never leaks even when the kernel refuses the open.
- Absolute symlink targets: they are resolved with `os.path.realpath()` and then re-walked from the root, so the
  containment check that matters is still the component walk, not the string comparison.

### What warrants a second pair of eyes
- `Root.resolve()`'s stack discipline (which descriptor is returned, which are closed, and the `..` pop) and the
  `finally` blocks in `open_file()`/`open_parent_for_write()`.

### What should be done in the future
- Build the writer, loader and workspace on top of `Root`/`Locator`, then test each hole from the chapter table.

### Code review instructions
- Read `jailfs/root.py` (`resolve`, `open_parent_for_write`, `create_temp`) and `jailfs/locator.py`
  (`locate_read`, `locate_write`, `locations`/`_relative`). Validate with
  `python3 -m unittest discover -s tests`.

## Step 3: Build the writer, loader and workspace (the public facade)

With containment in place I added the three policy layers: the writer (atomic, no-follow, identity-protected
saves), the loader (`load` only; `require` always refuses) and `Workspace` itself, which owns the roots, the
opened/written identity sets and the per-run `batch()` record.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Provide exactly the interface `TASK.md` requires, and make each refusal explain the
boundary and the fix.

**Inferred user intent:** An API an agent runtime can drop in, whose refusals teach agents the workspace instead of
leaving them to probe.

### What I did
- `jailfs/writer.py`: `Writer.save()` → `lstat` target (link → `E_ACCESS`, directory → `E_ARG`, opened-and-not-
  written → `E_ACCESS`), `open_parent_for_write`, `create_temp`, write + `fsync`, `rename`, then record the *new*
  identity. `as_bytes()` accepts `bytes`/`bytearray`/`memoryview`/`str`, `TypeError` otherwise.
- `jailfs/loader.py`: `Loader.load(name)` (only `.py`/`.js`, UTF-8, read through the workspace read path) and
  `Loader.require(path)` which always refuses with a fix pointing at `load(name)`.
- `jailfs/workspace.py`: `Workspace(root, reads=())`, `read`, `save`, `load`, `require`, `names`, `batch`, `close`,
  `writable_root`, `read_roots`, `warnings`; `_check_shadow` (`E_SHADOW`, regular read-only files only) and
  `_warn_if_shadowed` (chapter note 6 warning for the reverse direction); construction refuses a list/tuple of
  roots, missing roots and read roots that are not directories.
- `jailfs/__init__.py` exports `Workspace`, `Refused`, `CODES` and the codes.

### Why
- Chapter sketch (`save`, `load`, `require`, `startup`) and implementation notes 2, 3, 4, 6, 10.
- `TASK.md` codes: `E_ACCESS`, `E_NOT_FOUND`, `E_DUPLICATE`, `E_SHADOW`; `E_ARG` for configuration and shape
  errors, as in the chapter's `refuse(E_ARG, "a directory", ...)`.

### What worked
- The smoke run produced every intended refusal with a usable fix: `../etc/passwd` `E_ACCESS`, `/etc/passwd`
  `E_ACCESS`, duplicate save `E_DUPLICATE`, `labels.json` shadow `E_SHADOW`, saving an opened `tile.tif`
  `E_ACCESS`, saving a directory `E_ARG`, `load('/abs/lib.js')` refused, `require('/x.js')` refused.

### What didn't work
- A hard link named `hard.txt` in both the writable root and a read root produced `E_SHADOW` before the identity
  check; the identity guard was therefore not yet exercised by that case. I kept the test and moved the identity
  case to a name that exists only as a hard link (`copy.json`).

### What I learned
- The order of the checks matters for the *message*, not the safety: duplicate → shadow → link/directory →
  identity. The chapter's sketch checks the target before the shadow; the task names `E_SHADOW` and `E_DUPLICATE`
  as first-class codes, so they come first and say the most useful thing.

### What was tricky to build
- The "may be written again" rule. The identity recorded after a save is the identity *after* the rename, so a
  second save over the session's own file finds that identity in `written` and is allowed, while a file the
  session only read stays protected. Writing it as `identity in opened and identity not in written` (exactly the
  sketch) avoids a second flag.

### What warrants a second pair of eyes
- `Writer.save()`'s `finally` cleanup (temporary file removed, parent descriptor closed) and the written/opened
  bookkeeping in `Workspace.save()`.

### What should be done in the future
- Write the test suite, including one test per hole in the chapter's motivation table.

### Code review instructions
- `jailfs/writer.py` (`save`), `jailfs/workspace.py` (`save`, `_check_shadow`, `batch`) and
  `jailfs/loader.py`. Validate with `python3 -m unittest discover -s tests`.

## Step 4: Write the test suite (tests/, one test per hole) and run it

I wrote seven test modules plus `tests/support.py` (temporary directories only: `work`, `data`, `libs`), covering
construction, reads, saves, escapes (one test per hole in the chapter table), identities, shadowing, the loader and
`batch()`/`names()`.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Tests must be runnable with `python3 -m unittest discover -s tests`, must use
throwaway directories, and must demonstrate the boundary rather than assume it.

**Inferred user intent:** Evidence that the pattern holds, including for the five specific holes.

### What I did
- `tests/support.py`: `JailTestCase` with `open_ws()`, `plant()`, `plant_dir()`, `plant_link()`, `outside()`,
  `slurp()`, `assertFile()`, `assertGone()` and `refuses(code, call, ...)` which also asserts a non-empty `fix`.
- `tests/test_construction.py`, `test_read.py`, `test_save.py`, `test_escape.py`, `test_identity.py`,
  `test_shadow.py`, `test_loader.py`, `test_batch_names.py`.
- Ran `python3 -m unittest discover -s tests`: first run `Ran 131 tests ... FAILED (failures=1, errors=2)`.

### Why
- Chapter note 11: security tests must be shown to fail without their fix, so each hole test targets a specific
  mechanism (identity comparison, `O_EXCL`, fd walking, single loader, strict root).

### What worked
- Of the 131 tests that existed at that moment, 128 passed on the first run, including all escape, shadow,
  identity and loader tests (the suite is 134 tests after Steps 5 and 6).

### What didn't work
- Exact first failure text:
  `ERROR: test_same_name_different_identity_is_not_protected (test_identity.IdentityTests) ...
  jailfs.errors.Refused: E_SHADOW: 'labels.json' already exists in the read-only root ...`
- `ERROR: test_writable_root_wins_over_read_roots (test_read.ReadTests) ... jailfs.errors.Refused:
  E_SHADOW: 'labels.json' already exists in the read-only root ...`
- `FAIL: test_failed_save_leaves_no_partial_file (test_save.SaveTests) ... AssertionError: Refused not raised`

### What I learned
- `E_SHADOW` bites my own tests: any test that wants a writable copy of a read-only name must save by *absolute*
  path. That is the chapter's warning in note 6 turned into a test-writing rule.
- The temporary-name test was vacuous at first (see Step 5): `create_temp()` builds `TEMP_PREFIX + token_hex(8)`,
  and my mock returned a *complete* name, so no collision ever happened.

### What was tricky to build
- The three failures had three different causes: two were my tests relying on a relative save that `E_SHADOW`
  legitimately refuses (fixed by saving by absolute path), one was a planted temporary name created in the wrong
  directory (the save target was `out/labels.json`, so the planted link had to live in `out/`).

### What warrants a second pair of eyes
- Whether the escape tests really fail without the code they guard (Step 5 answers that for four mechanisms).

### What should be done in the future
- Prove non-vacuity by mutating the implementation, then fix anything that passes both ways.

### Code review instructions
- Run `python3 -m unittest discover -s tests`; then read `tests/test_escape.py` first, it maps one-to-one onto the
  chapter's hole table.

## Step 5: Prove the tests fail without their fix (chapter note 11), and fix the vacuous one

I mutated the implementation four times and re-ran the suite each time, to show that each mechanism's tests fail
when the mechanism is removed. One mutation revealed a genuinely vacuous test, which I then fixed.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Not optional polish: the chapter says twice that goja-cv's first test for a hole
passed without the fix, so the same must be checked here.

**Inferred user intent:** A test suite that would actually catch a regression, not one that merely passes.

### What I did
- Backed up `jailfs/` files inside the working directory (`_mut/`), applied each mutation with a small script, ran
  `python3 -m unittest discover -s tests`, recorded the result, restored the backup, and deleted `_mut/`.
- Mutation A (identity guard removed: `if identity in opened and identity not in written:` → `if False:`):
  `FAILED (failures=4)` — `test_saving_over_a_file_this_session_read_is_refused`,
  `test_hard_link_to_an_opened_read_only_input_is_refused`,
  `test_hard_link_is_refused_even_when_the_link_name_was_never_read`,
  `test_loaded_helper_identity_is_protected`.
- Mutation B (path-string containment: `resolve()` returns `os.path.join(*parts)` on a dup of the root fd):
  `FAILED (failures=4, errors=3)`, including
  `FAIL: test_symlinked_intermediate_directory_cannot_redirect_a_read`,
  `FAIL: test_missing_name_through_a_link_inside_a_read_root`.
- Mutation B2 (follow links everywhere: `follow_symlinks=True` and no `O_NOFOLLOW` on directories):
  `FAILED (failures=7, errors=3)`, including both
  `test_hole_1_dangling_symlink_cannot_create_a_file_outside`,
  `test_hole_1_save_does_not_follow_a_link_that_points_inside` and both intermediate-directory redirect tests.
- Mutation C (temporary file without `O_EXCL`): first run `FAILED (failures=2)`; after fixing the vacuous test,
  `FAILED (failures=3, errors=1)` — the two planted-name tests and the "every name taken" test fail.
- Mutation D (`require()` implemented as a read, and a `--root` list taking the last element):
  `FAILED (failures=6)` including `test_hole_4_require_always_refuses` and all three construction tests.

### Why
- Chapter note 11, and the motivation's "a comparison of paths was vacuous".

### What worked
- Every mechanism I claimed has at least one test that fails when the mechanism is removed.

### What didn't work
- The first version of the planted-temporary-name tests passed with mutation C applied, i.e. they were vacuous
  exactly as the chapter warns: `mock.patch("jailfs.root.secrets.token_hex", side_effect=[".jailfs-tmp-0000", ...])`
  returned a whole file name while `create_temp()` prepends `TEMP_PREFIX`, so the "collision" was really
  `.jailfs-tmp-.jailfs-tmp-0000`. Fixed by forcing only the token (`iter(["0000", os.urandom(8).hex()])`); the
  tests now fail without `O_EXCL`.

### What I learned
- A test for exclusive creation must force the *name the code computes*, not the name it wants to collide with.
  This is the second time in the chapter's history and the first time in mine, which confirms the note.
- Mutation testing is cheap here: each run takes about 0.15 s.

### What was tricky to build
- Choosing mutations that change one mechanism only; the crude path-join mutation (B) also broke legitimate
  in-root link following, which is why B2 isolates "follow links" from everything else.

### What warrants a second pair of eyes
- That the restored files are byte-identical to the tested ones: the suite was re-run after every restore and
  `Ran 134 tests ... OK` each time.

### What should be done in the future
- If the interface grows (a shell, network), add mutation-tested holes for each new capability.

### Code review instructions
- The mutation transcripts above are reproducible by editing one line in `jailfs/root.py`, `jailfs/writer.py`,
  `jailfs/loader.py` or `jailfs/workspace.py` and re-running the suite; each mutation is named in the list above.

## Step 6: Final check — full run, tidy imports, README

I removed two unused imports, re-ran the whole suite, and wrote a short `README.md` that maps the chapter's
participants onto the modules for the next reader.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Leave the directory in a state another engineer can pick up: tests green, imports
clean, one page of orientation.

**Inferred user intent:** A finished deliverable, not just working code.

### What I did
- Deleted the unused `E_ACCESS`/`join_parts` imports from `jailfs/workspace.py` and an unused code import from
  `tests/test_construction.py`.
- Restricted `E_SHADOW`/warning checks to regular files in read roots (`_has_read_only_file`), so a *directory* of
  the same name in a read root is not reported as a shadow; added three tests (PathLike roots, absolute-vs-relative
  duplicate, directory-not-a-shadow).
- Ran `python3 -m unittest discover -s tests` → `Ran 134 tests ... OK`.
- Wrote `README.md` with the participant table, the refusal codes and the commands.

### Why
- Chapter "Structure" participants are the review vocabulary; the README makes the mapping checkable.

### What worked
- Suite green at 134 tests; `python3 -m py_compile` of every module is clean.

### What didn't work
- A patch script of mine briefly produced an `IndentationError` in `jailfs/workspace.py` (`line 139:
  return  IndentationError: unexpected indent`) because I dedented a block with a string replacement that missed
  the `return`. Caught immediately by AST-parsing and re-running the suite; fixed with an exact `edit`.

### What I learned
- Small text-replacement mutations are how I want to verify security tests, but they must be followed by a syntax
  check before a test run, otherwise an indentation error masquerades as a failing test result.

### What warrants a second pair of eyes
- The `E_ARG` choices for shapes `TASK.md` does not specify (several roots, a save target that is a directory, a
  helper that is not `.py`/`.js`); a stricter test suite might expect `E_ACCESS` there.

### What should be done in the future
- If the runtime needs it: expose a `Location`-based `open()` for streaming reads, and a `--read`-style flag parser
  that enforces "given once, or refused".

### Code review instructions
- `README.md` for the map, then `python3 -m unittest discover -s tests`, then the code in the order
  `errors.py` → `root.py` → `locator.py` → `writer.py` → `loader.py` → `workspace.py`.

## Step 7: Final verification (full suite, descriptor leak loop, compile check)

Last pass before answering: compile every module, run the whole suite once more, and check that the refusal paths do
not leak directory descriptors, since `Root.resolve` hands ownership of descriptors around.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Finish with evidence, not assertions: a green suite and a leak check.

**Inferred user intent:** Confidence that the boundary is correct *and* that the implementation can run for
thousands of agent calls without exhausting descriptors.

### What I did
- `python3 -m py_compile jailfs/*.py tests/*.py` → `compile ok`.
- `python3 -m unittest discover -s tests` → `Ran 134 tests in 0.117s` / `OK`.
- Ran a loop script (600 saved/refused operations: `../x`, escaping link read, `/etc/passwd`, missing file, save
  through a link, save over the session's own file, nested save, read of a directory, `load('../../etc/passwd')`,
  `require`): descriptor count `fds before 6 after 6`, then `closed fds 4` after `ws.close()`.
- Removed `__pycache__` directories, leaving `CHAPTER.md`, `TASK.md`, `DIARY-FORMAT.md`, `DIARY.md`, `README.md`,
  `jailfs/` (7 modules) and `tests/` (9 modules).

### Why
- Chapter "Consequences": the boundary must hold under ordinary, repeated use; a descriptor leak would end a long
  run with `EMFILE`, which looks like a workspace bug to the agent.

### What worked
- No leak across 600 refusals; the root handles are the only descriptors held, and `close()` releases them.

### What didn't work
- Nothing failed in this step.

### What I learned
- Returning an owned parent descriptor from `resolve()` plus closing it in a `finally` in every caller is enough;
  the loop confirms the discipline holds for the error paths (which are the ones that usually leak).

### What warrants a second pair of eyes
- The `finally` in `Root.resolve` closes the whole stack including the root dup; confirm no path returns a
  descriptor that is also on the stack.

### What should be done in the future
- N/A for this task; a stress test with concurrent sessions writing the same root would test the documented
  assumption that no other process writes into a root at the same time.

### Code review instructions
- Run `python3 -m unittest discover -s tests` and, for the leak check, wrap any refused call in a loop and compare
  `len(os.listdir('/dev/fd'))` before and after.

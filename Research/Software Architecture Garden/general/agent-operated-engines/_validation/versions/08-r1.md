---
title: Contained Workspace
aliases:
  - Agent filesystem sandbox
  - One writable root, read-only mounts
  - Least-privilege file access for agents
status: established
type: architecture-garden-pattern
created: 2026-11-14
tags:
  - architecture-garden
  - patterns
  - agents
  - security
  - filesystem
related_notes:
  - "[[00-overview|Agent-Operated Engines - A Pattern Language]]"
---

# Chapter 8 · Contained Workspace

*One writable directory, read-only inputs, and writes that cannot escape, follow links or overwrite what was read.*

Rating: ★★ (close to invariant: any system with this problem converges on this shape; see the overview).

## Intent

Give an agent's programs exactly the file access their task needs: one directory they may write, a list of
directories they may only read, and nothing else. Resolve every path against those roots with the operating system's
own containment, refuse writes through links, write atomically, and, where the runtime can load code, allow one way
to do it. The boundary then holds even when the agent, or a file planted for it, tries to cross it.

## Also known as

Workspace jail, least-privilege mounts, capability-based file access, sandboxed working directory.

## Motivation

goja-cv lets agents open scans, save results and load helper scripts. The dust pipeline runs dozens of these agents
over a gold dataset labelled by hand; a single stray write could corrupt it. Within a week, five holes were found in
goja-cv's file access, each by an agent, a reviewer or a test written for something else:

| Hole | Found by | Fix |
| --- | --- | --- |
| A dangling symlink inside the output root let a save create a file outside it. | code review | a workspace built on the operating system's root-relative file access (`os.Root`) |
| An in-root symlink to an opened input let a save overwrite the input. | a cold review, by experiment | compare file identity (`os.SameFile`); never write through a link |
| Predictable temporary file names could be planted as symlinks before a save. | code review | exclusive creation under random names |
| `require("/abs/path.js")` loaded any JavaScript file on disk. | a pi agent, which used it to load its library from outside the roots | the require loader refuses all files; `cv.load` is the one way |
| A repeated `--root` flag silently kept the last value, so an old registration made the gold-data folder writable. | testing an existing registration against a new version | `--root` may be given once, with a fix pointing to `--read` |

None of these was a deliberate attack. Agents probe boundaries in the course of doing their task: the `require` escape
was used within two runs of being available.

Other systems face the same problem:

- A **coding agent** edits one repository and reads reference material, but not the user's home directory.
- A **plugin host** gives each plugin a data directory and read access to shared assets.
- A **CI job** gets a writable work tree, read-only caches and no access to other jobs.

## Problem

**When an agent's programs may name any path, a single unexpected path (a link, a repeated flag, a second loading
mechanism) lets them read or overwrite what they should not, and checks on path strings do not stop it.**

## Forces

- **Convenience against containment.** Agents work best with real paths and real files; every restriction is a
  failure mode they must be told about.
- **Name checks against identity checks.** Comparing path strings is easy and wrong under links; comparing file
  identities is right and needs the operating system's help. Roots come from trusted configuration and may be
  resolved; an agent's path may hide a link, and resolving it in the program does the kernel's work wrongly.
- **Mounting anywhere against one owner per file.** A read root inside the writable root has two policies, and the
  writable one wins.
- **Many ways in against one.** Each additional way to load or write files (a require function, a module system, a
  shell) is one more boundary to defend.
- **Flexible configuration against strict flags.** Repeatable flags and last-value-wins defaults are convenient and
  turn mistakes into silent privilege changes.
- **Atomic writes against simplicity.** Writing in place is simple; a crash or race then leaves a half-written file or
  a file written through a planted link.

## Solution

**Therefore: give each session one writable root and a list of read-only roots that do not overlap it, and resolve
every path an agent writes with the operating system's root-relative file operations, which refuse any path, `..` or
link that leaves the root. Resolve links in the roots once, at start-up; never resolve the agent's paths. Relative
paths name files in the writable root, then in the read-only roots in order; absolute paths must lie inside one.
Writes go only to the writable root, never through a link, and always through an exclusively created temporary file
renamed into place. If the runtime can load code, allow one way to do it. Make every security-relevant flag strict:
given once, or refused.**

## Applicability

Use it when:

- an agent or its programs read and write files on a machine that also holds data they must not change;
- inputs are valuable (labelled datasets, source of truth) and outputs are scratch;
- several agents run side by side and must not see each other's work.

Do not use it when:

- the agent needs a whole machine (installing packages, running services); use a container or virtual machine, and
  apply this pattern inside it if programs still need narrower access;
- all data arrives through the API; there is nothing to contain;
- the operating system offers neither root-relative operations nor directory handles with no-follow opens; string
  checks alone give a false sense of safety, so isolate at the process level instead, and do not keep them as a
  fallback.

## Structure

In a small library most of these are a function or a field.

| Participant | Responsibility | Needed |
| --- | --- | --- |
| **Start-up check** | One writable root; resolves root links once; refuses overlapping roots. | Always |
| **Writable and read roots** | One directory to write; directories to read, in lookup order. | Always |
| **Locator** | Maps an agent's path to a root and a relative name, lexically, or refuses. | Always |
| **Root handle** | A directory handle per root; every open goes through it, so the kernel refuses escapes. | Always |
| **Writer** | Exclusive random temporary file, then rename; refuses links and directories. | Always |
| **Shadow check** | Refuses a save whose relative name exists in a read root. | Only when relative reads search read roots |
| **Opened set** | Identities the session read and did not write; saves may not replace them. | Only when the writable root holds inputs |
| **Loader** | The single way to load code, through the locator. | Only when the runtime can load code |

## Collaborations

1. The session starts. The start-up check resolves each root's links once, refuses a second writable root with a fix
   that names the read flag, and refuses overlapping roots.
2. The agent opens `tile.tif`. The locator looks in the writable root, then each read root; the root handle opens the
   file without following links. If an opened set is kept, the file's identity joins it.
3. The agent saves `out/labels.json`. The locator maps it into the writable root. The writer refuses a link or a
   directory there, the shadow check and opened set (if present) have their say, and the writer renames an
   exclusively created, randomly named temporary file over the target.
4. Only when the runtime can load code: `load(name)` resolves through the locator like any read. Any other loader the
   runtime has (goja-cv's `require`) refuses files.
5. Every refusal names the roots and the fix ("relative paths are names inside the workspace; add `--read DIR` to
   read from DIR").

## Sketch

```text
value Root: given: path, real: path, handle: directory handle
value Location: root: Root, rel: name inside the root

startup(writable, reads) → Session | Error
  if writable is not exactly one directory: return error("one writable root; add others with --read DIR")
  roots = map(canonical, [writable] ++ reads)         -- links resolved here, once, in trusted configuration
  if a read root lies inside the writable root, or the reverse: return error("roots overlap")

locate(path, forWrite) → Location | Refusal
  candidates = forWrite ? [roots[0]] : roots
  if path is relative:                                -- lexical; a climb above the root is refused
    return first r in candidates where forWrite or r.handle.exists(path), as Location(r, path)
  for r in candidates, base in [r.given, r.real]:    -- lexical; the agent's path is never resolved
    if path lies under base: return Location(r, path relative to base)
  return refuse(access, "outside the roots")

open(path) → (File, Location) | Refusal
  loc = locate(path, forWrite: false)
  f = loc.root.handle.openNoFollow(loc.rel)          -- the kernel refuses .., links and escapes
  opened = opened ++ [identity(f)]                    -- only when an opened set is kept
  return f, loc

save(path, bytes) → ok | Refusal
  loc = locate(path, forWrite: true)
  st = loc.root.handle.lstat(loc.rel)                 -- do not follow a link
  if st is link:      return refuse(access, "saves do not follow links")
  if st is directory: return refuse(shape, "a directory", fix: loc.rel ++ "/x.json")
  if a read root has loc.rel: return refuse(shadow)   -- only with a shadow check; however path was spelled
  if identity(st) in opened and not in written:       -- only with an opened set
    return refuse(access, "would replace a file this session read")
  loc.root.handle.makeParents(loc.rel)                -- inside the root, never outside
  tmp = loc.root.handle.createExclusive(randomName()) -- fails if anything is there
  write(tmp, bytes); rename(tmp, loc.rel)             -- rename replaces a name, never follows a link
  written = written ++ [identity(loc.root.handle.lstat(loc.rel))]   -- taken after the rename

load(name) → Script | Refusal                         -- only when the runtime can load code
  (f, loc) = open(name)
  return compile(read(f), origin: loc)
```

Refusal kinds (`access`, `shape`, `shadow`) stand for your own error vocabulary.

## Implementation notes

1. **Let the operating system enforce the root.** goja-cv's first workspace checked path strings and was escaped by a
   dangling symlink. Its second opens every root as a Go `os.Root`, so the kernel refuses `..`, absolute links and
   links that leave the root; Linux `openat2` with `RESOLVE_BENEATH` does the same. Where neither exists (Python's
   standard library, for one), walk the path one component at a time from the root's directory handle, opening each
   directory relative to the last with no-follow flags (`openat` with `O_NOFOLLOW | O_DIRECTORY`; Python's
   `dir_fd=`), and `lstat` the last component.
   Decide whether a link that stays inside the root may be followed: `os.Root` follows it; refusing every link is
   simpler and stricter.
2. **Resolve links once, in the trusted configuration; never in the agent's paths.** A root may be spelled two ways
   (macOS `/tmp` is a link). goja-cv resolves each root at start-up and matches an absolute path lexically against
   both spellings, so the handle walk sees every link below the root. In construction experiments, three of five
   builds called `realpath` on the agent's absolute path instead, and a save to the absolute path of an in-root link
   wrote through it.
3. **Keep the roots disjoint.** A read root inside the writable root is writable through relative saves
   (`save("mounted/x")`); a writable root inside a read root is readable under two names. goja-cv has no such check.
   Refuse overlapping roots at start-up, or at least refuse saves beneath a nested read root. In probes, three of five
   builds wrote into a nested read root; the two with one of these checks did not.
4. **Create temporary files exclusively, under random names, and rename.** Exclusive creation fails on a planted link
   instead of following it. Rename replaces a name and leaves the
   old inode alone, so a hard link to an input cannot carry the write to it.
5. **Compare identities, not names, and know what the opened set protects.** goja-cv refuses a save that would replace
   an opened file (`os.SameFile`) unless the session wrote it, with that identity taken after the rename. Since writes
   never follow links and always rename, an input's bytes cannot change through a save anyway; the set protects the
   agent's view, so a file it read is not replaced behind its back. Keep the written exemption, so the session can
   re-save its own output, and do not refuse hard-linked files.
6. **Know what the lookup order allows: a save can shadow a read-only file.** Relative names look in the writable root
   first, so a session that saves `labels.json` makes every later read of `labels.json` return its own copy. goja-cv
   cannot save scripts, but data files can be shadowed. Refuse saves whose name exists in a read root, or warn when a
   read is served from the writable root over a read root's name. Check the resulting relative name, however the path
   was spelled: one build exempted absolute saves and let a session replace a read-only helper.
7. **One way to load code, when the runtime can load code.** goja-cv's JavaScript `require` loaded any file on disk
   until an agent used it to load its helper library from outside the roots. The fix refuses every file in `require`
   and keeps `cv.load` as the one way. A library with no module system has no `require` to refuse.
8. **Strict flags for anything that changes privileges.** goja-cv's repeated `--root` silently made a dataset
   writable. A security-relevant flag is given once, or start-up fails with a fix.
9. **Resolve and show names the same way everywhere.** Command-line paths (a prelude, an image) resolve like paths in
   programs. Show a writable-root file by its relative name and a read-root file by its absolute name, so the agent
   can copy either back into a call.
10. **Give each run its own writable root, and order refusals.** The dust runners create a fresh workspace per run,
    with data and helpers mounted read-only and never the answers. goja-cv refuses saving one path twice in one call
    (`E_DUPLICATE`). Report several refusals in a fixed order (shape, access, duplicate, shadow, replacing an opened
    file): the agent sees only the first.
11. **Test that a regression test fails without its fix.** Twice, goja-cv's first test for a hole passed without it
    (a small save beat the race; a path comparison was vacuous). Mutate the fix away (delete the
    link check, drop the exclusive flag) and require the test for that hole to go red. Check each test, not a group:
    one build's mutation script passed on a neighbouring test while its vacuous identity test stayed green.

## Variations

- **Smallest form**: the "always" participants only. It gives up the opened set (a session may overwrite a file it
  read from its own writable root; read roots stay safe), the shadow check and the loader. Enough when the runtime
  cannot load code and relative reads do not fall through to read roots.
- **Capability-passing** (WASI pre-opened directories, Capsicum): the runtime receives directory handles at start and
  has no ambient way to name other paths. The strongest form of the same idea.
- **Process-level isolation** (containers, virtual machines, seccomp, or copy-in, copy-out): contains everything a
  process does, including shells and network; heavier, and still benefits from this pattern for the file API.
- **Read-only session**: no writable root at all; saves refuse. Suits judges and validators that only answer.

## Consequences

- \+ Inputs in read roots cannot be modified by a session, whatever its programs do through the file API.
- \+ Escapes through `..`, links and alternative loaders are closed by the operating system and by one loader. The
  opened-file and duplicate checks are the engine's own; they assume no other process writes into the root.
- \+ Parallel runs cannot interfere with each other's files.
- \+ Refusals with fixes teach agents the boundary.
- − The file API is narrower than the language's; code that expects arbitrary paths must be adapted.
- − Read-only directories must be mounted beside the workspace, not inside it.
- − Root-relative operations are not available everywhere; portability needs care.
- − The boundary covers only the file API the session offers; a shell or network access needs process-level isolation.

## Known uses

- **Go's `os.Root`** (Go 1.24) provides file operations confined to a directory, refusing escapes through `..` and
  symbolic links.
- **Linux `openat2`** with `RESOLVE_BENEATH` resolves paths only beneath a directory file descriptor.
- **WASI** gives WebAssembly modules pre-opened directories as their only filesystem access.
- **FreeBSD Capsicum** restricts a process in capability mode to the descriptors it already holds.
- **Deno** requires explicit `--allow-read` and `--allow-write` permissions for paths.

## Related chapters

- [Chapter 5 · One Eval Tool over a Scripted Session](05-one-eval-tool-over-a-scripted-session.md): the session whose
  file access this contains.
- [Chapter 9 · Sealed Agent Run](09-sealed-agent-run.md): a fresh workspace per run, with read-only mounts.
- [Chapter 6 · Repairable Errors](06-repairable-errors.md): refusals that name the roots and the fix.
- [Chapter 11 · Lineage Ledger](11-lineage-ledger.md): what is saved is stamped with how it was made.
- Classic patterns: **Proxy** (the root handle stands between programs and the filesystem), **Facade** (one narrow
  file API).

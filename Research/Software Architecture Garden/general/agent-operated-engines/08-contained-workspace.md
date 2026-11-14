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
own containment, refuse writes through links or over files the session read, write atomically, and allow one way to
load code. The boundary then holds even when the agent, or a file planted for it, tries to cross it.

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

- A **coding agent** must edit one repository and read reference material, but not touch the user's home directory.
- A **plugin host** gives each plugin a data directory and read access to shared assets.
- A **CI job** gets a writable work tree, read-only caches and no access to other jobs.

## Problem

**When an agent's programs may name any path, a single unexpected path (a link, a repeated flag, a second loading
mechanism) lets them read or overwrite what they should not, and checks on path strings do not stop it.**

## Forces

- **Convenience against containment.** Agents work best with real paths and real files; every restriction is a
  failure mode they must be told about.
- **Name checks against identity checks.** Comparing path strings is easy and wrong under links; comparing file
  identities is right and needs the operating system's help.
- **Many ways in against one.** Each additional way to load or write files (a require function, a module system, a
  shell) is one more boundary to defend.
- **Flexible configuration against strict flags.** Repeatable flags and last-value-wins defaults are convenient and
  turn mistakes into silent privilege changes.
- **Atomic writes against simplicity.** Writing in place is simple; a crash or race then leaves a half-written file or
  a file written through a planted link.

## Solution

**Therefore: give each session one writable root and an explicit list of read-only roots, and resolve every path an
agent writes against them with the operating system's root-relative file operations, which refuse any path, `..` or
link that leaves the root. Relative paths name files in the writable root, then in the read-only roots in order;
absolute paths must lie inside one. Writes go only to the writable root, never through a link, never over a file the
session opened (compared by file identity, not name), and always through an exclusively created temporary file
renamed into place. Allow exactly one way to load code. Make every security-relevant flag strict: given once, or
refused.**

## Applicability

Use it when:

- an agent or its programs read and write files on a machine that also holds data they must not change;
- inputs are valuable (labelled datasets, source of truth) and outputs are scratch;
- several agents run side by side and must not see each other's work.

Do not use it when:

- the agent needs a whole machine (installing packages, running services); use a container or virtual machine, and
  apply this pattern inside it if programs still need narrower access;
- there is no filesystem access at all (all data arrives through the API); the pattern has nothing to contain;
- the operating system offers no root-relative file operations and you cannot add them; string checks alone give a
  false sense of safety, so isolate at the process level instead.

## Structure

| Participant | Responsibility |
| --- | --- |
| **Writable root** | The one directory a session may create and replace files in. |
| **Read roots** | Directories the session may read, in lookup order. |
| **Locator** | Maps a path an agent wrote to a root and a name inside it, or refuses. |
| **Root handle** | An operating-system handle on each root; every open and stat goes through it, so the kernel refuses escapes. |
| **Opened set** | File identities the session read; saves may not replace them. |
| **Writer** | Writes through a randomly named, exclusively created temporary file, then renames into place; refuses links and protected files. |
| **Loader** | The single way to load code into the session, resolving names through the locator. |

## Collaborations

1. The session starts with one writable root and its read roots. A second writable root is a start-up error with a
   fix that names the read flag.
2. The agent opens `tile.tif`. The locator looks in the writable root, then each read root; the root handle opens the
   file, and its identity joins the opened set.
3. The agent saves `out/labels.json`. The locator maps it into the writable root; the writer checks that the target
   is not a link, not a directory and not in the opened set, writes a temporary file with a random name created
   exclusively, and renames it over the target.
4. The agent calls `require("/elsewhere/lib.js")`. The loader refuses: the only way to load code is
   `load(name)`, which resolves through the locator like any read.
5. Every refusal names the roots and the fix ("relative paths are names inside the workspace; add `--read DIR` to
   read from DIR").

## Sketch

```text
value Location: root: Root, rel: path inside the root

open(path) → (File, Location) | Refusal
  loc = locate(path, forWrite: false)                 -- relative: writable root, then read roots; absolute: inside one
  f = loc.root.handle.open(loc.rel)                    -- the kernel refuses .., links and escapes
  opened = opened ++ [identity(f)]
  return f, loc

save(path, bytes) → ok | Refusal
  loc = locate(path, forWrite: true)                   -- only the writable root
  st = loc.root.handle.lstat(loc.rel)                   -- do not follow a link
  if st exists:
    if st is link:                 return refuse(E_ACCESS, "saves do not follow links", fix: "save under another name")
    if st is directory:            return refuse(E_ARG, "a directory", fix: loc.rel ++ "/x.json")
    if identity(st) in opened and identity(st) not in written:
                                   return refuse(E_ACCESS, "would replace a file this session opened")
  loc.root.handle.makeParents(loc.rel)                 -- parents are created inside the root, never outside
  tmp = loc.root.handle.createExclusive(randomName())  -- fails if anything already exists there
  write(tmp, bytes); rename(tmp, loc.rel)              -- atomic; rename replaces a name, it never follows a link
  written = written ++ [identity(loc.root.handle.lstat(loc.rel))]   -- the file's identity, taken after the rename

load(name) → Script | Refusal                          -- the one way to load code
  (f, loc) = open(name)
  return compile(read(f), origin: loc)

require(path) → refuse(E_ACCESS, "files cannot be required", fix: "await load(name)")

startup(flags) → Session | Error
  if count(flags.root) ≠ 1: return error("--root takes one directory; add read-only directories with --read DIR")
```

## Implementation notes

1. **Let the operating system enforce the root.** goja-cv's first workspace checked path strings and was escaped by a
   dangling symlink. Its second opens every root as an `os.Root` (Go's root-relative file access, built on `openat`
   style calls), so the kernel refuses `..`, absolute links and links that leave the root. On Linux, `openat2` with
   `RESOLVE_BENEATH` does the same. Where neither exists (Python's standard library, for one), walk the path one
   component at a time from the root's directory handle, opening each directory relative to the last with
   no-follow flags (`openat` with `O_NOFOLLOW | O_DIRECTORY`; Python's `dir_fd=`), and `lstat` the last component.
   Decide whether a link that stays inside the root may be followed: `os.Root` follows it; refusing every link is
   simpler and stricter, and every builder who implemented this chapter chose that.
2. **Compare identities, not names.** A link inside the root can point at an input the session opened. goja-cv records
   the identity of every opened file and refuses a save that would replace one, compared with `os.SameFile`, unless
   the session wrote that file itself earlier.
3. **Create temporary files exclusively, under random names.** A predictable temporary name can be planted as a link
   before the save; exclusive creation fails instead of following it.
4. **One way to load code.** The `require` function of goja-cv's runtime loaded any file on disk until an agent used
   it to load its helper library from outside the roots. The fix was to refuse every file in `require` and keep
   `load` as the single, contained way.
5. **Strict flags for anything that changes privileges.** A repeated `--root` used to keep the last value, so an old
   configuration with two roots made the dataset directory writable without any error. A security-relevant flag is
   given once, or start-up fails with a fix.
6. **Know what the lookup order allows: a save can shadow a read-only file.** Relative names look in the writable root
   first, so a session that saves `labels.json` makes every later read of `labels.json` return its own copy instead of
   the read-only one. goja-cv cannot save scripts, so a library cannot be shadowed this way, but data files can.
   Either refuse saves whose name exists in a read root, or warn when a read is served from the writable root while
   a read root has the same name; and load trusted libraries by absolute path at start-up.
7. **Resolve relative names the same way everywhere.** Paths given on the command line (a prelude, an image) resolve
   like paths in programs: the writable root first, then the read roots. A later fix had to make a symlinked read root
   inside the workspace resolve to its target, or the workspace's own containment refused it.
8. **Show names as the agent should write them.** A file in the writable root is shown by its relative name; a file in
   a read root by its absolute name, so the agent can copy either back into a call.
9. **Give each parallel run its own writable root.** The dust runners create a fresh workspace per run and mount data
   and helpers read-only; the subagents handbook adds the rule never to mount the answers (the controls' truth).
10. **Refuse saving one path twice in one call.** Two saves to the same name in one program are almost always a mistake;
   goja-cv refuses the second (`E_DUPLICATE`). When several refusals apply to one save, report them in a fixed,
   documented order (shape of the argument, access, duplicate, shadow, replacing an opened file): the agent sees only
   the first, and it decides what the agent tries next.
11. **Test that a regression test fails without its fix.** Twice, goja-cv's first test for a hole passed without the fix
    (a small save finished before the race could happen; a comparison of paths was vacuous). Security tests must be
    shown to fail first.

## Variations

- **Process-level isolation** (containers, virtual machines, seccomp): contains everything a process does, including
  shells and network; heavier, and still benefits from this pattern for the program's own file API.
- **Capability-passing** (WASI pre-opened directories, Capsicum): the runtime receives directory handles at start and
  has no ambient way to name other paths. The strongest form of the same idea.
- **Copy-in, copy-out**: inputs are copied into a scratch directory and outputs collected afterwards; nothing else is
  visible. Simple and safe; costs copies of large inputs.
- **Read-only session**: no writable root at all; saves refuse. Suits judges and validators that only answer.

## Consequences

- \+ Inputs cannot be modified by a session, whatever its programs do through the file API.
- \+ Escapes through `..`, links and alternative loaders are closed by the operating system and by having one loader.
  The opened-file and duplicate checks are the engine's own; they assume no other process writes into the same root
  at the same time.
- \+ Parallel runs cannot interfere with each other's files.
- \+ Refusals with fixes teach agents the boundary instead of leaving them to probe it.
- − The file API is narrower than the language's; code that expects arbitrary paths must be adapted.
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

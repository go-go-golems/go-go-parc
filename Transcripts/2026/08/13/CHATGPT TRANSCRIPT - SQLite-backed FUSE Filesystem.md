# SQLite-backed FUSE Filesystem

- URL: https://chatgpt.com/c/6a7e1afd-fa08-83ea-8a26-46d3024542b2
- Created: 2026-08-13T19:30:35.835Z

---

> Design a system / sandbox or ld preload or whatever where I can basically replace the filesystem with a SQLite database and catch writes and other file manipulations done by bash calls, the idea is to have llm agents be able to write / read to a SQLite db, but since so often bash tool calls are also used to manipulate files, we need to catch that at the os level. This gives us the possibility to do things like an audit log, rewind time without watching the fs and snapshotting it, etc…
>
> What technologies and base design patterns are useful for this, maybe existing technologies too

<details><summary>💭 Thinking</summary>

**Architecting SQLite-backed sandboxes**

I’m comparing FUSE, syscall interception, and virtual-machine approaches. FUSE best captures ordinary filesystem operations; preload alone is incomplete. I’ll verify existing projects and outline a practical architecture, caveats, and recommended starting point.

**Architected SQLite-backed sandboxes**

</details>

The strongest architectural split is: make the **agent-visible workspace a real mounted filesystem interface**, but make its **authoritative state transactional and versioned in SQLite**. Then sandbox the agent so it cannot write anywhere except that mount. I’ll compare FUSE, syscall interception, `LD_PRELOAD`, and VM/container-style approaches, plus the data model needed for rewind/audit.

```json
{"system1_search_query":[{"q":"site:sqlite.org vfs sqlite documentation virtual file system"},{"q":"site:kernel.org FUSE filesystem documentation userspace filesystem"},{"q":"site:man7.org seccomp user notification seccomp_unotify documentation"},{"q":"site:docs.kernel.org overlayfs documentation filesystem"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 13 websites**

</details>

There is already a project extremely close to your proposal: **Turso AgentFS**. Its stated model is a POSIX-like filesystem plus tool-call audit state in one SQLite-compatible database, with copy-on-write/time-travel goals; another project, `desplega-ai/agent-fs`, explicitly exposes SQLite-backed state through FUSE so `cat`, `mv`, `rm`, etc. work normally. 

That validates the basic direction. The main design decision is whether you need merely *observable filesystem behavior* or a *hard containment boundary*.

```json
{"click":[{"ref_id":"turn534752view0","id":86},{"ref_id":"turn534752view0","id":84}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 1 website**

**Refining the architecture**

I’m separating SQLite’s storage interface from a filesystem mount: they solve different problems. A FUSE-backed filesystem, combined with a mount namespace and read-only base image, can capture writes while preserving ordinary shell and program behavior.

**Refined the architecture**

</details>

```json
{"open":[{"ref_id":"turn331325search28"}],"response_length":"medium"}
```

<details><summary>💭 Thinking</summary>

**Searched 1 website**

</details>

Yes. On Linux, I would build this as **a SQLite-backed FUSE filesystem inside a mount-namespace sandbox**, not as `LD_PRELOAD`.

Conceptually:

```text
             agent / bash / python / gcc / sed / rm / mv
                              │
                         normal syscalls
                              │
                       Linux kernel VFS
                              │
                    ┌─────────▼──────────┐
                    │    FUSE mount      │
                    │    /workspace      │
                    └─────────┬──────────┘
                              │
                    ┌─────────▼──────────┐
                    │   agentfs daemon   │
                    │                    │
                    │ inode semantics    │
                    │ path resolution    │
                    │ audit/provenance   │
                    │ snapshot/versioning│
                    └─────────┬──────────┘
                              │
                    ┌─────────▼──────────┐
                    │      SQLite        │
                    │                    │
                    │ inodes             │
                    │ dentries           │
                    │ content chunks     │
                    │ versions           │
                    │ operations         │
                    │ snapshots          │
                    └────────────────────┘

        agent process lives in separate mount/PID/etc namespace
        SQLite DB + filesystem daemon live OUTSIDE that namespace
```

The interesting thing is that **you've essentially independently arrived at Turso's AgentFS architecture**. Current AgentFS has a SQLite filesystem specification, FUSE mounts on Linux, overlay/COW support, a tool-call audit trail, and an experimental sandbox for running commands. Their examples explicitly show normal shell redirection through the filesystem, e.g. `echo ... > ./mnt/hello.txt`. citeturn467169view0turn379445view0

## Why FUSE is the right interception layer

FUSE inserts your userspace daemon underneath the Linux filesystem API. The kernel VFS handles `open`, `stat`, `read`, `write`, `chmod`, etc., and routes requests for your mounted filesystem to the FUSE implementation. citeturn534752view2turn534752view5

That means all of these naturally hit your code:

```bash
echo hello > foo
cat foo
printf x >> foo
touch foo
truncate -s 2 foo
mv foo bar
rm bar
mkdir x
ln a b
ln -s a b
chmod 600 foo

python -c 'open("x","w").write("hi")'
sed -i s/a/b/ file
git checkout ...
tar xf archive.tar
gcc ...
```

You do not care whether the operation originated in Bash itself, coreutils, Python, Rust, Node, or a program doing raw filesystem syscalls. That's the big advantage over userspace hooking.

The low-level libfuse API is particularly appropriate because it exposes operations in inode-oriented form rather than forcing you to pretend paths are the fundamental object. citeturn534752view7

### Why not `LD_PRELOAD`

`LD_PRELOAD` is useful for a prototype, tracing, or adding behavior to cooperative programs. I would not make it the integrity boundary.

It depends on the dynamic linker and ELF symbol interposition. Static executables don't work that way, direct syscalls can bypass your libc wrappers, and the dynamic linker restricts `LD_PRELOAD` in secure-execution situations. citeturn629629search0turn629629search4

So:

```text
LD_PRELOAD
    good:  500-line prototype
    bad:   authoritative sandbox

FUSE
    good:  actual filesystem implementation
    good:  arbitrary Bash subprocesses
    good:  proper fd/inode semantics
```

## The second half: a mount namespace

FUSE alone says:

> “Everything underneath `/myfs` goes into SQLite.”

It does **not** say:

> “The agent cannot instead write to `/tmp/foo`, `~/.cache/foo`, `/var/tmp/foo`, or `/some/host/path`.”

So combine it with namespaces.

Bubblewrap is a very good primitive here because it creates a mount namespace and lets you precisely control which filesystem trees the sandbox sees, including read-only mounts. citeturn534752view3

For example, conceptually:

```text
/
├── usr/          read only from host/rootfs
├── bin/          read only
├── lib/          read only
├── etc/          read only/minimal
├── proc/         sandbox procfs
├── dev/          minimal
├── tmp/          SQLite FS or ephemeral tmpfs
├── home/agent/   SQLite FS
└── workspace/    SQLite FS
```

Then set:

```text
cwd=/workspace
HOME=/home/agent
TMPDIR=/tmp
```

and make **everything else either inaccessible or read-only**.

That is what makes your claim strong:

> Any persistent filesystem mutation the agent successfully performs must pass through the SQLite-backed filesystem.

Your SQLite database file itself should be somewhere the sandbox cannot see. The FUSE daemon should also ideally live outside the agent's PID/mount namespace.

---

# I would actually use an overlay model

For coding agents, you probably don't want `/usr/bin/bash`, shared libraries, Python, compilers, the repository baseline, etc. copied into SQLite.

Instead:

```text
                 visible filesystem
                       │
                 SQLite-FUSE
                  overlay layer
                 /           \
                /             \
       SQLite writable       base root/repo
          upper               read-only
```

Reads:

```text
lookup("src/foo.c")

SQLite upper?
    yes → return it

whiteout exists?
    yes → ENOENT

otherwise:
    read lower filesystem
```

Writes:

```text
write("src/foo.c")
    ↓
copy-up lower file if necessary
    ↓
write SQLite version
```

Deletes create a **whiteout** rather than deleting the lower-layer file.

This is exactly the same family of pattern used by overlay filesystems. Linux OverlayFS itself combines lower and upper filesystems, and AgentFS's current spec has explicit SQLite whiteout/origin tables for its overlay model. citeturn331325search4turn379445view0

This is probably the sweet spot for an agent sandbox:

```text
immutable environment + immutable repository baseline
                     +
              SQLite delta
```

A fork becomes almost trivial:

```text
base_snapshot = snapshot 123

agent A delta → SQLite A
agent B delta → SQLite B
agent C delta → SQLite C
```

No directory copying.

---

# SQLite data model

Do **not** make the schema primarily path-based like:

```sql
files(path TEXT PRIMARY KEY, contents BLOB)
```

Paths aren't objects in Unix. Inodes are.

You want roughly:

```text
inode
-----
ino
kind
mode
uid
gid
size
nlink
mtime
ctime
...

dentry
------
parent_inode
name
inode

file_chunk
----------
inode/version
chunk_no
blob/hash

symlink
-------
inode
target
```

This gives you correct semantics for:

```bash
ln foo bar
mv foo baz
rm baz
```

because a rename is really a namespace operation, not a “move the contents to another path” operation.

AgentFS's published SQLite schema uses exactly this Unix-like separation: inode metadata, directory entries, fixed-sized file chunks, and symlink information. citeturn379445view0

## I'd go one step further and make contents immutable

Instead of:

```text
file_chunks
    inode
    offset
    blob
```

I'd use content-addressed chunks:

```text
chunks
------
hash PK
data

file_version_chunks
-------------------
file_version
chunk_index
chunk_hash
```

Then:

```text
"hello world"
      │
      ├── chunk A
      ├── chunk B
      └── chunk C

version 42 → A,B,C

modify middle 4 KB

version 43 → A,D,C
```

Now snapshots and forks are cheap and deduplicate naturally.

For agent workloads I might start with 4–64 KiB chunks rather than whole-file BLOBs. AgentFS currently specifies fixed-sized chunks and defaults its schema to 4096 bytes. citeturn379445view0

---

# Time travel: don't make WAL your only history mechanism

SQLite WAL is useful because readers can see stable snapshots while writes continue; SQLite describes WAL mode as providing snapshot isolation. citeturn378736search2

SQLite even has historical WAL snapshot APIs. citeturn378736search4

But for your application I would treat WAL as **database machinery**, not your permanent version-control system.

Instead introduce an application-level generation:

```text
generation
----------
1
2
3
4
5
```

And versions:

```text
inode_version
-------------
inode
generation_from
generation_to
metadata...

dentry_version
--------------
parent
name
inode
generation_from
generation_to

file_version
------------
inode
generation
...
```

A snapshot can literally just be:

```text
snapshot {
    id: 932,
    generation: 189234,
    agent_id: "...",
    tool_call_id: "...",
    created_at: ...
}
```

Then:

```text
mount snapshot 932 read-only
```

or:

```text
fork snapshot 932 → new writable branch
```

becomes cheap.

---

# Another very useful SQLite feature: Session/Changesets

SQLite has a lesser-known **Session Extension** that can capture changes to tables as changesets. Those changesets can be inspected, reapplied, combined, and even inverted to undo changes. citeturn378736search0

That is extremely interesting for your design.

At the boundary of:

```text
LLM tool call #837
    bash("sed -i ... && mkdir ... && ...")
```

you could produce:

```text
tool_call
    id = 837

filesystem operations
    op 1
    op 2
    op 3

SQLite changeset
    Δ837

snapshot
    before = 1004
    after  = 1005
```

So you get both:

```text
semantic log:
    rename /a → /b

database delta:
    exact SQL state transition

snapshot:
    filesystem after command
```

I'd still keep your own filesystem operation log, because SQLite changesets describe row changes rather than Linux-level intent.

---

# Audit should exist above the storage tables

Have an append-only table something like:

```text
fs_operations
-------------
id
generation
timestamp
agent_id
session_id
tool_call_id

pid
ppid
executable

operation
inode
path
path2

offset
length

old_hash
new_hash

result
errno
```

Example:

```text
10293  tool=847  pid=4321  open     /src/a.py O_RDWR
10294  tool=847  pid=4321  write    inode=812 offset=532 len=19
10295  tool=847  pid=4321  fsync    inode=812
10296  tool=847  pid=4321  rename   /src/.a.py.tmp → /src/a.py
```

FUSE request context can provide process identity information including the request PID. citeturn123693search17

I would combine that with your tool runner.

When you invoke:

```text
bash tool call #847
```

put its process tree into its own cgroup or maintain a supervisor mapping:

```text
PID tree / cgroup → tool_call_id
```

Then the filesystem daemon can attribute changes to:

```text
conversation
agent
turn
tool call
process
filesystem operation
```

That's considerably more useful than an ordinary filesystem journal.

---

# Important distinction: tool-call snapshots vs syscall transactions

I would **not** keep a single SQLite write transaction open for the entire Bash tool call.

Suppose:

```bash
(
    producer > x &
    consumer x &
    wait
)
```

or a build system launches 64 processes.

You want normal visibility between those processes.

So do:

```text
FUSE mutation
  → short SQLite transaction
  → commit
  → generation N

FUSE mutation
  → short SQLite transaction
  → commit
  → generation N+1
```

but tag all of them:

```text
tool_call_id = 837
```

At the tool boundary:

```text
before_snapshot = N
run command
after_snapshot  = M
```

Now rollback-tool-call means logically:

```text
head = snapshot N
```

rather than trying to maintain a huge transaction during execution.

---

# POSIX edge cases are where most of the work is

The FUSE plumbing is not the hard part. Correct filesystem semantics are.

I'd explicitly design for these early:

```text
open("foo")
unlink("foo")
read(existing_fd)       # must continue to work

hard links
rename over existing file
rename across directories
renameat2 flags

O_APPEND
O_TRUNC
O_EXCL

sparse writes
truncate

chmod/chown
timestamps

symlinks
relative symlinks

directory iteration cookies

flock()
fcntl() locking

xattrs

fsync/fdatasync

mmap()

concurrent writers

crash between operations
```

The classic trap is open-then-unlink:

```c
fd = open("x")
unlink("x")

// x is gone from namespace,
// but this MUST still work:
write(fd, ...)
```

So deleting the last dentry cannot necessarily immediately delete the inode/content. You need to know whether open handles still exist.

---

# Be careful about FUSE caching if audit fidelity matters

FUSE supports direct I/O, normal cached write-through, and writeback caching. In writeback-cache mode, a `write(2)` can complete by writing into the kernel cache, and dirty pages may only reach your userspace daemon later. citeturn312664view0

For your use case I would initially use **cached + write-through**, not writeback caching.

That gives you a much cleaner relation:

```text
process write
      ↓
FUSE WRITE
      ↓
SQLite transaction
```

while retaining the page cache for reads.

If you absolutely need very tight causality, `direct_io` is even simpler conceptually, but it disables page-cache benefits and shared `mmap`, so I wouldn't begin there. citeturn312664view0

---

# Where syscall interception fits

There is another possible design:

```text
agent
  ↓
seccomp / ptrace
  ↓
filesystem syscall emulator
  ↓
SQLite
```

For example Linux seccomp user notifications can stop a syscall and delegate handling to a userspace supervisor. citeturn534752view4

I would **not** use this as the primary filesystem implementation.

You quickly discover that you are implementing half the Linux VFS yourself:

```text
openat()
openat2()
read()
write()
pwrite()
mmap()
renameat2()
linkat()
unlinkat()
fchmodat()
statx()
getdents64()
...
```

And resolving:

```text
fd 17 + "../../../foo"
```

safely and according to Linux semantics is surprisingly nasty.

Seccomp notifications are better for:

```text
"deny this syscall"
"broker this special operation"
"observe or mediate exec/network/etc."
```

than for reimplementing an entire FS. The documentation also explicitly notes that seccomp user notification is not intended by itself as a mechanism for implementing security policy. citeturn534752view4

AgentFS actually has an experimental ptrace syscall-interception sandbox as well as its FUSE approach, which is interesting reference material if you want to explore this branch. citeturn467169view1

---

# If you want much stronger isolation: gVisor

For hostile/untrusted agents, another architecture is:

```text
                       agent
                         │
                   Linux syscalls
                         │
                 gVisor Sentry
                 userspace kernel
                         │
               your filesystem backend
                         │
                      SQLite
```

gVisor actually intercepts application syscalls and implements a userspace Linux kernel, including filesystem semantics. citeturn534752view6

That's a significantly larger integration effort, but it gives you a much harder sandbox boundary.

So I'd roughly rank:

```text
normal coding agents:
    bwrap/userns + FUSE + SQLite

less-trusted arbitrary programs:
    OCI container + FUSE + SQLite

hostile multi-tenant workloads:
    gVisor/VM + exported SQLite FS
```

FUSE can still be useful in all three.

---

# One terminology trap: SQLite VFS

SQLite itself has something called a **VFS**.

It's not what you're looking for.

SQLite's VFS is:

```text
SQLite
   ↓
custom storage abstraction
   ↓
OS/files/network/etc
```

It answers:

> “Where does SQLite put its database pages?”

rather than:

> “How do Linux programs see SQLite as a filesystem?”

SQLite documents its VFS as the OS interface underneath the SQLite core. citeturn331325search0

Your direction is the inverse:

```text
Linux VFS
   ↓
FUSE
   ↓
SQLite
```

---

# Existing projects I'd study

The most relevant one by far is **Turso AgentFS**. As of now it has a published SQLite inode/dentry/chunk schema, FUSE on Linux, NFS on macOS, overlay mode, tool-call audit records, and sandbox execution. Their current documentation even describes Linux as using “FUSE + overlay filesystem with user namespaces.” citeturn467169view0turn467169view1

Also useful:

- **desplega-ai/agent-fs** independently has SQLite-backed versioned storage and a Linux FUSE mount explicitly intended so agents can use normal `cat`, `grep`, `mv`, and `rm`. citeturn534752view1
- **LiteFS** is not the same application, but it is a useful production example of putting FUSE in front of SQLite-related storage behavior. citeturn123693search32
- **libfuse** is the reference userspace library; its low-level API is what I'd study if implementing the filesystem core directly. citeturn534752view7
- For Rust, `fuser` is an actively released Rust implementation of the FUSE userspace interface; version 0.18.0 was released July 22, 2026. citeturn801894search0
- **bubblewrap** is a good low-level namespace/layout primitive around the mount. citeturn534752view3

## The architecture I'd build

If I were starting this project now:

```text
                       host
┌───────────────────────────────────────────────────┐
│                                                   │
│ agentfsd                                          │
│ ├─ FUSE low-level server                         │
│ ├─ read-only lower filesystem adapter             │
│ ├─ SQLite COW upper                              │
│ ├─ inode/handle manager                          │
│ ├─ provenance logger                             │
│ └─ snapshot/branch manager                       │
│             │                                     │
│             └────── agent-123.sqlite              │
│                                                   │
│             mount namespace                       │
│    ┌──────────────────────────────────────┐       │
│    │ /usr        → host rootfs [RO]       │       │
│    │ /etc        → curated [RO]           │       │
│    │ /workspace  → agentfs FUSE           │       │
│    │ /home/agent → agentfs FUSE           │       │
│    │ /tmp        → agentfs or tmpfs       │       │
│    │                                      │       │
│    │ bash / coding-agent / subprocesses   │       │
│    └──────────────────────────────────────┘       │
│                                                   │
└───────────────────────────────────────────────────┘
```

And I'd give the storage engine these first-class concepts:

```text
Agent
Session
ToolCall
FilesystemOperation
Inode
FileVersion
Chunk
Generation
Snapshot
Branch
```

Then your API becomes unusually powerful:

```text
snapshot before bash call
run bash
show me all mutations
diff snapshots
query which process created a file
query which LLM tool call modified line-producing content
rewind
fork from before the mistake
run two agents from the same snapshot
merge selected files
export current tree as tar/git checkout
```

The key pattern is **not really “filesystem stored in SQLite.”** It's:

> **A transactional, versioned, queryable virtual filesystem where POSIX is merely one frontend.**

FUSE is the compatibility frontend for Bash. An MCP/API interface can talk directly to the same storage engine. That way agents that know about the database can get rich operations such as snapshots and provenance, while arbitrary shell programs remain completely unaware that the filesystem is virtual.


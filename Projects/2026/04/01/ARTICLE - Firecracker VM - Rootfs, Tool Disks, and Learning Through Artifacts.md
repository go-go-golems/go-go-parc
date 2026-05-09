---
title: Firecracker VM - Rootfs, Tool Disks, and Learning Through Artifacts
aliases:
  - Firecracker Rootfs Work
  - Rootfs, Tool Disks, and Learning Through Artifacts
tags:
  - article
  - firecracker
  - virtualization
  - go
  - rootfs
  - ext4
  - systems
status: active
type: article
created: 2026-04-01
repo: /home/manuel/code/wesen/2026-03-31--firecracker-vm
---

# Rootfs, Tool Disks, and Learning Through Artifacts

The most useful change in this Firecracker project was not a clever optimization or a new subsystem. It was a clarification. The system stopped treating the guest filesystem as one vague blob and started treating it as a set of explicit artifacts with different meanings, different lifetimes, and different trust boundaries.

That shift matters because the project is not simply trying to boot a VM. It is trying to create an execution environment that is comfortable enough for an LLM-driven coding agent to do real work, but disciplined enough that the host never quietly leaks into the guest. The rootfs work turned that goal from a loose intention into a concrete filesystem model.

## The original problem

In the early state of the repository, the runtime already had the correct broad outline:

- a Go host orchestrator
- a Firecracker microVM
- a guest bootstrap daemon
- a mock agent
- one per-job workspace ext4 image
- host-mediated secrets delivered over vsock

That version was already valuable. It proved that the host could stage files, boot a guest, mount `/work`, run an agent, and retain a result artifact. But it still left a design pressure unresolved: as the guest became richer, where should all the additional power live?

If the answer had been "just put more stuff in the rootfs," the rootfs would have become a bag of unrelated concerns:

- baseline operating system
- bootstrap runtime
- development tools
- browser automation bits
- shared corpora
- temporary learning artifacts

And if the answer had been "just mount more host directories," the system would have drifted toward the exact failure mode the project is trying to avoid: blurred host and guest boundaries.

The rootfs work was therefore really about answering a simpler question correctly:

**What kinds of files should exist in the guest, and how should they get there?**

## The new filesystem contract

The answer that emerged is small enough to remember and strong enough to design around.

The guest now has four conceptual filesystem roles:

- `rootfs`
- `tool disk`
- `workspace`
- `/run/secrets`

That is not merely a naming scheme. Each role has a different operational meaning.

### `rootfs`

The rootfs is for the baseline guest operating system and the minimum runtime needed to accept and execute a job:

- bootable guest OS
- `bootstrapd`
- default agent entrypoint
- baseline packages

The important thing about the rootfs is not only what it contains, but what it does **not** contain. It is not the retained artifact. It is not the place where host secrets should be written. It is not where every optional tool should accumulate forever.

### `tool disk`

The tool disk is the first explicit answer to the question "how do we make the guest more comfortable without loosening the host boundary?"

It is a read-only ext4 image, mounted at `/opt/tools`, meant for things that are:

- non-secret
- broadly useful
- mostly static
- large enough that copying them into every workspace would be wasteful

That includes things like:

- helper binaries
- SDKs
- corpora
- browser dependencies
- shared reference material

The read-only property matters. The tool disk is part of the environment, not part of the job’s mutable state.

### `workspace`

The workspace remains the per-job mutable filesystem. It is the place where the agent explores, edits, and leaves a retained output artifact.

It is the right place for:

- staged repo content
- generated files
- logs safe to keep
- `AGENT_NOTE.md`
- `.agent-result.json`

The workspace is intentionally a durable artifact. That is why it must stay cleanly separated from secrets.

### `/run/secrets`

Secrets are not block devices in this design. They are runtime-only guest-local files that are materialized after the bootstrap request arrives. They are ephemeral by design and should never be mistaken for a retained output channel.

That design keeps the secret story coherent:

- Vault stays on the host
- the host resolves secret files
- the guest receives them over vsock
- the guest writes them under `/run/secrets`
- they do not belong in the workspace image

## Why this is better than "just a rootfs"

This project has been quietly teaching the same lesson over and over: isolation becomes stronger when the system has fewer ambiguous surfaces.

When everything goes into one rootfs, meaning collapses:

- immutable and mutable content get mixed
- platform data and job data get mixed
- shared tooling and per-run state get mixed

When the filesystem roles are explicit, the architecture becomes much easier to reason about:

- rootfs is baseline runtime
- tool disk is read-only shared capability
- workspace is retained mutable output
- secrets are ephemeral runtime state

That separation is not just conceptually nice. It changes the implementation in concrete ways.

## What changed in the codebase

The rootfs work became real in several layers of the repository.

### 1. The job spec learned explicit mounts

The spec surface in [`internal/job/spec.go`](/home/manuel/code/wesen/2026-03-31--firecracker-vm/internal/job/spec.go) now supports a real `mounts` model. That means the runtime can describe multiple guest-visible filesystems instead of assuming one extra drive always means one workspace.

The important detail is that this happened in a backward-compatible way. The legacy `workspace` block still works, but it is normalized into the newer `mounts` shape. That is a good example of preserving a proven path while improving the model behind it.

Pseudocode for the normalized shape:

```json
{
  "mounts": [
    {
      "name": "tools",
      "kind": "tool-disk",
      "mount_dir": "/opt/tools",
      "label": "TOOLS",
      "read_only": true,
      "image": "./artifacts/tools/demo-tools.ext4"
    },
    {
      "name": "workspace",
      "kind": "workspace",
      "mount_dir": "/work",
      "label": "JOBFS",
      "read_only": false
    }
  ]
}
```

### 2. The bootstrap protocol learned multiple mounts

Once the job spec had explicit mount metadata, the guest bootstrap protocol in [`internal/protocol/protocol.go`](/home/manuel/code/wesen/2026-03-31--firecracker-vm/internal/protocol/protocol.go) could carry it. That allowed the host and guest to agree on mount identity declaratively instead of via device-name guesses.

This is one of the quieter but more important design improvements in the project:

- the host says what mounts exist
- the guest mounts them by label and declared path
- the runtime no longer depends on ad hoc assumptions like "the workspace is probably `/dev/vdb`"

### 3. The guest learned to mount and finalize filesystems properly

The guest bootstrap daemon in [`cmd/bootstrapd/main.go`](/home/manuel/code/wesen/2026-03-31--firecracker-vm/cmd/bootstrapd/main.go) now mounts declared filesystems such as:

- `/work`
- `/opt/tools`

and it also now does something just as important after the agent exits:

- syncs guest filesystems
- unmounts retained mount points
- emits `guest filesystems finalized`

That finalization step matters because retained artifacts should not merely be recoverable. They should be clean.

### 4. The host verifier became stricter

The artifact verifier in [`scripts/verify-workspace-artifact.sh`](/home/manuel/code/wesen/2026-03-31--firecracker-vm/scripts/verify-workspace-artifact.sh) used to repair a copied image before reading it. That was useful during bring-up, but it also hid whether the guest had actually left the filesystem in a clean state.

The verifier now does a read-only `e2fsck -fn` preflight and fails if the retained image still looks dirty. That turns cleanliness into a tested invariant instead of a best-effort hope.

This is the kind of change I like in systems work: small, almost boring, and deeply clarifying.

## The tool disk as a teaching device

One reason the rootfs work feels satisfying is that the tool disk is not just an implementation feature. It is also a teaching device for the architecture.

The repository now includes:

- a tool-disk builder at [`scripts/build-tool-disk.sh`](/home/manuel/code/wesen/2026-03-31--firecracker-vm/scripts/build-tool-disk.sh)
- demo tool-disk contents under [`demo-assets/tool-disk/`](/home/manuel/code/wesen/2026-03-31--firecracker-vm/demo-assets/tool-disk/)
- multi-disk smoke coverage at [`scripts/run-multi-disk-smoke-test.sh`](/home/manuel/code/wesen/2026-03-31--firecracker-vm/scripts/run-multi-disk-smoke-test.sh)

That means a new developer can watch the full idea become concrete:

1. build a read-only ext4 image from host content
2. attach it beside the workspace image
3. mount it in the guest at `/opt/tools`
4. prove it is usable
5. prove it is not writable

That is much better than merely describing the architecture in prose.

## The system as a set of artifacts

One of the most useful ways to think about the project now is as a chain of artifacts, not a pile of processes.

```mermaid
flowchart LR
    A[Host source files] --> B[workspace staging tree]
    B --> C[workspace.ext4]
    D[tool source tree] --> E[tools.ext4]
    F[rootfs build inputs] --> G[rootfs.ext4]
    H[host Vault reads] --> I[/run/secrets payload]

    C --> J[Firecracker guest]
    E --> J
    G --> J
    I --> J

    J --> K[retained workspace artifact]
```

That diagram captures the core lesson of the rootfs work:

- stable platform content becomes images
- mutable job content becomes a separate image
- secrets become a runtime payload

The guest never needs the host filesystem itself.

## What this unlocks next

The rootfs work is not the end of the project. It is the part that makes the next steps legible.

Because the filesystem roles are now explicit, later work can attach to something stable:

- guest SELinux can reason about `/opt/tools`, `/work`, and `/run/secrets` as different classes
- host SELinux can reason about rootfs images, tool disks, and workspace artifacts as different host-side object types
- a future host capability broker can be defined as "the thing you use instead of mounting privileged host state"
- an interactive playground can teach the system by letting people manipulate these artifacts and immediately see what changes

That last point matters more than it may seem. A lot of systems design becomes understandable only after the shapes harden enough to be seen, inspected, and compared.

The rootfs work did exactly that. It gave the project visible structure.

## The commands that now define the system

There is something satisfying about how small the surface now feels.

The key entrypoints are:

```bash
make smoke-no-vault
make smoke-host-vault
make smoke-multi-disk
VAULT_ADDR=http://127.0.0.1:8200 VAULT_TOKEN=root make smoke-multi-disk-host-vault
```

And the explicit multi-disk examples are now real checked-in references:

- [job-spec.multi-disk.no-vault.json](/home/manuel/code/wesen/2026-03-31--firecracker-vm/examples/job-spec.multi-disk.no-vault.json)
- [job-spec.multi-disk.host-vault.json](/home/manuel/code/wesen/2026-03-31--firecracker-vm/examples/job-spec.multi-disk.host-vault.json)

Those examples matter because they show that the idea is no longer hypothetical.

## The larger lesson

The most interesting outcome of this work is not "the project has a tool disk now." It is that the system is becoming learnable through its artifacts.

The rootfs is no longer a vague environment.
The workspace is no longer just "some extra drive."
The tool disk is no longer just an idea in a ticket.
The retained artifact is no longer "probably fine."

Each piece now has a role, a lifecycle, and a reason to exist.

That is the kind of structure a project needs before it can be:

- hardened seriously
- taught clearly
- explored interactively
- trusted incrementally

The next work, especially around the interactive playground, should build on exactly this quality: the system has become explicit enough that people can now learn it by manipulating real parts instead of reading abstractions.

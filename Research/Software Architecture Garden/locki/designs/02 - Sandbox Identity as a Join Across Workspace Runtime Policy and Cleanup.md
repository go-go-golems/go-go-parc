---
title: Sandbox Identity as a Join Across Workspace Runtime Policy and Cleanup
aliases:
  - Locki sandbox join identity
  - Worktree namespace ownership
  - wt_id as cross-resource coordinate
status: emergent
maturity: Emergent
open_obligations:
  - collision detection is implicit
  - filename suffix parsing substitutes for validated identity
type: architecture-garden-design
created: 2026-08-19
analyzed: 2026-08-19
repository: /home/manuel/code/others/llms/locki
repository_remote: ssh://git@github.com/janpokorny/locki.git
source_commit: 0546b381005048418d9ff2622a47a3a67c982dc0
source_branch: main
tags:
  - architecture-garden
  - locki
  - identity
  - git-worktrees
  - ownership
  - lifecycle
related_files:
  - /home/manuel/code/others/llms/locki/src/locki/services/worktree.py
  - /home/manuel/code/others/llms/locki/src/locki/services/container.py
  - /home/manuel/code/others/llms/locki/src/locki/cmd/internal.py
  - /home/manuel/code/others/llms/locki/src/locki/cmd/include.py
  - /home/manuel/code/others/llms/locki/src/locki/cmd/remove.py
related_notes:
  - "[[Research/Software Architecture Garden/locki/README|Architecture Garden — Locki]]"
  - "[[Research/Software Architecture Garden/locki/designs/01 - Split-Plane Sandbox Aggregate and Writable Authority Projections]]"
  - "[[Research/Software Architecture Garden/locki/designs/03 - Capability Re-entry for Host Git and Collaboration Effects]]"
  - "[[Research/Software Architecture Garden/devctl/02 - Durable State Process Identity and Wrapper Evidence]]"
---

# Sandbox Identity as a Join Across Workspace, Runtime, Policy, and Cleanup

Locki's eight-character `wt_id` is the sandbox coordinate that makes several independently managed resources one aggregate. It appears in worktree directories, branch suffixes, trusted metadata, included repositories, Incus container names, scoped-cache paths, command-policy placeholders, and orphan cleanup. This naming discipline is load-bearing, but the current code often reconstructs identity from strings rather than validating ownership as a domain contract.

> [!summary]
> - `wt_id` joins host Git custody, guest runtime, policy scope, cache ownership, includes, and cleanup.
> - Branch suffixes and directory names encode identity; they should not be the source of identity in a port or rewrite.
> - `WORKTREES_META` is the host-owned trust anchor for repository location, `.git` pointer, hooks, and excludes.
> - Included repositories share the parent sandbox ID while retaining distinct workspace identities.
> - Destructive operations require ownership evidence; a matching suffix, pathname, or container name is not sufficient by itself.

## Why this note exists

The architecture is easy to misread as two parallel resources: worktree plus container. In fact, Locki joins more than two stores without a central database. The join works because all components reproduce the same short identity and because cleanup understands the naming/device conventions.

That makes identity a portability boundary. A new backend that changes names, paths, or resource ownership must preserve the join or replace it with an explicit catalog.

## Pattern statement

> **Allocate one validated sandbox identity before effects; encode it consistently into every owned resource; retain host-owned metadata that maps encodings back to semantic ownership; and require that mapping before destructive or privileged operations.**

The identity is semantic. Names are projections:

$$
name_i = encode_i(s).
$$

Correctness requires parsing/lookup to recover the same $s$ or fail:

$$
decode_i(name_i)=s.
$$

The current `wt_id_from_dir` simply takes the final eight characters (`worktree.py:48-53`), so malformed names can be interpreted as identities. A stronger domain constructor validates grammar, collision, and ownership.

## Concrete identity graph

```mermaid
flowchart TD
    ID[SandboxID / wt_id]
    ID --> WD[repo-locki-id worktree directory]
    ID --> BR[branch#locki-id]
    ID --> MD[WORKTREES_META/repo-locki-id]
    ID --> CT[Incus container name]
    ID --> SC[/var/cache/locki/scoped/id]
    ID --> IN[Included worktree branches/paths]
    ID --> PL[Policy placeholders wt-id / owned stash]
    ID --> CL[Orphan and idle cleanup]
```

`WorktreeInfo` carries `wt_id`, branch, source repository, worktree directory, and includes (`worktree.py:64-103`). The metadata directory records the source repository and a trusted copy of the `.git` pointer. Per-worktree hooks and excludes also live there (`worktree.py:168-225`).

The Incus container is named exactly by `wt_id`. Its `worktree` disk device source lets cleanup recover the corresponding host workspace (`container.py:14-19,183-198`; `internal.py:69-87`).

## Trusted metadata and projected workspace

The worktree `.git` file is projected and therefore guest-writable. The original Git directory is not. Locki copies the correct pointer into `WORKTREES_META`; before an accepted host command, `_resolve_bridged` compares the projected pointer with the trusted copy and repairs it using `O_NOFOLLOW` (`internal.py:154-193`).

This is a split-custody pattern:

```text
projected workspace:
    user code + writable .git pointer

host-only metadata:
    source repo locator
    trusted .git pointer
    hooks wrapper
    excludes
```

The projected pointer is not authority. The host-only copy is the repair source.

## Includes

`locki include` creates another repository's worktree beneath the primary workspace at `.locki/include/<repo>-locki-<id>` and uses the parent sandbox ID (`cmd/include.py:68-99`). The bridge resolver recognizes exactly two layouts: primary worktree and included worktree (`internal.py:166-175`).

The correct model distinguishes:

```text
SandboxID s
  owns WorkspaceID primary
  owns WorkspaceID include-a
  owns WorkspaceID include-b
```

All workspaces share sandbox policy/credential scope, but each maps to a different source repository and trusted metadata record.

## Behavioral contract

```text
I1. A new SandboxID is allocated before branch/worktree/container/cache mutation.
I2. Every resource carries or is indexed by that SandboxID.
I3. Branches created/switched for the sandbox end in #locki-<id>.
I4. Trusted .git metadata and repository locator remain host-owned.
I5. Includes share SandboxID but retain distinct workspace/repository identity.
I6. Removing a workspace does not remove branches unless explicitly requested.
I7. Removing a sandbox deletes only resources whose ownership maps to its ID.
I8. Collision or malformed identity fails before side effects.
```

The current implementation strongly supports I2–I6. I1/I8 remain weaker because random allocation has no explicit collision loop and parsers infer IDs from suffixes.

## Ownership relation

Let resources be $r\in\mathcal R$ and sandboxes $s\in\mathcal S$. Define:

$$
owner:\mathcal R\rightharpoonup\mathcal S.
$$

A resource name is a claim about `owner`, not proof. A destructive action must validate:

$$
owner(r)=s\land lease(s)=operationToken.
$$

For a PVE environment this means a configured VMID is not enough. For a worktree it means path suffix is not enough. The catalog/trusted metadata must attest ownership.

## Pattern vocabulary

- **Semantic identity as explicit projection:** one identity produces several storage/runtime encodings.
- **Aggregate identifier:** the ID joins components of a distributed aggregate.
- **Namespace ownership:** branch/stash mutations are restricted to names carrying the sandbox coordinate.
- **Trusted metadata sidecar:** host-only metadata repairs projected, mutable metadata.
- **Resource ownership record:** destructive operations require durable provenance, not a guessed name.
- **Composite aggregate:** included repositories are child workspaces under one sandbox scope.

## Why alternatives are wrong

### Use the branch name as identity

Branches can be renamed, detached, deleted, or recreated. The stable sandbox coordinate must survive branch presentation changes.

### Use the container name as identity

A worktree can exist without a container. Deleting the VM removes containers but must preserve workspace identity.

### Infer identity from the final eight path characters

It accepts malformed/colliding names and makes storage naming rules define the domain. Parsing should validate an explicit encoding.

### Give included repositories independent sandbox IDs

That would create separate policy/runtime ownership inside one container and break the intended shared-session scope. They need distinct workspace IDs under one sandbox ID.

### Delete every matching suffix

A suffix is not ownership evidence. A future provider on a shared hypervisor requires controller-created records and immutable markers.

## Failure modes and open obligations

1. **Collision:** `new()` does not check existing IDs before returning the object.
2. **Malformed directory acceptance:** `wt_id_from_dir` slices without validating the `-locki-` tag.
3. **Cross-sandbox authority confusion:** the gateway derives scope from caller-supplied cwd, not an authenticated identity.
4. **Transient missing storage:** metadata pruning and orphan deletion can treat an unmounted projection as deletion.
5. **Partial cleanup:** janitor orphan deletion does not use the same scoped-cache cleanup path as explicit removal.
6. **Path/identity conflation:** an absolute path currently carries both workspace location and claimed principal scope.

## Testing and verification

- Property test `Parse(Format(id)) == id` and reject malformed encodings.
- Force collisions and prove allocation retries before effects.
- Create primary/includes and verify all child resources map to one sandbox plus distinct workspaces.
- Differentially reconstruct the aggregate from metadata, Git, and runtime observations.
- Verify sandbox A cannot authorize workspace B even when B's path is known.
- Remove infrastructure and prove workspace/branch identity persists.
- Unmount projection storage and prove metadata/runtime is not deleted.
- Verify every destructive provider call requires ownership attestation and lease token.

## Applicability

Use this pattern when one logical execution scope spans heterogeneous resources—filesystem, VCS, containers, caches, endpoints, and policy—and resource lifecycle is independent.

Do not use a short human-readable ID as the sole security credential. Identity joins state; authentication proves the caller.

## Candidate ecosystem guidance

1. Allocate identity before effects.
2. Treat names as encodings, not authority.
3. Keep a host-owned ownership map for destructive operations.
4. Separate sandbox identity from workspace identity.
5. Test every adapter against one identity/ownership contract.
6. Fence cleanup with storage health and operation leases.

## Open questions

- Should IDs become UUID/ULID values with short display aliases?
- Where should target ownership records live in a Go rewrite?
- How should imported/adopted worktrees receive ownership attestations?
- Should branches remain the user-facing label while sandbox ID stays opaque?

## Evidence and references

- `src/locki/services/worktree.py:43-103,129-256,355-439`
- `src/locki/services/container.py:14-19,162-261`
- `src/locki/cmd/internal.py:69-87,136-200`
- `src/locki/cmd/include.py:23-99`
- `src/locki/cmd/remove.py:26-84`
- `test/e2e.sh` — new/include/tamper/branch/removal scenarios.
- [[Research/Software Architecture Garden/locki/README|Architecture Garden — Locki]]
- [[Research/Software Architecture Garden/devctl/02 - Durable State Process Identity and Wrapper Evidence|Durable State, Process Identity, and Wrapper Evidence]]

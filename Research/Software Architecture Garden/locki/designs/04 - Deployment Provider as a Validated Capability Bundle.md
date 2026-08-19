---
title: Deployment Provider as a Validated Capability Bundle
aliases:
  - Locki provider bundle
  - VM backend decomposition
  - Lima and Proxmox capability bundle
status: emergent
maturity: Emergent
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
  - ports-and-adapters
  - virtualization
  - lima
  - proxmox
  - ssh
  - virtiofs
related_files:
  - /home/manuel/code/others/llms/locki/src/locki/services/vm.py
  - /home/manuel/code/others/llms/locki/src/locki/services/container.py
  - /home/manuel/code/others/llms/locki/src/locki/services/daemon.py
  - /home/manuel/code/others/llms/locki/src/locki/cmd/port_forward.py
  - /home/manuel/code/others/llms/locki/src/locki/data/locki-ssh-config
related_notes:
  - "[[Research/Software Architecture Garden/locki/README|Architecture Garden — Locki]]"
  - "[[Research/Software Architecture Garden/locki/designs/01 - Split-Plane Sandbox Aggregate and Writable Authority Projections]]"
  - "[[Research/Software Architecture Garden/locki/designs/05 - Readiness Requires Generation and Verified Postconditions]]"
  - "[[Research/Software Architecture Garden/locki/designs/09 - Endpoint Exposure Owns the Whole Publication Path]]"
  - "[[Research/Software Architecture Garden/locki/designs/10 - Observed-State Idle Janitor Is Not Desired-State Reconciliation]]"
  - "[[Research/Software Architecture Garden/devctl/05 - Declarative Plugins and Validated Dynamic Commands]]"
---

# Deployment Provider as a Validated Capability Bundle

Locki's direct calls to Lima are concentrated in `VMService`, but the behavior that makes a deployment work is not. Lima also supplies writable projection semantics, a guest-to-host alias, automatic host endpoint publication, VM creation/provisioning integration, and status/start behavior relied on elsewhere. A portable deployment provider is therefore a validated tuple of capabilities, not one class named `VMBackend`.

> [!summary]
> - `VMService` currently combines binary discovery, lifecycle, implicit start, guest execution, interactive sessions, copy, mount construction, provisioning, and UI/subprocess concerns.
> - Hidden Lima dependencies live in guest SSH configuration, fixed host addressing, exact path identity, and endpoint forwarding.
> - The target provider bundle contains environment lifecycle, guest transport, projection provider, host-reachability transport, and outer endpoint transport.
> - Narrow ports are valuable, but arbitrary mix-and-match is not: the composition root validates a compatible bundle and shared path/reachability semantics.
> - Proxmox lifecycle is not the first hard problem. Controller/worktree data placement and projection semantics must be decided before implementation.

## Why this note exists

A plausible first port extracts `VMService` into `LimaBackend` and writes `SSHBackend`. That refactor would centralize command transport but leave the system unable to see worktrees, reach the host capability gateway, or publish sandbox endpoints with current semantics.

The source teaches a broader rule: portability boundaries should follow capabilities whose failure and conformance differ, while deployment adapters that must agree should be selected as a bundle.

## Pattern statement

> **Represent a deployment provider as a tuple of narrow capabilities—lifecycle, guest transport, writable projection, host reachability, and outer endpoint transport—and accept the tuple only when compatibility and conformance are validated. Possession of one capability never implies the others.**

Let:

$$
B=(L,T,P,R,O)
$$

where:

- $L$ — environment lifecycle;
- $T$ — guest transport;
- $P$ — projection provider;
- $R$ — host-reachability transport;
- $O$ — outer endpoint transport.

A bundle refines the abstract deployment contract only if each component passes its contract and cross-component relations—especially path mapping and reachability—hold.

## Current Lima bundle

### Lifecycle

`VMService.status`, `ensure_running`, `stop`, and `delete` call `limactl`. `ensure_running` constructs a Fedora Lima config, sizes memory/CPU/disk, declares mounts, embeds `vm-setup.sh`, and creates/starts the VM (`services/vm.py:67-75,124-202`).

### Guest transport

`run` uses `limactl shell --start ... sudo -E`; `shell` supplies inherited stdio/TTY behavior; `copy_into` uses `limactl copy`; `incus` is a daemon-safe path that deliberately does not start the VM (`vm.py:77-122`).

These operations expose provider-specific status strings and `CompletedProcess`/spinner concerns to callers.

### Projection

The Lima config mounts host `WORKTREES` at the same absolute path and `SANDBOX_HOME` at `/root/.locki/home` (`vm.py:147-160`). `ContainerService` later uses the host worktree pathname as both Incus disk source and guest destination (`container.py:183-198`).

### Host reachability

The guest SSH config names `host.lima.internal`; container setup hard-codes that name to `192.168.5.2` (`data/locki-ssh-config`; `container-setup.sh:528-535`). This is how a host-loopback daemon becomes reachable from the guest network.

### Outer endpoint transport

`port_forward.py` installs an Incus proxy listener on the VM. Lima detects the listening port and publishes it to host loopback; the E2E suite explicitly waits for that provider behavior (`test/e2e.sh:426-443`).

None of the last three contracts is provided by a generic SSH connection.

## Target ports

```go
type EnvironmentLifecycle interface {
    Observe(context.Context, OwnedEnvironmentRef) (EnvironmentObservation, error)
    Ensure(context.Context, EnvironmentSpec, OwnershipIntent) (EnvironmentObservation, error)
    Start(context.Context, OwnedEnvironmentRef) error
    Stop(context.Context, OwnedEnvironmentRef, StopMode) error
    Delete(context.Context, OwnedEnvironmentRef) error
}

type GuestTransport interface {
    Probe(context.Context) (GuestIdentity, error)
    Exec(context.Context, ExecRequest) (ExecResult, error)
    Interactive(context.Context, InteractiveRequest) (ExitStatus, error)
    Copy(context.Context, CopyRequest) error
}

type ProjectionProvider interface {
    Ensure(context.Context, ProjectionSpec) (ProjectionObservation, error)
    Remove(context.Context, ProjectionID) error
}

type HostReachabilityTransport interface {
    Ensure(context.Context, ReachabilitySpec) (ReachabilityObservation, error)
    Remove(context.Context, ReachabilityID) error
}

type OuterEndpointTransport interface {
    Publish(context.Context, OuterEndpointSpec) (OuterEndpointObservation, error)
    Observe(context.Context, OuterEndpointID) (OuterEndpointObservation, error)
    Remove(context.Context, OuterEndpointID) error
}
```

Lifecycle owns existence/power, not provisioning. Guest transport owns process I/O, not implicit lifecycle policy. Projection reports host/guest roots and semantics. Reachability carries sessions but does not decide principal identity. Outer endpoint transport is a primitive composed by the endpoint-exposure subsystem, which owns allocation/scope/records.

## Compatibility relations

A composition root validates more than interface presence:

```text
projection guest paths are reachable by runtime
PathMap is shared by workspace, gateway, and hooks
guest transport identity matches lifecycle environment
reachability listener is accessible from container network but not broader scope
outer endpoint transport can publish the runtime's inner proxy
provisioning bundle requirements match provider capabilities/OS
```

Independent configuration dropdowns could create valid objects that form an invalid deployment. Bundling records tested combinations without making ports coarse.

## Exact path identity is the hidden seam

The reference deployment effectively assumes:

```text
guest cwd == outer VM worktree path == authority-host worktree path
```

The host gateway accepts guest cwd as host cwd because Lima's mapping is identity. A PVE deployment may choose a different mount root. Then cwd, command arguments, and actual worktree hook files cross as workspace-relative semantic paths through a `PathMap`. Git administrative hook files such as `COMMIT_EDITMSG` are not workspace paths; design 08 carries them as hook-schema-specific ephemeral file capabilities through controlled guest scratch storage.

```go
type PathMap interface {
    HostPath(WorkspaceID, WorkspaceRelativePath) (HostPath, error)
    GuestPath(WorkspaceID, WorkspaceRelativePath) (GuestPath, error)
}
```

Path mapping is shared domain infrastructure, not an SSH option.

## Proxmox data-placement gate

Phase 1 runs the Locki authority process and worktrees inside controller VM 9410. A direct PVE-managed outer VM is a sibling, not a child. PVE virtiofs projects PVE-host directories into a VM; it does not directly project VM 9410's local files into the sibling.

Candidate topologies:

1. **Authority on PVE host:** simple projection; unacceptable hypervisor/application coupling unless explicitly accepted.
2. **PVE-hosted projection roots shared to controller and sandbox VMs:** removes nested QEMU, but PVE root joins worktree/credential trust and multi-VM coherence must be proved.
3. **Controller VM exports only worktrees/home over an isolated filesystem:** preserves authority placement; must solve UID/root squash, confinement, consistency, and reconnect.
4. **Keep nested Lima:** validated reference/fallback.

The decision precedes lifecycle API implementation.

## Behavioral contract

```text
B1. Lifecycle-local state is structured: absent/stopped/starting/running/unreachable/deleting; aggregate Ready is derived only from lifecycle plus projection, provisioning, gateway, and required postconditions.
B2. Every destructive lifecycle action verifies ownership attestation, not VMID/name alone.
B3. Guest transport preserves stdin/stdout/stderr/TTY/env/signal/cancellation/exit status semantics.
B4. Projection declares roots, mutability, sharing, identity, health, and filesystem semantics.
B5. Reachability does not imply authentication; gateway core binds principal.
B6. Outer endpoint transport cannot choose bind policy or ExposureID.
B7. Bundle validation rejects incompatible component tuples.
B8. Provider observations do not become desired state implicitly.
B9. Repository config cannot select host-executable providers or widen host authority.
```

## Refinement and conformance

Let abstract operations be $A$ and concrete provider histories be $H_B$. A bundle is substitutable when an abstraction mapping $\alpha_B$ produces legal abstract histories and equivalent observations:

$$
\alpha_B(H_B)\in A^*,
\qquad
observe(\alpha_{Lima}(H))\approx observe(\alpha_{PVE}(H')).
$$

Equivalence covers user-visible and security-relevant behavior, not identical implementation:

- durable work survives environment deletion;
- projected edits are coherent;
- host effects remain non-routable and authenticated;
- endpoint scope is preserved;
- readiness generations are honored;
- unowned resources are never mutated.

## Pattern vocabulary

- **Ports and Adapters:** provider-specific mechanisms implement stable capabilities.
- **Abstract Factory / Bundle:** a tested provider constructs a compatible family of adapters.
- **Refinement Mapping:** concrete Lima/PVE histories map to one abstract contract.
- **Capability Negotiation:** provisioning/runtime requirements are checked before use.
- **Anti-Corruption Layer:** provider status/process types do not leak into the domain.
- **Conformance Suite:** behavior, not method shape, defines substitutability.

## Why tempting alternatives fail

### One `VMBackend` with every method

It recreates provider coupling and hides independent failure/security boundaries.

### Completely independent plugin selection

Lifecycle, transport, paths, reachability, and publication may be individually valid but mutually incompatible.

### SSH backend first

SSH proves command reachability, not workspace projection, gateway path, endpoint publication, or ownership.

### Put provisioning inside lifecycle ensure

It makes a stopped/current environment indistinguishable from stale provisioning and prevents target-specific generations.

### Make provider plugins responsible for gateway authentication

Connectivity plugins should not mint application principals. Gateway identity/policy remain core.

## Failure modes and tricky details

1. Proxmox VMID reuse can target an unrelated VM without ownership attestation.
2. Non-identity mounts break cwd, argv paths, and hook paths if `PathMap` is incomplete.
3. SSH TTY/signal/env semantics may diverge from Lima shell.
4. Multi-VM shared filesystem coherence may differ from Lima 9p.
5. Reverse tunnels may bind only guest loopback, unreachable from Incus containers.
6. Endpoint publication can widen from loopback to LAN/tailnet unintentionally.
7. Plugin catalog/discovery is not live authority or compatibility proof.

## Testing and verification

Run one differential suite against Lima and PVE:

- lifecycle idempotency, unreachable/degraded states, ownership-negative mutations;
- noninteractive/interactive streams, signals, env, cancellation, exit codes;
- path mapping, permissions, symlinks, locks, watchers, concurrent edits;
- storage health versus absence;
- gateway reachability, server identity, principal rotation/revocation;
- Incus bridge/NAT, DNS/HTTPS, MTU, KVM/vhost capability observation;
- endpoint bind scope, collision, recovery, teardown;
- environment/container/home persistence and provisioning generations.

Keep Lima as the acceptance oracle until the second bundle passes.

## Applicability

Use the bundle pattern when deployment behavior spans several independently testable capabilities that must still be selected compatibly.

Do not create external provider plugins before two in-tree implementations establish real commonality. Do not use a bundle to hide core security policy inside provider code.

## Candidate ecosystem guidance

1. Split ports by capability and failure semantics.
2. Select compatible families as a bundle.
3. Validate cross-port relations, not interfaces alone.
4. Treat path projection as first-class.
5. Keep desired state, provisioning, and authentication outside lifecycle adapters.
6. Define substitutability through differential conformance.

## Open questions

- Which PVE data topology wins the projection experiment?
- What ownership marker can safely attest a Proxmox VM across VMID reuse?
- Which filesystem semantics are normative versus compatibility-only?
- What is the minimal out-of-process provider protocol after two bundles exist?
- Should externally managed environments be a third bundle mode?

## Evidence and references

- `src/locki/services/vm.py:52-202`
- `src/locki/services/container.py:162-261`
- `src/locki/services/daemon.py:20-71`
- `src/locki/cmd/port_forward.py:12-126`
- `src/locki/data/locki-ssh-config`
- `src/locki/data/container-setup.sh:528-535`
- `test/e2e.sh:426-443`
- [[Research/Software Architecture Garden/locki/README|Architecture Garden — Locki]]
- [[Research/Software Architecture Garden/devctl/05 - Declarative Plugins and Validated Dynamic Commands|Declarative Plugins and Validated Dynamic Commands]]

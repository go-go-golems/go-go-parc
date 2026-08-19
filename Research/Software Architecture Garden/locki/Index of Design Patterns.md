---
title: Locki — Index of Design Patterns
aliases:
  - Locki design pattern index
  - Locki architecture glossary
status: active
type: architecture-garden-index
created: 2026-08-19
analyzed: 2026-08-19
analysis_schema: architecture-garden-v1
repository: /home/manuel/code/others/llms/locki
repository_commit: 0546b381005048418d9ff2622a47a3a67c982dc0
derived_from: Research/Software Architecture Garden/locki/README.md
tags:
  - architecture-garden
  - locki
  - design-pattern-index
  - sandboxing
  - capability-security
related_notes:
  - "[[Research/Software Architecture Garden/locki/README]]"
  - "[[Research/Software Architecture Garden/locki/Index of Design Patterns - Rationale]]"
  - "[[Research/Software Architecture Garden/README]]"
---

# Locki — Index of Design Patterns

This hybrid index and glossary files Locki by the ideas readers are likely to remember: authority, projection, identity, readiness, contamination, re-entry, exposure, and cleanup. Locators point to substantive sections. Maturity labels use the Garden's exact vocabulary.

## How to read this index

- **See** redirects an alternate phrase to its canonical entry.
- **see also** links related but non-equivalent concepts.
- `[Established]`, `[Emergent]`, `[Architecture debt]`, and `[Open correctness obligation]` are evidence claims, not quality scores.
- A link to a design title points to the focused study; README links point to system-level context.

## A

### Accepted-effect audit

Structured redacted evidence for successful and denied host Git/GitHub/Locki effects, including principal, workspace, effect class, outcome, and duration. [Open correctness obligation]
[[Research/Software Architecture Garden/locki/designs/03 - Capability Re-entry for Host Git and Collaboration Effects#Effect execution and audit|effect/audit boundary]], [[Research/Software Architecture Garden/locki/README#Architecture debt and open laws|open law]].

### Acceleration-independent correctness

Cache loss or disablement should change performance, not semantic results or authority. [Open correctness obligation]
[[Research/Software Architecture Garden/locki/designs/07 - Shared Acceleration Is an Explicit Contamination Domain#Behavioral contract|behavioral contract]], [[Research/Software Architecture Garden/locki/README#Architecture debt and open laws|overview obligations]].
*see also* [[#Contamination domain]], [[#Cache ownership]].

### Authenticated sandbox binding

The credential accepted by the host gateway must identify the same sandbox whose workspace and policy scope are authorized. [Open correctness obligation]
↳ [[Transcripts/Research/09 - RAG-MATHS Pattern Zoo#Pattern 12 — Authorization Dominates Disclosure|RAG 12 — Authorization Dominates Disclosure]] (correspondence, not equivalence).
[[Research/Software Architecture Garden/locki/designs/03 - Capability Re-entry for Host Git and Collaboration Effects#Authenticated sandbox binding|binding gap and target]], [[Research/Software Architecture Garden/locki/designs/03 - Capability Re-entry for Host Git and Collaboration Effects#Testing and verification|verification]].
*see also* [[#Capability re-entry]], [[#AuthorizedCommand]], [[#Sandbox identity]].

### Authority plane

The trusted host custody domain that owns original Git databases, trusted metadata, lifecycle credentials, and host effects. [Established]
[[Research/Software Architecture Garden/locki/README#The four governing laws|governing laws]], [[Research/Software Architecture Garden/locki/designs/01 - Split-Plane Sandbox Aggregate and Writable Authority Projections#Concrete architecture|concrete architecture]].
*see also* [[#Writable projection]], [[#Host effect authority]], [[#Outer environment]].

### AuthorizedCommand

An opaque value produced only after principal, ownership, path, and policy checks; the host executor accepts this value rather than raw argv. [Open correctness obligation]
[[Research/Software Architecture Garden/locki/designs/03 - Capability Re-entry for Host Git and Collaboration Effects#Policy shape|policy shape]], [[Research/Software Architecture Garden/locki/designs/03 - Capability Re-entry for Host Git and Collaboration Effects#Behavioral contract|contract]].

## B

### Bridge

*See* [[#Capability re-entry]]. The historical name hides identity, path binding, effect adapters, and audit.

### Bundle compatibility

The cross-port relation proving lifecycle, guest transport, projections, reachability, and endpoint transport form one usable deployment. [Emergent]
[[Research/Software Architecture Garden/locki/designs/04 - Deployment Provider as a Validated Capability Bundle#Compatibility relations|compatibility relations]].
*see also* [[#Provider capability bundle]], [[#Differential conformance]].

## C

### Cache ownership

The acceleration subsystem alone owns scoped-cache paths, pruning, and sandbox-scoped deletion. [Open correctness obligation]
[[Research/Software Architecture Garden/locki/designs/07 - Shared Acceleration Is an Explicit Contamination Domain#Cache ownership contract|cache contract]], [[Research/Software Architecture Garden/locki/designs/10 - Observed-State Idle Janitor Is Not Desired-State Reconciliation#Why it is not reconciliation|cleanup mismatch]].

### Capability re-entry

Policy-mediated guest request for selected host Git, GitHub, or Locki-control effects. [Emergent]
↳ [[Transcripts/Research/10 - PBUI-MATHS Pattern Zoo Handbook#Pattern 5 — Command as Data|PBUI 5 — Command as Data]] (correspondence, not equivalence).
[[Research/Software Architecture Garden/locki/designs/03 - Capability Re-entry for Host Git and Collaboration Effects#Concrete request path|request path]], [[Research/Software Architecture Garden/locki/designs/03 - Capability Re-entry for Host Git and Collaboration Effects#The bridge is six responsibilities|decomposition]].
*see also* [[#Authenticated sandbox binding]], [[#Host effect authority]], [[#Writable projection]].

### Cleanup loop

*See* [[#Idle janitor]]. It is not a synonym for desired-state reconciliation.

### Contamination domain

A sharing scope in which members can affect common integrity, availability, and sometimes confidentiality; Locki's caches, builder, CA/cache, home, and VM kernel create distinct contamination domains. [Established]
[[Research/Software Architecture Garden/locki/designs/07 - Shared Acceleration Is an Explicit Contamination Domain#Contamination dimensions|acceleration dimensions]], [[Research/Software Architecture Garden/locki/designs/01 - Split-Plane Sandbox Aggregate and Writable Authority Projections#Ownership and durability classes|system trust classes]].
*see also* [[#Harness-home sharing scope]], [[#Operational tenant]].

## D

### Daemon incarnation identity

Daemon supervision should bind PID to a start/incarnation token or live socket handshake; PID liveness plus version files can misidentify reused processes. [Open correctness obligation]
[[Research/Software Architecture Garden/locki/README#Architecture debt and open laws|open law]], [[Research/Software Architecture Garden/locki/designs/10 - Observed-State Idle Janitor Is Not Desired-State Reconciliation#Pattern vocabulary|incarnation/ownership vocabulary]].

### Desired state

Controller-owned declaration of resource existence, retention, runtime state, and exposures; it must remain distinct from provider observations. [Open correctness obligation]
[[Research/Software Architecture Garden/locki/designs/10 - Observed-State Idle Janitor Is Not Desired-State Reconciliation#Target records|target records]], [[Research/Software Architecture Garden/locki/designs/10 - Observed-State Idle Janitor Is Not Desired-State Reconciliation#Replacement law|replacement law]].

### Desired-state reconciler

A controller that uses desired records, ownership, positive health, leases, and observations to produce idempotent convergence plans. [Open correctness obligation]
[[Research/Software Architecture Garden/locki/designs/10 - Observed-State Idle Janitor Is Not Desired-State Reconciliation#Why it is not reconciliation|missing pieces]], [[Research/Software Architecture Garden/locki/designs/10 - Observed-State Idle Janitor Is Not Desired-State Reconciliation#Reconciliation plan|target plan]].
*must not be confused with* [[#Idle janitor]].

### Differential conformance

One provider-neutral suite applied to Lima and a future PVE bundle to establish behavioral substitution. [Open correctness obligation]
[[Research/Software Architecture Garden/locki/designs/04 - Deployment Provider as a Validated Capability Bundle#Refinement and conformance|refinement]], [[Research/Software Architecture Garden/locki/designs/04 - Deployment Provider as a Validated Capability Bundle#Testing and verification|suite]].

### Durable work / disposable infrastructure

Worktrees and branches survive VM/container deletion; reconstruction of infrastructure never implies deletion of user work. [Established]
[[Research/Software Architecture Garden/locki/designs/01 - Split-Plane Sandbox Aggregate and Writable Authority Projections#Ownership and durability classes|durability classes]], [[Research/Software Architecture Garden/locki/README#4. Durable user work survives disposable infrastructure|law]].

## E

### Endpoint exposure

One owned object spanning allocation, container endpoint, inner proxy, outer transport, bind scope, advertised URL, observation, and teardown. [Emergent]
[[Research/Software Architecture Garden/locki/designs/09 - Endpoint Exposure Owns the Whole Publication Path#Target object|target object]], [[Research/Software Architecture Garden/locki/designs/09 - Endpoint Exposure Owns the Whole Publication Path#Behavioral contract|contract]].
*see also* [[#Exposure identity and bind scope]], [[#Outer endpoint transport]].

### Existence means ready

*See* [[#Provisioning generation and receipt]]. Resource existence is explicitly insufficient.

### Exposure identity and bind scope

`ExposureID` owns the publication lifecycle, while scope (`loopback`, `tailnet`, `LAN`, `public`) limits who can reach it. [Open correctness obligation]
[[Research/Software Architecture Garden/locki/designs/09 - Endpoint Exposure Owns the Whole Publication Path#Behavioral contract|contract]], [[Research/Software Architecture Garden/locki/designs/09 - Endpoint Exposure Owns the Whole Publication Path#Mathematical foundations|scope law]].

## G

### Generation-stamped readiness

A target is ready only when observed generation/digest equals desired generation/digest and all postconditions pass. [Open correctness obligation]
[[Research/Software Architecture Garden/locki/designs/05 - Readiness Requires Generation and Verified Postconditions#Pattern statement|pattern]], [[Research/Software Architecture Garden/locki/designs/05 - Readiness Requires Generation and Verified Postconditions#Behavioral contract|contract]].

### Git hook re-entry

Trusted host wrapper re-enters the same sandbox/workspace so original repository hook code runs in guest authority. [Emergent]
[[Research/Software Architecture Garden/locki/designs/08 - Git Hook Re-entry Across the Sandbox Boundary#Recursive flow|flow]], [[Research/Software Architecture Garden/locki/designs/08 - Git Hook Re-entry Across the Sandbox Boundary#Behavioral contract|contract]].
*see also* [[#Capability re-entry]], [[#PathMap]].

## H

### Harness-home sharing scope

Explicit set of sandboxes with read/write/exfiltration authority over durable AI credentials, settings, hooks, and transcripts. [Established]
[[Research/Software Architecture Garden/locki/designs/06 - Shared Harness Home Is an Explicit Credential Domain#Authority and sharing model|sharing model]], [[Research/Software Architecture Garden/locki/designs/06 - Shared Harness Home Is an Explicit Credential Domain#Sharing scopes|scope options]].
*see also* [[#Contamination domain]], [[#Writable projection]].

### Hook ephemeral file

A hook-schema-specific capability for trusted Git administrative files such as `COMMIT_EDITMSG`: copied to controlled guest scratch and copied back only to the exact host-owned source file. [Open correctness obligation]
[[Research/Software Architecture Garden/locki/designs/08 - Git Hook Re-entry Across the Sandbox Boundary#Path transfer|path classes]], [[Research/Software Architecture Garden/locki/designs/08 - Git Hook Re-entry Across the Sandbox Boundary#Behavioral contract|contract]].
*must not be confused with* [[#Workspace identity]], [[#PathMap]].

### Host effect authority

Host-user Git, GitHub, and Locki-control powers exposed only through the capability gateway and effect-specific policy. [Emergent]
[[Research/Software Architecture Garden/locki/designs/03 - Capability Re-entry for Host Git and Collaboration Effects#Effect execution and audit|effect adapters]], [[Research/Software Architecture Garden/locki/README#2. Workspace mutation and host process authority are distinct|system law]].

## I

### Idle janitor

Current periodic heuristic that stops idle containers, deletes selected orphans, and stops the VM without durable desired-state proof. [Architecture debt]
[[Research/Software Architecture Garden/locki/designs/10 - Observed-State Idle Janitor Is Not Desired-State Reconciliation#Current janitor|current mechanism]], [[Research/Software Architecture Garden/locki/designs/10 - Observed-State Idle Janitor Is Not Desired-State Reconciliation#Why it is not reconciliation|limits]].

## O

### Operation lease

Fenced controller record preventing entry, provisioning, hooks, endpoint publication, removal, and cleanup from destructively racing. [Open correctness obligation]
[[Research/Software Architecture Garden/locki/designs/10 - Observed-State Idle Janitor Is Not Desired-State Reconciliation#Target records|lease record]], [[Research/Software Architecture Garden/locki/README#Architecture debt and open laws|overview obligations]].

### Operational tenant

One privileged Incus container with separate rootfs/process namespace and `/tmp`, but shared VM kernel/home/cache planes. [Established]
[[Research/Software Architecture Garden/locki/README#Trust zones and explicit capabilities|trust zones]], [[Research/Software Architecture Garden/locki/designs/01 - Split-Plane Sandbox Aggregate and Writable Authority Projections#Concrete architecture|architecture]].

### Outer endpoint transport

Provider-specific tunnel/listener primitive composed by endpoint exposure; it does not own allocation, scope, or exposure records. [Emergent]
[[Research/Software Architecture Garden/locki/designs/04 - Deployment Provider as a Validated Capability Bundle#Target ports|provider port]], [[Research/Software Architecture Garden/locki/designs/09 - Endpoint Exposure Owns the Whole Publication Path#Provider-specific outer transport|composition]].

### Outer environment

The managed Lima VM that forms the primary host-isolation boundary and shared-fate domain for Incus tenants. [Established]
[[Research/Software Architecture Garden/locki/designs/01 - Split-Plane Sandbox Aggregate and Writable Authority Projections#Concrete architecture|architecture]].

### Ownership attestation

Controller-owned evidence that a concrete resource incarnation belongs to one sandbox/environment; names and reusable platform IDs are insufficient. [Open correctness obligation]
[[Research/Software Architecture Garden/locki/designs/02 - Sandbox Identity as a Join Across Workspace Runtime Policy and Cleanup#Ownership relation|ownership relation]], [[Research/Software Architecture Garden/locki/designs/04 - Deployment Provider as a Validated Capability Bundle#Behavioral contract|provider contract]].

## P

### PathMap

Shared translation from semantic workspace-relative paths to host and guest roots, including cwd, command arguments, and actual worktree hook files; Git administrative hook files use `HookEphemeralFile` instead. [Open correctness obligation]
[[Research/Software Architecture Garden/locki/designs/04 - Deployment Provider as a Validated Capability Bundle#Exact path identity is the hidden seam|hidden seam]], [[Research/Software Architecture Garden/locki/designs/08 - Git Hook Re-entry Across the Sandbox Boundary#Path transfer|hook transfer]].

### Policy artifact separation

Executable host-command policy should be independently versioned/validated from human `AGENTS.md` instructions; unknown placeholders fail compilation. [Architecture debt]
[[Research/Software Architecture Garden/locki/designs/03 - Capability Re-entry for Host Git and Collaboration Effects#Policy shape|current fusion]], [[Research/Software Architecture Garden/locki/README#Architecture debt and open laws|open law]].

### Port forwarding

*See* [[#Endpoint exposure]]. The historical command name describes only part of the publication path.

### Positive storage-health evidence

Proof that the expected projection storage/mount is healthy before missing paths may be interpreted as deletion. [Open correctness obligation]
[[Research/Software Architecture Garden/locki/designs/10 - Observed-State Idle Janitor Is Not Desired-State Reconciliation#Replacement law|replacement law]], [[Research/Software Architecture Garden/locki/designs/10 - Observed-State Idle Janitor Is Not Desired-State Reconciliation#Behavioral contract|contract]].

### Pre-policy trusted context

Trusted `.git`, repository, remote, and stash context must be established from host-owned workspace custody before contextual policy evaluation. [Open correctness obligation]
[[Research/Software Architecture Garden/locki/designs/03 - Capability Re-entry for Host Git and Collaboration Effects#Trusted policy context must precede evaluation|ordering gap]], [[Research/Software Architecture Garden/locki/README#Architecture debt and open laws|open law]].

### Provider capability bundle

Compatible family of lifecycle, guest transport, projection, reachability, and outer endpoint transports. [Emergent]
[[Research/Software Architecture Garden/locki/designs/04 - Deployment Provider as a Validated Capability Bundle#Pattern statement|pattern]], [[Research/Software Architecture Garden/locki/designs/04 - Deployment Provider as a Validated Capability Bundle#Compatibility relations|compatibility]].

### Provisioning generation and receipt

Target-specific desired/observed bundle identity plus phase/postcondition evidence; the readiness witness absent from current resources. [Open correctness obligation]
[[Research/Software Architecture Garden/locki/designs/05 - Readiness Requires Generation and Verified Postconditions#Target bundle and receipts|bundle/receipt]], [[Research/Software Architecture Garden/locki/designs/05 - Readiness Requires Generation and Verified Postconditions#Observed failure|failure evidence]].

### PVE data-placement decision gate

Pre-implementation decision identifying which trusted machine owns repositories, metadata, home, credentials, gateway, and projection roots. [Open correctness obligation]
[[Research/Software Architecture Garden/locki/designs/04 - Deployment Provider as a Validated Capability Bundle#Proxmox data-placement gate|decision gate]], [[Research/Software Architecture Garden/locki/README#Recommended next investigations|next investigation]].

## S

### Sandbox aggregate

Logical sandbox reconstructed from independently observed workspace, storage, environment, projections, home, container, gateway, generations, endpoints, and lease. [Established]
[[Research/Software Architecture Garden/locki/README#The sandbox is a product state, not one enum|product state]], [[Research/Software Architecture Garden/locki/designs/01 - Split-Plane Sandbox Aggregate and Writable Authority Projections#The sandbox aggregate|aggregate]].

### Sandbox identity

Aggregate join coordinate `wt_id` projected into worktree, branch, metadata, runtime, cache, includes, policy, and cleanup. [Emergent]
↳ [[Transcripts/Research/09 - RAG-MATHS Pattern Zoo#Pattern 1 — Semantic Identity as Explicit Projection|RAG 1 — Semantic Identity as Explicit Projection]] (correspondence, not equivalence).
[[Research/Software Architecture Garden/locki/designs/02 - Sandbox Identity as a Join Across Workspace Runtime Policy and Cleanup#Concrete identity graph|identity graph]].

### Sandbox is a container

*See* [[#Sandbox aggregate]]. A container is one resource axis, not the aggregate.

### Scoped cache isolation

*See* [[#Contamination domain]]. Scoped names support semantic cleanup, not ACL isolation.

### Shared harness home

*See* [[#Harness-home sharing scope]].

## T

### Trust tiers

Host-admin, user, repository, and sandbox configuration sources with decreasing authority to select providers, projections, plugins, policy, and effects. [Emergent]
[[Research/Software Architecture Garden/locki/README#Trust tiers|focused tier model]], [[Research/Software Architecture Garden/locki/designs/03 - Capability Re-entry for Host Git and Collaboration Effects#Why tempting alternatives are wrong|policy boundary]].

## V

### VM backend

*See* [[#Provider capability bundle]]. One coarse backend hides projection, reachability, and publication contracts.

### VMService seam

*See* [[#Provider capability bundle]]. `VMService` is evidence for extraction, not the finished abstraction.

## W

### Workspace identity

Identity of one primary or included repository worktree subordinate to a sandbox identity. [Emergent]
[[Research/Software Architecture Garden/locki/designs/02 - Sandbox Identity as a Join Across Workspace Runtime Policy and Cleanup#Includes|includes]].
*must not be confused with* [[#Sandbox identity]].

### Writable projection

Explicit host data root made writable inside the outer environment/container, distinct from host process-effect capability. [Established]
[[Research/Software Architecture Garden/locki/designs/01 - Split-Plane Sandbox Aggregate and Writable Authority Projections#Pattern statement|pattern]], [[Research/Software Architecture Garden/locki/README#1. Host authority stays outside untrusted execution|law]].

## Identity strings, scopes, and state coordinates

| Handle / coordinate | Kind | Meaning | Where |
|---|---|---|---|
| `wt_id` | sandbox identity encoding | Eight-character coordinate joining worktree/runtime/cache/policy/cleanup. | [[#Sandbox identity]] |
| `#locki-<wt-id>` | branch namespace | Sandbox-owned branch suffix. | [[#Sandbox identity]] |
| `WORKTREES_META` | host trust root | Repository locator, trusted `.git` pointer, hooks, excludes. | [[#Authority plane]], [[#Workspace identity]] |
| `SANDBOX_HOME` | credential scope root | Durable shared harness state projected as `/root`. | [[#Harness-home sharing scope]] |
| `ProjectionObservation` | state coordinate | Host/guest roots, mutability, sharing, health, filesystem semantics. | [[#Writable projection]], [[#PathMap]] |
| `ProvisioningGeneration` | incarnation/readiness coordinate | Desired/observed trusted bundle generation per target. | [[#Provisioning generation and receipt]] |
| `ExposureID` | publication identity | Owns end-to-end endpoint lifecycle. | [[#Endpoint exposure]] |
| `OperationLease` | concurrency fence | Prevents stale/conflicting lifecycle effects. | [[#Operation lease]] |
| Bind scopes | closed vocabulary | `loopback | tailnet | LAN | public`. | [[#Exposure identity and bind scope]] |
| Home scopes | closed vocabulary | `global | group | sandbox | brokered`. | [[#Harness-home sharing scope]] |

## Cross-reference summary

- **Host-owned effects:** Locki corresponds to [[Research/Software Architecture Garden/researchctl/README|Researchctl]] and devctl's host supervision, but its Git/GitHub gateway is a security authority boundary, not an experiment-plan interpreter.
- **Identity/ownership:** Locki corresponds to devctl process incarnation and PBUI identity discipline; a sandbox ID, generation, workspace ID, operation lease, and provider resource incarnation remain non-equivalent.
- **Reconciliation:** Locki's target law corresponds to [[Research/Software Architecture Garden/devctl/03 - Reconciliation and the Shared Operator Boundary|devctl reconciliation]], while the current janitor lacks desired state and leases.
- **Generation fencing:** provisioning generations correspond to Sessionstream/Pinocchio stale-completion fencing, but are not resource identity or authorization.
- **Cache semantics:** Flowkit's complete cache identity is relevant, while Locki's contamination domain additionally concerns cross-sandbox integrity and availability.

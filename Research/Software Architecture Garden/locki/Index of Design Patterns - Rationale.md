---
title: Locki — Index of Design Patterns (Rationale)
aliases:
  - Locki design index rationale
  - Locki architecture glossary rationale
status: active
type: architecture-garden-index-rationale
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
  - rationale
related_notes:
  - "[[Research/Software Architecture Garden/locki/README]]"
  - "[[Research/Software Architecture Garden/locki/Index of Design Patterns]]"
  - "[[Research/Software Architecture Garden/README]]"
---

# Locki — Index of Design Patterns (Rationale)

This rationale records why the Locki index uses its canonical terms, redirects, maturity labels, and omissions. It is editorial evidence: it does not introduce new architecture claims beyond the overview and ten focused designs.

## Principles of selection

### Index laws and authority boundaries, not every mechanism

The index includes a mechanism when a reader needs it to reason about ownership, authority, persistence, failure, or portability. `PathMap` belongs because it controls host/guest path meaning. Individual Lima flags do not.

### Keep non-equivalent identities separate

Sandbox identity, workspace identity, provider resource incarnation, provisioning generation, exposure identity, and operation lease solve different problems. The index uses `see also` rather than redirects among them.

### Index negative corrections

Readers may remember the incorrect simplification: “VM backend,” “sandbox is a container,” “scoped cache isolation,” “cleanup loop.” Redirects lead to the corrected concept and explain the mismatch.

### Index failures and open laws as carefully as established behavior

Architecture debt and open laws receive first-class canonical entries because a future port is more likely to fail at those boundaries than at the well-documented happy path. The README's `Architecture debt and open laws` section is the canonical list; the index provides reader-memory access paths rather than preserving an imported O-number namespace.

### Keep current mechanisms distinct from target patterns

`Idle janitor` names current behavior. `Desired-state reconciler` names a target contract. `Capability re-entry` is emergent; `Authenticated sandbox binding` is still open. The index never upgrades a target law into current evidence.

## What was deliberately excluded

- Individual Lima CLI flags and status strings: adapter details, not reusable laws.
- Fixed addresses such as `10.99.0.1` and `192.168.5.2`: current deployment constants; they appear in provider/network studies but do not deserve canonical index entries.
- Every package-manager cache environment variable: the pattern is contamination/semantic cache identity, not a catalog of variables.
- Individual bridge grammar rules: the gateway study explains policy shape; exact commands remain source evidence.
- Every `VMService` method: grouped under provider capabilities and the `VM backend` redirect.
- Every Incus profile device: KVM/vhost/cache/home devices matter as capability/trust evidence, not separate patterns.
- Every Click command: use cases are documented in source/README; the Garden indexes architectural boundaries.
- Proxmox topology Options A–D as separate patterns: the data-placement decision is unresolved, not four endorsed designs.
- `go-plugin`, gRPC, or NDJSON: no plugin protocol has been selected and the study explicitly delays that decision.

## Canonical-term rationale

### Authority plane

> Index entry: [[Index of Design Patterns#Authority plane]].

Chosen because “host” alone is ambiguous in a nested deployment. The term identifies where trusted custody/effects live, independent of whether that plane is a laptop, controller VM, or PVE host.

### Writable projection

> Index entry: [[Index of Design Patterns#Writable projection]].

Chosen to prevent mounts from being described as observations or incidental plumbing. They grant direct write authority over host-backed bytes.

### Sandbox aggregate

> Index entry: [[Index of Design Patterns#Sandbox aggregate]].

Chosen because a sandbox is reconstructed from independently failing resources. Omitting it would encourage one flattened `Running` state or “sandbox = container.”

### Sandbox identity and workspace identity

> Index entries: [[Index of Design Patterns#Sandbox identity]], [[Index of Design Patterns#Workspace identity]].

Separated because one sandbox may own a primary and included workspaces. `wt_id` joins the aggregate; workspace identity selects one repository/path inside that aggregate.

### Ownership attestation

> Index entry: [[Index of Design Patterns#Ownership attestation]].

Chosen instead of “resource name” because destructive authority must survive platform-local ID reuse and external operator changes.

### PathMap

> Index entry: [[Index of Design Patterns#PathMap]].

Preserves the primary portability finding: SSH does not map controller worktrees into a remote VM, and path-bearing argv/hooks must translate consistently.

### Capability re-entry and AuthorizedCommand

> Index entries: [[Index of Design Patterns#Capability re-entry]], [[Index of Design Patterns#AuthorizedCommand]].

Separated because the first is the end-to-end effect path; the second is the type-level domination boundary between authorization and execution.

### Authenticated sandbox binding

> Index entry: [[Index of Design Patterns#Authenticated sandbox binding]].

Kept separate from capability re-entry because the mechanism exists while the principal-binding law does not. This prevents `Emergent` from hiding an open security obligation.

### Provider capability bundle

> Index entry: [[Index of Design Patterns#Provider capability bundle]].

Chosen over `VMBackend` because lifecycle, transport, projection, reachability, and publication fail and test independently, while bundle compatibility prevents arbitrary combinations.

### Provisioning generation and receipt

> Index entry: [[Index of Design Patterns#Provisioning generation and receipt]].

Combines the desired/observed incarnation fence with evidence of privileged phase completion. A process/version field without postconditions would be too weak.

### Harness-home sharing scope

> Index entry: [[Index of Design Patterns#Harness-home sharing scope]].

Chosen instead of “shared projection” because home is authoritative credential/collaboration state with explicit member authority, not a worktree or cache.

### Contamination domain

> Index entry: [[Index of Design Patterns#Contamination domain]].

Chosen to make non-isolation visible. `Shared cache` sounds purely beneficial; contamination names integrity/availability influence across members.

### Git hook re-entry

> Index entry: [[Index of Design Patterns#Git hook re-entry]].

Kept separate from capability re-entry because the control flow reverses direction again inside a host Git effect and has distinct recursion/path/cancellation laws.

### Endpoint exposure

> Index entry: [[Index of Design Patterns#Endpoint exposure]].

Chosen over “port forward” because one service publication spans allocation, runtime proxy, provider transport, final scope, observation, and teardown.

### Idle janitor and desired-state reconciler

> Index entries: [[Index of Design Patterns#Idle janitor]], [[Index of Design Patterns#Desired-state reconciler]].

Separated to preserve maturity honesty. The current loop is useful but lacks the desired records, ownership, leases, and positive health needed by the target.

### Positive storage-health evidence

> Index entry: [[Index of Design Patterns#Positive storage-health evidence]].

Chosen because PVE/NFS/virtiofs makes `ENOENT` ambiguous. The operational consequence—prevent destructive cleanup under unmounted storage—warrants an independent access path.

### Operation lease

> Index entry: [[Index of Design Patterns#Operation lease]].

Chosen because lifecycle races span multiple subsystems. A local file lock around one setup step does not fence aggregate mutation or stale cleanup.

### Trust tiers

> Index entry: [[Index of Design Patterns#Trust tiers]].

Chosen to encode which configuration sources may select host providers/plugins/effects. Repository configuration is intentionally lower authority than host-admin configuration.

## Additional entry-by-entry marginalia

The canonical-term essays above cover the load-bearing families. This table completes the per-entry rationale for narrower access paths rather than leaving them as generated vocabulary.

| Entry | Chosen because | Belongs because omission would hide… |
|---|---|---|
| [[Index of Design Patterns#Accepted-effect audit]] | Host GitHub mutations are meaningful authority. | the asymmetry between full denial logging and absent accepted-effect evidence. |
| [[Index of Design Patterns#Acceleration-independent correctness]] | “Cache is optional” is a behavioral law, not a performance slogan. | the risk that hidden shared state becomes correctness authority. |
| [[Index of Design Patterns#AuthorizedCommand]] | Authorization/execution domination needs a type-level handle. | the raw-argv bypass class. |
| [[Index of Design Patterns#Bundle compatibility]] | Narrow ports can still form invalid combinations. | the cross-port path/reachability contract. |
| [[Index of Design Patterns#Cache ownership]] | Runtime and janitor currently clean adjacent state differently. | the single-owner cleanup rule. |
| [[Index of Design Patterns#Daemon incarnation identity]] | PID reuse is a distinct ownership problem. | a stale daemon record being mistaken for the current process. |
| [[Index of Design Patterns#Desired state]] | Observed resources are not user/controller intent. | the source of legal convergence decisions. |
| [[Index of Design Patterns#Desired-state reconciler]] | It is the target object readers will otherwise conflate with janitor. | desired records, leases, ownership, and contradiction policy. |
| [[Index of Design Patterns#Differential conformance]] | Method-shape compatibility is insufficient for providers. | the behavior evidence needed before plugin extraction. |
| [[Index of Design Patterns#Durable work / disposable infrastructure]] | It governs deletion and recovery. | the core user-work preservation law. |
| [[Index of Design Patterns#Exposure identity and bind scope]] | Publication reach is security authority. | silent widening and orphan listener lifecycle. |
| [[Index of Design Patterns#Generation-stamped readiness]] | Readers may remember the law rather than the bundle/receipt object. | existence-versus-readiness and stale-completion fencing. |
| [[Index of Design Patterns#Hook ephemeral file]] | Git administrative files are not worktree paths. | the established `COMMIT_EDITMSG` behavior and its separate capability class. |
| [[Index of Design Patterns#Host effect authority]] | The bridge grants local and remote side effects, not just Git syntax. | GitHub credential authority and effect-specific policy. |
| [[Index of Design Patterns#Operational tenant]] | “Container” otherwise implies stronger isolation than evidence supports. | the common privileged VM/kernel/home/cache domain. |
| [[Index of Design Patterns#Outer endpoint transport]] | Provider publication is only one primitive. | the ownership boundary between transport and exposure. |
| [[Index of Design Patterns#Outer environment]] | The outer VM is the actual host-isolation boundary. | the distinction from Incus operational tenants. |
| [[Index of Design Patterns#Policy artifact separation]] | Human docs currently carry executable authority rules. | review/versioning debt and unknown-placeholder broadening. |
| [[Index of Design Patterns#Positive storage-health evidence]] | Remote projections make absence ambiguous. | destructive cleanup during an unmounted share. |
| [[Index of Design Patterns#Pre-policy trusted context]] | Policy lookups currently precede `.git` repair. | attacker-influenced repo/remote/stash authorization context. |
| [[Index of Design Patterns#PVE data-placement decision gate]] | It blocks implementation for a concrete reason. | the false belief that SSH or virtiofs alone moves controller worktrees. |
| [[Index of Design Patterns#Trust tiers]] | Config source determines legitimate authority. | repository-controlled host plugin/projection expansion. |
| [[Index of Design Patterns#Workspace identity]] | Includes create several workspaces under one sandbox. | the difference between aggregate ownership and repository selection. |

## Redirect rationale

### Bridge → Capability re-entry

“Bridge” is the user/source term, but it hides identity, path, policy, effect adapters, and audit. Redirecting preserves findability without endorsing the flattened model.

### VM backend / VMService seam → Provider capability bundle

Readers will search these phrases from the original Phase-2 plan. Both redirect to the corrected portability boundary.

### Sandbox is a container → Sandbox aggregate

A deliberate correction. The container is one reconstructable resource; worktree/home/provider/gateway/endpoints remain independent.

### Scoped cache isolation → Contamination domain

A deliberate correction. Scoped paths support semantic cleanup, not ACL enforcement.

### Shared harness home → Harness-home sharing scope

Preserves the familiar implementation phrase while routing to the authority-bearing concept: who shares the credentials/settings and what every member may do. The redirect belongs because “shared home” by itself does not communicate scope or security consequences.

### Cleanup loop → Idle janitor

Uses the current mechanism's honest maturity rather than promoting it to reconciliation.

### Port forwarding → Endpoint exposure

Preserves the CLI term while directing readers to the end-to-end publication object.

### Existence means ready → Provisioning generation and receipt

Indexes the exact false inference demonstrated by the Phase-1 setup failure.

## Maturity rationale

| Entry family | Label | Why |
|---|---|---|
| Split plane, writable projections, durable work, outer environment | Established | Source, E2E, and Phase-1 deployment exercise important runtime paths. |
| Sandbox identity join | Emergent | Naming joins many resources, but identity validation/ownership records are implicit. |
| Capability re-entry | Emergent | Mechanism and policy tests exist; sandbox-bound authentication is open. |
| Provider capability bundle | Emergent | Lima supplies behavior implicitly; the explicit ports and bundle-validation boundary do not exist yet. |
| Generation-stamped readiness | Open correctness obligation | Target law motivated by an observed interrupted setup; not implemented. |
| Harness-home scope | Established | One writable home is intentionally mounted into every container. |
| Shared acceleration contamination | Established | Shared wiring and reuse tests exist; cache-neutral semantics is separately open. |
| Git hook re-entry | Emergent | Wrapper/E2E exist; portable path and re-entrant lifecycle contracts are implicit. |
| Endpoint exposure | Emergent | Multi-hop mechanism exists; ownership/allocation/scope contract is incomplete. |
| Idle janitor | Architecture debt | Heuristic deletion/stop behavior has concrete false-authority/race gaps. |

No entry is labeled Candidate ecosystem pattern yet. Current reusable-looking structures are either still implicit/emergent or lack a sufficiently precise likely comparison target established by this study; this is a judgment about current evidence, not a rule that Candidate always requires a second implementation.

## Reader-situation usability test

1. *“Where is the distinction between editing files and running host Git?”* → [[Index of Design Patterns#Writable projection]] and [[Index of Design Patterns#Capability re-entry]].
2. *“I thought each sandbox was a container.”* → [[Index of Design Patterns#Sandbox is a container]] → [[Index of Design Patterns#Sandbox aggregate]].
3. *“Why isn't `VMBackend.run()` enough for Proxmox?”* → [[Index of Design Patterns#VM backend]] → [[Index of Design Patterns#Provider capability bundle]].
4. *“What maps a path when host and guest roots differ?”* → [[Index of Design Patterns#PathMap]].
5. *“How does one ID connect Git, Incus, cache, and cleanup?”* → [[Index of Design Patterns#Sandbox identity]].
6. *“Can a matching VMID authorize deletion?”* → [[Index of Design Patterns#Ownership attestation]] and [[Research/Software Architecture Garden/locki/README#Architecture debt and open laws|the PVE ownership law]].
7. *“Why did a running container still fail setup?”* → [[Index of Design Patterns#Existence means ready]] → [[Index of Design Patterns#Provisioning generation and receipt]].
8. *“Where is the actual cross-sandbox bridge-key problem?”* → [[Index of Design Patterns#Authenticated sandbox binding]].
9. *“Why not put per-sandbox keys in different shared-home filenames?”* → [[Index of Design Patterns#Harness-home sharing scope]].
10. *“Are scoped caches isolated?”* → [[Index of Design Patterns#Scoped cache isolation]] → [[Index of Design Patterns#Contamination domain]].
11. *“Who owns deleting `scoped/<id>`?”* → [[Index of Design Patterns#Cache ownership]].
12. *“How do original Git hooks run without host authority?”* → [[Index of Design Patterns#Git hook re-entry]].
13. *“Why is port forwarding more than an Incus proxy?”* → [[Index of Design Patterns#Port forwarding]] → [[Index of Design Patterns#Endpoint exposure]].
14. *“How broad is the published service?”* → [[Index of Design Patterns#Exposure identity and bind scope]].
15. *“Why not call the daemon loop a reconciler?”* → [[Index of Design Patterns#Idle janitor]] and [[Index of Design Patterns#Desired-state reconciler]].
16. *“What prevents cleanup during an active hook/provision?”* → [[Index of Design Patterns#Operation lease]].
17. *“Why can missing worktree storage not trigger deletion?”* → [[Index of Design Patterns#Positive storage-health evidence]].
18. *“Which config can load a host provider/plugin?”* → [[Index of Design Patterns#Trust tiers]].
19. *“What proves two providers are substitutes?”* → [[Index of Design Patterns#Differential conformance]].
20. *“Which single list captures every known architecture gap?”* → [[Research/Software Architecture Garden/locki/README#Architecture debt and open laws|Architecture debt and open laws]], then the corresponding canonical index entries.

## Cross-Garden terminology decisions

- `Typed intent, host-owned effect` is a correspondence for capability re-entry, not an equivalence: Locki includes authentication/path/OS authority.
- devctl's process ownership and reconciliation provide comparison vocabulary, not a direct Proxmox resource implementation.
- Sessionstream/Pinocchio generation tokens explain stale completion fencing, not Locki resource identity or authorization.
- Flowkit cache identity explains semantic-key validation, while Locki contamination additionally concerns cross-sandbox integrity/availability.
- PBUI identity discipline supports explicit non-equivalences among sandbox identity, workspace identity, generation, revision, exposure, and lease.

## Validation requirement

Run:

```bash
python3 Research/playbooks/scripts/validate_index_links.py \
  "Research/Software Architecture Garden/locki/Index of Design Patterns.md" \
  "Research/Software Architecture Garden/locki/Index of Design Patterns - Rationale.md" \
  "Research/Software Architecture Garden/locki/README.md"
```

A clean link pass proves only mechanical resolution. The reader-situation test and disappointed-reader test establish editorial usefulness.

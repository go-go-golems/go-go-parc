---
title: Makera Z1 Control — Controller Ownership, Adapter Cutover and Hardware Qualification
aliases:
  - Makera Z1 P3 P4 P5 technical report
  - Z1 controller ownership and cutover
  - single-owner CNC controller hardware qualification
tags:
  - project
  - cnc
  - go
  - concurrency
  - software-architecture
  - safety
status: active
type: project
created: 2026-09-14
project_started: 2026-08-11
repo: /home/manuel/workspaces/2026-08-11/cnc-control-dropcut/dropcut-studio
branch: task/cnc-control-dropcut
implementation_commit: 70141f2
source_ticket: MZ1-016
scope: P3 controller ownership, P4 adapter cutover with owner deletion, and P5 staged hardware qualification of the changed paths
implementation_status: Controller core, adapter cutover and the first P5 batches are implemented and machine-qualified; accessories, filesystem, stored-program lifecycle and the hold-release drill remain unqualified
---

# Makera Z1 Control — Controller Ownership, Adapter Cutover and Hardware Qualification

A motion command has a shorter lifetime than the motion it requests. The host writes a jog, the axis travels after the write returns, and the HTTP request that submitted the jog may time out or close before the axis stops. A controller for such a machine must keep three lifetimes separate — the request, the software worker that performs the write, and the physical operation — and it must decide what each of them proves. This report explains the three implementation phases of MZ1-016 that followed the protocol work described in the previous report: the controller that owns operations, the adapter cutover that deleted every other execution path, and the staged hardware qualification that exercised the result on the installed machine.

The report follows the actual implementation through concrete events, including two that were unplanned: a deliberate limit-switch approach that the machine's soft limits stopped before any switch was struck, and a spindle-start refusal caused by an engaged emergency stop, which exposed an evidence gap that was then reproduced, fixed and re-verified on the machine. Every machine claim cites an archived receipt. Where a property is only designed or only tested offline, the text says so.

> [!summary]
> - P3 built a single-owner controller whose operation records resolve on concrete machine evidence, never on request or worker completion alone.
> - P4 cut the HTTP and native adapters over to that controller and deleted the legacy execution stack — 4,238 lines — with source-search proofs that no enabling route bypasses controller admission.
> - P5 qualification ran under a stop-and-confirm operator protocol: read-only surfaces, homing, bounded moves, a soft-limit trip, E-stop refusal, evidence-gated alarm unlock, and spindle start/stop all passed with receipts.
> - Two evidence-chain defects found on the machine were fixed and re-verified live: alarm-affected operations now carry the halt reason, and CLI errors no longer double-wrap.
> - Four capabilities were deleted from scope by explicit decision rather than deferred: park, generic recovery, host-side inactive-WCS management, and continuous jog.

## 1. The problem the controller solves

The protocol foundation from P2 established who owns bytes, replies and observations. What it did not establish is who owns an *operation*. Consider the sequence an operator triggers by pressing a jog button on the control page:

1. The browser POSTs a jog request.
2. The host admits the request, checks fresh machine state, writes the jog command.
3. The firmware accepts the command and starts moving the axis.
4. The browser request times out; the operator closes the tab.

At step 4, the previous architecture answered three questions incorrectly. It treated the request timeout as an outcome — but the axis is still moving. It allowed the next request to dial a fresh connection and submit new motion — but nothing established that the first jog finished. It reported "sent" as success — but a written byte proves only that the transport accepted it.

The controller's contract inverts these answers:

- The request's lifetime covers admission only. A generated operation ID remains queryable after the requester leaves.
- The operation resolves when machine evidence satisfies a concrete, operation-specific predicate — or never, if uncertainty prevents resolution.
- An unresolved operation (`unknown`, `held`) blocks all new enabling work, because deleting the record would convert loss of control into permission.

## 2. The layer model

The final architecture assigns each concern to one package, with one-directional dependencies:

```text
browser page / HTTP-default CLI   native CLI commands
        \                             /
   internal/httpapi            typed runners (action / stop)
            \                     /
              internal/app  (one owned session)
                     |
              pkg/controller  (coordinator, operations, evidence)
                     |
               ProtocolDriver
                     |
        pkg/makera/protocol  (reader, bounded writer,
                     |        one transaction collector,
        pkg/makera/stock     observation feed)
             wire framing — transport

camera / UDP discovery / read-only capture   (preserved services,
                                              no command path)
```

| Layer | Owns | Must never do |
|---|---|---|
| Transport | Connection, deadlines, bounded writes | Interpret frames |
| Wire | Framing, CRC, packet types, drop counting | Route or decode semantics |
| Protocol | Reader, bounded writer, transaction, observation feed | Admit application operations |
| Stock | Firmware semantics: report grammars, halt bands, encodings | Hold state |
| Controller | Operation records, admission, evidence, cancellation | Touch a socket |
| App | Constructing and closing the one session | Reconnect, replay, expose raw commands |
| Adapters | Decode, authenticate, translate, encode responses | Own machine pointers or locks |

`internal/app` enforces the single-connection constraint. Its constructor dials exactly once, assembles the stack, assigns a fresh random observation generation so stale cursors from a previous session can never alias, and exposes only the controller, the driver's reviewed read-only queries, and decoder drop counts. There is no redial. A transport loss leaves the session faulted until the process restarts; restarting the server is documented as a lifecycle action, never as a way to stop the machine.

The camera and discovery services survive the cutover unchanged because they never execute machine commands: the camera bridges its own connection to the machine's WiFi module, and discovery passively enumerates the LAN.

## 3. Transaction completion is not machine evidence

The protocol separates two data paths that the legacy client merged behind one mutex.

**The transaction collector** owns one text exchange at a time. A command and its exact echo sentinel are written as one batch; the collector accumulates reply records until the sentinel arrives. If the write fails, the reply overruns its bounds, or the window expires, the session is quarantined: a lost reply cannot distinguish "the firmware never saw the command" from "the firmware saw it and the reply was lost", so no component retries into that uncertainty.

**The observation feed** runs independently. Status replies to the realtime `?` query carry a session generation and a monotonic sequence, and any number of consumers can read them without consuming each other's evidence. A homing cycle can occupy the transaction collector for two minutes while the feed continues to publish machine state.

The controller defines completion as predicates over the feed — each one bounded to what the firmware can actually report:

| Operation family | Completion evidence |
|---|---|
| Finite jog, positioning | Three fresh `Idle`/zero-feed samples with every selected axis within 0.02 mm of target; work-frame completion additionally requires the machine-minus-work offset to be unchanged |
| Homing | Observed `Home` state after dispatch, then three stable `Idle`/zero-feed/zero-RPM samples; the −1,−1,−1 rest position is never accepted as homing proof |
| Spindle start | Three fresh `Run` samples with RPM within 5 % (minimum 50 RPM) of the request |
| Spindle stop | A bounded window of fresh samples at or below 50 RPM; one Ctrl-X software halt escalation only if M5 evidence fails |
| Job play | Source Player acceptance; the operation stays running — status `Idle` never completes a program |
| Job inspection | Only the Player's own "Not currently playing" report resolves the job, recorded as *ended, machining success unverified* |
| Accessory output | Dispatch only; the record states that physical output state is unverified |

No rule engine or configurable evidence language exists. Each predicate is an ordinary Go function over the observation type, and the operation record's evidence text states what the predicate proved — and what it did not.

## 4. One coordinator, three lifetimes

All operation state is mutated by a single coordinator goroutine. Requests, worker results, observations and timer events arrive as typed values; no transition performs I/O. Blocking work runs in bounded workers, with two fixed, identity-checked slots (command and review) holding the owning operation's ID. A completion event releases a slot only when both its worker token and its operation ID match.

The three lifetimes are visible in one cancelled jog:

```text
request:    admitted → ID published → caller may leave
worker:     preflight → write → posts result → slot released
operation:  preparing → dispatching → observing → resolved
```

The worker finishing establishes that no further software I/O will come from that worker. The operation resolving establishes the machine reached a defined state. Neither substitutes for the other: a resolved operation can briefly have a draining worker, and a finished worker never implies the target was reached. The test suite pins this with stale-result races — a completion event from an older worker invocation must not release a newer one.

Because the request context is only an admission scope, the HTTP contract gained `operation_id` and `phase` fields. A request window that ends while an operation continues returns 202 with the operation identity; the response never implies the command did not run.

## 5. Uncertainty, alarms, and the evidence found on the machine

The qualification produced the most instructive finding of the project, and it began with a diagnostic error on the operator's part that the software then amplified.

### 5.1 The event

During the spindle-start test, the operator had engaged the physical emergency stop before the command started. The command failed in under a second and printed:

```text
z1ctl: observation stream fault: observation stream fault
```

Two defects hide in that line. The text names no machine fact — the machine was latched in `Alarm` with halt reason 13, and learning that required a separate diagnostic. And the text appears twice, because the CLI wrapped the operation's error string around a wait error that already carried it.

### 5.2 A wrong inference, and how it was corrected

The first analysis of this failure inferred from the error string that the `M3` command had been dispatched. The operator then supplied the decisive fact — the E-stop was engaged beforehand — and a deliberate reproduction confirmed it: the controller had observed `Alarm`, faulted the session, and cancelled the operation **before dispatch**. No `M3` byte was sent, the RPM never left zero, and the refusal completed in about one second.

The inference failed for a structural reason worth recording: the string `observation stream fault` is written on two different coordinator paths — cancellation of a still-preparing operation (nothing dispatched) and the hold of an already-dispatched operation. Shared strings across paths are not evidence of a path. The durable fix was not to reword the string but to put the machine fact into the operation record, so no inference is needed.

### 5.3 The fixes

The alarm branch of the coordinator now builds the concrete evidence text and applies it whichever way the fault's intervention resolved the operation:

```go
note := alarmFaultText
if o.HaltReasonValid {
    if text, _, known := stock.HaltReason(o.HaltReason); known {
        note = fmt.Sprintf("%s (halt reason %d: %s)", alarmFaultText, o.HaltReason, text)
    }
}
active := s.active
c.event(s, event{kind: eventFault, err: errors.New(alarmFaultText)})
if active != nil {
    op := &s.snapshot.Operations[active.index]
    switch op.Phase {
    case Cancelled: // preparing: nothing was dispatched
        op.Error = note + "; cancelled before dispatch"
    case Dispatching, HoldRequested, Observing: // bytes may have moved
        op.Phase = Unknown
        op.Error = note + "; outcome unresolved"
        active.cancel()
        s.active = nil
    }
}
```

Two rules are encoded here. First, an alarmed machine cannot reach any operation's target, so the alarm is terminal evidence: a dispatched operation resolves immediately as `unknown` — bytes may have moved, the target was not reached — instead of lingering until its 30-second operation bound. Second, the dispatched/not-dispatched distinction is preserved in the error text: a preparing operation cancelled by an alarm says `cancelled before dispatch`, which proves nothing was sent. The same reproduction after the fix printed, in 1.1 seconds:

```text
z1ctl: machine reports Alarm (halt reason 13: emergency stop button pressed); cancelled before dispatch
```

Other fault kinds — stale telemetry, generation mismatch, transport loss — carry no machine fact and keep the deadline path. This boundary keeps alarm resolution from becoming a generic "faults resolve operations" rule, which the project explicitly rejected.

## 6. The recovery loop: unlock as a typed operation

The firmware latches an alarm on emergency stop, soft-limit trips and probe faults, and refuses motion until the alarm clears. The stock halt table divides causes into recovery bands:

| Band | Examples | Required recovery |
|---|---|---|
| ≤ 20 | 10 soft limit, 13 emergency stop | Unlock (`$X`) is sufficient |
| 21–40 | 21 hard limit, motor errors | Reset |
| > 40 | 41 spindle alarm | Power cycle |

An `Alarm` observation faults the controller session, so unlock cannot be an ordinary admitted operation — it would be blocked by the very fault it exists to clear. It is independently admitted, with its own evidence chain: fresh `Alarm` status whose halt reason lies in the unlock band, fresh emergency-stop-clear and closed-cover diagnostics, exactly one `$X`, then a bounded observation of the machine leaving `Alarm` (two fresh non-Alarm reports). A refusal before dispatch resolves and frees the attempt; a failure after bytes were sent stays `unknown` and retains its blocker, so a repeated request returns the existing ID rather than resending `$X`. Success clears exactly the alarm-caused session fault; held sessions keep their reconciliation requirement, and every transport fault survives.

The qualification exercised this loop twice on the machine — once for the soft-limit alarm (Section 7) and once for the E-stop alarm — with receipts of this shape:

```json
{
  "cleared": true,
  "halt_meaning": "emergency stop button pressed",
  "halt_reason": 13,
  "operation_id": "d8c0e78db60dc9a487a77742b48a37ac",
  "phase": "succeeded",
  "state_after": "Idle"
}
```

The cycle-start release (`~`) followed the same design discipline in the opposite direction: it is an enabling write, so it requires observed `Hold` state plus interlock evidence, reports dispatch only ("resumption unverified"), and never clears the held session's reconciliation requirement.

## 7. Hardware qualification: method and results

Qualification ran under a fixed operator protocol: each batch was described, stopped, and executed only after a fresh go-ahead, with the operator at the machine and the physical E-stop authoritative over every software action. Every command's raw output, operation row and post-state read is archived in the ticket workspace.

| Batch | Scope | Result on the machine |
|---|---|---|
| 1 | Read-only native commands; `serve` with all read-only HTTP endpoints | All green; a known SD file's digest matched a 2026-08 hardware record, cross-validating the new digest path; one live-found HTTP response-typing bug fixed |
| 2 | Homing; six bounded machine-coordinate moves; slow jog into the limit | Homing completed with observed `Home`→`Idle` evidence; all moves completed at target; the jog tripped the **soft limit (H:10) with no physical switch impact**, position unchanged; unlock recovered to `Idle` |
| 2 (remainder) | Work-coordinate move; active-WCS zeroing through the serve route | Work move completed at target in the work frame; zeroing produced WPos X exactly 0.000 with machine position unchanged — the first live mutating HTTP route through the new stack |
| 3 | Spindle on 10 000 RPM; spindle off | Start completed with observed-RPM evidence in 9.2 s; stop completed with M5 plus bounded evidence in 3.3 s, no escalation; E-stop-engaged start refusal reproduced twice; halt-reason evidence fix verified live |

The limit test measured the machine as much as the software. The axis rested about 2 mm from its maximum switch; a jog at 10 % of axis maximum speed toward the switch tripped the firmware's soft limit in planning, latched `H:10`, and left the position unchanged. The physical switch was never struck. The stock configuration therefore protects its own switches; what the qualification established is that the host reports the event honestly — alarm latched, unlock-eligible band identified, evidence-gated recovery to `Idle` — and that the operator sees the halt reason within about one second.

## 8. The cutover: deleting the second owner

An adapter cutover in this design is the removal of every alternative path to the machine, not a rewrite of the handlers. The work proceeded in committed increments:

1. **Contract relocation.** The protobuf payloads moved out of the doomed web package. Responses gained `operation_id` and `phase`; the zeroing request lost its inactive-work-system selector and gained the mandatory Z tool-offset acknowledgement; play and resume gained the operator's `homed` declaration, because stock telemetry cannot prove homing and the firmware itself refuses play on an unhomed machine.
2. **HTTP cutover.** `internal/httpapi` serves every route through the owned session. The security posture — host validation against DNS rebinding, same-origin checks, token enforcement beyond loopback — was ported verbatim. The old package with its broad callback lock and its second admission flag was deleted, not wrapped.
3. **Native CLI cutover.** Two runners translate typed intents: one for enabling actions (`--dry-run` renders the intent's exact command text without connecting; `--confirm` required; `--homed` declares homing), one for stops, which never require confirmation. Read-only commands use the driver's reviewed queries; filesystem mutations and transfers became controller operations.
4. **Owner deletion.** The legacy client, its motion renderer (including a source-corrected but now-deleted G53 ordering bug), its transfer mode, preflight and job paths were removed — 4,238 lines in one commit — leaving camera, discovery, the read-only capture harness, the offline codec and the raw-command risk classification.

The exit condition was a source-search proof, not a test pass. No reference to the deleted client remains. The raw command surface exists once, on the owned session, and is reachable only from the explicit experimental `exec` command, which refuses motion-class text before connecting. The HTTP layer imports the legacy package for the camera service only. Every enabling route crosses controller admission; there is no second execution owner to drift.

Two behavior changes were made openly rather than silently: `serve` now fails to start when the machine is unreachable, because no per-request redial exists to hide behind; and filesystem mutations and uploads require fresh idle admission, where the old client ran them in any machine state. Both are stated in the served page's own help text.

## 9. What was deleted from scope, and why

Four capabilities were removed by explicit decision during the work, each with a recorded reason and an explicit refusal message in the software:

- **Park / fixed safe-Z.** The historical host coordinates (`Z-3`, then `X-197 Y-206`) conflict with the only retained example file (`X-295 Y-205`, then `Z-50`), and the bytes of the installed machine's own pack file were never retained in evidence. Unverifiable coordinates combined with unknown fixture clearance do not become a controller action. The legacy command was deleted at cutover.
- **Generic recovery.** A reusable acknowledge/retry/reconnect/replay subsystem would add state machinery while remaining unable to prove output state or prior-command disposition. Uncertain outcomes stay blockers; unlock and cycle-start are narrow typed operations with their own evidence chains.
- **Host-side inactive-WCS management.** No current workflow requires the host to select or edit a work coordinate system that is not the firmware's active one. Stored programs select their own WCS in their own G-code, and the stock P-slot mapping came from community folklore rather than verified source.
- **Continuous jog and spindle PID tuning.** Continuous-jog semantics remain deferred for stock firmware; the routes return an explicit not-implemented response and the server-held jog machinery was deleted. PID tuning (`M958`) is a maintenance write outside the reviewed catalogue and is refused with a pointer to the experimental `exec` surface.

The common rule: a capability enters only with a concrete evidence source and a real consumer. A scope decision is enforced by deletion or refusal, never by a silent downgrade or a hidden fallback route.

## 10. Complexity accounting

The refactor's size is best measured by what it did not add. The controller implements its coordinator, evidence predicates, cancellation and recovery without a scheduler, a workflow engine, an evidence DSL, leases, request deduplication or a durable journal. The two worker slots exist because stale-result and cancellation races were demonstrated in tests, not because an activity framework was wanted. Public subscriptions are one bounded broadcast buffer with copied snapshots and explicit gap errors.

Validation concentrated where behavior changed: per-operation race scenarios, byte-level protocol fixtures over in-memory pipes, and the staged machine batches of Section 7. The full module — 13 test packages under the race detector, the embedded frontend's type check and 34 component tests, protobuf lint, rendered help — passes offline. The embedded help topic `z1ctl help z1-controller-core` documents the design baseline in-repo for contributors.

## 11. Status and remaining work

Implemented, committed and machine-qualified at repository commit `70141f2`: the layered protocol and controller, the complete adapter cutover with owner deletion, and the read-only, motion, limit, alarm-recovery and spindle/spindle-stop batches. Two evidence-chain defects found on the machine were fixed with race-tested commits and re-verified live.

Not yet exercised on the machine: accessory outputs (dispatch-only by design), the filesystem scratch cycle and file transfers, the benign stored-program lifecycle (play → progress → suspend → resume → abort), and the hold → cycle-start release drill. These follow the same stop-and-confirm protocol. Downstream, the MZ1-015 embedded-JavaScript work receives its seam as-is: a Goja facade over the controller registers operations, awaits results through operation IDs, and uses the urgent hold path. The concurrency questions that runtime would otherwise raise were answered by this refactor rather than left to it.

## 12. Evidence and source navigation

- Ticket workspace: `ttmp/2026/09/13/MZ1-016--controller-architecture-refactor-before-embedded-scripting/` in the repository — diary (Steps 38–48 cover this report's phases), design guide, changelog, and all hardware receipts under `reference/` (batches numbered 17–22).
- Controller core: `makera-z1-cli/pkg/controller/` — `coordinator.go` (alarm branch), `unlock.go` (evidence-gated unlock), `actions.go`, `types.go`; the embedded help topic `pkg/doc/topics/controller-core.md`.
- Session and adapters: `internal/app/app.go`, `internal/httpapi/` (server, commands, readonly), `cmd/z1ctl/cmds/motionrun.go` (the two runners).
- Protocol: `pkg/makera/protocol/` — `transaction.go` (sentinel collector and quarantine), `connection.go`, `writer.go`; stock halt bands in `pkg/makera/stock/halt.go`.
- Key commits: `f88ed30` (app session), `3f17f01` (unlock/cycle-start), `b6bc28a` (contract), `e44f2c2` (HTTP cutover), `6a04c91` (CLI cutover), `3e61460` (owner deletion), `0dc4e30` (alarm evidence fixes), `70141f2` (batch 3 receipts).

## Related notes

- [[Projects/2026/09/13/PROJ - Makera Z1 Control - P1 and P2 Protocol Ownership and Hardware Evidence|PROJ — Makera Z1 Control: P1 and P2 Protocol Ownership and Hardware Evidence]]
- [[Projects/2026/09/13/PROJ - Makera Z1 Control - Three Refactors for Authority Evidence and Browser Intent|PROJ — Makera Z1 Control: Three Refactors for Authority, Evidence and Browser Intent]]
- [[Projects/2026/09/12/PROJ - Makera Z1 Control - Protocol Hardening and Spindle Stop Safety|PROJ — Makera Z1 Control: Protocol Hardening and Spindle Stop Safety]]
- [[Projects/2026/09/12/ARTICLE - Makera Z1 Stock Firmware - Source-Grounded Command and Telemetry Reference|ARTICLE — Makera Z1 Stock Firmware: Source-Grounded Command and Telemetry Reference]]
- [[Research/Software Architecture Garden/dropcut-studio/designs/09 - Single-Owner CNC Controller - Worker Ownership Separate from Operation Evidence|Garden 09 — Single-Owner CNC Controller]]
- [[Research/Software Architecture Garden/dropcut-studio/designs/08 - Bounded Cursor Broadcast - Independent Readers with Explicit Gaps|Garden 08 — Bounded Cursor Broadcast]]

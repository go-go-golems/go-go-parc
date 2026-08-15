---
title: Dead-Man Keepalive — Fail-Safe Motion by Causal Inversion
aliases:
  - dead-man's switch motion
  - heartbeat-gated actuation
  - omission-as-safe-state
  - causal-inverted liveness
  - keepalive-gated continuous action
status: candidate
type: architecture-garden-design
created: 2026-08-14
analyzed: 2026-08-14
repository: /home/manuel/workspaces/2026-08-11/cnc-control-dropcut/dropcut-studio
repository_remote: git@github.com:wesen/dropcut-studio
repository_branch: task/cnc-control-dropcut
repository_commit: 5f33ba1
source_ticket: /home/manuel/workspaces/2026-08-11/cnc-control-dropcut/dropcut-studio/ttmp/2026/08/14/MZ1-005--cnc-to-z1ctl-command-control-protocol-wire-level-study-and-correct-design-theory
tags:
  - architecture-garden
  - dropcut-studio
  - command-control
  - safety
  - liveness
  - fail-safe
  - real-time
  - go
related_files:
  - makera-z1-cli/pkg/makera/motion.go
  - makera-z1-cli/pkg/makera/client.go
related_notes:
  - "[[Research/Software Architecture Garden/dropcut-studio/README|Architecture Garden — dropcut-studio]]"
  - "[[Research/Software Architecture Garden/dropcut-studio/designs/01 - Sentinel-Delimited Command Completion over an Ordered Line Queue|01 — Sentinel-Delimited Command Completion over an Ordered Line Queue]]"
  - "[[Research/Software Architecture Garden/dropcut-studio/designs/02 - Latched Safety Channel over a Lossy Inbound Queue|02 — Latched Safety Channel over a Lossy Inbound Queue]]"
  - "[[Research/Software Architecture Garden/README|Software Architecture Garden]]"
---

# Dead-Man Keepalive — Fail-Safe Motion by Causal Inversion

This note records a reusable pattern for **continuous, potentially hazardous
action that must stop the instant its operator stops being engaged**: a host
emits a periodic *keepalive* (heartbeat) to a device, and the device
**moves only while keepalives keep arriving**, stopping on its own when they
cease. The safe state is reached by *omission*, and omission is the easy
failure mode — so the design bets on the failure that is most likely rather
than the one that is most convenient. It is the strongest safety pattern
available in a command-control link because its guarantee depends on the
controller **stopping**, not on it **behaving correctly**.

The pattern was observed in `z1ctl`'s continuous-jog session
(`makera-z1-cli/pkg/makera/motion.go`), where the Makera Z1 firmware stops the
axis when keepalives cease. Crucially, `z1ctl` implements it in *two* modes — a
proper one and a subtly weaker one — which makes it an unusually good
specimen: the proper mode is the pattern; the weaker mode is the cautionary
tale that clarifies *why* the proper mode is proper.

> [!summary]
> - Continuous hazardous action is gated by a **keepalive heartbeat**: the
>   device acts while heartbeats arrive and stops when they cease. The safe
>   state is the *absence* of the signal, reached by the easy failure.
> - The proper version places the **causal origin of each heartbeat with the
>   human operator** (one button-press → one heartbeat, forwarded 1:1), so no
>   software timer exists that could keep motion alive without a human. The
>   device's own watchdog enforces the bound; the host cannot violate it.
> - The guarantee is a **causally-inverted liveness** property: the normal
>   reading is "motion is alive *while* heartbeats flow"; the safety reading
>   is "motion is dead *unless* heartbeats flow." It is a **fail-safe** design
>   because the safe state is reached by *omission*, the most likely failure.
> - Time bounds it: the host must emit a heartbeat strictly before the
>   device's watchdog times out — `τ_k + Δ_clock + Δ_network < τ_f` — a
>   real-time schedulability condition. The proper pattern owns the bound on
>   the *device* side, so a hung/crashed host cannot violate it.
> - Do not use a host-side timer that emits heartbeats on its own schedule
>   when a human is the intended dead-man: a crashed UI then leaves a live
>   process timer still feeding the device. Do not use it for actions whose
>   safe state is "completed" rather than "stopped" (a one-shot move is not a
>   dead-man action).

## Why this note exists

The sentinel pattern (entry 01) and the latched-safety-channel pattern (entry
02) are both *fix* patterns — they document the proper design and use `z1ctl`
as the defect. The dead-man jog is the opposite: it is the one place `z1ctl`
is **already correct**, and the review itself names it "the strongest
guarantee in this system." Recording it does two things: it captures a
genuinely reusable fail-safe pattern, and it uses `z1ctl`'s two modes to show
the boundary between the proper pattern and its most seductive near-miss. The
proper version is the pattern; the near-miss is the cautionary section.

## Pattern statement

> **Law.** A continuous, hazardous action is gated by a keepalive heartbeat
> emitted from the **operator's causal presence**: the device acts while
> heartbeats arrive and stops on its own when they cease. The safe state
> (stopped) is reached by *omission* — the absence of heartbeats — which is
> the most likely failure, so the design fails safe. The device's own
> watchdog enforces the stop bound (`τ_f`); the host cannot keep motion alive
> by any correct behavior, only by continued heartbeats. The host must emit a
> heartbeat strictly before the watchdog fires: `τ_k + Δ_clock + Δ_network <
> τ_f`. Stop is an out-of-band, always-admissible action that never waits on
> the heartbeat or the action it gates.

The pattern deliberately does **not** promise: that motion started when the
first heartbeat arrived (the start command is a separate, one-shot admit);
that the host can *force* a stop faster than `τ_f` (it can only cease
heartbeats and let the watchdog fire, plus optionally send an explicit stop);
that the heartbeat proves the operator is *attentive* (it proves only that
*something* is emitting it — see the near-miss); or that the action is
correct, only that it is bounded in time by a live human's continued
engagement.

## Concrete architecture

`z1ctl`'s continuous jog starts an axis moving and then emits a keepalive
"digram" (the realtime status byte `?` plus the Makera jog-keep byte `0x1A`)
every `τ_k = 200ms`. The firmware moves while keepalives arrive and stops the
axis when they cease after its own watchdog `τ_f`. Stop suppresses keepalives
**first**, then sends an explicit stop byte (`0x19`), then awaits the
firmware's `^Y` acknowledgement — but the comment is explicit that even if
the stop byte never lands, "the moment keepalives ceased, the firmware's
dead-man guaranteed the axis stops."

```mermaid
sequenceDiagram
    participant H as Host (operator presence)
    participant D as Device (firmware watchdog)
    H->>D: start continuous jog (one-shot admit)
    loop every τ_k while operator engaged
        H->>D: keepalive digram (? + 0x1A)
        D->>D: reset watchdog; keep moving
    end
    Note over H,D: operator releases / UI crashes / process dies
    Note over D: no keepalive for τ_f
    D->>D: watchdog fires -> STOP (safe by omission)
```

Two modes exist, and the difference is the whole lesson:

- **Manual mode (`JogStartManual`)** — the *proper* pattern. Each protocol
  keepalive is **caused by** a browser keepalive from a held button, forwarded
  1:1 by the server. "When the calls stop — released button, hidden tab,
  crashed browser — the firmware's own dead-man stops the axis; nothing on the
  server needs to notice for the machine to be safe." No server-side timer
  exists that could keep motion alive without a human.
- **Auto mode (`JogStart`)** — the *near-miss*. The host process emits
  keepalives on its own `time.Ticker` every 200ms. "The caller's liveness is
  the dead-man, which is right for the CLI, where the process holding the
  terminal is the held button." This is correct *only when the process IS
  the human* (a CLI run from a terminal). It is wrong when a UI front-end
  drives a long-lived backend process: a crashed/frozen UI leaves the backend
  timer still feeding the device, and the axis keeps moving with no human
  engaged.

## Implementation details

The keepalive and its interval (`makera-z1-cli/pkg/makera/motion.go`):

```go
// jogKeepaliveInterval matches the reference controller's status-poll cadence
// while jogging. The firmware stops the axis when keepalives cease — that is
// the dead-man property, and it is the strongest guarantee in this system
// because it depends on our software STOPPING, not on it behaving correctly.
const jogKeepaliveInterval = 200 * time.Millisecond
```

The proper (manual) mode forwards one heartbeat per human action:

```go
// JogStartManual: keepalives the CALLER emits by calling Keepalive — one call,
// one ?+0x1A write, forwarded 1:1. ... each protocol keepalive is CAUSED by a
// browser keepalive from a held button, so no software timer exists that
// could keep motion alive without a human.
func (c *Client) JogStartManual(...) (*JogSession, error) { return c.jogStart(..., false) }

func (s *JogSession) Keepalive() error {
    if s.stopping.Load() { return errors.New("jog is stopping; keepalive refused so it cannot fight the stop") }
    return s.c.write(s.c.proto.EncodeRealtime(RealtimeStatus, RealtimeJogKeep))
}
```

The near-miss (auto) mode runs a host timer:

```go
func (c *Client) JogStart(...) (*JogSession, error) { return c.jogStart(..., true) }

func (s *JogSession) keepaliveLoop(ctx context.Context) {
    defer close(s.done)
    tick := time.NewTicker(jogKeepaliveInterval)
    for {
        select {
        case <-ctx.Done(): return
        case <-tick.C:
            if err := s.c.write(s.c.proto.EncodeRealtime(RealtimeStatus, RealtimeJogKeep)); err != nil {
                // ceasing keepalives IS the safe failure
                return
            }
        }
    }
}
```

Three details are load-bearing for the proper pattern:

1. **Heartbeats are emitted in one write** (`? + 0x1A` together). The comment
   warns that splitting them "races other traffic and leaves orphaned bytes in
   the firmware's command buffer" — atomicity of the keepalive is a
   correctness requirement, not an optimization.
2. **A write error stops the heartbeat loop immediately.** "Ceasing
   keepalives IS the safe failure, because the firmware then stops the axis."
   The loop fails *toward* the safe state.
3. **Stop suppresses keepalives first** (`stopping.Store(true); cancel(); <-s.done`),
   *then* sends the stop byte, *then* awaits ack — so a late keepalive can
   never "fight the stop." Ordering is the invariant: suppress → stop → ack,
   and even if stop/ack fail, suppression alone is sufficient.

## Behavioral contract

**Guaranteed (proper mode):**
- The device moves only while heartbeats flow; it stops within `τ_f` of the
  last heartbeat, by the device's own watchdog — regardless of host state.
- A crashed/hung host, a released button, a hidden tab, a dead network link
  all converge to the same outcome: no heartbeat → stop, within `τ_f`.
- Stop is out-of-band and always admissible; it never waits on the heartbeat.

**Not guaranteed:**
- That motion started the instant the first heartbeat arrived (start is a
  separate admit).
- That the host can force a stop faster than `τ_f` (only cease + optionally
  send an explicit stop; the watchdog bound is the floor).
- That the heartbeat proves operator *attentiveness* — only that its causal
  source (button or timer) is live.
- That the action is correct, only that it is time-bounded by continued
  engagement.

## Mathematical / CS foundations

### Causal inversion: liveness read backwards

The normal liveness reading of a heartbeat is: *"the action is alive **while**
heartbeats flow."* The safety reading inverts the causation: *"the action is
dead **unless** heartbeats flow."* Formally, where `◇` is "eventually" and
`□` is "always":

```
Normal (liveness):   heartbeat ⟶ action continues
Inverted (safety):   ¬heartbeat  ⟹ ◇_{≤τ_f} (action stopped)
```

The inverted form is a **bounded liveness** property with the bound owned by
the **device**, not the host: `◇_{≤τ_f} (stopped)` holds *unconditionally* once
heartbeats cease, because `τ_f` is enforced by the firmware's watchdog, not by
the host's cooperation. This is the strongest form of bounded liveness — a
liveness property whose bound is owned by the *opposite* party, so the host
cannot violate it by any correct behavior, only by continued heartbeats. (See
design entry 02, §6.9, on bounded liveness; the dead-man is the canonical case
where the bound is device-owned.)

### Fail-safe: safe state by omission

A system is **fail-safe** if its safe state is reached by the most likely
failure mode. Here the most likely failure is **omission** (a missed
heartbeat: dropped packet, hung process, dead UI, cut network), and the safe
state (stopped) is exactly what omission produces. Contrast with
**fail-active** designs, where the safe state requires a *correct* action
(send a stop), and the most likely failure (omission) leaves the action
running. The dead-man pattern is fail-safe because it bets on omission:

```
P(safe | omission)  = 1      (omission → stop, by watchdog)
P(safe | commission) = depends on correct stop logic
```

Since `P(omission) ≫ P(correct commission)` in real systems, the expected
safety is dominated by the fail-safe term. This is the quantitative statement
of "depends on our software stopping, not on it behaving correctly."

### Real-time schedulability of the heartbeat

The heartbeat is a **periodic real-time task** with period `τ_k` and a
relative deadline `D = τ_f − Δ_clock − Δ_network`. Schedulability requires
the host's emitter to never be blocked longer than `D`:

```
τ_k + Δ_clock + Δ_network < τ_f       (keepalive beats the watchdog)
```

In `z1ctl`, `τ_k = 200ms`, `τ_f` is firmware-owned, and the keepalive loop runs
in its **own goroutine** so a 15s command exchange on another path cannot
starve it. That is the correct application of real-time scheduling theory:
the heartbeat is decoupled from the command path by concurrency, so the
deadline holds under worst-case command load. The proper (manual) mode is
*even stronger*: the heartbeat's causal source is the human, so the
schedulability condition reduces to "the human keeps pressing" — which is
exactly the engagement the dead-man is meant to detect.

### The near-miss as a model-theoretic distinction

The auto mode is not *incorrect* in a closed system where `process == human`
(a CLI holding a terminal). It is incorrect in an open system where a UI
front-end drives a backend process, because the **causal origin** of the
heartbeat shifts from the human to the host. In modal-logic terms:

- **Proper:** `□(heartbeat ⟸ human_engaged)` — heartbeat *implies* human
  engaged (each heartbeat is caused by one).
- **Near-miss:** `□(heartbeat ⟹ process_alive)` but **not**
  `□(heartbeat ⟹ human_engaged)` — a live process can emit heartbeats with
  a dead/disengaged human.

The near-miss preserves *liveness* (process alive → heartbeat) but breaks
the *safety correspondence* (heartbeat ↔ human). It is the same class of error
as the sentinel's "delimiter mistaken for identifier" (entry 01): a mechanism
that satisfies a *weaker* property is mistaken for one that satisfies the
*stronger* one. The proper pattern keeps the strong correspondence by making
the human the sole causal source.

## Design-pattern vocabulary

- **Dead-man's switch** — the physical archetype: a spring-loaded switch that
  releases (safe state) unless continuously held. The heartbeat is the "hold";
  omission is the "release." The original is fail-safe by spring physics; the
  software version replicates it by watchdog.
- **Heartbeat / watchdog timer** — the implementation pair: a periodic
  "I'm alive" signal and a timer that fires (to the safe state) on its
  absence. The dead-man pattern is a heartbeat whose safe-state-on-timeout is
  *stop the action*, and whose "I'm alive" is *the operator is engaged*.
- **Fail-safe / fail-to-safe-state** — the safety-engineering property; here
  the safe state is reached by omission (the easy failure).
- **Watchdog / kick** — embedded-systems idiom; the dead-man is a watchdog
  whose timeout action is "cease the gated action" rather than "reset the
  system."
- **Lease / lease renewal** — the distributed-systems analogue: a grant of
  authority that expires unless renewed. The dead-man is a lease on motion
  with a very short renewal period (`τ_k`), expiring to "stopped."
- **Causal inversion / contrapositive liveness** — the modal-logic framing:
  the safety property is the contrapositive of the liveness property, with the
  bound on the device.

Deliberately distinguished:

- **Heartbeat for *liveness detection*** (e.g. a failure detector) uses a
  heartbeat to *detect* a dead peer and then act. The dead-man uses the
  heartbeat to *gate* an action and lets its absence *cause* the stop — the
  device need not detect anything, only time out.
- **Timeout-retry** is the opposite philosophy: omission triggers a
  *re-action*. The dead-man triggers a *stop*. Never combine a dead-man with
  retry-on-timeout for the gated action.

## Why the tempting alternatives are wrong

- **"Emit heartbeats on a host timer (auto mode) even for UI-driven action."**
  Breaks the safety correspondence: a live process with a dead human keeps
  moving. The proper pattern makes the human the sole causal source.
- **"Send an explicit stop on detection of operator disengagement."** This
  is a fail-*active* design: the safe state requires a correct action, and
  the most likely failure (the detector itself dying, or the stop command
  being lost) leaves the action running. The dead-man fails safe on
  omission, which needs no correct action.
- **"Retry the stop command on timeout."** Retrying a stop is safe *in
  addition*, but it must never be the *only* path to safe: omission must
  already guarantee the stop. Treat the explicit stop as an optimization to
  stop *faster* than `τ_f`, not as a substitute for the watchdog.
- **"Lengthen `τ_k` to reduce traffic."** Violates `τ_k + Δ + Δ < τ_f`; the
  heartbeat must beat the watchdog. The cost of a short `τ_k` is the price of
  the guarantee.
- **"Let the host own the watchdog."** Then a hung host never times out and
  the action runs forever. The watchdog must be on the device (or on a party
  independent of the host's continued correct behavior).

## Failure modes and tricky details

- **Auto mode used where a UI drives a backend.** The review's own framing
  exposes this: auto is "right for the CLI, where the process holding the
  terminal is the held button." The instant a UI front-end drives a
  long-lived backend, the process is no longer the human, and auto mode
  becomes a live process with a dead human. The fix is to use manual mode
  (forward each human heartbeat 1:1) — which `z1ctl` already provides, making
  this a *selection* bug, not an *implementation* bug.
- **Splitting the keepalive digram into two writes.** The comment is explicit
  that `?` and `0x1A` must go in one write or they "race other traffic and
  leave orphaned bytes in the firmware's command buffer." Atomicity of the
  heartbeat is a correctness invariant.
- **A late keepalive "fighting the stop."** Stop suppresses heartbeats *first*
  (`stopping.Store(true)`) and the manual `Keepalive()` refuses once stopping
  has begun. Without this ordering, a heartbeat arriving after the stop byte
  could restart motion.
- **Stop-byte write failure mistaken for stop failure.** Even if `0x19` never
  lands, "keepalives have ceased, so the firmware's dead-man stops the axis."
  The error return means "ack not observed," not "stop failed" — the safe
  state is already guaranteed by omission.
- **Treating the explicit stop as required.** It is an optimization to stop
  faster than `τ_f`; the watchdog is the guarantee. If a reviewer believes the
  stop byte is load-bearing, they will add retry logic, which is correct *as
  an optimization* but must never be presented as the safety path.

## Testing and verification

- **Omission-stops:** start a jog, emit no keepalives; assert the axis stops
  within `τ_f` (device-enforced), with no host action.
- **Host-crash-stops:** kill the host process mid-jog; assert the axis stops
  within `τ_f` (no process to emit heartbeats).
- **Manual-mode-correspondence:** in manual mode, assert that *no* heartbeat
  is emitted unless a `Keepalive()` call occurred (no host timer exists).
- **Auto-mode-liveness-without-human:** in auto mode with a live process,
  assert heartbeats continue even when the human is disengaged — the
  *demonstration* that auto is the near-miss, documented as a test so the
  selection rule is enforced.
- **Atomicity:** fault-inject an interleaved writer between the `?` and
  `0x1A`; assert the keepalive is one write (the digram is atomic).
- **Stop-ordering:** call `Stop()` while a manual `Keepalive()` is in flight;
  assert the heartbeat is refused (suppression precedes stop).
- **Stop-byte-loss:** fault-inject a loss of the `0x19` stop byte; assert the
  axis still stops within `τ_f` (omission is sufficient).
- **Deadline:** under worst-case command load, assert two consecutive
  heartbeats are never more than `τ_f − Δ_clock − Δ_network` apart
  (schedulability of the heartbeat task).

## Applicability and non-appactibility

**Use when:**
- A continuous action is hazardous and must stop the instant the operator
  disengages (jog, feed, hold-open valve, "press to move").
- The safe state is "stopped," reachable by omission.
- A device-side watchdog can enforce the bound independent of the host.

**Do not use when:**
- The action is a **one-shot move to a target** — the safe state is
  "completed," not "stopped"; a dead-man would abort every long move on
  heartbeat loss. Use an admitted, at-most-once command instead (entry 01).
- There is no device-side watchdog to own `τ_f` (then a hung host runs
  forever; the guarantee requires an independent enforcer).
- The operator's continued engagement is *not* the safety question (e.g. a
  long unattended job — there the question is job completion, not operator
  presence; use job supervision, not a dead-man).

## Candidate ecosystem guidance

1. **Make the human the sole causal source of each heartbeat.** One human
   action → one heartbeat, forwarded 1:1. No host timer stands between the
   human and the device.
2. **Own the bound on the device, not the host.** The watchdog `τ_f` must be
   enforced by a party that survives host failure; otherwise a hung host
   defeats the guarantee.
3. **Fail safe on omission.** The safe state is reached by the absence of
   heartbeats (the easy failure), not by a correct stop (which can fail).
   Treat the explicit stop as an optimization, never the only safe path.
4. **Emit the heartbeat atomically and on its own lane.** The keepalive is
   one write; its goroutine/task is independent of the command path so a slow
   command cannot starve it (`τ_k + Δ + Δ < τ_f`).
5. **Suppress before stop.** Stop ordering is suppress-heartbeats →
   explicit-stop → ack. A late heartbeat must never be able to fight the stop.
6. **Select the mode by who the dead-man is.** Auto (host timer) only when
   the process *is* the human (CLI); manual (forwarded 1:1) whenever a UI
   front-end drives a backend.

## Open questions

- Should the heartbeat carry a **nonce or sequence** so the device can reject
  stale/replayed keepalives? (Composes with entry 01's correlation-by-value;
  a replayed heartbeat could keep a dead-man alive past disengagement.)
- Should `τ_k` be adaptive (Φ-accrual) to trade traffic for responsiveness,
  or fixed to keep the schedulability proof simple? Fixed is safer to reason
  about; adaptive reduces load.
- Does the pattern compose with the latched safety channel (entry 02)? A
  dead-man timeout could *latch* a "jog timed out" safety event that the
  operator must ack before re-starting — making the omission observable
  rather than silent.
- Can the explicit-stop-as-optimization be proven non-load-bearing (so a
  reviewer never mistakes it for the safety path) with a TLA⁺ model?

## Evidence and references

- `makera-z1-cli/pkg/makera/motion.go` — `jogKeepaliveInterval`/`jogStopAckTimeout`
  constants; `JogStart` (auto, near-miss) vs `JogStartManual` (proper);
  `keepaliveLoop`; `Keepalive` (1:1 forward); `Stop`/`stop` (suppress → stop
  → ack ordering); the "depends on our software STOPPING" comment.
- `makera-z1-cli/pkg/makera/client.go` — `RealtimeJogKeep = 0x1A`,
  `EncodeRealtime` (one write), the read loop's `jogAck` channel for the `^Y`
  acknowledgement.
- docmgr ticket `MZ1-005` (in-repo, branch `task/cnc-control-dropcut`): the
  full study, §3.8 (the dead-man jog), §5.13 (time/FLP), §6.4 (deadline
  schedulability), §6.9 (bounded liveness, device-owned bound).
- Sibling entries: [[Research/Software Architecture Garden/dropcut-studio/designs/01 - Sentinel-Delimited Command Completion over an Ordered Line Queue|01]] (correlation) and [[Research/Software Architecture Garden/dropcut-studio/designs/02 - Latched Safety Channel over a Lossy Inbound Queue|02]] (delivery QoS).
- Theory: Alpern & Schneider (safety/liveness, bounded liveness); real-time
  scheduling (periodic-task deadline monotonicity, `τ_k + Δ + Δ < τ_f`);
  fail-safe design (safe state by the most likely failure); watchdog/heartbeat
  and lease/lease-renewal in distributed systems. See `../sources/` for
  related papers and reference pages.

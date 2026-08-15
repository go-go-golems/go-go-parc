---
title: Latched Safety Channel over a Lossy Inbound Queue
aliases:
  - QoS-separated inbound dispatch
  - latched safety event channel
  - traffic-class channel separation
  - drain-safe alarm latch
status: candidate
type: architecture-garden-design
created: 2026-08-14
analyzed: 2026-08-14
repository: /home/manuel/workspaces/2026-08-11/cnc-control-dropcut/dropcut-studio
repository_remote: git@github.com:wesen/dropcut-studio
repository_branch: task/cnc-control-dropcut
repository_commit: 5f33ba1
source_ticket: /home/manuel/workspaces/2026-08-11/cnc-control-dropcut/dropcut-studio/ttmp/2026/08/14/MZ1-005--cnc-to-z1ctl-command-control-protocol-wire-level-study-and-correct-design-theory
repository_note_url: https://github.com/go-go-golems/go-go-parc/blob/main/Research/Software%20Architecture%20Garden/dropcut-studio/designs/02%20-%20Latched%20Safety%20Channel%20over%20a%20Lossy%20Inbound%20Queue.md
tracking_issue: https://github.com/wesen/dropcut-studio/issues/3
architecture_catalog: https://github.com/orgs/go-go-golems/projects/3
tags:
  - architecture-garden
  - dropcut-studio
  - command-control
  - qos
  - queueing
  - safety
  - liveness
  - go
related_files:
  - makera-z1-cli/pkg/makera/client.go
related_notes:
  - "[[Research/Software Architecture Garden/dropcut-studio/README|Architecture Garden — dropcut-studio]]"
  - "[[Research/Software Architecture Garden/dropcut-studio/designs/01 - Sentinel-Delimited Command Completion over an Ordered Line Queue|01 — Sentinel-Delimited Command Completion over an Ordered Line Queue]]"
  - "[[Research/Software Architecture Garden/README|Software Architecture Garden]]"
---

# Latched Safety Channel over a Lossy Inbound Queue

This note records a reusable pattern for **inbound dispatch in a command-control
link where safety events and ordinary traffic arrive on the same stream**. A
single reader decodes everything the device emits, but it must not treat all of
it alike: alarms, halt reasons, and cover/endstop events are **safety events**
that must remain observable until acknowledged, while command replies,
telemetry snapshots, and debug chatter may be dropped under pressure. The
pattern separates the one physical stream into **traffic classes by Quality of
Service**, routing safety to a **latched** (lossless, monotonic-merge) channel
and everything else to **lossy** channels — and redefines "drain" so it can
never clear safety state.

The pattern was observed as a defect in `z1ctl`'s Makera Z1 controller, where
every inbound class shares one drop-oldest FIFO and a pre-command `drain()`
discards anything in it, including alarms (finding MC-06). The defect is
portable: any single-reader command loop that multiplexes safety and telemetry
through one buffer will, by construction, give safety events the loss profile
of chatter. The fix is a queueing/QoS discipline, not a bigger buffer.

> [!summary]
> - A single reader cannot block (blocking it stalls all inbound parsing), so
>   the *loss policy* is the only lever. One loss policy on one shared buffer
>   forces every traffic class to that policy — and drop-oldest is right for
>   telemetry and wrong for alarms.
> - Separate inbound traffic by QoS class. Safety events route to a **latched**
>   channel: a join-semilattice register that merges new events (`latch :=
>   latch ⊔ s'`), is never dropped on overflow, and is cleared only by an
>   explicit ack — never by a drain. Telemetry and logs route to lossy
>   channels where drop-oldest/latest-wins is correct.
> - The invariant: **draining a command queue never clears safety state.**
>   Queueing theory says the lossless class and the lossy classes can coexist
>   only in separate buffers; Little's law says the latched safety channel
>   need not be large, only lossless.
> - Use wherever a command loop multiplexes safety and non-safety inbound
>   traffic. Do not use a single FIFO when any inbound message is a safety
>   event whose loss is a hazard, or when the consumer may drain before
>   acknowledging.

## Why this note exists

The sentinel pattern (design entry 01) explains *correlation*; this entry
explains *delivery QoS*. They share a root cause in `z1ctl`: the sentinel
design forces all inbound traffic onto one stream (because the host can only
split the stream on the sentinel), and that single stream is then served by one
lossy FIFO. So MC-06 is the downstream consequence of the sentinel design — but
the QoS fix is an independent, reusable pattern that applies to any
single-reader command loop, sentinel or not. Naming it separately lets an
engineer apply it without first adopting the sentinel.

## Pattern statement

> **Law.** When a single reader multiplexes inbound traffic of differing
> Quality-of-Service through one stream, it must dispatch by class at the
> moment of decode, giving each class the loss policy its semantics require.
> Safety events route to a **latched** channel — lossless, monotonic-merge,
> ack-cleared — so that overflow and pre-command draining cannot lose them.
> Telemetry and logs route to **lossy** channels where drop-oldest or
> latest-wins is correct. The drain operation is defined to act on the
> command-reply and log channels only: `drain` is the identity on the safety
> latch. The protected property is: *a delivered safety event remains
> observable until an explicit acknowledgement, regardless of buffer
> pressure or pre-command draining.*

The pattern deliberately does **not** promise: that every safety event is
delivered to the latch (a reader crash or a desynced frame can still lose
*arrival* — that is the framing/sentinel pattern's job); that telemetry is
fresh (it may be stale-by-design); or that the latch reflects current machine
state (it reflects the *latest observed* safety state, which may lag).

## Concrete architecture

`z1ctl` has one reader (`readLoop`) decoding frames and enqueuing `Message`s
onto one buffered channel `msgs` of capacity 256. Delivery never blocks; on a
full buffer it drops the oldest message, with a single exception — a message
carrying the completion sentinel is never the one dropped. Before each command
exchange, `drain()` empties the channel so a stale reply cannot be mistaken
for the current one.

```text
                 ┌─────────── single reader (readLoop) ───────────┐
  device ──►  decode  ──►  deliver(m)  ──►  [ msgs (cap 256) ] ──►  consumer
                                    │            │
                                    │      full? drop-oldest
                                    │      (never drop sentinel)
                                    │
                          drain() before each command exchange
                          discards EVERYTHING buffered
```

Every inbound class rides this one channel:

| Traffic class | Required QoS | What it carries | Correct policy |
|---|---|---|---|
| Safety | **latched, lossless until ack** | alarms, halt reasons, cover/endstop | **drop-oldest is wrong** |
| Command replies | lossless within an exchange | output of the current command | bounded by correlation |
| Telemetry | lossy; latest-wins | status snapshots, `?` reports | drop-oldest OK |
| Logs | lossy; drop-oldest | informational chatter | drop-oldest OK |

The defect is that rows 2–4 get their correct policy *by accident* (drop-oldest
happens to suit them) while row 1 gets the wrong policy *by construction*: the
shared buffer forces the alarm-loss probability to equal the chatter-loss
probability.

## Implementation details

The mechanism is in `makera-z1-cli/pkg/makera/client.go`:

```go
msgs: make(chan Message, 256)              // L96, L133 — one shared buffer

// deliver enqueues without ever blocking the reader. When full it drops
// the oldest — unless the oldest carries the sentinel.
func (c *Client) deliver(ctx, m) bool {
    select { case c.msgs <- m: return true; default: }
    select {
    case old := <-c.msgs:
        if hasSentinel(old) && !hasSentinel(m) { m = old }   // L263
    default: }
    select { case c.msgs <- m: default: }
    return true
}

// drain empties any buffered messages, so a command's reply cannot be
// confused with unsolicited output that arrived before it.
func (c *Client) drain() {                  // L294
    for { select { case <-c.msgs: default: return } }
}
```

Two details are load-bearing for the failure:

1. **One loss policy for all classes.** `deliver` decides drop-vs-keep using
   *one* predicate (does it carry the sentinel?). An alarm and a debug line
   are indistinguishable to the dropper.
2. **`drain()` is class-blind.** It discards whatever is buffered, including
   an alarm that arrived between the last consumer read and the next command.
   Draining is correct for *stale command replies* and catastrophic for
   *unacknowledged alarms*.

## Behavioral contract

**Guaranteed (current design):**
- The reader never blocks (no deadlock from a full consumer).
- A sentinel-bearing message is preferentially retained through overflow.
- A command's reply is not confused with older output (drain-before-send).

**Not guaranteed (the defects):**
- That an alarm survives a full buffer — it can be the dropped-oldest.
- That an alarm survives a `drain()` — it is unconditionally discarded.
- That a safety event is ever observed by the application before it is lost.
- That the consumer can distinguish "no alarm" from "alarm was dropped."

## Mathematical / CS foundations

### QoS separation theorem (queueing)

Model the shared buffer as a finite-capacity queue under a single non-blocking
producer. For an `M/M/1/K` queue with arrival rate `λ`, service rate `μ`,
load `ρ = λ/μ`, capacity `K`, the steady-state loss probability is

```
P_loss = ρ^K (1−ρ) / (1 − ρ^{K+1})     (ρ ≠ 1)
P_loss = 1/(K+1)                       (ρ = 1)
```

(Drop-oldest is not identical to drop-on-arrival-to-full, but shares the same
order and the same qualitative conclusion.)

**The separation theorem.** If `k` traffic classes with loss tolerances
`p_1 ≤ p_2 ≤ … ≤ p_k` share **one** buffer of size `K`, the achieved loss
probability for **every** class is the single-class `P_loss(K, ρ_combined)`.
The most loss-tolerant class drags the least-tolerant class down to its level.
Separating into `k` buffers of sizes `K_i` gives each class its own
`P_loss(K_i, ρ_i)`, so a **lossless** class (`K_i = ∞`, or latched) can
coexist with a lossy class. **The single-FIFO design makes the alarm-loss
probability equal to the chatter-loss probability — this is the quantitative
form of MC-06.**

### Little's law: the safety channel need not be large, only lossless

Little's law `L = λW` bounds the average occupancy of a lossless channel: a
safety channel with arrival rate `λ_s` and bounded ack latency `W_s` holds
`L_s = λ_s W_s` messages on average. With alarms rare (`λ_s` small) and a short
ack window, `L_s ≈ 1`. **The safety channel need not be a big buffer; it must
merely be lossless.** A single latched slot is usually sufficient — which is
why "make the buffer bigger" is the wrong fix: bigger buffers reduce
`P_loss` for *all* classes but never make it zero, and they do nothing for the
`drain()` problem.

### The latch as a join semilattice

A safety channel is **not a FIFO**; it is a **latch** — a register holding the
latest safety state, cleared only by an explicit ack. Model the safety state
space as a join semilattice `(S, ⊔)` where `⊔` is "merge alarms, take the
worst": `Alarm ⊔ Idle = Alarm`, `Alarm_a ⊔ Alarm_b = Alarm_{max(a,b)}`. On a
new safety event `s'`, the latch updates monotonically:

```
latch := latch ⊔ s'        (monotone; never loses severity)
ack:    latch := ⊥          (the only permitted decrease)
```

The `drain()` operation is the **identity** on the latch:

```
drain(safety_latch) = safety_latch      (a latch is not drained; it is acked)
drain(command_q)    = empty             (drain acts on lossy/bounded classes)
```

This is the formal statement of the invariant: *a delivered safety event
remains in the latch until an ack, regardless of overflow or drain.* A FIFO is
cleared by draining; a latch is cleared by acknowledging — conflating the two
is the bug.

### Safety vs. liveness (Alpern–Schneider)

- **Safety property:** "an unacknowledged alarm is never lost to overflow or
  drain." Violated by a finite prefix — point at the drop/drain.
- **Liveness property:** "an ack eventually happens (or the latch is
  observable on query)." Violated only in the limit.

The latch makes the *safety* property structural (loss probability 0 for the
latch, by construction), leaving only the liveness property to argue
(the application must eventually ack/query). This is the same
probabilistic→structural move as the nonce fix in the sentinel pattern: a
lossy FIFO gives a *probabilistic* alarm-preservation argument
(`P_loss` small); a latch gives a *structural* one (loss = 0).

### Back-pressure and the single-reader constraint

The reader cannot block — blocking the single reader stalls all inbound
parsing, which is itself a safety hazard (a feed-hold reply would not be
read). So the loss policy is decided **at dispatch time, per class**, not by
the channel's blocking behavior:

```
on decode(m):
   class(m) ∈ {safety, command, telemetry, log}
   switch class(m):
     safety:   latch := latch ⊔ m          // merge, never drop, never drain
     command:  command_q <- m   (bounded; lossless within exchange)
     telemetry: telemetry_q <- m  (cap 1–4; drop-oldest; latest-wins)
     log:      log_q <- m         (cap 256; drop-oldest)
```

The lossy channels keep `deliver`'s non-blocking property (they are allowed to
drop); the safety channel is non-blocking *and* non-dropping because a
single-slot latch with monotone merge has constant-time update and never
rejects.

## Design-pattern vocabulary

- **QoS separation / traffic-class channel separation** — the networking
  term; the inbound stream is a link, classes are QoS levels, the latch is the
  highest-priority (lossless) class. See Tanenbaum & Wetherall, *Computer
  Networks*, on priority/multi-level queuing.
- **Bulkhead** (resilience pattern) — segregating resources so failure or
  pressure in one class does not starve another. Channel separation is a
  bulkhead between safety and telemetry.
- **Latched register / hold register** (hardware) — a flip-flop that holds a
  value until explicitly reset; the ack is the reset. The alarm latch is a
  software hold register.
- **Priority queue / multi-level feedback queue** — QoS in OS scheduling; here
  applied to *delivery loss policy*, not CPU time.
- **Dead-man's switch** (the dual) — the jog keepalive (design entry 01) makes
  safety the *absence* of a signal; the alarm latch makes safety the
  *presence* of an unacknowledged signal. Both are fail-safe: the safe state
  is reached by the easy failure (omission of keepalive; absence of ack).
- **Join semilattice / CRDT register** — the latch's monotone-merge is the
  same algebra as a state-based CRDT register (e.g. an LWW-or-max register),
  which converges without coordination. The ack is the only allowed
  anti-monotone step, taken by a single authorized consumer.

Deliberately distinguished:

- **Mailbox / FIFO** — a mailbox is a queue (cleared by draining); the latch
  is *not* a queue (cleared by ack). Using a FIFO for safety is the bug.
- **Bigger buffer** — increases `K`, lowers `P_loss` for all classes, never
  reaches 0, and does not fix `drain()`. The wrong fix for the right problem.

## Why the tempting alternatives are wrong

- **"Make the buffer bigger (256 → 4096)."** Lowers `P_loss` for *all* classes
  but never to zero; under sustained chatter the alarm still drops; and it
  does nothing for the `drain()` path. The latch makes loss *structurally*
  zero for the one class that needs it.
- **"Drop-newest instead of drop-oldest."** Trades which alarm you lose, not
  whether you lose one. The lossless class must not drop at all.
- **"Never drain."** Then stale command replies corrupt the next exchange (the
  sentinel pattern's correlation breaks). Drain is *correct* for command
  replies and logs; the fix is to *scope* it, not remove it.
- **"Priority: keep alarms in the buffer."** A priority FIFO is still a FIFO;
  a drain clears it, and under enough pressure the highest-priority class
  still drops. The latch is lossless by construction, not by priority.
- **"Block the reader when the alarm channel is full."** Blocks the single
  reader → stalls all parsing → a feed-hold reply goes unread. The latch is
  non-blocking because a single slot with merge is constant-time and never
  full.

## Failure modes and tricky details

These are the concrete defects observed in `z1ctl` (full evidence in MZ1-005,
MC-06), each a symptom of one-loss-policy-for-all-classes:

- **Drop-oldest loses an alarm under chatter.** When the 256-deep `msgs` fills
  with bulk listings or debug output, `deliver` drops the oldest — which may
  be an unacknowledged halt reason or cover-open event. The sentinel exception
  does not help: an alarm carries no sentinel byte.
- **`drain()` clears an unacknowledged alarm.** Before each command exchange
  `commandUnchecked` calls `drain()`, discarding everything buffered — including
  a safety event that arrived between the last consumer read and the next
  command. The consumer then sees "no alarm" when the machine is in alarm.
- **"No alarm" is indistinguishable from "alarm dropped."** Because the loss
  is silent, the application cannot tell a safe machine from a machine whose
  alarm was discarded. This is the safety/liveness collapse: a *safety*
  property ("alarm observed") is treated as a *liveness* property ("probably
  delivered").
- **The sentinel exception is class-blind.** The only drop-protection in
  `deliver` keys on the sentinel byte, i.e. on *command correlation*, not on
  *safety*. An alarm gets no protection an ordinary reply does not already
  have.

## Testing and verification

- **Overflow-survival:** fill the log channel to capacity, then deliver an
  alarm; assert the alarm is observable and not dropped.
- **Drain-survival:** deliver an alarm, then call `drain()`; assert the alarm
  survives (the latch is drain-invariant).
- **Monotone-merge:** deliver `Alarm_a` then `Alarm_b` with `b > a`; assert
  the latch holds `Alarm_b`; deliver `Idle`; assert the latch still holds
  `Alarm_b` (merge is monotone; only an ack decreases).
- **Ack-clears:** after an alarm, call `ack()`; assert the latch is `⊥` and a
  subsequent `Idle` stays `⊥`.
- **Reader-non-blocking:** under sustained alarm+chatter flood, assert the
  reader never blocks (the latch update is constant-time; lossy channels drop).
- **Property/fuzz:** for any interleaving of alarms, chatter, drains, and
  overflows, *if a safety event was delivered to the dispatcher, then either
  it is in the latch or an ack was received* (the latch liveness invariant).

## Applicability and non-applicability

**Use when:**

- A single reader multiplexes inbound traffic of differing QoS (safety +
  telemetry + logs) through one stream.
- Any inbound message is a safety event whose loss or drain is a hazard.
- The consumer may drain or fall behind (back-pressure must not stall the
  reader).

**Do not use (as-is) when:**

- The peer already separates safety traffic onto its own channel (use it
  directly).
- No inbound message is safety-relevant — a single lossy FIFO is simpler and
  fine.
- The consumer is guaranteed to keep up and never drains — then a single FIFO
  loses nothing, but the guarantee is usually false in practice.

## Candidate ecosystem guidance

1. **Classify at decode, not at consume.** The loss policy is decided when the
   reader decodes a frame, by its class — not later by a consumer that may
   have already fallen behind.
2. **Safety is a latch, not a queue.** Lossless, monotone-merge, ack-cleared.
   A FIFO cleared by draining is the wrong structure for an event that must
   survive until acknowledged.
3. **Scope the drain.** `drain()` acts on command-reply and log channels only;
   it is the identity on the safety latch. "Drain everything" is a bug.
4. **Lossless need not be large.** Little's law (`L = λW`) says the safety
   channel needs ~1 slot for rare alarms; make it lossless, not big.
5. **Never block the single reader.** A blocked reader stalls all parsing,
   including stop replies — a safety hazard. The latch is non-blocking
   because monotone merge is constant-time.

## Open questions

- Is one latched slot sufficient, or should the latch retain a *bounded
  history* of distinct alarms (e.g. a small ring with merge-by-severity) so the
  operator sees a sequence of distinct events, not just the worst? Little's
  law suggests history is bounded by `λ_s W_s`.
- Should the latch expose a "latched since" timestamp so the operator can tell
  a stale latch (machine safe, ack overdue) from a fresh one?
- Does the latch compose with the session state machine of the sentinel
  pattern (design entry 01)? A `Quarantined` state should arguably *force* a
  latch read on entry, so a desync cannot hide an alarm.

## Evidence and references

- `makera-z1-cli/pkg/makera/client.go` — `msgs` (L96, L133), `deliver`
  (L245–272), `drain` (L294–302), the single reader `readLoop` (L228+), the
  sentinel exception (L263).
- docmgr ticket `MZ1-005` (in-repo, branch `task/cnc-control-dropcut`): the
  full study, §3.5 (inbound dispatch), §5.10 (QoS & channel separation), §6.3
  (queueing theory, Little's law, the separation theorem), §7.5 (the
  separated-channels target design).
- Sibling design entry: [[Research/Software Architecture Garden/dropcut-studio/designs/01 - Sentinel-Delimited Command Completion over an Ordered Line Queue|01 — Sentinel-Delimited Command Completion over an Ordered Line Queue]] (the sentinel forces the single stream this pattern separates).
- Theory: Alpern & Schneider (safety/liveness); Kleinrock, *Queueing Systems*
  (M/M/1/K loss); Little's law (`L = λW`); join semilattices / state-based
  CRDT registers (monotone-merge convergence). See `../sources/` for saved
  papers and reference pages.

---
title: "Playbook - Race-Free Testbench Monitors and the Ready/Valid Boundary"
aliases:
  - Testbench Monitor Sampling Playbook
  - Ready/Valid Commit Boundary Playbook
tags:
  - article
  - playbook
  - verilog
  - testbench
  - ready-valid
  - verification
status: active
type: article
created: 2026-09-04
repo: /home/manuel/code/wesen/2026-09-04--gatemate-symbolic
---

# Playbook - Race-Free Testbench Monitors and the Ready/Valid Boundary

This playbook records two testbench disciplines that are easy to get wrong and expensive to debug: sampling signals at a clock edge without racing the design or the randomizer, and verifying a ready/valid boundary where the producer's commit and the consumer's acceptance are different events. Both come from a project where the symptoms were spurious assertion failures and truncated output — not design bugs at all, but measurement bugs.

## Race-free monitor sampling

The failure looks like this: a monitor that checks "a blocked producer holds its data stable" fires spuriously, reporting a violation the design did not commit. The cause is `#1`-delayed sampling. A monitor that waits a nanosecond after the edge reads *post*-nonblocking-update values, while the design sampled *pre*-edge values — and if the randomizer also updates its stimulus with `#1`, the stimulus the monitor sees is not the stimulus the design saw.

The fix is a fixed sampling discipline with no delays:

- **Stimulus is registered.** The randomizer drives a register (`stall_q`), and the handshake signal is a continuous assign of it. The value is stable within the cycle and is the same value for the design and every monitor.
- **Monitors read with blocking statements at `posedge clk`.** A blocking read inside `always @(posedge clk)` sees the values that were valid *just before* the edge — exactly what the design sampled at that edge.
- **Previous-cycle state is captured with nonblocking assignments.** `pv_valid <= out_valid; pv_data <= out_data;` gives the monitor the previous cycle without a second clock or a delay.

```systemverilog
always @(posedge clk) begin
  if (rst_n && pv_valid && !pv_ready) begin
    if (out_valid !== 1'b1 || out_data !== pv_data)
      errors = errors + 1;                 // blocked item changed
  end
  pv_valid <= out_valid;  pv_ready <= out_ready;  pv_data <= out_data;
end
```

One caveat: printing registered pulses (trace records) is the exception — print in a separate block with a `#1` after the edge so the newly assigned pulse and its payload fields are read together. This is safe only when pulses are guaranteed non-adjacent, which holds for instruction-commit pulses in a multi-cycle FSM.

## The ready/valid commit boundary

A ready/valid channel has an ownership rule: a transfer occurs on the edge where both are true; while blocked, the producer holds the item stable. Two properties are cheap to assert with the sampling pattern above:

1. **Blocked stability:** `out_valid && !out_ready` in cycle N implies `out_valid && out_data` unchanged in cycle N+1.
2. **One acceptance, one effect:** each accepted item produces exactly one architectural effect (in the source project, one pop and one trace record) — verified by comparing committed traces against the model under random backpressure.

The boundary lesson that cost a debugging cycle: **acceptance is not transmission.** When the producer's commit happens at channel acceptance but the consumer drains slowly (in the source project: an `EMIT` accepted by a one-entry elastic register, then framed into thirteen UART bytes at 115200 baud), the machine can reach its terminal state while the drain path is still busy. A testbench that stops at `halted` truncates the output. Rules:

- Give every drain path its own termination condition (quiescence of the elastic register and the framer), or budget the wait from the protocol (byte time × maximum in-flight bytes) rather than from the machine's state.
- Hold `ready` low through the framing to verify backpressure end-to-end; the trace must not change.

## Working rules

- Never mix `#1` sampling into the same block that feeds assertions; assertions read pre-edge, pulses print post-edge, and the two live in different always blocks.
- Randomize stimulus through registers only; a comb randomizer races every monitor in the design.
- Assertions that reference internal state (`depth`, occupancy counters) must be guarded by reset and a warm-up cycle count, or they fire on initialization values.
- Prefer asserting invariants every cycle (occupancy = sum of parts) over checking final state; the per-cycle check localizes the first violating edge, which is usually the whole answer.

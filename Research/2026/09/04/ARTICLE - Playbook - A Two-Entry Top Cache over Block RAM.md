---
title: "Playbook - A Two-Entry Top Cache over Block RAM"
aliases:
  - Top Cache Playbook
  - Split-Lifetime Frame Implementation
tags:
  - article
  - playbook
  - fpga
  - verilog
  - block-ram
  - microarchitecture
status: active
type: article
created: 2026-09-04
repo: /home/manuel/code/wesen/2026-09-04--gatemate-symbolic
---

# Playbook - A Two-Entry Top Cache over Block RAM

This playbook preserves the implementation discipline for the most error-prone refinement in a small stack machine: keeping the two newest stack entries in registers while the body of the stack lives in synchronous block RAM. The book pattern is called a *Split-Lifetime Frame*; the worked implementation is `rtl/stack_core_bram.sv` in the source repo. It applies to any LIFO (or LIFO-like) structure mapped to BRAM: operand stacks, return stacks, trail stacks, checkpoint stacks, undo logs.

## Why this note exists

Block RAM is synchronous: data requested in cycle N is valid in cycle N+1, and designs that "work" against a behavioral array with combinational reads fail in synthesis. The obvious fix — cache the top entries in registers — creates the real problem: two representations of one logical stack, and an invariant that must hold across push, pop, binary operations, and stalls. Every bug in the source project's refinement was a violation of one of the rules below.

## The representation

```text
top0_q       newest value            (valid when tc_q >= 1)
top1_q       next value             (valid when tc_q == 2)
RAM[dc-1]    newest deep value      (dc_q live entries, LIFO, no holes)
dt_q         first free address     (== dc_q)

invariant:  architectural depth == tc_q + dc_q
logical stack, newest -> oldest:
    top0, top1, RAM[dc-1], RAM[dc-2], ...
```

The invariant is not documentation. It is checked by the testbench **every cycle after reset**, and that check — not the directed tests — is what makes the refinement an argument rather than a hope.

## The algorithms

**Push (spill when the cache is full):**

```text
if tc == 0:   top0 = v;                 tc = 1
elif tc == 1: top1 = top0; top0 = v;    tc = 2
else:         RAM[dc] = top1; dc++; dt++        # spill write
              top1 = top0; top0 = v              # cache unchanged in size
```

**Pop (refill when the cache would empty but the deep region is non-empty):**

```text
if tc == 2:   top0 = top1; tc = 1
elif dc > 0: top0 = RAM[dc-1]; dc--; dt--        # refill read, tc stays 1
else:        tc = 0
```

**Binary operation — the subtle case.** With both operands cached, the result replaces `top0` and the new `top1` comes from `RAM[dc-1]` (one refill read). With `tc == 1`, operand *a* lives at `RAM[dc-1]` **and**, because the operation consumes one element, the new `top1` lives at `RAM[dc-2]` — **two sequential reads at different addresses for one instruction**. Budget the states for both.

**Swap with `tc == 1`:** read `RAM[dc-1]`, make it the new `top0`, shift the old `top0` into `top1`, and shrink the deep region (`dc--`).

## Working rules

1. **Atomic count updates at the commit point.** `depth`, `tc`, `dc`, `dt`, and `pc` change on the same edge — in the single `COMMIT` state or on the output-acceptance edge. RAM reads that repair the representation are internal stuttering *around* that edge. The trace must never observe an intermediate state where `depth != tc + dc`.
2. **One mutation owner.** All register writes apply in one `always_ff` block; stack and RAM writes happen only in the commit state. A second writer anywhere destroys the ability to argue about precise faults.
3. **Prefetching is safe because reads are side-effect-free.** The FSM issues the `RAM[dc-1]` read *before* the instruction's precondition checks whenever the representation will need it. A prefetched value that an ensuing fault discards changes nothing — but the fault record must not depend on it.
4. **Guard the reads that feed records.** Stale cache registers must not leak into fault records when the stack is shallower than two; mask operand tags by depth.
5. **Writes only in the commit state, at address `dc`.** Reads target `dc-1` or `dc-2` from *other* states, so a read and a write never collide in one cycle, and a spill write is always at least two cycles older than any read of that slot.
6. **Wrap the RAM behind request/response-valid points.** No design logic depends on combinational read data; behavioral arrays in testbenches model the sync read explicitly.

## Common failure modes

- Staging the wrong `dc` delta for a binary operation (`dc-1` when the operands came from the cache, `dc-2` when one came from RAM) — caught by the invariant check within one test run.
- Forgetting the second sequential read for `tc == 1` binary operations, leaving `top1` stale.
- A pop implemented as `tc--` without shifting `top0 <= top1`, leaving the removed value as the cached top.
- EMIT acceptance updating `depth` but deferring the cache repair past the trace pulse, letting the invariant dangle.
- Reset clearing the RAM *contents* — unnecessary and expensive; clearing the occupancy counters is sufficient because unreachable data is never observed.

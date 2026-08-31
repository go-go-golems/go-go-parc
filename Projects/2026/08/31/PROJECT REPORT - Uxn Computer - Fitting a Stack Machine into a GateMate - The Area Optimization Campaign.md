---
title: "PROJECT REPORT - Uxn Computer - Fitting a Stack Machine into a GateMate: The Area Optimization Campaign"
aliases:
  - Uxn Computer Area Optimization Deep Dive
  - UXN-GM-001 Place and Route Utilization Campaign
  - Sequential Stack Peeks Report
tags:
  - project
  - article
  - fpga
  - verilog
  - uxn
  - varvara
  - gatemate
  - place-and-route
  - area-optimization
status: active
type: project
created: 2026-08-31
repo: /home/manuel/code/wesen/2026-08-30--uxn-computer
---

# PROJECT REPORT - Uxn Computer - Fitting a Stack Machine into a GateMate: The Area Optimization Campaign

This report covers the area optimization work of the Uxn/Varvara computer project (ticket UXN-GM-001): the sequence of measurements, failed experiments, and one structural CPU refactor that took the design from a hard placement failure at 92% LUT utilization to a routable 66%. The machine itself — an FPGA implementation of the Uxn stack machine with console, PS/2 keyboard, and VGA display — was functionally complete and verified in simulation before this campaign started; every change described here was therefore gated by a differential test suite, not by inspection.

The campaign has a simple narrative arc: synthesis succeeded, place-and-route refused to place, and the fix required knowing *which* part of the design was actually large. The answer was not the one the design document predicted. This report walks through the measurement methodology, the toolchain discovery that reframed the problem, and the microarchitectural change that resolved it.

> [!summary]
> Three facts determined the outcome:
> 1. The design's LUT utilization was dominated by the CPU's *stack operand read network* — roughly one third of the device — not by the ALU, the divider, or the screen engine.
> 2. Yosys can map that network onto dedicated mux infrastructure (57% utilization), but nextpnr-himbaechel in the current OSS CAD Suite rejects the resulting `CC_MX8` cells, so the mux cost has to be paid in LUTs.
> 3. Serializing the operand reads — one byte per cycle through a single shared read port — removed ten and a half thousand LUT sites (92% → 66%) without changing a single architectural behavior; all 58 tests and 100 random differential programs still pass.

## The starting point: a machine that would not place

The full machine synthesizes to 28,730 cells after the sequential-peek refactor (37,703 CPE_LUT-sites before it): the Uxn core, 64 KiB main RAM, the Varvara device system, UART, PS/2 receiver, screen engine, 80 KiB framebuffer, and a VGA scanner. On the GateMate CCGM1A1 (20,480 CPEs ≈ 40,960 LUT-tree sites, 40,960 flip-flops, 64 × 20 Kb block RAMs), the first place-and-route attempt reported:

```
Info: Device utilisation:
Info:              CPE_LT:   37703/  960    92%
ERROR: Unable to find legal placement for cell of type 'CPE_L2T4'
       after 10001 attempts, check constraints and utilisation.
```

The analytical placer gives up when it cannot find a legal site for a LUT-tree cell within its attempt budget. At 92% utilization the remaining sites are fragmented — LUT-trees want adjacent CPEs, and 8% of scattered free sites are not adjacency. Increasing the heap placer's timeout does not help: the failure occurs in the analytical placer's own 10,000-attempt stage, before the heap placer runs. The design had to shrink; the question was where.

## Measuring the biggest components

Area attribution in an FPGA flow is not a solved problem: Yosys's cell statistics are pre-placement, and nextpnr's utilization is post-packing. The project used three measurements, each answering a different question.

### Measurement 1: the whole machine, one knob at a time

The cheapest experiments delete a subsystem and re-synthesize:

| Configuration | Cells (Yosys) | CPE_LT (nextpnr) |
|---|---|---|
| CPU + RAM + dev bus only (P3 smoke test) | — | 28,954 (70%) |
| Full machine, parallel stack peeks | 35,055 | 37,703 (92%) |
| Full machine, divider gutted to `0` | 34,362 | — (≈600 LUTs saved) |
| Full machine, muxcover allowed to use MX8 | — | 23,577 (57%) |

The first row was known from the P3 phase: the CPU *alone* was 70% of the device, before the screen engine, the VGA scanner, or the PS/2 translator existed. That single fact redirected the whole campaign — the screen subsystem everyone might suspect first adds only about 9,000 sites; the core is the consumer.

The divider row killed the design document's first prepared mitigation. Uxn's `DIV` opcode is a full 16-bit combinational divide (`alu = y_val / x_val`), and the risk register had proposed a sequential divider as the primary area lever. Gutting it to a constant and re-synthesizing saved roughly 600 LUTs. A 16-bit divider is wide but shallow: it costs about 2% of the device, not the 10-15% the mitigation assumed. The lever existed elsewhere.

### Measurement 2: the MX8 experiment

The decisive experiment was accidental in spirit but cheap to run: synthesize the same design *without* the `-nomx8` flag that the MATE-16 project had always passed to `synth_gatemate`. The result was 23,577 CPE_LT — 57% utilization — for the identical netlist. The 14,000-site gap between 57% and 92% is entirely a question of how Yosys's `muxcover` pass implements wide multiplexer trees:

- with `-nomx8`, mux trees become cascades of `CC_MX2`/`CC_MX4` cells that nextpnr expands into LUT-tree sites (`CPE_LT`);
- without it, muxcover may emit `CC_MX8` cells that pack into the CPE's dedicated mux routing (`CPE_CPLINES`, which the utilization report shows at 1% used).

This reframed the problem: the design's dominant cost was not "logic" but a specific structure — wide multiplexer trees — and the question became *which* trees. The answer was in the CPU.

### Measurement 3: where the muxes live

The Uxn core reads its operands from the two 256-byte stacks. Before the refactor, decode was fully parallel: every operand of every instruction was peeked combinationally, at mode-dependent depths, in the same cycle:

```systemverilog
x_val = m2 ? {peek(mr, 8'd2), peek(mr, 8'd1)} : {8'h00, peek(mr, 8'd1)};
y_val = m2 ? {peek(mr, 8'd4), peek(mr, 8'd3)} : {8'h00, peek(mr, 8'd2)};
z_val = m2 ? {peek(mr, 8'd6), peek(mr, 8'd5)} : {8'h00, peek(mr, 8'd3)};
// plus special forms for LDZ/STZ/LDR/STR/DEI/DEO/SFT (x always a byte),
// LDA/STA (x always a short), JCN (condition at Lb(d+2)), STA (y at 4,3)
```

Each `peek` is a read of one stack at a computed depth. The distinct depths run from 1 to 6, and both stacks must be readable at each, so synthesis materializes on the order of twelve 256:1 by 8-bit multiplexers just to fetch operands — before any ALU, control, or device logic. At roughly 680 LUT4-equivalents per 256:1 8-bit mux, that is on the order of 8,000 LUTs of pure operand selection, plus the depth-computation logic feeding it. This is the component that the MX8 experiment measured at ~14,000 sites: operand selection, the stacks' write-side muxes, and the related fan-in.

For contrast, the rest of the machine:

| Component | Approximate cost | Notes |
|---|---|---|
| Stack operand read network | ~10,000 CPE_LT | 12 × 256:1 8-bit muxes + depth logic (pre-refactor) |
| Stacks as state | 4,096 FF | 2 × 256 × 8; no LUTRAM inference on this flow |
| ALU incl. 16-bit divider | ~600 LUTs | divider measured by deletion |
| Screen engine + VGA scanner + palette | ~9,000 CPE_LT | full display subsystem, measured as full-machine minus P3 core |
| Main RAM | 13 × CC_BRAM_40K | 64 KiB, initialized from the rom hex image |
| Framebuffer | 16 × CC_BRAM_40K | 80 KiB dual-clock; 29 of 32 block RAMs total |

The campaign therefore had one real target: the operand read network.

## The toolchain constraint that ruled out the easy fix

The obvious resolution — let muxcover emit `CC_MX8` and run at 57% — fails one step later:

```
ERROR: Cell type 'CC_MX8' is unsupported (instantiated as
       '$auto$muxcover.cc:539:implement_best_cover$142980').
```

The `nextpnr-himbaechel` build in the current OSS CAD Suite (2026-08-25) does not implement the `CC_MX8` cell in its GateMate uarch. The uarch's option list (`--vopt help`) exposes placement strategies (`no-cpe-cp`, `no-bridges`, `clk-cp`) but no mux-cell support. This is why the reference GateMate projects (prjpeppercorn, MATE-16) pass `-nomx8` to `synth_gatemate` for the nextpnr flow: it is not a style preference, it is a compatibility requirement. The lesson generalizes: when a tool flag disables a cell type, find out what that cell type costs you before accepting the flag as tradition.

## The fix: sequential operand peeks

The design document's second prepared mitigation was "sync-read stacks." The implementation went one step further than planned: rather than making the stacks synchronous, it serialized the operand reads themselves, which is what actually removes the mux ports.

### The new read path

The stacks remain flip-flop arrays (LUTRAM is not inferable for asynchronous reads on this flow, and block RAM is nearly fully allocated), but they now expose exactly one shared asynchronous read port:

```systemverilog
wire logic [7:0] pk_addr = b8((mr ? pk_rp : pk_sp) - {5'b0, peek_depth});
wire logic [7:0] stk_rd = mr ? rst[pk_addr] : wst[pk_addr];
```

Two 256:1 muxes replace twelve — one per stack, with a 2:1 stack select. The depth comes from a small register set selected by a peek index.

### The peek plan

Decode is restructured into three states:

1. **S_DECODE** computes the instruction's control (pop count, push target, memory/device routing), latches the *pre-pop* stack pointers (`pk_sp`, `pk_rp` — the pop happens in this state, so later cycles must not use the moved pointer), and latches a *peek plan*: a list of up to six stack depths, MSB-first, grouped into the operands `x`, `y`, `z`.
2. **S_PEEK** walks the list, one byte per cycle, accumulating into the operand registers with a shift: `x_val <= {x_val[7:0], stk_rd}`.
3. **S_OPEXEC** consumes the operands — this is the old decode case, moved verbatim: pushes, ALU results, jump targets, store data.

The plan itself is a small combinational table, because Uxn's operand depth rules have exactly seven special forms. The table must reproduce them all:

| Opcode class | X depths | Y depths | Z depths |
|---|---|---|---|
| default, byte | `[1]` | `[2]` | `[3]` (ROT) |
| default, short | `[2,1]` | `[4,3]` | `[6,5]` (ROT) |
| LDZ/STZ/LDR/STR/DEI/DEO/SFT (x always byte) | `[1]` | `[3,2]` short / `[2]` byte | — |
| LDA/STA (x always short) | `[2,1]` | `[4,3]` short / `[3]` byte (STA) | — |
| JCN (condition is one byte) | default | `[3]` short / `[2]` byte | — |

Y and Z depths are placed at plan slots offset by the X byte count (1 or 2), which is why the table is a table and not a formula.

### The bug the difftest caught

The refactor's one functional bug was caught eleven minutes after it compiled, by the first random program — not by review. Byte-mode operands accumulate as `{reg[7:0], byte}`, so a one-byte operand inherits the *previous* instruction's high byte: GTH on `02 > 00` evaluated against a stale upper byte and pushed the wrong result. The old parallel code zero-extended explicitly (`{8'h00, peek(...)}`); the fix clears all three operand registers when the plan is latched.

This is the differential-testing payoff in its purest form: the failure was a single wrong byte on one opcode in one mode, in a design that otherwise executed 55 instructions identically. Nothing short of a per-instruction, byte-level comparison would have caught it, and the project had that comparison already running as a script.

### What it cost and what it bought

The CPU now spends 1–6 extra cycles per instruction reading operands (2 on average). At the 10 MHz board clock the machine moves from roughly 2 MIPS to roughly 1.5 MIPS; the 60 Hz frame-loop workload this computer runs cannot observe the difference. What it bought:

| Metric | Before | After |
|---|---|---|
| CPE_LT utilization | 37,703 (92%) | 27,193 (66%) |
| Placement | fails (analytical placer exhausted) | converges |
| Retired-instruction trace vs model | identical | identical |
| Random differential programs | pass | pass (100/100) |
| Full pytest suite (58 tests) | pass | pass |

## Two adjacent fixes from the same campaign

Two further area-related bugs were found and fixed while getting the first synthesis to complete; they are part of the same story because both were invisible in simulation and material only in synthesis.

**The framebuffer that became 662,594 flip-flops.** The 80 KiB framebuffer was coded as a dual-clock true dual-port memory with an `initial` loop zeroing all 81,920 bytes. Synthesis treated that loop as 81,920 memory-init fragments, which defeated block RAM inference entirely: the framebuffer synthesized to 662,594 DFFs on a part with 40,960, and the synthesis run took 32 minutes. Two fixes were needed: guard the zero-fill with `ifndef SYNTHESIS` (simulation still needs a clean screen; FPGA configuration zeroes block RAM anyway), and change port A's read-during-write behavior from "old data" to write-through (`rdata_a <= we_a ? wdata_a : mem[addr_a]`), because Yosys's `$__CC_BRAM_TDP_` match requires defined write-through semantics when the second read port lives on another clock. The engine never consumes the read data in a write cycle, so the change is behavior-neutral — confirmed by re-running the screen differential tests. The framebuffer now maps to 16 `CC_BRAM_40K` blocks, for a system total of 29 of 32.

**The multi-driven FIFO pointers.** The console FIFO pointers `rxr` and `txw` were each assigned in two `always_ff` blocks: reset in the FIFO block, incremented in the dispatch/serve block. Simulation masks this because the two writes never conflict in the same cycle on the tested paths. Yosys does not mask it — it resolves the driver conflict "using constant," which would have tied the pointers to zero in the bitstream, silently breaking every console event after the first. The fix is the single-driver rule: each register is reset and updated in exactly one always block. The general lesson: grep every synthesis log for `multiple conflicting drivers`; the simulator and the synthesizer disagree about what that means.

## What remains open

- The 66% design is still routing at the time of this writing; router2 needs on the order of an hour at this density. Timing closure at 10 MHz is expected but not yet measured (the pre-refactor estimate was 11.1 MHz Fmax).
- Two block RAMs remain free; if area pressure returns, the stacks can move to block RAM (2 × 256×8) to reclaim the 4,096 flip-flops and the last read muxes.
- The sequential peek machine makes the CPU ~30% slower per instruction. If a workload ever needs the throughput back, the operand registers could be widened into a two-byte read (one port, 16-bit word) for the common short-mode case.

## How to reproduce the measurements

```bash
source ~/fpga/oss-cad-suite/environment
make synth ROM=hello        # ~12 min; stat in build/yosys.log
make pnr ROM=hello          # router2; utilization in build/nextpnr.log
python3 ttmp/2026/08/30/UXN-GM-001-*/scripts/02-rtl-difftest.py --n 100 --seed 7
python3 -m pytest uxn/sim -q   # 58 tests, ~18 min
```

## Sources

- Design document and investigation diary:
  `ttmp/2026/08/30/UXN-GM-001--uxn-varvara-computer-on-the-gatematea1-evb/` in the project repository
- Prior project report (machine architecture, verification chain):
  `Projects/2026/08/30/PROJ - Uxn Computer - A Varvara Machine in GateMate FPGA.md`
- Toolchain: OSS CAD Suite 2026-08-25 (Yosys 0.68+130, nextpnr-himbaechel 0.11.1-9-gb17408e2)

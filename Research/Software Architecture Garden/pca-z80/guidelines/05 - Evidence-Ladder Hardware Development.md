---
title: PCA-Z80 Research Brief — Evidence-Ladder Hardware Development
status: assigned
type: architecture-garden-research-guideline
created: 2026-08-29
repository: /home/manuel/code/wesen/2026-08-28--pca-gatemate
repository_commit: c07e700652732cd7264af6e2473eb1c6e1f20cc9
pattern_maturity: candidate-ecosystem-pattern
tags: [architecture-garden, pca-z80, verification, evidence, hardware]
related_notes:
  - "[[Research/Software Architecture Garden/pca-z80/index]]"
  - "[[Research/Software Architecture Garden/pca-z80/guidelines/00 - Shared Research and Subentry Guidelines]]"
---

# Evidence-Ladder Hardware Development — Research Brief

## Assignment

Write `designs/05 - Evidence-Ladder Hardware Development.md`. Explain how PCA-Z80 orders evidence from cheap semantic checks to expensive physical observation, and why no single layer can substitute for the others.

## Central question

What precise claim does each verification layer establish, and which plausible failures remain after it passes?

## Required local evidence

Read:

- model and assembler tests;
- direct RTL tests;
- mesh differential tests;
- `check_gatemate_rom.py`;
- `tb_post_synth.sv`;
- `tb_hello.sv` and `tb_mesh_hello.sv`;
- Makefile verification/build targets;
- physical capture script 18;
- route experiment script 19;
- diary failures from reset, ROM, PnR, UART, and mesh work.

Build a matrix mapping every command to its artifact, oracle, cost, and residual uncertainty.

## Required evidence ladder

At minimum include:

```text
hand-computed model tests
→ model/direct RTL differential
→ assembled program integration
→ mesh differential plus transaction conservation
→ synthesized primitive allocation/content inspection
→ post-synthesis primitive execution
→ placement and routed timing
→ packed bitstream and JTAG load
→ visible LED / physical UART capture
```

Explain why later evidence is not simply “better.” Each layer is stronger for some claims and weaker for diagnosis.

## External research requirements

Research:

1. verification pyramids and layered assurance in hardware;
2. refinement from specification/model to RTL and netlist;
3. equivalence checking and its limits;
4. FPGA post-synthesis and post-route simulation practices;
5. design-for-debug and observability;
6. hardware-in-the-loop and post-silicon validation;
7. assurance-case or claim-evidence-argument methods;
8. one documented incident where simulation passed but physical behavior failed.

Use primary verification literature, official simulator/tool documentation, and credible hardware case studies. Avoid generic software-testing pyramid citations unless their mapping to hardware claims is argued.

## Required experiments

Choose one historical false-positive boundary and reproduce the distinction. Examples:

- show `RAM_HALF: 1` while firmware content check fails in a controlled variant;
- show pre-route timing pass while routing times out;
- show successful JTAG load with a diagnostic image that intentionally does not blink;
- show sticky UART event versus actual decoded UART bytes.

The experiment must be safe, bounded, and restored afterward.

## Required claim matrix

For each layer state:

| Layer | Claim established | Oracle | Artifact | Residual failure |
|---|---|---|---|---|

Include negative claims: what the layer cannot prove.

## Required argument

Explain:

- why independent oracles matter;
- why transaction counters supplement state comparison;
- why BRAM existence and contents are separate claims;
- why route closure and routed timing are separate from placement estimates;
- why physical UART is stronger than LED but narrower than ISA verification;
- why scarce physical outputs motivate selectable observability;
- how the ladder reduces diagnosis cost.

## Textbook structure

Open with one concrete false confidence: RTL tests and BRAM allocation passed while firmware INIT was wrong. Then build the ladder as the response. Include an evidence-flow diagram, command table, failure matrix, and one complete chain from source firmware to captured bytes.

## Candidate subentries

- Model-Differential RTL Verification.
- Transaction Conservation Check.
- Primitive Allocation Plus Content Proof.
- Post-Synthesis Executable Acceptance.
- Sticky Event Witness.
- Selectable Diagnostic Observable.
- Dual-CDC Physical Capture.

## Definition of done

A reviewer can take any project claim—CPU semantics, mesh transport, firmware initialization, timing, configuration, or UART—and identify the cheapest sufficient evidence plus the next unresolved uncertainty.

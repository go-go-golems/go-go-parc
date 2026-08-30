---
title: PCA-Z80 Research Brief — Synthesis-Shaped Representation
status: assigned
type: architecture-garden-research-guideline
created: 2026-08-29
repository: /home/manuel/code/wesen/2026-08-28--pca-gatemate
repository_commit: c07e700652732cd7264af6e2473eb1c6e1f20cc9
pattern_maturity: established-locally
tags: [architecture-garden, pca-z80, synthesis, fpga, representation]
related_notes:
  - "[[Research/Software Architecture Garden/pca-z80/index]]"
  - "[[Research/Software Architecture Garden/pca-z80/guidelines/00 - Shared Research and Subentry Guidelines]]"
---

# Synthesis-Shaped Representation — Research Brief

## Assignment

Write `designs/04 - Synthesis-Shaped Representation.md`. Show how logically equivalent or sufficient representations produce different inferred memories, resource counts, timing, and routing outcomes on GateMate. Determine which lessons are device-specific and which generalize to FPGA design.

## Central question

When does representation become part of physical architecture rather than an implementation detail?

Use both major cases: firmware ROM and mesh packet/topology width.

## Required local evidence

Read completely:

- `pca_z80/rtl/obj_memio.sv`
- `pca_z80/tools/zasm.py`
- `pca_z80/tools/check_gatemate_rom.py`
- `pca_z80/sim/tb_post_synth.sv`
- `pca_z80/rtl/pca_types.sv`
- `pca_z80/rtl/pca_router.sv`
- `pca_z80/rtl/pca_mesh.sv`
- `pca_z80/config/z80_objects.json`
- `pca_z80/Makefile`
- ticket scripts 15, 16, 19, and 20

Read design-docs 03, 05, and 06 plus diary Steps 23, 30, 33, and 34.

## Required case study A: firmware ROM

Explain and reproduce as practical:

- asynchronous versus registered reads;
- 256×8 versus larger inference threshold behavior;
- partial `$readmemh` plus procedural fill failure;
- full padded 512-byte image;
- one `CC_BRAM_20K` with nonzero `INIT_*`;
- post-synthesis execution.

Separate “memory resource allocated,” “firmware bytes initialized,” and “processor executed firmware.”

## Required case study B: packet/topology

Build the experiment table from evidence:

| Topology | Packet | LUTs | Placement timing | Routing result |
|---|---:|---:|---:|---|
| 3×3 | 67 | measured | measured | bounded failure |
| 3×2 | 67 | measured | measured | bounded failure |
| 3×2 | 43 | measured | measured | routed success |

Explain what changed physically when unused routers were removed and coordinate fields narrowed.

## External research requirements

Research:

1. FPGA block-RAM inference templates and synchronous-read requirements;
2. Yosys memory inference and GateMate BRAM mapping documentation;
3. official Cologne Chip/GateMate memory and routing documentation;
4. HDL coding guidelines for portable memory inference;
5. mux/fanout/interconnect width costs in FPGA fabrics;
6. placement-versus-routing timing and congestion;
7. one comparison from another FPGA family or open-source flow.

Use exact tool versions. A claim true for current Yosys GateMate mapping must not be presented as a language-level Verilog law.

## Required experiments

Run at least one ROM inference matrix case and one packet/topology synthesis comparison. Preserve commands, versions, resource lines, and bounded timeout. Remove stale outputs before route experiments so an old bitstream cannot be mistaken for new success.

## Required argument

Explain:

- why semantically adequate RTL can be synthesis-hostile;
- why pre-route timing and capacity do not imply route closure;
- why complete memory images are part of the hardware contract;
- why width reduction is valid only under an explicit coordinate limit;
- which compatibility concessions (`PKT_W` expression, flattened arrays, scalar constants) belong to tools rather than domain semantics;
- when portability is worth extra representation cost.

## Textbook structure

Begin with the distinction between simulation semantics and mapped hardware. Present the ROM case before the wider mesh case so the reader sees the same principle at two scales. Include actual Yosys/nextpnr output, primitive snippets, a resource table, and a causal account of each correction.

## Candidate subentries

- Inference-Safe Synchronous ROM.
- Complete Physical Memory Image.
- Resource Allocation Is Not Content Proof.
- Flattened Packed Port Arrays.
- Coordinate Width as Routing Budget.
- Topology Matched to Occupied Endpoints.

## Definition of done

A reviewer can reproduce one inference and one routing result, identify the tool/device scope of every rule, and explain why logical equivalence does not guarantee equivalent physical implementation.

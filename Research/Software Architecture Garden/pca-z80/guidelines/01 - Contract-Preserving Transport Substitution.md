---
title: PCA-Z80 Research Brief — Contract-Preserving Transport Substitution
status: assigned
type: architecture-garden-research-guideline
created: 2026-08-29
repository: /home/manuel/code/wesen/2026-08-28--pca-gatemate
repository_commit: c07e700652732cd7264af6e2473eb1c6e1f20cc9
pattern_maturity: candidate-ecosystem-pattern
tags: [architecture-garden, pca-z80, adapters, refinement, transport]
related_notes:
  - "[[Research/Software Architecture Garden/pca-z80/index]]"
  - "[[Research/Software Architecture Garden/pca-z80/guidelines/00 - Shared Research and Subentry Guidelines]]"
---

# Contract-Preserving Transport Substitution — Research Brief

## Assignment

Write `designs/01 - Contract-Preserving Transport Substitution.md`. Explain how PCA-Z80 replaces direct object-bus transport with packetized mesh transport while preserving the processor-facing contract and unchanged object behavior. Determine whether this deserves its proposed name after comparing it with established refinement, adapter, and interconnect literature.

## Central question

Which observable contract remains invariant when addressing, latency, topology, acknowledgement path, and physical implementation all change?

The entry must answer this in terms of fields, state transitions, and model-visible CPU state—not merely say that adapters decouple components.

## Required local evidence

Read completely:

- `pca_z80/rtl/z80_obj.sv`
- `pca_z80/rtl/z80_core.sv`
- `pca_z80/rtl/z80_mesh_adapter.sv`
- `pca_z80/rtl/z80_mesh_core.sv`
- `pca_z80/rtl/top.sv`
- `pca_z80/sim/run_integ.py`
- `pca_z80/sim/run_mesh_integ.py`
- `pca_z80/sim/test_integ.py`
- `pca_z80/sim/test_mesh_integ.py`

Read diary Steps 29–33 and design-docs 05–06. Use the code as authority and the docs to recover intent and failure history.

## Required concrete comparison

Construct a side-by-side trace of one instruction that uses at least two objects, such as `ADD A,1`:

```text
Direct path:
decode → PC → memory → register → ALU → register → flags

Mesh path:
decode → master adapter → routers → endpoint adapter → same object
       ← master adapter ← routers ← response adapter ← same object
```

For each object operation, identify:

- fields that remain identical;
- transport-only fields introduced by the mesh;
- states added by adapters;
- model-visible result;
- latency difference;
- error behavior.

## External research requirements

Search by invariant rather than by the proposed title. Research:

1. refinement mappings and observational equivalence;
2. ports-and-adapters or protocol-adapter architecture, while separating software modularity claims from clocked RTL semantics;
3. latency-insensitive design and wrapper-based communication;
4. bus bridges that preserve transaction semantics across protocols;
5. at least one NoC endpoint/network-interface implementation;
6. one counterexample where an adapter changes ordering, completion, or error semantics.

Prioritize original latency-insensitive-design papers, formal refinement literature, official bus protocol/bridge documentation, and maintained RTL source. Do not claim equivalence merely because two interfaces have similarly named fields.

## Required experiment

Run one direct and one mesh integration program and capture:

- final architectural state;
- retired instruction count;
- mesh transaction counts;
- cycle or wall-time difference if measured consistently.

Then introduce one bounded adapter mutation or test-only perturbation—such as dropping returned ALU data—and show that direct mode still passes while mesh differential verification fails. Do not leave the mutation in production code.

## Required argument

The study must explain:

- why retaining the direct path is part of the pattern rather than temporary duplication;
- what constitutes the refinement boundary;
- why unchanged slave modules are stronger evidence than duplicated mesh-specific objects;
- which semantics are not preserved, especially latency and transport error state;
- when transport substitution would require changing the domain contract instead.

## Pattern forces

At minimum analyze:

| Force | Question |
|---|---|
| Reuse | Can tested objects remain unchanged? |
| Correctness | Which observations must be equivalent? |
| Latency | Is timing part of the public contract? |
| Failure | How do packet errors appear at the original boundary? |
| Verification | What independent oracle establishes equivalence? |
| Physical cost | Does preserving the interface create expensive adapters? |

## Textbook structure

Open by defining the direct contract and why transport replacement is dangerous. Introduce the mesh only after the invariant is explicit. Include:

- a direct-versus-mesh architecture diagram;
- a real `bus_req_t`/packet field table;
- one complete instruction trace;
- a table of preserved and intentionally changed observations;
- the historical ALU response-data failure;
- applicability and non-applicability guidance.

## Candidate subentries

Create separate subentries only if research justifies them:

- Selectable Reference and Production Architecture.
- Unchanged Object Behind an Adapter.
- Bus-to-Packet Envelope.
- Centralized Coordinate Lookup.

Otherwise keep them as tactics inside the parent entry.

## Definition of done

The entry is done when a reviewer can state precisely what “preserved” means, reproduce one direct/mesh equivalence test, identify a semantic change the pattern permits, and distinguish this pattern from a generic adapter description.

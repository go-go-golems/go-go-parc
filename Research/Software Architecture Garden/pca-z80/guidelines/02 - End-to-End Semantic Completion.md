---
title: PCA-Z80 Research Brief — End-to-End Semantic Completion
status: assigned
type: architecture-garden-research-guideline
created: 2026-08-29
repository: /home/manuel/code/wesen/2026-08-28--pca-gatemate
repository_commit: c07e700652732cd7264af6e2473eb1c6e1f20cc9
pattern_maturity: candidate-ecosystem-pattern
tags: [architecture-garden, pca-z80, protocols, acknowledgement, exactly-once]
related_notes:
  - "[[Research/Software Architecture Garden/pca-z80/index]]"
  - "[[Research/Software Architecture Garden/pca-z80/guidelines/00 - Shared Research and Subentry Guidelines]]"
---

# End-to-End Semantic Completion — Research Brief

## Assignment

Write `designs/02 - End-to-End Semantic Completion.md`. Explain why packet delivery, object acceptance, response return, and CPU completion are distinct events, and how PCA-Z80 orders them to preserve one architectural side effect.

## Central question

At which transition may the requester safely treat an operation as complete?

The answer must identify the component that owns each acknowledgement and the invariant it establishes. Avoid vague “exactly once” language unless the scope and failure model are explicit.

## Required local evidence

Read completely:

- `pca_z80/rtl/z80_mesh_adapter.sv`
- `pca_z80/rtl/pca_router.sv`
- `pca_z80/rtl/pca_cell.sv`
- `pca_z80/rtl/z80_obj.sv`
- `pca_z80/rtl/obj_pc.sv`
- `pca_z80/rtl/obj_memio.sv`
- `pca_z80/rtl/obj_alu.sv`
- `pca_z80/sim/tb_pca_mesh.sv`
- `pca_z80/sim/run_mesh_integ.py`

Inspect the ALU response-data correction and diary Steps 29, 32, and 33. Identify tests that prove anti-double behavior and tests that remain missing, especially reset and malformed-response paths.

## Required transaction trace

Write a clock-ordered trace for both:

1. a state-changing write such as PC increment or GPIO write;
2. an ALU request with `we=1` whose response data remains architecturally meaningful.

Name these events separately:

```text
request latched
packet injection accepted
destination router presents packet
slave object accepts operation
inbound packet drains
response packet accepted
master validates response
architectural ack asserted
architectural request released
```

Show why collapsing any two adjacent events can be incorrect.

## External research requirements

Research:

1. the end-to-end argument in system design;
2. linearizability and operation linearization points;
3. four-phase or return-to-zero handshakes;
4. ready/valid and request/ack protocol semantics;
5. exactly-once side effects under retries and failure assumptions;
6. network delivery versus application-level acknowledgement;
7. one hardware protocol with separate request and response channels.

Use original papers and official protocol specifications. Compare terminology carefully: a network “ack” may acknowledge buffering, transfer, execution, persistence, or response receipt.

## Required experiments

Implement bounded test-only experiments for at least two of:

- hold a request many cycles after ack and prove one side effect;
- delay destination acceptance and prove packet/request stability;
- inject a response with wrong source or echoed address and observe protocol error;
- reset during injection or response drain and record current behavior;
- compare request, accept, and response counters after a complete program.

If a promised invariant lacks a test, label it an open correctness obligation rather than filling the gap with prose.

## Required invariants

State and evaluate:

- Request stability while asserted.
- One object acceptance per architectural request assertion.
- No response before object acceptance.
- No new request before the prior architectural request releases.
- Matching response metadata before architectural ack.
- Conservation after drain: requests = accepts = responses.
- Reset cancellation semantics.

Use temporal notation or state-machine pseudocode where it improves precision.

## Required failure analysis

Explain the historical ALU failure:

- `we=1` carried operands;
- object `rdata` carried `{flags,result}`;
- the first adapter zeroed write responses;
- the CPU loop diverged despite successful delivery and object execution.

This is central evidence that delivery and semantic completion differ.

## Textbook structure

Begin with the ambiguity of “acknowledged,” not with module names. Include:

- a sequence diagram with all acknowledgement boundaries;
- master and slave state diagrams;
- a table mapping each ack to its meaning;
- one side-effect trace and one ALU-return trace;
- observed failures, missing tests, and reuse limits.

## Candidate subentries

- Held-Request Transaction.
- Capture-Once Slave.
- Request Drain Before Response.
- Response Metadata Validation.
- Transaction Conservation Check.
- Sticky Protocol Error.

Treat these as supporting entries, not peer architectural patterns.

## Definition of done

A reviewer should be able to identify the architectural completion point, explain why router ack is insufficient, state the failure model under which one side effect is guaranteed, and name any untested reset/error obligations.

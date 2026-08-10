---
title: PBUI and CLIM Research Cluster
tags:
  - research
  - pbui
  - clim
  - semantics
  - transcripts
---

# PBUI and CLIM Research Cluster

## What this cluster is about

This is the largest long-form research program in the archive. It begins with **presentation-based user interfaces**—the CLIM tradition of typed presentations, translators, commands, and views—and expands into a broader semantic architecture for modern interfaces. The generated documents repeatedly ask the same foundational question: how can a UI make meaning, admissible interaction, state change, explanation, and composition explicit enough to serialize, test, inspect, and eventually prove?

The work moves through three related modes:

1. **Historical/architectural grounding:** CLIM, Genera Dynamic Windows, Smalltalk, HyperCard, and the existing PBUI/widget DSL are treated as evidence.
2. **Subsystem research:** fifteen bounded projects examine identity, occurrence lifecycle, selectors, fixed points, capabilities, typed ports, composition, links, interaction machines, effects, incremental evaluation, local-first topology, accessibility, proof-carrying compilation, and conformance.
3. **Clean-slate synthesis:** later documents ask what survives if CLIM is treated as historical evidence rather than as the decomposition to preserve.

## Core research claims

- A semantic UI should distinguish **denotation** from its visible occurrences and from the actions available for those occurrences.
- Selectors and translators are not merely UI plumbing: they form a typed language of admissible interaction and conversion reachability.
- Eligibility, capabilities, dependency closure, and derived UI state are naturally expressed as monotone rules and least fixed points.
- Applications should be open systems with typed ports and explicit wiring rather than opaque component trees.
- Links, unlinking, duplication, and deletion are graph rewrites; editable views require bidirectional laws; long-running interaction is naturally coalgebraic.
- Incremental recomputation, collaboration, accessibility, and proof-carrying compilation are different concerns and should not be collapsed into a single “UI state” abstraction.
- The practical research method is deliberately capsule-based: each subsystem has a bounded claim, executable evidence, negative results, and a handoff contract before composition.

## Main research program

The P01–P15 series is best read as a research curriculum rather than fifteen unrelated reports:

- **P01–P03:** semantic identity, occurrence lifecycle, and typed selector languages.
- **P04–P06:** recursive/fixed-point rules, capabilities/invariants, and typed ports/binding/quotient compilation.
- **P07–P09:** open components, bidirectional links, and coalgebraic interaction machines.
- **P10–P12:** algebraic effects, differential/incremental evaluation, and local-first replicated topology.
- **P13–P15:** explanation/accessibility, mechanized semantic kernels and proof-carrying compilation, and conformance/model-based testing.

The program then produces implementation compendia, a subsystem handbook, a research-project index, and composition reports. Multiple branches exist, so the same P01–P15 names appear under different conversation directories; those are revisions or regenerated packages, not automatically distinct theories.

## Major deliverables

### Program-level documents

- [[Transcripts/Research/10 - PBUI-MATHS Pattern Zoo Handbook|PBUI-MATHS Pattern Zoo Handbook]] — evidence-backed synthesis of fourteen recurring patterns, separating independent source families from duplicate branches and pairing first-week explanations with category theory and abstract mathematics.
- [[Transcripts/2026/08/06/Branch Branch CLIM UI in React/PBUI-RESEARCH-PROJECTS-COMPENDIUM|PBUI research projects compendium]] — the fifteen-project program, composition pass, and evidence protocol.
- [[Transcripts/2026/08/06/Branch Branch CLIM UI in React/PBUI-SUBSYSTEM-RESEARCH-PROGRAM-HANDBOOK|PBUI subsystem research program handbook]] — graduate/engineering-research framing for independent capsules and controlled composition.
- [[Transcripts/2026/08/06/Branch Branch CLIM UI in React/PBUI-RESEARCH-PROJECT-INDEX|PBUI research project index]] — navigation and project-level status.
- [[Transcripts/2026/08/06/CLIM UI in React/BEYOND-CLIM-PROOF-ORIENTED-PRESENTATION-SYSTEM-ARCHITECTURES|Beyond CLIM]] — clean-slate semantic alternatives: algebras/effects, fixed points, open systems, graph rewriting, lenses, coalgebra, incremental computation, and CRDTs.
- [[Transcripts/2026/08/06/Branch CLIM UI in React/PRESENTATION-BASED-UI-CLIM-DESIGN-AND-IMPLEMENTATION|Presentation-based UI / CLIM design and implementation]] — historical and implementation-oriented architecture.
- [[Transcripts/2026/08/06/Branch Branch Branch CLIM UI in React/SENTINEL-KERNEL-THESIS.md|Sentinel kernel thesis]] — proof-oriented semantic kernel and proof-carrying compilation direction.
- [[Transcripts/2026/08/06/Branch Branch CLIM UI in React/Semantic-Interfaces-Textbook|Semantic Interfaces textbook]] — educational presentation of the semantic architecture.

### P01–P15 capsule artifacts

The branch directories contain Markdown/PDF pairs for the individual capsules: semantic identity; occurrence lifecycle; typed selectors; recursive fixed points; operations/capabilities/invariants; typed ports and quotient compilation; open components; bidirectional links; coalgebraic interaction machines; algebraic effects and workflow handlers; incremental differential evaluation; local-first replicated topology; explanation and proof-relevant interaction; mechanized semantic kernels; and conformance/model-based testing. The complete path-level register is in [[Transcripts/Research/01 - Markdown Thesis and PDF Inventory|the artifact inventory]].

### Earlier PBUI/widget research

- [[Transcripts/2026/07/21/React PBUI Widget DSL Guide/pbui-widget-dsl-intern-guide|PBUI widget DSL intern guide]] and [[Transcripts/2026/07/21/React PBUI Widget DSL Guide/docgraph-pbui-delivery-readme|PBUI delivery README]].
- [[Transcripts/2026/07/21/Widget DSL Extension Design — Streaming Chat/widget-dsl-streaming-chat-architecture-report|Streaming-chat widget DSL architecture report]].
- [[Transcripts/2026/07/22/PBUI WM Integration Possibilities/pbui_wails_qml_integration_report|PBUI/WM integration report]].
- [[Transcripts/2026/07/26/Codebase Analysis and Refactor/PBUI_REACT_ARCHITECTURE_REVIEW|PBUI React architecture review]].
- [[Transcripts/2026/07/26/Frontend Optimization and Tutorial/pbui-duckdb-integration|PBUI DuckDB integration notes]].

## Source conversations

- [[Transcripts/2026/08/06/CHATGPT TRANSCRIPT - CLIM UI in React|CLIM UI in React]] and its branch variants.
- [[Transcripts/2026/07/21/CHATGPT TRANSCRIPT - React PBUI Widget DSL Guide|React PBUI Widget DSL Guide]].
- [[Transcripts/2026/07/21/CHATGPT TRANSCRIPT - Widget DSL Extension Design — Streaming Chat|Widget DSL streaming-chat extension]].
- [[Transcripts/2026/07/22/CHATGPT TRANSCRIPT - PBUI WM Integration Possibilities|PBUI WM integration possibilities]].
- [[Transcripts/2026/07/30/CHATGPT TRANSCRIPT - Frontend for Lean Proof|Frontend for Lean proof]].

## How to read it

Start with the handbook, then the P01–P06 capsules, then *Beyond CLIM*. Read P07–P15 as the composition and proof-oriented extension. Use the PDFs for polished reading and the Markdown for searchable source, citations, and version comparison.

> [!warning] Generated-research caveat
> These are design studies and generated research packages. They contain executable sketches, proposed laws, and evidence plans, but a “thesis” filename does not by itself establish peer review, formal proof, or production validation.

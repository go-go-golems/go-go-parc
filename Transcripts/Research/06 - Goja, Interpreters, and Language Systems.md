---
title: Goja, Interpreters, and Language Systems Research Cluster
tags:
  - research
  - goja
  - interpreters
  - programming-languages
  - transcripts
---

# Goja, Interpreters, and Language Systems Research Cluster

## Research arc

The Goja material treats JavaScript as a language/runtime design problem under failure, authority, and durability constraints—not as configuration glued onto Go. Tiny-IDP, Langblocks, the “malleable interpreter” work, semantic probes, and hosted-Goja platform studies all ask how an expressive language can be embedded while keeping privileged state and effects under host control.

## Main ideas

- **Explicit control state:** durable continuations should serialize named control state and bounded environments, not arbitrary Goja heaps or closures.
- **Capabilities over ambient authority:** secrets, browser access, cryptography, durable state, and atomic effects stay in Go and are exposed through scoped capabilities.
- **Plans before effects:** JavaScript constructs effect proposals or inert plans; a privileged interpreter validates and commits them.
- **Generation-pinned runtime ownership:** worker/VM lifecycles need exclusive ownership, generation checks, cancellation, and fail-stop replacement.
- **Semantic instrumentation:** probes should attach at language-level boundaries, with typed state, bounded helpers, event ABIs, and replay/model-comparison evidence. The probe monograph is an architecture proposal, not a completed soundness theorem.
- **Hosted execution:** the Go host owns listener/router/request/session/auth/CSRF/resource/authorization/rate/audit/shutdown concerns; JavaScript declares application behavior. The hosted-Goja documents label current implementation, design principle, and target platform separately.

## Major deliverables

- [[Transcripts/2026/07/21/Interpreter Constructs Analysis — tiny-idp Goja/tiny-idp-interpreter-theory-companion|Tiny-IDP interpreter theory companion]].
- [[Transcripts/2026/07/21/Interpreter Constructs Analysis — tiny-idp Goja/tiny-idp-goja-interpreter-monograph|Tiny-IDP Goja interpreter monograph]].
- [[Transcripts/2026/07/21/Branch Interpreter Constructs Analysis — Abstraction Machine/malleable-js-interpreter-compiler-monograph|Malleable JS interpreter/compiler monograph]].
- [[Transcripts/2026/07/21/Branch Interpreter Constructs Analysis v2 — Langblocks/langblocks-framework-design|Langblocks framework design]].
- [[Transcripts/2026/07/21/Hosting Platform Analysis — Goja Cloud/hosted_goja_platform_textbook|Hosted Goja platform textbook]].
- [[Transcripts/2026/07/21/Hosting Platform Analysis — Goja Cloud/agent_native_application_cloud_founder_dossier|Agent-native application cloud founder dossier]].
- [[Transcripts/2026/07/21/JavaScript Interpreter Instrumentation — Goja eBPF/verified_semantic_probes_monograph.pdf|Verified semantic probes monograph]].
- [[Transcripts/2026/08/08/AST-driven Macro Processor/README|AST-driven macro processor package]].

## Source conversations

- [[Transcripts/2026/07/21/CHATGPT TRANSCRIPT - Interpreter Constructs Analysis — tiny-idp Goja|Interpreter Constructs Analysis — tiny-idp Goja]].
- [[Transcripts/2026/07/21/CHATGPT TRANSCRIPT - JavaScript Interpreter Instrumentation — Goja eBPF|JavaScript Interpreter Instrumentation — Goja/eBPF]].
- [[Transcripts/2026/07/21/CHATGPT TRANSCRIPT - Hosting Platform Analysis — Goja Cloud|Hosting Platform Analysis — Goja Cloud]].
- [[Transcripts/2026/07/21/CHATGPT TRANSCRIPT - Branch Interpreter Constructs Analysis v2 — Langblocks|Langblocks branch]].

## Caveats

The monographs deliberately distinguish runtime discipline from static soundness, capability restriction from hostile-process sandboxing, and target platform from current code. Empty or duplicate generated Markdown/PDF files exist in some branch directories; use readable Markdown and explicit evidence labels as the primary source.

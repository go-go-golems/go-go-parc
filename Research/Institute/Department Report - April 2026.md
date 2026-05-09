---
title: Department Report - April 2026
aliases:
  - April 2026 Activity Report
  - Lab Report April 2026
tags:
  - research
  - institute
  - report
  - department
status: active
type: report
created: 2026-04-03
---

# Department Report — April 2026

An overview of recent research activity across the lab, based on active ChatGPT conversations and projects as of April 3, 2026. The work clusters into six distinct areas of activity, reflecting a lab that is simultaneously building interactive JavaScript tooling, designing embedded systems UIs, hardening infrastructure, researching programming language theory, and standing up operational tooling.

---

## 1. JavaScript REPL and Introspection Platform

**Status:** Very active — this is the current primary research thrust.

The largest cluster of activity centers on building a persistent, multi-cell JavaScript REPL with deep introspection capabilities, backed by the goja embedded JS engine in Go (the "go-go-goja webrepl" project).

| Conversation | Focus |
|-------------|-------|
| **JS REPL Design Research** | Deep research report on REPL persistence models (Smalltalk → Jupyter → DevTools), IIFE patterns, embedded engine comparison, and scope simulation |
| **JS REPL Introspection Design** | Architecture for static analysis + runtime inspection — how to expose AST, scope resolution, binding provenance to LLM agents |
| **Web UI Review System** | Review/audit of the web frontend for the REPL inspector UI |

**Key findings so far:**
- JavaScript's `let`/`const`/`class` declarations fundamentally cannot survive across separate `eval()` calls due to the ECMA-262 spec's two-environment model (LexicalEnvironment vs VariableEnvironment)
- The async IIFE capture-and-replay pattern was chosen as the persistence strategy because it works *with* the spec rather than against it
- Four approaches were evaluated: var promotion (lossy), IIFE capture (chosen), `with(scopeProxy)` (deprecated, fundamentally broken for `let`/`const`), and Node.js-style source rewriting
- A 38-citation deep research report was produced covering the full design space

**Related project:** SMAILNAIL — the parent project context for the JS REPL work.

---

## 2. Go-Go-OS Frontend and Framework

**Status:** Active — concurrent with the REPL work.

A set of conversations focused on the Go-based application platform (go-go-os), particularly its web frontend, middleware layer, and tooling:

| Conversation | Focus |
|-------------|-------|
| **Glazed Fields Middleware** | Middleware architecture for the Glazed command framework — field processing pipeline |
| **Glazed Fields Credentials Setup** | Credential management integration with Glazed fields/middleware |
| **Credentials and Middleware Setup** | Broader credential flow across the middleware stack |
| **Unified Doc-Tool Design** | Design for a unified documentation tool that integrates with Glazed |
| **Design Doc Review and Implementation** | Review of design documents and implementation planning |
| **Markdown SQL Rendering in Go** | Rendering SQL query results as Markdown — likely for CLI output formatting |
| **Vim Mode Integration** | Adding vim keybinding support to an interactive component |

**Related project:** GO-GO-OS

---

## 3. Embedded Systems and Hardware

**Status:** Active exploration.

Two conversations indicate hardware/embedded work:

| Conversation | Focus |
|-------------|-------|
| **WASM WebUI with ESP32** | Building a web UI for ESP32 using WebAssembly — bringing rich UI to microcontrollers |
| **EINK** | E-ink display project (details in the EINK project workspace) |

**Related projects:** EINK

---

## 4. Infrastructure and DevOps

**Status:** Supportive work — enabling other projects.

Several conversations focus on infrastructure hardening, deployment, and security:

| Conversation | Focus |
|-------------|-------|
| **Firecracker Credential Access Control** | Security model for Firecracker VM credential access |
| **GitHub CI/CD Vault Secrets** | Wiring HashiCorp Vault secrets into GitHub Actions CI/CD |
| **Open-source Datadog Alternatives** | Evaluating observability platforms (likely for monitoring the lab's services) |
| **VMs in i3 environment** | Running virtual machines within an i3 window manager setup |
| **Go SQLite in Browser** | Running SQLite from Go in the browser — possibly via WASM |

---

## 5. NLP, Embeddings, and AI Applications

**Status:** Exploratory.

| Conversation | Focus |
|-------------|-------|
| **Effective Embeddings for Emails** | Embedding strategies for email content — likely for search or classification |
| **Human Language Processing Models** | Research into language processing models |
| **Capsule Lab Design** | Design for a "capsule lab" — possibly an isolated experiment environment |

**Related project:** TEMPORAL-RELATIONSHIPS — may relate to the NLP/embedding work.

---

## 6. Programming Language Theory and Agent Tooling

**Status:** Foundational research.

| Conversation | Focus |
|-------------|-------|
| **CPS Transformation in Scheme** | Continuation-passing style transformations — fundamental PL theory |
| **Ghidra CodeBrowser Explanation** | Understanding Ghidra's reverse engineering CodeBrowser — binary analysis tooling |
| **Pi-Agent Extension Guide** | Writing extensions for the pi coding agent — meta-tooling |
| **Playwright MCP Headless Issue** | Debugging Playwright MCP server headless mode — operational tooling |
| **OpenClaw Overview** | Overview of the OpenClaw project |
| **ZAI GLM Setup** | Setting up ZAI GLM (likely a language model integration) |

---

## 7. Client/Product Work

**Status:** Ongoing.

| Conversation | Focus |
|-------------|-------|
| **HAIR-BOOKING-APP** | A hair salon booking application (full project workspace) |
| **Simplifying Webchat Component** | Simplifying a webchat UI component |
| **Webchat Component Simplification** | Continuation of the webchat simplification work |

**Related project:** HAIR-BOOKING-APP

---

## Active Projects Summary

| Project | Domain | Status |
|---------|--------|--------|
| **SMAILNAIL** | JS REPL / interactive tooling | Primary research focus |
| **GO-GO-OS** | Go application platform + frontend | Active development |
| **EINK** | E-ink hardware | Active exploration |
| **TEMPORAL-RELATIONSHIPS** | NLP / temporal reasoning | Exploratory |
| **HAIR-BOOKING-APP** | Client product | Ongoing |

---

## Observations

**The lab is prototype-heavy.** Most conversations involve building working systems (REPL prototypes, middleware, embedded UIs), not writing papers. This aligns with the [[From Question to Prototype]] guideline — the primary research output is running code that tests ideas.

**Three work streams are converging.** The JS REPL work (cluster 1), the Glazed framework work (cluster 2), and the agent tooling work (cluster 6) are all circling the same meta-question: *how do you build interactive systems that LLM agents can use effectively?* The REPL exposes JavaScript introspection to agents; Glazed provides structured command output; the pi extensions provide agent-side tooling. These should be treated as facets of one research program, not three separate projects.

**Infrastructure work is enabling but under-documented.** The Firecracker, CI/CD, and observability conversations suggest real infrastructure is being built, but there's no corresponding knowledge base trail. These would benefit from [[Writing a Trip Report]]-style notes so the decisions are traceable.

**The PL theory work (CPS, Scheme) is disconnected.** The continuation-passing style conversation doesn't obviously connect to any active project. This might be pure exploration — which is fine — but a [[Cross-Pollination Notes|cross-pollination note]] explaining how CPS relates to the REPL work (if it does) would be valuable.

---

## Recommendations

1. **Write up the JS REPL research formally.** The deep research report and the two reference docs (JS Scoping, REPL State Persistence Strategies) are a strong start. The Jupyter protocol section and embedded engine comparison from the ChatGPT deep research should become their own knowledge base articles.

2. **Connect the three converging streams.** Schedule a cross-cutting [[The Weekly Demo|demo session]] where the REPL, Glazed, and pi-extension researchers present together. The integration points will become visible.

3. **Create infrastructure decision records.** The Firecracker security model and the Vault-CI/CD wiring are important decisions. They should be written up as technology evaluation docs so the next person understands why things are configured the way they are.

4. **Time-box the NLP exploration.** The email embeddings and language processing conversations are exploratory. Set a deadline for deciding whether to make this a formal research direction or park it.

---
Title: Initial Scan and Subagent Fanout Plan
Ticket: PROJECT-MAPS-001
Status: active
Topics:
    - research
    - projects
    - concept-maps
DocType: design
Intent: long-term
Owners: []
RelatedFiles:
    - Path: Projects/2026
      Note: Corpus for the concept-map research
    - Path: ttmp/2026/06/22/PROJECT-MAPS-001--concept-maps-for-recent-project-topics/sources
      Note: Subagent source reports target directory
ExternalSources: []
Summary: Initial inventory and first subagent fanout plan for concept-mapping recent project reports.
LastUpdated: 2026-06-22T17:04:25.661360382-04:00
WhatFor: Use this to understand the first-batch parallel research plan before reading the source reports.
WhenToUse: Before launching or reviewing subagent reports for PROJECT-MAPS-001.
---


# Initial Scan and Subagent Fanout Plan

## Parent quick pass

Scope: all Markdown files under `Projects/2026/{03,04,05,06}/`, treated as the recent-project corpus.

Quick inventory from filenames/frontmatter:

- Total files: **554**
- By month: **March 64**, **April 180**, **May 201**, **June 109**
- Dominant document types: article/playbook/deep-dive notes, project reports, project notes, and a few reviews/research notes.
- High-signal tags and title clusters: `go`, `goja`, `xgoja`, `javascript`, `react`, `sqlite`, `glazed`, `firmware`, `esp32`, `embedded`, `design-system`, `typography`, `k3s`, `argocd`, `vault`, `keycloak`, `go-minitrace`, `sessionstream`, `rag`, `ocr`, `remarkable`, `loupedeck`, `pi`, `protobuf`, `dsl`.

Initial topic hypothesis: the corpus is not organized around isolated projects, but around recurring platforms and research threads. The first fanout should therefore ask agents to map **topic constellations**: what projects belong together, what concepts recur, what artifacts/reports exist, and which edges should appear in later concept maps.

## First-batch subagent fanout

```mermaid
flowchart TD
    P[Parent orchestrator\nPROJECT-MAPS-001] --> Q[Parent quick pass\nProjects/2026 Mar-Jun\n554 markdown files]
    Q --> D[Design doc\nMermaid fanout plan]
    D --> A1[Agent 1\nHardware / embedded / ESP32\nOutput: sources/01-hardware-embedded-esp32.md]
    D --> A2[Agent 2\nJavaScript runtimes / Goja / xgoja DSLs\nOutput: sources/02-javascript-goja-xgoja-dsls.md]
    D --> A3[Agent 3\nTypography / layout / design systems\nOutput: sources/03-typography-layout-design-systems.md]
    D --> A4[Agent 4\nInfra / auth / deployment / GitOps\nOutput: sources/04-infra-auth-deployment-gitops.md]
    D --> A5[Agent 5\nAI agents / transcripts / observability\nOutput: sources/05-ai-agents-transcripts-observability.md]
    D --> A6[Agent 6\nData / RAG / OCR / search / knowledge systems\nOutput: sources/06-data-rag-ocr-search.md]
    D --> A7[Agent 7\nWeb UI / apps / media / productivity surfaces\nOutput: sources/07-web-ui-apps-media-productivity.md]
    A1 --> G[Post-batch format guidelines\nCompare report shapes and define schema]
    A2 --> G
    A3 --> G
    A4 --> G
    A5 --> G
    A6 --> G
    A7 --> G
    G --> M[Later concept maps by topic\nMermaid/Canvas/summary docs]
```

## Agent task slices

### Agent 1: Hardware / embedded / ESP32

Inspect projects and reports about ESP32, ESP-IDF, M5Stack, AtomS3R, PaperS3, PicoCalc, Loupedeck, reMarkable, thermal printers, BLE/WiFi provisioning, display pipelines, firmware flashing, and physical-device debugging.

### Agent 2: JavaScript runtimes / Goja / xgoja DSLs

Inspect go-go-goja, goja, xgoja, jsverbs, Geppetto bindings, Go-backed JavaScript APIs, generated modules, durable objects, runtime plans, auth hosts, TypeScript support, and DSL patterns.

### Agent 3: Typography / layout / design systems

Inspect Pretext, typography, print layout, Canvas text measurement, DMETA, TTC design systems, CSS visual diff, Storybook/widget systems, layout constraints, visual parity, and generated UI/design artifacts.

### Agent 4: Infra / auth / deployment / GitOps

Inspect K3s, Argo CD, Terraform, Vault, Keycloak/OIDC, Coolify, GitHub App/OIDC tokens, DNS/TLS, backup, deployment outages, release trains, package publishing, and hosted environments.

### Agent 5: AI agents / transcripts / observability

Inspect Pi extensions/core, go-minitrace, transcript analysis, sessionstream, Pinocchio/Geppetto agent flows, LLM proxy/provider work, tool-calling behavior, dashboards, observability, compaction/search extensions, and agent readability.

### Agent 6: Data / RAG / OCR / search / knowledge systems

Inspect RAG evaluation, OCR/book workflows, SQLite/Bleve/FAISS, codebase browser/indexing, Readwise, document co-read, corpus pipelines, search/reranking, data export/import, and knowledge-base workflows.

### Agent 7: Web UI / apps / media / productivity surfaces

Inspect React/browser apps, chat overlays, admin DSLs, Wails/md-view, screencast/audio/video/podcast pipelines, browser automation extensions, web chat, static sites, productivity tools, and end-user app shells not fully covered by other slices.

## First-batch reporting intent

The first batch is intentionally semi-structured: each report should be useful on its own, but the parent will compare the seven outputs afterward and derive stronger reporting guidelines for the next pass. Minimum expected evidence:

- The projects/reports found, with file paths.
- Topic clusters and subclusters.
- Repeated concepts, technologies, methods, and failure modes.
- Candidate concept-map nodes and edges.
- Open questions and overlaps with other agents' slices.

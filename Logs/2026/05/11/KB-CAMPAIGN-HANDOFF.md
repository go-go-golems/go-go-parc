# KB Campaign Handoff: Indexed vs Remaining Projects and Future Batch Plan

## Purpose

This document exists to make the rest of the KB campaign easy to hand off.

It answers three questions:
1. Which project reports have already been analyzed and indexed?
2. Which project reports have **not** been analyzed yet?
3. What are sensible future batches for continuing the work?

## Current campaign state

- **Total project reports found**: 167 canonical reports (168 raw files, including one duplicate Racket report variant)
- **Analysis slots completed**: 55
- **Unique project reports analyzed/indexed**: 51
- **Unique project reports still unindexed / unanalyzed**: 116

### Why 49 analysis slots but only 45 unique projects?

A few projects were revisited in later batches because they became useful for cross-batch concept counting or because a later batch reframed them in a different cluster:
- Smalltalk-80 VM
- Capsule Lab
- SToMS3R
- a few runtime/auth projects indirectly fed later synthesis

For handoff purposes, **the important number is 51 unique project reports already covered** after Batch C / Batch 9.

### Completed after this handoff was first drafted

- **Batch C / Batch 9 — Tree-sitter and structured text systems** is complete. See [[KB-BATCH9-tree-sitter-structured-text]].
- Created [[On-Ramp/tree-sitter-for-go-tools]].
- Updated the canonical index through project 55.

---

## Unique project reports already analyzed / indexed

1. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/03/15/PROJ - ZK Tool.md`
2. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/03/16/PROJ - Keycloak Identity Platform on Coolify.md`
3. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/03/16/PROJ - Smailnail OIDC Identity and Hosted Auth.md`
4. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/03/16/PROJ - go-go-goja jsverbs - JavaScript to Glazed Commands.md`
5. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/03/18/PROJ - Smalltalk-80 VM - Blue Book Interpreter in Go.md`
6. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/03/18/PROJ - Smailnail - Hosted Identity, Terraform, and Claude Fix.md`
7. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/03/18/PROJ - go-go-goja Plugins - Since origin main.md`
8. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/03/18/PROJ - go-go-mcp - Hosted OIDC and Smailnail Delivery.md`
9. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/03/19/PROJ - Remarquee - reMarkable Toolkit.md`
10. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/03/23/PROJ - PaperS3 WAMR Debugging - Embedded Wasm Root Cause.md`
11. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/03/25/PROJ - Hair Booking - MVP Buildout, Hosted Auth, Vault, and Production Fixes.md`
12. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/03/25/PROJ - Terraform Infra - Vault Platform Bring-Up, Auth Hardening, and Hair-Booking Handoff.md`
13. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/03/27/PROJ - CoinVault on K3s - First Real GitOps App.md`
14. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/03/27/PROJ - Hetzner K3s Platform - Single-Node GitOps Bring-Up.md`
15. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/03/27/PROJ - Vault on K3s - Auth and Secret Delivery Platform.md`
16. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/03/28/PROJ - Geppetto - Open Responses and Chat Boundary Cutover.md`
17. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/03/31/PROJ - Firecracker VM - Guest Bring-Up, Host-Mediated Secrets, and Isolation Design.md`
18. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/04/02/PROJ - Capsule Lab - A Sandboxed JS Capsule Runtime in the Browser.md`
19. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/04/02/PROJ - Cardputer Web Serial Demo - Technical Project Report.md`
20. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/04/02/PROJ - Glazed Secret Redaction and Vault Bootstrap - Technical Project Report.md`
21. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/04/02/PROJ - Sqleton SQL Command Cleanup - Technical Project Report.md`
22. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/04/03/PROJ - go-go-goja REPL API - Profiles, IIFE Rewriting, and AST-Driven Session Semantics.md`
23. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/04/05/PROJ - Wi-Fi Audio Cues Lab - ESP32-S3 Audio Feedback for Wi-Fi Events.md`
24. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/04/08/PROJ - Glazed Serve - Help Browser, Embedded Docs, and SPA.md`
25. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/04/08/PROJ - Goja REPL Hardening.md`
26. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/04/09/PROJ - Glazed Static Help Export - render-site and Static Snapshot Publishing.md`
27. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/04/10/PROJ - Minitrace Query Commands - Sqleton-Inspired SQL Verb System.md`
28. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/04/10/PROJ - Screencast Studio - Architecture and Runtime Deep Dive.md`
29. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/04/12/PROJ - Goja vs Sobek Deep Analysis.md`
30. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/04/14/PROJ - E2E Encrypted Storage Prototype.md`
31. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/04/17/PROJ - BYOK Host - Project Report.md`
32. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/04/20/PROJ - JS Discord Bot - Adding jsverbs Support.md`
33. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/04/20/PROJ - JS Discord Bot - Building a Discord Bot with a JavaScript API.md`
34. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/04/21/PROJ - go-minitrace - JS Commands and Structured Query Catalog PR #6.md`
35. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/04/22/PROJ - JS Discord Bot Framework.md`
36. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/04/25/PROJ - go-go-goja Node-like Primitives - Technical Deep Dive.md`
37. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/04/27/PROJ - go-minitrace - Local Query Repository Config.md`
38. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/04/28/PROJ - SToMS3R - AtomS3R Lite Thermal Printer Firmware.md`
39. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/05/02/PROJ - Wish Git - OAuth Scoped Git over SSH for Coding Agents.md`
40. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/05/03/PROJ - Agent Enroll - Kanban Agent Credential MVP Deep Dive.md`
41. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/05/05/PROJ - uLisp PicoCalc - From Cross-Compilation to a Lisp Machine in Your Hand.md`
42. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/05/06/PROJ - uLisp PicoCalc Firmware Split - CMake Modularization Report.md`
43. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/05/09/PROJ - AUTODISCO - Keyhive Access Control Architecture.md`
44. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/04/11/PROJ - Loupedeck Live Hello World - Serial Go Driver.md`
45. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/03/22/PROJ - Gnosis Layout Engine - PaperS3 UI Operating System.md`
46. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/03/15/PROJ - Query Treesitter - Tree-sitter Query Language Prototypes and Design.md`
47. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/03/15/PROJ - Sanitize - Tree-sitter Structured Text Sanitizer.md`
48. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/03/15/PROJ - Tree-sitter Templating - Syntax-Aware Code Expansion System.md`
49. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/03/27/PROJ - Sanitize - JSON Recovery Experiments and Limits.md`
50. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/03/27/PROJ - Sanitize - YAML Sanitizing Deep Dive.md`
51. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/03/15/PROJ - Scenario Runtime Workbench - Scenario-Driven Reconciliation Demo.md`

---

## Unique project reports not yet analyzed / indexed

> Note: This section still preserves the original raw backlog listing from the first handoff draft. Batch C items in this list have now been completed; use the completed list above and the canonical index for authoritative progress.

1. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/03/15/PROJ - Coolify Hetzner - Self-Hosted Deployment Platform.md`
2. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/03/15/PROJ - CozoDB Editor - SEM Streaming, Widgetization, and Hydration Refactor.md`
3. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/03/15/PROJ - Query Treesitter - Tree-sitter Query Language Prototypes and Design.md`
4. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/03/15/PROJ - Sanitize - Tree-sitter Structured Text Sanitizer.md`
5. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/03/15/PROJ - Scenario Runtime Workbench - Scenario-Driven Reconciliation Demo.md`
6. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/03/15/PROJ - Tree-sitter Templating - Syntax-Aware Code Expansion System.md`
7. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/03/16/PROJ - Scopedjs Runtime and Demo - Geppetto and Pinocchio.md`
8. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/03/16/PROJ - Smailnail Coolify Deployment.md`
9. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/03/16/PROJ - Smailnail Hosted Backend and SPA.md`
10. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/03/17/PROJ - Claude Code Hook Analytics - Full-Stack Session Telemetry.md`
11. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/03/17/PROJ - Claude Code Hook Events Logger - SQLite Analytics for Claude Sessions.md`
12. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/03/17/PROJ - CoinVault - RAG Web Chat for Gold Coin Inventory.md`
13. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/03/17/PROJ - Scopedjs Runtime - Geppetto Final State.md`
14. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/03/17/PROJ - reMarkable Cleanup - Tablet Root Reorganization.md`
15. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/03/18/PROJ - Geppetto - Opinionated JS APIs and Engine Profiles.md`
16. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/03/19/PROJ - CozoScript Web UI - CodeMirror Language Package and Browser Editor.md`
17. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/03/19/PROJ - Smailnail IMAP and Sieve Expansion Report.md`
18. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/03/19/PROJ - close-dependabot-prs - Dependabot PR Merge Skill.md`
19. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/03/21/PROJ - DOM Scraping Experiment - Web to Markdown via JS DOM Queries.md`
20. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/03/21/PROJ - Glyph Protractor Algorithm - PaperS3 Handwriting Recognition.md`
21. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/03/21/PROJ - PaperS3 Firmware - Setup and Build Workflow.md`
22. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/03/22/PROJ - Claude Agent SDK - Teaching an AI to Write Web Scrapers.md`
23. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/03/22/PROJ - CozoDB Editor - Notebook Packaging and JavaScript Preset.md`
24. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/03/22/PROJ - Federated Modules - Single-Origin Runtime Demo.md`
25. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/03/22/PROJ - Gnosis Compiler - Python Rebuild and Web Experimentation Tool.md`
26. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/03/22/PROJ - LibriVox Player - Retro Macintosh Browser Audio Prototype.md`
27. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/03/22/PROJ - PaperS3 E-Reader - Interactive Book Reader on E-Ink.md`
28. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/03/22/PROJ - TupleSpace - Go service and Glazed CLI.md`
29. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/03/23/PROJ - CozoDB Editor - Merge Resolution, SQLite Preset, and Editor Highlighting.md`
30. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/03/25/PROJ - GPT Base Principles Compiler Experiment - Principles-Guided JS to Wasm Compiler.md`
31. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/03/25/PROJ - Generic Agent - Principled Compiler Experiment.md`
32. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/03/25/PROJ - Scraper - Runtime Events Session Report.md`
33. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/03/25/PROJ - wesen terraform - Infra Session Report.md`
34. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/03/27/PROJ - K3s Migration Program - From Coolify to GitOps Platform.md`
35. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/03/27/PROJ - MySQL IDE on K3s - Authenticated CoinVault SQL Debug Surface.md`
36. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/03/27/PROJ - Sanitize - JSON Recovery Experiments and Limits.md`
37. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/03/27/PROJ - Sanitize - YAML Sanitizing Deep Dive.md`
38. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/03/28/PROJ - Gnosis Dynamic VM - Stack Machine Debugger and Interactive Explorer.md`
39. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/03/28/PROJ - Remarquee - Markdown Upload Polish.md`
40. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/03/28/PROJ - Remarquee - V6 Render Overlay Y-Placement Bug.md`
41. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/03/29/PROJ - Cardputer ADV Animation UI - Experimental Minimap Firmware.md`
42. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/03/29/PROJ - Serve Artifacts - Claude AI Artifact Server.md`
43. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/03/29/PROJ - Serve Artifacts - Deploying to K3s with GitOps.md`
44. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/03/30/PROJ - Pretext - Current AssemblyScript Implementation.md`
45. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/03/30/PROJ - Pretext - Interactive Article Demo Pages.md`
46. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/03/30/PROJ - Pretext - Trace Server.md`
47. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/04/01/PROJ - go-minitrace - Web UI and Transcript Explorer.md`
48. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/04/02/PROJ - Cardputer Web Demo - Bluetooth Architecture And Bringup.md`
49. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/04/02/PROJ - Cardputer Web Serial Demo - Architecture And Build.md`
50. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/04/02/PROJ - SQLide Browser - Go Wasm SQL IDE.md`
51. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/04/02/PROJ - Smailnail SQLite Mirror, Merge, Enrich, and Annotation Report.md`
52. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/04/03/PROJ - Email Triage - AI Secretary for a 33K Message Inbox.md`
53. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/04/04/PROJ - go-minitrace - Annotation System.md`
54. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/04/05/PROJ - Wi-Fi Audio Cues Lab - ESP-IDF Sample for Audio Cues on AtomS3R with Atomic Echo Base.md`
55. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/04/06/PROJ - Paper Pro Pen Probe - reMarkable E-Ink Drawing and Pen Input.md`
56. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/04/07/PROJ - Paper Pro E-Ink - DRM KMS Fast Mode Investigation.md`
57. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/04/07/PROJ - Paper Pro E-Ink - Ghidra Reverse Engineering of libqsgepaper.so.md`
58. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/04/07/PROJ - Paper Pro E-Ink - Pen Input and SDK Build Fix.md`
59. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/04/07/PROJ - pi Mono - Investigating LLM Thinking Content Truncation.md`
60. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/04/07/PROJ - reMarkable Cloud Activity Timeline.md`
61. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/04/09/PROJ - Cross-Model Transcript Analysis - Minimax M2.7 vs GPT-5.4.md`
62. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/04/10/PROJ - reMarkable Book Indexing - Using kimi-k2p5 and remarquee to catalog programming books.md`
63. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/04/11/PROJ - Firefox Tab Tracker - Browser Tab Monitoring via Native Messaging.md`
64. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/04/11/PROJ - Rabbit Hole Podcast Intros - Remotion Video Generation.md`
65. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/04/11/PROJ - Surf CLI - ChatGPT Transcript Extraction.md`
66. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/04/11/PROJ - i3 Event Logger - Workspace and Window Focus Tracking via i3 IPC.md`
67. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/04/12/PROJ - KV-Cache VM - Token-Editing Decoding VM for CPU-Side LLM Inference.md`
68. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/04/13/PROJ - Jingle Extractor - AI Audio Pipeline with MiniMax Demucs WhisperX.md`
69. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/04/13/PROJ - Loupedeck - Architecture Cleanup and Performance Report.md`
70. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/04/13/PROJ - Screencast Studio - GStreamer Migration and Media Runtime Intern Guide.md`
71. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/04/13/PROJ - Screencast Studio - GStreamer Setup, Performance, and Region Debugging Report.md`
72. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/04/13/PROJ - Transcription Go - Dagger Nemotron ASR Pipeline.md`
73. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/04/13/PROJ - Transcription Go - Streaming Transcription Architecture and Implementation Report.md`
74. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/04/14/PROJ - Goja REPL Essay - Implementation Deep Dive.md`
75. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/04/14/PROJ - PinocchioRC - Declarative Config Plans and Cleanup.md`
76. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/04/14/PROJ - WASM JSON Flattener - Go CLI and WebAssembly Tool.md`
77. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/04/14/PROJ - go-minitrace HTML Transcript Export - Reader Architecture.md`
78. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/04/15/PROJ - JSON Flattener - Go WASM JSON Conversion Tool.md`
79. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/04/15/PROJ - VT100 WASM Emulator.md`
80. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/04/15/PROJ - poll-modem k3s Cluster on Proxmox.md`
81. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/04/16/PROJ - Nightly Transcript Review - 2026-04-16.md`
82. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/04/17/PROJ - BYOK Host - Keycloak and SQLite Broker Intern Research Guide.md`
83. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/04/17/PROJ - Client-side Tool Broker for Chat - Intern Research Guide.md`
84. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/04/17/PROJ - pi-sandbox - Intern Report on Firecracker, Proxmox, and the k3s Control-Plane Plan.md`
85. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/04/17/PROJ - pi-sandbox - Sandboxed Pi Runner and Firecracker Research Guide.md`
86. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/04/17/PROJ - surf-cli - Anna's Archive and Z-Library Browser Commands.md`
87. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/04/20/PROJ - BYOK Host - Broker, PKCE, and Chat Workflow Technical Textbook.md`
88. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/04/20/PROJ - Codebase Browser - Embedded Go+TS Doc Server with Live Source Snippets.md`
89. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/04/20/PROJ - Codebase Browser - Static Analysis and Dagger Pipeline.md`
90. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/04/21/PROJ - CSS Visual Diff - Hair Booking Fringe Restyle Tooling.md`
91. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/04/21/PROJ - M5 Tab5 - Getting Acquainted.md`
92. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/04/21/PROJ - Pi Extension - Hello World Before Thinking Blocks.md`
93. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/04/21/PROJ - Smailnail - Review UI PR #3.md`
94. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/04/21/PROJ - css-visual-diff - Script Runtime and JS DSL.md`
95. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/04/22/PROJ - Geppetto - OpenAI Responses Image Support.md`
96. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/04/23/PROJ - Codebase Browser - Static WASM Build and SQLite Prototype.md`
97. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/04/23/PROJ - Pi Extension - A Textbook on Writing and Testing Pi Extensions.md`
98. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/04/24/PROJ - Goja Essay - Argo CD Deployment Report.md`
99. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/04/25/PROJ - Goja WASM Web REPL - A JavaScript Sandbox in the Browser.md`
100. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/04/25/PROJ - Pi Session Summary Extension - Textbook Report.md`
101. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/04/25/PROJ - WASM Plugin REPL - Goja wazero Deep Dive.md`
102. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/04/26/PROJ - Pi Extensions - Agent Env and Response Capture.md`
103. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/04/27/PROJ - CSS Visual Diff Review Site.md`
104. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/04/27/PROJ - Pi Extensions - Compaction Title Extension.md`
105. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/04/27/PROJ - Pi Extensions - Direnv Bash Extension.md`
106. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/04/27/PROJ - go-go-goja - YAML and Run Support.md`
107. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/04/28/PROJ - Glazed Help Export and External Serve Sources - Technical Project Report.md`
108. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/04/28/PROJ - Hover Component Inspector - Building a Browser Overlay Lens.md`
109. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/04/28/PROJ - MiroTalk SFU on K3s - Video Realm and WebRTC Deployment.md`
110. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/04/28/PROJ - RESEARCH PROPOSAL - Remote Capability Plugins for go-go-goja.md`
111. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/04/29/PROJ - Docker Pi Agent Runtime - SQLite Container Setup.md`
112. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/04/29/PROJ - Sessionstream - Replay Store Remediation and Systemlab UI Refinement.md`
113. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/04/30/PROJ - Browser-Side React Widget Runtime - In-Browser TSX Compilation and Reload.md`
114. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/04/30/PROJ - Racket Web Editor - Interactive Compiler Course.md`
115. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/04/30/PROJECT_REPORT - Racket Web Editor.md`
116. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/05/01/PROJ - Static Apple Music Player - Deep Dive.md`
117. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/05/01/PROJ - VibeBot Sessions - Discord Bot Vibe-Coding Signup Platform.md`
118. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/05/02/PROJ - Latent Space Podcast Downloader.md`
119. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/05/03/PROJ - Agent Enroll - Full Stack Kanban Agent System Technical Report.md`
120. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/05/05/PROJ - Configuring Wafer Models in Pi.md`
121. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/05/07/PROJ - Standalone Pico 2W Web Server - Pico SDK Deep Dive.md`
122. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/05/09/PROJ - AUTODISCO - Automerge Discord App Architecture.md`
123. `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/05/09/PROJ - AUTODISCO - Keyhive Access Control Architecture.md` *(already analyzed; keep this line only if using the raw file export — otherwise exclude in follow-up cleanup)*

> Note: item 123 above appears because the raw file export was generated before one final manual exclusion cleanup. Treat **AUTODISCO Keyhive Access Control Architecture** as already analyzed. The true remaining unique count is **122** if you remove that duplicate line.

---

## Proposed future batches

These are suggested batches for a colleague to continue the work. They are not mandatory — they are a practical queue organized to maximize concept density and reuse.

### Batch A — Smailnail delivery and hosted app shape
**Projects**: Smailnail Coolify Deployment, Smailnail Hosted Backend and SPA, Smailnail IMAP and Sieve Expansion, Smailnail SQLite Mirror/Merge/Enrich, Smailnail Review UI PR #3, one related backend or deployment note.

This batch deepens the hosted Smailnail product cluster after the identity work. It should clarify what is product runtime, what is MCP substrate, what is persistence shape, and what belongs in future app/platform docs. Good chance of reinforcing hosted-app architecture, SQLite-as-app-db variants, and embedded-SPA delivery patterns.

### Batch B — Geppetto / Scopedjs / Pinocchio runtime evolution
**Projects**: Scopedjs Runtime and Demo, Scopedjs Runtime Final State, Geppetto Opinionated JS APIs and Engine Profiles, Geppetto OpenAI Responses Image Support, PinocchioRC, Goja Essay Argo CD report or Goja REPL Essay.

This batch should consolidate the older Geppetto/Pinocchio runtime lineage and connect it back to the newer goja execution model. Useful for surfacing older host/runtime abstractions, declarative config-plan patterns, and provider-boundary cleanup patterns.

### Batch C — Tree-sitter and structured text systems — COMPLETED 2026-05-11
**Projects**: Query Treesitter, Sanitize Structured Text Sanitizer, Tree-sitter Templating, Sanitize JSON Recovery, Sanitize YAML Deep Dive, Scenario Runtime Workbench.

Completed as [[KB-BATCH9-tree-sitter-structured-text]]. Created [[On-Ramp/tree-sitter-for-go-tools]]. Strong follow-up candidates are conservative repair boundary, shared parse-aware analysis object, and Tree-sitter as structural prefilter plus semantic layer; all should get implementer review before Tribal entries are written.

### Batch D — Cozo / editor / structured browser tools
**Projects**: CozoDB Editor SEM Streaming, CozoDB Notebook Packaging, CozoDB Merge Resolution, CozoScript Web UI, MySQL IDE on K3s, SQLide Browser.

This batch should expose a browser-database/editor cluster: query surfaces, packaging, preset systems, browser IDE patterns, and maybe more SQL/command-config interplay. It could reinforce command-source patterns and produce new on-ramp candidates around browser SQL tooling.

### Batch E — PaperS3 / reMarkable / e-ink continuation
**Projects**: PaperS3 Firmware Setup, Glyph Protractor, PaperS3 E-Reader, Paper Pro Pen Probe, Paper Pro E-Ink DRM/KMS, Paper Pro Ghidra RE, Paper Pro Pen Input Fix, reMarkable Cleanup, reMarkable Cloud Activity, reMarkable Book Indexing, Remarquee Markdown Upload Polish, Remarquee V6 Y-placement bug.

This is a large hardware/document-device cluster. It should deepen the already-strong e-ink, rendering, and document-format work. Good place to promote E-ink and rendering-related candidates and maybe surface new fundamentals if the rendering theory cluster gets denser.

### Batch F — Minitrace analytics and transcript-analysis workflows
**Projects**: Claude Code Hook Analytics, Claude Code Hook Events Logger, go-minitrace Web UI and Transcript Explorer, go-minitrace Annotation System, go-minitrace HTML Transcript Export, Nightly Transcript Review, Cross-Model Transcript Analysis.

This batch should turn transcript analysis into a stronger domain cluster. Likely outputs: more command-catalog evidence, annotation workflow patterns, maybe an on-ramp around transcript-analysis system design, and possible fundamental support for distributed/event-log reasoning.

### Batch G — Browser/device demos and human-interface experiments
**Projects**: Cardputer Web Demo Bluetooth, Cardputer Web Serial Architecture and Build, Cardputer ADV Animation UI, Firefox Tab Tracker, i3 Event Logger, Hover Component Inspector.

This batch is about browser/device/control-loop experiments. It may reinforce browser-side processing, serial/web transport patterns, UI overlay tooling, and event/logging surface design.

### Batch H — Media / audio / video pipeline cluster
**Projects**: Rabbit Hole Podcast Intros, Jingle Extractor, Transcription Go Nemotron pipeline, Transcription Go Streaming Architecture, MiroTalk SFU on K3s, Static Apple Music Player, Latent Space Podcast Downloader, LibriVox Player.

This is the strongest remaining media cluster. It should deepen or expand the Screencast/GStreamer on-ramp domain and potentially create new tribal material around ASR pipelines, media orchestration, and pipeline/runtime boundaries.

### Batch I — Compiler / VM / language experiments
**Projects**: Gnosis Compiler, Gnosis Dynamic VM, Generic Agent compiler experiment, GPT Base Principles compiler experiment, KV-Cache VM, Racket Web Editor (both reports), What Is a Stack-Based VM feeder projects.

This batch could produce strong language-runtime and compiler design candidates. It also gives more support for the stack-VM on-ramp and perhaps future fundamentals if VM theory starts underpinning multiple entries.

### Batch J — WASM/browser runtime cluster
**Projects**: WASM JSON Flattener, JSON Flattener Go WASM, VT100 WASM Emulator, Goja WASM Web REPL, WASM Plugin REPL, Federated Modules, Browser-Side React Widget Runtime.

This batch is high-yield for Go→WASM, browser runtime boundaries, module loading, and plugin/runtime architecture. It may create more support for sandbox and browser-runtime on-ramp material.

### Batch K — Pi extensions and Pi tooling cluster
**Projects**: Pi Extension Hello World, Pi Extension textbook, Pi Session Summary Extension, Pi Extensions Compaction Title, Pi Extensions Direnv Bash, Pi Extensions Agent Env and Response Capture, Configuring Wafer Models in Pi.

This batch should create a coherent Pi-extension/tooling cluster. Good candidate for future on-ramp material around Pi extension authoring and host/runtime contract patterns.

### Batch L — Codebase Browser / docs-as-product cluster
**Projects**: Codebase Browser embedded doc server, static analysis & Dagger pipeline, static WASM/SQLite prototype, Glazed Help Export and External Serve Sources.

This batch deepens the Go CLI + embedded SPA + docs/browser tooling direction. It may justify a proper on-ramp for “Go CLI with embedded SPA” if two more projects land in that area.

### Batch M — Auth/product follow-on cluster
**Projects**: VibeBot Sessions, CoinVault RAG Web Chat, Email Triage, TupleSpace, maybe AUTODISCO Automerge Discord App Architecture.

This is a mixed product-level batch. It is useful when you want to see how auth, agent UX, local-first state, and hosted product concerns show up in real apps rather than infrastructure or runtime layers.

### Batch N — Infra/platform leftovers
**Projects**: Coolify Hetzner, K3s Migration Program, Serve Artifacts on K3s, wesen terraform infra session, poll-modem k3s Cluster on Proxmox, Docker Pi Agent Runtime.

This batch is good for cleaning up the remaining infra story: platform migration, delivery surfaces, runtime containers, and deployment evolution. Useful for finishing the platform cluster without re-reading already-covered Vault/K3s core notes.

### Batch O — Sharp-edged one-offs / cleanup queue
**Projects**: close-dependabot-prs, reMarkable Cleanup, pi Mono thinking truncation, M5 Tab5, Surf CLI projects, CSS Visual Diff projects, any remaining one-offs not absorbed by other batches.

This is the catch-all batch for things that do not naturally cluster or that are too small to anchor their own domain. Expect more 1/3 candidates here, but also useful operational/on-ramp notes.

---

## Suggested handoff workflow for the colleague

1. Start each new batch by checking this document and choosing the next batch letter.
2. Read the canonical index first: `Projects/00-project-index-repos-and-concepts.md`.
3. Read the playbook: `Research/playbooks/building-knowledge-base.md`.
4. For each project in the batch:
   - extract tribal candidates
   - extract on-ramp candidates
   - note missing fundamentals support
5. Update the canonical index directly.
6. If a concept is below threshold but obviously valuable, flag it as:
   - `🌐 Domain seed`, or
   - `created by user request`
7. Keep the auth cluster consolidated — prefer strengthening existing auth docs over creating narrow new auth entries.

---

## Suggested rule for campaign metrics

Track **both** of these:
- **analysis slots completed** — useful for batch progress
- **unique project reports analyzed** — useful for remaining backlog

That avoids confusion when a project is revisited for a later concept cluster.

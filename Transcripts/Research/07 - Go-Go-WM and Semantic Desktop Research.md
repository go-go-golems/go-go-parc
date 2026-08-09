---
title: Go-Go-WM and Semantic Desktop Research Cluster
tags:
  - research
  - go-go-wm
  - semantic-desktop
  - pbui
  - transcripts
---

# Go-Go-WM and Semantic Desktop Research Cluster

## Research arc

The Go-Go-WM documents reinterpret a window manager as a programmable presentation environment and semantic desktop. Windows, transient tools, REPL results, applications, devices, and scripts become typed presentations and inspectable objects in a local semantic object space. JavaScript supplies composition and live authoring; Go remains responsible for state, validation, X11, resources, security, and lifecycle.

## Material synthesis

The architecture reports connect CLIM and Genera Dynamic Windows with Smalltalk, HyperCard, Dynabook, and contemporary scriptable window managers. The proposed system includes a broker/presentation protocol, typed presentations and verbs, leases and capabilities, supervised scripts, transient applications, retained scenes/widgets, event/device meshes, and a rich REPL.

The engineering handbook grounds that vision in ordinary window-manager constraints. It identifies resize cost at the boundary between pointer events, layout recomputation, client resize, rendering, and script scheduling. The recommendation is to keep expensive, dimension-dependent work off the X11 owner loop while preserving a pure layout model, immutable render snapshots, bounded event ingestion, and separate JavaScript ownership.

The “semantic desktop” reports are intentionally architectural. They describe a direction and a set of seams—not proof that every broker-v2, semantic-object, or isolation proposal exists in the current code.

## Major deliverables

- [[Transcripts/2026/07/22/Go-Go-WM Documentation Guide/go-go-wm-programmable-presentation-environment|Programmable presentation environment]].
- [[Transcripts/2026/07/22/Window Manager Development Guide/go-go-wm-architecture-performance-scriptability-handbook|Architecture, performance, and scriptability handbook]].
- [[Transcripts/2026/07/22/Lost UI Approaches/go-go-wm-programmable-semantic-desktop|Programmable semantic desktop report]].
- [[Transcripts/2026/07/22/Window Manager Performance and UI/go-go-wm-engineering-guide|Go-Go-WM engineering guide]] and PDF.
- [[Transcripts/2026/07/22/Window Manager Performance and UI/go-go-wm_engineering_handbook|Go-Go-WM engineering handbook]].
- [[Transcripts/2026/07/22/PBUI WM Integration Possibilities/pbui_wails_qml_integration_report|PBUI/WM integration report]].

## Source conversations

- [[Transcripts/2026/07/22/CHATGPT TRANSCRIPT - Go-Go-WM Documentation Guide|Go-Go-WM Documentation Guide]].
- [[Transcripts/2026/07/22/CHATGPT TRANSCRIPT - Window Manager Development Guide|Window Manager Development Guide]].
- [[Transcripts/2026/07/22/CHATGPT TRANSCRIPT - Window Manager Performance and UI|Window Manager Performance and UI]].
- [[Transcripts/2026/07/22/CHATGPT TRANSCRIPT - Window Manager Performance Optimization|Window Manager Performance Optimization]].
- [[Transcripts/2026/07/22/CHATGPT TRANSCRIPT - Lost UI Approaches|Lost UI Approaches]].

## Evidence boundary

The performance conclusions inherit the handbook’s qualification that existing repository records were used when live PARC pages or fresh profiling were unavailable. Treat this cluster as architecture/review material with selected repository evidence, not a current benchmark report.

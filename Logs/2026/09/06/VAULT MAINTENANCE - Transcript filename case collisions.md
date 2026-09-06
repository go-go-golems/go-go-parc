---
title: Vault transcript filename case-collision repair
created: 2026-09-06
type: maintenance
status: complete
tags: [git, obsidian, maintenance]
---

# Vault transcript filename case-collision repair

The vault tracked six pairs of Markdown paths differing only by capitalization. On this case-insensitive macOS filesystem, three pairs had different contents and appeared as local modifications because only one physical file could occupy each path. The other three pairs contained identical bytes. This repair gives each previously colliding file a distinct path and preserves every original Git blob, including the duplicate exports.

Active exact vault wikilinks were updated in the career inventory, thesis/PDF inventory, and PBUI handbook. Historical transcript commands and sandbox download URLs remain unchanged because they document original filenames. The prior local semantic-feedback commit is replayed separately onto the updated remote history; this repair does not discard it.

| Previous tracked path | New distinct path | Preserved Git blob |
|---|---|---|
| `Transcripts/2026/07/28/CHATGPT TRANSCRIPT - ZITADEL Branding Setup.md` | `Transcripts/2026/07/28/CHATGPT TRANSCRIPT - ZITADEL Branding Setup - Session 003931.md` | `c34884aabf33e2c2000d74616a9cd8bb9f454864` |
| `Transcripts/2026/08/06/Branch Branch Branch CLIM UI in React/P06-TYPED-PORTS-BINDING-QUOTIENT-COMPILER.md` | `Transcripts/2026/08/06/Branch Branch Branch CLIM UI in React/P06-TYPED-PORTS-BINDING-QUOTIENT-COMPILER - Mathematical Semantics.md` | `78f5935582b51acefaa33db5dae38c165004ca3f` |
| `Transcripts/2026/08/06/Branch Branch Branch CLIM UI in React/PRESENTATION-BASED-UI-ARCHITECTURES-BEYOND-CLIM.md` | `Transcripts/2026/08/06/Branch Branch Branch CLIM UI in React/PRESENTATION-BASED-UI-ARCHITECTURES-BEYOND-CLIM - Uppercase Export.md` | `07db97c7143663ffb0479062c191df794f083a21` |
| `Transcripts/2026/08/06/Branch Branch CLIM UI in React/PRESENTATION-BASED-UI-ARCHITECTURES-BEYOND-CLIM.md` | `Transcripts/2026/08/06/Branch Branch CLIM UI in React/PRESENTATION-BASED-UI-ARCHITECTURES-BEYOND-CLIM - Uppercase Export.md` | `07db97c7143663ffb0479062c191df794f083a21` |
| `Transcripts/2026/08/06/Branch CLIM UI in React/PRESENTATION-BASED-UI-ARCHITECTURES-BEYOND-CLIM.md` | `Transcripts/2026/08/06/Branch CLIM UI in React/PRESENTATION-BASED-UI-ARCHITECTURES-BEYOND-CLIM - Uppercase Export.md` | `07db97c7143663ffb0479062c191df794f083a21` |
| `Transcripts/2026/08/13/CHATGPT TRANSCRIPT - DreamCoder Tiling WM.md` | `Transcripts/2026/08/13/CHATGPT TRANSCRIPT - DreamCoder Tiling WM - Session 194502.md` | `07e1381de4f3d5b5bd6b46eaee89ce584e5f8c90` |

Remote base: `f53dab25ac1a53144b8655e7a4ffcd4488e63360`. Original local tip: `7065d6728d748e0587df18f1272b6cf3b453ee19`. No transcript content was merged or deleted.

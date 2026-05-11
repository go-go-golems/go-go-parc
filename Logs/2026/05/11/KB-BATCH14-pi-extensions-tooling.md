---
title: "KB Batch 14 — Pi Extensions and Pi Tooling"
aliases:
  - KB-BATCH14-pi-extensions-tooling
  - Batch K Pi extensions tooling
status: active
type: kb-review
created: 2026-05-11
tags: [knowledge-base, kb-review, pi, extensions, tooling]
---

# KB Batch 14 — Pi Extensions and Pi Tooling

## Scope

Batch K reviewed the Pi extension/tooling cluster from the campaign handoff:

1. [[PROJ - Pi Extension - Hello World Before Thinking Blocks]]
2. [[PROJ - Pi Extension - A Textbook on Writing and Testing Pi Extensions]]
3. [[PROJ - Pi Session Summary Extension - Textbook Report]]
4. [[PROJ - Pi Extensions - Agent Env and Response Capture]]
5. [[PROJ - Pi Extensions - Compaction Title Extension]]
6. [[PROJ - Pi Extensions - Direnv Bash Extension]]
7. [[PROJ - Configuring Wafer Models in Pi]]

I also read the KB playbook before processing the batch and checked Pi's extension documentation so the analysis used Pi's current event/lifecycle terminology.

## Main conclusion

The cluster has one strong Tribal pattern: **Pi extensions should use documented event seams as narrow middleware boundaries rather than replacing Pi internals.** This pattern appears in thinking-block widgets, session summaries, bash metadata injection, direnv loading, response capture, compaction metering, compaction-title generation, and model-provider configuration.

That pattern is now documented as:

- [[Tribal/pi-extension-event-seams]]

The entry deliberately frames the pattern around seam selection:

- observe streaming/final state at read-only events;
- mutate behavior only at documented mutable hooks;
- display through `ctx.ui` surfaces;
- preserve built-in tools and compaction where possible;
- use files or custom session entries for durable extension state;
- validate inside Pi, not only by static inspection.

## Written

### Tribal/pi-extension-event-seams

Created [[Tribal/pi-extension-event-seams]].

This entry consolidates several recurring implementation lessons:

- `message_update` is a stream-observation seam, not a message rewrite seam.
- `turn_end` is good for parsing completed assistant output, but standard message mutation there does not persist.
- `tool_call` can mutate bash arguments before execution; this is preferable to replacing bash for v1 command-preamble extensions.
- `user_bash` needs a separate wrapper for human `!` / `!!` commands.
- `ctx.ui.setWidget()` and `ctx.ui.setStatus()` should be the default surfaces for ambient extension state.
- `session_before_compact` should preserve Pi's built-in compaction behavior unless a custom summary is truly required.
- Multi-file extensions should be installed as directory symlinks.
- Generated shell preambles require real quoting/idempotence tests.

## Could / should be written later

### Pi extension authoring mental model

Status: **5/5 — ready, but already partially covered by article form.**

Seen in:

- Pi Hello World
- Pi Extension Textbook
- Session Summary
- Agent Env / Response Capture / Compaction Meter
- Compaction Title
- Direnv Bash

This could become an On-Ramp if we want KB readers to have a canonical 10-minute entry. The current PARC article already provides much of the material, so the next decision is whether to canonicalize that article into `Research/KB/On-Ramp/` or keep the article as the teaching surface and the Tribal entry as the implementation pattern.

### Pi TUI widget/status surfaces

Status: **4/5 🌐 Domain seed.**

Seen in:

- Hello World thinking widget
- Pi Extension Textbook
- Session Summary widget
- Agent Env / Response Capture / Compaction Meter status and widget surfaces
- TUI article/read-through material, but not counted as a canonical project slot here

This is close to On-Ramp threshold. The likely angle is not “what is a TUI” but “which Pi TUI surface should this state live on: notify, status, widget, overlay, renderer, footer, or editor replacement?”

### Pi context compaction model

Status: **2/5.**

Seen in:

- Compaction Meter
- Compaction Title

The useful On-Ramp would explain context windows, reserve tokens, compaction thresholds, `session_before_compact`, compaction entries, and why custom compaction is a high-risk hook.

### Pi custom model/provider configuration

Status: **1/5 🌐 Domain seed.**

Seen in:

- Configuring Wafer Models in Pi

This might become an On-Ramp if more model/provider registration projects appear. The angle is documentation-first provider metadata, JSON schema discipline, and `pi --list-models` validation.

## Updated / reinforced

- [[Fundamentals/host-mediated-sandbox-principles]] — reinforced by the extension model: Pi remains the host and extensions receive mediated capabilities through explicit APIs/events.
- [[Tribal/transcript-analysis-with-go-minitrace]] — reinforced by the Pi Extension Textbook's use of go-minitrace for post-hoc session/extension analysis.

## New candidates

### Tribal candidates

| Concept | Seen in | Status |
|---|---|---|
| Safe bash command preamble injection with idempotence markers | Pi agent-env, Pi direnv-bash | 2/3 |
| Multi-file Pi extension installed as directory symlink | Pi session-summary, Pi compaction-title | 2/3 |
| Contract + parser + widget extension architecture | Pi session-summary | 1/3 |
| Extension-to-docmgr artifact handoff via saved markdown | Pi response-capture | 1/3 |
| Status item as lightweight agent instrument | Pi compaction-meter | 1/3 |
| Compaction as session metadata checkpoint | Pi compaction-title | 1/3 |
| Extension load + standalone + tmux validation ladder | Pi direnv-bash | 1/3 |
| Documentation-first model-provider registration | Configuring Wafer Models in Pi | 1/3 |

### On-Ramp candidates

| Concept | Seen in | Status |
|---|---|---|
| Pi extension authoring mental model | Pi extension cluster | 5/5 — ready/covered by article |
| Pi TUI widget/status surfaces | Pi extension cluster | 4/5 🌐 |
| Pi context compaction model | Compaction Meter, Compaction Title | 2/5 |
| Pi custom model/provider configuration | Wafer model config | 1/5 🌐 |
| direnv for agent-launched shells | Direnv Bash | 1/5 |
| OpenAI-compatible model endpoint registration | Wafer model config | 1/5 |

## Project report updates

Added `## KB reviews` and `## Related KB entries` links to all seven Batch K project reports. Each now links back to this review and to [[Tribal/pi-extension-event-seams]].

## Index updates

Updated [[00-project-index-repos-and-concepts]] with analysis slots 69–75 and advanced campaign counts to:

- analyzed: 75
- remaining: 92
- Tribal entries: 21
- On-Ramp entries: 18
- Fundamentals: 5

## Notes for future review

The created Tribal entry is longer than the old narrow length bands, but the playbook now treats length as a target rather than a hard rule. The entry carries several real project failures and variations, which is why it was kept as one consolidated pattern instead of split into many narrow Pi-extension micro-docs.

---
title: "pi Mono: Investigating LLM Thinking Content Truncation"
aliases:
  - pi Thinking Investigation
  - PI-001
tags:
  - project
  - llm
  - debugging
  - streaming
  - reasoning
  - z-ai
  - glm
  - go-minitrace
status: complete
type: project
created: 2026-04-07
repo: /home/manuel/code/others/llms/pi/pi-mono
---

# pi Mono: Investigating LLM Thinking Content Truncation

What started as a go-minitrace rendering bug turned into a systematic investigation of how LLM reasoning content flows through pi's streaming pipeline, and whether thinking blocks are being truncated somewhere between the provider API and the session JSONL file.

> [!summary]
> 1. **Not a pi bug.** The model legitimately thinks less in tool-rich coding agent contexts — the system prompt alone causes a 93% reduction in reasoning content.
> 2. **Seven real bugs were found and fixed in go-minitrace** — tool results rendered as user messages, missing diffs, no markdown rendering, thinking/model/usage not surfaced, proto schema gaps.
> 3. **"Think through it yourself" recovers deep reasoning** even with 28 tools present — the model listens to explicit instructions.

## Why this project exists

While analyzing a 14-hour coding session with go-minitrace, I noticed that `z.ai/glm-5.1` thinking blocks averaged only 21 characters — barely a sentence. The initial hypothesis was that pi's streaming pipeline was truncating `reasoning_content` from the SSE stream. This warranted a full investigation because:

1. Accurate thinking capture is essential for understanding model reasoning in long coding sessions
2. go-minitrace's web UI had several rendering gaps that masked the real data
3. If pi was dropping thinking, every session recorded with z.ai/glm models would be affected

## Project history

The investigation unfolded in three phases:

### Phase 1: go-minitrace rendering fixes (GMT-001)

Work done in `/home/manuel/code/wesen/corporate-headquarters/go-minitrace`:

| Issue | Fix |
|-------|-----|
| Tool result turns rendered as "user" messages | Added `continue` in Pi converter after `applyToolResult()` |
| Tool call summary showed "read read" | Added `file_path`/`query`/`path` to fallback chain |
| Assistant content rendered as plain text | Added `react-markdown` for assistant turns |
| Thinking traces not surfaced | Added `Thinking`/`Model`/`Usage` to `TurnResponse`, proto schema |
| Edit diffs not shown | Added `DiffView` component (red/green from `edits[]`) |
| Write content not shown | Added `ContentBlock` with auto-truncation |
| Model/usage not shown | Added `TurnMetaChips` component |

Files modified in go-minitrace: `convert.go`, `handlers_sessions.go`, `sessions.proto`, `BlockBody.tsx`, `ToolCallRow.tsx`, `sessionProtoAdapters.ts`, `session.ts`, `Makefile`, `.gitignore`.

### Phase 2: Thinking accumulation analysis

Traced pi's complete streaming pipeline through source code:

```
pi --mode json
  └─ Agent.prompt()
       └─ runAgentLoop() → streamAssistantResponse()
            └─ streamOpenAICompletions()
                 └─ OpenAI SDK → client.chat.completions.create({stream: true})
                      └─ SSE from z.ai API
                           └─ for await (chunk)
                                └─ choice.delta.reasoning_content → currentBlock.thinking += delta
```

Confirmed every layer preserves the data:
- **OpenAI SDK**: Raw `JSON.parse(sse.data)`, no field stripping — unknown fields like `reasoning_content` pass through
- **pi-ai**: `currentBlock.thinking += delta` correctly accumulates every non-empty chunk
- **EventStream.result()**: Returns same `output` object mutated during streaming
- **agent-loop**: Forwards `message_end` with final message
- **session-manager**: Persists `event.message` as-is to JSONL
- **print-mode**: Serializes every event directly for `--mode json`

### Phase 3: Controlled experiments

See [[ARTICLE - Investigating LLM Thinking Content in Tool-Rich Coding Agent Contexts|the companion article]] for the full experimental methodology and results.

## Current project status

**Investigation complete.** Ticket PI-001 in pi-mono repo is closed.

Key artifacts:
- **PI-001 ticket**: `ttmp/2026/04/07/PI-001--investigate-z-ai-glm-5-1-thinking-content-truncation-in-pi-streaming-pipeline/`
- **GMT-001 ticket** (go-minitrace): `ttmp/2026/04/07/GMT-001--fix-pi-minitrace-conversion-and-web-ui-rendering-gaps/`
- **Interactive results viewer**: `PI-001/scripts/44-serve-results.py`
- **Raw experiment data**: `PI-001/various/thinking-experiment-results/`
- **Investigation scripts**: 45 scripts numbered 28–45 across both tickets

## Important project docs

- PI-001 design doc: `PI-001/design/01-investigation-plan.md`
- PI-001 diary: `PI-001/reference/01-diary.md`
- GMT-001 design doc: `GMT-001/design/01-pi-conversion-and-web-ui-gaps.md`
- GMT-001 diary: `GMT-001/reference/01-diary.md`

## Open questions

- Should minitrace record request context (system prompt length, tool count) alongside thinking blocks to explain short thinking?
- Should the z.ai `thinkingSignature` ("reasoning_content") be preserved for multi-turn reasoning continuity?
- Does the same system-prompt dampening effect apply to OpenAI's o-series and Anthropic's Claude with extended thinking?

## Project working rule

When investigating "data loss" in a streaming pipeline, first confirm the data is actually lost by testing the raw API directly, then bisect by adding one layer at a time. Non-deterministic LLM outputs require multi-trial experiments — a single comparison is anecdotal, not evidence.

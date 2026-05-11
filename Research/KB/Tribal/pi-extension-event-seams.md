---
title: "Pi Extension Event Seams — How We Do It"
aliases:
  - pi extension event seams
  - Pi extension middleware pattern
  - Pi extension lifecycle hooks
  - Pi extension boundary pattern
tags: [knowledge-base, tribal, pi, extensions, typescript, tui, coding-agent]
status: active
type: knowledge-base
created: 2026-05-11
---

# Pi Extension Event Seams — How We Do It

> [!summary]
> Our Pi extensions work best when they treat Pi's documented lifecycle events as narrow integration seams: observe state, transform inputs only at mutable hooks, display through TUI surfaces, and avoid replacing Pi internals unless the seam cannot express the behavior.

Related foundation: [[Fundamentals/host-mediated-sandbox-principles]]

## The pattern

A Pi extension is not a patch to Pi. It is a TypeScript module loaded by Pi and handed an `ExtensionAPI`. The extension registers handlers, commands, tools, and UI surfaces. The durable pattern across our Pi extension work is to keep each extension small and attach it to the most specific documented event seam that solves the problem.

The rule is:

> Use the smallest Pi event seam that can express the behavior, and let Pi keep owning the agent loop, session file, built-in tools, and terminal shell.

That pattern shows up in several forms.

| Goal | Seam we use | Why |
|---|---|---|
| React to streamed thinking blocks | `message_update` | It exposes raw `AssistantMessageEvent` without rewriting messages. |
| Add persistent instructions | `before_agent_start` and `input` | These are explicit prompt-shaping seams. |
| Parse the final assistant answer | `turn_end` | The full assistant text is available and stable. |
| Modify bash before execution | `tool_call` for LLM bash, `user_bash` for human `!` commands | Pi still owns the bash tool; we only alter command input. |
| Surface state in the terminal | `ctx.ui.setWidget()` and `ctx.ui.setStatus()` | The extension contributes UI without replacing Pi chrome. |
| Name sessions during compaction | `session_before_compact` + Pi's `compact()` helper | We preserve built-in memory preservation and add only title extraction. |
| Persist extension bookkeeping | `pi.appendEntry()` or source-controlled artifacts | State survives reloads without corrupting standard messages. |
| Register a provider | `models.json` or `pi.registerProvider()` | Model metadata enters Pi's registry rather than being hardcoded into prompts. |

The extension should usually be a thin middleware layer around one boundary. `agent-env` injects a metadata preamble before shell execution. `direnv-bash` injects a `direnv export bash` preamble before shell execution. `response-capture` captures the completed assistant text and delegates durable storage to files/docmgr. `compaction-title` asks Pi's own compactor for a summary and extracts a session title from it. None of these extensions replaces the whole subsystem.

## Why we do it this way

Pi already owns hard problems: model streaming, session trees, tool execution, context construction, compaction, terminal rendering, cancellation, and reload. Replacing those systems in an extension creates a second runtime that must now stay compatible with Pi's first runtime. That is almost never the right first move.

The documented event seams give us enough leverage without that cost. They also tell us what is mutable and what is only observable. This distinction is the most important implementation fact for Pi extension work:

- `before_agent_start`, `input`, `tool_call`, `tool_result`, `session_before_compact`, and similar hooks can change behavior by returning a value or mutating documented input fields.
- `message_update`, `turn_end`, `message_end`, and many lifecycle events are observation points. They are excellent for UI, logging, parsing, and bookkeeping, but they should not be treated as session-rewrite hooks.

This is why the session-summary extension displays a widget instead of rewriting the final assistant message. `turn_end` gives a completed message view, but message mutation there does not rewrite the stored session entry. The raw `<summary>` block remains the durable record; the widget is the ergonomic view.

This is also why `agent-env` and `direnv-bash` mutate `event.input.command` instead of replacing the bash tool. For version 1, command preambles preserved Pi's built-in bash execution, rendering, truncation, cancellation, and process cleanup. A spawn-hook or custom bash wrapper may be cleaner later, but it should be a deliberate v2 after the event seam proves insufficient.

## Where it lives

### Pi extension repository

| Path | Role |
|---|---|
| `/home/manuel/code/wesen/2026-04-21--pi-extensions/extensions/session-summary` | Contract + parser + widget extension for mandatory summary blocks. |
| `/home/manuel/code/wesen/2026-04-21--pi-extensions/extensions/agent-env` | `PI_AGENT_*` environment metadata through bash command preambles. |
| `/home/manuel/code/wesen/2026-04-21--pi-extensions/extensions/response-capture` | Capture assistant output, save markdown, import into docmgr. |
| `/home/manuel/code/wesen/2026-04-21--pi-extensions/extensions/compaction-meter` | Context-window distance as a status-bar instrument. |
| `/home/manuel/code/wesen/2026-04-21--pi-extensions/extensions/compaction-title` | Session titles generated during Pi compaction. |
| `/home/manuel/code/wesen/2026-04-21--pi-extensions/extensions/direnv-bash` | `direnv` environment loading through bash/user_bash preambles. |
| `/home/manuel/code/wesen/2026-04-21--pi-extensions/extensions/tui-showcase` | TUI surface pattern library. |
| `/home/manuel/code/wesen/2026-04-21--pi-extensions/extensions/kanban-demo` | Product-shaped extension with overlay, widget, status, tool, and renderer. |

### Related PARC project reports

- [[PROJ - Pi Extension - Hello World Before Thinking Blocks]] — minimal `message_update` + widget example for thinking events.
- [[PROJ - Pi Extension - A Textbook on Writing and Testing Pi Extensions]] — records the observation/injection/display split and the read-only message-mutation lesson.
- [[PROJ - Pi Session Summary Extension - Textbook Report]] — contract + parser + widget pattern, plus directory-symlink installation for multi-file extensions.
- [[PROJ - Pi Extensions - Agent Env and Response Capture]] — command mutation, CLI integration, status meters, and docmgr artifact handoff.
- [[PROJ - Pi Extensions - Compaction Title Extension]] — preserves built-in compaction while adding session title extraction.
- [[PROJ - Pi Extensions - Direnv Bash Extension]] — shell preamble middleware that preserves direnv's trust model and Pi's built-in bash.
- [[PROJ - Configuring Wafer Models in Pi]] — model registry customization through Pi's documented configuration instead of runtime hacks.
- [[ARTICLE - Playbook - Building and Testing Pi Extensions]] — reusable authoring/testing guidance for extension lifecycle, events, UI, and debugging.
- [[ARTICLE - Textbook - Building Beautiful TUIs for Pi Extensions]] — TUI surface selection and product-shaped extension design.

## Common mistakes

### Treating read-only event views as mutable session state

The session-summary work tried to replace raw `<summary>...</summary>` text inside the final assistant message during `turn_end`. The code ran, but the session file still contained the raw XML. The reason is that Pi passes a copy of the completed message to `turn_end`; mutating it does not rewrite the persisted session.

The fix was to respect the seam. The raw summary stays in the assistant text as the durable record. The extension parses the block and displays a widget as the ergonomic view. If an extension must create durable custom state, it should use `pi.appendEntry()`, `pi.sendMessage()` for custom messages, or an explicit file artifact, not accidental mutation of standard messages.

### Replacing a built-in tool before exhausting middleware hooks

Both `agent-env` and `direnv-bash` could have replaced Pi's bash tool. That would have hidden injected shell preambles from the displayed command, which is attractive. But it would also have made the extension responsible for matching Pi's bash behavior over time.

The first version instead uses `tool_call` mutation for model-driven bash and `user_bash` wrapping for human `!` commands. This keeps Pi's built-in tool in charge. If a later version needs invisible environment injection, use a dedicated spawn-hook design and test it against built-in behavior.

### Forgetting that generated shell is code

`agent-env` injects environment variables by generating shell `export` statements. The first design sketch used double quotes. That is unsafe because Bash still performs command substitution inside double quotes:

```bash
export PI_AGENT_TEST="$(printf injected)"
```

The implemented helper uses single-quote shell escaping so metadata is literal data:

```bash
export PI_AGENT_TEST='$(printf injected)'
```

Any extension that rewrites shell commands needs tests for `$()`, backticks, quotes, newlines, and idempotence markers. Command preambles are part of the security boundary.

### Sourcing `.envrc` directly instead of asking direnv

The `direnv-bash` extension deliberately uses `direnv export bash`, not `source .envrc`. Direct sourcing would bypass direnv's trust gate and execute changed or untrusted `.envrc` files as part of every Pi command.

The correct seam is: let direnv decide whether the directory is allowed, then evaluate only the exported environment code inside the same shell process as the original command.

### Installing a multi-file extension as a file symlink

The session-summary extension imports `./prompt`. A single-file symlink into `~/.pi/agent/extensions` broke that relative import shape. The correct installation for multi-file extensions is a directory with `index.ts`, symlinked as a directory:

```text
~/.pi/agent/extensions/session-summary
  -> /home/manuel/code/wesen/2026-04-21--pi-extensions/extensions/session-summary
```

Use a file extension only when it is genuinely one file.

### Clearing widgets at the wrong lifecycle point

The session-summary widget originally cleared too aggressively. If it cleared on `agent_end`, it disappeared immediately after `turn_end` in no-tool-call turns, before the user could read it. The fix was to clear at `turn_start` instead: the previous summary remains visible while the user reads it and disappears when the next turn begins.

The general rule is that cleanup timing should match the UI's meaning. A thinking-block widget should clear on `thinking_end`/`agent_end`. A last-turn summary should clear on the next turn.

### Letting UI previews hide meaning

The session-summary extension also had a fixed line cap in its widget. That made the widget a preview, not a trustworthy summary surface. The project rule became: full summary content should be displayed; line wrapping may adapt to width, but meaning should not be silently thrown away.

For TUI work, truncation can be correct for logs, lists, or status strips. It is wrong when the widget claims to be the complete artifact.

### Treating configuration as vibes instead of schema

The Wafer model configuration project showed the same seam discipline outside extensions. Pi's model registry expects specific JSON fields: provider key, `baseUrl`, API dialect, model ids, context windows, max tokens, reasoning flags, input modalities, and cost. Hand-editing the registry without `jq` validation produced a structural issue. The correct workflow is docs/API discovery, schema-shaped JSON, `jq`, then `pi --list-models` as ground truth.

## Variations

### Event middleware vs spawn hooks

Command preamble mutation is visible in the session and can look noisy. A spawn-hook implementation can inject environment variables without changing the displayed command. Use preamble mutation first when preserving built-in behavior matters more than display cleanliness. Consider spawn hooks when the pattern stabilizes and the visible command noise becomes a real workflow cost.

### Closure state vs persisted state

Use closure state for transient UI: active thinking block, last summary in the current runtime, injection counts, or current widget state. Use `pi.appendEntry()` when the state must survive reloads/resumes and belongs to the session. Use files when the extension's product is an artifact, as with response-capture markdown files.

### Widgets, statuses, overlays, and renderers

Use the least invasive TUI surface that tells the truth:

- status for tiny continuous facts like `compact:184k left`;
- widget for ambient state that should remain near the editor;
- overlay for focused keyboard workflows;
- custom renderer for durable transcript readability;
- editor replacement only when the primary input model truly changes.

The TUI showcase and Kanban demo prove that a product-shaped Pi extension is often a coordinated set of surfaces around one state model, not a single screen.

### Built-in behavior plus one appendix

`compaction-title` is the model variation for high-risk hooks. Compaction preserves memory for future turns, so replacing it entirely would be dangerous. The extension calls Pi's built-in `compact()` helper and appends only a small title instruction. It parses `## Session Title`, stores the title with `pi.setSessionName()`, and returns the normal compaction result.

For any high-risk Pi subsystem, prefer this shape: built-in behavior first, one narrow addition second.

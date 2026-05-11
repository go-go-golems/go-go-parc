---
title: "Pi Extension Authoring Mental Model"
aliases:
  - Pi extension authoring
  - Pi extensions mental model
  - writing Pi extensions
  - Pi extension lifecycle
tags: [knowledge-base, on-ramp, pi, extensions, typescript, tui, coding-agent]
status: active
type: knowledge-base
created: 2026-05-11
---

# Pi Extension Authoring Mental Model

> [!summary]
> Pi extensions are TypeScript modules that attach to Pi's runtime through documented seams: events, commands, tools, UI surfaces, session state, and provider/model registration. Read this before project reports about Pi widgets, summary blocks, command mutation, compaction hooks, or custom TUI extensions.

Related tribal pattern: [[Tribal/pi-extension-event-seams]]

## The idea in one paragraph

A Pi extension is a small TypeScript runtime plugin loaded by Pi. It exports a default factory function, receives an `ExtensionAPI`, and registers behavior: event handlers with `pi.on(...)`, slash commands with `pi.registerCommand(...)`, LLM-callable tools with `pi.registerTool(...)`, UI surfaces through `ctx.ui`, and durable bookkeeping through session entries or files. The key mental model is not “an extension can do anything,” even though it runs with local permissions. The key mental model is **choose the right seam**: observe, inject, block, render, persist, or register at the narrowest documented place in Pi's lifecycle.

## Why we care

Several PARC reports assume you already know how Pi extensions fit into the agent loop. Without that context, the reports can look like unrelated TypeScript hacks: one extension shows “Hello World” during thinking blocks, another forces `<summary>` blocks, another injects `PI_AGENT_*` environment variables into bash calls, another loads `direnv`, another names sessions during compaction, and another registers Wafer models.

They are all instances of one extension model. Pi owns the agent session, tool execution, message stream, compaction, and terminal UI. Extensions do not usually replace those systems. They attach to lifecycle events and add one piece of behavior at a time.

This matters because the sharp edges are mostly boundary mistakes:

- mutating an event that is only a read-only view;
- replacing a built-in tool when command mutation was enough;
- leaving widgets or timers alive after the turn/session ends;
- storing important state only in closure variables when it must survive reload;
- putting secrets or shell syntax in the wrong place;
- using an invasive TUI surface when a status item would do.

## The 6 things to understand

### 1. An extension starts as a factory function

The simplest extension is a TypeScript file like this:

```ts
import type { ExtensionAPI } from "@mariozechner/pi-coding-agent";

export default function (pi: ExtensionAPI) {
  pi.on("session_start", async (_event, ctx) => {
    ctx.ui.notify("Extension loaded", "info");
  });
}
```

Pi loads the file with `jiti`, calls the default export once per extension runtime, and then fires lifecycle events. For small extensions, one `.ts` file is enough. For multi-file extensions, use a directory with `index.ts` and symlink the directory into `~/.pi/agent/extensions/` or `.pi/extensions/`.

Common locations:

| Location | Use |
|---|---|
| `~/.pi/agent/extensions/*.ts` | Global one-file extension. |
| `~/.pi/agent/extensions/*/index.ts` | Global multi-file extension. |
| `.pi/extensions/*.ts` | Project-local one-file extension. |
| `.pi/extensions/*/index.ts` | Project-local multi-file extension. |
| `pi -e ./path.ts` | One-shot test extension. |

Use `/reload` during development after changing auto-discovered extensions.

### 2. Events are the backbone

Most extension work starts with `pi.on(eventName, handler)`. The handler receives an event object and an extension context:

```ts
pi.on("tool_call", async (event, ctx) => {
  // event: what happened
  // ctx: session, cwd, UI, model, abort signal, helpers
});
```

For one user turn, the rough sequence is:

```text
input
before_agent_start
agent_start
turn_start
context
before_provider_request
message_start / message_update / message_end
tool_execution_start / tool_call / tool_result / tool_execution_end
turn_end
agent_end
```

Session-level events exist too: `session_start`, `session_shutdown`, `session_before_compact`, `session_compact`, `model_select`, and more.

The single most important distinction is whether an event is **mutable** or **observational**.

| Event | Typical use | Mutable? |
|---|---|---|
| `input` | Rewrite or handle raw user input. | Yes, by return value. |
| `before_agent_start` | Add system prompt instructions or injected messages. | Yes, by return value. |
| `message_update` | Watch streaming tokens/thinking/toolcall chunks. | Observe only. |
| `turn_end` | Parse completed assistant message. | Observe only for standard messages. |
| `tool_call` | Block or mutate tool arguments before execution. | Yes. |
| `tool_result` | Modify tool result after execution. | Yes. |
| `session_before_compact` | Cancel or provide custom compaction. | Yes. |

This distinction explains most Pi extension bugs.

### 3. The message stream is for observing, not rewriting history

`message_update` exposes the raw assistant event stream. It is how the Hello World extension detects `thinking_start` and `thinking_end`. It is also how you can observe text deltas, tool-call deltas, and stream errors.

A thinking-block widget looks like this conceptually:

```ts
pi.on("message_update", async (event, ctx) => {
  const e = event.assistantMessageEvent;

  if (e.type === "thinking_start") {
    ctx.ui.setWidget("thinking", ["Thinking…"]);
  }

  if (e.type === "thinking_end" || e.type === "error") {
    ctx.ui.setWidget("thinking", undefined);
  }
});
```

What it should not do is rewrite the assistant's standard message content and assume that rewrite will persist. The session-summary project learned this the hard way. `turn_end` gave access to the completed assistant message, mutation code ran, but the stored JSONL session still contained the raw `<summary>...</summary>` block. Pi had passed a copy, not a mutable reference to the stored message.

The working pattern became: keep the raw text as durable conversation record, parse it, and render the ergonomic view in a widget.

### 4. Tools and shell commands are separate seams

Pi has LLM-called tools, such as `bash`, `read`, `edit`, and custom tools registered by extensions. It also has user shell commands entered with `!` or `!!`. These are related but not the same event path.

For LLM tool calls, use `tool_call`:

```ts
import { isToolCallEventType } from "@mariozechner/pi-coding-agent";

pi.on("tool_call", async (event) => {
  if (!isToolCallEventType("bash", event)) return;
  event.input.command = `source ~/.profile\n${event.input.command}`;
});
```

For user-entered shell commands, use `user_bash` and wrap Pi's local bash operations:

```ts
import { createLocalBashOperations } from "@mariozechner/pi-coding-agent";

pi.on("user_bash", async () => {
  const local = createLocalBashOperations();
  return {
    operations: {
      exec(command, cwd, options) {
        return local.exec(`source ~/.profile\n${command}`, cwd, options);
      },
    },
  };
});
```

This distinction is why `agent-env` and `direnv-bash` both needed two paths. LLM `bash` calls go through `tool_call`; human `!` commands go through `user_bash`.

### 5. UI has multiple surfaces; choose the least invasive one

Pi extensions can show UI in several ways:

| Surface | API | Best for |
|---|---|---|
| Notification | `ctx.ui.notify()` | Short feedback after an action. |
| Status item | `ctx.ui.setStatus()` | Tiny persistent state in the footer. |
| Widget | `ctx.ui.setWidget()` | Ambient state near the editor. |
| Dialog | `ctx.ui.select/confirm/input/editor()` | One focused user decision. |
| Overlay/custom component | `ctx.ui.custom()` | Full keyboard-driven workflows. |
| Message renderer | `pi.registerMessageRenderer()` | Durable custom transcript cards. |
| Tool renderer | `renderCall` / `renderResult` | Readable tool rows. |
| Editor replacement | `ctx.ui.setEditorComponent()` | Alternate input model; use sparingly. |

The surface should match the meaning. A compaction distance belongs in a status item. A last-turn summary belongs in a widget that persists until the next turn. A Kanban board belongs in an overlay plus a small ambient widget. Replacing the editor is the sharpest tool and should be rare.

TUI components must also be width-safe. Terminal rendering is not web layout. Use visible-width-aware truncation/wrapping utilities, clear timers in `dispose()` or `session_shutdown`, and always provide a way back from invasive chrome changes.

### 6. State has scope: closure, session, file, or external system

The easiest state is a closure variable:

```ts
export default function (pi: ExtensionAPI) {
  let active = false;
  pi.on("turn_start", () => { active = false; });
}
```

That is right for transient UI state. It resets on reload and does not survive session switches.

For state that must survive reload/resume, use custom session entries:

```ts
pi.appendEntry("my-extension-state", { lastTitle, updateCount });

pi.on("session_start", async (_event, ctx) => {
  for (const entry of ctx.sessionManager.getEntries()) {
    if (entry.type === "custom" && entry.customType === "my-extension-state") {
      // restore from entry.data
    }
  }
});
```

For artifacts, write files. `response-capture` saves assistant responses to markdown files and imports them into docmgr; the file is the durable product. It does not need to pretend that extension closure state is persistence.

## The gotchas we've hit

### Mutating a completed standard message does not persist

The session-summary extension tried to rewrite the completed assistant message in `turn_end`. The mutation code ran, but the raw summary tags stayed in the session file. The fix was architectural: parse at `turn_end`, render a widget, and leave the conversation record alone.

### Clearing widgets too early makes them disappear

The summary widget initially cleared at `agent_end`, which can happen immediately after `turn_end` in no-tool-call turns. The user never had time to read it. Clearing at `turn_start` was the right semantic boundary: keep the last summary visible until the next user turn begins.

### File symlinks break multi-file extensions

A multi-file extension that imports `./prompt` should be installed as a directory symlink, not as a single file symlink. Otherwise relative imports can fail because Pi sees only the entrypoint file.

### Generated shell needs real quoting tests

`agent-env` generates `export PI_AGENT_*='...'` statements. Double quotes would allow command substitution, so values like `$(printf injected)` would execute. The extension needed single-quote shell escaping and explicit self-tests. Treat shell preambles as code generation, not string decoration.

### `direnv` should be asked, not bypassed

`direnv-bash` uses `direnv export bash` and evaluates the exported environment. It does not `source .envrc` directly, because direct sourcing bypasses direnv's trust model. This is an extension authoring lesson: when wrapping an external tool, preserve the tool's safety boundary.

### Replacing built-in tools is expensive

It is tempting to replace the built-in `bash` tool to get cleaner environment injection. But replacing a built-in means owning execution, cancellation, truncation, rendering, and future compatibility. `agent-env` and `direnv-bash` started with command mutation because that preserved Pi's built-in bash behavior.

### Compaction is memory preservation first

`compaction-title` adds session naming during compaction, but it does not invent its own compaction system. It calls Pi's built-in `compact()` helper and appends a small title instruction. This preserves the primary purpose of compaction: keeping future work resumable.

## Where to go deeper

1. Pi extension docs: `/home/manuel/.nvm/versions/node/v22.22.1/lib/node_modules/@mariozechner/pi-coding-agent/docs/extensions.md`
2. Pi TUI docs: `/home/manuel/.nvm/versions/node/v22.22.1/lib/node_modules/@mariozechner/pi-coding-agent/docs/tui.md`
3. [[Tribal/pi-extension-event-seams]] — our implementation pattern and scar tissue for Pi extension boundaries.
4. [[ARTICLE - Playbook - Building and Testing Pi Extensions]] — practical project article with examples and testing checklist.
5. [[ARTICLE - Textbook - Building Beautiful TUIs for Pi Extensions]] — deeper guide to overlays, widgets, renderers, and width-safe terminal UI.

### Related PARC project reports

- [[PROJ - Pi Extension - Hello World Before Thinking Blocks]] — minimal `message_update` + widget extension.
- [[PROJ - Pi Extension - A Textbook on Writing and Testing Pi Extensions]] — broad extension lifecycle and debugging report.
- [[PROJ - Pi Session Summary Extension - Textbook Report]] — contract + parser + widget pattern.
- [[PROJ - Pi Extensions - Agent Env and Response Capture]] — tool-call mutation, response artifacts, status meters.
- [[PROJ - Pi Extensions - Compaction Title Extension]] — high-risk compaction hook using built-in compaction plus one appendix.
- [[PROJ - Pi Extensions - Direnv Bash Extension]] — command preamble middleware preserving direnv's trust model.
- [[PROJ - Configuring Wafer Models in Pi]] — provider/model configuration at the registry seam.

---
title: "Pi Extension: A Textbook on Writing and Testing Pi Extensions"
aliases:
  - Pi Extension Authoring
  - Writing Pi Extensions
  - Testing Pi Extensions
  - Pi Extension Patterns
tags:
  - project
  - pi
  - extensions
  - typescript
  - tui
  - agent-system
  - coding-agent
  - debugging
  - go-minitrace
status: active
type: project
created: 2026-04-23
repo: /home/manuel/code/wesen/2026-04-21--pi-extensions
---

# Pi Extension: A Textbook on Writing and Testing Pi Extensions

This is the extended lifecycle and testing reference in the [[pi-extensions]] project map.

> [!warning] Historical DuckDB commands
> This note contains an older go-minitrace query example. The Pi-extension guidance remains useful, but use [[go-minitrace]] and the normalized SQLite workflow documented in [[ARTICLE - go-minitrace Query Engine Migration - DuckDB to Normalized SQLite]].

This is a textbook. Its purpose is to teach you how Pi's extension system works at a level that lets you build your own extensions from first principles—not by copying examples, but by understanding why the API is shaped the way it is, which parts are reliable and which are fragile, and how to debug when things go wrong.

Two extensions were built while writing this document. The first was a minimal proof-of-concept that displayed "Hello World" in a widget whenever the LLM emitted a thinking block. The second was a session-summary extension that injected a system prompt instruction, appended reminders to user prompts, parsed `<summary>...</summary>` blocks at turn end, and displayed them in a bordered widget. Building both revealed a great deal about how Pi actually works—not just how the documentation describes it, but how it behaves in practice. This textbook is the record of that learning.

> [!summary]
> - Pi's extension API exposes a small, orthogonal set of capabilities: event subscription, tool registration, command registration, and UI methods.
> - The event system is the heart of the API. Understanding which events fire when, and which carry mutable data, is the core skill.
> - The `message_update` event gives access to the raw `AssistantMessageEvent` stream, including `thinking_start` and `thinking_end`.
> - Standard message mutation at `turn_end` does not work—Pi passes copies, not references.
> - File logging is the most reliable debugging tool.
> - go-minitrace turns verbose session JSONL into a queryable DuckDB archive—essential for post-hoc analysis.

## 1. What Pi Is

Pi is a terminal-based coding agent. It is not a chatbot—it is an agent runtime. When you type a prompt, Pi sends it to an LLM, receives a streaming response, executes any tool calls the model makes (read, bash, edit, write, and more), collects the results, and loops until the model stops. Sessions persist to disk as JSONL files. The conversation forms a tree—branches and forks are native concepts, not afterthoughts.

The terminal UI is rendered by a library called `pi-tui`. Extensions do not interact with the terminal directly. They interact with Pi's extension API, which in turn communicates with the TUI.

The extension API is written in TypeScript. Pi uses [jiti](https://github.com/unjs/jiti) to run TypeScript source files directly, without a build step. This is a deliberate choice: extensions are plain `.ts` files that Pi loads at startup.

## 2. The Extension Factory

Every extension is a single TypeScript file that exports a default factory function. Pi calls this factory once per session and passes in a single object: `pi: ExtensionAPI`. This object is your entire interface to Pi.

```typescript
import type { ExtensionAPI } from "@mariozechner/pi-coding-agent";

export default function (pi: ExtensionAPI) {
  // pi gives you everything: event subscription, tool registration,
  // command registration, and UI methods.
}
```

The factory can be synchronous or async. If it returns a `Promise`, Pi awaits it before firing `session_start`. This means you can do async initialization—fetching remote config, discovering models, establishing connections—before any event fires.

## 3. The Event System

The event system is where extensions earn their power. Pi fires events in a predictable sequence. Your extension subscribes to the events it cares about. Each handler receives two arguments: the event object and a context object.

```typescript
pi.on("event_name", async (event, ctx) => {
  // event — the event-specific payload
  // ctx — ExtensionContext, your interface to the session and UI
});
```

The handler type is:

```typescript
type ExtensionHandler<E, R = undefined> = (event: E, ctx: ExtensionContext) => Promise<R | void> | R | void;
```

Most handlers return `void`. Some events accept a return value that modifies behavior—`tool_call` can return `{ block: true, reason: "..." }` to block a tool call, and `before_agent_start` can return a modified `systemPrompt`. These return values are the only way extensions can change Pi's behavior, not just observe it.

### 3.1 The Full Event Sequence

Understanding when each event fires is the most important skill in extension authoring. Here is the complete sequence for one user prompt that produces a tool call:

```
session_start                    Session begins or reloads
  │
input                           User submitted a prompt
  │
before_agent_start              Before the agent loop starts
  │
agent_start                    Agent loop begins
  │
turn_start                     Turn begins
  │
context                        Pi is assembling messages for the LLM
  │
before_provider_request        Right before the HTTP request fires
  │
    ┌─── LLM streams tokens ───┐
    │                           │
    │  message_start            Message begins assembling
    │  message_update          Token by token (fires many times)
    │    text_start / text_delta / text_end
    │    thinking_start / thinking_delta / thinking_end
    │    toolcall_start / toolcall_delta / toolcall_end
    │  message_end              Message complete
    │                           │
    │  tool_execution_start    Tool begins
    │  tool_call               Tool invoked (can be blocked)
    │  tool_result             Tool finished (can be modified)
    │  tool_execution_end      Tool done
    │                           │
    └─── LLM streams next turn ─┘
  │
turn_end                       Turn complete
  │
agent_end                      Agent loop done
```

For extensions, the most useful events are:

| Event | Fires when | Mutable? | Use for |
|-------|-----------|---------|---------|
| `input` | User submits prompt | Yes (`prompt`) | Append reminders |
| `before_agent_start` | Agent loop starts | Yes (`systemPrompt`) | Inject instructions |
| `message_start` | Message begins | No | — |
| `message_update` | Token streamed | No | Stream observation |
| `turn_end` | Turn completes | No | Final message analysis |
| `tool_call` | Tool invoked | Yes (`block`) | Permission gates |
| `agent_end` | Agent done | No | Cleanup |

The "Mutable?" column tells you whether the handler return value changes behavior. The `--` means the event fires but returning a value does nothing.

### 3.2 The message_update Event and the AssistantMessageEvent Stream

The `message_update` event is the most powerful event in the system. It fires for every token the LLM emits, wrapped in an `AssistantMessageEvent`. This is the same event stream that Pi uses internally to assemble messages. Extensions get to see it raw.

The event object:

```typescript
interface MessageUpdateEvent {
  type: "message_update";
  message: AgentMessage;              // The in-progress message being assembled
  assistantMessageEvent: AssistantMessageEvent; // The raw stream token
}
```

The stream event types (from `@mariozechner/pi-ai`):

```typescript
type AssistantMessageEvent =
  | { type: "start"; partial: AssistantMessage }
  | { type: "text_start"; contentIndex: number; partial: AssistantMessage }
  | { type: "text_delta"; contentIndex: number; delta: string; partial: AssistantMessage }
  | { type: "text_end"; contentIndex: number; content: string; partial: AssistantMessage }
  | { type: "thinking_start"; contentIndex: number; partial: AssistantMessage }
  | { type: "thinking_delta"; contentIndex: number; delta: string; partial: AssistantMessage }
  | { type: "thinking_end"; contentIndex: number; content: string; partial: AssistantMessage }
  | { type: "toolcall_start"; contentIndex: number; partial: AssistantMessage }
  | { type: "toolcall_delta"; contentIndex: number; delta: string; partial: AssistantMessage }
  | { type: "toolcall_end"; contentIndex: number; toolCall: ToolCall; partial: AssistantMessage }
  | { type: "done"; reason: "stop" | "length" | "toolUse"; message: AssistantMessage }
  | { type: "error"; reason: "aborted" | "error"; error: AssistantMessage };
```

For the Hello World thinking block extension, the relevant events are `thinking_start` and `thinking_end`. When `thinking_start` fires, we call `ctx.ui.setWidget()`. When `thinking_end` fires, we clear the widget.

## 4. The ExtensionContext and UI Methods

The `ctx` object passed to every handler is `ExtensionContext`. Its most important field is `ctx.ui: ExtensionUIContext`.

The UI context gives extensions a narrow but powerful set of capabilities:

```typescript
interface ExtensionUIContext {
  // Notifications — transient toasts
  notify(message: string, type?: "info" | "warning" | "error"): void;

  // Widgets — panels above or below the editor
  setWidget(
    key: string,
    content: string[] | undefined,
    options?: { placement?: "aboveEditor" | "belowEditor" }
  ): void;
  // Also accepts a component factory for rich rendering:
  setWidget(
    key: string,
    content: ((tui: TUI, theme: Theme) => Component) | undefined,
    options?: { placement?: "aboveEditor" | "belowEditor" }
  ): void;

  // Footer status line
  setStatus(key: string, text: string | undefined): void;

  // Footer working message during streaming
  setWorkingMessage(message?: string): void;

  // Hidden thinking block label
  setHiddenThinkingLabel(label?: string): void;
}
```

The widget API accepts either a `string[]` for simple text display, or a component factory `(tui, theme) => Component` for rich rendering with colors and borders. The component factory uses `Box` and `Text` from `@mariozechner/pi-tui`:

```typescript
import { Box, Text } from "@mariozechner/pi-tui";
import type { Theme } from "@mariozechner/pi-tui";

function buildBorderedWidget(title: string, lines: string[], theme: Theme, isWarning: boolean) {
  const maxWidth = Math.max(...lines.map(l => l.length), title.length, 20);
  const rule = "─".repeat(maxWidth + 2);
  const text = [
    `┌${rule}┐`,
    `│ ${title.padEnd(maxWidth)} │`,
    `├${rule}┤`,
    ...lines.map(l => `│ ${l.padEnd(maxWidth)} │`),
    `└${rule}┘`,
  ].join("\n");

  const borderColor = isWarning ? "warning" : "dim";
  const colored = theme.fg(borderColor, text);
  const box = new Box(1, 1, (t) => theme.bg("customMessageBg", t));
  box.addChild(new Text(colored, 0, 0));
  return box;
}
```

This pattern is how the session-summary extension renders its bordered widget with muted colors.

## 5. The First Extension: Hello World Thinking Blocks

The goal of this extension was simple: display "Hello World" in a widget whenever the LLM emitted a thinking block. It is the minimal useful demonstration of `message_update` and `ctx.ui.setWidget()`.

The complete extension is 66 lines:

```typescript
import type { ExtensionAPI } from "@mariozechner/pi-coding-agent";

const WIDGET_KEY = "hello-world-thinking";

export default function (pi: ExtensionAPI) {
  let active = false;
  let blockCount = 0;
  let startTime = 0;

  pi.on("turn_start", async () => {
    active = false;
    blockCount = 0;
    startTime = 0;
  });

  pi.on("message_update", async (event, ctx) => {
    const e = event.assistantMessageEvent;

    if (e.type === "thinking_start") {
      active = true;
      blockCount++;
      startTime = Date.now();
      ctx.ui.setWidget(WIDGET_KEY, ["🌍 Hello World"], { placement: "aboveEditor" });
    }

    if (e.type === "thinking_delta" && active) {
      const elapsed = ((Date.now() - startTime) / 1000).toFixed(1);
      ctx.ui.setWidget(WIDGET_KEY, ["🌍 Hello World", `   ⏱️ ${elapsed}s`], { placement: "aboveEditor" });
    }

    if (e.type === "thinking_end" && active) {
      active = false;
      ctx.ui.setWidget(WIDGET_KEY, undefined);
    }

    if (e.type === "error") {
      active = false;
      ctx.ui.setWidget(WIDGET_KEY, undefined);
    }
  });

  pi.on("agent_end", async (_event, ctx) => {
    active = false;
    ctx.ui.setWidget(WIDGET_KEY, undefined);
  });
}
```

The state is stored in closure variables: `active` tracks whether a thinking block is currently open, `blockCount` counts blocks per turn, and `startTime` records when the block opened for elapsed time display.

Safety cleanups are attached to `error` and `agent_end`. This matters: not all providers emit perfectly balanced `thinking_start`/`thinking_end` pairs. Without these handlers, the widget would persist forever if the stream errored.

## 6. The Second Extension: Session Summary Blocks

This extension was more ambitious. Its goal was to force the model to produce a structured `<summary>...</summary>` block at the end of every turn, then display the parsed summary in a widget.

Four subsystems had to be touched:

1. **System prompt injection** (`before_agent_start`) — Append the summary instruction to the system prompt so the model knows the format before it starts generating.
2. **User prompt injection** (`input`) — Append a reminder to every user prompt for near-term reinforcement.
3. **Summary parsing** (`turn_end`) — When the turn completes, search the message for `<summary>...</summary>` and extract the content.
4. **Widget display** (`turn_end`) — Show the parsed summary or a warning.

The system prompt instruction:

```
At the VERY END of EVERY response — after all text, after all tool calls —
you MUST output a <summary>...</summary> block.  This is NOT optional.

The summary MUST contain:
1. THIS TURN: what files you read, edited, wrote, what commands you ran
2. SESSION SO FAR: cumulative progress since the session started
3. ISSUES: any errors, blockers, warnings, or assumptions
4. NEXT STEPS: what to do next
```

The parsing at `turn_end` uses the complete assembled `AssistantMessage`:

```typescript
pi.on("turn_end", async (event, ctx) => {
  const message = event.message;
  if (message.role !== "assistant") return;

  // Extract text from ALL content block types (text + thinking)
  const fullText = message.content
    .filter((block): block is { type: "text"; text: string } => block.type === "text")
    .map((block) => block.text)
    .join("");

  // Find the LAST <summary>...</summary> in the message
  const allMatches = [...fullText.matchAll(/<summary>([\s\S]*?)<\/summary>/gi)];
  const lastMatch = allMatches.length > 0 ? allMatches[allMatches.length - 1] : null;

  if (lastMatch && lastMatch[1].trim()) {
    // Show widget with parsed summary
    ctx.ui.setWidget(WIDGET_KEY, ["📋 Summary", "...", ...], { placement: "aboveEditor" });
  } else {
    // Show warning
    ctx.ui.setWidget(WIDGET_KEY, ["⚠️ No summary detected"], { placement: "aboveEditor" });
  }
});
```

The widget clears at `turn_start`, not `agent_end`. This is because when there are no tool calls, `agent_end` fires immediately after `turn_end`, clearing the widget before the user can see it. Clearing at `turn_start` means the widget persists through the user's reading time and disappears when they type the next prompt.

## 7. The Mutation Problem

One goal of the session-summary extension was to replace the raw `<summary>...</summary>` XML in the assistant message with a nicely formatted block. The approach was to mutate `event.message.content` in `turn_end` to replace the raw XML with formatted text.

This did not work.

The session file was examined after a test run. The JSONL entry still contained the raw `<summary>...</summary>` tags. The mutation code ran—the logs confirmed it—but the change had no effect on what was stored.

The reason is that **Pi passes a copy of the message to `turn_end`, not a reference**. Mutations to the copy are discarded. This is a deliberate design choice by Pi to protect session integrity: extensions cannot corrupt the session file.

The practical consequence is this: the raw XML stays in the message text. The widget is the only place where the parsed, formatted summary appears. The widget approach works perfectly. The inline replacement approach is not available.

This is the most important lesson from building both extensions: **Pi's event handlers receive read-only views of the session state**. The only mutable events are `tool_call` (which can return a block result) and `before_agent_start` (which can return a modified system prompt). Everything else is observation only.

## 8. Custom Messages and Custom Renderers

Pi supports a `CustomMessage` type that extensions can send into the conversation:

```typescript
interface CustomMessage<T = unknown> {
  role: "custom";
  customType: string;           // Extension identifier
  content: string | (TextContent | ImageContent)[];
  display: boolean;             // Show in TUI or hidden (data only)
  details?: T;                 // Extension-specific metadata
  timestamp: number;
}
```

Extensions register a renderer for their `customType`:

```typescript
pi.registerMessageRenderer("my-extension", (message, { expanded }, theme) => {
  const box = new Box(1, 1, (t) => theme.bg("customMessageBg", t));
  box.addChild(new Text(`📋 ${message.content}`, 0, 0));
  return box;
});
```

This is the only way to control how a message looks in the TUI. However, `registerMessageRenderer` only works for `CustomMessage` entries. Standard messages (`UserMessage`, `AssistantMessage`, `ToolResultMessage`) are rendered by Pi's internal renderers and cannot be overridden by extensions. The `message_update` event gives you a view of the streaming tokens, but you cannot redirect how the TUI draws the message bubble.

## 9. State Management

Extensions need to track state across events. The options are:

### Closure variables

The simplest approach. State lives in variables captured by the handler closures:

```typescript
export default function (pi: ExtensionAPI) {
  let active = false;           // Reset on /reload, lost on session switch
  let turnIndex = 0;

  pi.on("turn_start", async () => { active = false; turnIndex++; });
}
```

Closure state is recreated when the extension loads. It survives `/reload` but is lost on session switches. This is correct for transient UI state like widget visibility.

### pi.appendEntry()

For state that must survive session switches, use `pi.appendEntry()`:

```typescript
pi.on("agent_end", async (event, ctx) => {
  pi.appendEntry("my-extension-state", { lastSummary, summaryCount });
});

pi.on("session_start", async (_event, ctx) => {
  for (const entry of ctx.sessionManager.getBranch()) {
    if (entry.type === "custom" && entry.customType === "my-extension-state") {
      // Reconstruct state from session
    }
  }
});
```

Entries are stored in the session JSONL and persist across sessions. They are sent back to the LLM as part of the message context, so keep them small.

## 10. Debugging Strategies

When an extension misbehaves, there are four tools at your disposal.

### 10.1 File Logging

The most reliable debugging tool. Pi extensions run in Node.js, so `fs.appendFileSync()` works:

```typescript
import { appendFileSync, existsSync, mkdirSync } from "node:fs";
import { join } from "node:path";
import { homedir } from "node:os";

const LOG_DIR = join(homedir(), ".pi", "agent", "logs");
const LOG_FILE = join(LOG_DIR, "my-extension.log");

function ensureLogDir() {
  if (!existsSync(LOG_DIR)) mkdirSync(LOG_DIR, { recursive: true });
}

function log(label: string, data: unknown) {
  ensureLogDir();
  appendFileSync(LOG_FILE,
    `[${new Date().toISOString()}] [${label}] ${JSON.stringify(data)}\n`);
}

log("INIT", "Extension loaded");
log("TURN_END", { found: true, summaryLength: 166 });
```

Tail the log in another terminal:

```bash
tail -f ~/.pi/agent/logs/my-extension.log
```

### 10.2 go-minitrace for Session Analysis

Raw session files are verbose JSONL. [go-minitrace](https://github.com/go-go-golems/go-minitrace) converts them to DuckDB-queryable `.minitrace.json` archives. This is essential for understanding what actually happened across multiple turns or sessions.

```bash
# Convert Pi sessions to a queryable archive
go-minitrace convert pi \
  --source-dir ~/.pi/agent/sessions/--home-manuel-code-wesen-2026-04-21--pi-extensions-- \
  --output-dir ./analysis/pi-extensions

# Find extension-related bash commands
go-minitrace query duckdb \
  --archive-glob './analysis/pi-extensions/active/*/*.minitrace.json' \
  --sql-file ./scripts/bash-keyword-search.sql
```

A useful SQL pattern for finding extension-related events:

```sql
SELECT
  id AS session_id,
  title,
  timing->>'started_at' AS started_at,
  CAST(tc->>'emitting_turn_index' AS INT) AS turn_index,
  json_extract_string(tc, '$.input.command') AS bash_command,
  json_extract_string(tc, '$.output.result') AS bash_output
FROM sessions_base,
     UNNEST(tool_calls) AS t(tc)
WHERE (tc->>'tool_name') = 'bash'
  AND (
    json_extract_string(tc, '$.input.command') LIKE '%extension%'
    OR json_extract_string(tc, '$.output.result') LIKE '%error%'
  )
ORDER BY started_at, turn_index
LIMIT 50;
```

### 10.3 The /reload Command

Inside Pi, typing `/reload` reinitializes the extension runtime. Your closure state is reset, but the extension is reloaded from disk. This is the fastest way to test changes without restarting Pi.

### 10.4 Console.log

Pi extensions can use `console.log()` and the output appears in the terminal where Pi is running. It is less persistent than file logging, but useful for quick tracing during development.

## 11. Common Pitfalls

### Mutating standard messages

As described in section 7, `turn_end` gives a read-only copy. Mutations are discarded. Do not rely on message mutation.

### Forgetting to clear widgets

If you set a widget in `turn_end` and never clear it, it persists. Always attach a cleanup handler to `turn_start` or `agent_end`.

### Blocking tool calls incorrectly

The `tool_call` event handler must return exactly `{ block: true, reason: "..." }`. Returning `true` or a partial object does not block the call.

```typescript
// Correct
if (shouldBlock) return { block: true, reason: "Blocked by user" };

// Wrong — this does NOT block
if (shouldBlock) return true;
```

### Wrong input source

The `input` event fires for user prompts, extension-generated prompts, and API calls. Check `event.source`:

```typescript
pi.on("input", async (event) => {
  if (event.source !== "user") return; // Only modify user prompts
  return { prompt: event.prompt + " reminder" };
});
```

### Tool call argument field names

Different tools store their arguments in different fields:

```typescript
// bash stores command in $.input.command
json_extract_string(tc, '$.input.command')

// read stores path in $.input.path
json_extract_string(tc, '$.input.path')

// Some tools use $.input.arguments.path
json_extract_string(tc, '$.input.arguments.path')
```

Always check the actual JSON structure in a session file before writing a query.

## 12. The Three-Layer Extension Design Pattern

Every non-trivial extension touches three concerns: observation (what events to listen to), injection (how to modify prompts or system instructions), and display (how to surface information in the UI). Separating these concerns makes extensions easier to reason about.

```
┌─────────────────────────────────────────────────────┐
│                  OBSERVATION                        │
│  pi.on("message_update", ...)                       │
│  pi.on("turn_end", ...)                            │
│  pi.on("tool_call", ...)                          │
│  Read-only. Events are facts.                      │
└───────────────────────┬─────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────┐
│                   INJECTION                          │
│  before_agent_start → return { systemPrompt: ... }  │
│  input             → return { prompt: ... }         │
│  tool_call         → return { block: true }         │
│  These are the ONLY mutable events.                  │
└───────────────────────┬─────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────┐
│                    DISPLAY                           │
│  ctx.ui.setWidget(...)    → above/below editor      │
│  ctx.ui.notify(...)       → transient toast          │
│  ctx.ui.setStatus(...)   → footer status line       │
│  pi.sendMessage(...)     → inject CustomMessage     │
│  pi.registerMessageRenderer(...) → custom bubble     │
└─────────────────────────────────────────────────────┘
```

## 13. Key Reference

### File locations

| What | Where |
|------|-------|
| Extension files | `~/.pi/agent/extensions/*.ts` (global) or `.pi/extensions/*.ts` (project-local) |
| Session files | `~/.pi/agent/sessions/--slugged-cwd--/*.jsonl` |
| Extension logs | `~/.pi/agent/logs/` |
| Pi config | `~/.pi/agent/settings.json` |

### Extension types

| Package | What it defines |
|--------|----------------|
| `@mariozechner/pi-coding-agent` | `ExtensionAPI`, `ExtensionContext`, `ExtensionUIContext` |
| `@mariozechner/pi-ai` | `AssistantMessageEvent`, `TextContent`, `ThinkingContent` |
| `@mariozechner/pi-tui` | `Box`, `Text`, `Theme` for component rendering |
| `@sinclair/typebox` | Schema definitions for tool parameters |

### The working rules

- Always attach cleanup handlers (`agent_end`, `turn_start`) when you set widget or status state.
- Check `event.source === "user"` before modifying prompts.
- Use `json_extract_string(...)` in DuckDB queries for safe JSON access.
- Prefix helper-only top-level functions with `_` in JS command files.
- Prefer closure state for transient UI; `appendEntry()` for persistent state.
- File logging is more reliable than `console.log()` for post-hoc debugging.

## 14. Related Work

The reference implementations live in:

- `~/.pi/agent/extensions/hello-world-thinking.ts` — thinking block widget
- `~/.pi/agent/extensions/session-summary.ts` — session summary with bordered widget

The design documents, analysis, and playbooks are in:
- `ttmp/2026/04/21/pi-ext-thinking-hello--pi-extension-hello-world-before-thinking-blocks/`
- `ttmp/2026/04/23/pi-ext-session-summary--pi-extension-session-summary-block-with-system-prompt-injection/`

The upstream Pi mono repo and extension documentation:
- [github.com/badlogic/pi-mono](https://github.com/badlogic/pi-mono)
- [packages/coding-agent/docs/extensions.md](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/docs/extensions.md)
- [packages/coding-agent/examples/extensions/](https://github.com/badlogic/pi-mono/tree/main/packages/coding-agent/examples/extensions/)

The go-minitrace transcript analysis system is documented at:
- [[ARTICLE - Playbook - Efficient Past Transcript Analysis with go-minitrace]]

> [!important]
> The most important single fact about Pi extension development: event handlers receive read-only copies of session state. The only events where your return value changes behavior are `before_agent_start` (system prompt), `input` (prompt), and `tool_call` (blocking). Everything else is observation only.

## KB reviews

- [[KB-BATCH14-pi-extensions-tooling]] (2026-05-11) — Batch K Pi extension/tooling review; created [[pi-extension-event-seams]] and advanced Pi TUI/model-config candidates.

## Related KB entries

- [[pi-extension-authoring-mental-model]] — 10-minute orientation to Pi extension lifecycle, events, tools, UI surfaces, and state scopes.
- [[pi-extension-event-seams]] — Pi lifecycle/event seams, prompt shaping, tool-call mutation, TUI surfaces, and model/config integration discipline.
- [[host-mediated-sandbox-principles]] — the host/runtime boundary principle behind narrow extension capabilities and mediated side effects.

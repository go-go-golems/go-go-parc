---
title: "Pi Extension: Hello World Before Thinking Blocks"
aliases:
  - Pi Hello World Extension
  - Hello World Thinking Extension
tags:
  - project
  - pi
  - extensions
  - typescript
  - tui
  - agent-system
  - coding-agent
status: active
type: project
created: 2026-04-21
repo: /home/manuel/code/wesen/2026-04-21--pi-extensions
---

# Pi Extension: Hello World Before Thinking Blocks

This project is an educational deep-dive into Pi's extension system. The stated goal was to build an extension that displays "Hello World" whenever the LLM emits a thinking block. The more important goal was to understand Pi's architecture deeply enough to write extensions from first principles — message types, the event stream protocol, the extension lifecycle, and the TUI's widget system.

> [!summary]
> Three documents were produced and uploaded to reMarkable:
> 1. **Analysis** — system architecture, message types, event stream protocol, thinking block lifecycle, design options comparison
> 2. **Implementation guide** — minimal working extension, production-quality enhanced version, debugging playbook, copy-paste-ready code
> 3. **API cheat sheet** — quick reference for ExtensionAPI, event types, AssistantMessageEvent, and UI methods

## Why this project exists

Pi is a terminal coding agent built by Mario Zechner. It runs inside a terminal, manages persistent conversation trees (sessions stored as JSONL), and exposes a TypeScript extension API that lets you customize nearly every aspect of its behavior. The goal of this project was to understand that extension API well enough to write a non-trivial extension — one that reacts to a specific event in the LLM response stream rather than just registering a command or tool.

The "Hello World before thinking blocks" feature was chosen because it sits at the intersection of three systems: the provider layer (which normalizes LLM output into Pi's event protocol), the message assembly layer (which streams events into a growing AssistantMessage), and the TUI layer (which renders widgets). Understanding how those three connect is the core of Pi extension authoring.

## Project shape

The documentation is stored in a docmgr ticket workspace. The implementation is a single TypeScript file that lives in the Pi extensions directory.

### Documentation (docmgr ticket)

```
ttmp/2026/04/21/pi-ext-thinking-hello--pi-extension-hello-world-before-thinking-blocks/
├── index.md
├── changelog.md
├── tasks.md
├── design/
│   ├── analysis.md          ← system architecture deep-dive
│   └── implementation.md    ← code walkthrough, testing, packaging
├── reference/
│   └── api-cheatsheet.md    ← quick API reference
├── playbooks/
│   └── setup-and-test.md   ← step-by-step testing commands
└── sources/                 ← saved upstream resources
    ├── pi-extensions-docs.md
    ├── pi-session-docs.md
    ├── extending-pi-readme.md
    ├── extending-pi-skill.md
    ├── pi-ai-types.ts
    ├── extension-types.ts
    ├── messages.ts
    ├── event-stream.ts
    ├── hidden-thinking-label.ts
    ├── message-renderer.ts
    ├── widget-placement.ts
    ├── status-line.ts
    └── extension-examples-readme.md
```

### The extension file

```bash
~/.pi/agent/extensions/hello-world-thinking.ts
```

A single TypeScript file (66 lines). No build step, no dependencies. Pi uses [jiti](https://github.com/unjs/jiti) to run `.ts` files directly.

## Core mental model: how thinking blocks reach the extension

Pi connects LLMs to the terminal through a layered architecture. Before writing the extension, it was necessary to understand the path a thinking block takes from the LLM API to the extension handler. Here is the mental model that the analysis document developed.

When you send a prompt, Pi sends it to an LLM provider. The LLM does not return a complete response — it streams tokens. The provider normalizes those tokens into a stream of `AssistantMessageEvent` objects. Pi calls this stream `AssistantMessageEventStream`. Each event carries a token (or a group of tokens) and a partial `AssistantMessage` that is being assembled in real time.

The most important event types for thinking blocks:

```typescript
type AssistantMessageEvent =
  | { type: "thinking_start"; contentIndex: number; partial: AssistantMessage }
  | { type: "thinking_delta"; contentIndex: number; delta: string; partial: AssistantMessage }
  | { type: "thinking_end"; contentIndex: number; content: string; partial: AssistantMessage }
  | { type: "text_start"; contentIndex: number; partial: AssistantMessage }
  | { type: "text_delta"; contentIndex: number; delta: string; partial: AssistantMessage }
  | { type: "toolcall_start"; contentIndex: number; partial: AssistantMessage }
  // ... and more
```

The sequence for a thinking block looks like this:

```
thinking_start (contentIndex: 1, partial: {...})
thinking_delta (contentIndex: 1, delta: "1. First step...")
thinking_delta (contentIndex: 1, delta: "\n2. Second step...")
thinking_end (contentIndex: 1, content: "1. First step...\n2. Second step...")
```

Not all models emit thinking blocks. The following do:

| Provider | Model | Thinking blocks? |
|----------|-------|----------------|
| Anthropic | Claude 3.7 Sonnet | ✅ Yes |
| Anthropic | Claude 3.5 Sonnet | ❌ No |
| OpenAI | o1, o3-mini | ✅ Yes |
| OpenAI | GPT-4o | ❌ No |
| DeepSeek | DeepSeek-R1, V3 | ✅ Yes |

## Extension lifecycle

Pi fires events in a predictable sequence. Extensions subscribe to events using `pi.on()`. The most relevant events for thinking block interception are:

```text
session_start
  │
input (extension can transform the prompt)
  │
before_agent_start (extension can inject messages or modify system prompt)
  │
agent_start
  │
message_start ────────────────────────────────────────────────────────┐
message_update ──────────────────────────────────────────────────────►│ (fires for every token)
message_end ───────────────────────────────────────────────────────┘
  │
tool_execution_start
tool_call (extension can block/modify tool calls)
tool_result
tool_execution_end
  │
agent_end
```

The key insight: **`message_update`** is the only event that gives you access to the raw `AssistantMessageEvent` (including `thinking_start` and `thinking_end`). Other events like `message_start` and `message_end` give you the fully assembled message but not the streaming events.

## Implementation details

### The widget approach

The chosen implementation uses `ctx.ui.setWidget()` — a documented public API that places a string array above or below the editor. When `thinking_start` fires, the extension shows the widget. When `thinking_end` fires, it clears the widget. This is the safest approach: it uses a public API, does not mutate messages, and works across all providers.

```typescript
const WIDGET_KEY = "hello-world-thinking";

export default function (pi: ExtensionAPI) {
  let active = false;
  let startTime = 0;

  pi.on("turn_start", async () => {
    active = false;
    startTime = 0;
  });

  pi.on("message_update", async (event, ctx) => {
    const e = event.assistantMessageEvent;

    if (e.type === "thinking_start") {
      active = true;
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

### Safety cleanups

The extension registers three cleanup handlers to prevent the widget from persisting:

1. **`agent_end`**: Fires when the agent loop terminates. Clears the widget in all cases.
2. **`message_end`**: Fires when the message is complete. Clears the widget if `thinking_end` was somehow missed.
3. **`message_update` → `error`**: Fires when the stream errors. Clears the widget immediately.

This is defensive programming. Not all providers emit perfectly balanced `thinking_start`/`thinking_end` pairs.

### State management

State is stored in closure variables (`active`, `blockCount`, `startTime`). This is intentional:

- Closure state is reset on `/reload`, which is correct for transient UI state
- It does not need to survive session switches
- `pi.appendEntry()` would persist to the session file, which is overkill for UI-only state

### Design options considered

The analysis document evaluated four approaches:

| Approach | Mechanism | Pros | Cons |
|----------|-----------|------|------|
| **Widget** (chosen) | `ctx.ui.setWidget()` on `thinking_start`/`thinking_end` | Documented, non-invasive, provider-agnostic | Appears above editor, not inline |
| **Notification** | `ctx.ui.notify()` on `thinking_start` | Dead simple | Transient, may be missed |
| **Custom message** | `pi.sendMessage()` to inject a CustomMessage entry | Persistent, renderable | Affects context window, separate bubble |
| **Content mutation** | Mutate `event.message.content` to insert text before thinking block | Inline, visually "before the block" | Undocumented, fragile, corrupts session |

The widget approach was chosen because it is the only one that is fully documented, non-invasive, and guaranteed to work across providers. The content mutation approach was documented as experimental but explicitly warned against for production use.

## Extension locations

Pi discovers extensions from three locations:

| Location | Scope | Hot reload |
|---------|-------|-----------|
| `~/.pi/agent/extensions/*.ts` | Global (all projects) | Yes, via `/reload` |
| `.pi/extensions/*.ts` | Project-local | Yes, via `/reload` |
| `pi -e ./path.ts` | One-shot for this session only | No |

The extension is installed at `~/.pi/agent/extensions/hello-world-thinking.ts`.

## Architecture diagram

```text
┌──────────────────────────────────────────────────────────────────┐
│                       USER TERMINAL                               │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                         TUI                                  │  │
│  │  ┌────────────┐  ┌──────────────────┐  ┌────────────────┐  │  │
│  │  │  Header    │  │     Widget        │  │   Message       │  │  │
│  │  │            │  │  "🌍 Hello World" │  │   Pane         │  │  │
│  │  └────────────┘  └──────────────────┘  └────────────────┘  │  │
│  │  ┌──────────────────────────────────────────────────────┐   │  │
│  │  │                   Editor                             │   │  │
│  │  └──────────────────────────────────────────────────────┘   │  │
│  │  ┌──────────────────────────────────────────────────────┐   │  │
│  │  │  Footer: [status] [model] [tokens] [git branch]     │   │  │
│  │  └──────────────────────────────────────────────────────┘   │  │
│  └──────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│                    EXTENSION RUNTIME                              │
│  hello-world-thinking.ts                                          │
│                                                                    │
│  pi.on("message_update", (event, ctx) => {                        │
│    if (event.assistantMessageEvent.type === "thinking_start") {   │
│      ctx.ui.setWidget("hello-world-thinking", ["🌍 Hello World"]);  │
│    }                                                               │
│    if (event.assistantMessageEvent.type === "thinking_end") {      │
│      ctx.ui.setWidget("hello-world-thinking", undefined);           │
│    }                                                               │
│  });                                                               │
└──────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│                    AGENT SESSION RUNTIME                           │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────────┐   │
│  │  Input   │─►│  Agent   │─►│ Provider │─►│    LLM API       │   │
│  │ Handler  │  │  Loop    │  │  Layer   │  │ (Claude/GPT/DS) │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────────────┘   │
│       │             │             │              │               │
│       ▼             ▼             ▼              ▼               │
│  before_agent_start  message_update  after_provider_response  Token stream
│  agent_start       thinking_start   (provider-specific)
│  message_start     thinking_delta
│  message_end       thinking_end
└──────────────────────────────────────────────────────────────────┘
```

## Event flow for one turn with thinking

```
1. USER types prompt + Enter

2. BEFORE AGENT STARTS
   └── before_agent_start fires
       └── Extension could inject messages or modify system prompt

3. MESSAGE STARTS
   └── message_start fires

4. MESSAGE STREAMS (message_update fires repeatedly)
   └── text_delta (user's text assembled)
   └── thinking_start ★
       └── OUR EXTENSION: ctx.ui.setWidget("hello-world-thinking", ["🌍 Hello World"])
   └── thinking_delta (reasoning tokens stream in)
       └── OUR EXTENSION: ctx.ui.setWidget with elapsed time
   └── thinking_end ★
       └── OUR EXTENSION: ctx.ui.setWidget("hello-world-thinking", undefined)
   └── toolcall_delta (tool call assembled)
   └── toolcall_end (tool call complete)

5. TOOL EXECUTES
   └── tool_execution_start
   └── tool_call (extension can block)
   └── tool_result
   └── tool_execution_end

6. MESSAGE ENDS
   └── message_end fires
       └── OUR EXTENSION: ctx.ui.setWidget cleanup (safety net)

7. AGENT ENDS
   └── agent_end fires
       └── OUR EXTENSION: ctx.ui.setWidget cleanup (safety net)
```

## Key files and their roles

| File | Role |
|------|------|
| `~/.pi/agent/extensions/hello-world-thinking.ts` | The extension (the only file we wrote) |
| `packages/coding-agent/docs/extensions.md` | Primary extension system documentation |
| `packages/coding-agent/docs/session.md` | Message types, content blocks, session entry format |
| `packages/ai/src/types.ts` | `AssistantMessageEvent` stream protocol definition |
| `packages/coding-agent/src/core/extensions/types.ts` | `ExtensionAPI`, `ExtensionContext`, event handlers |
| `packages/coding-agent/examples/extensions/hidden-thinking-label.ts` | Example: thinking block UI customization |
| `packages/coding-agent/examples/extensions/widget-placement.ts` | Example: widget placement above/below editor |
| `packages/coding-agent/examples/extensions/message-renderer.ts` | Example: custom message rendering |
| `packages/coding-agent/examples/extensions/status-line.ts` | Example: footer status manipulation |
| `packages/ai/src/utils/event-stream.ts` | `AssistantMessageEventStream` implementation |
| `packages/coding-agent/src/core/messages.ts` | Extended message types (BashExecutionMessage, CustomMessage) |

## Open questions

- Should the extension also work with models that emit thinking content as plain text (no `thinking_start`/`thinking_end` events)? This would require heuristics to detect thinking patterns in `text_delta` streams.
- Should the widget show additional information, such as the number of reasoning tokens or the elapsed time?
- Should the extension register a command like `/hello-thinking` to toggle the behavior on and off?
- Should the extension track statistics across turns (total thinking time, thinking blocks per turn)?

## Near-term next steps

- [ ] Test the extension with Claude 3.7 Sonnet to verify widget display
- [ ] Add a `/hello-thinking` toggle command
- [ ] Consider tracking thinking time statistics across a session
- [ ] Write a follow-up article about extending the pattern to detect non-thinking-block reasoning (heuristic text-based detection)

## Important project docs

These live in the docmgr ticket workspace:

- `ttmp/.../design/analysis.md` — full system analysis
- `ttmp/.../design/implementation.md` — complete implementation guide
- `ttmp/.../reference/api-cheatsheet.md` — API quick reference
- `ttmp/.../playbooks/setup-and-test.md` — testing playbook

Saved upstream sources:

- `ttmp/.../sources/pi-extensions-docs.md` — defuddled extensions.md
- `ttmp/.../sources/pi-session-docs.md` — defuddled session.md
- `ttmp/.../sources/pi-ai-types.ts` — @mariozechner/pi-ai type definitions
- `ttmp/.../sources/extension-types.ts` — ExtensionAPI type definitions
- `ttmp/.../sources/hidden-thinking-label.ts` — thinking label example
- `ttmp/.../sources/message-renderer.ts` — message renderer example
- `ttmp/.../sources/widget-placement.ts` — widget placement example

## Project working rule

> [!important]
> Always verify that your model emits thinking blocks before debugging an extension that intercepts thinking events. Add `console.log()` temporarily to trace `message_update` event types. If you only see `text_delta` events (no `thinking_start`), the model does not emit thinking blocks — switch models, not code.

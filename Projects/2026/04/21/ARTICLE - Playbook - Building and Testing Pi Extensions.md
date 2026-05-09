---
title: "Playbook: Building and Testing Pi Extensions"
aliases:
  - Pi Extension Authoring
  - Pi Extension Development
  - Writing Pi Extensions
tags:
  - article
  - playbook
  - pi
  - extensions
  - typescript
  - tui
  - agent-system
  - coding-agent
status: active
type: article
created: 2026-04-21
repo: /home/manuel/code/wesen/2026-04-21--pi-extensions
---

# Playbook: Building and Testing Pi Extensions

This is a practical playbook for building, testing, and debugging Pi extensions. It covers the extension lifecycle, the event system, the UI API, common failure modes, and the tools you need to debug extensions in a live terminal session.

The reference implementation is the [[PROJ - Pi Extension - Hello World Before Thinking Blocks|Hello World Thinking Block]] extension. That project produced detailed analysis and implementation documents; this playbook distills the engineering knowledge into reusable guidance.

## When to write an extension

Pi extensions are the right tool when you need:

- **Event hooks** — to react to lifecycle events (session start, message stream, tool calls)
- **Custom tools** — to register new tools the LLM can call
- **Command registration** — to add slash commands like `/mycommand`
- **UI manipulation** — to display widgets, notifications, or custom TUI components
- **Policy enforcement** — to block or modify tool calls before they execute

If you can solve the problem with `bash` commands and written instructions, use a **Skill** instead. Skills are simpler and require no code to maintain. Extensions are for runtime behavior changes that cannot be expressed as text.

## The extension factory pattern

Every extension is a single TypeScript module that exports a default factory function:

```typescript
import type { ExtensionAPI } from "@mariozechner/pi-coding-agent";

export default function (pi: ExtensionAPI) {
  // Subscribe to events
  pi.on("session_start", async (_event, ctx) => {
    ctx.ui.notify("Extension loaded!", "info");
  });

  // Register a command
  pi.registerCommand("hello", {
    description: "Say hello",
    handler: async (args, ctx) => {
      ctx.ui.notify(`Hello ${args || "world"}!`, "info");
    },
  });
}
```

The factory receives `pi: ExtensionAPI` — your gateway to the entire system. Use `import type` for Pi packages. No runtime imports needed; Pi resolves `@mariozechner/pi-coding-agent` internally via jiti.

The factory can be synchronous or asynchronous. If it returns a `Promise`, Pi awaits it before firing `session_start`.

## The event system

Pi fires dozens of events in a predictable sequence. Subscribe with `pi.on(eventName, handler)`. Each handler receives `(event, ctx)`:

```typescript
pi.on("message_update", async (event, ctx) => {
  // event contains event-specific data
  // ctx.ui has all UI methods
});
```

The handler type is:

```typescript
type ExtensionHandler<E, R = undefined> = (event: E, ctx: ExtensionContext) => Promise<R | void> | R | void;
```

Most handlers return `void`. Some events allow a return value to modify behavior (e.g., `tool_call` can return `{ block: true, reason: "..." }` to block a tool call).

### The most useful events

| Event | When it fires | What you get |
|-------|--------------|-------------|
| `session_start` | Session begins or reloads | `reason`, session file path |
| `before_agent_start` | Before agent loop starts | Prompt, system prompt, can inject messages |
| `message_start` | Message begins assembling | `AgentMessage` in progress |
| `message_update` | Token streamed from LLM | `AssistantMessageEvent` — the key one |
| `message_end` | Message fully assembled | Complete `AgentMessage` |
| `tool_execution_start` | Tool begins executing | `toolCallId`, `toolName`, `args` |
| `tool_call` | Tool invoked by LLM | Can block or modify |
| `tool_result` | Tool finished | Can modify result |
| `agent_end` | Agent loop ends | All messages from this turn |
| `turn_start` / `turn_end` | Turn boundaries | `turnIndex`, messages, tool results |

## The message stream: understanding message_update

`message_update` is the most powerful event because it gives you access to the raw `AssistantMessageEvent` stream — the same stream that Pi uses to assemble messages token-by-token.

The event object:

```typescript
interface MessageUpdateEvent {
  type: "message_update";
  message: AgentMessage;              // The growing message object
  assistantMessageEvent: AssistantMessageEvent; // The raw stream event
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

Notice `thinking_start`, `thinking_delta`, and `thinking_end`. These are the events that let you intercept thinking blocks as they stream.

## The UI API: ExtensionUIContext

Every handler receives `ctx: ExtensionContext`. The `ctx.ui` field is `ExtensionUIContext` and provides all UI methods:

```typescript
// Show a transient notification
ctx.ui.notify(message: string, type?: "info" | "warning" | "error"): void;

// Place a widget above or below the editor
ctx.ui.setWidget(
  key: string,
  content: string[] | undefined,
  options?: { placement?: "aboveEditor" | "belowEditor" }
): void;

// Set footer status text
ctx.ui.setStatus(key: string, text: string | undefined): void;

// Set the working message shown during streaming
ctx.ui.setWorkingMessage(message?: string): void;

// Customize the collapsed thinking block label
ctx.ui.setHiddenThinkingLabel(label?: string): void;

// Customize the streaming spinner
ctx.ui.setWorkingIndicator(options?: { frames?: string[]; intervalMs?: number }): void;

// Show a custom TUI component (complex interactions)
ctx.ui.custom(factory: (tui, theme, keybindings, done) => Component, options?): Promise<T>;
```

For most extensions, `notify()`, `setWidget()`, and `setStatus()` are the tools you need.

## Common patterns

### Pattern 1: React to a specific event type in message_update

```typescript
pi.on("message_update", async (event, ctx) => {
  const e = event.assistantMessageEvent;

  if (e.type === "thinking_start") {
    ctx.ui.setWidget("my-key", ["Action started"]);
  }

  if (e.type === "thinking_end") {
    ctx.ui.setWidget("my-key", undefined);
  }
});
```

### Pattern 2: Block a tool call with confirmation

```typescript
pi.on("tool_call", async (event, ctx) => {
  if (event.toolName === "bash" && event.input.command?.includes("rm -rf")) {
    const ok = await ctx.ui.confirm("Dangerous!", "Allow rm -rf?");
    if (!ok) return { block: true, reason: "Blocked by user" };
  }
});
```

Return `{ block: true, reason: "..." }` to prevent the tool from executing.

### Pattern 3: Register a custom command

```typescript
pi.registerCommand("hello", {
  description: "Say hello (usage: /hello [name])",
  handler: async (args, ctx) => {
    ctx.ui.notify(`Hello ${args || "world"}!`, "info");
  },
});
```

### Pattern 4: Register a custom tool

```typescript
import { Type } from "@sinclair/typebox";

pi.registerTool({
  name: "greet",
  label: "Greeting",
  description: "Generate a greeting for someone",
  parameters: Type.Object({
    name: Type.String({ description: "Name to greet" }),
  }),
  async execute(toolCallId, params, signal, onUpdate, ctx) {
    return {
      content: [{ type: "text", text: `Hello, ${params.name}!` }],
      details: {},
    };
  },
});
```

### Pattern 5: Safety cleanups

Always clean up after yourself. If you set a widget or status, clear it when the agent ends:

```typescript
pi.on("agent_end", async (_event, ctx) => {
  ctx.ui.setWidget("my-key", undefined);
  ctx.ui.setStatus("my-key", undefined);
});
```

## Installation and hot reload

### Option A: Auto-discovery (daily use)

Put the file in one of these locations:

| Location | Scope |
|---------|-------|
| `~/.pi/agent/extensions/*.ts` | Global (all projects) |
| `.pi/extensions/*.ts` | Project-local |

Pi discovers and loads extensions on startup. Use `/reload` inside Pi to hot-reload after edits.

### Option B: One-shot with `--extension`

```bash
pi -e ~/.pi/agent/extensions/my-extension.ts
```

The extension loads only for this session. No hot reload.

## Testing checklist

Before calling an extension complete:

- [ ] Extension file is in the right location (`~/.pi/agent/extensions/*.ts`)
- [ ] Pi loads the extension without errors on startup
- [ ] Extension behavior triggers correctly on the target event
- [ ] Extension cleans up after itself (widgets cleared, statuses reset)
- [ ] Extension works with `/reload` after edits
- [ ] No `console.log()` spam left in production code
- [ ] Code is formatted and commented
- [ ] Tested with a model that exercises the target path

## Debugging

### Extension not loading?

Check terminal output on Pi startup. Look for lines like:

```
Loading extensions from /home/manuel/.pi/agent/extensions...
  ✓ my-extension.ts
```

If you see an error, it's usually a TypeScript syntax issue or a missing type import.

### Type errors?

Use `import type { ... }` for Pi packages:

```typescript
// Correct
import type { ExtensionAPI } from "@mariozechner/pi-coding-agent";

// Wrong (runtime import won't work)
import { ExtensionAPI } from "@mariozechner/pi-coding-agent";
```

### Something not triggering?

Add temporary debug logging:

```typescript
pi.on("message_update", async (event) => {
  console.log("[debug]", event.assistantMessageEvent.type);
});
```

Then `/reload` and watch the terminal output.

### Widget not appearing?

Your model might not emit the event type you are looking for. Not all models emit thinking blocks. Add debug logging and check what `message_update` event types you actually receive.

## Common failure modes

| Failure mode | Symptom | Fix |
|------------|---------|-----|
| Widget never clears | Widget persists after event ends | Add `agent_end` and `message_end` cleanup handlers |
| Extension not loaded | No behavior change | Check file path: `~/.pi/agent/extensions/*.ts` |
| Type error on import | `Cannot find module` or similar | Use `import type` for Pi packages |
| Model emits no thinking | `thinking_start` never fires | Switch to a thinking-capable model (Claude 3.7, o1, DeepSeek-R1) |
| Blocked tool keeps running | Tool executes after block | Check return value: must be `{ block: true, reason: "..." }` exactly |
| State lost on reload | Extension resets | Closure state is reset on `/reload`. Use `session_start` to reconstruct if needed. |

## Key source files

For deep reference, these files in the pi-mono repo are authoritative:

| File | What it covers |
|------|---------------|
| `packages/coding-agent/docs/extensions.md` | Extension system overview, event reference |
| `packages/coding-agent/docs/session.md` | Message types, content blocks, session entry format |
| `packages/ai/src/types.ts` | `AssistantMessageEvent` stream protocol |
| `packages/coding-agent/src/core/extensions/types.ts` | `ExtensionAPI`, `ExtensionContext`, all handler signatures |
| `packages/coding-agent/src/core/messages.ts` | Extended types: `CustomMessage`, `BashExecutionMessage` |
| `packages/ai/src/utils/event-stream.ts` | `AssistantMessageEventStream` implementation |
| `packages/coding-agent/examples/extensions/` | Working example extensions |

## Pseudocode: the extension lifecycle

```
pi starts
  │
  ├─ extension factory runs
  │     └─ pi.on() registers handlers
  │     └─ pi.registerTool() adds tools
  │     └─ pi.registerCommand() adds commands
  │
  ├─ session_start fires
  │
  └─ resources_discover fires
        └─ Extension can return additional skill/prompt/theme paths

user sends prompt
  │
  ├─ input fires (extension can transform prompt)
  ├─ before_agent_start fires (extension can inject messages)
  │
  ├─ agent_start fires
  │
  ├─ message_start fires
  ├─ message_update fires (repeat: token-by-token)
  │     └─ YOUR HANDLER: react to specific event types here
  ├─ message_end fires
  │
  ├─ tool_execution_start fires
  ├─ tool_call fires (extension can block)
  ├─ tool_result fires (extension can modify)
  ├─ tool_execution_end fires
  │
  ├─ turn_end fires
  │
  └─ agent_end fires

/reload
  │
  └─ Extension runtime re-initializes
        └─ Closure state is reset
        └─ Handlers are re-registered
```

## Related notes

- [[PROJ - Pi Extension - Hello World Before Thinking Blocks]] — reference implementation with full analysis and implementation documents
- [[PROJ - Pi Extension - Hello World Before Thinking Blocks]] points to docmgr ticket at `ttmp/.../pi-ext-thinking-hello--.../` for detailed analysis, implementation guide, API cheatsheet, and testing playbook

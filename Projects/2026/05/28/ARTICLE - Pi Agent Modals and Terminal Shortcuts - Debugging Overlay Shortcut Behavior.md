---
title: "Pi Agent Modals and Terminal Shortcuts: Debugging Overlay Shortcut Behavior"
aliases:
  - Pi Agent Modal Shortcut Debugging
  - Pi TUI Overlay Shortcut Playbook
  - Modal Shortcut Lab Report
tags:
  - article
  - playbook
  - pi
  - tui
  - extensions
  - keyboard-shortcuts
  - terminal
  - kitty
  - tmux
status: active
type: article
created: 2026-05-28
repo: /home/manuel/code/wesen/2026-04-21--pi-extensions
source_ticket: MODAL-SHORTCUT-LAB
---

# Pi Agent Modals and Terminal Shortcuts: Debugging Overlay Shortcut Behavior

This note preserves the engineering knowledge from the Pi modal shortcut investigation. The immediate incident was that `Ctrl+Shift+P` did not reliably open the command palette inside Kitty/tmux: it appeared only after a later keypress, while `Ctrl+Shift+O` did nothing. The durable lesson is broader: a modal shortcut in Pi crosses terminal key protocols, tmux forwarding, Pi’s raw input path, extension shortcut registration, overlay focus, render scheduling, and component input handling.

> [!summary]
> - `ctx.ui.custom()` and Pi TUI overlays were not the root cause; command-opened overlays rendered correctly.
> - `Ctrl+Shift+P` conflicted with Kitty’s default key-chord prefix, and `Ctrl+Shift+O` conflicted with a Kitty terminal action.
> - The safe production default became `Ctrl+Shift+Alt+N`, with `Ctrl+Space` kept as an opt-in candidate.
> - Future shortcut bugs should be debugged layer by layer: command path, registered shortcut path, raw terminal input, overlay focus, render, and immediate-close input.

## Why this note exists

The original debugging path produced a useful minimal laboratory: `extensions/modal-shortcut-lab`. That lab made it possible to separate terminal delivery problems from Pi rendering problems. Without that separation, a developer can easily patch the wrong layer. A key that never reaches Pi cannot be fixed by changing `render()`. A modal that is built but never focused cannot be fixed by changing Kitty configuration. A key-release sequence that closes a modal immediately requires input filtering, not a new shortcut.

The note should be used as a playbook whenever a Pi extension needs a keyboard-opened overlay or whenever a shortcut behaves differently in Kitty, tmux, SSH, or another terminal stack.

## When to use this pattern

Use this pattern when:

- a Pi extension opens a modal, palette, dashboard, picker, or other custom TUI component from a keyboard shortcut
- a shortcut works in one terminal but not another
- a shortcut appears to open a modal only after a later keypress
- a shortcut opens a modal that immediately disappears
- a raw terminal listener needs to consume a shortcut before the editor sees it
- a terminal-level shortcut table may conflict with an application-level shortcut

Do not start with this full investigation path when a slash command fails to load the extension at all. In that case, first debug extension discovery, TypeScript load errors, and command registration.

## Core mental model

A Pi modal shortcut has several independent layers. Each layer must pass evidence to the next layer.

```mermaid
flowchart TD
    Key[Physical key press] --> Terminal[Terminal emulator]
    Terminal -->|forwards sequence| Tmux[tmux/session layer]
    Terminal -->|reserved shortcut| TerminalAction[Terminal action or key-chord state]
    Tmux --> RawInput[Pi TUI raw input]
    RawInput --> Parser[matchesKey / parseKey]
    Parser --> Listener[Extension raw terminal listener]
    Parser --> Registered[pi.registerShortcut fallback]
    Listener --> Scheduler[setImmediate scheduled open]
    Scheduler --> CustomUI[ctx.ui.custom]
    Registered --> CustomUI
    CustomUI --> Overlay[Overlay handle + focus]
    Overlay --> Render[Component render(width)]
    Overlay --> Input[Focused component handleInput]

    style TerminalAction fill:#ffd6d6,stroke:#cc3333
    style Overlay fill:#d9ecff,stroke:#2f6db0
    style Render fill:#e1ffd9,stroke:#3c8c2f
```

The important rule is that Pi can only match a shortcut after the terminal forwards a sequence to the child process. If Kitty reserves a key, tmux consumes it, or the desktop input method captures it, then Pi’s parser and overlay code are never reached.

## The TUI component contract

Pi custom UI is built on `@mariozechner/pi-tui`. A component renders terminal rows and optionally handles focused input.

```ts
interface Component {
  render(width: number): string[];
  handleInput?(data: string): void;
  wantsKeyRelease?: boolean;
  invalidate(): void;
}
```

The component contract is intentionally small. The component should treat `width` as authoritative and return visible rows that fit inside it. If rows contain ANSI styling, the implementation must use visible-width helpers rather than raw string length. A correctly written component can be used as a replacement editor surface or as an overlay.

The modal shortcut lab uses a deliberately small component. It records render count, input count, and the last input. Escape cancels; Enter accepts. The small state surface makes it a good diagnostic instrument: when the lab fails, the failure is probably in setup, focus, rendering, shortcut delivery, or input replay rather than in application-specific state.

## Opening overlays with `ctx.ui.custom()`

A modal overlay is opened by calling `ctx.ui.custom()` with a component factory and overlay options.

```ts
const result = await ctx.ui.custom<LabResult>(
  (tui, theme, _keybindings, done) => {
    const component = new LabModal({
      theme,
      done,
      requestRender: () => tui.requestRender(),
    });
    return component;
  },
  {
    overlay: true,
    overlayOptions: {
      anchor: "center",
      width: 72,
      maxHeight: 16,
      margin: 1,
    },
    onHandle: (handle) => {
      handle.focus();
      tui.requestRender(true);
    },
  },
);
```

The factory creates the component. The `done` callback closes the custom UI and resolves the promise. In overlay mode, Pi stacks the component above the current chat/editor UI. The overlay should be focused if it must receive Escape, Enter, arrows, or printable keys.

## Why the lab exposes multiple entry paths

The modal shortcut lab is structured as a diagnostic matrix. Every entry path opens the same modal but exercises a different layer.

| Entry path | Example | What it proves |
| --- | --- | --- |
| Notification command | `/modal-lab notify` | Extension load, command dispatch, and `ctx.ui.notify()` work. |
| Replacement UI | `/modal-lab replace` | `ctx.ui.custom()` can mount a component outside overlay mode. |
| Command overlay | `/modal-lab overlay` | Overlay rendering works without keyboard shortcut timing. |
| Scheduled command overlay | `/modal-lab scheduled` | Deferred overlay creation works after the command returns. |
| Registered shortcut | `Ctrl+Shift+M` | Pi’s high-level shortcut path can open UI. |
| Registered scheduled shortcut | `Ctrl+Shift+Alt+M` | Deferring from a shortcut callback is safe. |
| Raw original target | `Ctrl+Shift+P` | The original command-palette chord can be inspected. |
| Raw safe candidate | `Ctrl+Shift+Alt+N` | A Kitty-safe candidate can be verified. |
| Raw alternate candidate | `Ctrl+Space` | An ergonomic override candidate can be tested. |

A good shortcut investigation should use the simplest passing entry path as a baseline. If `/modal-lab overlay` works but `Ctrl+Shift+P` does not, the overlay component is not the first suspect.

## Terminal protocol findings

The decisive evidence came from comparing raw input with Kitty’s default shortcut table. Pi’s TUI parser can recognize modern modified-key sequences such as CSI-u. Recognition was not the problem.

| Physical key | CSI-u sequence | Pi parse result | Investigation result |
| --- | --- | --- | --- |
| `Ctrl+Shift+P` | `ESC[112:80;6u` | `shift+ctrl+p` | Parser recognized it, but Kitty reserves `Ctrl+Shift+P` as a key-chord prefix. |
| `Ctrl+Shift+O` | terminal-dependent | `ctrl+shift+o` when delivered | Kitty binds this to `pass_selection_to_program`; Pi may never see it. |
| `Ctrl+Shift+Alt+N` | `ESC[110:78;8u` | `shift+ctrl+alt+n` | Verified as the safe default candidate. |
| `Ctrl+Space` | `ESC[32;5u` | `ctrl+space` | Works in smoke tests; may conflict with IME/tmux/user config. |

The practical conclusion is that a shortcut can be syntactically valid in Pi and still be unsuitable as a default. A production default must be evaluated against terminal emulator shortcuts, session/multiplexer behavior, and Pi’s parser.

## Scheduling the open

Raw terminal callbacks run inside the input dispatch path. Opening a modal directly inside that path can couple UI construction to the current key event. The lab and command palette therefore schedule raw opens with `setImmediate()`.

```ts
function scheduleOpen(ctx: ExtensionCommandContext, source: string): void {
  if (openScheduled || modalOpen) return;
  openScheduled = true;

  setImmediate(() => {
    openScheduled = false;
    void openModal(ctx, source);
  });
}
```

The guard prevents duplicate opens from press/release sequences or repeated events. The scheduling step lets the current terminal input callback finish before `ctx.ui.custom()` mounts the overlay. Scheduling does not solve terminal-level conflicts; it only makes the application-level mount sequence less fragile.

## Handling mount-window input

A modal may be opened by a shortcut and then receive another key immediately. For a command palette, this enables fast sequences such as `Ctrl+Shift+Alt+N` followed by a menu key. But the second input can arrive before the overlay is focused. The production command palette handles this with a small mount-window buffer.

```ts
if (paletteOpenScheduled || (paletteOpen && !paletteInputReady)) {
  if (shouldReplayOpeningInput(data)) {
    pendingOpeningInputs.push(data);
  }
  return { consume: true };
}
```

The replay policy should be conservative. Replay printable characters and simple navigation keys. Do not replay arbitrary CSI-u key release events. Key release sequences can parse as semantic keys and cause immediate close behavior that the user did not intend.

## Diagnostic decision tree

Use this sequence when debugging a modal shortcut.

```text
1. Does the extension load and does a slash command run?
2. Does ctx.ui.notify() display status output?
3. Does /modal-lab overlay render the component?
4. Does /modal-lab scheduled render after an event-loop delay?
5. Does pi.registerShortcut() open the modal for a known safe key?
6. Does the raw terminal listener receive the intended key?
7. Does matchesKey(data, shortcut) return true?
8. Does the scheduled open fire?
9. Does ctx.ui.custom() call the component factory?
10. Does onHandle focus the overlay?
11. Does render(width) run and return visible rows?
12. Does a later input immediately close or overwrite the overlay?
```

This ordering prevents conflating unrelated problems. The point is not to collect more logs; the point is to localize the failure to the first layer where expected evidence disappears.

## Recommended implementation sequence

1. Implement the modal component and open it from a slash command.
2. Add overlay options and focus the overlay in `onHandle`.
3. Add a debug log that records command entry, factory creation, handle focus, render count, input count, and close result.
4. Add a high-level `pi.registerShortcut()` shortcut for a known safe key.
5. Add a raw terminal listener only if the shortcut must be global or pre-editor.
6. Schedule raw opens with `setImmediate()` and guard against duplicate opens.
7. Add narrow mount-window buffering if fast follow-up input matters.
8. Test the physical terminal path with a raw-mode key probe in the same Kitty/tmux session.
9. Avoid terminal-reserved defaults; provide environment overrides for local preference.

## Working rules

- Always provide a slash-command fallback for keyboard-only UI.
- Never assume a terminal forwards every modified key to the application.
- Treat terminal shortcut tables as part of application UX design.
- Use Pi TUI’s parser in diagnostics so the probe agrees with production behavior.
- Distinguish key press, key repeat, and key release when Kitty keyboard protocol is active.
- Focus the overlay before expecting `handleInput()` to receive user input.
- Log render calls, not only open requests.
- Keep raw listeners narrow and unsubscribe during session shutdown.

## Important source locations

- Source repo: `/home/manuel/code/wesen/2026-04-21--pi-extensions`
- Modal lab extension: `extensions/modal-shortcut-lab/index.ts`
- Modal lab README: `extensions/modal-shortcut-lab/README.md`
- Production command palette shortcut path: `extensions/command-palette/index.ts`
- Production command palette overlay component: `extensions/_shared/ui/command-palette.ts`
- Raw key probe: `ttmp/2026/05/27/MODAL-SHORTCUT-LAB--minimal-pi-shortcut-modal-lab-for-debugging-terminal-overlay-opening/scripts/03-terminal-key-probe.mjs`
- Safe shortcut smoke test: `ttmp/2026/05/27/MODAL-SHORTCUT-LAB--minimal-pi-shortcut-modal-lab-for-debugging-terminal-overlay-opening/scripts/04-smoke-tmux-safe-shortcuts.sh`

## Related notes

- [[ARTICLE - Pi Agent Command Palette Extension Architecture - Shared Registry and Keyboard-Driven Actions]]

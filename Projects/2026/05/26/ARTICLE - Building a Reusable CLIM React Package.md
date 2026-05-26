---
title: "Building a Reusable CLIM React Package: Cross-Pollinating UX from a Production Viewer into a Standalone Library"
aliases:
  - PBUI CLIM Package Deep Dive
  - go-go-golems/pbui Technical Report
tags:
  - article
  - pbui
  - clim
  - react
  - tailwind
  - typescript
  - redux
  - architecture
  - go-go-golems
status: active
type: article
created: 2026-05-26
repo: /home/manuel/workspaces/2026-05-19/dmeta-dsl/dmeta
---

# Building a Reusable CLIM React Package: Cross-Pollinating UX from a Production Viewer into a Standalone Library

This article documents the design, implementation, and extraction of `@go-go-golems/pbui`, a Presentation-Based User Interface (PBUI) framework for React that implements the Command Line Interface Model (CLIM) pattern. The work proceeded in two phases: first, identifying and porting UX interaction patterns from a production Readwise Viewer (written with mutable DOM globals) into a Deli ordering proof-of-concept (written in React with Redux); second, extracting the domain-agnostic layer into a standalone npm package with proper Tailwind v4 integration.

The target audience is someone building keyboard-first, command-driven UIs in React who needs to understand why certain architectural decisions — discriminated unions for interaction state, semantic action intents, and source-level Tailwind distribution — produce a framework that avoids whole categories of bugs while remaining customizable.

> [!summary]
> - A CLIM interface has three interaction modes — normal, select, and confirm — and representing these as a discriminated union eliminates impossible states at the type level.
> - Every action carries semantic intents (navigate, mutate, dangerous, confirm) derived from its specification, and these intents drive visual rendering, confirmation gates, and context-sensitive hints without per-component logic.
> - Extracting a Tailwind-based component library into an npm package requires shipping uncompiled source files and consumers must add `@source` directives — Tailwind v4 does not scan `node_modules` by default and the generated CSS will be silently incomplete without it.

## Why this article exists

The Deli PBUI React proof-of-concept had a working CLIM shell, action engine, and command parser, but it was a single monolithic application. The generic layer (`src/generic/clim/`) and the domain layer (`src/domain/deli/`) lived in the same Vite project with relative imports between them. Meanwhile, a production Readwise Viewer — built without React — had accumulated years of UX polish: right-click context menus, action intents that drove visual styling, prefix commands for filtering, and a discriminated mode system that prevented invalid state combinations.

The question was whether these patterns could be ported into React idioms and then extracted into a reusable package. This article records what was ported, what was redesigned, what broke during extraction, and what the resulting package looks like.

## When to use this pattern

Use the CLIM pattern (and this package) when:

- You are building a keyboard-first application where users type commands and click presentation references to fill action arguments
- Your application has distinct interaction modes (browsing, selecting an argument, confirming a dangerous action) that need strict state management
- You want a generic framework that multiple domain applications can consume without duplicating shell, command line, and action engine logic

Do not use this pattern when:

- You need a standard point-and-click form UI — the command-driven model adds complexity without benefit
- Your application has no concept of typed actions with ref/value arguments
- You need server-side rendering — the current implementation is client-only React

## The starting point: two codebases, one pattern

The Readwise Viewer is a browser application written in vanilla TypeScript with mutable DOM globals for state. It renders a CLIM interface for browsing and managing Readwise highlights. Its key architectural elements:

- A `mode` variable (normal, select, confirm) stored as a plain string, checked in render functions
- Action functions that inspect the current mode and available selections to decide what to render
- A command parser that recognizes action commands, prefix commands, and meta commands (ESC, YES)
- Context menus positioned at mouse event coordinates using `position: absolute`
- Action intents (dangerous, confirm, navigate) computed inline during rendering

The Deli PBUI React PoC is a Vite + React + Redux Toolkit application that implements the same CLIM pattern for a Hudson Street Deli ordering system. Before this work, it had:

- A `PbuiShell` component with header, main content area, and command line
- An `ActionSpec` type defining actions with id, label, views, args, and a `run` function
- A `PresentationRef` type for clickable references to domain objects
- A `pbuiSessionSlice` Redux slice with scattered mode fields: `mode`, `pendingActionId`, `pendingRequest`, `filledArgs`
- A `commandParser` that recognized only action commands and meta commands
- No context menu, no hint bar, no confirm modal, no prefix commands, no action intents

The gap between the two was substantial. The Readwise Viewer had years of UX refinement that the PoC lacked. The goal was to close that gap while keeping the PoC's cleaner type system and React idioms.

## Core mental model: the discriminated interaction state

The most consequential design decision in this work was replacing the scattered mode fields with a discriminated union. Understanding why this matters requires seeing the problem it solves.

### The problem with scattered mode fields

The original session state stored the current interaction mode as separate fields:

```typescript
interface PbuiSessionState {
  mode: 'normal' | 'select' | 'confirm';
  pendingActionId?: string;
  pendingRequest?: ActionRequest;
  filledArgs?: Record<string, unknown>;
}
```

This structure can represent states that should never exist. Nothing prevents `mode` from being `'select'` while `pendingActionId` is undefined, or `mode` from being `'confirm'` while `filledArgs` is empty. The render logic has to guard against these impossible states at every point of use:

```typescript
// Every consumer needs this kind of guard
if (state.mode === 'select' && state.pendingActionId) {
  const action = actions[state.pendingActionId];
  // ...
}
```

The guards accumulate. The action controller, the shell, the workbench, the view components — each one checks mode and then checks whether the associated data exists. Miss one guard and you get a runtime error or, worse, silently wrong behavior.

### The discriminated union solution

The redesigned state uses a single `interaction` field whose `kind` property determines what data is available:

```typescript
type PbuiInteractionState =
  | { kind: 'normal' }
  | { kind: 'select'; action: ActionSpec; filledArgs: Record<string, unknown> }
  | { kind: 'confirm'; action: ActionSpec; request: ActionRequest; filledArgs: Record<string, unknown> }
```

When `kind` is `'normal'`, there is no action, no request, no filled args. When `kind` is `'select'`, the action and filled args exist and are non-optional. TypeScript enforces this at compile time through narrowing:

```typescript
if (interaction.kind === 'select') {
  // interaction.action is ActionSpec — no undefined check needed
  // interaction.filledArgs is Record<string, unknown> — no undefined check needed
}
```

The impossible states are not just unlikely — they are unrepresentable. The type system prevents them from being constructed in the first place.

### What this changes in the Redux slice

The session slice was refactored from mode-scattered actions (`setMode`, `setPendingActionId`, `setPendingRequest`, `setFilledArgs`) to transition actions (`enterSelect`, `selectCompleted`, `enterConfirm`, `confirmCompleted`, `selectCancelled`, `confirmCancelled`). Each transition action replaces the entire `interaction` field:

```typescript
enterSelect: (state, action: PayloadAction<{ action: ActionSpec; filledArgs: Record<string, unknown> }>) => {
  state.interaction = { kind: 'select', ...action.payload };
},
selectCompleted: (state) => {
  state.interaction = { kind: 'normal' };
},
```

There is no way to enter select mode without providing an action. There is no way to be in confirm mode without a request. The transitions are atomic — they replace the whole state, not individual fields.

### The shell-facing view model

The `PbuiShell` component does not consume `PbuiInteractionState` directly. Instead, it receives a `ClimSessionState` view model that the workbench constructs from the interaction:

```typescript
interface ClimSessionState {
  mode: 'normal' | 'select' | 'confirm';
  modeLabel: string;
  commandBuffer: string;
  resultLine: string;
  commandHint?: string;
}
```

This separation exists because the shell is a generic layout component. It does not need to know about `ActionSpec` or `ActionRequest` — it only needs to know which mode label to display, what hint text to show, and whether to render the confirm modal or context menu overlay. The workbench translates between the rich interaction state and this flat view model.

## Action intents: semantic meaning drives rendering

In the original PoC, an action was either available or not. The action bar rendered all enabled actions with the same visual treatment. The Readwise Viewer had a richer model: some actions were dangerous (placing an order), some required confirmation (deleting an item), some were navigational (going back), and these semantic distinctions drove different visual presentations.

### The intent system

Each `ActionSpec` now produces a list of `ActionIntent` values through the `actionIntents()` function:

```typescript
type ActionIntent =
  | 'navigate'    // changes the current view (BACK, CART, HELP)
  | 'inspect'     // opens a detail view (CUSTOMIZE)
  | 'filter'      // filters the current view (FILTER-DIETARY)
  | 'mutate'      // modifies domain state (REMOVE-INGREDIENT, ADD-TO-ORDER)
  | 'dangerous'   // has irreversible effects (PLACE-ORDER)
  | 'external'    // interacts with the system clipboard (COPY)
  | 'confirm'     // triggers the confirmation modal
  | 'cancel'      // dismisses the current interaction (ESC, CANCEL);
```

The `actionIntents()` function derives these from the action's properties:

```typescript
function actionIntents(action: ActionSpec): ActionIntent[] {
  const intents: ActionIntent[] = [];
  if (action.requiresConfirmation) intents.push('dangerous', 'confirm');
  if (action.views.length > 0) intents.push('navigate');
  if (action.args.some(a => a.kind === 'ref')) intents.push('inspect');
  if (action.args.some(a => a.kind === 'value')) intents.push('filter');
  // mutate, cancel detected by convention
  return intents;
}
```

This derivation is deterministic. The same action always produces the same intents. There is no runtime state involved — intents are a pure function of the action specification.

### How intents drive the UI

Intents flow into `ActionPresentation` objects that components consume:

```typescript
interface ActionPresentation {
  action: ActionSpec;
  commandLabel: string;
  intents: ActionIntent[];
  requiresConfirmation: boolean;
  disabledReason?: string;
  applicableToSelected?: boolean;
}
```

The `PbuiAction` component renders actions differently based on their intents. Actions with the `dangerous` intent get red text and a confirm gate. Actions with the `cancel` intent get muted styling. The `PbuiHintBar` shows only actions whose intents include `inspect` or `filter` when a presentation is selected. The `PbuiContextMenu` renders all compatible actions but visually distinguishes dangerous ones.

The key insight is that no component needs to know the specific action ID. A future domain application can define entirely new actions, and as long as the intents are correct, the generic components will render them appropriately.

### The confirm gate

Actions with the `dangerous` and `confirm` intents trigger a modal overlay before execution. The workbench detects these intents when the user submits a command and transitions to the confirm interaction state:

```typescript
if (intents.includes('confirm')) {
  dispatch(pbuiSessionActions.enterConfirm({ action, request, filledArgs }));
}
```

The `PbuiConfirmModal` renders the action label, a CONFIRM button, and a CANCEL button. The user can confirm by clicking CONFIRM, pressing Enter, or typing YES. They can cancel by clicking CANCEL, pressing Escape, or typing ESC. This three-way input path (click, keyboard shortcut, typed command) is a direct port from the Readwise Viewer's confirm behavior.

## New components ported from the Readwise Viewer

Four new components were added to the generic CLIM layer, each implementing a UX pattern observed in the Readwise Viewer but redesigned for React.

### PbuiContextMenu

The Readwise Viewer renders a context menu by creating a DOM element with `position: absolute` at the mouse event coordinates. The React version uses `position: fixed` and accepts x/y coordinates from the `onContextMenu` event. The menu renders a list of `ActionPresentation` objects that are compatible with the right-clicked `PresentationRef`.

Keyboard accessibility was added during a later polish pass: Up/Down arrow keys cycle focus through enabled actions, Enter selects the focused action, and Escape dismisses the menu. Disabled actions are rendered but skipped during keyboard navigation — this keeps the visual layout stable while preventing the user from selecting an unavailable action.

The context menu state lives in the Redux session slice as `ContextMenuState`:

```typescript
interface ContextMenuState {
  visible: boolean;
  x: number;
  y: number;
  ref?: PresentationRef;
  actions: ActionPresentation[];
}
```

The workbench computes the context menu actions by filtering all visible actions against the right-clicked presentation's type and capabilities.

### PbuiHintBar

When the user selects a presentation (clicking a menu item, an ingredient, a cart entry), the hint bar appears below the main content showing which actions are compatible with that selection. This replaces the Readwise Viewer's inline "you can X, Y, Z this item" text.

The hint bar receives the selected `PresentationRef` and a filtered list of `ActionPresentation` objects. Each action is rendered as a clickable label. Clicking an action in the hint bar invokes it directly — if the action requires additional arguments, the interaction transitions to select mode; if the action requires confirmation, the confirm modal appears.

### PbuiConfirmModal

The Readwise Viewer uses inline confirmation prompts. The React version uses a fixed-position overlay modal that covers the entire shell. This design choice prevents the user from interacting with other elements while a dangerous action is pending confirmation.

The modal accepts the pending `ActionSpec` and a `PresentationRef` (for display). It handles three input methods: click CONFIRM/CANCEL buttons, press Enter/Escape keys, or type YES/ESC in the command line. All three paths converge on the same `onConfirm` or `onCancel` callbacks.

### PbuiHelpView

The help view renders two sections: a list of all available actions (grouped by intent) and a reference of registered prefix commands. It consumes the `actionPresentationsForSpecs()` function from the action engine and `getPrefixCommandHelp()` from the command parser.

The domain-specific `DeliHelpView` delegates entirely to the generic `PbuiHelpView`, passing the deli action registry and prefix commands. This delegation pattern means the generic help view works for any domain without modification.

## Prefix commands: SEARCH, CATEGORY, DIET

The Readwise Viewer supports prefix commands — commands that take a single string argument and perform a non-action operation like filtering the view. The command parser was extended to recognize these:

```typescript
type CommandParseResult =
  | { kind: 'empty'; original: string }
  | { kind: 'confirm'; original: string }
  | { kind: 'cancel'; original: string }
  | { kind: 'action'; commandId: string; args: string[]; original: string }
  | { kind: 'prefix'; prefix: string; value: string; original: string }
  | { kind: 'missing-argument'; prefix: string; original: string }
```

Prefix commands are registered globally via `registerPrefixCommands()`. The Deli domain registers three:

| Command | With argument | Without argument |
|---------|--------------|-----------------|
| `SEARCH hudson` | Filters menu items matching "hudson" | Clears the search filter |
| `CATEGORY sandwich` | Filters menu items with category "sandwich" | Clears the category filter |
| `DIET gluten-free` | Filters menu items tagged "gluten-free" | Clears the diet filter |

The "without argument clears the filter" convention was chosen because it mirrors the natural mental model: typing `SEARCH` alone means "stop searching."

Multiple filters compose with AND logic. If SEARCH and CATEGORY are both active, only items matching both criteria appear. The workbench computes `filteredMenu` by chaining all active filter predicates over the full menu. The `selectedItem` is always looked up from the full menu, not the filtered one — this means the selected item persists even when filtered out of the visible list.

Active filters are displayed as red-bordered badges in the view header (e.g., "SEARCH: hudson", "CATEGORY: salad"), giving the user constant awareness of what constraints are applied.

## Extracting the package: from inline generic layer to @go-go-golems/pbui

After implementing all cross-pollinated features, the generic CLIM layer lived at `src/generic/clim/` within the Deli PoC application. It had zero outbound imports from the domain layer — every import was either from React, Redux Toolkit, or from other files within `src/generic/clim/`. This self-containment made it a candidate for extraction.

### Package structure

The package was created at `dmeta/packages/pbui/` following the conventions established in the go-go-os-frontend monorepo:

```
packages/pbui/
├── package.json
├── tsconfig.json
├── README.md
└── src/
    ├── index.ts              # barrel: re-exports all public API
    ├── types.ts              # core types
    ├── actionEngine.ts       # action intents, presentations, compatibility
    ├── actionStatus.ts       # formatInteractionStatus
    ├── commandParser.ts       # parseCommandLine, prefix command registry
    ├── routing.ts            # route codec, navigation helpers
    ├── pbuiSessionSlice.ts   # RTK session slice
    ├── css.d.ts              # CSS module declaration
    ├── theme/
    │   ├── index.ts          # import entry
    │   └── clim-tokens.css   # [data-widget="clim"] scoped tokens
    └── components/
        ├── PbuiAction/
        ├── PbuiActionBar/
        ├── PbuiClickableText/
        ├── PbuiCommandLine/
        ├── PbuiConfirmModal/
        ├── PbuiConfirmPrompt/
        ├── PbuiContextMenu/
        ├── PbuiHelpView/
        ├── PbuiHintBar/
        ├── PbuiPresentationRef/
        ├── PbuiSectionLabel/
        ├── PbuiShell/
        └── PbuiText/
```

Each component directory contains the component `.tsx`, a `types.ts` (where applicable), and an `index.ts` barrel that re-exports the component and its types.

### The package.json

The package follows the go-go-golems convention: `peerDependencies` for React, Redux Toolkit, and React-Redux (the consumer provides these); `files: ["src", "README.md"]` to ship uncompiled source for Tailwind scanning; sub-path `exports` for tree-shakeable imports.

```json
{
  "name": "@go-go-golems/pbui",
  "peerDependencies": {
    "@reduxjs/toolkit": "^2.0.0",
    "react": "^18 || ^19",
    "react-dom": "^18 || ^19",
    "react-redux": "^9.0.0"
  },
  "files": ["src", "README.md"],
  "exports": {
    ".": "./src/index.ts",
    "./theme": "./src/theme/index.ts",
    "./action-engine": "./src/actionEngine.ts",
    "./command-parser": "./src/commandParser.ts"
  }
}
```

### What changed during extraction

The component source files needed zero modifications. All internal imports (`../../types`, `../PbuiAction`) resolve identically in the new location because the directory structure was preserved. The only changes were at the integration boundary:

1. The PoC's 30+ relative imports (`../../generic/clim/types`) were replaced with package imports (`@go-go-golems/pbui`)
2. Multiple import lines from the same package were consolidated into single statements
3. The barrel `index.ts` was audited to ensure every type and function the PoC consumed was exported

The barrel audit revealed several missing exports: `actionAcceptsRef`, `canFillRefArg`, `canFillValueArg`, `nextOpenArg`, and `presentationVisualState` from the action engine, and `PrefixCommandHelp` from the command parser (it was exported from `commandParser.ts` but not from the package barrel). These were functions the PoC used but that had not been needed when everything was in the same project.

### The pnpm workspace

A `pnpm-workspace.yaml` was created at the `dmeta/` level to link the package and the PoC:

```yaml
packages:
  - "packages/*"
  - "proof-of-concept/*"
```

The PoC's `package.json` depends on the package via `workspace:*`:

```json
{
  "dependencies": {
    "@go-go-golems/pbui": "workspace:*"
  }
}
```

pnpm resolves `workspace:*` to the local package directory, creating a symlink in `node_modules/@go-go-golems/pbui` that points back to `packages/pbui/`.

## The Tailwind v4 integration problem

The package extraction exposed a critical issue with Tailwind CSS v4's content scanning. Understanding this problem and its solution is essential for anyone building Tailwind-based component libraries.

### What happened

After extraction, the Deli PoC's CSS completely broke. The layout collapsed: buttons had no padding, the grid layout disappeared, colors reverted to defaults, and the action bar buttons rendered as a single jammed-together string of text. The class names were present in the HTML — React had rendered them correctly — but the corresponding CSS rules did not exist in the generated stylesheet.

### Why it happened

Tailwind v4 generates CSS by scanning source files for class names, then producing only the rules for classes it finds. This is the core performance optimization: the generated CSS contains only what the application uses.

By default, Tailwind v4 scans every file in the project **except**:

- Files listed in `.gitignore`
- Files in `node_modules/`
- Binary files (images, videos, archives)
- CSS files
- Lock files

Before extraction, the CLIM components lived at `src/generic/clim/components/`, which is inside the project and not ignored. Tailwind scanned these files, found class names like `flex`, `gap-2`, `px-3`, `py-2`, and generated the corresponding CSS rules.

After extraction, the components lived in `packages/pbui/src/components/`, which is outside the PoC project. Tailwind's auto-detection did not scan that directory. The class names were still in the rendered HTML (because React imported the components from the package), but the CSS rules were never generated.

### The solution: @source directive

Tailwind v4 provides the `@source` directive to explicitly register additional scan paths:

```css
/* In the consumer's main CSS file (e.g. src/index.css) */
@import "tailwindcss";

/* Scan the package source for Tailwind class names */
@source "../node_modules/@go-go-golems/pbui/src";
```

The `@source` path is **relative to the CSS file**, not the project root. If the CSS file is at `src/index.css`, then `../node_modules/` goes up one level from `src/` to the project root and then into `node_modules/`.

### What went wrong during debugging

Three separate attempts were needed to get the `@source` path right:

1. **First attempt:** `@source "../../node_modules/@go-go-golems/pbui/src/**/*.tsx"` — two levels up from `src/` instead of one. This pointed past the project root into the parent directory. The path resolved to nothing.

2. **Second attempt:** `@source "../../../packages/pbui/src"` — the real filesystem path through the workspace. This worked because pnpm's `workspace:*` creates a symlink that resolves back to the actual package directory. However, this path is fragile: it only works in workspace mode and would break when the package is installed from npm.

3. **Final working solution:** `@source "../node_modules/@go-go-golems/pbui/src"` — one level up from `src/` into the project's `node_modules/`. This path works both in workspace mode (pnpm creates a symlink there) and when the package is installed from npm (the files are physically present). Tailwind v4 follows the symlink to the real source directory and scans it.

The key debugging technique was using `getComputedStyle()` in the browser console to check whether specific Tailwind classes had generated CSS rules. Classes like `flex` and `text-clim-bright` worked (they were used in the PoC's own source files), while `gap-2` and `grid-rows-[auto_1fr_auto]` did not (they only appeared in the package components). This confirmed the issue was specifically about the package source not being scanned.

### The `files` field requirement

The `@source` directive can only scan files that exist in the installed package. The package's `files` field in `package.json` must include `src/`:

```json
{
  "files": ["src", "README.md"]
}
```

Without `src/` in the `files` array, npm would publish only the compiled output, and `@source` would have no `.tsx` files to scan.

### Documented consumer setup

The package README documents the setup in two lines:

```css
@import "tailwindcss";
@source "../node_modules/@go-go-golems/pbui/src";
```

And includes a warning:

> Without the `@source` directive, Tailwind v4 will not generate CSS for the utility classes used by the package components, and spacing/layout will break.

This is the single most important integration instruction. Every consumer must follow it. The failure mode is silent — no error, no warning, just missing CSS rules.

## Results

The session produced a complete, working package from analysis through extraction. The numbers:

| Metric | Value |
|--------|-------|
| Cross-pollinated features | 8 of 10 (2 skipped: pagination, build freshness) |
| New types | `ActionIntent`, `PbuiInteractionState`, `ContextMenuState`, `PrefixCommandHelp` |
| New components | 4 (`PbuiContextMenu`, `PbuiHintBar`, `PbuiConfirmModal`, `PbuiHelpView`) |
| Updated components | 6 (`PbuiShell`, `PbuiCommandLine`, `PbuiActionBar`, `PbuiPresentationRef`, `PbuiAction`, `PbuiPresentationRef`) |
| New domain features | Prefix commands (SEARCH/CATEGORY/DIET), COPY action, filter badges |
| Package source files | 43 (1,506 lines of TypeScript/TSX) |
| Commits | 20 |
| TypeScript compilation errors in final state | 0 |
| Console errors in browser | 0 |

The package is consumed by the Deli PoC via `workspace:*` and renders identically to the pre-extraction state.

## Remaining type-safety gaps

The current package has two type-safety gaps that were accepted for the proof-of-concept but should be addressed before broader use.

### ActionSpec widening

The generic layer defines `ActionSpec<string>`, but the domain layer uses `ActionSpec<DeliCommandId>` where `DeliCommandId` is a union of literal strings (`'CUSTOMIZE' | 'BACK' | 'CART' | ...`). When the workbench passes an action from the interaction state to a domain function, TypeScript widens the type:

```typescript
// interaction.action is ActionSpec<string> (from the generic slice)
// but DeliDetailView expects ActionSpec<DeliCommandId>
const detailView = <DeliDetailView action={interaction.action as ActionSpec<DeliCommandId>} />;
```

The cast is safe by construction (only `DeliCommandId` actions are registered) but the type system cannot verify this. The fix would be to make `PbuiShellProps` and `PbuiInteractionState` generic on the action type parameter.

### Mutable prefix command registry

Prefix commands are registered through a module-level mutable array:

```typescript
let prefixCommandRegistry: PrefixCommandHelp[] = [];
export function registerPrefixCommands(commands: PrefixCommandHelp[]) {
  prefixCommandRegistry = commands;
}
```

This works for a single-domain application but creates shared state across test environments. A future improvement would use React context or an explicit registry passed through props.

## Common failure modes

### The silent Tailwind @source failure

This is the most dangerous failure mode because it produces no error message. The symptoms are: class names appear in the HTML, but the rendered layout has no spacing, no colors, no grid structure. The fix is always to check the `@source` directive in the consumer's CSS file.

### Accidentally deleting declarations during edits

When inserting code before a `const` declaration, the edit tool can accidentally consume the declaration line. This happened three times during the session with `const interaction = session.interaction;`. The fix is to always include the target line in the replacement text.

### RTK serializable check for function-valued fields

`ActionSpec` objects contain `accepts` functions (predicates for determining which presentations an action can receive). When these objects are stored in Redux state, RTK's `serializableCheck` middleware emits warnings. The fix is to add the specific paths and actions to the `ignoredPaths` and `ignoredActions` configuration:

```typescript
middleware: (getDefaultMiddleware) => getDefaultMiddleware({
  serializableCheck: {
    ignoredPaths: ['pbuiSession.interaction.action.args'],
    ignoredActions: ['pbuiSession/enterSelect', 'pbuiSession/enterConfirm'],
  },
})
```

## Working rules

1. **Never represent interaction modes as scattered fields.** Use a discriminated union with `kind` as the discriminant. Every transition replaces the entire state, not individual fields.

2. **Derive visual rendering from semantic intents, not action IDs.** New actions should render correctly in the existing components as long as their intents are accurate.

3. **Ship source files in Tailwind-based packages.** The `files` field must include `src/` so consumers can point `@source` at the uncompiled component files.

4. **Document the `@source` requirement prominently.** The failure is silent and the fix is two lines. Every consumer will hit this.

5. **Keep the shell-facing API flat.** `ClimSessionState` is a view model with no generic type parameters. The workbench translates between the rich interaction state and this flat model. This keeps the shell simple and reusable.

6. **Test the @source path from the CSS file's location.** The path is relative to the CSS file, not the project root. Count the directory levels carefully.

## Near-term next steps

- Add unit tests for the action engine and command parser pure functions (these have zero dependencies and are straightforward to test)
- Add ARIA roles to the context menu (`role="menu"`, `role="menuitem"`) and confirm modal (`role="dialog"`)
- Make `PbuiShellProps` generic on the action type to eliminate `as ActionSpec<DeliCommandId>` casts
- Build a second CLIM application (e.g., a Readwise Viewer rewrite) to validate the package's reusability
- Consider adding a pre-built CSS mode for consumers who do not use Tailwind

## Related notes

- Ticket: `DMETA-PBUI-RW-CROSSPOLL` in the dmeta-dsl workspace
- Design doc: `design-doc/01-clim-ux-cross-pollination-analysis-readwise-viewer-deli-pbui-react.md`
- Package: `/home/manuel/workspaces/2026-05-19/dmeta-dsl/dmeta/packages/pbui/`
- PoC app: `/home/manuel/workspaces/2026-05-19/dmeta-dsl/dmeta/proof-of-concept/deli-pbui-react/`
- Tailwind research: `design-doc/02-tailwind-library-packaging-research.md`

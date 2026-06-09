---
title: "Palette Theming for Context Diagrams and Transcripts"
aliases:
  - "Configurable Style Sets for Context Window Diagrams"
tags:
  - article
  - theming
  - frontend
  - context-window
  - visualization
  - storybook
status: active
type: article
created: 2026-06-09
repo: /home/manuel/workspaces/2026-06-07/club-meetup-site/2026-05-27--rag-evaluation-system
---

# Palette Theming for Context Diagrams and Transcripts

This note captures a complete implementation of a configurable palette and style-set system for context window visualization — covering context diagrams, transcript cards, annotation side-notes, and inline note-link chips. The system replaces hardcoded `ContextPartKind` visual keys with a caller-defined `ContextStyleSet` that separates data segments, legend labels, and visual styles into three independent concerns.

> [!summary]
> 1. **The old system** tied every context-window part to a hardcoded `kind` enum that served as semantic category, style key, legend label, and CSS class suffix all at once.
> 2. **The new system** uses `styleKey: string` for data segments, a `ContextStyleSet` with `styles` and `legend` for visual configuration, and CSS variables (`--ctx-fill`, `--ctx-line`, `--ctx-stroke`, `--ctx-label`) for rendering.
> 3. **The same visual grammar** — halftone patterns, CSS-variable tones, palette controls — applies to context diagrams, transcript message cards, annotation note cards, and inline note-link chips.

## Why This Note Exists

The context diagram palette theming task (ticket `CTX-COLOR-PALETTE`) started as a narrow visual request: "we need more than just blue" and "use these four macOS color palettes." It quickly expanded into a deeper architectural shift — from a hardcoded visual taxonomy to a fully caller-configurable style system. This note captures the full implementation journey, the design decisions made along the way, and the concrete patterns that emerged.

The system serves two products: the RAG evaluation site (`2026-05-27--rag-evaluation-system/`) and the ClubMed Meetup course app (`ClubMedMeetup/minitrace-viz/`). Both consumers share the same `ContextStyleSet` contract through Widget IR and direct React rendering.

## Core Mental Model

The old architecture collapsed four roles into a single concept — `ContextPartKind`. A kind value like `"system"` was simultaneously:

- **Semantic data**: the actual category of a context-window segment.
- **Visual style key**: the lookup key for CSS class `.kind_system`.
- **Legend label**: the text shown in the legend ("system / instructions").
- **CSS class suffix**: the deterministic suffix for pattern rules.

The new architecture splits these into three independent layers:

1. **Data segments** — `ContextWindowPart.styleKey: string`. Any string value. No enum.
2. **Legend** — `ContextStyleSet.legend: ContextLegendItemSpec[]`. Caller-defined label text, hidden entries, ordering.
3. **Visual styles** — `ContextStyleSet.styles: Record<string, ContextVisualStyle>`. Each `styleKey` maps to a visual style with `fill`, `line`, `stroke`, `labelColor`, `pattern`, and CSS-variable output.

The relationship is simple: a snapshot's parts carry `styleKey` values, the component receives a `ContextStyleSet`, and `resolveContextVisualStyle(styleKey, styleSet)` returns the `ContextVisualStyle` for rendering.

```typescript
// Old: kind does everything
{ kind: 'system', tokens: 7200 }
// .kind_system { fill: #...; }

// New: three independent layers
{ styleKey: 'system', tokens: 7200 }
styleSet.styles['system'] = { pattern: 'checker', fill: mix(#a, 20%, paper), line: mix(#a, 100%, paper), ... }
styleSet.legend = [{ id: 'system', label: 'system / instructions' }]
```

## The Visual Style Model

Every visual style is defined by `ContextVisualStyle`:

```typescript
interface ContextVisualStyle {
  fill: string;        // Background tint behind halftone pattern
  line?: string;       // Color of pattern marks (checker lines, stipple dots)
  stroke?: string;     // Solid stroke/outlines
  labelColor?: string; // Text color on top of fill (for readable labels on palette color)
  pattern?: ContextPatternName; // none | solid | checker | diagonal | diagonalDense | stipple | cross | overflow
  dashed?: boolean;
  dotted?: boolean;
  strokeWidth?: number;
  vars?: Record<string, string>; // Extra CSS variables the consumer should apply
}
```

The critical field for the palette theming use case is `labelColor`. Without it, palette-colored backgrounds would make small text like "100 tok" or "note 5" unreadable. The `labelColor` field provides the explicit foreground for each palette entry, resolved as the CSS variable `--ctx-label`.

## Palette-to-Style-Set Construction

The system does not store raw palette colors in the `ContextStyleSet`. Instead, it converts imported palette definitions (four preferred palettes from the macOS palette JSON) into complete style sets via `createContextStyleSetFromPalette()`.

The conversion function takes an array of entry specs and produces both the `styles` map and the `legend`:

```typescript
// Entry spec: the caller specifies the semantic mapping
{ id: 'system', label: 'system / instructions', accent: 'b', pattern: 'checker', fillPct: 20, linePct: 100 }

// Produces:
styles['system'] = {
  pattern: 'checker',
  fill: 'color-mix(in srgb, #4F74A8 20%, #F2EEF2)',  // accent_b at 20% paper
  line: 'color-mix(in srgb, #4F74A8 100%, #F2EEF2)', // accent_b at 100% paper
  stroke: '#141214',
  labelColor: '#141214',
}
legend = [{ id: 'system', label: 'system / instructions' }]
```

The `accent` field maps to palette colors (`accent_a`, `accent_b`, `accent_c`, `grid`, `shadow`, `ink`), allowing callers to choose which palette color drives the style. The `fillPct` and `linePct` control opacity for the halftone tint and pattern lines respectively. `solid: true` produces a solid fill with transparent pattern lines.

Four style set presets are exported:

| Preset | Palette | Use |
|--------|---------|-----|
| `contextDefaultStyleSet` | Dusty Magenta / Blue (default) | Full context-window vocabulary (15 entries) |
| `contextSignalOrangeStyleSet` | Signal Orange / Cyan | Alert/selection emphasis |
| `contextSlateCoralStyleSet` | Slate / Coral | Primary/corruption distinction |
| `contextCobaltSandStyleSet` | Cobalt / Sand | Active/passive navigation |
| `transcriptDefaultStyleSet` | Dusty Magenta / Blue | Transcript role tones (10+ entries) |
| `transcriptSignalOrangeStyleSet` | Signal Orange / Cyan | Transcript palette variant |
| `transcriptSlateCoralStyleSet` | Slate / Coral | Transcript palette variant |
| `transcriptCobaltSandStyleSet` | Cobalt / Sand | Transcript palette variant |

## Generic Halftone CSS

The hard-cutover replaced `.kind_*` CSS selectors with generic `.pattern_*` classes that work with any style set. All four context diagram CSS modules and the transcript message card CSS now use the same pattern vocabulary:

```css
/* Pattern classes applied as CSS classes on container elements */
.pattern_checker {
  background-image:
    linear-gradient(45deg, color-mix(in srgb, var(--ctx-line) 45%, transparent) 25%, transparent 25%),
    linear-gradient(-45deg, color-mix(in srgb, var(--ctx-line) 45%, transparent) 25%, transparent 25%);
  background-size: 8px 8px;
}

.pattern_diagonal {
  background: repeating-linear-gradient(45deg, color-mix(in srgb, var(--ctx-line) 48%, transparent) 0 1px, transparent 1px 8px);
}

.pattern_stipple {
  background-image: radial-gradient(color-mix(in srgb, var(--ctx-line) 58%, transparent) 1px, transparent 1px);
  background-size: 6px 6px;
}

.pattern_cross {
  background:
    repeating-linear-gradient(0deg, color-mix(in srgb, var(--ctx-line) 42%, transparent) 0 1px, transparent 1px 8px),
    repeating-linear-gradient(90deg, color-mix(in srgb, var(--ctx-line) 42%, transparent) 0 1px, transparent 1px 8px);
}
```

The CSS variables `--ctx-fill`, `--ctx-line`, `--ctx-stroke`, and `--ctx-label` are set inline by React via `contextVisualStyleToCssVars(style)`. Pattern CSS uses `var(--ctx-line)` for pattern marks and the fill is set as the base `background` of the element.

## Transcript Styling: Colored Chrome, Neutral Body

Transcript message cards receive the same `ContextStyleSet` treatment as context diagrams, with an important visual rule: **palette colors live in the title/header strip, the body remains white/neutral by default.**

This rule emerged from a specific user correction: the token count chip ("100 tok") and other small labels became unreadable when the palette color bled into the body or when small text was painted with a palette line color. The solution was threefold:

1. **Title bar** gets the palette `fill`, `line`, and `--ctx-label` foreground. Pattern halftone renders as a `::before` pseudo-element overlay on the title bar only.
2. **Message body** stays on `var(--mac-surface)` (white/neutral). No palette color touches the message text.
3. **Token chips and note chips** use a mostly-white background with a palette-tinted left border. Selected chips switch to palette fill + matching label color.

```css
/* Title bar: colored chrome */
.titleBar {
  background: var(--ctx-fill, var(--mac-surface-2));
  color: var(--ctx-label, var(--mac-text));
}

.titleBar::before {
  background: repeating-linear-gradient(..., var(--ctx-line), ...);
  /* halftone pattern overlay, pointer-events: none */
}

/* Body: neutral */
.body {
  background: var(--mac-surface);
  color: var(--mac-text);
}

/* Token chip: mostly white */
.tokenChip {
  background: color-mix(in srgb, var(--mac-surface) 82%, var(--ctx-fill) 18%);
  color: var(--mac-text);
}

/* Note chip: neutral by default, palette when selected */
.noteChip {
  background: var(--mac-surface);
  color: var(--mac-text);
  border-left: 3px solid color-mix(in srgb, var(--ctx-line) 68%, var(--mac-border));
}
.noteChip[data-selected="true"] {
  background: var(--ctx-fill);
  color: var(--ctx-label);
}
```

The same colored-chrome/neutral-body rule applies to annotation note cards in the side rail: the note title bar gets palette color and halftone, the note body stays neutral, and the confidence metadata chip uses a mostly-white background.

## Widget IR and Goja DSL

The `ContextStyleSet` contract extends through Widget IR and the Goja DSL. Server-generated widgets carry the same `styleSet` object that React components consume directly.

Goja DSL helpers:

| Helper | Purpose |
|--------|---------|
| `visualStyle(options)` | Returns a `ContextVisualStyle` object |
| `legendItem(id, label, options?)` | Returns a `ContextLegendItemSpec` |
| `styleSet(options)` | Returns a complete `ContextStyleSet` |
| `contextPart(id, label, styleKey, tokens, options?)` | Returns a `ContextWindowPart` with required `styleKey` |
| `contextSnapshot(options)` | Returns a normalized snapshot with `parts` and `selectedPartId` |
| `paletteStyleSet(options)` | Returns a palette-derived `ContextStyleSet` from entry specs |

The `contextDiagram` recipe requires either an explicit `styleSet` or enough `palette` + `entries` data to construct one. If neither is provided, it throws a descriptive error. This is the hard-cutover enforcement: you cannot create a context diagram without specifying how it should be styled.

```javascript
// Goja DSL example: palette-derived style set
contextWindow.recipes.contextDiagram({
  title: "Context Window Budget",
  snapshot: contextWindow.contextSnapshot({
    title: "Current context",
    parts: [
      contextWindow.contextPart("system", "Instructions", "system", 7200),
      contextWindow.contextPart("context", "Project", "context", 4100),
      contextWindow.contextPart("active", "Current task", "active", 1400),
    ],
    limit: 128000,
  }),
  palette: "signalOrangeCyan",
  entries: [
    contextWindow.legendItem("system", "Instructions"),
    contextWindow.legendItem("context", "Project context"),
    contextWindow.legendItem("active", "Active task"),
  ],
})
```

## Storybook Palette Controls

Every context diagram and transcript story exposes a `palette` dropdown control in Storybook's Controls panel. The control maps from a simple string name (`"Dusty Magenta / Blue"`) to the full `ContextStyleSet` object at render time. This keeps the control surface simple while still allowing full palette switching.

The palette controls are applied to:

- **Context atoms**: `AnnotationBadge`, `ContextStyleSwatch`
- **Context molecules**: `ContextBudgetBar`, `ContextLegend`, `ContextStackDiagram`, `ContextStripDiagram`, `ContextTreemap`, `FigureBlock`
- **Organisms**: `ContextDiagramPanel`, `CourseSlidePanel`, `CourseStudioShell`, `SlideShell`
- **Transcript widgets**: `TranscriptMessageCard`, `TranscriptReaderPanel`, `TranscriptWorkspacePanel`, `AnnotationRailPanel`, `AnnotationNoteCard`
- **Widget IR stories**: all context diagram and transcript IR examples

A shared `storyPalettes.ts` module avoids duplicating the `Record<ContextPaletteName, ContextStyleSet>` map across story files:

```typescript
// storyPalettes.ts
export const contextPaletteStyleSets: Record<ContextPaletteName, ContextStyleSet> = {
  'Dusty Magenta / Blue': contextDefaultStyleSet,
  'Signal Orange / Cyan': contextSignalOrangeStyleSet,
  'Slate / Coral': contextSlateCoralStyleSet,
  'Cobalt / Sand': contextCobaltSandStyleSet,
};

export function contextStyleSetForPalette(palette: ContextPaletteName) {
  return contextPaletteStyleSets[palette];
}
```

For Widget IR stories, palette switching rebuilds the `WidgetNode` tree from the selected palette, proving that the full serialization/deserialization path works:

```typescript
export const ContextDiagramPanelViews: Story = {
  render: ({ palette, registry }) => renderNode(
    contextDiagramPanelViewsNode(contextStyleSetForPalette(palette)),
    registry
  ),
}
```

The stories also demonstrate **varied legend vocabularies**: not all examples use the full 15-entry context-window legend. Some stories show compact caller-defined legends with 3–6 labels, proving that the system works for any vocabulary size.

## ClubMed Consumer

The ClubMed Meetup course app (`ClubMedMeetup/minitrace-viz/`) was updated as a separate consumer audit step. Markdown slide context-window blocks, slide loader, session snapshot producer, and live LiteLLM snapshot producer all now emit `styleKey` instead of `kind`. Page composition builds a palette-derived `styleSet` via `contextWindow.paletteStyleSet(...)` and passes it to `CourseSlidePanel` and `ContextDiagramPanel`.

The embedded SPA was regenerated after the RAG package build, and stale embedded asset hashes were cleaned from the xgoja embed directory.

## Key Design Decisions

### Hard cutover, no compatibility wrappers

The decision to remove `ContextPartKind` entirely rather than preserving a compatibility layer kept the implementation clean. Both consumers (`rag-evaluation-system` and `ClubMedMeetup`) were updated in the same branch, so no migration path was needed.

### Palette and vocabulary are separate concerns

The palette controls control color and pattern tones. The style set's `legend` array controls what labels appear. A story can show the same palette colors with 3 labels or 15 labels independently. This separation proved essential in Storybook, where showing varied legend sizes made the configurability obvious.

### Label color is part of the palette contract

Every `ContextVisualStyle` carries a `labelColor` field, resolved as `--ctx-label`. This is not optional — without it, palette-colored backgrounds make small text unreadable. The implementation went through three rounds of refinement on this point: message title bars first, then token chips, then inline note-link chips.

### Colored chrome, neutral body

Transcript styling uses palette color only in title/header strips, borders, glyphs, and note chips. The message body and note body remain neutral. This prevents palette colors from making dense content noisier.

### CSS custom properties over inline styles

CSS variables (`--ctx-fill`, `--ctx-line`, etc.) enable palette switching without React re-renders. The inline `style` prop on a container sets the variables; descendant CSS consumes them via `var()`. This is the simplest mechanism that works.

## Common Failure Modes

### Palette color as text color

Using `--ctx-line` or `accent_a` directly as text color on neutral backgrounds often produces insufficient contrast, especially for small labels. The rule is: palette colors drive background fills and pattern marks; `labelColor`/`mac-text` drives text.

### Forgetting the chip distinction

Token count chips, note-link chips, and confidence chips need their own background treatment. They should not sit directly on the palette fill. The default is a mostly-white chip with a palette-tinted left border; selected state uses palette fill + label color.

### Hardcoded style keys in Widget IR

If a Widget IR story hardcodes `styleKey` values that don't exist in the story's `styleSet.styles`, `resolveContextVisualStyle` falls back to the `overflow` pattern with a console error. Always ensure snapshot `styleKey` values match legend entry IDs.

### Widget IR story arg type errors

When adding story-only args like `palette` to a Storybook meta that still declares `component`, TypeScript rejects the extra arg. The fix: remove `component` from the meta and type stories directly as `StoryObj<StoryArgs>`.

## Working Rules

1. **Every component that consumes visual styles must also consume `labelColor`** — either through `--ctx-label` or an equivalent foreground variable.
2. **Transcript message bodies stay neutral** — palette color is chrome only.
3. **Legend vocabulary and palette colors are independent** — Storybook should demonstrate different legend sizes with the same palette colors.
4. **Small metadata controls need stronger contrast than larger headers** — tokens, note links, confidence text should have neutral backgrounds even when other elements use palette fills.
5. **CSS variables over inline styles** — palette switching works best through CSS custom properties, not per-element inline color values.
6. **Hard cutover over migration** — if a consumer can be updated, remove the old API entirely rather than preserving a compatibility layer.

## Files of Interest

| File | Role |
|------|------|
| `packages/rag-evaluation-site/src/context/types.ts` | `ContextVisualStyle`, `ContextStyleSet`, `ContextLegendItemSpec`, `styleKey` types |
| `packages/rag-evaluation-site/src/context/styles.ts` | `createContextStyleSetFromPalette`, `resolveContextVisualStyle`, `contextVisualStyleToCssVars`, `transcriptStyleSet`, `defaultContextStyleSet` |
| `packages/rag-evaluation-site/src/context/fixtures.ts` | Default/preferred style set instances, transcript style set fixtures |
| `packages/rag-evaluation-site/src/context/storyPalettes.ts` | `ContextPaletteName`, `contextStyleSetForPalette`, `transcriptStyleSetForPalette` |
| `packages/rag-evaluation-site/src/components/atoms/ContextStyleSwatch/` | Generic visual-style swatch atom |
| `packages/rag-evaluation-site/src/components/molecules/ContextLegend/` | Required items+styles legend |
| `packages/rag-evaluation-site/src/components/molecules/ContextStripDiagram/` | Strip diagram with `styleSet` + CSS variable rendering |
| `packages/rag-evaluation-site/src/components/molecules/ContextStackDiagram/` | Stack diagram with `styleSet` + CSS variable rendering |
| `packages/rag-evaluation-site/src/components/molecules/ContextBudgetBar/` | Budget bar with `styleSet` + CSS variable rendering |
| `packages/rag-evaluation-site/src/components/molecules/ContextTreemap/` | Treemap with `styleSet` + CSS variable rendering |
| `packages/rag-evaluation-site/src/components/molecules/TranscriptMessageCard/` | Transcript cards with palette title chrome, neutral body, token/contrast chips |
| `packages/rag-evaluation-site/src/components/molecules/AnnotationNoteCard/` | Side-note cards with palette title chrome, neutral body, confidence chips |
| `packages/rag-evaluation-site/src/widgets/ir.ts` | Widget IR prop interfaces with required `styleSet` |
| `pkg/widgetdsl/module.go` | Goja DSL helpers: `visualStyle`, `legendItem`, `styleSet`, `paletteStyleSet` |
| `ClubMedMeetup/minitrace-viz/lib/course-pages.js` | ClubMed page composition with explicit `styleSet` |

## Screenshots

### Default Palette — Dusty Magenta / Blue

<details>
<summary>Context Diagram Panel — Widget IR with varied legend vocabularies</summary>

![](.playwright-mcp/storybook-context-diagram-panel-views.png)

The Widget IR `ContextDiagramPanelViews` story shows four different legend sizes (3, 4, 5, and 6 labels) under the same layout. The palette dropdown in Storybook Controls switches colors independently of the legend vocabulary.

</details>

<details>
<summary>Transcript Message Card States — Palette-controlled with neutral bodies</summary>

![](.playwright-mcp/storybook-message-card-states.png)

Each message card shows a palette-colored title bar with halftone pattern, a token-count chip with a mostly-white background, and a white message body. The note-link chips ("note 5", "note 4") use a neutral background with a palette left-border accent.

</details>

<details>
<summary>Transcript Action Logger — Full transcript workspace with palette control</summary>

![](.playwright-mcp/storybook-transcript-action-logger.png)

The transcript action logger Widget IR story renders a full `TranscriptWorkspacePanel` with palette controls. The palette dropdown switches between all four preferred palettes across the entire transcript surface — message title bars, note chips, and annotation rails all update.

</details>

### Signal Orange / Cyan

<details>
<summary>Transcript message cards with Signal Orange / Cyan palette</summary>

![](.playwright-mcp/sb-message-cards-orange.png)

The same message card states under the Signal Orange / Cyan palette. The assistant title bars now use cyan tones, tool call bars use orange, and the note chips have cyan borders. Token chips remain neutral-white.

</details>

### Cobalt / Sand

<details>
<summary>Context diagram panel views with Cobalt / Sand palette</summary>

![](.playwright-mcp/sb-context-diagram-cobalt.png)

The `ContextDiagramPanelViews` story under the Cobalt / Sand palette. The strip diagram, budget bar, stack diagram, and treemap all use cobalt blue for active elements and sand for passive/hovered tones.

</details>

### Slate / Coral

<details>
<summary>Transcript action logger with Slate / Coral palette</summary>

![](.playwright-mcp/sb-slate-coral-action-logger.png)

The transcript workspace under the Slate / Coral palette. The assistant bars use slate tones, tool call bars use coral, and the annotation note cards use slate-accented title bars with neutral bodies.

</details>

### Palette switching via URL

The palette can also be controlled via Storybook URL arguments rather than the Controls panel dropdown:

```
http://localhost:6007/iframe.html?id=widget-ir-renderer-transcript-and-notes--message-card-states&viewMode=story&args=palette:'Signal+Orange+/+Cyan'
```

The URL argument format uses single quotes around the palette value with `+` for spaces and `%2F` (or `/`) for the forward slash. This is useful for automated testing, screenshot generation, and sharing palette-specific preview links.

## Related Notes

- `PROJ - ClubMeetupSite` — The broader project this palette work serves
- `ARTICLE - Playbook - Self-Contained Go Wasm and JavaScript Browser Applications` — The deployment architecture that hosts both the RAG evaluation site and the ClubMed app

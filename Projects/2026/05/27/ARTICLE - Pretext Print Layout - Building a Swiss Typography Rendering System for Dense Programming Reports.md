---
title: "Pretext Print Layout — Building a Swiss Typography Rendering System for Dense Programming Reports"
aliases:
  - Pretext Print Layout
  - Pretext Swiss Typography System
  - Print Layout Design System
tags:
  - article
  - pretext
  - react
  - typescript
  - print-layout
  - swiss-typography
  - design-system
  - text-measurement
status: active
type: article
created: 2026-05-27
repo: /home/manuel/code/wesen/2026-05-27--pretext-design-system
---

# Pretext Print Layout — Building a Swiss Typography Rendering System for Dense Programming Reports

This article documents the design and implementation of a React-based print layout system that renders dense technical reports as paginated Swiss-typography HTML. The system uses Pretext — a pure JavaScript text measurement library by Cheng Lou — to measure all text without DOM reflow, a custom pagination engine to flow content blocks through fixed-size pages, and a set of typed React components that render headings, prose, code blocks, data tables, callouts, and lists with consistent typographic treatment.

The work was done in two phases. The first phase produced a working single-column renderer that parses Markdown, measures every block with Pretext, paginates the blocks into A4 pages, and renders them as styled HTML with a print stylesheet for PDF output. The second phase (design only, not yet implemented) specifies a two-column grid layout with semantic CSS custom properties and width-adaptive code blocks.

The article explains every layer of the system — input parsing, text measurement, pagination, and rendering — with concrete code, concrete measurements, and concrete bugs encountered and fixed. It is written for someone who wants to understand how the system works, why each design decision was made, and what the failure modes are.

> [!summary]
> - Pretext measures text 500–600× faster than DOM-based approaches by separating one-time font measurement from per-frame layout arithmetic. This makes it viable to measure every block in a 48KB report in under 50ms.
> - The Swiss typography system uses a strict baseline grid (6px), three typefaces (Newsreader for body, Inter for headings, JetBrains Mono for code), and all spacing derived from the baseline unit.
> - Using Pretext measurement for absolute CSS positioning does not work — the measured heights diverge from CSS rendering heights. The fix is to use Pretext only for page-break decisions and let CSS flow handle intra-page layout.
> - The two-column grid design introduces width-adaptive code blocks (measure natural line width, promote to full-width if it exceeds column width), greedy-balance pagination, and semantic CSS custom properties for all spacing tokens.

## Why this system exists

Technical project reports are a specific document genre. They combine long-form prose with code blocks, data tables, file paths, blockquotes, and section hierarchies. A typical example is the Book OCR Project Report — a 48KB Markdown file with 23 sections, Common Lisp code, Markdown tables, Mermaid diagrams, and structured metadata. Rendering this kind of document well requires typographic decisions at every level: headings must be visually distinct through size and weight, not decoration. Code blocks must use a monospace face at a size that preserves indentation without dominating the page. Tables must align columns precisely. Page breaks must not orphan headings.

The existing rendering pipeline for these reports is Pandoc → XeLaTeX → PDF. This produces adequate output but offers no fine-grained control over line breaks within code blocks, no precise table column measurement, and no deterministic page-break placement. The goal of the Pretext Print Layout system is to replace this pipeline with a React-based renderer that measures all text with Pretext and produces Swiss International Typographic Style layouts optimized for dense technical content.

Swiss typography provides the design framework. The International Typographic Style, developed in the 1950s by Max Miedinger, Josef Müller-Brockmann, and others, establishes clear principles: clarity through restrained type palettes, mathematical grid-based layout, generous white space, and visual hierarchy through size and weight contrast rather than color or decoration. These principles map well to technical documents. A code block is visually distinct from prose because it uses a different typeface at a different size with a strong left border, not because it has a colored background and rounded corners.

## The Pretext library

Pretext is a pure TypeScript text measurement library created by Cheng Lou. It provides two operations: `prepare()` and `layout()`. The `prepare()` function takes text and a font string, segments the text using the Unicode Line Breaking Algorithm (UAX #14), measures each segment's width using the browser's Canvas `measureText()` API, and returns an opaque handle. The `layout()` function takes that handle, a container width, and a line height, and computes the total height and line count using pure arithmetic over the cached segment widths. No DOM access occurs during `layout()`.

The performance numbers are instructive. For a 500-word text block:

| Operation | Time | When to call |
|-----------|------|--------------|
| `prepare()` | ~19ms | Once per content change |
| `layout()` | ~0.09ms | Every resize or width change |
| `layoutWithLines()` | ~0.12ms | Every resize, need line-by-line data |

A `prepare()` call is intentionally not free — it runs the font engine. A `layout()` call is pure arithmetic and runs in sub-microsecond time. This separation means that for a document with ~50 blocks, the one-time preparation costs roughly 1 second total, and every subsequent layout recalculation (resize, theme change, column rebalance) costs under 5ms.

The library also provides `prepareRichInline()` from `@chenglou/pretext/rich-inline`, which handles mixed-format inline text — body serif with inline monospace code, bold, italic, and links — as a single measurement unit with correct whitespace collapse. This is critical for technical prose where inline code spans appear frequently.

The font parameter uses canvas font string format, not a CSS object:

```typescript
// Correct: canvas font string
prepare(text, '16px Georgia')
prepare(text, 'bold 10.5px Newsreader, Georgia, serif')

// Not this: CSS object syntax does not work
prepare(text, { fontFamily: 'Georgia', fontSize: 16 })
```

This format matters because the canvas font string is what the browser's font engine expects. The font strings in the Pretext calls must exactly match the CSS `font-family` and `font-size` declarations in the React components. Any mismatch produces measurement errors — the measured height will not match the rendered height.

## The four-layer architecture

The system is organized into four layers, each with a single responsibility:

```
┌────────────────────────────────────────────┐
│  Input Layer: Markdown → typed blocks      │
├────────────────────────────────────────────┤
│  Measurement Layer: blocks → heights       │
├────────────────────────────────────────────┤
│  Pagination Engine: blocks → pages         │
├────────────────────────────────────────────┤
│  React Components: pages → HTML            │
└────────────────────────────────────────────┘
```

**Input layer.** A remark/unified pipeline parses Markdown into an MDAST tree. A converter walks the tree and produces typed content blocks: `HeadingBlock`, `ProseBlock`, `CodeBlock`, `TableBlock`, `CalloutBlock`, `ListBlock`, `ImageBlock`, `HorizontalRuleBlock`, `PageBreakBlock`. Each block has a unique ID and carries its content in a typed structure. The converter also strips YAML frontmatter (the `---` blocks that Obsidian adds to Markdown files) and removes callout markers like `[!NOTE]` and `[!SUMMARY]` from blockquote content.

**Measurement layer.** Each block is measured with Pretext. Heading blocks use `prepare()` + `layout()` with the Inter font at the appropriate size. Prose blocks use `prepare()` + `layout()` with the Newsreader font. Code and table blocks currently use height estimates based on line count — precise Pretext measurement for these types is planned for a later phase. The measurement results are stored in a `Map<string, BlockMeasurement>` keyed by block ID.

**Pagination engine.** The engine processes blocks in document order and places each block on the current page if it fits, or starts a new page if it does not. It enforces one constraint: a heading must not appear at the bottom of a page without at least one paragraph of content below it (orphan prevention). If a heading plus its next block would overflow the page, the heading moves to the next page.

**React components.** Each block type maps to a dedicated React component. The components use CSS flow layout (not absolute positioning) and reference design tokens for spacing, sizing, and colors. A `Page` component wraps each page with A4 dimensions and margins. A `BlockRenderer` dispatches to the correct component based on block type.

## The content model

The content model bridges between MDAST (the Markdown Abstract Syntax Tree) and the typed blocks that the measurement and rendering layers consume. MDAST represents syntax. The content model represents typographic intent.

A heading in MDAST is a node with `depth: 1–6` and children. A `HeadingBlock` in the content model has `level: 1–4`, `text: string`, and `children: InlineContent[]`. The distinction matters: the content model captures the text for measurement, the level for font selection, and the inline content for rendering. The MDAST node has none of these directly.

The core types:

```typescript
type ContentBlock =
  | HeadingBlock | ProseBlock | CodeBlock | TableBlock
  | CalloutBlock | ListBlock | ImageBlock
  | HorizontalRuleBlock | PageBreakBlock

type InlineContent =
  | { type: 'text'; value: string }
  | { type: 'bold'; children: InlineContent[] }
  | { type: 'italic'; children: InlineContent[] }
  | { type: 'code'; value: string }
  | { type: 'link'; url: string; children: InlineContent[] }
  | { type: 'break' }
```

The `InlineContent` union handles mixed formatting within prose. A paragraph containing "The `scraper` repository owns the **generic** workflow" produces five inline nodes: text, code, text, bold, text. This inline content is what the `prepareRichInline()` function consumes when measuring prose with mixed fonts.

### Three bugs in the converter and how they were fixed

**Bug 1: YAML frontmatter parsed as content.** The Book OCR report starts with a YAML frontmatter block delimited by `---`. Remark treats this as a thematic break followed by text content. The result was that the frontmatter fields (title, aliases, tags, etc.) appeared as rendered text at the top of the document. The fix was a `stripFrontmatter()` function that removes the leading `---\n...\n---` block before parsing.

**Bug 2: Callout markers rendered as visible text.** Obsidian blockquotes use markers like `> [!NOTE]` and `> [!SUMMARY]` to specify callout variants. The converter correctly detected these markers to set the variant, but it did not strip the marker text from the inline content. The rendered callout showed `[!summary]` as visible text at the beginning. The fix was a `stripCalloutMarker()` function that removes the `[!TYPE]` prefix from the first text node of the first paragraph inside a callout.

**Bug 3: GFM tables not parsed.** Remark-parse does not support GitHub Flavored Markdown tables by default. A Markdown table like `| A | B |` was parsed as a paragraph, not a table. The fix was adding `remark-gfm` to the unified pipeline.

## The typographic palette

The system uses three typefaces with distinct roles:

| Role | Typeface | CSS stack | Usage |
|------|----------|-----------|-------|
| Serif body | Newsreader | `Newsreader, Georgia, serif` | Prose paragraphs, list items, table cells |
| Sans-serif | Inter | `Inter, 'Helvetica Neue', sans-serif` | Headings, captions, annotations, page numbers |
| Monospace | JetBrains Mono | `'JetBrains Mono', Menlo, monospace` | Code blocks, inline code, file paths |

Each typeface appears at one size per context. Newsreader runs at 10.5px with 16px line height. Inter headings range from 28px (H1) down to 14px (H4). JetBrains Mono runs at 9px in full-width code blocks and is planned to run at 8px in column-width code blocks. The restraint is deliberate: Swiss typography achieves hierarchy through size and weight contrast, not through using many different fonts.

The spacing system derives from a 6px baseline grid. Every vertical space in the system is a multiple of this unit:

| Element | Spacing before | Spacing after | Baselines |
|---------|---------------|---------------|-----------|
| H1 | 0px | 36px | 6 |
| H2 | 20px | 8px | 3.3 / 1.3 |
| H3 | 24px | 12px | 4 / 2 |
| Prose | 0 | 12px | 2 |
| Code padding | 12px top/bottom | 12px margin | 2 / 2 |

The H2 spacing went through two iterations. The initial design used 36px before and 16px after, which produced too much vertical space between sections. After visual review, the spacing was reduced to 20px before and 8px after. The spacing is still derived from the baseline grid (20 ≈ 3.3 baselines, 8 ≈ 1.3 baselines) but the exact multiples were adjusted based on how the rendered output actually looked.

## The measurement pipeline

The measurement layer provides a single entry point:

```typescript
function measureBlock(block: ContentBlock, pageWidth: number): BlockMeasurement
```

Each block type has a dedicated measurement strategy. Heading blocks call `prepare()` with the Inter font at the heading's size, then `layout()` with the page width and the heading's line height. Prose blocks extract plain text from their inline content, call `prepare()` with the Newsreader font, then `layout()` with the content width (page width minus padding) and the body line height.

```typescript
function measureHeadingBlock(block: HeadingBlock, pageWidth: number): BlockMeasurement {
  const font = FONTS.heading[block.level];   // e.g. 'bold 28px Inter, "Helvetica Neue", sans-serif'
  const lineHeight = LINE_HEIGHTS.heading[block.level];  // e.g. 36
  const spacing = HEADING_SPACING[block.level];          // e.g. { before: 0, after: 36 }

  const prepared = getOrCreatePrepared(block.text, font);
  const { height, lineCount } = layout(prepared, pageWidth, lineHeight);

  return {
    blockId: block.id,
    heightPx: spacing.before + height + spacing.after,
    lineCount,
    minHeightPx: spacing.before + lineHeight + spacing.after,
  };
}
```

The `getOrCreatePrepared()` function caches prepared handles by a composite key of font string and text hash. This avoids re-running `prepare()` when the same text and font combination appears multiple times — for example, when a heading appears in both the document body and a table of contents.

Code blocks, tables, callouts, lists, and images currently use height estimates rather than Pretext measurement. A code block's height is estimated as `lineCount × lineHeight + padding`. This is accurate for code blocks that don't wrap, but inaccurate for code blocks with long lines that wrap at the container width. Precise Pretext measurement for these types is planned for a later phase.

### Font string synchronization

The font strings passed to Pretext must exactly match the CSS declarations in the React components. If the component renders text at `font-family: 'Newsreader', Georgia, serif; font-size: 10.5px` but the measurement uses `'10.5px Georgia, serif'` (without Newsreader), the measured height will differ from the rendered height. The font constants are centralized in a single file (`src/measurement/fonts.ts`) to prevent this class of error:

```typescript
export const FONTS = {
  body: {
    regular: '10.5px Newsreader, Georgia, serif',
    bold: 'bold 10.5px Newsreader, Georgia, serif',
    italic: 'italic 10.5px Newsreader, Georgia, serif',
  },
  heading: {
    1: 'bold 28px Inter, "Helvetica Neue", sans-serif',
    // ...
  },
  code: {
    regular: '9px "JetBrains Mono", Menlo, monospace',
  },
};
```

## The pagination engine

The pagination engine is a single-pass greedy algorithm. It processes blocks in document order, placing each block on the current page if it fits, or starting a new page if it does not. The engine maintains a cursor tracking the vertical position on the current page and checks each block's measured height against the remaining space.

The algorithm has three special cases:

1. **Explicit page breaks.** A `PageBreakBlock` (parsed from `<!-- page-break -->` comments) forces a new page regardless of remaining space.

2. **Orphan prevention for headings.** Before placing a heading, the engine checks whether the heading plus the next block's minimum height would overflow the page. If so, the heading moves to the next page. This prevents a heading from appearing at the bottom of a page with no content below it.

3. **Blocks that don't fit.** If a block's measured height exceeds the remaining space on the current page, the block moves to the next page. The current implementation does not split blocks across page boundaries — a long prose paragraph that overflows by one line still moves entirely to the next page. Block splitting is planned for a later phase.

The orphan prevention logic:

```typescript
if (block.type === 'heading') {
  const nextBlock = blocks[i + 1];
  if (nextBlock) {
    const nextMeasurement = measurements.get(nextBlock.id);
    const combinedHeight = measurement.heightPx + (nextMeasurement?.minHeightPx ?? 0);
    if (cursorY + combinedHeight > config.pageHeightPx) {
      // Move heading to next page
      pages.push(currentPage);
      currentPage = createPage(pages.length + 1, config.pageHeightPx);
      cursorY = 0;
    }
  }
}
```

The key insight is that the orphan check looks ahead at the next block's `minHeightPx`, not its full height. A paragraph might be 200px tall, but the orphan rule only requires showing at least two lines (32px). This allows paragraphs to be placed even when their full height would overflow, as long as the first two lines fit.

## The absolute-positioning failure and the flow-layout fix

The initial implementation used absolute positioning for blocks within a page. Each block received a `yOffset` from the pagination engine and was rendered with `position: absolute; top: yOffset`. This approach has a fundamental problem: the yOffset is computed from Pretext measurements, but the actual rendered height depends on CSS.

CSS applies its own line-height calculations, its own padding collapsing, its own font fallback chains, and its own text wrapping rules. Pretext measures text in isolation using Canvas `measureText()`, which does not perfectly model all CSS text rendering behaviors. When a block's Pretext-measured height of 120px renders as 128px in CSS, the next block's yOffset of 120px places it 8px inside the previous block. These small measurement errors accumulate across a page, producing progressively worse overlapping.

The visual manifestation was clear in the rendered output: on page 2 of the Book OCR report, the "2. Repository layout" heading overlapped the preceding content, and several blocks had text running over text. The spacing errors were not consistent — some blocks matched perfectly, others diverged by several pixels.

The fix was to abandon absolute positioning entirely. The pagination engine still decides which page each block belongs to, but within a page, blocks are rendered using normal CSS flow layout. Each block has a `marginBottom` value and flows naturally below the previous block. The `yOffset` and `heightPx` from pagination are used only for page-break decisions, not for visual positioning.

```typescript
// Before (broken): absolute positioning
<div style={{ position: 'absolute', top: pb.yOffset, height: pb.heightPx }}>
  <BlockRenderer block={pb.block} />
</div>

// After (working): CSS flow
<div>
  <BlockRenderer block={pb.block} />
</div>
```

This is the most important architectural lesson from the project: use Pretext for page-level decisions (which page does this block belong to?), not for pixel-level positioning (where exactly does this block sit on the page?). The browser's CSS engine is the authority for intra-page layout. Pretext is the authority for text measurement. These two responsibilities must not be conflated.

## The visual review process

After the Phase 1 implementation was rendering without overlapping, the system was reviewed visually by taking high-resolution section screenshots and requesting detailed typography feedback. The review produced 13 specific findings across three priority categories.

### Critical findings

**Body text measure too wide.** The initial margins were 25mm left / 20mm right, producing a content width of ~545px. At 10.5px Newsreader, this yielded approximately 85–95 characters per line. For serif body text, the optimal range is 60–75 characters. The fix was widening the margins to 35mm left / 30mm right, reducing the content width to ~490px and bringing the character count into the 65–70 range.

**H1 to intro paragraph spacing too tight.** The H1 had 24px of bottom spacing. This was insufficient to clearly separate the document title from the first paragraph. The fix was increasing H1 bottom spacing to 36px (6 baselines).

**Callout background too saturated.** The initial callout used saturated green and blue backgrounds (`#f0fdf4`, `#f0f4ff`). These drew too much attention for page 1 of a technical document. The fix was lighter, desaturated tints (`#f4faf7`, `#f7f9ff`).

### Important findings

**Inline code too prominent.** JetBrains Mono at 9px with a solid background and full-black color created too much visual density for inline code spans. The fix was reducing the size to 9.5px (slightly smaller than body), lightening the color to `#333333` (85% black), and adding 0.02em letter-spacing.

**Code line numbers too heavy.** Full-opacity line numbers in 9px JetBrains Mono competed with the code content. The fix was reducing opacity to 0.4 and shrinking the number font to 8px.

**Language label too shouty.** The code block language label was rendered as `COMMON-LISP` in uppercase, which was visually aggressive. The fix was a `formatLanguageName()` function that converts `common-lisp` to `Common Lisp` and dims the label with `opacity: 0.6`.

**Table header insufficiently distinct.** The initial table had header cells with the same background as body cells. The fix was adding a `#f5f5f5` gray background to header cells, increasing header padding to 10px, and adding subtle zebra striping to data rows.

## The two-column grid design

The second design phase (not yet implemented) specifies a two-column grid layout. The design introduces three concepts that work together: a CSS Grid with named regions, width-adaptive code blocks, and semantic CSS custom properties for all layout tokens.

### Grid rules

The grid enforces five rules:

1. **H1 and H2 span both columns.** They are section-level markers that establish context. A reader scanning the page sees the section title at full width before diving into columns.

2. **H3 and below sit within a single column.** Subsection headings, prose, lists, tables, and callouts render at column width (~260px). This creates the dense, newspaper-like layout characteristic of Swiss typography.

3. **Code blocks are width-adaptive.** Each code block is measured against the column width. If its longest line fits within the column, it renders at column width with an 8px font. If it overflows, it automatically spans both columns at the full 9px font.

4. **The gutter is empty.** The 20px space between columns contains no content. It is the breathing space that prevents the two columns from visually merging.

5. **The baseline grid governs vertical rhythm.** Every text line and spacing gap is a multiple of the 6px baseline. Text lines in the left and right columns align horizontally because they snap to the same grid.

The grid layout:

```
┌──────────────────────────────────────────────────────────┐
│  margin  │  column 1  │ gutter │  column 2  │  margin   │
│  35mm    │  ~260px    │  20px  │  ~260px    │  30mm     │
├──────────┼─────────────┼────────┼────────────┼───────────┤
│          │  H1: spans full width                   │      │
│          │  H2: spans full width                   │      │
│          ├─────────────┤        ├────────────┤          │
│          │  H3+ prose  │        │  H3+ prose │          │
│          │  lists      │        │  lists     │          │
│          │  tables     │        │  tables    │          │
│          ├─────────────┴────────┴────────────┤          │
│          │  wide code block (spans both cols)  │          │
│          ├─────────────┤        ├────────────┤          │
│          │  narrow code│        │  more prose│          │
└──────────┴─────────────┴────────┴────────────┘          │
```

### Width-adaptive code blocks

The width decision for code blocks uses Pretext's `measureNaturalWidth()` function. This function returns the width of the widest single line when no line breaking is applied — the minimum width the text needs before it starts wrapping.

```typescript
function computeNaturalWidth(block: CodeBlock): number {
  const lines = block.text.split('\n');
  let maxWidth = 0;
  for (const line of lines) {
    const prepared = getOrCreatePrepared(line, FONTS.code.regular);
    const width = measureNaturalWidth(prepared as PreparedTextWithSegments);
    maxWidth = Math.max(maxWidth, width);
  }
  return maxWidth;
}
```

If the natural width plus code padding exceeds the column width, the code block is promoted to full-width. The promotion is a layout decision, not a visual hint — the block renders with a different font size (9px instead of 8px), different padding, and a different CSS Grid column span.

The threshold includes a tolerance. Pretext measurement at 8px may not perfectly match CSS rendering at 8px, so a code block whose natural width is within 10% of the column width is kept in the column even if it technically overflows by a few pixels. This prevents unnecessary promotions where the wrapped version is still readable.

### Greedy-balance pagination

Two-column pagination must assign blocks to columns while preserving reading order and keeping the columns roughly balanced in height. Four strategies were evaluated:

- **Left-first fill:** Fill left column, then right. Simple but produces unbalanced columns.
- **Alternating:** Alternate blocks between columns. Balanced but breaks reading order.
- **Section-based:** Assign all content under an H2 to a column pair. Correct for narrative but complex to implement.
- **Greedy balance:** Process blocks in order, assign each to the shorter column. Balanced, preserves reading order, handles full-width interludes naturally.

The greedy balance strategy was chosen. For each column-width block, the algorithm assigns it to whichever column cursor is currently lower. Full-width blocks (H1, H2, wide code) consume both columns and reset both cursors to the same baseline. Page breaks occur when neither column has room for the next block.

### Semantic CSS custom properties

The design replaces TypeScript spacing constants with CSS custom properties organized in three layers:

**Layer 1: Primitives** — derived from the baseline grid.

```css
--baseline: 6px;
--gutter: 20px;
--column-width: calc((var(--content-width) - var(--gutter)) / 2);
```

**Layer 2: Layout tokens** — derived from primitives.

```css
--content-width: calc(var(--page-width) - var(--margin-left) - var(--margin-right));
--column-width: calc((var(--content-width) - var(--gutter)) / 2);
```

**Layer 3: Semantic spacing** — named by their typographic role.

```css
--space-h2-before: calc(var(--baseline) * 3.33);
--space-h2-after: calc(var(--baseline) * 1.33);
--space-paragraph-after: calc(var(--baseline) * 2);
--space-code-padding-y: calc(var(--baseline) * 2);
```

Components reference these tokens by name:

```tsx
<h2 style={{
  marginTop: 'var(--space-h2-before)',
  marginBottom: 'var(--space-h2-after)',
}}>
```

This has three advantages over JavaScript constants. First, the tokens can be overridden in `@media print` queries without changing React code. Second, the tokens appear in the browser's DevTools and can be adjusted live. Third, the token names communicate intent: `--space-h2-before` says "this is the space before an H2 heading," while `20` says nothing.

## Working rules

These are the stable engineering rules extracted from the project:

- **Rule 1: Pretext measures text. CSS renders text. Never use Pretext measurement for pixel-level CSS positioning.** The two engines will disagree on exact heights. Use Pretext for page-break decisions and CSS for intra-page layout.

- **Rule 2: Font strings in Pretext must match CSS declarations exactly.** A mismatch between the canvas font string and the CSS `font-family`/`font-size` produces measurement errors that accumulate across a page.

- **Rule 3: Swiss typography achieves hierarchy through size and weight contrast, not decoration.** A heading stands out because it is larger and bolder, not because it has a border, background color, or underline. Code blocks are distinct because they use a different typeface with a strong left border.

- **Rule 4: All spacing derives from a single baseline unit.** When the baseline is 6px, every vertical space in the system is a multiple of 6px. This creates consistent vertical rhythm. Changing the baseline changes the entire spacing system.

- **Rule 5: Visual review catches what code review cannot.** The measure-too-wide, callout-too-saturated, and inline-code-too-prominent findings were invisible in the code. They were only visible when looking at the rendered output.

## File reference

### Project directory

```
/home/manuel/code/wesen/2026-05-27--pretext-design-system/
├── pretext-print-layout/           # React + Pretext implementation
│   ├── src/
│   │   ├── input/                  # Markdown parsing (3 files)
│   │   ├── measurement/            # Pretext measurement (5 files)
│   │   ├── pagination/             # Page flow engine (1 file)
│   │   ├── components/             # React rendering (10 files)
│   │   ├── theme/                  # Design tokens + CSS (3 files)
│   │   └── __tests__/              # Unit tests (3 files, 22 tests)
│   └── public/
│       └── book-ocr-report.md      # Real 48KB test document
└── ttmp/                           # Docmgr ticket workspace
    ├── PRETEXT-PRINT-LAYOUT-001/   # Phase 1 ticket
    └── PRETEXT-2COL-LAYOUT-001/    # Two-column grid ticket (design only)
```

### Key source files

| File | Lines | Purpose |
|------|-------|---------|
| `src/input/content-model.ts` | 160 | All TypeScript types for content blocks, inline content, and pagination |
| `src/input/mdast-to-blocks.ts` | 230 | MDAST → typed blocks converter with callout marker stripping |
| `src/input/parse-markdown.ts` | 25 | remark/unified pipeline with remark-gfm and frontmatter stripping |
| `src/measurement/measure.ts` | 120 | `measureBlock()` dispatcher with estimates for non-text blocks |
| `src/measurement/measure-prose.ts` | 40 | Prose measurement with Pretext prepare/layout |
| `src/measurement/measure-heading.ts` | 25 | Heading measurement with font-specific prepare/layout |
| `src/measurement/cache.ts` | 50 | Prepared text handle cache with composite key |
| `src/measurement/fonts.ts` | 60 | Swiss typography font constants and spacing configs |
| `src/pagination/paginate.ts` | 110 | Greedy single-pass pagination with orphan prevention |
| `src/theme/tokens.ts` | 100 | Page dimensions, colors, heading configurations |
| `src/components/Document.tsx` | 50 | Top-level pipeline: parse → measure → paginate → render |
| `src/components/Page.tsx` | 50 | A4 page container with CSS flow layout |

### Implementation statistics

- **Source files:** 28 (TypeScript + CSS)
- **Implementation lines:** 1,791 (excluding tests)
- **Test lines:** 350 (22 tests across 3 test files)
- **Test environment:** jsdom + canvas (Pretext requires a real Canvas context for measurement)
- **Commits:** 9
- **Rendered output:** The full Book OCR report (48KB, 1081 lines) renders as 19 paginated A4 pages

## Related notes

- [[ARTICLE - Book OCR Project Report - Structured Workflow Runtime and Manual PDF Repair]] — the target document that drives content model and layout requirements
- The Pretext API documentation is saved in the ticket workspace at `ttmp/.../PRETEXT-PRINT-LAYOUT-001/sources/` (8 files, ~90KB)


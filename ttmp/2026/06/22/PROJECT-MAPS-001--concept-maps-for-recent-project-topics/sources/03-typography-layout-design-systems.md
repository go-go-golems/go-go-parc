# Code Context

## Files Retrieved
1. `Projects/2026/05/18/ARTICLE - Semantic Print-Layout DSL - Berkeley Mono Manual Specimen Lab.md` (lines 1-120) - semantic print-layout DSL, builder/tree/render architecture.
2. `Projects/2026/05/27/ARTICLE - Pretext Print Layout - Building a Swiss Typography Rendering System for Dense Programming Reports.md` (lines 1-120) - core Pretext print layout system and failure modes.
3. `Projects/2026/05/19/ARTICLE - DMETA Design System Factory - From Semantic Archetypes to Validated IR.md` (lines 1-100) - DMETA source IR, semantic archetypes, validator/generator framing.
4. `Projects/2026/06/01/ARTICLE - TTC Design System - DMETA Layout Foundation and CSS Governance.md` (lines 1-100) - TTC layered React design system and CSS ownership rules.
5. `Projects/2026/04/21/PROJ - CSS Visual Diff - Hair Booking Fringe Restyle Tooling.md` (lines 1-100) - chromedp evidence model for visual diffs and cascade analysis.
6. `Projects/2026/04/23/ARTICLE - Pyxis - Baseline Element Extraction and Visual Catalogs.md` (lines 1-100) - prototype/Storybook baseline catalog workflow.
7. `Projects/2026/05/28/ARTICLE - TTC DMETA Visual Parity - Preserving IR and Codegen While Matching the Original Design.md` (lines 1-100) - visual parity workflow preserving IR/codegen.
8. `Projects/2026/06/02/ARTICLE - Constraint-Based Layout on Canvas - Cassowary + Pretext + React.md` (lines 1-100) - constraint layout, Canvas, Pretext iterative solve-measure loop.
9. `Projects/2026/06/19/ARTICLE - Perpendicular Text Composition on Canvas - A Frame + Run Engine.md` (lines 1-80) - Canvas orthogonal typography with structural invariants.
10. `Projects/2026/06/19/ARTICLE - Responsive Orthogonal Typography Solver - Pretext Poster Fitting Deep Dive.md` (lines 1-80) - responsive poster fitting solver and measured segments.
11. `Projects/2026/06/20/PROJECT REPORT - typo-reflow-foldout - Pretext-Driven Text Reflow Architecture.md` (lines 1-80) - region-based live text reflow using Pretext.
12. `Projects/2026/05/23/ARTICLE - Devouring Details - Building an Interactive Typography Debug Tool.md` (lines 1-80) - interactive typography debugging via CSS vars and computed style sampling.
13. `ttmp/2026/06/22/PROJECT-MAPS-001--concept-maps-for-recent-project-topics/design/01-initial-scan-and-subagent-fanout-plan.md` (lines 1-100) - scope and assignment framing.

## Scope and search method

Scope was Markdown reports under `Projects/2026/{03,04,05,06}/`. I used a broad keyword grep for `typography`, `pretext`, `print layout`, `canvas text`, `text measurement`, `DMETA`, `TTC`, `design system`, `visual diff`, `storybook`, `widget`, `layout constraint`, `visual parity`, `generated UI`, `CSS`, `font`, `typeset`, `kerning`, `baseline`, and `print`, then used the full corpus file list to catch high-signal titles. The broad grep found 170 Markdown files with at least one matching term, so I narrowed to reports where the topic was central rather than incidental CSS or widget mentions.

## Key Code / report evidence

### Pretext and print-layout core

- `Projects/2026/03/30/PROJ - Pretext - Current AssemblyScript Implementation.md` is the earliest Pretext architecture checkpoint. Its key warning is that wasm only owns the numeric arithmetic layout core over JavaScript-prepared numeric arrays; analysis, segmentation, measurement, and rich line materialization remain JavaScript-side.
- `Projects/2026/05/27/ARTICLE - Pretext Print Layout - Building a Swiss Typography Rendering System for Dense Programming Reports.md` (lines 20-35) frames a React print renderer for dense technical reports: Markdown parsing, Pretext measurement, custom pagination, typed React blocks, A4 pages, and print CSS.
- Same file (lines 38-60) explains the two-stage Pretext API: `prepare()` segments/measures via Canvas once; `layout()` computes line count/height by arithmetic. Reported speed is roughly 500-600x faster than DOM approaches for repeat layout.
- Same file (lines 72-120) gives the main layered content model: Markdown/MDAST -> typed blocks -> Pretext measurements -> page breaks -> React components. Critical failure mode: Pretext heights diverged from CSS rendering heights when used for absolute positioning; the working rule is use Pretext for page-break decisions and CSS flow for intra-page layout.
- `Projects/2026/06/20/PROJECT REPORT - typo-reflow-foldout - Pretext-Driven Text Reflow Architecture.md` (lines 1-80) extends Pretext into interactive reflow around draggable callouts. Critical failure modes: CSS `white-space` parity mismatch, callout chrome parity mismatch, and silent Pretext font-cache poisoning at narrow widths.

### Canvas text measurement, geometry, and constraints

- `Projects/2026/06/02/ARTICLE - Constraint-Based Layout on Canvas - Cassowary + Pretext + React.md` (lines 1-42) identifies the hard problem: text height is a discontinuous function of width, while Cassowary constraints are linear. The solution is an iterative solve-measure loop: solve positions, measure text heights with Pretext, feed measured heights back as suggestions, repeat until convergence.
- Same file (lines 50-100) shows the architecture: Redux document state -> ConstraintBuilder -> IterativeResolver -> PretextBridge -> CanvasRenderer. The Cassowary solver is mutable/non-serializable and kept outside Redux; only resolved layout values are stored.
- `Projects/2026/06/19/ARTICLE - Perpendicular Text Composition on Canvas - A Frame + Run Engine.md` (lines 1-80) gives a reusable invariant pattern: represent orthogonality structurally via one local frame and a derived perpendicular axis, not by recalculating a second angle.
- `Projects/2026/06/19/ARTICLE - Responsive Orthogonal Typography Solver - Pretext Poster Fitting Deep Dive.md` (lines 1-80) broadens that into a solver: measure segments, generate candidates, fit to bounds, resolve overlap, validate invariants, and score results.

### DMETA, TTC, generated UI, and design systems

- `Projects/2026/05/19/ARTICLE - DMETA Design System Factory - From Semantic Archetypes to Validated IR.md` (lines 23-52) defines DMETA as a design-system factory for dense operational UI: semantic archetypes, capabilities, projections, presentations, actions, widgets, and design-language rules, with a Go/Glazed validator over YAML IR.
- Same file (lines 54-100) explains the origin: reusable process and artifacts extracted from HAIR-041, including widget IR catalog, design-language IR, Storybook coverage manifest, review guides, and widget-definition YAML.
- `Projects/2026/05/28/ARTICLE - TTC DMETA Visual Parity - Preserving IR and Codegen While Matching the Original Design.md` (lines 21-55) is the key visual parity report. It separates imported original design, DMETA IR, generated artifacts, promoted React components, Storybook/css-visual-diff, and ticket docs.
- `Projects/2026/06/01/ARTICLE - TTC Design System - DMETA Layout Foundation and CSS Governance.md` (lines 1-73) stabilizes TTC into layered React architecture: tokens, foundation primitives, layout primitives, atoms, molecules, organisms, pages, generated artifacts, and validators.
- Same file (lines 75-100) gives the central rule: put each visual/layout decision at the narrowest durable owner. This is likely an important concept-map hub node.
- Related DMETA/TTC files from the title scan: `Projects/2026/05/20/ARTICLE - DMETA Meta Design System - Street Deli Core Model and Mobile Ordering App.md`, `Projects/2026/05/20/ARTICLE - DMETA Widget Templates and Street Deli Menu Instantiations.md`, `Projects/2026/05/23/ARTICLE - DMETA Design System Factory - From Semantic Schemas to Generated React Widgets.md`, `Projects/2026/05/24/ARTICLE - DMETA as a Design System Compiler - Layered IRs and MetaDesignSystems.md`, `Projects/2026/05/31/ARTICLE - DMETA Language Cleanup - Multi-IR Architecture and Web Component System.md`, `Projects/2026/06/01/ARTICLE - DMETA React Design System - Layout Primitives Storybook and Cleanup.md`, `Projects/2026/05/27/ARTICLE - TTC DMETA React Workflow - Semantic IR to Storybook Garden Assistant.md`.

### CSS visual diff, Storybook, and parity workflows

- `Projects/2026/04/21/PROJ - CSS Visual Diff - Hair Booking Fringe Restyle Tooling.md` (lines 1-44) defines `css-visual-diff` as a browser comparison engine capturing screenshots, element screenshots, computed CSS, cascade winners, pixel diffs, and optional LLM review.
- Same file (lines 46-100) exposes the central data model: `CompareResult`, side-specific screenshots/style snapshots/matched snapshots, `StyleDiff`, `WinnerDiff`, and `PixelDiffStats`.
- `Projects/2026/04/23/ARTICLE - Pyxis - Baseline Element Extraction and Visual Catalogs.md` (lines 21-60) gives a reusable baseline-catalog method: prototype baseline catalog + Storybook implementation catalog -> comparison and repair.
- Same file (lines 62-100) defines baseline elements as stable units of comparison, not necessarily React components.
- Related reports: `Projects/2026/04/23/ARTICLE - Pyxis - Developer Handoff for Visual Comparisons and Storybook Parity.md`, `Projects/2026/04/23/ARTICLE - css-visual-diff - Building a Visual Diff Workbench for Pyxis.md`, `Projects/2026/04/24/ARTICLE - Textbook - CSS Visual Diff Flexible JavaScript API Implementation.md`, `Projects/2026/04/25/ARTICLE - Textbook - Embeddable Semantic Diff Widgets for Literate PR Review.md`, `Projects/2026/04/27/PROJ - CSS Visual Diff Review Site.md`, `Projects/2026/04/29/ARTICLE - CSS Visual Diff - Retiring the Native YAML Runner for a JavaScript First Workflow Engine.md`.

### Typography debugging and font tooling

- `Projects/2026/05/23/ARTICLE - Devouring Details - Building an Interactive Typography Debug Tool.md` (lines 1-80) describes live typography debugging: Redux state -> CSS custom properties -> DOM, `getComputedStyle` sampling, sliders added by inspecting actual elements, and crosshair spatial overlays.
- Other high-signal files: `Projects/2026/05/18/PROJ - TypoScope - Firefox Typography Measurement Extension.md`, `Projects/2026/05/22/PROJ - Typo Copy Generator - Font Practice Sheet CLI.md`, `Projects/2026/05/23/PROJ - font-util - TTC Extraction and Typography Practice CLI.md`, `Projects/2026/05/29/ARTICLE - TTF Glyph-Outline VM Renderer - Architecture and Implementation.md`, `Projects/2026/05/30/ARTICLE - TTF Rasterizer Bug Hunting - Scale, Windings, and Coverage.md`, `Projects/2026/06/22/ARTICLE - Taking Control of Sphinx LaTeX PDF Typography.md`.

## Architecture

The topic slice is organized around four overlapping systems:

1. **Measurement-driven typography/layout**: Pretext and Canvas measurement appear as a recurring primitive for print PDFs, poster composition, constraint layout, and live reflow. The strongest architectural edge is `prepare/measure once -> layout/solve many times`.
2. **Semantic design-system generation**: DMETA models semantic roles/capabilities/actions/widgets, lowers them through IRs, and generates React scaffolds/metadata. TTC is the most concrete consumer.
3. **Promoted React design systems**: Generated artifacts become hand-owned React components, but keep provenance and manifest connections. CSS governance assigns repeated decisions to tokens/foundation/layout/atoms/molecules/organisms/pages.
4. **Evidence-based visual parity**: css-visual-diff, Storybook, prototype catalogs, and imported originals form an evidence loop for making generated/promoted UI match a reference without abandoning codegen.

A likely concept-map spine:

```text
Pretext two-stage measurement
  -> print pagination
  -> canvas constraint solve-measure loop
  -> interactive text reflow
  -> orthogonal/poster fitting solvers

DMETA semantic IR
  -> Web MetaDesignSystem / widget templates
  -> generated React scaffolds
  -> promoted React components
  -> Storybook review surface
  -> css-visual-diff visual parity loop
  -> CSS governance / ownership validators
```

## Clusters and subclusters

### Cluster A: Pretext/text measurement/layout engines
- Pretext AssemblyScript port: numeric core boundary, wasm vs JS responsibility.
- Swiss print-layout renderer: Markdown -> typed blocks -> Pretext measurement -> pagination -> React/print CSS.
- Canvas constraint layout: Cassowary linear constraints plus Pretext nonlinear text height feedback.
- Typo reflow foldout: free rectangular regions, line-band obstruction subtraction, live pointer-move reflow.
- Orthogonal poster solvers: measured segments, invariant-preserving frames, scoring/candidate selection.

### Cluster B: Print and specimen DSLs
- Berkeley Mono manual specimen lab: semantic JS builder DSL emits serializable document tree rendered to HTML; live CodeMirror/eval controls typography and style rules.
- Pretext print layout: technical-report PDFs with Swiss typography, baseline grid, width-adaptive future two-column design.
- Sphinx LaTeX PDF typography: likely overlaps in print pipeline control, though I did not inspect it deeply.

### Cluster C: DMETA and meta-design-system compiler
- Semantic archetypes/capabilities/presentations/actions/widgets/design-language IR.
- Go/Glazed validator and planned TypeScript registry/generator.
- Street Deli and TTC as concrete instantiations.
- Multi-IR cleanup and web-component/React target evolution.

### Cluster D: TTC generated UI and visual parity
- Semantic IR -> Storybook Garden Assistant.
- Imported original as visual baseline.
- Generated artifacts remain current, promoted React owns runtime truth.
- CSS/token/foundation/layout governance prevents repeated local visual decisions.

### Cluster E: Visual diff and Storybook systems
- css-visual-diff/sbcap extraction from hair-booking.
- Pyxis prototype baseline extraction and Storybook implementation catalog.
- Diff review site and embeddable semantic diff widgets.
- JavaScript-first workflow engine for comparison plans.

### Cluster F: Typography tooling and fonts
- TypoScope, Devouring Details, Typography Debug Palette.
- TTC extraction/font-util/TTF rendering/rasterizer investigations.
- Font practice sheet CLI and glyph outline VM.

## Recurring concepts, technologies, and failure modes

Recurring concepts:
- Two-stage layout: slow prepare/measure, fast repeated layout.
- Structural invariants over computed targets: e.g. orthogonality by derived axes.
- Typed content/semantic blocks before rendering.
- Generated scaffolds plus promoted hand-owned implementation.
- Baseline catalogs as evidence, not screenshots alone.
- CSS governance: narrowest durable owner.
- Storybook as architecture/review test, not just demo surface.

Technologies:
- `@chenglou/pretext`, Canvas `measureText`, Canvas `TextMetrics`, SVG, React, Vite, TypeScript, Redux.
- Cassowary/kiwi constraints.
- DMETA YAML IR, Go/Glazed validators, generated TypeScript/React.
- Storybook, MSW in older notebook/editor flows, chromedp, css-visual-diff, Goja/jsverbs for scriptable workflows.
- CSS custom properties, computed style extraction, CSS cascade winner analysis.

Failure modes:
- Pretext measurement and CSS rendered height diverge if used for absolute positioning.
- Canvas font strings must exactly match CSS font declarations.
- Browser-only bugs: `white-space` mismatch, chrome/parity mismatch, Pretext font-cache poisoning at narrow widths.
- Constraint solvers cannot express nonlinear text height directly; need iterative solve/measure.
- Visual parity can drift if generated IR, promoted React, Storybook, and imported originals are not explicitly assigned roles.
- CSS decisions duplicated locally become unreviewable; design systems require ownership validators.
- Prototype screenshots can be misleading when design canvases/artboards/transforms are captured instead of clean product render targets.

## Candidate concept-map nodes and edges

Nodes:
- Pretext `prepare()` / `layout()` split
- Canvas text measurement
- Rich inline measurement
- Pagination engine
- Baseline grid / Swiss typography
- CSS flow vs absolute positioning
- Cassowary solve-measure loop
- Region-based text reflow
- Orthogonal frame/run engine
- DMETA semantic archetype
- Capability / projection / presentation / action
- Widget IR
- Web MetaDesignSystem
- Generated React scaffold
- Promoted React component
- Storybook contract
- css-visual-diff CompareResult
- Cascade winner diff
- Prototype baseline catalog
- Visual parity loop
- CSS governance / narrowest durable owner
- Typography debug palette / computed-style sampling
- Font cache / font string parity

Edges:
- `Pretext prepare/layout` -> enables -> `fast pagination and interactive reflow`.
- `Canvas measureText` -> backs -> `Pretext prepare stage`.
- `Pretext measurement` -> informs -> `pagination page-break decisions` but not `absolute CSS heights`.
- `Cassowary solver` -> requires bridge to -> `Pretext measured text height`.
- `Orthogonal frame` -> guarantees -> `perpendicular typography invariant`.
- `DMETA semantic IR` -> lowers to -> `Web MetaDesignSystem` -> generates -> `React scaffolds`.
- `Generated React scaffolds` -> promote into -> `hand-owned React components`.
- `Promoted React components` -> validated by -> `Storybook contracts` and `css-visual-diff`.
- `Imported original design/prototype` -> defines -> `visual baseline catalog`.
- `css-visual-diff` -> produces -> `pixel diff + computed CSS diff + cascade winner diff`.
- `CSS governance` -> constrains -> `where layout/typography decisions may live`.
- `Typography debug tools` -> sample -> `computed DOM styles` -> mutate -> `CSS custom properties`.

## Overlaps with other topic slices

- Agent 2 / JavaScript runtimes: css-visual-diff JS DSL, Goja/jsverbs orchestration, generated UI DSL reports, WidgetRenderer standalone site, go-go-goja UI DSL.
- Agent 5 / observability/transcripts: Transcript-driven design-system recovery with go-minitrace and LLM review for css-visual-diff.
- Agent 6 / data/RAG/search: RAG React design system, Widget IR for RAG Evaluation, corpus explorer UI, document/report rendering.
- Agent 7 / web UI/apps: React app shells, Storybook surfaces, browser-side widget runtime, md-view/Wails surfaces, chat overlay widgets.
- Agent 1 / hardware: Loupedeck font/text rendering, e-ink/PicoCalc UI backbuffer text, thermal printer/Almanach layout/rasterization.

## Open questions

- Should Pretext be represented as one node or split into `library`, `measurement API`, `print-layout usage`, `canvas usage`, and `wasm numeric core`?
- Which DMETA generation reports are canonical after the later language cleanup: 05/19 factory, 05/24 compiler, 05/31 cleanup, or 06/01 TTC foundation?
- Should visual parity be mapped as a workflow cluster independent of DMETA, with Pyxis/Hair/TTC as examples?
- How much of font tooling (TTC extraction, TTF rasterizer, glyph outline VM) belongs in this slice versus hardware/rendering?
- Does `Taking Control of Sphinx LaTeX PDF Typography` represent a separate print pipeline that should connect to Pretext print layout as alternative paths to PDF typography?

## Recommended report-format lessons

- Use two levels: a compact list of found reports first, then clusters and concept-map candidates. This corpus has too many related reports for a flat annotated bibliography.
- Separate `central` vs `incidental` hits. Many reports mention Storybook/widgets/CSS, but only a subset are design-system or visual-parity projects.
- Include failure modes explicitly; they are the best edges for future concept maps because they connect projects across months.
- Preserve repo paths from frontmatter when available; many reports point to code outside this repository.

## Start Here

Start with `Projects/2026/05/27/ARTICLE - Pretext Print Layout - Building a Swiss Typography Rendering System for Dense Programming Reports.md` for the typography/layout half, then `Projects/2026/06/01/ARTICLE - TTC Design System - DMETA Layout Foundation and CSS Governance.md` for the DMETA/TTC design-system half. Together they expose the two main spines of this topic slice.

```acceptance-report
{
  "criteriaSatisfied": [
    {
      "id": "criterion-1",
      "status": "satisfied",
      "evidence": "Wrote only the requested scout findings artifact under ttmp/.../sources/03-typography-layout-design-systems.md and did not modify project/source corpus files."
    },
    {
      "id": "criterion-2",
      "status": "satisfied",
      "evidence": "Report includes scope/search method, retrieved file paths with line ranges, clusters, recurring concepts/failure modes, candidate nodes/edges, overlaps, open questions, and format lessons."
    }
  ],
  "changedFiles": [
    "ttmp/2026/06/22/PROJECT-MAPS-001--concept-maps-for-recent-project-topics/sources/03-typography-layout-design-systems.md"
  ],
  "testsAddedOrUpdated": [],
  "commandsRun": [
    {
      "command": "ls Projects/2026",
      "result": "passed",
      "summary": "Confirmed target month directories 03, 04, 05, 06 exist."
    },
    {
      "command": "grep -RIlE \"typography|pretext|print-layout|print layout|canvas|DMETA|TTC|design-system|visual parity|visual diff|storybook|widget IR|text measurement|font\" Projects/2026/{03,04,05,06} --include='*.md' | wc -l",
      "result": "passed",
      "summary": "Found 170 Markdown files with broad typography/layout/design-system terms before narrowing to central reports."
    },
    {
      "command": "git status --short",
      "result": "passed",
      "summary": "Showed existing untracked .pi/.ttmp/ttmp paths; no staged files indicated."
    }
  ],
  "validationOutput": [
    "Artifact written to requested output path.",
    "No project/source files under Projects/2026 were modified."
  ],
  "residualRisks": [
    "Broad grep produced many incidental CSS/widget hits; this report prioritizes central topic reports and may omit minor UI mentions.",
    "Some related DMETA/TTC follow-up reports were identified by title/frontmatter rather than deeply read due to time and scope."
  ],
  "noStagedFiles": true,
  "notes": "Existing untracked files/directories were present before/around this scout run; only the requested source report was intentionally written."
}
```

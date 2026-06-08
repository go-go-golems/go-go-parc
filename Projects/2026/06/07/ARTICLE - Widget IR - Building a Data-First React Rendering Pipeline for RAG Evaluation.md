---
title: "Widget IR: Building a Data-First React Rendering Pipeline for RAG Evaluation"
aliases:
  - "Widget IR"
  - "Semantic Widget IR"
  - "xgoja widget DSL"
tags:
  - article
  - widget-ir
  - react
  - xgoja
  - goja
  - rag-evaluation
  - design-system
status: active
type: article
created: 2026-06-07
repo: /home/manuel/workspaces/2026-05-27/rag-evaluation-system/2026-05-27--rag-evaluation-system
---

# Widget IR: Building a Data-First React Rendering Pipeline for RAG Evaluation

This article documents how the RAG Evaluation System grew a rendering pipeline that separates data authoring from UI rendering: JavaScript scripts written in Goja emit JSON-compatible Widget IR, a Go server serves that IR as JSON, and a React `WidgetRenderer` maps each IR node to a real package component. The pipeline spans from low-level atoms and layout primitives through semantic context diagrams, annotated transcripts, course slides, and handout documents, all the way to a runnable xgoja example site with eight navigable pages.

> [!summary]
> - **Widget IR is data, not HTML.** Goja scripts produce JSON objects describing UI structure. The renderer maps those objects to React components. No HTML is generated anywhere in the pipeline.
> - **Five surfaces must stay in sync.** Adding a new component means updating TypeScript IR types, the React renderer, Goja helpers, the server schema, and stories/tests.
> - **Recipes sit above direct nodes.** Direct component nodes handle custom composition; recipes handle common product screens. Both produce the same Widget IR shape.

## Why This Architecture Exists

The RAG Evaluation System needed a way for backend JavaScript scripts to produce interactive UI without the scripts themselves knowing about CSS modules, controlled form behavior, accessibility, or component internals. The initial approach was simple: define a small Widget IR model, write a React renderer, and let JavaScript produce IR through a Goja module.

The early implementation served dashboard tables, metric panels, and action toolbars well. But as the design-system package grew—adding context-window diagrams, transcript readers, annotation rails, course studio shells, and handout document browsers—the IR layer had not kept up. The package components were stable and story-covered. The Goja DSL still exposed only the older, smaller vocabulary. A gap had formed between what authors could do and what the package actually contained.

The correct fix was not to build a Go-side HTML renderer. Copying React component DOM into Go creates a second UI implementation and breaks CSS Module ownership. The existing architecture was sound: Goja produces JSON IR, React owns rendering. The task was to widen the coverage.

## The Data-to-UI Pipeline

The pipeline has five stages. Each stage has a single responsibility and passes data forward without mutating it.

```text
JavaScript authoring script
  require("widget.dsl") or require("rag.dsl")
          |
          v
Goja native module: pkg/widgetdsl/module.go
  returns JSON-compatible Widget IR objects
          |
          v
widgetrunner validates page shape and action results
          |
          v
widgetserver serves /api/widget/pages/{id}
          |
          v
React app: RagEvaluationSiteApp + useWidgetPage
          |
          v
WidgetRenderer maps { kind: "component", type: "..." }
  to actual @go-go-golems/rag-evaluation-site React components
          |
          v
CSS Modules + theme tokens + real component behavior
```

The critical invariant is that Goja never touches HTML. It never knows about class names, layout, or interaction. It knows only about component type strings, JSON-serializable props, and action specifications. The renderer knows everything about rendering and nothing about data authoring.

### Widget IR Shape

The TypeScript model defines JSON primitives, JSON values, and Widget nodes. The important shape is:

```typescript
export type WidgetNode = TextNode | ElementNode | ComponentNode;

export interface ComponentNode {
  kind: 'component';
  type: RagWidgetType | string;
  props?: WidgetProps;
  children?: WidgetNode[];
}
```

All component props must remain serializable. A prop may contain `WidgetNode` or `RenderableValue`, but it cannot contain functions, React elements, class instances, or live service references. This constraint is not a limitation; it is the reason the architecture works. JSON data crosses the Goja→server→browser boundary cleanly. Functions cannot.

### ActionSpec: Crossing the Callback Boundary

React callbacks such as `onAnnotationSelect` cannot appear in JSON. The renderer converts `onAnnotationSelectAction` into a callback that fires when the component detects a selection, sending context objects like `{ annotationId, value: annotationId, componentType }`. The server receives these as standard widget actions and can respond with data refreshes, state mutations, or toast notifications. The action model works uniformly for buttons, table rows, transcript annotations, comment rails, document selections, and agenda navigation.

## Five Surfaces to Keep in Sync

Adding a new Widget IR component requires updating five places simultaneously. The implementation plan treats these as a single atomic change:

1. **TypeScript IR contract** — `packages/rag-evaluation-site/src/widgets/ir.ts` — add the component type to `RagWidgetType`, define the props interface, add it to `WidgetProps`.
2. **React renderer** — `packages/rag-evaluation-site/src/widgets/WidgetRenderer.tsx` — import the component, add a switch case, add a render helper that normalizes `WidgetNode` slots and `ActionSpec` callbacks.
3. **Goja DSL helpers** — `pkg/widgetdsl/module.go` — add the JavaScript helper name to `componentNames` and the React type to `componentTypes`.
4. **Server schema** — `pkg/widgetschema/schema.go` — add component types to `ComponentTypes`.
5. **Stories and tests** — `WidgetRenderer.*.stories.tsx` and `pkg/widgetdsl/module_test.go` — add at least one Storybook story and one Go JSON round-trip test per component family.

Missing any surface produces visible failures. An unknown type renders an `ErrorCallout`. A missing helper causes Goja to reject the script. A missing schema entry produces no server error but makes the API lie about supported components.

## The Design-System Foundation

The package `@go-go-golems/rag-evaluation-site` is the canonical reusable UI layer. It exports five component layers:

- **Foundation** — text, captions, status, code, dividers, accessibility helpers.
- **Atoms** — basic controls and semantic markers: `ContextKindSwatch`, `AnnotationBadge`, `TranscriptRoleBadge`.
- **Layout** — generic structure primitives: `SectionBlock`, `SplitPane`, `SidebarShell`, `SlideShell`.
- **Molecules** — reusable data-display patterns with no backend hooks.
- **Organisms** — feature panels with DTO-shaped props and callbacks.

The guidelines say React first, Widget IR later. Only components with stable visual APIs, mostly JSON-compatible props, and Storybook coverage become Widget IR nodes. The Widget IR layer follows, never leads.

## Widget IR Expansion: Phase by Phase

The implementation proceeded in phases, each adding a coherent component family and keeping the validation set green.

### Foundation, Atoms, and Layout

The lowest-risk phase added core layout primitives: `Text`, `CodeText`, `Divider`, `ContextKindSwatch`, `AnnotationBadge`, `SectionBlock`, `SplitPane`, `SidebarShell`, and `SlideShell`. These components do not depend on context-domain DTOs. Their props are plain strings, numbers, booleans, and `WidgetNode` slots. The stories proved that Widget IR can assemble layouts that look identical to their JSX originals.

`SplitPane` received two new features during this phase: a `sidebar` ratio that constrains the left column to a bounded range, and a `gutter` option that adds inner padding on both panes. These solved a real visual problem where documents and previews pressed directly against the divider.

`SidebarShell` received a `contentPadding` option for the same reason: layout primitives need their own spacing APIs rather than forcing every caller to wrap children in padded containers.

### Context Diagrams

Context diagrams were the first DTO-backed family. The props are already JSON-compatible `ContextWindowSnapshot` objects from `packages/rag-evaluation-site/src/context/types.ts`. The diagram components expose different optional props — `ContextBudgetBar` and `ContextStripDiagram` accept a `mode` parameter, while `ContextStackDiagram` and `ContextTreemap` do not — and the IR prop interfaces mirror the real component APIs instead of inventing a fake unified shape.

The diagram family includes `ContextLegend`, `ContextBudgetBar`, `ContextStripDiagram`, `ContextStackDiagram`, `ContextTreemap`, and the stateful `ContextDiagramPanel` which handles view switching internally.

### Transcript, Annotation, and Comments

The transcript family validated both high-level and low-level authoring patterns. `TranscriptWorkspacePanel` is the ergonomic default, but `TranscriptReaderPanel` + `AnnotationRailPanel` gives authors full control over the split composition. `AnchoredCommentCard` and `AnchoredCommentRail` brought the comment system into the IR model with `onDismissAction` and `onCommentSelectAction`.

The `annotationSelectHandler()` helper was added to the renderer to construct consistent context objects across all transcript-related components. This was important because the action model requires predictable context keys: `annotationId` for annotations, `commentId` for anchored comments.

### Course, Studio, Handout, and Document

These were the most page-like components. `CourseLessonPanel`, `CourseSlidePanel`, and `CourseStudioShell` compose with `SidebarShell` + `SidebarNav` for navigation. `SlideShell` was added as a generic teaching layout with `primary`, `secondary`, and `footer` slot props, not context-domain-specific.

`HandoutDocumentShell`, `DocumentListPanel`, and `DocumentPreviewToolbar` handle document browsing. `MarkdownArticle` provides a dependency-free markdown subset renderer for handout content. Several molecule props contain arrays with nested `RenderableValue` fields, so the renderer maps those through `renderRenderableValue` rather than passing JSON objects directly.

`DocumentPreviewToolbar.onDownloadAction` and `HandoutDocumentShell.onDownloadAllAction` have no natural selected ID, so the renderer binds component-level contexts for those actions.

### Semantic Recipes

The recipe layer sits on top of direct nodes. It does not render anything new; it expands domain objects into Widget IR trees that the renderer already knows how to display.

The new recipes are:

```javascript
rag.recipes.contextDiagram({ snapshot, view: "budget" })
rag.recipes.annotatedTranscript({ transcript, selectedAnnotationId: "a1" })
rag.recipes.courseStudio({ sections, main: slidePanel })
rag.recipes.courseSlide({ slide, snapshot, index: 0, total: 3 })
rag.recipes.handout({ bundle, selectedDocumentId: "guide" })
```

Each recipe accepts a domain object (snapshot, transcript, course, slide, handout bundle) and produces a single Widget IR node. The `courseStudio` recipe accepts a `main` Widget IR node and puts it into children, so it validates that `main` is actually a WidgetNode export. The recipes keep Goja scripts short and readable without sacrificing the renderer's control over rendering.

## The xgoja Widget Site

The generated xgoja widget-site example is where the pipeline becomes tangible. It runs a Go binary that serves an embedded React SPA, exposes Widget IR pages through HTTP, and handles server actions.

The example was expanded from a single dashboard demo page to eight distinct navigable pages:

- `/pages/index` — overview of all example pages
- `/pages/demo` — queue/master-detail table with row-selection detail switching
- `/pages/actions` — server-action lab with toolbar buttons and audit trail
- `/pages/semantic` — all five recipes in one page
- `/pages/transcripts` — transcript workspace, reader, annotation rail, anchored comments
- `/pages/slides` — course slide panels and custom SlideShell composition
- `/pages/handouts` — handout shell with document-list, preview toolbar, and markdown article
- `/pages/course-examples` — course lesson panel and course studio shell

Each page returns a JSON page object with `schemaVersion`, `id`, `title`, and `root`. The `root` is a Widget IR tree built from recipes and direct component helpers. The React app loads the page through `useWidgetPage`, renders the root through `WidgetRenderer`, and applies the default `AppShell` navigation shell.

The top navigation uses shared `navItems` and `pageMeta` to provide consistent navigation across all pages. Each page includes its own metadata: `activeNavItemId`, `navItems`, and `maxWidth`.

### xgoja Documentation

Two documentation files ship through the widget-site xgoja provider's embedded help FS:

- `01-widget-dsl-getting-started.md` — tutorial covering widget.dsl, recipes, xgoja build steps, and the new semantic pages.
- `02-widget-dsl-js-api-reference.md` — complete reference for all module names, core constructors, component helpers, cell specifications, child normalization, actions, recipe documentation, and the new semantic DTO shapes for context snapshots, transcripts, anchored comments, course/slides, handouts, split panes, and sidebar shells.

The API reference was expanded to cover the full helper table, the semantic component props, and the layout details for gutter/sidebar ratio and sidebar content padding.

### The Embedded SPA Problem

The xgoja example embeds a static SPA bundle from `packages/rag-evaluation-site/app-dist`. After renderer changes, the embedded assets can become stale and show `Unknown widget` errors for new component types. The fix is:

```bash
pnpm --dir packages/rag-evaluation-site build:app
cd examples/xgoja/widget-site && make sync-app
```

The Makefile `smoke` target includes this step. The smoke test also verifies the new semantic pages by checking for expected component names in JSON page responses.

## Validation

The implementation was validated at every level:

**Frontend/package:**
- `pnpm --dir packages/rag-evaluation-site typecheck`
- `pnpm --dir packages/rag-evaluation-site build`
- `pnpm --dir packages/rag-evaluation-site build:app`
- Storybook build to multiple output directories covering all subgroups.

**Go/xgoja:**
- `go test ./pkg/widgetdsl ./pkg/widgetrunner ./pkg/widgetserver ./pkg/widgetschema -count=1`
- `cd examples/xgoja/widget-site && make smoke`
- `node --check examples/xgoja/widget-site/verbs/sites.js`

**Browser:**
- Storybook stories checked visually for course/handout split-pane spacing and SidebarShell padding.
- Generated xgoja site run locally, pages checked in browser for correct rendering, row selection, and action refresh.
- No `Unknown widget` messages after refreshing embedded assets.

**Docmgr:**
- `docmgr doctor --ticket RAGEVAL-WIDGET-IR-SEMANTIC-COMPONENTS --stale-after 30`

## Common Failure Modes

### Stale embedded xgoja assets

After adding renderer support for new components, the xgoja binary serves an outdated SPA. The browser shows `Unknown widget` for the new component types. The fix is to rebuild `app-dist` and re-sync.

### Callback props in IR

React components use functions for callbacks. Widget IR must use `ActionSpec` objects. A renderer case that accepts `onSelect` as a function will break if the IR passes a JSON action spec. The renderer must check the prop type and convert action specs to callbacks.

### Node-valued props

Props like `SplitPane.left`, `SidebarShell.sidebar`, and `SlideShell.primary` are `WidgetNode`, not `ReactNode`. The renderer must call `renderWidgetNode` on them, not pass them through directly. This was a recurring source of errors in the course/handout phase.

### Schema drift

Adding a new component to `ir.ts` and `WidgetRenderer.tsx` without updating `pkg/widgetschema/schema.go` produces no build error. The schema endpoint lies about supported components. This is a silent failure mode that requires the schema step to always be included.

### Storybook `args` requirement

When a Storybook story uses a custom `render` function instead of the default, the `Story` type still requires an `args` property. Adding a minimal `args: { node: {...} }` fixes the typecheck error.

## Working Rules

From the implementation:

- Widget IR should describe semantic UI, not recreate CSS-module DOM internals.
- React is the rendering source of truth. Goja and Go validate, serve, and dispatch actions, but do not render.
- Add direct nodes for stable JSON-compatible components. Add recipes for common product compositions.
- Every new component updates five surfaces: IR types, renderer, Goja helpers, schema, stories/tests.
- Use `WidgetRenderer` in Storybook, not direct component JSX, for Widget IR validation stories.
- The `gutter` and `contentPadding` options on layout primitives are intentionally opt-in; defaults remain tight to match the existing dashboard aesthetic.

## What Comes Next

The foundation is in place. The remaining work is incremental:

- Add semantic recipes for additional compositions (e.g., context diagram + metadata grid, transcript + anchored comments).
- Expand the xgoja example with a navigation page that links all examples.
- Add browser-level visual smoke for the xgoja semantic pages.
- Consider generating the Goja helper table from `module.go` to prevent documentation drift.
- Explore splitting `WidgetRenderer.tsx` by component family if it becomes hard to maintain.
- Add a shared action logger decorator for all action-related Widget IR stories.
- Compose the web pages `ContextVisualizerPage`, `TranscriptAnnotationPage`, and `ContextCoursePage` using the new package fixtures and components.

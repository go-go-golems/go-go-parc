---
title: "RAG React Design System: From Prototype Dashboard to Structured Design System"
aliases:
  - RAG React Design System Cleanup
  - RAG Evaluation Dashboard Design System
  - RAG Web Refactor Deep Dive
tags:
  - article
  - react
  - design-system
  - rag
  - storybook
  - css
  - dmeta
  - frontend-architecture
status: active
type: article
created: 2026-06-02
repo: /home/manuel/workspaces/2026-05-27/ttc-design-system/2026-05-27--rag-evaluation-system
---

# RAG React Design System: From Prototype Dashboard to Structured Design System

This article records how the RAG Evaluation System web page was transformed from a useful but prototype-shaped React dashboard into a coherent design-system-based frontend. The work happened in many passes. Each pass reduced one kind of ambiguity: ambiguous CSS ownership, ambiguous component boundaries, ambiguous Storybook coverage, ambiguous page contracts, and ambiguous relations between DMETA design language and the concrete React implementation.

The result is not a finished product in the sense that every page is now split into a perfect container/presentation hierarchy. The result is a stable architecture that can keep improving. The dashboard now has tokens, foundation primitives, atoms, layout primitives, reusable molecules, feature organisms, page boundaries, Storybook review surfaces, and a documentation-only DMETA IR seed. The global stylesheet has been reduced to true global concerns. Most visible interface decisions now live in named components with local CSS Modules and stories.

> [!summary]
> The RAG dashboard cleanup followed a strict sequence: first identify the implicit system, then extract tokens and primitives, then migrate components bottom-up, then delete globals only after searches proved they had no active consumers. Storybook became the review surface, and DMETA IR stayed documentation-only until there is a concrete generator requirement.

## The starting point

The RAG Evaluation System already had a strong functional surface. The web app exposed Search, Corpus, Workflows, Pipeline, Embeddings, and Evaluation views. It could submit retrieval queries, inspect evidence chunks, browse corpus sources and documents, submit intake workflows, inspect workflow operations, compute embeddings, and compare stored vectors. The backend API and RTK Query layer were meaningful; the problem was not that the app lacked behavior.

The problem was that the UI implementation encoded too many design decisions in the wrong places. `web/src/index.css` acted as a token file, a foundation system, a layout system, a set of atoms, a table library, workflow visualization styling, form styling, and utility library. React components mixed API fetching, layout rules, typography choices, dense data display, status formatting, and feature-specific rendering in the same JSX blocks. Many surfaces worked visually because they shared global class names, not because those classes had explicit ownership.

The first review document described this condition directly. Existing React and CSS were treated as evidence, not as architecture. The important distinction is that evidence tells us what the product currently needs to express; architecture decides where those expressions belong.

The initial target layering was:

```text
raw tokens
  -> semantic dashboard tokens
  -> foundation primitives
  -> layout primitives
  -> reusable data/display molecules
  -> feature organisms
  -> page presentation boundaries
  -> RTK Query containers
  -> documentation-only DMETA IR
```

This ordering mattered. A dashboard cannot be cleaned up safely by deleting CSS first. The reusable layer must exist before consumers can move to it. Only then can legacy globals be removed with confidence.

## The visual language was preserved

The project did not need a new visual identity. The existing retro monochrome dashboard language was coherent: black panel headers, thin borders, compact monospace labels, dense tabular information, and sparse use of accent colors. The cleanup preserved that language while changing the ownership model behind it.

The current real Search page still looks like the same product:

![](assets/rag-design-system/rag-real-01-search.png)

The Corpus page still presents a dense operational dashboard:

![](assets/rag-design-system/rag-real-02-corpus.png)

The refactor changed how these pixels are produced. The visual grammar now comes from tokens, primitives, components, and local CSS Modules rather than from a broad global stylesheet.

## The core ownership rule

The most important rule was simple enough to test during every edit:

```text
tokens own values
foundation owns text and accessibility
atoms own basic controls
layout owns structure
molecules own reusable data/display patterns
organisms own feature panels
pages own composition
containers own API behavior and side effects
CSS Modules own local anatomy
```

This rule prevented several common failure modes.

It prevented the core model and DMETA documents from accumulating React-specific details. Web layout concerns do not belong in core model fields. The core model is for archetypes, capabilities, projections, and domain examples. Interaction IR is for visible obligations and actions. Web MDS is for target-specific lowering. React is the final implementation target.

It also prevented CSS Modules from becoming arbitrary replacements for global CSS. A CSS Module is not automatically good architecture. A CSS Module is correct when it owns component anatomy that is not reusable elsewhere. Typography, status tone, panel shell, table structure, and form controls should not be repeatedly redefined inside feature CSS Modules.

The ownership table used during the work was:

| Layer | Owns | Does not own |
| --- | --- | --- |
| `tokens.css` | color, font, border, spacing, semantic aliases | component selectors and feature anatomy |
| foundation | text roles, code text, captions, status text, dividers, hidden text | grids, panels, API behavior |
| atoms | buttons, icon buttons, inputs, selects, checkbox rows, error callouts | page state, data fetching, table rendering |
| layout | panels, stacks, inline groups, dashboard grids, shells, tabs, form rows, scroll regions | domain formatting and API behavior |
| molecules | reusable tables, metadata grids, coverage summaries, preset lists, app navigation | RTK Query hooks and page orchestration |
| organisms | feature panels with DTO-shaped props and callbacks | global layout policy and app-wide state |
| pages | composition of organisms and page-local state | low-level typography and raw CSS globals |
| containers | RTK Query, mutations, navigation events, side effects | presentational styling decisions |

This table became more useful than any single component. It was the test for every proposed extraction.

## Pass 1: documentation and architecture review

The first pass created a ticketed documentation workspace and wrote a long-form review of the RAG web architecture. That review mapped the API handlers, RTK Query services, major React views, global CSS, and the intended DMETA path. It established the initial plan: start with Search as the first vertical slice, extract design-system primitives, add Storybook, and seed a documentation-only IR catalog.

The review also set a constraint that remained important throughout the project: the current scope should not generate scaffolds or validate IR unless explicitly requested. This mattered because it kept the cleanup concrete. The RAG IR files were allowed to document semantics, interactions, and web lowering ideas, but the React cleanup was not blocked on building an executable IR toolchain.

The documentation-only DMETA layer followed this shape:

```text
dmeta-ir/
  core-model/
    archetypes/
    capabilities/
  interactions/
    representations/
    actions/
    elaboration-rules/
  meta-design-systems/
    web/
      widgets/
      lowering-rules.yaml
  instantiations/
```

The important boundary was this:

```text
core model semantics/projections
  -> Interaction IR visible obligations and actions
  -> Web MetaDesignSystem lowering rules
  -> Web widget/page templates
  -> React implementation
```

The cleanup did not collapse these layers. The React design system was built in a way that remains compatible with that chain, but it did not pretend that IR generation was already required.

## Pass 2: tokens, foundation, and layout

The first implementation pass extracted the design-system base.

`web/src/styles/tokens.css` became the source for the retro monochrome palette and role aliases. The token file preserved names such as `--mac-bg`, `--mac-text`, `--mac-border`, `--mac-surface`, `--mac-accent`, and `--mac-accent-2`, while adding RAG font role aliases. This was not a complete enterprise token system. It was a deliberately small set of values sufficient to make the current dashboard consistent.

Foundation primitives were added for the concerns that were previously scattered through global classes:

```text
Text
CodeText
StatusText
Caption
Divider
VisuallyHidden
```

These components own typography roles, status tones, compact captions, code-like identifiers, separators, and accessible hidden text. They deliberately do not own layout.

Layout primitives were added separately:

```text
Panel
Stack
Inline
DashboardGrid
AppShell
ScrollRegion
TabList
FormRow
```

The separation between foundation and layout was not cosmetic. It meant that a component could say, in JSX, whether it is choosing text semantics or choosing structure. For example, a workflow panel can use `Panel` for the shell, `MetadataGrid` for key/value structure, and `Caption` for compact muted labels. Each choice has one responsibility.

The foundation overview Storybook page later made these decisions visible:

![](assets/rag-design-system/rag-story-06-foundation-colors.png)

Storybook was introduced early because a primitive without a story is difficult to review independently. The story is the component's public contract. It shows states, variants, and visual regressions without requiring the full app to be running.

## Pass 3: atoms and basic controls

The next set of repeated patterns were action and form controls.

The first atoms were `Button` and `IconButton`. `Button` replaced global `.btn` and `.btn-primary` usage. `IconButton` replaced compact copy, close, and back controls that previously depended on a `.copy-btn` global. The migration used the same pattern repeatedly:

```text
create atom
add story
export atom
migrate active consumers
scan for old class names
remove global CSS only after scan passes
```

Later, form controls and error callouts were atomized:

```text
TextInput
SelectInput
CheckboxRow
ErrorCallout
```

This removed the global `.input`, `.select`, `.checkbox-row`, and `.error-box` styles. The important detail is that the atom components still accept `className`. Width and placement remain local to the consuming component, while the control's baseline visual contract lives in the atom.

The Search controls story shows the result. The panel is dense, but its controls are now named atoms and layout primitives rather than global classes:

![](assets/rag-design-system/rag-story-crop-02-search-controls.png)

The rule here is precise: an atom owns the appearance and state of the native control, but it does not own the feature's layout. The Search panel still decides that one input is full width and another is narrow. The atom decides the border, background, focus outline, font, and disabled behavior.

## Pass 4: reusable molecules

Once primitives and atoms existed, the cleanup moved to patterns that appeared across multiple feature areas.

The reusable molecules included:

```text
DataTable
MetadataGrid
CoveragePanel
QueryPresetList
AppNav
```

`DataTable` replaced repeated dense table structures. `MetadataGrid` replaced repeated key/value inspector layouts. `CoveragePanel` and `QueryPresetList` captured search-support patterns. `AppNav` moved the top-level navigation out of global `.nav-*` classes and into a storyable molecule.

The AppNav extraction was a small but important endpoint for the global CSS cleanup. Before extraction, `index.css` still contained `.nav-strip`, `.nav-brand`, and `.nav-item`. After extraction, the top-level app used a semantic component:

```tsx
<AppNav
  brand="◉ RAG Eval"
  items={views}
  activeItemId={activeView}
  onItemSelect={setActiveView}
/>
```

The component renders buttons with `aria-current="page"` for the active item. The visual result remained the same:

![](assets/rag-design-system/rag-story-crop-01-appnav.png)

This pass showed an important distinction between molecules and layout primitives. App navigation is not just layout. It has a brand, a set of items, active item semantics, and selection behavior. That makes it a molecule rather than a layout primitive.

## Pass 5: Search as the first vertical slice

Search was the first full vertical slice because it exposes the core RAG workflow: compose a query, retrieve evidence, inspect the selected result, and open source context.

The initial Search view was split into:

```text
SearchControlsPanel
RetrievalResultsPanel
ResultInspectorPanel
SearchWorkbenchPage
```

The panels became organisms. They accept DTO-shaped props and callbacks where possible. The page boundary composes the panels into a dashboard grid. RTK Query hooks and cross-view navigation remain in the container layer where practical.

The Search page now expresses its structure through components:

```text
SearchView container
  -> SearchWorkbenchPage
       -> SearchControlsPanel
       -> RetrievalResultsPanel
       -> ResultInspectorPanel
```

This is the point where the design system started to change the source code's readability. The JSX no longer had to explain every border, header, spacing rule, and table class directly. Those decisions moved into reusable components.

The current real Search page confirms that the visual behavior survived the extraction:

![](assets/rag-design-system/rag-real-01-search.png)

The empty states are still sparse because the dev database used for visual QA contained little data. Sparse data is acceptable. The important visual questions were whether panels aligned, controls retained styling, text remained readable, and the app navigation still worked.

## Pass 6: Corpus cleanup

Corpus required more careful handling than Search because it contained several feature-local widgets with domain-specific behavior:

```text
SourcePanel
DocumentBrowser
DocumentInspector
IdentityBar
ArtifactIdentityBar
ChunkTimelineBar
```

The cleanup did not force every Corpus component into generic molecules. That would have removed useful domain structure. Instead, Corpus widgets stayed in `web/src/components/corpus/` while adopting shared primitives, atoms, layout primitives, and reusable molecules.

The important file-organization rule became:

```text
WidgetName/
  WidgetName.tsx
  WidgetName.module.css
  WidgetName.stories.tsx
  index.ts
```

This rule made feature-local widgets reviewable. A component can remain Corpus-specific and still be part of the design system discipline.

The `ChunkTimelineBar` migration was representative. Its previous `chunk-bar-*` classes lived globally. The refactor moved that anatomy into `ChunkTimelineBar.module.css`, converted chunks into accessible buttons, added stories, and then deleted the global styles. `IdentityBar` and `ArtifactIdentityBar` were refactored through shared primitives and atoms. `DocumentBrowser` adopted `TextInput` and `DataTable`. `DocumentInspector` adopted `TabList`, `MetadataGrid`, `DataTable`, `ErrorCallout`, and local link styling.

The report-ready DocumentInspector story shows a component that is still dense, but now structured:

![](assets/rag-design-system/rag-story-crop-03-document-inspector-overview.png)

The Corpus real page also remained visually intact:

![](assets/rag-design-system/rag-real-02-corpus.png)

One design decision is worth recording: `DocumentInspector` still calls an RTK Query hook for artifacts in one path. That is acceptable for now because the project is mid-transition. The architectural direction is still to separate API-aware containers from storyable presentation where the split is practical.

## Pass 7: Workflow organisms

The Workflows view was the largest feature surface. It contained queue health, workflow lists, summaries, operation graphs, operation groups, selected operation inspectors, result rendering, retry actions, and an intake modal.

The extraction created organisms:

```text
QueueHealthPanel
WorkflowListPanel
WorkflowSummaryPanel
WorkflowOpGraphPanel
WorkflowOpGroupsPanel
WorkflowOpInspectorPanel
WorkflowOpResultPanel
```

Shared formatting logic moved into `workflowFormat.ts`. The container retained workflow fetching, selected workflow state, retry mutation behavior, result fetching, and intake submission. The organisms received data and callbacks.

The failed operation inspector story captures the design-system result:

![](assets/rag-design-system/rag-story-crop-04-workflow-inspector.png)

The failed state uses `ErrorCallout`, `Caption`, `Button`, `MetadataGrid`, and component-local workflow anatomy. The retry behavior remains a callback. This is the desired split: the organism knows how a failed sampled operation is displayed; the container knows how retrying works.

The intake modal was also refactored through `Panel`, `Stack`, `FormRow`, `Caption`, `TextInput`, `SelectInput`, and `Button`. The modal did not become a generic modal system. It became cleaner because its form rows and controls stopped depending on global CSS.

The real Workflows page after the refactor was sparse because no workflows were present, but the layout was coherent:

![](assets/rag-design-system/rag-real-03-workflows.png)

## Pass 8: Pipeline, Embeddings, and Evaluation

After Search, Corpus, and Workflows, the remaining views were smaller but still important.

`EmbeddingsView` was refactored through shared primitives and form atoms. It still acts as a container/view, but the old global form and error classes were removed. It now uses `Panel`, `Stack`, `Inline`, `FormRow`, `TextInput`, `SelectInput`, `ErrorCallout`, `MetadataGrid`, and `DataTable` where appropriate.

The real Embeddings page remained visually stable:

![](assets/rag-design-system/rag-real-05-embeddings.png)

Pipeline received a presentational boundary:

```text
PipelineOverview
PipelinePage
```

The populated Storybook page became a useful report asset because it demonstrates a page-level boundary rather than a tiny atom:

![](assets/rag-design-system/rag-story-05-pipeline-page.png)

Evaluation was originally a placeholder. It received an explicit `EvaluationPage` boundary and Storybook stories. This was a small change, but it followed the same rule: every page boundary should be reviewable independently.

The current real Evaluation page is intentionally simple:

![](assets/rag-design-system/rag-real-06-evaluation.png)

## Pass 9: global CSS deletion

The most visible metric of the cleanup is `web/src/index.css`.

At the beginning, it carried much of the interface. Over the course of the project, entire global families were removed after active consumers were migrated:

```text
.panel*
.data-table*
.status-*
.coverage-*
.fieldset
.text-*
.divider
.meta-*
.tab-*
.stat-*
.progress-*
.op-*
.modal-*
.form-row
.btn
.btn-primary
.copy-btn
.input
.select
.error-box
.checkbox-row
.accent
.truncate
.no-select
.nav-*
```

The deletion rule was always the same:

```bash
rg -n '<legacy-class-or-family>' web/src
# migrate active consumers
rg -n '<legacy-class-or-family>' web/src
# only then delete global CSS
```

False positives had to be reviewed manually. For example, searches for `select` can match `.selected` or `.selectable` in CSS Modules, which are not uses of the global `.select` class.

After the AppNav extraction, `index.css` was reduced to imports, box sizing, body base styles, and scrollbar styling:

```css
@import "tailwindcss";
@import "./styles/tokens.css";

* { box-sizing: border-box; }

body {
  font-family: var(--font-body);
  font-size: 12px;
  line-height: 1.45;
  color: var(--mac-text);
  background: var(--mac-bg);
  margin: 0;
  padding: 0;
  -webkit-font-smoothing: none;
}

::-webkit-scrollbar { ... }
::-webkit-scrollbar-track { ... }
::-webkit-scrollbar-thumb { ... }
```

This is the central CSS outcome. The global stylesheet no longer acts as the component library.

## Pass 10: visual QA and screenshots

After the major refactors, the app was started through `devctl` and visually checked in the browser. This found one unrelated but important launch bug: the devctl plugin allocated a free backend port but did not pass that port to `rag-eval serve`. The backend still tried to bind `127.0.0.1:8772`, which failed when another process already owned that port.

The fix changed the devctl launch command to pass the allocated address explicitly:

```text
rag-eval serve
  --address 127.0.0.1:<allocated-port>
  --db state/rag-eval.db
  --engine-db state/rag-eval-workflows.db
  --log-level debug
```

Once the app started, screenshots were taken for all top-level pages. The visual smoke check found no obvious broken layouts. The only browser console error was a missing favicon request.

Storybook screenshots were captured through `iframe.html?id=...&viewMode=story`, not through the Storybook manager UI. This matters for reports because it excludes Storybook navigation chrome. Element-level screenshots were used where full-page captures had too much whitespace.

The screenshot set became both QA evidence and source material for this article.

## Why the sequence worked

The project succeeded because each pass made a small set of ownership claims and then enforced those claims through migration and deletion.

The sequence was:

```text
1. document the current state
2. define ownership rules
3. extract tokens
4. extract foundation primitives
5. extract layout primitives
6. add Storybook
7. extract molecules
8. extract feature organisms
9. add page boundaries
10. atomize controls
11. remove globals after scans
12. visually verify the real app
```

The work did not begin by inventing a large abstract component model. It began by reading the actual dashboard and asking which obligations were repeated. Repeated text roles became foundation primitives. Repeated panel and grid structure became layout primitives. Repeated controls became atoms. Repeated data displays became molecules. Feature panels became organisms. Page composition became page boundaries.

This bottom-up method also avoided premature generalization. For example, the project deliberately did not add a generic `Box` primitive. A `Box` would have allowed arbitrary style choices to move from CSS into JSX props without clarifying ownership. The absence of `Box` forced each repeated need to find the correct layer.

## The DMETA boundary

The project also clarified how DMETA should relate to this React work.

The RAG `dmeta-ir/` catalog currently documents the Search Workbench domain and interaction structure. It is not used to generate React. This is intentional. The current useful role of RAG IR is to document semantic and interaction obligations:

```text
RetrievalQuery
SourceDocument
EvidenceChunk
SearchWorkbench
submit_query
inspect_evidence
open_source_document
```

The React design system gives those obligations a concrete implementation vocabulary:

```text
SearchWorkbenchPage
SearchControlsPanel
RetrievalResultsPanel
ResultInspectorPanel
Panel
DashboardGrid
DataTable
MetadataGrid
Button
TextInput
```

The important boundary is that Interaction IR owns target-neutral visible obligations. Web MDS can describe target-specific widget choices and coarse layout hints. React prop schemas should not be pushed into core model fields. Detailed React prop contracts only belong in IR if a real tooling consumer appears.

For now, RAG IR remains documentation-only. That decision prevented the project from spending effort on validators and scaffolding before the design-system foundations were stable.

## What changed in the codebase

The final component tree contains the expected design-system layers:

```text
web/src/components/
  atoms/
    Button/
    IconButton/
    TextInput/
    SelectInput/
    CheckboxRow/
    ErrorCallout/
  foundation/
    Text/
    CodeText/
    StatusText/
    Caption/
    Divider/
    VisuallyHidden/
  layout/
    Panel/
    Stack/
    Inline/
    DashboardGrid/
    AppShell/
    ScrollRegion/
    TabList/
    FormRow/
  molecules/
    AppNav/
    DataTable/
    MetadataGrid/
    CoveragePanel/
    QueryPresetList/
  organisms/
    SearchControlsPanel/
    RetrievalResultsPanel/
    ResultInspectorPanel/
    QueueHealthPanel/
    WorkflowListPanel/
    WorkflowSummaryPanel/
    WorkflowOpGraphPanel/
    WorkflowOpGroupsPanel/
    WorkflowOpInspectorPanel/
    WorkflowOpResultPanel/
  pages/
    SearchWorkbenchPage/
    PipelinePage/
    EvaluationPage/
  corpus/
    SourcePanel/
    DocumentBrowser/
    DocumentInspector/
    IdentityBar/
    ArtifactIdentityBar/
    ChunkTimelineBar/
```

There are now 45 Storybook story files under `web/src/components`. That number is not important by itself. What matters is that story coverage exists at every reusable layer: foundation, atoms, layout, molecules, organisms, and some page boundaries.

The remaining incomplete areas are known:

- Corpus, Workflows, Embeddings, and Search can still gain more DTO-shaped page presentation boundaries.
- `DocumentInspector` still has an internal RTK Query artifact fetch path.
- Legacy `retro/*` components need a decision: add stories and fold them into the system, or delete them.
- The missing favicon can be fixed separately.

These are follow-up tasks, not signs that the architecture failed.

## Implementation rules that should survive this project

The following rules are the durable part of the work.

### 1. Do not delete a global class before migrating consumers

A global CSS deletion is safe only after a scan proves active consumers are gone. The order is:

```text
identify class family
create component owner
migrate consumers
run search
review false positives
remove global CSS
run typecheck/build/storybook
```

This rule prevented accidental visual regressions.

### 2. Storybook is not optional for reusable surfaces

Every public primitive, atom, molecule, organism, and page boundary should have a story. The story is where the component's state contract becomes visible.

A component without a story can still be used in the app, but it is not yet a stable design-system component.

### 3. CSS Modules are for anatomy, not for reimplementing primitives

A CSS Module may own local structure such as a workflow graph rail, a chunk timeline row, or a document inspector link. It should not redefine generic panel headers, table cells, status tones, form controls, or typography roles.

### 4. Containers should own side effects

RTK Query hooks, mutations, cross-view navigation events, and polling behavior should stay in containers or page-level runtime components where possible. Storyable organisms should prefer DTO-shaped props and callbacks.

This rule improves testability and Storybook coverage because a panel can be rendered with sample data rather than a live store.

### 5. DMETA should stay at the right abstraction level

Core model files should not carry React props. Interaction IR should describe what must be visible and actionable. Web MDS can lower those obligations into web components. React implements the promoted design system.

Adding validators or scaffolding before there is a tooling consumer creates maintenance cost without improving the dashboard.

## A compact reconstruction algorithm

If this cleanup had to be repeated in another dashboard, the implementation sequence would be:

```text
function build_design_system(app):
    write_current_state_review(app)
    define_layer_ownership()

    extract_tokens_from_global_css()
    add_foundation_primitives()
    add_layout_primitives()
    configure_storybook()

    for repeated_pattern in find_repeated_patterns(app):
        component = create_smallest_named_owner(repeated_pattern)
        add_story(component)
        migrate_consumers(component)
        delete_legacy_css_when_unused()
        run_validation()

    for feature_view in major_views(app):
        split_feature_panels_into_organisms(feature_view)
        keep_api_behavior_in_container(feature_view)
        add_page_boundary_where_stable(feature_view)
        add_stories_for_presentational_boundaries()

    seed_ir_docs_only_if_the_domain_needs_it()
    run_real_browser_visual_qa()
```

This is not a generator. It is a working discipline. The key operation is `create_smallest_named_owner`. It prevents both under-extraction and over-extraction. A repeated button becomes `Button`; it does not become a complete control framework. A repeated metadata layout becomes `MetadataGrid`; it does not become a generic arbitrary grid primitive.

## Final state

The RAG dashboard is now structured enough to extend. A future engineer can add a panel by choosing from existing layers rather than copying global classes. A future report can include Storybook images of components without starting the full backend. A future DMETA pass can refer to concrete React components that already have stable names and stories.

The refactor did not erase the prototype. It translated the useful parts of the prototype into explicit frontend architecture. The dashboard still looks like the RAG Evaluation System. The difference is that its visual and interaction decisions now have addresses in the codebase.

## Source material

Primary project sources:

- `/home/manuel/workspaces/2026-05-27/ttc-design-system/2026-05-27--rag-evaluation-system`
- `ttmp/2026/06/01/RAG-WEB-DESIGN-SYSTEM-REVIEW--rag-evaluation-web-architecture-and-design-system-review/design-doc/01-rag-evaluation-web-architecture-and-design-system-review.md`
- `ttmp/2026/06/01/RAG-WEB-DESIGN-SYSTEM-REVIEW--rag-evaluation-web-architecture-and-design-system-review/design-doc/02-rag-react-design-system-guidelines.md`
- `ttmp/2026/06/01/RAG-WEB-DESIGN-SYSTEM-REVIEW--rag-evaluation-web-architecture-and-design-system-review/analysis/01-rag-design-system-guideline-audit.md`
- `ttmp/2026/06/01/RAG-WEB-DESIGN-SYSTEM-REVIEW--rag-evaluation-web-architecture-and-design-system-review/reference/01-investigation-diary.md`

Representative commits:

```text
4f07074 feat: add RAG web design system foundations
e893396 feat: extract RAG search workbench components
f50181c feat: extract RAG result inspector panel
ada6dfd feat: seed RAG search workbench DMETA IR
5de4155 docs: keep RAG DMETA IR documentation-only
d9c2c70 feat: expand RAG design system primitives
c187c46 feat: adopt RAG design system in corpus views
f5cd822 feat: extract RAG workflow detail panels
302e5c2 feat: extract RAG workflow op inspector
b5c73f5 feat: extract RAG workflow op result panel
7e48c28 feat: refactor RAG embeddings view layout
af207b0 feat: add RAG pipeline page stories
600ce6d docs: add RAG react design system guidelines
1cb51dd docs: audit RAG design system guidelines
2ed581b feat: refactor RAG corpus identity bar
c6dfcbc feat: refactor RAG artifact identity bars
efe6b3e feat: add RAG button atom and timeline stories
0841784 feat: add RAG icon button atom
e09259a feat: add RAG evaluation page story
30f4c66 feat: remove RAG legacy global CSS
2a98180 feat: atomize RAG form controls
826ed52 feat: remove leftover RAG global utilities
e6d7c24 feat: extract RAG app navigation
a595420 test: capture RAG visual smoke screenshots
```

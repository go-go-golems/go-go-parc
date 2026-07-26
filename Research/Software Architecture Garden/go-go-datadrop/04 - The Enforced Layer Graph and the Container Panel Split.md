---
title: go-go-datadrop — The Enforced Layer Graph and the Container/Panel Split
aliases:
  - enforced import layer graph
  - container panel split react
  - atomic design enforced by test
tags:
  - architecture-garden
  - go-go-datadrop
  - design-system
  - layering
  - react
status: active
type: architecture-pattern-study
pattern_maturity: established
created: 2026-07-26
analyzed: 2026-07-26
repository: /home/manuel/code/wesen/go-go-golems/go-go-datadrop
repository_commit: ef996430f8a3a63e6812d961eb2bae5d631272a0
analysis_commit: 69b82257f75a4ca236d985629dc298844128409f
source_tickets:
  - DATADROP-6
related_files:
  - ui/test/layers.test.ts
  - ui/test/render-path.test.ts
  - ui/src/appkit/registry.ts
  - ui/src/pbui/types.ts
  - ui/src/apps/useTable.ts
  - ui/src/apps/TableApp/TableApp.tsx
  - ui/src/components/organisms/TablePanel/TablePanel.tsx
  - ui/GUIDELINES.md
---

# The Enforced Layer Graph and the Container/Panel Split

**Maturity: Established.**

## 1. What problem is being solved

A design system with six component layers and nine source layers has a dependency graph whether or not anyone writes it down. Left unwritten, it acquires cycles: a component reaches for a store selector, an organism imports an application, and eventually two modules import each other and the bundler resolves it in an order nobody chose.

The second, subtler problem is that a component which fetches cannot be looked at. Storybook can render a component that takes data; it cannot easily render one that requires a live server, a Redux provider and a populated cache.

## 2. The concrete shape

Nine source layers plus six component layers, declared as an allow-list:

```text
model      ──> (nothing)
api        ──> model
export     ──> model
fixtures   ──> model
pbui       ──> model, foundation
store      ──> model, api, pbui
appkit     ──> model, pbui, store
tour       ──> model, pbui, store, appkit, api, fixtures

foundation ──> (nothing)
layout     ──> foundation
atoms      ──> foundation, layout, pbui, model
molecules  ──> atoms, layout, foundation, pbui, model, store
organisms  ──> molecules, atoms, layout, foundation, pbui, model, store, api, appkit
apps       ──> organisms … appkit          (pages is absent, deliberately)
pages      ──> everything above, plus apps and tour
```

`ui/test/layers.test.ts` walks every import in `src/` and fails on a violation, naming the file and the offending specifier.

The container/panel split is the component-level half:

```tsx
// apps/TableApp/TableApp.tsx — the container. One hook.
function TableApp({ leafId, docId }: AppProps) {
  const { doc, pipeline, loading } = useDocPipeline(docId);
  return (
    <>
      <DocBar leafId={leafId} docId={docId} />
      <TablePanel pipeline={pipeline} docId={doc?.id ?? null} loading={loading} />
    </>
  );
}
```

Thirty-one lines of container over a panel that takes three props. The rule stated in the guidelines:

> The container keeps the hooks and the fetches. The panel takes data and callbacks.

## 3. How it is woven into the rest of the application

Three details make the graph hold rather than merely exist.

**`model` imports nothing, and that is the load-bearing row.** The pipeline evaluator, the plot builder and the table types are pure — nothing under `model/` imports React. That is what lets the entire grammar of graphics be exercised with no DOM, which is why the plot tests are fast enough to run on every save. Every other decision in the browser tier is downstream of this one.

**`pbui` may import `foundation` but not `atoms`.** An exception granted deliberately: `foundation` is the bottom of the component stack — design tokens made usable in React, importing nothing itself — so depending on it cannot create a cycle, and the alternative is the protocol re-implementing the type scale. What it may *not* import is `atoms` and above, because descriptors hold no components.

**`appkit` exists because of one edge.** It holds the application-descriptor interface, a `Map`, and three functions over it — the contract applications register against, not an application. While it sat under `apps/`, one organism importing `appFor` was the *only* reason the graph carried an `organisms → apps` edge, and that edge is why `apps → organisms` had to be forbidden to keep the pair acyclic. The forbidden edge made the standard pattern illegal: presentational panels in `organisms` with applications as thin containers above them. Moving forty-nine lines removed the edge, and the pattern became available.

That is the most instructive event in this study. **A layering rule was blocking the architecture the team wanted, and the cause was a single import in a single file.**

## 4. Why it works

**A story is possible exactly when a component takes data.** The payoff is measurable rather than aesthetic. The nine applications converted during DATADROP-6 went from 1 135 lines of container to 554, and produced 54 new story exports covering states that previously required a running server and a specific sequence of clicks — a unary derive operator that hides one of its inputs, a channel mapped to a column a later step removed, a trace long enough to have dropped its own beginning.

**The graph makes a violation cheap to diagnose.** The test names the file and the specifier. A cycle discovered by a bundler at build time does not.

**The allow-list model catches new directories.** This is the property that decides an implementation question below: `layers.test.ts` includes a test called *"every source directory sits in the graph"*, so a directory added to `src/` without a declared row fails. A deny-list would silently permit it.

## 5. What goes wrong

**A panel can be given a lookup that is expensive.** The most serious failure in this project's history came through this seam. The presentation environment exposed a table lookup that evaluates the whole pipeline, and a helper called from a *render body* used it:

```tsx
// components/atoms/FieldChip/FieldChip.tsx
const { field, type } = resolveField(ref, pbui.environment);
```

A table header draws one chip per column. Measured over the fixture grown to each row budget, warmed:

```text
                    13x evaluate   13x schemaAfter    ratio
  2 000 rows              5.2 ms        0.032 ms        161x
 10 000 rows             30.6 ms        0.080 ms        381x
 50 000 rows            144.0 ms        0.023 ms      6 329x
```

144 ms is roughly nine dropped frames, paid on every keystroke in the pipeline editor, every divider drag and every arriving event on a live stream. The 50 000-row budget is one of four buttons in the interface.

The repair split the environment along the line between **schema** and **rows**: `fieldsFor` for the render path, `tableFor` for menu handlers. The decisive observation was that the resolver never touches a row, and the engine already computed the post-pipeline schema without evaluating anything.

Two things are worth extracting from the repair. First, the resolver stopped returning the table, because its callers used two of three returned fields — *returning a value nobody reads is what makes a cheap call look expensive, which is how the next person reaches for a cache instead of a schema*. Second, memoisation was the obvious alternative and was rejected: a cache turning 144 ms into 12 ms is worse than a call that never costs a microsecond, it leaves the cost one invalidation away, and the invalidating event is a specification edit — exactly when the editor re-renders hardest.

**The reasoning failure that let it ship is the more transferable lesson.** The implementation diary had recorded *"runs once per menu open, so this is very probably fine."* That is true of descriptors and false of this helper, which is not one. The reasoning classified the function by the category of its neighbours rather than by enumerating its call sites, and one `grep` would have settled it.

**The guidelines document under-reports its own enforcement.** `ui/GUIDELINES.md §10` lists five tests under the heading *"what the tests actually guarantee"*. There are thirteen. Recorded in [[Research/Software Architecture Garden/go-go-datadrop/08 - Architecture Debt and Patterns Not to Repeat|document 08]].

## 6. When should another project reuse it

The container/panel split applies to any project with a component library and a state store, and its cost is close to zero.

The **enforced** graph is worth it once a project has more than about six source directories and more than one person. Below that the graph fits in a reviewer's head. Above it, the graph is real whether it is written down or not, and the only question is whether it is discovered by a test or by a bundler.

The implementation choice matters and this project's answer is worth copying: **the graph is a whitelist walked by a test, not a deny-list in a linter.** A deny-list expresses "organisms may not import apps" and silently permits a directory nobody has classified. A whitelist expresses "organisms may import exactly these nine" and fails on anything new. During this analysis the alternative was verified to work — a linter rule can catch relative cross-layer specifiers — and rejected for exactly this reason, plus the risk of two declarations of one graph disagreeing.

## 7. What should become ecosystem guidance

1. **A dependency graph should be a whitelist and should fail on an unclassified directory.** The unclassified-directory test is the part everyone omits.
2. **A cheap call should not look expensive.** Do not return values callers do not read.
3. **Classify a function by its call sites, not by its neighbours.** The check costs one `grep`.

All three are developed in [[Research/Software Architecture Garden/go-go-datadrop/09 - Candidate Ecosystem Guidelines|document 09]]. The first engages `rag-evaluation-system`'s Candidate 3 and its recorded debt about broad package barrels.

## Related notes

- [[Research/Software Architecture Garden/go-go-datadrop/01 - Project Architecture Overview]]
- [[Research/Software Architecture Garden/go-go-datadrop/05 - Structural Guard Tests as a Genre]]
- [[Research/Software Architecture Garden/go-go-datadrop/08 - Architecture Debt and Patterns Not to Repeat]]
- [[PROJECT REPORT - go-go-datadrop v0.7 - What Makes a Defect Findable]]

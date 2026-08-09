# P08 Link Taxonomy

This catalogue prevents a common architecture error: calling every connection a link and then implementing all links with one propagation mechanism. The recommended kind is a hypothesis about semantics, not a judgment based only on payload type.

## Classification criteria

- **Identity reference:** both endpoints are projections of one logical resource. There is no representation conversion.
- **Directed:** one endpoint derives another; no inverse is promised.
- **Asymmetric lens:** one model is treated as source and the other as a view, with a partial or total `put`.
- **Symmetric consistency:** neither side is universally primary; a relation and two repair directions are needed.
- **Delta consistency:** edit provenance is semantically significant.
- **Replicated merge:** independently evolving replicas require a merge algebra, causality, or conflict policy.
- **No link:** the relationship should remain an explicit action, query, or workflow step.

## Catalogue

| ID | Left | Right | Recommendation | Confidence | Risk | Disputed alternatives |
|---|---|---|---|---|---|---|
| T01 | `chart.primaryDocument` | `pipeline.primaryDocument` | `identity-reference` | settled | low | `symmetric-consistency` |
| T02 | `table.primaryDocument` | `chart.primaryDocument` | `identity-reference` | provisional | low | `directed` |
| T03 | `pipeline.outputDocument` | `chart.primaryDocument` | `directed` | settled | medium | `no-link` |
| T04 | `sourceBrowser.selectedDocument` | `table.primaryDocument` | `directed` | disputed | low | `identity-reference` |
| T05 | `table.rowSelection` | `pipeline.filter` | `delta-consistency` | settled | high | `symmetric-consistency`, `asymmetric-lens`, `directed` |
| T06 | `chart.brushSelection` | `pipeline.filter` | `symmetric-consistency` | provisional | high | `delta-consistency`, `directed` |
| T07 | `chart.zoomDomain` | `pipeline.rangeFilter` | `asymmetric-lens` | provisional | medium | `directed`, `symmetric-consistency` |
| T08 | `table.columnOrder` | `chart.encodingOrder` | `symmetric-consistency` | disputed | medium | `no-link` |
| T09 | `queryText` | `queryAst` | `asymmetric-lens` | settled | high | `symmetric-consistency` |
| T10 | `structuredForm` | `jsonConfig` | `asymmetric-lens` | settled | high | `symmetric-consistency` |
| T11 | `fieldOccurrence` | `chart.xChannel` | `directed` | settled | low | `no-link` |
| T12 | `pipeline.stageSelection` | `inspector.focus` | `directed` | provisional | low | `identity-reference` |
| T13 | `workspace.timeRange` | `chart.xDomain` | `symmetric-consistency` | disputed | medium | `asymmetric-lens`, `identity-reference` |
| T14 | `user.locale` | `formattedAxisLabels` | `directed` | settled | low | `no-link` |
| T15 | `sortSpecification` | `tableHeaderIndicators` | `asymmetric-lens` | provisional | medium | `symmetric-consistency` |
| T16 | `task.status` | `kanban.columnMembership` | `identity-reference` | disputed | low | `asymmetric-lens` |
| T17 | `rowSelectionModel` | `renderedRowHighlights` | `directed` | settled | low | `identity-reference` |
| T18 | `chart.colorScale` | `legendEditor` | `asymmetric-lens` | provisional | medium | `symmetric-consistency` |
| T19 | `twoCollaborativeTextEditors` | `sharedDocument` | `replicated-merge` | settled | high | `symmetric-consistency` |
| T20 | `replicaA.bindingTopology` | `replicaB.bindingTopology` | `replicated-merge` | settled | high | `no-link` |
| T21 | `authorityState` | `offeredAffordances` | `directed` | settled | high | `no-link` |
| T22 | `savedViewDefinition` | `currentAdHocWorkspaceState` | `symmetric-consistency` | disputed | high | `asymmetric-lens`, `no-link` |

## Case notes

### T01 - `chart.primaryDocument` and `pipeline.primaryDocument`

**Recommended:** `identity-reference`. **Confidence:** settled. **Information risk:** low.

Both ports claim the same current-document role and should project onto one binding resource when their full contracts agree.

### T02 - `table.primaryDocument` and `chart.primaryDocument`

**Recommended:** `identity-reference`. **Confidence:** provisional. **Information risk:** low.

Identity is appropriate only when both views are intended to follow one subject; a dashboard may instead deliberately drive one direction.

### T03 - `pipeline.outputDocument` and `chart.primaryDocument`

**Recommended:** `directed`. **Confidence:** settled. **Information risk:** medium.

A derived output may drive a chart, but edits to the chart document cannot reconstruct or mutate the pipeline output.

### T04 - `sourceBrowser.selectedDocument` and `table.primaryDocument`

**Recommended:** `directed`. **Confidence:** disputed. **Information risk:** low.

Browser focus commonly drives a table. Identity would make table navigation unexpectedly rewrite browser focus.

### T05 - `table.rowSelection` and `pipeline.filter`

**Recommended:** `delta-consistency`. **Confidence:** settled. **Information risk:** high.

The representations differ, inverse mappings can be ambiguous, and preserving unrelated filter clauses requires edit-aware repair.

### T06 - `chart.brushSelection` and `pipeline.filter`

**Recommended:** `symmetric-consistency`. **Confidence:** provisional. **Information risk:** high.

A brush denotes a region while a filter may contain richer constraints; both-direction repair is useful but partial.

### T07 - `chart.zoomDomain` and `pipeline.rangeFilter`

**Recommended:** `asymmetric-lens`. **Confidence:** provisional. **Information risk:** medium.

The chart domain is a view of a richer range filter; put can preserve hidden source structure when the range fragment is recognized.

### T08 - `table.columnOrder` and `chart.encodingOrder`

**Recommended:** `symmetric-consistency`. **Confidence:** disputed. **Information risk:** medium.

Both are orders over overlapping fields, but missing and derived columns make total equality inappropriate.

### T09 - `queryText` and `queryAst`

**Recommended:** `asymmetric-lens`. **Confidence:** settled. **Information risk:** high.

Parsing is partial and pretty-printing is many-to-one. Source formatting and comments require explicit preservation policy.

### T10 - `structuredForm` and `jsonConfig`

**Recommended:** `asymmetric-lens`. **Confidence:** settled. **Information risk:** high.

The form exposes a supported fragment of a larger configuration. Unknown fields must survive put or appear as loss.

### T11 - `fieldOccurrence` and `chart.xChannel`

**Recommended:** `directed`. **Confidence:** settled. **Information risk:** low.

Selecting a field can assign a channel; changing the channel does not identify one originating occurrence.

### T12 - `pipeline.stageSelection` and `inspector.focus`

**Recommended:** `directed`. **Confidence:** provisional. **Information risk:** low.

Inspector focus is usually derived from stage selection and may also focus non-stage subjects.

### T13 - `workspace.timeRange` and `chart.xDomain`

**Recommended:** `symmetric-consistency`. **Confidence:** disputed. **Information risk:** medium.

A workspace range may include timezone, calendar, and inclusivity semantics absent from a numeric chart domain.

### T14 - `user.locale` and `formattedAxisLabels`

**Recommended:** `directed`. **Confidence:** settled. **Information risk:** low.

Formatting is derivation. Labels cannot reconstruct locale or formatting policy uniquely.

### T15 - `sortSpecification` and `tableHeaderIndicators`

**Recommended:** `asymmetric-lens`. **Confidence:** provisional. **Information risk:** medium.

Header indicators expose a view of a richer multi-key sort and can update one fragment while preserving hidden keys.

### T16 - `task.status` and `kanban.columnMembership`

**Recommended:** `identity-reference`. **Confidence:** disputed. **Information risk:** low.

Identity is defensible if column membership is merely the status field. Swimlanes or filters turn it into a view instead.

### T17 - `rowSelectionModel` and `renderedRowHighlights`

**Recommended:** `directed`. **Confidence:** settled. **Information risk:** low.

Highlights are rendered occurrences and should be projections of semantic selection, not an independent writable model.

### T18 - `chart.colorScale` and `legendEditor`

**Recommended:** `asymmetric-lens`. **Confidence:** provisional. **Information risk:** medium.

The legend edits a visible fragment; scale interpolation and hidden defaults remain in the source.

### T19 - `twoCollaborativeTextEditors` and `sharedDocument`

**Recommended:** `replicated-merge`. **Confidence:** settled. **Information risk:** high.

Concurrent edits require causal or operation-based merge semantics. Calling this a lens hides replication assumptions.

### T20 - `replicaA.bindingTopology` and `replicaB.bindingTopology`

**Recommended:** `replicated-merge`. **Confidence:** settled. **Information risk:** high.

Offline topology edits need a replicated data type or explicit coordination, which is outside ordinary lens laws.

### T21 - `authorityState` and `offeredAffordances`

**Recommended:** `directed`. **Confidence:** settled. **Information risk:** high.

Affordances are derived observations. Clicking an affordance cannot mutate authority by inverse synchronization.

### T22 - `savedViewDefinition` and `currentAdHocWorkspaceState`

**Recommended:** `symmetric-consistency`. **Confidence:** disputed. **Information risk:** high.

Saving and loading can be bidirectional, but ephemeral state and defaults make the consistency boundary a product decision.

## Disputed cases

A disputed classification is preserved rather than normalized away. It identifies a composition question that must be resolved with domain semantics.

- **T04**: `sourceBrowser.selectedDocument` to `table.primaryDocument` is provisionally `directed` but also plausibly `identity-reference`. The host must decide whether there is one resource, a preferred source, a repair relation, or no stable link at all.
- **T08**: `table.columnOrder` to `chart.encodingOrder` is provisionally `symmetric-consistency` but also plausibly `no-link`. The host must decide whether there is one resource, a preferred source, a repair relation, or no stable link at all.
- **T13**: `workspace.timeRange` to `chart.xDomain` is provisionally `symmetric-consistency` but also plausibly `asymmetric-lens`, `identity-reference`. The host must decide whether there is one resource, a preferred source, a repair relation, or no stable link at all.
- **T16**: `task.status` to `kanban.columnMembership` is provisionally `identity-reference` but also plausibly `asymmetric-lens`. The host must decide whether there is one resource, a preferred source, a repair relation, or no stable link at all.
- **T22**: `savedViewDefinition` to `currentAdHocWorkspaceState` is provisionally `symmetric-consistency` but also plausibly `asymmetric-lens`, `no-link`. The host must decide whether there is one resource, a preferred source, a repair relation, or no stable link at all.

## Integration rule

The taxonomy should be consulted before policy selection, but it is not a runtime dispatcher. A host must bind a concrete pair of typed endpoint contracts to a versioned policy. Two endpoints carrying the same JSON shape may still have different authority, temporal, and information semantics.


---
title: "pbui Action-Selection Kernel and the Post-Legacy Unification"
aliases:
  - pbui Action Kernel Deep Dive
  - pbui PBUI-ACTIONS-3 Report
  - Post-Legacy Kernel Unification Report
  - PBUI-ACTIONS-3
tags:
  - project
  - pbui
  - frontend
  - typescript
  - action-selection
  - presentation-based-ui
  - go
  - architecture
status: active
type: project
created: 2026-08-27
repo: /home/manuel/workspaces/2026-08-24/use-optkit/pbui
source_tickets:
  - PBUI-ACTIONS-2
  - PBUI-ACTIONS-3
follows:
  - "[[PROJECT REPORT - PBUI Action Selection Kernel - From Descriptor Callbacks to a Pure Resolver]]"
related_docs:
  - /home/manuel/workspaces/2026-08-24/use-optkit/pbui/ttmp/2026/08/26/PBUI-ACTIONS-2--type-directed-action-selection-engine-in-the-pbui-package/design-doc/01-intern-guide-implementing-the-action-selection-kernel-in-current-pbui.md
  - /home/manuel/workspaces/2026-08-24/use-optkit/pbui/ttmp/2026/08/26/PBUI-ACTIONS-2--type-directed-action-selection-engine-in-the-pbui-package/reference/01-diary.md
  - /home/manuel/workspaces/2026-08-24/use-optkit/pbui/ttmp/2026/08/26/PBUI-ACTIONS-3--post-legacy-simplification-and-kernel-unification-backlog/analysis/01-the-backlog-what-no-legacy-affords-and-what-pulls-each-item.md
  - /home/manuel/workspaces/2026-08-24/use-optkit/pbui/ttmp/2026/08/26/PBUI-ACTIONS-3--post-legacy-simplification-and-kernel-unification-backlog/reference/01-diary.md
---

# pbui Action-Selection Kernel and the Post-Legacy Unification

> [!info] Related report
> This is the follow-up to [[PROJECT REPORT - PBUI Action Selection Kernel - From Descriptor Callbacks to a Pure Resolver]], which documents PBUI-ACTIONS-2: building the kernel across eight phases and shipping it as pbui 0.7.0 behind a deprecation window. This report covers PBUI-ACTIONS-3 — deleting that window — and the chat-layer work that followed.

This report explains the state of the pbui presentation library after the action-selection kernel landed and after the legacy compatibility surfaces that buffered its arrival were deleted. It is written as a technical article, not a changelog. The goal is to make the architecture legible: why a pure, type-directed action-selection kernel replaced the exact-type descriptor lookup, what the kernel's load-bearing contracts are, what the "no backwards compatibility" ruling unlocked, and how the follow-on work — the primary invocation, the perform envelope, the generated vocabulary, and the chat reference adapter — made the kernel the only selection engine in the system.

The source repository is `/home/manuel/workspaces/2026-08-24/use-optkit/pbui`, on branch `task/use-optkit`. The work spans two docmgr tickets: PBUI-ACTIONS-2, which built the kernel across eight phases and shipped it as pbui 0.7.0 behind a deprecation window, and PBUI-ACTIONS-3, which deleted that window and shipped the kernel-only API as pbui 0.8.0 and 0.9.0. A final set of commits extended the chat package with a reference adapter and two coarse-type vocabulary fixes.

> [!summary]
> The central design move is that action discovery is separated from representation: a descriptor owns only `label`/`describe`/`tone`, and a pure type-directed kernel — a validated nominal type graph, a four-state availability model, a 16-step resolver, and fresh revalidation at perform time — decides which actions exist for any reference.
>
> The central implementation move is the "one live selection engine" invariant: during migration a legacy descriptor family ran *inside* the kernel so the swap was reviewable as test equivalence, and the post-legacy phase deleted that family so the kernel is now the only path.
>
> The central correctness move is that provenance and vocabulary are derived from the same registry the menus use: the perform envelope is built from the fresh re-resolved action, and the agent-facing vocabulary is generated from the type graph and contributions, so a rule rename is the vocabulary bump and "menu and agent disagree about what exists" stops being a representable state.

## The project in one paragraph

pbui is a presentation-based React UI library. A product declares its object world as a `PresentationValues` interface, and a **reference** — `{type, value}` where `type` is a key of that interface — is the unit the library renders, menus, accepts, and performs verbs against. Before this work, a presentation's descriptor owned both its representation and its actions: `ObjectMenu` called `registry.actionsFor(reference, environment)`, one exact-type lookup with an empty-array fallback, at render time, and `perform` delegated whatever verb was baked into the menu row at render time with no revalidation. That single seam blocked five things the products needed: actions contributed by several independent packages, actions inherited from abstract types, an explanation of why an action is absent or disabled, deterministic handling of conflicting contributions, and a guarantee that the verb a user clicked was computed from current state. This work replaces that seam with a small pure action-selection kernel and then deletes every mechanism that coexisted with it during the migration.

## Why the kernel exists

The exact descriptor callback conflated four distinct ownership models into one function. Representation has one owner per concrete type: the descriptor that knows how to label and describe a `tile` belongs to the package that defines `tile`. Actions have many independent contributors: a shared workbench package contributes `tile.close`, a product contributes its own `tile.export`, and a live agent library contributes actions that did not exist when the descriptor map closed. Inherited behavior belongs to semantic type relationships: every inspectable type shares one Inspect rule, and that rule should be declared once against an abstract node, not copied across fifteen concrete types. And live generated actions appear after the descriptor map closed: the sandbox mints agent-created actions from a program library while the menu is open.

The descriptor callback cannot express any of these. It returns one array from one function, so the only composition available is array concatenation, and the only identity available is array position. The four consumers in the repository each worked around this in a different way, and every workaround reinstated array-order semantics and unstable identity.

- **pbui-workbench** added an `extra?(tile)` seam to the shared tile descriptor so products could append rows. The merge owner was the shared package, which is the wrong place for a product's actions.
- **datalab-ui** manufactured ids as `` `${ptype}:${index}:${label}` ``. A label edit or an inserted row changed identity, so the ids were unusable for overrides, traces, or revalidation.
- **pbui-sandbox** wrapped the entire registry in `withGeneratedActions` and appended live agent actions when `actionsFor` ran. The wrapper, not the data, was the problem.
- **pbui-chat demo** reused the unstable-id adapter pattern and depended on the sandbox wrapper.

The perform path had a separate defect. `perform: (verb) => { setMenu(null); return onPerform(verb); }` delegated the raw verb from the menu row. That verb was computed at render time from whatever the state was then. Between render and click the state could change — a more-specific rule could load, the row could become unavailable, the action could stop resolving — and the library would delegate the stale verb anyway. Authorization lived in product routers and chat gateways, but the library never even checked that the action it delegated still existed.

The kernel replaces the seam with a pure resolver that reads an immutable, query-local snapshot, and it replaces the stale perform with fresh revalidation. The rest of the library — the `Presentation` gesture and accessibility layer, focus and Escape infrastructure, serializable verbs, product verb routers — stays as it is.

## The kernel's load-bearing contracts

The kernel lives under `src/presentation/actions/` and contains no React imports. Every module is testable in Node. The contracts below are the ones that shape every decision that follows.

### Five identities

The kernel distinguishes five notions of identity that the exact lookup collapsed into one.

| Identity | Meaning | Example |
| --- | --- | --- |
| Runtime type ID | A node in the nominal type graph; concrete or abstract | `tile`, `object` |
| Rule ID | One declaration by one package; globally unique | `workbench.tile.close` |
| Family ID + instance key → candidate ID | A dynamic contribution source and its stable per-expansion keys | `datalab.datum.filters/keep:region` |
| Action ID | The conceptual operation several rules compete to implement | `presentation.open` |
| Menu `group`/`order` | Presentation metadata; never a tie-breaker | `group: "NAVIGATE", order: 5` |

The rule-versus-action distinction is what makes overrides expressible. Several rules can implement the same action ID; they compete, and exactly one wins. Different action IDs accumulate. Array index and label are forbidden as identity, because both change when a row is inserted or a label is edited.

### A nominal type graph

The graph is nominal, not structural, and validated at registration: duplicate types, unknown parents, and cycles all throw. Multiple inheritance is allowed, and specificity is BFS shortest distance. The one subtle contract is that inheritance never coerces payloads. An inherited rule for the abstract type `node` receives the *original* concrete reference, not a narrowed one. The API makes this visible with two factories: `actions.exact(type, …)` narrows the payload to that type, while `actions.inherited(typeNode, …)` takes the generic reference.

### A revisioned selection snapshot

The resolver never reads live stores. The product supplies `snapshotFor(query, environment)` returning `{revision, scopes, modes, capabilities, product}` — immutable, query-local facts plus a revision that advances whenever any resolution-relevant fact changes. The revision is drift telemetry, not authorization; perform always re-resolves. datalab's environment already separates cheap schema access from expensive table evaluation, and the snapshot must preserve that cost boundary: render-adjacent paths get schema-only facts, and table evaluation runs only where rows are genuinely needed.

### The four-state availability model

Availability is not a boolean. It is a four-state type, and the distinction between the two absent states is a policy-safety mechanism.

```ts
type Availability =
  | { kind: "available" }
  | { kind: "unavailable"; because: string; code?: string }
  | { kind: "inapplicable"; because: "not-relevant" | "not-applicable" }
  | { kind: "hidden"; because: "not-disclosed" | "policy" };
```

`unavailable` is visible and disabled, carrying one actionable reason. `inapplicable` is absent and permits fallback: an irrelevant `restore` on a live file must not block a different fallback. `hidden` is absent and suppresses fallback: a `secret-file.open` hidden by policy must keep suppressing a generic `document.open`, and an `unavailable` specific rule also suppresses generic fallback so a protected-file rule cannot be bypassed by falling back to generic `delete`. This quartet is the part of the design most worth internalizing before reading the resolver.

### The resolver ladder

Within one action ID, the precedence ladder is deterministic: smallest type distance, then nearest active scope, then highest explicit priority, and ambiguity is returned as data with nothing selected. Registration order, import order, array order, labels, and menu order are never tie-breakers. A permutation test enforces this. Binding runs only for the uniquely selected *available* candidate; earlier binding is wasted work and produces misleading audit values. The trace is emitted by the same branches that select, never by a second debug resolver, so an empty menu and a trace that proves suppression come from one pass.

### Fresh revalidation at perform

```ts
async function performAction(stale) {
  const fresh = actions.resolve(stale.query, snapshotFor(stale.query, environment));
  const current = fresh.actions.find((a) => a.action === stale.action);
  if (!current)                                  return refused("action-no-longer-resolves");
  if (current.candidateId !== stale.candidateId) return refused("action-implementation-changed");
  if (current.status.kind !== "available")       return refused("action-no-longer-available", …);
  await onPerform(current.verb);
  return { kind: "delegated" };
}
```

Both the action ID and the candidate ID must match. A newly loaded, more-specific rule must not silently change semantics after the user chose a row. `delegated` means pbui crossed its boundary, not that the domain accepted the mutation; authorization stays in product routers and the chat gateway.

## The migration: one live selection engine

PBUI-ACTIONS-2 shipped the kernel across eight phases (P0 through P7) without forcing any product to change. The mechanism that made that possible was Amendment B: an automatic legacy adapter. When a product did not pass `actions` and `snapshotFor` to `createPbui`, the provider constructed an internal registry around `legacyDescriptorFamily`, which routed the descriptor `actions()` callbacks through the same resolver with a trivial snapshot. There was never a second selection engine. The legacy path was a family *inside* the kernel, not a bypass.

This made the engine swap reviewable as test equivalence. Each consumer phase froze its menus as golden fixtures before migration, migrated its descriptors to kernel rules, and reviewed the diff filtered to non-id and non-label lines. The only accepted semantic diff class was `verb: undefined` on disabled rows — the kernel refuses to bind verbs for unavailable actions, so disabled rows no longer carry a verb. Three full migrations ran this protocol (datalab's first four types, datalab's remaining eleven types, the chat demo), and each produced zero label diffs.

The phase ladder ended with P7, which deleted `withGeneratedActions` from the sandbox, made `createTileDescriptor` representation-only, and reduced the datalab descriptor interface to representation with a `never` tombstone on the removed `actions` callback. At that point no in-repository product used the legacy path. The decision left open by P7 was whether to delete the generic compatibility surface outright or deprecate it for out-of-repo consumers still on 0.6.x shapes. PBUI-ACTIONS-2 chose deprecation and shipped pbui 0.7.0.

## Phase A: the no-legacy ruling and the deletions

PBUI-ACTIONS-3 opened with a ruling from the user: pbui has no backwards-compatibility obligations. In-repo and out-of-repo consumers — datalab-ui, the pbui-chat demo, agentlogic, turboproof — are adapted rather than shimmed. This resolved the delete-versus-deprecate adjudication from PBUI-ACTIONS-2 in favor of **delete**. It also resolved a class of API-shape questions that a deprecation window would have frozen: `actions` and `snapshotFor` become required in `createPbui`, and the descriptor drops its `Verb` generic, because nothing obligates the library to keep carrying them as optional.

Phase A shipped as pbui 0.8.0 in one commit. It deleted:

- The descriptor `actions()` callback and the `PresentationAction` row shape.
- The `actionsFor` exact lookup.
- The `conversions` ordered-array option and `PresentationConversion`.
- The automatic legacy engine: `legacyDescriptorFamily`, `LegacyFacts`, and `legacy.ts` with its test.
- The 0.4.0 `onActivate`/`activateDoc` tombstone props.

`createPbui` now requires `actions` and `snapshotFor`; the type system enforces them, so the runtime guards that checked for their absence are deleted. Acceptance always resolves through the typed translator path with `translators ?? []`, so every product gets graph-subtype satisfaction whether or not it declares translators. `PresentationDescriptorRegistry` is the only registry name. The result is that the diff to `src/presentation/types.ts` removes 116 lines and the diff to `src/presentation/createPbui.tsx` removes the entire fallback construction block — the `createActionRegistry` call, the trivial snapshot, the `acceptedReference` function, and the construction-time guards.

```ts
// Before: the provider built an engine when the product supplied none.
const actionEngine: ActionRegistry<…> =
  actions ??
  (createActionRegistry({ graph: createPresentationTypeGraph([]), scopes: ["global"],
    contributions: [legacyDescriptorFamily({ id: "legacy.descriptor-actions", descriptors: registry })]
  }) as unknown as ActionRegistry<Values, ProductFacts, Verb>);
const snapshotOf = snapshotFor ?? ((_query, environment) => ({ … }) as …);

// After: the product supplies both; there is no fallback.
const actionEngine = actions;
const snapshotOf = snapshotFor;
```

The deletion surfaced zero behavioral regressions. The only test-count change was the deleted legacy suite versus the new primary invocation suite.

## The primary invocation

Phase A added one new capability alongside the deletions: the primary invocation. The backlog had assumed that `activate` was a descriptor-side legacy mechanism. Reading the code showed otherwise: since 0.4.0, `activate` has been a per-instance JSX prop whose job is host-owned clicks — selection and expansion owned by the surrounding organism, which a type-scoped kernel rule cannot express. A4 therefore became "delete the tombstone props, add kernel primary resolution as the default, keep `activate` as the instance override."

`ActionMetadata.primary` marks an action as its subject's primary. `Presentation` resolves the click with `invocation: "primary"` and performs the action only when it is the **unique** available primary for that subject. Zero available primaries or several available primaries fall back to opening the menu.

```ts
const primaryFor = (): ResolvedAction<Values, Verb> | null => {
  const resolution = pbui.resolve({ subject: reference, invocation: "primary" });
  const primaries = resolution.actions.filter(
    (action) => action.primary && action.status.kind === "available",
  );
  return primaries.length === 1 ? (primaries[0] ?? null) : null;
};
```

Two decisions in this function matter. First, the unique-or-menu rule. Performing the highest-priority primary would reintroduce exactly the guessing the kernel exists to kill: it would make registration order, priority, or some other tie-breaker decide which of two equally valid actions the user gets from a single click. Keeping ambiguity user-visible — two primaries open the menu, the user picks — preserves the kernel's invariant that nothing is selected when declarations do not decide. A test pins this: two available primaries open the menu and `onPerform` is never called.

Second, the cost boundary. `primaryFor` resolves against the kernel, and a naive implementation would compute it per render. A grid of presentations would then run a kernel resolution per cell on every render, putting menu-time work on the render path of every datalab table. The symptom would be invisible until a large table rendered. The implementation avoids this by making `primaryFor` lazy: it is evaluated on hover, focus, click, and Enter only. The render path does no resolution. The `clickDoc` string is likewise computed by a function called on demand, not a value built per render.

`activate` stays as the instance-level override and wins over the kernel primary when present. The click handler checks `activate` first, then `primaryFor`, then opens the menu. The keyboard path mirrors this: Enter runs `activate` if present, then `primaryFor`, then opens the menu. A primary click goes through `performAction`, so it gets fresh revalidation like every other kernel action — the verb is the fresh one, never the stale render-time one.

## Phase B: the perform envelope

Phase B shipped as pbui 0.9.0 in two commits, both pulled directly by the OPTKIT-024 task list. The first gave every delegated verb its provenance natively.

Before Phase B, `onPerform` received only the verb. A product that wanted a verb log or a trace record reconstructed provenance from the verb's own fields. The OPTKIT trace record shape `{seq, actor, verb, target, outcome}` had to be assembled by hand, and it could drift from what the kernel actually resolved. Phase B introduces a `PerformEnvelope`:

```ts
export interface PerformEnvelope<Values extends PresentationValues> {
  invocation: ActionInvocation | "direct";
  action?: ActionId;
  candidateId?: CandidateId;
  subject?: PresentationReference<Values>;
  actor?: string;
}
```

Three properties of the envelope shape the design.

The envelope is built from the **fresh** resolution, not the stale one. `evaluateFresh`'s proceed arm now carries the fresh `ResolvedAction`, and the menu and primary envelopes are built from it. This is the same reason the verb is fresh: the provenance records post-revalidation truth, so a verb log entry cannot claim an action that no longer resolves.

`invocation: "direct"` marks chrome-owned delegation. Tile chrome buttons and product toolbars call `pbui.perform(verb)` with verbs built at click time from live props. Those calls have no resolved action behind them — the verb is constructed deliberately, because the tile and the menu must not drift into two different flows. The envelope for a direct call carries only `invocation` and `actor`; `action`, `candidateId`, and `subject` are absent there and only there. `direct` is a new literal on the envelope union, deliberately not in `ActionInvocation`, because it is not a resolution invocation.

`actor` is the Provider's `actor` prop, threaded verbatim. It is principal attribution for multi-seat products — "human", "agent:reviewer", whatever the product's seats are called — and it is absent when the Provider declares one undifferentiated seat. Attribution is not authorization. Routers and gateways stay the security boundary; the envelope records who acted, not who may act.

The signature change broke no consumer. TypeScript's variance does the adaptation work: adding a parameter to a callback *type* is non-breaking for implementers. A single-parameter router is assignable to the two-parameter type, so all six workspace packages passed unchanged. The breakage is only for callers that spread arguments, which is why two existing `toHaveBeenCalledWith(verb)` assertions had to be updated to expect the envelope explicitly — expected, and listed in the backlog as such.

```ts
// Chrome-owned delegation: no resolved action stands behind the verb.
perform: (verb) => {
  setMenu(null);
  return onPerform(verb, { invocation: "direct", ...(actor !== undefined ? { actor } : {}) });
},
// Menu/primary: the envelope is built from the FRESH resolution.
await onPerform(decision.verb, {
  invocation: decision.action.query.invocation,
  action: decision.action.action,
  candidateId: decision.action.candidateId,
  subject: decision.action.query.subject,
  ...(actor !== undefined ? { actor } : {}),
});
```

## Phase B: the generated vocabulary

The second item Phase B shipped stops the agent-facing vocabulary from being a thing a product could hand-maintain into a lie. Products used to keep a parallel "what exists" module for their agent seat. That module could drift from the registry: a rule could be renamed in the kernel while the vocabulary still named the old action, and "menu and agent disagree about what exists" was a representable state. Phase B generates the vocabulary from the type graph and the contributions.

```ts
export function vocabularyOf<Values, ProductFacts, Verb>(
  graph: PresentationTypeGraph,
  contributions: readonly ActionContribution<Values, ProductFacts, Verb>[],
  version: string | number,
): ActionVocabulary {
  const types = graph.types().map((type): VocabularyTypeEntry => ({
    type,
    abstract: graph.isAbstract(type),
    parents: graph.ancestors(type).filter((a) => a.distance === 1).map((a) => a.type),
  }));
  const actions = contributions.map((contribution): VocabularyActionEntry => { /* … */ });
  return { version, types, actions };
}
```

`registry.vocabulary()` calls this with the registry's own graph and contributions, so renaming a rule *is* the vocabulary bump. The export is the static shape only: every field is JSON-serializable, so a build step can write it to disk and a golden test can pin it. The vocabulary test pins the serialized shape byte for byte through `JSON.parse(JSON.stringify(...))`, asserts that a dynamic label yields no label, asserts that renaming a rule changes exactly the id, and asserts that the vocabulary and `listReachable` agree over every type.

What the vocabulary deliberately omits is as important as what it carries. Three fields are absent by design, and the docstring pins them so the export never grows a fabricating field.

- **Verbs** are absent. Binding needs a live snapshot and a subject value; agents get verbs by resolving, not from the vocabulary.
- **Dynamic labels** are absent. A label declared as a function is context-dependent by construction; the entry carries no label rather than a lie. The test asserts that an inherited rule with a label function has no `label` key.
- **Family instances** are absent. Families expand per snapshot. The vocabulary names the family and its subject; instances exist only at resolution time.

The vocabulary is documentation, not authorization. An entry's presence says a rule is declared, not that any principal may perform it.

## The chat reference adapter

The final set of commits, shipped as pbui-chat 0.3.0, decouple the wire reference format from the product's presentation value. The chat package has always used an identity convention: the presentation value *is* the wire reference. `toPresentationReference` wraps a wire reference as the value, and `fromPresentationReference` unwraps it. That convention breaks for products whose `Values` predate it — structured values with composite identity, like the rag-ttc workbench, where a `case` is identified by `{campaignId, caseId}` and the wire id is a composite key.

The fix is a `ReferenceAdapter<Values>` codec, plugged in once at `createPbuiChat({ referenceAdapter })`.

```ts
export interface ReferenceAdapter<Values extends PresentationValues = PresentationValues> {
  toProduct(reference: Reference): PresentationReference<Values>;
  fromProduct(reference: PresentationReference<Values>): Reference;
}

export function identityReferenceAdapter<Values>(): ReferenceAdapter<Values> {
  return {
    toProduct: (reference) => toPresentationReference<Values>(reference),
    fromProduct: (reference) => fromPresentationReference(reference),
  };
}
```

The identity adapter is the default and round-trips exactly, so nothing changes for convention-following products. A structured-values product supplies its own codec: `toProduct` turns a wire reference into the reference its descriptors and rules actually read (the structured value, not `.value.value`), and `fromProduct` mints the wire id going the other way. The adapter is threaded through the chat context as `chat.refs`, and every chat-layer crossing goes through it — `RefPresentation`, the `Composer` mention picker, the `acceptTool`, the `FormChild` field picker, and the `labelFor` lookup.

Before, each of those surfaces called `toPresentationReference` or `fromPresentationReference` directly. A structured-values product would have had to shim every surface, or rewrite its presentation layer to fit the identity convention. After, it plugs in one codec. The test for the adapter demonstrates both shapes: the identity adapter round-trips a wire reference, and a structured-values codec round-trips a `case` through its composite id scheme, with the product's rules reading the structured value directly.

## The coarse-type vocabulary fixes

The same set of commits fixed two coarse-type behaviors in the chat vocabulary, with the TypeScript deriver and the Go validator kept in parity.

The `object` field type now accepts arrays. The zod schema deriver coarsens non-reference arrays — a string list, for example — to `object`, because they are structured JSON values rather than scalar fields. The validator previously rejected anything that was not a `map`, which meant it refused fields the schema itself declared. The fix accepts both maps and arrays as `object`, and a scalar still fails. The Go side mirrors this exactly: `checkCoarseType` accepts `map[string]any` or `[]any` for `object`.

A new `any` field type was added for product-typed fields. Some verb fields carry values whose meaning is defined entirely by the receiving domain — a compile loop, a document validator — and the vocabulary's job is to name the field, not to validate its contents. The `any` type accepts anything and defers validation to the domain. Both the TypeScript `validate.ts` and the Go `vocabulary.go` accept the literal, and `ValidateVerb` in Go allows it in its known-types switch.

```ts
// validate.ts
case "object":
  return isRecord(value) || Array.isArray(value) ? null : `expected object, got ${goType(value)}`;
case "any":
  return null; // Product-typed: the receiving domain validates; the vocabulary names it.
```

The Go validator and the TypeScript validator mirror each other by design. The Go side is the authority at the agent boundary; the TypeScript side is the authority in the browser. A field that passes one must pass the other, and the `validate.test.ts` suite asserts the exact error strings Go would produce, so drift between the two becomes a test failure.

## What was tricky

Three things in this work warrant a second pair of eyes or a careful read.

**The module cycle the construction guard exposed.** During PBUI-ACTIONS-2 P6, two rounds of module-cycle whack-a-mole appeared in the chat demo. The first was `actions.ts → chat.ts → runtime.tsx → actions.ts`, which made `createPbui` see a partial actions module. The new construction guard threw where the old closure-based code had silently tolerated the cycle. The second was deeper: the conversation and chatEvent descriptors imported `chat` for labels and `describe`, so the registry itself closed the same loop. The fix was a dependency-light `conversationFacts` slot that `chat.ts` registers its registry into at startup; descriptors and the snapshot builder read through it, and an unregistered slot resolves to the honest "not in this browser's list" state. The lesson is general: the old `createPbui` survived cycles because it only closed over its options. Any create-time validation converts a silently-tolerated partial-module evaluation into a startup crash. That is a feature — the cycle was real — but it means construction guards and module graphs have to be reviewed together.

**The lazy primary resolution cost boundary.** The primary invocation had to resolve against the kernel without putting a resolution per rendered presentation. The trap is that the defect is invisible until a large grid renders, because a small story or test never exercises the render path at scale. Making `primaryFor` lazy — evaluated on hover, focus, click, and Enter only — keeps the render path free of resolution. The `clickDoc` builder is a function, not a value, for the same reason.

**The ambiguity reporting simplification.** The resolver reports `incomparable-types` when tied candidates declare different types, and `equal-priority` otherwise. `equal-specificity` and `equal-scope` are currently never emitted, though the union suggests finer reporting. The cases are semantically covered — ambiguity is returned as data and nothing is selected — but the simplification is documented in the diary so it is a decision rather than an oversight, to be refined if a real inheritance case demands it.

## Open questions and next steps

Phase C of the backlog has no puller and waits until something needs it. Six items are recorded but unscheduled: a single predicate registry shared by rules and translators (translator `when` currently evaluates against an empty map), refusal surfacing so products can toast fresh-revalidation refusals, a `defineProduct` builder that collapses the generic-threading sites into one, a snapshot helper with derived revision, per-type order overrides on inherited rules, and a dev-mode introspection surface. Each is annotated with the consumer that would pull it; an item with no puller waits.

Two near-term follow-ups are pulled by the OPTKIT track. The OPTKIT-024 agent seat consumes both Phase B items: agent seats are snapshots without the seal capability, and the vocabulary build step with its golden is the agent's picture of what exists. Out-of-repo consumers — agentlogic and turboproof — adapt to pbui 0.8.0 with the golden-fence method the migration already ran three times: freeze their menus as golden fixtures, migrate descriptors to rules, and review the diff filtered to non-id and non-label lines.

The one semantic change a reviewer should confirm is the acceptance-path widening. Before Phase A, products without translators got exact-type matching only; after, they also get graph-subtype satisfaction. For every in-repo product the graphs make this a no-op or an upgrade, but it is a semantic widening worth a glance. The other is the envelope's wholesale `subject` reference: if a product logs envelopes verbatim, subject values with sensitive fields land in the log. Products own redaction at the router; the envelope records the subject, it does not sanitize it.

The work leaves the kernel as the single selection engine, with provenance and vocabulary derived from the same source the menus use, and the chat layer decoupled from one reference format. The claim that held through the migration — "adding a variable or action touches one declaration" — is now true for every consumer in the repository, because the old path is gone.

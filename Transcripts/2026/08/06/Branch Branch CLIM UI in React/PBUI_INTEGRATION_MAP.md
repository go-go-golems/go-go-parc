# PBUI integration map

This note maps the textbook architecture onto the supplied repository. It is intentionally staged: each stage leaves the application in a coherent state and can be the final stopping point.

## 1. Existing semantic seams

The supplied code already has the correct initial boundaries.

| Current file | Existing responsibility | Textbook concept |
|---|---|---|
| `src/presentation/types.ts` | tagged `PresentationReference`, descriptors, accept request, conversions | atomic references and the minimal input context |
| `src/presentation/registry.ts` | descriptor lookup, labels, descriptions, actions, tones | atomic declaration registry |
| `src/presentation/createPbui.tsx` | provider-local acceptance, conversion attempts, menu state, presentation wrapper | runtime matcher facade and React adapter |
| `packages/datalab-ui/src/pbui/types.ts` | product value vocabulary and narrow environment | application universe and environment snapshot |
| `packages/datalab-ui/src/pbui/registry.ts` | one descriptor per product presentation type | product atom declarations |
| `packages/datalab-ui/src/pbui/runtime.tsx` | product PBUI instance and `cat → field` conversion | product registry assembly and translator declaration |

The existing design also makes two sound choices worth preserving:

1. descriptors do not contain React components;
2. the product environment is deliberately narrower than the Redux store.

The textbook kernel should therefore remain underneath React and should consume a coherent, read-only environment interface.

## 2. Recommended target

For this repository, implement **Profile B** first and add selected Profile C features afterward.

Profile B immediately solves the concrete problems that motivated the work:

- semantic identity across different occurrences and representations;
- prepared arbitrary selection predicates;
- operation-scoped caching and commit revalidation;
- typed direct translators;
- context-contributed actions;
- linked document-subject cells.

The first Profile C additions should be:

- nominal subtypes;
- static capabilities;
- union and intersection;
- base-relative difference;
- evidence-producing matching.

BDD normalization, recursive types, unrestricted negation, and mechanized proofs should remain separate research branches until application expressions demonstrate a real need.

## 3. Stage 1 — Add semantic identity and revision

Extend `PresentationDescriptor` in `src/presentation/types.ts`:

```ts
export interface SemanticIdentity {
  readonly namespace: string;
  readonly key: string | number;
}

export interface PresentationDescriptor<Value, Environment, Verb> {
  label(value: Value, environment: Environment): ReactNode;
  describe?(value: Value, environment: Environment): unknown;
  actions?(value: Value, environment: Environment): readonly PresentationAction<Verb>[];
  identity?(
    value: Value,
    environment: Environment,
  ): SemanticIdentity | undefined;
  revision?(
    value: Value,
    environment: Environment,
  ): string | number | undefined;
  tone?: PresentationTone;
}
```

Add to `PresentationRegistry`:

```ts
identityFor(reference, environment): SemanticIdentity | undefined;
revisionFor(reference, environment): string | number | undefined;
sameObject(left, right, environment): boolean;
```

Product declarations should use namespaced identities:

```ts
field: {
  identity: field => ({
    namespace: "field",
    key: JSON.stringify([field.docId, field.name]),
  }),
}

doc: {
  identity: doc => ({ namespace: "document", key: doc.id }),
}
```

Alternate presentation roles may intentionally share a namespace. A future `docId` atom and `doc` atom should both identify the same document namespace.

### Tests

- separately allocated references for one domain entity compare equal;
- unrelated types with the same raw ID do not compare equal;
- immutable revision changes preserve identity but change revision;
- fallback object identity does not collapse structurally equal rows.

### Safe stopping point

Identity alone is useful for coordinated highlighting, watchlists, selection memory, and cache keys. No algebra is required.

## 4. Stage 2 — Replace `types + filter` internally with a selector

Keep the public compatibility form, but compile it to:

```ts
export interface PresentationSelector<Values, Environment> {
  readonly id?: string;
  readonly types: PresentationType<Values> | readonly PresentationType<Values>[];
  readonly includeSubtypes?: boolean;
  readonly cache?: "none" | "occurrence" | "identity";
  readonly description?: string;
  readonly where?: (
    reference: PresentationReference<Values>,
    context: SelectorContext<Environment>,
  ) => boolean;
  readonly prepare?: (
    context: SelectorPreparationContext<Environment>,
  ) => (
    reference: PresentationReference<Values>,
    context: SelectorContext<Environment>,
  ) => boolean;
}
```

Change `AcceptRequest` to accept either form:

```ts
interface AcceptRequest<Values, Environment> {
  readonly prompt: string;
  readonly selector?: PresentationSelector<Values, Environment>;
  readonly types?: PresentationType<Values> | readonly PresentationType<Values>[];
  readonly filter?: (reference: PresentationReference<Values>) => boolean;
}
```

At `accept` start:

1. compile the selector once;
2. execute `prepare` once against the provider's coherent environment snapshot;
3. install an operation-local memo table;
4. evaluate mounted presentations through the compiled selector;
5. re-evaluate the clicked occurrence before resolution.

Do not place the memo table in the global registry. Selector validity belongs to one input-context lifetime.

### Product example

```ts
const selectableField = selector("field", {
  id: "visible-field",
  cache: "identity",
  prepare: ({ environment }) => {
    const allowed = new Set(
      environment.fieldsFor(environment.activeDocId).map(field => field.name),
    );
    return reference =>
      reference.type === "field" && allowed.has(reference.value.name);
  },
});
```

### Safe stopping point

Prepared selectors deliver most of the requested lambda flexibility without requiring set-theoretic type expressions.

## 5. Stage 3 — Introduce a registry snapshot

The current registry is already immutable in ordinary use, but make the lifecycle explicit:

```text
RegistryBuilder
    ↓ validate and freeze
RegistrySnapshot
    ↓ compile selectors and methods
Runtime matcher
```

Suggested modules:

```text
src/presentation/
  algebra.ts
  builder.ts
  registry.ts
  matcher.ts
  selectors.ts
  translators.ts
  actions.ts
  evidence.ts
  createPbui.tsx
```

`freeze()` should perform all setup-time validation:

- duplicate IDs;
- unknown names;
- subtype cycles;
- action-table cycles;
- translator endpoint validation;
- precomputed nominal closure;
- source and method indexes;
- registry version/hash creation.

An active input context retains the snapshot with which it began. Plugin changes build a new snapshot instead of mutating the current one under pointer interaction.

## 6. Stage 4 — Add nominal subtypes and static capabilities

Add a representation-safe declaration surface:

```ts
builder.declareSubtype(Project, Entity);
builder.addCapability("inspectable");
builder.implementStatic(Entity, Inspectable);
```

The runtime relation is transitive. The TypeScript signature should require the subtype representation to be assignable to the supertype representation.

Use subtyping only for direct substitutability. Keep `cat → field` as a translator because it constructs a different representation.

Capabilities should represent orthogonal semantic affordances:

```text
inspectable
editable
document-backed
linkable-subject
watchable
```

They prevent nominal names such as:

```text
editable-inspectable-document-backed-field
```

### Product candidates

- `field <: entity`
- `doc <: entity`
- `tile <: workspace-object`
- `field implements inspectable`
- `doc implements inspectable`
- `tile implements document-backed` when the tile's application exposes a primary document role

Start with static capabilities. Add dynamic capabilities only where the predicate represents a changing proposition rather than permission enforcement.

## 7. Stage 5 — Add the small algebra

Use the restricted grammar:

```text
τ ::= atom(a)
    | capability(c)
    | τ ∨ τ
    | τ ∧ τ
    | τ \ τ
    | refine(p, args, τ)
```

Prefer base-relative difference over unrestricted global complement in the public API:

```ts
const ActiveProject = difference(Project, Archived);
```

The base makes the intended universe explicit and behaves better under plugins.

Legacy requests compile as follows:

```text
types: [field, cat]
    ↦ field ∨ cat

filter: lambda
    ↦ ephemeral(lambda, field ∨ cat)
```

Keep string tags as atom identifiers. Atom-handle wrappers can improve TypeScript inference without changing persisted representation.

## 8. Stage 6 — Make matching proof-relevant

Replace the internal result:

```ts
PresentationReference | undefined
```

with:

```ts
type MatchResult =
  | { ok: true; match: Match }
  | { ok: false; failure: MatchFailure };
```

A `Match` should retain:

- source occurrence reference;
- accepted reference;
- requested type expression;
- membership evidence;
- translator path;
- registry version;
- environment epoch;
- object identity and revision;
- refinement dependency fingerprints.

The ordinary `accept` API may continue returning the accepted reference. Expose evidence through diagnostics and an advanced overload.

This change supports:

- explanation panels;
- stale-result detection;
- auditable translator selection;
- action execution against the exact accepted occurrence;
- property tests against a simple reference interpreter.

## 9. Stage 7 — Replace anonymous conversions with translators

The current conversion array loses source/target metadata and ordering semantics. Replace it with definitions:

```ts
builder.addTranslator({
  id: "category/to-field",
  from: Cat,
  to: Field,
  cost: 1,
  preservesIdentity: false,
  applicable: cat => cat.field !== undefined,
  translate: cat =>
    cat.field
      ? { docId: cat.docId, name: cat.field }
      : undefined,
});
```

Begin with direct translation only. Add path search only after there are genuine multi-step use cases.

When path search is added:

- costs must be nonnegative;
- depth and state budgets are mandatory;
- equal best paths must be diagnosed or explicitly preferred;
- cycles use semantic visited-state keys;
- the result records every edge.

Do not let translators perform hidden mutation. Asynchronous loading should be explicit in metadata and cancellation-aware.

## 10. Stage 8 — Move cross-cutting actions to multimethods

Keep descriptor-local actions for intrinsic, exact-type defaults. Add generic action methods for contextual and inherited behavior:

```ts
builder.addMethod({
  id: "inspect-any-inspectable",
  generic: "object-menu-actions",
  subject: Inspectable,
  invoke: ({ subject }) => ({
    id: "inspect",
    label: "Inspect",
    verb: inspectVerb(subject.accepted),
  }),
});
```

Dispatch signatures can later add context and arguments:

```text
[subject type, command context, gesture type, argument types...]
```

Order methods by semantic specificity. Use numeric priority only after specificity when incomparable methods require an explicit policy. Report unresolved ambiguity during development rather than silently depending on registration order.

## 11. Stage 9 — Add linked document-subject cells

Do not model chart/pipeline synchronization through presentation subtyping. It is a state-identity relation.

Give each logical view an optional binding ID:

```ts
interface AppView {
  readonly id: ViewId;
  readonly appId: AppId;
  readonly documents: Readonly<Record<string, DocId>>;
  readonly documentBindingId?: string;
}
```

Interpret a missing ID as a private binding whose identity is the view ID.

Reducers:

```ts
linkViewDocuments({ sourceViewId, targetViewId });
setViewDocument({ viewId, role, docId });
unlinkViewDocuments({ viewId });
```

Invariant:

```text
views with the same effective binding ID have identical document-role maps
```

Test that link, document update, unlink, import, and conflict resolution preserve the invariant.

Use PBUI itself to choose a link target:

```text
begin input context for document-backed tile
    ↓
click another chart or pipeline tile
    ↓
link the two logical views' subject bindings
```

The presentation system selects the target; the layout reducer owns durable linkage.

## 12. Compatibility and migration

Preserve these source forms during migration:

```ts
accept({ types: "field", filter, prompt });
createPbui({ conversions: [...] });
```

Compile them into new internals and mark them as compatibility APIs. Product teams can adopt identity, selectors, links, capabilities, and algebra independently.

A useful release sequence is:

1. identity/revision with no behavior change;
2. selector compiler behind legacy requests;
3. linked subjects;
4. named translators behind legacy conversions;
5. nominal subtypes and capabilities;
6. algebraic expressions;
7. evidence and multimethods;
8. optional path search and advanced decision procedures.

## 13. Verification plan

### Unit laws

- subtype reflexivity and transitivity;
- smart-constructor identities;
- matcher soundness against a direct denotational interpreter;
- identity equivalence laws under descriptor assumptions;
- translation result endpoint correctness;
- unique-maximal dispatch determinism;
- input-context at-most-once settlement;
- link-group coherence preservation.

### Property tests

Generate small finite registries and references. Compare the optimized matcher with a deliberately simple set interpreter. Generate random subtype DAGs and verify closure against graph reachability.

### UI tests

- acceptable occurrences receive keyboard and pointer affordances;
- the clicked occurrence, not a cached equivalent occurrence, supplies the final payload;
- environment changes trigger commitment revalidation;
- Escape aborts only the owning input context;
- object menus announce ambiguity and disabled reasons;
- chart and pipeline document selectors remain synchronized after linking;
- unlink preserves the current document while ending future synchronization.

### Persistence tests

- unknown atom/refinement/translator names fail with diagnostics;
- registry-version migrations are explicit;
- runtime binding IDs are regenerated when importing portable bundles;
- shared-binding equivalence classes survive export/import;
- remote protocols either preserve binding IDs or explicitly document that they do not.

## 14. Final recommendation

Implement the semantic kernel as a pure package and keep `createPbui.tsx` as an adapter. Do not make React rendering the owner of type meaning, identity, translation, or dispatch. Conversely, do not force ordinary local widget behavior through the semantic kernel.

The repository's most valuable next steps are identity, prepared selectors, and linked subjects. The set-theoretic algebra and evidence model should be introduced after those foundations are stable, because they then formalize real relations already present in the product rather than creating abstractions in search of use cases.

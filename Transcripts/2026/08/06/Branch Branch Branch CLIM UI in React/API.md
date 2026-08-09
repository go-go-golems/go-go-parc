# P06 API reference

## Semantic layers

The implementation intentionally exposes different APIs for different semantic layers:

1. **Contract construction** — declare typed local port occurrences.
2. **Semantic compilation** — compute the finite quotient relation.
3. **Persistent planning** — assign external binding identities and lineage.
4. **Runtime interpretation** — allocate one shared cell per binding class.
5. **Registry operations** — perform transactional topology edits.
6. **Research adapter** — invoke the subsystem over JSON Lines.

Union-find is confined to layer 2. Its representatives are not exported as binding IDs.

## Contracts and port occurrences

```ts
import { component, portContract } from "./dist/index.js";

interface DocumentRef {
  readonly sort: "document";
  readonly key: string;
}

const primaryDocument = portContract<DocumentRef>({
  contractId: "primary-document/1",
  semanticTag: "primary-document",
  payloadSort: "document",
  mode: "read-write",
  authorityDomain: "workspace-1",
  multiplicity: "one",
  updateAlgebra: "replace",
  lifetime: "workspace",
});

const chart = component("chart-1");
const chartDocument = chart.port("document", primaryDocument);
```

A `PortRef<T>` is a local occurrence. The key `chart-1.document` is an address, not a binding identity.

### Identity compatibility

```ts
import { checkIdentityCompatibility } from "./dist/index.js";

const judgment = checkIdentityCompatibility(chartDocument, pipelineDocument);
if (!judgment.ok) {
  console.table(judgment.mismatches);
}
```

Identity compatibility requires equality of:

- `semanticTag`;
- `payloadSort`;
- `mode`;
- `authorityDomain`;
- `multiplicity`;
- `updateAlgebra`;
- `lifetime`.

`contractId` is a declaration label. It is intentionally not accepted as a proof that two contracts have equal meaning, and it is not required to be textually equal when the semantic fields coincide.

## Reference and optimized compilers

```ts
import { compileReference, compileOptimized } from "./dist/index.js";

const input = {
  ports: [chartDocument, pipelineDocument],
  links: [{
    linkId: "link-chart-pipeline",
    left: chartDocument,
    right: pipelineDocument,
    mode: "identity" as const,
  }],
};

const reference = compileReference(input);
const optimized = compileOptimized(input);

console.assert(reference.signature === optimized.signature);
```

Both return a `SemanticPlan` containing:

- canonical classes;
- a projection from port keys to semantic class keys;
- preserved link declarations and provenance;
- a normalized signature independent of insertion order;
- diagnostics.

The reference compiler computes graph connected components by traversal. The optimized compiler computes the same equivalence closure using union-find and then discards representatives before canonicalization.

## Registry

```ts
import { PortBindingResolverRegistry } from "./dist/index.js";

const registry = new PortBindingResolverRegistry({
  engine: "optimized",
  verifyOptimizedAgainstReference: true,
});

registry
  .declare(chartDocument, { sort: "document", key: "doc-a" })
  .declare(pipelineDocument, { sort: "document", key: "doc-b" })
  .compile();
```

### `checkLink(left, right)`

Returns a typed compatibility judgment without mutating the registry.

### `identify(left, right, options)`

```ts
registry.identify(chartDocument, pipelineDocument, {
  linkId: "link-chart-pipeline",
  mergePolicy: {
    kind: "prefer-left",
    left: chartDocument,
  },
  provenance: {
    actor: "analyst",
    reason: "compare one document in chart and pipeline",
    logicalTime: "local:17",
  },
});
```

The merge policy is required because the old classes may contain unequal values. The quotient relation does not choose the initial value of the merged runtime resource.

Supported merge policies:

```ts
{ kind: "require-equal" }
{ kind: "preserve-winner" }
{ kind: "prefer-left", left: PortAddress }
{ kind: "prefer-right", right: PortAddress }
{ kind: "user-choice", value: unknown }
```

The operation compiles and allocates a candidate plan first. It commits only if validation and allocation succeed.

### `unlink(linkId, options)`

```ts
registry.unlink("link-chart-pipeline", {
  policy: { kind: "history-restore" },
});
```

Supported unlink policies:

```ts
{ kind: "copy-current" }
{ kind: "reset" }
{ kind: "history-restore" }
{ kind: "user-choice", values: Record<bindingId, unknown> }
```

A split has no canonical initialization. Omitting a policy is an error.

### `removePort(port, options)`

Removes the occurrence and every incident identity-link declaration, recompiles the quotient, and applies the supplied split policy to newly created classes. Surviving nonempty classes remain valid.

### Runtime projections

```ts
const chartProjection = registry.projection(chartDocument);
const pipelineProjection = registry.projection(pipelineDocument);

console.assert(chartProjection.bindingId === pipelineProjection.bindingId);
console.assert(chartProjection.resourceId === pipelineProjection.resourceId);

pipelineProjection.set({ sort: "document", key: "doc-z" });
console.assert(chartProjection.get().key === "doc-z");
```

A projection supplies:

```ts
interface PortProjection<T> {
  readonly port: PortRef<T>;
  readonly bindingId: string;
  readonly resourceId: string;
  get(): T;
  set(value: T): void;
  subscribe(listener: (value: T, revision: number) => void): () => void;
}
```

Read-only, write-only, source, and sink modes are enforced by projection methods. Payload-sort validators run on initialization and writes.

### Explanation and provenance

```ts
const explanation = registry.explain([
  chartDocument,
  pipelineDocument,
]);
```

The explanation contains:

- requested ports;
- their binding class and resource if shared;
- projection snapshots;
- a link-declaration path between each pair;
- lineage and preserved link IDs;
- a deterministic textual summary.

### Finite factorization witness

```ts
const witness = registry.factor({
  "chart-1.document": "document-widget",
  "pipeline-1.document": "document-widget",
});

witness.valueForPort(chartDocument); // "document-widget"
```

`factor` checks that the supplied port-level interpretation is constant on each binding class. If so, it constructs `valuesByBinding` and verifies the commuting triangle. If not, it raises `interpretation-does-not-respect-links`.

This is a runtime finite-set witness, not a proof assistant theorem. The corresponding Lean quotient factorization appears in `proofs/Main.lean`.

## Fluent builder

```ts
import { bindings } from "./dist/index.js";

const compiled = bindings({ engine: "optimized" })
  .declare(chartDocument, { sort: "document", key: "doc-a" })
  .declare(pipelineDocument, { sort: "document", key: "doc-b" })
  .identify(chartDocument, pipelineDocument, {
    linkId: "link-chart-pipeline",
    mergePolicy: { kind: "prefer-left", left: chartDocument },
  })
  .compile();

compiled.bindingOf(chartDocument);
compiled.projection(chartDocument);
compiled.allocate(({ bindingId, members, projection }) => ({
  bindingId,
  members,
  initialValue: projection.get(),
}));
```

The builder is an ergonomic facade. The registry remains the complete dynamic API.

## JSONL research adapter

Start the process:

```bash
./scripts/reproduce --adapter
```

Send one request per line:

```json
{"protocol":"pbui-research/0.1","requestId":"r1","kind":"control.hello","payload":{"deterministic":true,"seed":17}}
```

Supported kinds:

- `control.hello`
- `control.reset`
- `control.snapshot`
- `control.shutdown`
- `bindings.check-link`
- `bindings.compile`
- `bindings.edit`
- `bindings.explain`
- `bindings.allocate`
- `bindings.factor`

Out-of-scope transformed links and replica operations return `status: "unsupported"`; they are not silently interpreted as identity links.

## Typed failures

Representative error codes include:

- `unknown-port`
- `duplicate-port`
- `duplicate-link-id`
- `incompatible-identity-link`
- `merge-value-conflict`
- `explicit-unlink-policy-required`
- `invalid-initial-value`
- `invalid-write`
- `not-readable`
- `not-writable`
- `interpretation-does-not-respect-links`
- `compiler-disagreement`

Callers should branch on `BindingOperationError.code`, not error-message text.

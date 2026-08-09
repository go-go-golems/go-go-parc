# P08 - Bidirectional Links and Consistency Restoration

This project is a self-contained research artifact for PBUI project P08. It studies links between UI components whose endpoint values are related but are not necessarily identical.

The implementation keeps six mechanisms distinct:

1. **identity references**, where endpoints genuinely share one mutable resource;
2. **directed derivations**, where a value flows in one direction and no inverse is promised;
3. **partial asymmetric lenses**, with `get` and a partial or conflicting `put`;
4. **symmetric consistency policies**, defined by a relation and two repair directions;
5. **delta-aware repair**, which carries edit intent and provenance;
6. **replicated merge**, which is classified but deliberately left to P12.

The central claim is not that every pair of UI models can be synchronized. It is that partiality, ambiguity, information loss, scheduling, and authority to choose a repair should be explicit values in the API.

## Quick start

The repository includes compiled JavaScript, so the reference semantics and the dependency-free browser laboratory can be used without installing packages.

```bash
# Run the complete compiled verification path.
npm run verify:compiled

# Start the browser laboratory.
npm run demo
# Open http://127.0.0.1:4178/
```

To rebuild from TypeScript, use Node 22 and TypeScript 5.8.3:

```bash
npm run verify
```

The toolchain and deterministic seed are recorded in `toolchain.json`.

## Interactive laboratory

The browser laboratory places four workbench components in a tile shell:

- a source browser;
- a chart with a document port and brush-selection port;
- a table with a document port and row-selection port;
- a pipeline with a document port and filter-expression port.

The right-hand laboratory panel exposes policy selection, forward and backward repair, repair evidence, law results, feedback simulations, and the 22-case link taxonomy.

![P08 laboratory](docs/demo-screenshot.png)

Suggested first session:

1. Press **link** on `chart.document`, then choose `pipeline.document`. Changing either document selector now writes through one `IdentityCell`.
2. Press **link** on `table.selection`, then choose `pipeline.filter`.
3. Select `station A + B` in the pipeline and run backward repair. The result is a typed conflict with ranked, consistency-preserving row selections rather than a guessed inverse.
4. Compare `directed replacement`, `partial asymmetric lens`, `symmetric repair`, and `delta repair` while adding and removing table rows.
5. Run the law harness. Fourteen law obligations pass and the seeded incorrect toggle design yields a minimized counterexample.
6. Run the three feedback scenarios to distinguish stable convergence, oscillation, and bounded divergence.

The browser UI is keyboard-operable: Tab reaches controls and typed ports; Enter or Space commits an acceptable port while link mode is active; Escape cancels link mode and menus.

## Semantic kernel

A link policy has endpoint domains `L` and `R`, a consistency judgment, and one or both repair directions:

```ts
interface LinkPolicy<L, R> {
  readonly metadata: PolicyMetadata;

  consistent(left: L, right: R): ConsistencyEvidence;

  propagate(
    request: PropagationRequest<L, R>,
  ): Repair<L> | Repair<R>;
}
```

A repair never hides failure in `undefined` or an exception:

```ts
type Repair<T> =
  | {
      kind: "updated";
      value: T;
      evidence: RepairEvidence;
    }
  | {
      kind: "unchanged";
      value: T;
      evidence: RepairEvidence;
    }
  | {
      kind: "conflict";
      choices: readonly RepairChoice<T>[];
      conflictKind:
        | "ambiguous-inverse"
        | "information-loss"
        | "concurrent-intent"
        | "non-convergent"
        | "policy-refusal";
      evidence: RepairEvidence;
    }
  | {
      kind: "invalid";
      reason: string;
      evidence: RepairEvidence;
    };
```

The evidence object records:

- consistency before and after repair;
- preserved and discarded intent;
- information loss;
- provenance;
- the applied delta, when available;
- policy assumptions.

This evidence is the basis of the conflict UI and the JSONL composition capsule.

## Worked domain

The fixed row catalogue is:

```text
row-7   station A   temperature 18.4   pressure 1008
row-9   station B   temperature 21.1   pressure 1003
row-11  station A   temperature 19.7   pressure 1006
row-13  station C   temperature 17.8   pressure 1012
row-17  station B   temperature 22.0   pressure 1001
```

A row selection is an ordered list of row IDs. The filter language is inspectable syntax:

```ts
type FilterExpr =
  | { op: "true" }
  | { op: "inRows"; rows: readonly RowId[] }
  | { op: "stationIn"; stations: readonly string[] }
  | { op: "and"; args: readonly FilterExpr[] }
  | { op: "or"; args: readonly FilterExpr[] }
  | { op: "opaque"; id: string; label: string };
```

Exact row filters identify a unique row set. Station-summary filters generally do not. For example, `stationIn(["A"])` can denote `row-7`, `row-11`, or both. Backward propagation therefore returns a conflict with explicit preimages and information-loss evidence.

Opaque clauses are preserved by envelope-aware repairs but are treated as true by the reference evaluator. Claims involving their actual meaning are explicitly outside the trusted fragment.

## Implemented policies

| Policy ID | Kind | Directions | Main behavior |
|---|---|---:|---|
| `primary-document-identity/0.1` | identity reference | both | both projections read and write one `IdentityCell` |
| `row-selection-replacement/0.1` | directed | forward | replaces the filter with an exact row filter |
| `row-selection-filter-lens/0.1` | asymmetric lens | both | exact `get`; partial `put`; conflicts on non-exact inverse |
| `row-selection-to-filter/0.1` | symmetric consistency | both | preserves inspectable filter envelopes and repairs either side |
| `row-selection-filter-delta/0.1` | delta consistency | both | records add/remove/reorder intent and updates the selection clause |
| `lawful-surprising-set-lens/0.1` | asymmetric lens | both | lawful under set equivalence but visibly sorts and deduplicates |
| `intuitive-toggle-but-unlawful/0.1` | negative control | both | intentionally violates `put(s, get(s)) = s` |

The last policy is not a feature. It is a seeded bad design used to demonstrate that the law harness finds and shrinks a plausible implementation error.

## Identity is not two setters

Document identity is modeled by one cell:

```ts
const session = createIdentitySession(
  "document-cell",
  ["chart.document", "pipeline.document"],
  { sort: "document", key: "doc-a" },
);

session.projections["pipeline.document"].set({
  sort: "document",
  key: "doc-b",
});

session.projections["chart.document"].get();
// { sort: "document", key: "doc-b" }
```

No endpoint calls the other endpoint's setter. Persistent quotient classes and durable binding identity remain a P06 responsibility; P08 only supplies a bounded single-session identity-reference implementation so that its semantics can be compared with transformed links.

## Directed, asymmetric, symmetric, and delta repair

### Directed replacement

```ts
const repair = propagateForward(
  directedReplacementPolicy,
  { rows: ["row-7", "row-11"] },
  currentFilter,
);
```

Backward propagation returns `invalid`. This is intentional: derivation is not mislabeled as a bidirectional link.

### Partial asymmetric lens

`get(selection)` produces an exact row filter. `put(selection, filter)` accepts exact row filters. A station summary is a partial inverse and returns a typed conflict.

### Symmetric consistency

The symmetric policy defines a relation between selections and filter denotations. Repairs preserve unrelated inspectable clauses when possible. A stable consistent pair returns `unchanged`.

### Delta repair

The delta policy receives:

```ts
interface DeltaLeftState {
  before: RowSelection;
  after: RowSelection;
  delta: SelectionDelta;
}
```

The delta distinguishes an add, remove, and reorder even when the final extensional row set is identical. Evidence retains that intent for scheduling and explanation.

## Deterministic scheduler

`PropagationScheduler` maintains nodes and explicitly directed policy edges. A transaction:

1. copies the current state;
2. applies user changes;
3. sorts edges by priority, edge ID, and target ID;
4. propagates through a deterministic work queue;
5. resolves or reports conflicts according to the selected strategy;
6. detects a repeated state plus pending-work signature;
7. commits only if the transaction reaches an allowed terminal state.

By default, unresolved conflicts, invalid repairs, oscillations, and bounded failures roll back atomically.

The scheduler does not claim to make arbitrary cycles converge. It makes convergence or failure deterministic and inspectable.

## Laws and counterexamples

The generated law report contains:

- 14 passing obligations;
- 1 expected failing negative-control obligation;
- 0 unsupported obligations.

The tested properties include:

- forward and backward repair establish consistency;
- stable exact pairs remain unchanged;
- every enumerated ambiguous inverse is consistent;
- forward repair is idempotent;
- asymmetric `get-put` and exact-fragment `put-get`;
- zero delta does not rewrite a stable target;
- delta forward repair restores consistency;
- both identity projections observe one cell;
- a lawful set lens satisfies its law under declared set equivalence.

The negative-control counterexample shrinks to:

```json
{
  "source": { "rows": [] },
  "view": { "selected": false }
}
```

The bad `put` toggles `row-7` on even though the requested view already says false. That violates:

```text
put(source, get(source)) = source
```

See `counterexamples/law-counterexamples.json`.

## Experiments and negative findings

The experiment suite compares four designs for add, remove, reorder, and replacement cases.

For the scripted enriched filter with two unrelated clauses:

- directed replacement preserves 0 clauses;
- the asymmetric lens preserves 0 clauses;
- symmetric envelope-aware repair preserves both clauses;
- delta repair preserves both clauses and additionally records edit provenance.

The experiment did **not** show that delta repair uniquely dominates symmetric repair on clause preservation. Its clearer benefit is edit granularity and provenance.

Other negative findings include:

- a lawful lens may still surprise users when its equivalence relation ignores visible ordering;
- deterministic scheduling diagnoses but cannot cure non-convergent feedback;
- a unique ranking score is not proof of user intent;
- finite inverse enumeration over five rows is not a scalable general inverse algorithm.

See `docs/EXPERIMENTS.md` and `results/experiments.json`.

## Ambiguity strategies

`resolveConflict` supports:

- `automatic`: commit only a uniquely top-ranked choice;
- `ranked`: expose ranked choices without committing;
- `dialog`: require an explicit host or user choice;
- `refuse`: preserve the conflict and decline repair.

The policy creates and explains choices. The host owns authority to select a strategy. A score is not treated as universal authority.

## JSONL composition adapter

Run:

```bash
node dist/src/adapter.js
```

Then send one JSON object per line:

```json
{"protocol":"pbui-research/0.1","requestId":"1","kind":"control.hello","payload":{}}
{"protocol":"pbui-research/0.1","requestId":"2","kind":"links.propagate","payload":{"policy":"row-selection-to-filter/0.1","direction":"forward","source":{"rows":["row-7","row-11"]},"targetBefore":{"op":"true"}}}
```

Relevant capabilities:

- `links.check-policy`
- `links.propagate`
- `links.explain-repair`
- `links.simulate-feedback`
- `links.run-laws`
- `links.taxonomy`

The adapter also implements a deliberately bounded identity-reference subset of `bindings.*` to replay the common identity-link trace. Persistent quotient compilation remains outside P08.

Unsupported messages return a typed `unsupported` response rather than being silently ignored.

## Validation and evidence levels

The artifact distinguishes:

- **unchecked formal source**: `proofs/Main.lean`, because Lean was unavailable during assembly;
- **finite model checks**: exact selections and filters over a two-row abstraction;
- **generated property tests**: deterministic seeded tests with shrinkers;
- **example tests**: scheduler, identity cell, conflict handling, and adapter behavior;
- **empirical measurements**: normalization and scheduler timings on one recorded host;
- **design conclusions**: bounded to the fixture and stated assumptions.

Run results are under `results/`. The evidence ledger is `docs/EVIDENCE.md`.

## Repository map

```text
src/                 typed reference semantics
  domain.ts          row/filter syntax, denotation, equivalence, deltas
  policies.ts        identity, directed, lens, symmetric, and delta policies
  repair.ts          typed repair constructors and conflict strategies
  scheduler.ts       deterministic transactional propagation
  laws.ts            generators, shrinkers, finite model checks
  experiments.ts     comparative studies and hypotheses
  taxonomy.ts        22 classified PBUI link cases
  adapter.ts         JSONL composition seam

test/                Node test suite
dist/                compiled JavaScript and declarations
web/                 dependency-free interactive laboratory
react/               React adapter using the same semantic kernel
capsule/             manifest and JSON schemas
fixtures/            common PBUI workbench fixture and traces
results/             generated laws, experiments, traces, benchmarks
counterexamples/     minimized failing examples
proofs/              small Lean model, unchecked in this environment
docs/                API, taxonomy, experiments, evidence, screenshot
report/              framing report, PDF, walkthrough, and handoff
```

## React adapter

`react/P08BidirectionalLinkLab.jsx` imports the compiled semantic kernel. It does not reimplement the policies in React state. The component supplies occurrence lifecycles, visual tiles, accept-mode port picking, keyboard handling, and conflict presentation.

The dependency-free `web/` implementation is the reproducible demonstration when a React host is unavailable.

## Independence from P07

This project was developed as an independent P08 implementation. It does not import, copy, or depend on P07 code. `scripts/check-independence.mjs` scans source imports and fails if a P07 dependency appears.

The composition boundary is contractual rather than code-sharing:

- P06 owns durable identity classes and quotient compilation;
- P07 may later supply typed component signatures;
- P08 consumes endpoint values and policy metadata;
- P09 may orchestrate link-creation workflows;
- P12 owns replicated merge semantics.

## Documentation

- `report/REPORT.md` and `report/REPORT.pdf` - complete framing report
- `docs/API.md` - semantic API and examples
- `docs/TAXONOMY.md` - 22-case classification
- `docs/EXPERIMENTS.md` - methods and results
- `docs/EVIDENCE.md` - claim and evidence ledger
- `docs/COUNTEREXAMPLES.md` - failing designs and minimized examples
- `report/DEMO-WALKTHROUGH.md` - 10-15 minute demonstration
- `report/HANDOFF.md` - solid, provisional, and non-composable results

## License

MIT. See `LICENSE`.

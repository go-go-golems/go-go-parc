# P08 Counterexample Corpus

## Purpose

A synchronization API is easy to make plausible with happy-path examples. This corpus records designs that fail a stated law, preservation obligation, or composition assumption.

The machine-readable corpus is `counterexamples/law-counterexamples.json`.

## C01 - Toggle mistaken for `put`

Policy:

```text
intuitive-toggle-but-unlawful/0.1
```

Intended law:

```text
put(source, get(source)) ~= source
```

Generated input before shrinking:

```json
{
  "source":{"rows":["row-13","row-11","row-9"]},
  "view":{"selected":false}
}
```

Minimized input:

```json
{
  "source":{"rows":[]},
  "view":{"selected":false}
}
```

Observed result:

```json
{"rows":["row-7"]}
```

The operation toggles membership rather than establishing the requested view. When the current view is already false, `put` must preserve false. This example changed the API by reinforcing the distinction between event deltas and desired-state updates.

## C02 - Directed derivation given an invented inverse

A table selection can derive an exact filter. The reverse is not generally defined because a filter may contain summary predicates, ranges, opaque clauses, and disjunctions.

P08 rejects:

```ts
propagateBackward(
  directedReplacementPolicy,
  selection,
  filter,
);
```

with an `invalid` repair. An implementation that chooses rows from an arbitrary filter would silently convert a directed link into a partial inverse.

## C03 - Station summary treated as unique row identity

Fixture:

```text
row-7   station A
row-11  station A
```

Target:

```json
{"op":"stationIn","stations":["A"]}
```

At least three selections satisfy the summary in the bounded fixture:

```text
{row-7}
{row-11}
{row-7,row-11}
```

A total backward function that chooses one of these without evidence loses row identity. P08 returns ranked choices with `ambiguous-inverse` and information-loss evidence.

## C04 - Rich filter envelope destroyed by lawful projection

Initial target:

```json
{
  "op":"and",
  "args":[
    {"op":"opaque","id":"owner","label":"owner=analyst"},
    {"op":"inRows","rows":["row-7","row-9"]}
  ]
}
```

A conventional asymmetric `get` can be lawful while replacing the complete target with only:

```json
{"op":"inRows","rows":["row-7","row-9","row-11"]}
```

The law does not itself preserve target-local intent. Envelope-aware symmetric or delta repair is needed for that obligation.

## C05 - Feedback suppression flag hides oscillation

A common implementation sets a mutable `propagating` flag and ignores callbacks produced by a repair. That can stop a loop but also suppress legitimate downstream updates and makes behavior depend on call-stack timing.

The modulo-three scenario has a genuine cycle:

```text
a -> b := a + 1 mod 3
b -> a := b + 1 mod 3
```

P08 reports repeated global state after eight steps. It does not declare success merely because a flag prevented another callback.

## C06 - Union of replicas mislabeled as a lens

Two offline replicas that independently edit topology need causality and merge semantics. A lens law between current snapshots is not sufficient. P08 classifies these cases as `replicated-merge` and returns typed unsupported responses for replica operations.

## C07 - Structural equality used as the only law equality

The lawful set lens maps:

```text
row-9, row-7, row-7
```

to:

```text
row-7, row-9
```

The round trip is equal as a set but not as an array. A property test that hardcodes structural equality would incorrectly reject the declared law. Conversely, a UI that displays sequence order must not use set equivalence without warning.

## C08 - Automatic ranking treated as user authority

The inverse enumerator assigns scores using prior-row preservation and deterministic tie-breaking. This can support a host strategy, but it cannot establish that the highest-scoring choice matches the user's intention.

The automatic strategy therefore commits only a uniquely top-ranked choice and records provenance. A product may still choose `ranked`, `dialog`, or `refuse` based on risk.

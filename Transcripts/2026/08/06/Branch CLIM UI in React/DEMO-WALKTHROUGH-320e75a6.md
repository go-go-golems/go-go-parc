# P08 Demonstration Walkthrough

Target duration: 10-15 minutes.

## 0. Start the artifact

```bash
npm run demo
```

Open `http://127.0.0.1:4178/`.

The screen contains a source browser, chart, table, pipeline, and a consistency-restoration laboratory. Point out that document ports and transformed data ports have different type labels and link controls.

## 1. Identity reference: one resource, two projections

1. In the chart tile, activate **link** on the primary-document port.
2. The shell enters red link mode. The pipeline primary-document port becomes acceptable.
3. Select the pipeline port using pointer or keyboard.
4. Change the chart document to `Pressure study`.
5. Observe that the pipeline selector changes at the same time.
6. Change the pipeline document back to `Weather stations` and observe the chart.

Explain:

```text
chart.document ----\
                    > one IdentityCell<DocumentRef>
pipeline.document -/
```

This is not a pair of recursive setters. Both endpoints project onto one cell.

## 2. Directed derivation

1. Set the policy to **directed replacement**.
2. Link table row selection to the pipeline filter.
3. Select or deselect a row.
4. Run forward propagation if the link is not already active.
5. Observe an exact `inRows` filter.
6. Try backward propagation.

Expected result: `invalid`, with evidence stating that the policy has no backward direction.

## 3. Partial asymmetric lens

1. Choose **partial asymmetric lens**.
2. Set the pipeline filter to **exact rows**.
3. Run backward repair. The table selection updates.
4. Set the filter to **station A + B**.
5. Run backward repair.

Expected result: a typed `ambiguous-inverse` conflict. The filter identifies station membership but not individual row identity.

## 4. Symmetric consistency and envelope preservation

1. Choose **symmetric repair**.
2. Set the pipeline filter to **enriched filter**. It contains opaque owner intent plus an exact row clause.
3. Add `row-11` in the table.
4. Inspect the filter.

Expected result: only the selection clause changes. The owner clause remains present, and evidence lists it as preserved intent.

5. Reverse the row order without changing membership.

Expected result: the target is `unchanged` because the consistency relation uses row-set equivalence.

## 5. Delta-aware repair

1. Choose **delta repair**.
2. Add a row, remove a row, and perform a reorder-only edit.
3. Open the repair/evidence tab.

Expected result:

- add and remove are recorded explicitly;
- unrelated filter clauses remain present;
- reorder intent is reported even though the filter cannot represent it extensionally.

State the negative result: symmetric repair preserved the same clauses; delta's clearer gain is provenance and edit granularity.

## 6. Conflict policies

1. Use the station A+B summary to create an ambiguous inverse.
2. Switch among `automatic`, `ranked`, `dialog`, and `refuse`.

Expected behavior:

- automatic commits only a uniquely top-ranked choice;
- ranked and dialog leave choices pending;
- refuse declines repair.

Emphasize that a ranking score is not user authority.

## 7. Law harness and counterexample

1. Open the **laws** tab.
2. Run the harness.
3. Show 14 passes and the one expected negative-control failure.
4. Open `counterexamples/law-counterexamples.json`.

The minimized example is an empty selection and a false membership view. The seeded bad `put` toggles the row on, violating `put(s,get(s))=s`.

## 8. Feedback scheduling

1. Open the **feedback** tab.
2. Run **trim then lowercase**: stable convergence.
3. Run **modulo-three cycle**: repeated-state oscillation.
4. Run **unbounded counter**: bounded failure.

Explain that deterministic scheduling gives reproducible diagnostics, not guaranteed convergence.

## 9. Taxonomy and composition boundary

1. Open the **taxonomy** tab.
2. Show the 22 cases, including disputed cases.
3. Point out replicated topology links classified as `replicated-merge`, not as lenses.
4. Run `npm run verify:compiled` in a terminal.
5. Optionally send `control.hello` and `links.propagate` requests to the JSONL adapter.

Conclude with the subsystem boundaries:

- P06 owns persistent identity classes;
- P08 owns transformed-link relation and repair semantics;
- P09 may own link-creation workflow;
- P12 owns replicated merge.

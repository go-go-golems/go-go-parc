# P06 demonstration walkthrough

Target duration: 12 minutes.

## 1. Start and orient — 1 minute

```sh
npm run demo
```

Open the printed local URL. Point out the three widgets and the inspector:

```text
chart.document   --q--> binding --v--> resource
pipeline.document --q--/
```

Each port card displays its local name, semantic contract, binding ID, and resource ID.

## 2. Inspect independent ports — 1 minute

The initial fixture has:

- chart document = `doc-a`;
- pipeline document = `doc-b`;
- table document = `doc-a`.

Change the chart document. Verify that pipeline does not change because the ports are singleton classes.

## 3. Check and reject an invalid identity link — 1 minute

Use **try invalid identity** or select:

- `chart-1.document`;
- `pipeline-1.outputDocument`.

Show that both carry a document-shaped payload, yet the link is rejected because semantic tag and mode differ. Open the compatibility panel.

## 4. Link chart and pipeline — 2 minutes

Select chart and pipeline primary-document ports. Their current values differ, so choose a merge policy. Use **prefer endpoint 1** and identify them.

Observe:

- both local ports now map to one binding ID;
- both projections name one resource ID;
- the pipeline widget immediately renders the chart’s chosen document.

Change the document from the pipeline selector. The chart changes because both controls write through one resource, not because callbacks copy between widgets.

## 5. Add the table transitively — 1 minute

Use **link all documents**. Show that chart, pipeline, and table inhabit one class even though only two equations were declared.

Open **projection** and **provenance**. Explain that the class is the generated equivalence closure and the stored declarations supply a path witness.

## 6. Remove one declaration — 2 minutes

Choose `history-restore` or `copy-current`, then remove one link declaration.

If another path still connects the endpoints, the partition remains linked. Otherwise the class splits. Emphasize that the split value comes from the selected policy, not from the quotient.

## 7. Factorization experiment — 1 minute

Run **factor interpretation**. The per-port interpretation is constant on each class, so it produces one value per binding and commuting checks.

Run **break factor law**. One member of a linked class is assigned a different value, and factorization is rejected.

## 8. Algorithm comparison and counterexamples — 2 minutes

Run the browser differential test. Open **laws** and **counterexamples**.

Highlight:

- reference graph closure versus union-find;
- external IDs are assigned after union-find representatives are discarded;
- pairwise callbacks do not provide a quotient;
- a quotient cannot recover the generating declaration set;
- component shadow state can still violate observed synchronization.

## 9. Close with evidence levels — 1 minute

Show `report/REPORT.md`, `test/`, and `proofs/Main.lean`.

State the evidence boundary:

- the Lean source supplies proof terms for the small indexed model, pending an independent checker run;
- generated tests compare the two JavaScript compilers;
- runtime laws are executable tests;
- benchmark results are empirical;
- transformed and replicated links remain unsupported.

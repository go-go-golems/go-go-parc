# Lean port-binding proof

This is a dependency-free Lean 4 example of:

- semantically typed local UI ports;
- identity-link declarations and their reflexive/symmetric/transitive closure;
- bindings as quotient classes of linked ports;
- the quotient projection `project : Port t -> Binding t`;
- the existence and uniqueness factorization property for maps out of a binding;
- a concrete `f : Binding .document -> Widget`;
- proofs that linked chart, pipeline, and table ports share a binding and widget;
- a tiny executable renderer.

## Run

With `elan` installed, enter this directory and run:

```sh
lean --run Main.lean
```

Expected output:

```text
chart:    <select aria-label="Shared document">Document</select>
pipeline: <select aria-label="Shared document">Document</select>
table:    <select aria-label="Shared document">Document</select>
```

The file uses only Lean's `Init` library and pins Lean 4.32.2 in
`lean-toolchain`.

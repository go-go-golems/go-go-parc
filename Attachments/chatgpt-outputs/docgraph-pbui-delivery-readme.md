# Docgraph PBUI Widget DSL delivery

## Files

- `docgraph-workbench-pbui.jsx` — drop-in replacement for the attached prototype.
- `docgraph-workbench-pbui.patch` — unified diff against `docgraph-workbench.jsx`.
- `pbui-widget-dsl-intern-guide.md` — textbook-style analysis, design, and implementation guide.
- `pbui-widget-dsl-reference/` — production-oriented Go/Goja, contract, React, PBUI, example, and test seams.

## Demonstrator entry point

Load preset **07 · Widget DSL + PBUI framework** in the modified workbench.

The preset compiles:

- one search recipe,
- one versioned Widget page,
- a presentation-type lattice,
- five declarative commands,
- one page shortcut,
- a React-rendered semantic page with corpus, document, hit, and recipe presentations.

Try these interactions:

1. Left-click a corpus to invoke its default command.
2. Right-click a document to inspect its computed command menu.
3. Invoke **Compare with another document…**, then select a second document while accept mode is active.
4. Invoke the recipe and select a corpus.
5. Search, then use document commands on a `<hit>`; `hit` is a subtype of `doc`.
6. Press `D` over a focused presentation to describe it, or `M` to open its menu.

## Verification commands used

```sh
npx tsc --allowJs --checkJs false --jsx preserve --noEmit \
  --target ES2020 --module ESNext --skipLibCheck docgraph-workbench-pbui.jsx

python pbui-widget-dsl-reference/tests/validate_contract.py
```

The Go validator can be tested inside the target Go module with:

```sh
go test ./path/to/pkg/widgetdsl
```

`builders_stub.go` is deliberately an integration seam. Replace it with generated or implemented fluent builders and replace the placeholder Go module import in `go/widgetsite/provider.go`.

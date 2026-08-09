# gojamacro

`gojamacro` is an AST-driven validation and source-rewriting layer for JavaScript executed by [Goja](https://github.com/dop251/goja).

It is designed for macro points such as “the first argument to `foobar()`,” where Go code needs to validate, instrument, precompile, or replace an exact JavaScript expression before evaluation.

The module currently uses the placeholder import path `example.com/gojamacro`. Replace the `module` directive in `go.mod` before publishing it.

## Core behavior

1. Parse JavaScript with Goja.
2. Walk the Goja AST and run registered matchers.
3. Give each match to a processor with its AST captures, byte span, source text, and position.
4. Collect replacements without mutating the AST.
5. Reject overlapping replacements.
6. Apply edits from right to left.
7. Parse the generated source again.
8. Optionally compile it to a reusable `*goja.Program`.

Goja is pinned to `v0.0.0-20260311135729-065cd970411c`, which declares Go 1.20 compatibility. Goja describes its parser and AST APIs as works in progress; reflection-based traversal is therefore isolated in `walk.go`.

## Instrument the first argument to `foobar`

```go
package main

import (
    "fmt"

    macro "example.com/gojamacro"
)

func main() {
    engine := macro.New()
    engine.MustAdd(macro.Rule{
        Name:    "instrument-foobar-first-argument",
        Matcher: macro.CallArg("foobar", 0),
        Process: macro.Rewrite(func(ctx *macro.Context) (string, error) {
            return fmt.Sprintf(
                `__trace(%q, () => (%s))`,
                ctx.Position().String(),
                ctx.MatchedSource(),
            ), nil
        }),
    })

    result, err := engine.Transform(
        "script.js",
        `const answer = foobar(x * 100);`,
    )
    if err != nil {
        panic(err)
    }

    fmt.Println(result.Source)
}
```

Output:

```javascript
const answer = foobar(__trace("script.js:1:23", () => (x * 100)));
```

## Compile and run

```go
compiled, err := engine.Compile("script.js", source)
if err != nil {
    return err
}

vm := goja.New()
_, err = vm.RunProgram(compiled.Program)
```

The transformed source and edit history are available through `compiled.Transformation`.

When the caller already parsed the source, use that AST for the first pass:

```go
program, err := goja.Parse("script.js", source, parser.WithDisableSourceMaps)
if err != nil {
    return err
}

result, err := engine.TransformAST(source, program)
```

`TransformAST` verifies that `program.File.Source()` exactly equals the supplied source. Later passes, when enabled, reparse the rewritten source.

## Validate a macro point

```go
engine.MustAdd(macro.Rule{
    Name:    "literal-query",
    Matcher: macro.CallArg("query", 0),
    Process: macro.Validate(func(ctx *macro.Context) error {
        if _, ok := ctx.Node().(*ast.StringLiteral); !ok {
            return errors.New("query() requires a string literal")
        }
        return nil
    }),
})
```

All validation failures from a pass are returned together as `macro.Diagnostics`. No edits from that pass are applied when any diagnostic exists.

## Optimize or precompile

```go
engine.MustAdd(macro.Rule{
    Name:    "prepared-query",
    Matcher: macro.CallArg("db.query", 0),
    Process: macro.Rewrite(func(ctx *macro.Context) (string, error) {
        id, err := precompileSQL(ctx.MatchedSource())
        if err != nil {
            return "", err
        }
        return strconv.Itoa(id), nil
    }),
})
```

For example, `db.query("SELECT ...")` can become `db.query(17)`, where `17` indexes Go-side precompiled state.

## Public matching API

Built-in matchers:

- `Call("foobar")` selects the whole call.
- `CallArg("foobar", 0)` selects a zero-based argument.
- `Call("db.query")` and `CallArg("db.query", 0)` match dotted syntactic callees.
- `CallPath(...)` and `CallArgPath(...)` avoid parsing a dotted string.
- `WhereNode(...)`, `Where(...)`, `AnyOf(...)`, and `MatcherFunc` support custom matching.

Useful captures from call matchers:

- `macro.CaptureWhole`
- `macro.CaptureCall`
- `macro.CaptureCallee`
- `macro.CaptureArgument`

A processor can use `Capture`, `CaptureSource`, `SourceOf`, `SpanOf`, `PositionOf`, and `ArgumentIndex` on its `*macro.Context`.

## Syntactic, not binding-aware

`Call("foobar")` matches the syntax `foobar(...)`. It does not perform JavaScript lexical name resolution. Therefore this also matches a shadowing local binding:

```javascript
function run(foobar) {
    return foobar(value);
}
```

For an embedded DSL, reserve macro callee names and reject shadowing. If shadowing is required, build a scope-aware custom matcher on top of `MatcherFunc` and `Cursor.Ancestors`.

Computed properties are deliberately not treated as dotted paths: `db["query"]()` does not match `Call("db.query")`.

## Rewrites and conflicts

Processors return one of:

```go
macro.Keep()
macro.Replace("generated JavaScript")
macro.Reject("diagnostic message")
```

Two different replacements whose spans overlap produce `*macro.EditConflictError`. This includes nested targets such as an outer call argument containing an independently rewritten inner argument. Resolve that ambiguity by combining the transformation into one rule, changing match boundaries, or staging rules in separate engines.

Identical edits to an identical span are deduplicated.

## Multiple passes

The default is one pass. Enable staged expansion explicitly:

```go
engine := macro.New(macro.WithMaxPasses(8))
```

The engine detects exact source cycles, such as `a()` → `b()` → `a()`, and returns `*macro.ExpansionCycleError`. Monotonically growing rewrites cannot form an exact cycle, so the pass count remains the hard bound. `Result.ChangedOnLastPass` indicates whether the final allowed pass changed the source.

An instrumentation rule targeting an argument often still matches its own generated wrapper on the next pass. Such rules should normally remain single-pass.

## Parser and source maps

The default parser option is `parser.WithDisableSourceMaps`. This avoids loading paths referenced by `sourceMappingURL` comments while processing untrusted source.

Replace the parser options when source-map loading is intentional:

```go
engine := macro.New(
    macro.WithParserOptions(
        parser.WithSourceMapLoader(loader),
    ),
)
```

## Concurrency and runtime safety

The engine snapshots its registered rules for each transformation, so registration and transformation can occur concurrently. Matcher and processor callbacks are invoked without engine locks; callbacks that share mutable state must synchronize it themselves.

This package transforms and compiles JavaScript; it is not a sandbox. Apply the normal runtime controls needed for untrusted JavaScript, including interruption, host-function restrictions, and resource limits appropriate to the embedding application.

## Test and demo

```sh
go test ./...
go run ./cmd/demo
```

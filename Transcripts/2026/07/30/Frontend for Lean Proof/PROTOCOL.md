# Mock Lean protocol surface

The backend uses JSON-RPC 2.0 envelopes over a browser WebSocket. Real Lean normally transports the same LSP/RPC concepts through the language-server connection; WebSocket is the deliberate browser-facing deviation in this mock.

## Standard-style LSP methods

| Method | Direction | Mock behavior |
|---|---:|---|
| `initialize` | request | Advertises full document sync, hover, symbols, RPC v1, tagged code, and goal diffs. |
| `initialized` | notification | Emits a log message. |
| `textDocument/didOpen` | notification | Opens and analyzes a document. |
| `textDocument/didChange` | notification | Accepts full-document changes, increments the model, and invalidates file RPC sessions. |
| `textDocument/didClose` | notification | Drops the document and its sessions. |
| `textDocument/publishDiagnostics` | notification | Publishes versioned parser/tactic warnings and errors. When the client advertises incremental support and a version has multiple messages, the first chunk replaces and later `isIncremental: true` chunks append. |
| `$/lean/fileProgress` | notification | Reports a processing range and then an empty range set. |
| `$/lean/plainGoal` | request | Returns rendered and per-goal text without interactive references. |
| `textDocument/hover` | request | Returns a Markdown hover for the token at the source position. |
| `textDocument/documentSymbol` | request | Returns parsed theorem/lemma/example symbols. |

## Lean RPC session methods

| Method | Direction | Mock behavior |
|---|---:|---|
| `$/lean/rpc/connect` | request | Creates a file-scoped string session ID. |
| `$/lean/rpc/call` | request | Calls a fully-qualified procedure at a source position. |
| `$/lean/rpc/keepAlive` | notification | Refreshes the session lifetime. Sessions expire after 30 seconds without activity. |
| `$/lean/rpc/release` | notification | Releases v1 RPC references. |

A document edit invalidates every RPC session for that URI. A subsequent call with the old session returns error code `-32900`, allowing the frontend to reconnect.

## RPC procedures

### Lean-shaped procedures

- `Lean.Widget.getInteractiveGoals`
- `Lean.Widget.getInteractiveDiagnostics`
- `Lean.Widget.InteractiveDiagnostics.infoToInteractive`
- `Lean.Widget.getGoToLocation`

### PBUI extension procedures

- `PBUI.getProofTimeline`
- `PBUI.getDeclarations`
- `PBUI.getServerModel`

The PBUI procedures are explicitly custom. They demonstrate how a later Lean companion package can expose `InfoTree`-derived data through server RPC methods.

## Tagged code

`CodeWithInfos` uses the current three-way tagged-text representation:

```json
{
  "append": [
    { "text": "⊢ " },
    {
      "tag": [
        {
          "info": { "__rpcref": "42" },
          "subexprPos": "3",
          "diffStatus": "wasInserted"
        },
        { "text": "Nat.succ" }
      ]
    }
  ]
}
```

The React renderer recursively handles `text`, `append`, and `tag`. Each tag becomes a typed PBUI presentation. Activating it invokes `infoToInteractive`; its context menu can inspect, navigate, or pin the object.

## Interactive goals

The mock emits:

- bundled hypotheses with `names`, `fvarIds`, tagged `type`, optional `val`, and diff flags;
- tagged goal targets;
- `ctx` v1 RPC references;
- `userName`, `goalPrefix`, `mvarId`, `isInserted`, and `isRemoved`;
- removed goal ghosts plus inserted branch goals after tactics such as `induction`.

## Semantic limits

This backend is not a Lean kernel or elaborator. Its analyzer is deterministic and rule-based. It recognizes theorem headers, binders, tactic lines, branches, a small tactic vocabulary, `sorry`, and obvious errors. The point is to make frontend protocol, rendering, cancellation, versioning, stale references, diagnostics, and CLIM-style commands testable before connecting to real Lean.

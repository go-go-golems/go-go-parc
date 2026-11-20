---
title: "Reusing source spans in PicoCalc’s asynchronous compiler"
aliases:
  - "Reusing source spans in PicoCalc’s asynchronous compiler"
tags:
  - article
  - picocalc
  - compiler-construction
  - performance
status: complete
type: article
created: 2026-11-20
repo: /home/manuel/code/wesen/2026-10-20--ds-js-os
---

# Reusing source spans in PicoCalc’s asynchronous compiler

PicoCalc Editor compiles its typed source on the device. Its asynchronous functions contain waits for events such as file-read completions. The compiler turns those functions into ordinary typed code with saved state and a resume dispatcher, then emits Wasm or RV32. The same compilation may discover a function in the original source, copy its entire body into rewritten text, and scan the copy again.

This study asks which parts can still be read from the original source and which parts must be generated. In vendored QuickJS on the host, the combined source-span and indexed-prepass variant reduced median linked G4 Editor compile CPU time from **169.852 to 154.838 ms** against the indexed compiler with borrowed current tokens. Peak tracked allocation fell by **124,992 bytes**. The staged compilers produced the same Wasm, RV32 words and linked ELF. [Study analysis and evidence](https://github.com/wesen/2026-10-20--ds-js-os/tree/d3e7c7d/ttmp/2026/11/19/PICOCALC-LANGUAGE-E--control-flow-forward-calls-enums-and-distinct-integers/various/span-studies)

> [!summary]
> A source span gives the emitter a range to parse in an existing string. The native token index can also supply ordinary source call edges. The two changes reduce different costs, which is why the experiment measures them separately and together.

## Three functions can come from three places

A *source span* is a start and exclusive end offset in a named source string. The typed signature scanner records each function's name, parameter and result types, and opening and closing brace positions. After this scan the emitter can seek to a body's opening brace and parse the instructions there.

Consider this fragment of a typed world. Its ordinary caller starts a task, and the task calls another ordinary function after a timer event.

~~~typescript
record WorldState { count: i32; }

function plusOne(value: i32): i32 {
    return value + 1;
}

async function advance(state: WorldState): i32 {
    await typedSdkYield();
    state.count = plusOne(state.count);
    return state.count;
}

function begin(state: WorldState): bool {
    return start advance(state);
}
~~~

The transformation handles each function differently.

| Source function | What the emission plan gives the lexer |
| --- | --- |
| plusOne | A span in the authored source. Its body and signature are already available. |
| begin | An edited body segment containing a call to the generated start wrapper. Its signature is unchanged. |
| advance | A generated step in a common suffix, alongside the generated task operations. Those functions get fresh signatures. |

The emitter installs the existing declaration layouts and appends the generated frame fields to WorldState. It reads the generated headers and puts their signatures in the same call table as the existing ones. It then emits each function in the original rewritten order. The old output offsets remain in the function descriptors. The lexer uses an offset in the selected segment while parsing. In this example the compiled record has three fields. The source declares count and the task contributes its wait state and token. The call to plusOne reads through the current state parameter after resumption.

The difference matters for native indexing. The ordinary scanner has already built a token index for the authored source during async discovery. If ordinary emission reads the same string, it can use those records again. The generated suffix and the changed bodies have separate coordinates and receive their own smaller indices. [Source-span implementation](https://github.com/wesen/2026-10-20--ds-js-os/blob/d3e7c7d/ttmp/2026/11/19/PICOCALC-LANGUAGE-E--control-flow-forward-calls-enums-and-distinct-integers/scripts/13-stage-span-reuse.py)

~~~mermaid
flowchart LR
    Original["Authored source and its token index"]
    Plan["Known signatures and body spans"]
    Edited["Changed body segments"]
    Generated["Generated suffix and new signatures"]
    Emit["One typed emitter and call table"]
    Original --> Plan --> Emit
    Original --> Edited --> Emit
    Original --> Generated --> Emit
~~~

For G4 Editor, the indexed reference scans the 69,884-code-unit authored source and the 81,233-unit complete rewrite. The composed compiler indexes the original once, then scans a 14,946-unit generated suffix and five changed bodies. The additional text totals **18,498 code units**. An oracle recorded each native provider invocation and checked those source lengths. A separate test made the lazy full-source accessor throw and confirmed that normal emission still succeeded. Explicitly requesting the generated source returned the same complete text as the stock compiler. [Exact provider and output checks](https://github.com/wesen/2026-10-20--ds-js-os/blob/d3e7c7d/ttmp/2026/11/19/PICOCALC-LANGUAGE-E--control-flow-forward-calls-enums-and-distinct-integers/scripts/15-check-span-reuse.mjs)

## An ordinary body can contribute call edges without another text scan

A call graph records which functions call which other functions. The async pass uses that information to reject cycles before discovering and laying out task frames. The old pass checks whether each ordinary body may contain operations such as await and start. In bodies without those operations, it scans source text for direct calls. A comment that mentions await can send a body down the slower token-by-token path even when its code has no task operation.

The native index already gives each token occurrence an absolute position and a symbol ordinal, which identifies a spelling and kind. The indexed prepass classifies the symbols for task words and known function names once per original source. In an ordinary body, a known function name followed by an opening parenthesis contributes an edge. A preceding dot makes it a member access, so the inspector leaves it out of the direct call graph. It records the edges as they occur in the source and lets the existing semantic phase handle them. A body with task syntax takes the original operation-discovery path.

That division preserves error order. The malformed text below can contain an identifier token named advance immediately after an integer. The original call regex would also require a word boundary before advance. A comment mentioning await can change which of the legacy scanners the function uses.

~~~typescript
return 1advance(state);
~~~

The prototype gives such a body back to the old scanner. It also keeps semantic diagnosis in the old pass, so discovering a bad call earlier in the native table does not make its error jump ahead of a bad declaration elsewhere. If segmented emission itself reports a syntax error, the prototype runs the canonical full-text checker with backend callbacks disabled and returns the diagnostic through the normal source map. [Indexed body inspection](https://github.com/wesen/2026-10-20--ds-js-os/blob/d3e7c7d/ttmp/2026/11/19/PICOCALC-LANGUAGE-E--control-flow-forward-calls-enums-and-distinct-integers/scripts/14-indexed-prepass-overlay.mjs)

## What changed in the host compiler

Every sample used a fresh vendored QuickJS runtime, the same SDK reactor, one pinned host CPU, and a 4 MiB tracked allocation cap. Nine trials per lane alternated the order of variants. The linked CPU time includes analysis, emission and linking. Loading the compiler modules has its own measurement. Tracked peak includes native index buffers and temporary tables.

| G4 variant | Linked CPU median, ms | Linked wall median, ms | Module load CPU median, ms | Tracked peak, bytes |
| --- | ---: | ---: | ---: | ---: |
| Stock | 228.499 | 235 | 17.314 | 3,052,176 |
| Reuse signatures | 211.706 | 216 | 17.579 | 3,076,208 |
| Reuse signatures and original body spans | 214.785 | 220 | 18.492 | 2,947,544 |
| Native index with borrowed token | 169.852 | 175 | 18.137 | 3,496,512 |
| Index and indexed prepass | 158.068 | 158 | 18.928 | 3,541,680 |
| Index and original spans | 167.570 | 168 | 19.177 | 3,418,216 |
| Index, original spans and indexed prepass | 154.838 | 156 | 19.502 | 3,371,520 |

Within the regex lanes, using original spans saved 128,664 peak bytes against signature reuse and took 3.079 ms more median CPU time. Within the indexed lanes, most of the CPU savings came from the prepass while source spans recovered memory. The combination decreased linked CPU by **8.8%** against the indexed reference and used about **3.22 MiB** of tracked peak allocation.

A separate five-run host phase probe located the prepass savings. Median time for scanning operations fell from 10.749 to 1.227 ms. Reading the original source program fell from 18.981 to 15.838 ms. Task analysis fell from 10.320 to 9.228 ms. These phase samples compare the indexed reference with the prepass-only arm. The ordinary-parameter change also reuses existing type signature arrays, so the overall comparison includes less descriptor allocation as well as less scanning. [Linked timing samples](https://github.com/wesen/2026-10-20--ds-js-os/blob/d3e7c7d/ttmp/2026/11/19/PICOCALC-LANGUAGE-E--control-flow-forward-calls-enums-and-distinct-integers/various/span-studies/linked-timing.jsonl) · [Phase samples](https://github.com/wesen/2026-10-20--ds-js-os/blob/d3e7c7d/ttmp/2026/11/19/PICOCALC-LANGUAGE-E--control-flow-forward-calls-enums-and-distinct-integers/various/span-studies/indexed-phases.jsonl)

## Artifact identity is the qualification for timing the board

Across seven staged compiler variants, the oracle checked six positive inputs, five complete source-order call graph traces, and 35 further inputs. Thirty-four of the last group were rejected with the same diagnostics. The checks compare generated source, state layout, signatures, entries, relocations, raw machine words and linked files. The historical language E, continuation G and real Editor interleaving suites also returned identical receipts in the span, indexed-prepass and combined lanes.

Editor retains 70 WorldState fields. With the shared SDK reactor, the linked Wasm SHA-256 is `5dfeb5713680bc2c475ed5c530209a98cea40ce152faae5fb11c7de1fff04c65` and the linked RV32 ELF SHA-256 is `7c182547f28e7e6d9921f2a7df7472c6a44df184b7e5eb0543b40c523e6253bd`. The fingerprints let a cold device run identify the exact application independently of how much compiler CPU it required. [Parity and historical receipts](https://github.com/wesen/2026-10-20--ds-js-os/tree/d3e7c7d/ttmp/2026/11/19/PICOCALC-LANGUAGE-E--control-flow-forward-calls-enums-and-distinct-integers/various/span-studies)

The earlier physical G4 trace explains why these phases were targeted. In that firmware, reading the program took 440.8 ms and scanning operations took 181.4 ms. The physical cold interval also includes firmware-side setup and final module copying. The host study fixes source and artifacts and identifies the candidate, while the paired device trial determines the actual cold timing. [Physical G4 phase measurements](https://github.com/wesen/2026-10-20--ds-js-os/blob/d3e7c7d/ttmp/2026/11/19/PICOCALC-EG-QUAL--implement-and-qualify-the-typed-language-and-asynchronous-editor-on-the-picocalc/analysis/01-compiling-a-complete-asynchronous-editor-on-the-picocalc.md)

To reproduce the study, stage the lanes with scripts/16-run-span-studies.sh in the Language E ticket and use the same reactor ELF for every lane. The stage launcher exports stock source from 2e4fee1 and pre-G control from 1357545. The parity oracle compares the seven G4 compiler variants on the same inputs. The pre-G control provides a separate timing reference. [Staging recipe and investigation diary](https://github.com/wesen/2026-10-20--ds-js-os/tree/d3e7c7d/ttmp/2026/11/19/PICOCALC-LANGUAGE-E--control-flow-forward-calls-enums-and-distinct-integers)

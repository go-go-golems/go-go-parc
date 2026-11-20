---
title: Two guards can prove a text read safe
aliases:
  - PicoCalc bounded index proof
  - Versioned two-hop bounds proof
tags:
  - article
  - picocalc
  - compiler-construction
  - static-analysis
status: complete
type: article
created: 2026-11-19
repo: /home/manuel/code/wesen/2026-10-20--ds-js-os
---

# Two guards can prove a text read safe

A Markdown preview function in PicoCalc Editor walks a UTF-16 span from its current index to an exclusive end. The read is safe when the current index is nonnegative and the end is at most the text's length. The source originally exposed only the loop condition `i < end`. This experiment exposed the other two comparisons and tested how much a bounded, per-function proof could recover.

> [!summary]
> - One proven static read in Editor's copy loop avoided 202 and 3,129 checks in two separate 64 KiB preview replays.
> - The compiler required a nonnegative index and a strict path to the receiver length. Reassignment, effects, unsupported expressions and a spent eight-edge budget leave checks in place.
> - The original checked loop remains available for invalid spans. All 357 focused vectors agreed with Wasm on values, traps and memory.

## Establish exactly what the load needs

PicoCalc stores a 32-bit length at the start of a counted string. `charCodeAt(i)` uses an unsigned comparison to detect an index outside the text, then reads a 16-bit unit. With `length = 8`, `end = 6` and `i = 5`, the guard `i < end` combined with `end <= length` yields `i < length`. The other guard, `0 <= i`, ensures the signed source value and the unsigned machine check agree.

The prototype inserts these explicit conditions around the existing preview copy. The copy loop uses the nonnegative and upper guards, and the original checked loop follows it. When a valid copy finishes its index equals the end, so the checked loop executes zero iterations. For valid string and buffer objects, a negative initial index or an excessive end reaches the original loop’s check when a read is required. Other surrounding effects retain their order, including the destination buffer check before the source read. Every lane compiles this same source.

The upper proof must include a strict relation. From `i <= end` and `end <= length`, the three values can all be equal. That leaves `i` outside the array. Either upper edge may supply strictness.

## Give facts identities and lifetimes

The fact table stores inequalities between versioned local values, receiver lengths and zero. For example, `i@7 < end@4` refers to the names' current values when a guard succeeds. Assigning `i = fresh` creates a new identity. A read at the new value cannot use the older relation. A receiver change also invalidates its length term.

A comparison on the left of `&&` must be true before evaluation reaches the right operand. The parser temporarily extends the active facts while compiling that operand. At an if-only join, a fact can survive when it was present before the branch and remains valid after compiling the body. A changed binding gets a fresh version at the join. A disjunction allows either branch to be true, so this analysis collects no positive relational facts from it.

A call can resize a counted view and an aliasing record store can change a header. Both operations clear the current facts. A loop can also execute those effects after the candidate read, which matters when the next iteration enters. The experimental compiler scans a bounded number of loop tokens before using an outer length fact. It keeps the outer relation when the scan finds only effects that preserve the header, and otherwise retains the check. Loop entry also renews mutable local identities. The loop's own lower and upper tests then establish the facts for that iteration.

```text
0 <= i@current
i@current < end@parameter
end@parameter <= length(text@parameter)
```

The direct query needs a strict edge straight from the index to the receiver length. The bounded query may go through one intermediate. It examines at most eight edges, and a scope keeps up to 24 live relation entries. Unknown arithmetic such as `i + 1` stays checked because the experiment has no wraparound proof.

## Count executions along the actual preview

A compiled check site can execute thousands of times. To measure it, dedicated instrumented variants emit an RV32 no-op with an immediate that the host emulator counts once whenever the check executes. The existing native Editor driver brackets the preview actions. The measurement excludes checks in the SDK and buffer writes. All lanes produce the same native stdout digest and pass the existing frame comparisons.

| Measurement | Current | Direct | Bounded |
| --- | ---: | ---: | ---: |
| RV32 words on the guarded Editor source | 16,214 | 16,214 | 16,210 |
| Emitted read-check sites | 116 | 116 | 115 |
| Actually executed checks, sparse inline preview | 4,740 | 4,740 | 4,538 |
| Actually executed checks, dense inline preview | 47,105 | 47,105 | 43,976 |

The bounded lane saves one header load, one redundant receiver load, one conditional branch and one trap instruction at the proven site. The trap instruction accounts for a word of static output even on a successful access. The one-hop implementation proves a separate direct fixture, and the measured Editor source requires the two-hop relation.

## Measure the compile and guest trade on the ESP32-P4

The two physical boots each used six balanced cold compile blocks per lane with fresh QuickJS runtimes. The bounded Editor build took +8.08% / +10.10% more time than the current compiler, while peak heap rose +1.11% / +1.11%. The direct analysis also paid the bookkeeping cost, at +9.03% / +10.05% compile time and +1.11% / +1.12% peak heap, with the same native image as current.

| Physical copy benchmark | Boot 1 / Boot 2 |
| --- | ---: |
| Current cycles per UTF-16 unit | 42.391 / 42.393 |
| Direct cycles per UTF-16 unit | 42.386 / 42.385 |
| Bounded cycles per UTF-16 unit | 38.378 / 38.379 |
| Bounded paired change | −9.49% / −9.46% |

The guest benchmark runs the exact copy routine emitted for Editor. It checks all output and state and copies 65,536 units per pass at 360 MHz. The full preview dynamic counts came from the separate native-loader replays. This distinction matters because the complete preview also spends time in Markdown parsing, layout, native SDK functions and other typed routines.

The source change has a cost of its own. The original direct-read Editor used 16,174 words without the extra guarded loop and fallback code. The bounded result of 16,210 words measures the optimization against the guarded source. Study the direct and bounded variants side by side to learn what the proof contributes, and compare back to the original source to judge any source intervention.

The experiment is documented in project ticket `PICOCALC-BOUNDED-INDEX` at commit `5ef7051`. The typed text operation used in the proof is described separately. [[ARTICLE - PicoCalc Compiler - Preserving Checked Text Reads Through Native Lowering]]

# Formal assurance claims and boundary

## Claim matrix

| ID | Claim | Method | Scope |
|---|---|---|---|
| C1 | RTL-lowered signed less-than equals mathematical signed less-than | Z3 bit-vectors; `cmp_formal.sby` | All 2^64 operand pairs |
| C2 | All eight opcode and NULL cases equal the SQL subset specification | Z3; synthesized-VHDL comparator harness | All operands, NULL bit, opcodes |
| C3 | Packed lanes and slots select the intended logical row/configuration | Z3 bit-vector extraction; synthesized-VHDL datapath harness | Four row lanes, four slots, all selectors |
| C4 | Disabled slots are identity and enabled slots reduce by conjunction | Z3 Boolean equivalence; synthesized-VHDL datapath harness | All slot outputs/enables |
| C5 | Reset clears output state | Z3 transition proof; stream SBY harness | One-stage state transition |
| C6 | Backpressure preserves valid and payload | Z3 transition proof; stream SBY harness | Arbitrary current state/input |
| C7 | Accepted inputs create a valid next-cycle result | Z3 transition proof; stream SBY harness | Arbitrary current state/input |
| C8 | Drain without replacement clears valid | Z3 transition proof; stream SBY harness | Arbitrary current state/input |

## How the universal proofs work

The proof script declares free 32-bit bit-vectors and Boolean variables. It
constructs both the hardware equation and an independent signed-SQL equation,
then asks Z3 whether they can differ. An `unsat` result means there is no
counterexample in the complete finite domain; this is not random or bounded
input enumeration.

The packed-datapath proof builds the 128-bit row and right-hand-side buses, the
8-bit column bus, the 12-bit opcode bus, the four-bit NULL bus, and the four-bit
enable bus. It then compares physical bit extraction with logical array
selection for symbolic selectors.

The stream proof encodes the exact next-state equations from the RTL and asks
for counterexamples to individual invariants.

## Source binding

`formal/rtl_manifest.json` contains SHA-256 hashes for the reviewed RTL files.
`formal/prove.py` verifies those hashes and the opcode constants before running
its equations. A source change therefore invalidates the checked proof run
until the manifest is deliberately regenerated with
`tools/update_rtl_manifest.py`.

The stronger source-level targets are:

- `cmp_formal.sby`: GHDL elaborates and synthesizes the actual VHDL comparator;
  a VHDL reference model uses `numeric_std.signed` comparisons, and Yosys/SBY
  proves equality.
- `datapath_formal.sby`: GHDL synthesizes `sql_predicate_datapath.vhd` and
  its comparator cells, then proves the packed column selection, opcode/constant
  extraction, NULL behavior, disabled-slot identity, and AND reduction against
  an independent `numeric_std.signed` reference.
- `stream_formal.sby`: GHDL synthesizes `elastic_match_step.vhd`, the exact
  next-state component instantiated by the accelerator, and proves equality to
  independent ready/reset/accept/stall/drain equations for all inputs.

## Trusted computing base

The claims depend on:

- Correctness of Z3's bit-vector and Boolean decision procedures.
- Correctness of the Python Z3 bindings and proof-model transcription.
- For RTL-level targets, correctness of GHDL elaboration/synthesis, the GHDL
  Yosys plugin, Yosys lowering, SymbiYosys orchestration, and the selected SMT
  engine.
- Correct review of the relationship between the SQL subset and its formal
  specification.

Using two paths—direct Z3 equations and synthesized-VHDL SBY checks—reduces the
risk of a single transcription error but does not eliminate the trusted base.

## Explicit non-claims

The project does not claim formal correctness for:

- SQL tokenization, parsing, projection, aggregation, or planner code.
- Filesystem atomicity beyond the operations stated in the architecture note.
- Concurrent transactions, crash recovery, or durability under arbitrary
  hardware/filesystem failure.
- FPGA timing closure, metastability, reset release, CDC, DMA, caches, or
  external-memory ordering.
- Liveness if `out_ready` remains low forever.
- Query forms outside the documented SQL subset.

## Recorded local run

The included `formal/proof_results.txt` records the Z3 run made for this source
revision. The Python suite records 15 passing tests when the package was built.
GHDL, Yosys, and SymbiYosys were not available in that build environment, so the
SBY targets are supplied but were not executed there. This distinction is
intentional: the Z3 contract results are completed evidence; the SBY files are
reproducible proof targets requiring the external HDL toolchain.

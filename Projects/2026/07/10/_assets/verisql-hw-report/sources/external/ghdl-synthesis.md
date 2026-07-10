# GHDL synthesis and Yosys integration

- Source: GHDL documentation, “Synthesis”.
- URL: https://ghdl.github.io/ghdl/using/Synthesis.html
- Accessed: 2026-07-10.

GHDL documents `--synth` as its synthesis entry point. The GHDL-Yosys plugin maps GHDL’s internal representation into Yosys and can produce formal-analysis formats such as SMT2 and BTOR2. The documentation recommends checking a design with GHDL’s own synthesis command before running the Yosys flow. This matches the repository’s separation between `make vhdl-synth` and the later SymbiYosys targets.

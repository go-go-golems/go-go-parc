# Formal directory

## Completed contract proof

```bash
python -m pip install z3-solver
python formal/prove.py
```

The script checks the RTL integrity manifest and discharges universal
bit-vector/transition claims. Its output for this revision is captured in
`proof_results.txt`.

## Actual synthesized-VHDL targets

The `.sby` files require a Yosys build with the GHDL plugin. GHDL's Yosys
front-end command must be visible inside Yosys as `ghdl`.

```bash
cd formal
sby -f cmp_formal.sby
sby -f datapath_formal.sby
sby -f stream_formal.sby
```

`cmp_formal.sby` proves combinational equivalence of `sql_cmp32` to a VHDL
reference using signed `numeric_std` comparisons. `datapath_formal.sby` proves
the synthesized packed four-slot datapath, including lane selection and AND
reduction, against an independent signed reference. `stream_formal.sby` proves the actual VHDL next-state block used by the
accelerator against independent elastic
register equations for every current-state/input combination.

Run normal VHDL simulations and GHDL's synthesis front-end check separately:

```bash
make vhdl-test
make vhdl-synth
```

Do not update `rtl_manifest.json` mechanically after an RTL edit. Review whether
`prove.py`, all three formal harnesses, and the Python model still represent the
changed implementation; then run `tools/update_rtl_manifest.py` and rerun all
proof/test targets.

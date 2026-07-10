# Z3 bit-vector semantics

- Source: Microsoft, Online Z3 Guide, “Introduction”.
- URL: https://microsoft.github.io/z3guide/programming/Z3%20Python%20-%20Readonly/Introduction/
- Accessed: 2026-07-10.

The guide distinguishes the bit-vector representation from the signedness of individual operations. In Z3Py, relational operators such as `<`, `<=`, `>`, and `>=` are signed; the corresponding unsigned operations are `ULT`, `ULE`, `UGT`, and `UGE`. This distinction is central to the VeriSQL-HW proof because the VHDL comparator constructs signed ordering from sign bits and unsigned magnitude comparison.

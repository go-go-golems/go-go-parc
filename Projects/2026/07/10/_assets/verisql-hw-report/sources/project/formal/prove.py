#!/usr/bin/env python3
"""Machine-check the accelerator contract with Z3 bit-vectors.

This proof has no finite test-vector bound.  It asks Z3 for a counterexample to
several universally quantified claims represented by free symbolic variables;
UNSAT means no assignment exists over the full 32-bit domains.

The script also verifies SHA-256 hashes for the RTL revision against
``rtl_manifest.json``.  Actual synthesized-VHDL equivalence targets are provided
as ``cmp_formal.sby``, ``datapath_formal.sby``, and ``stream_formal.sby``.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import sys

try:
    import z3
except ImportError as exc:  # pragma: no cover - setup failure
    raise SystemExit("z3-solver is required: python -m pip install z3-solver") from exc


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

RTL = ROOT / "rtl"
MANIFEST = Path(__file__).with_name("rtl_manifest.json")

EXPECTED_OPCODES = {
    "OP_EQ": 0b000,
    "OP_NE": 0b001,
    "OP_LT": 0b010,
    "OP_LE": 0b011,
    "OP_GT": 0b100,
    "OP_GE": 0b101,
    "OP_IS_NULL": 0b110,
    "OP_IS_NOT_NULL": 0b111,
}

EXPECTED_DIMENSIONS = {
    "DATA_WIDTH": 32,
    "COLUMN_COUNT": 4,
    "PREDICATE_COUNT": 4,
}

REVIEWED_RTL_FILES = {
    "rtl/sql_pkg.vhd",
    "rtl/sql_cmp32.vhd",
    "rtl/elastic_match_step.vhd",
    "rtl/sql_predicate_datapath.vhd",
    "rtl/sql_predicate_accel.vhd",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_rtl_integrity() -> None:
    if not MANIFEST.exists():
        raise AssertionError("missing formal/rtl_manifest.json")
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if manifest.get("schema") != 1:
        raise AssertionError(
            f"unsupported RTL manifest schema: {manifest.get('schema')!r}"
        )
    hashes = manifest.get("sha256")
    if not isinstance(hashes, dict) or set(hashes) != REVIEWED_RTL_FILES:
        raise AssertionError(
            "RTL manifest file set differs from the reviewed proof boundary: "
            f"{sorted(hashes) if isinstance(hashes, dict) else hashes!r}"
        )
    for relative, expected_hash in hashes.items():
        path = ROOT / relative
        actual = sha256(path)
        if actual != expected_hash:
            raise AssertionError(
                f"RTL integrity mismatch for {relative}:\n"
                f"  manifest: {expected_hash}\n  actual:   {actual}\n"
                "Run tools/update_rtl_manifest.py only after reviewing RTL and proofs."
            )

    package_text = (RTL / "sql_pkg.vhd").read_text(encoding="utf-8")
    found = {
        name: int(bits, 2)
        for name, bits in re.findall(
            r"constant\s+(OP_[A-Z_]+)\s*:[^:;]+:=\s*\"([01]{3})\"",
            package_text,
            flags=re.IGNORECASE,
        )
    }
    if found != EXPECTED_OPCODES:
        raise AssertionError(f"VHDL opcode map differs from proof model: {found!r}")

    dimensions = {
        name: int(value)
        for name, value in re.findall(
            r"constant\s+(DATA_WIDTH|COLUMN_COUNT|PREDICATE_COUNT)\s*"
            r":\s*positive\s*:=\s*(\d+)",
            package_text,
            flags=re.IGNORECASE,
        )
    }
    if dimensions != EXPECTED_DIMENSIONS:
        raise AssertionError(f"VHDL dimensions differ from proof model: {dimensions!r}")

    from verisql.accelerator import (
        COLUMN_COUNT,
        DATA_WIDTH,
        PREDICATE_COUNT,
        Opcode,
    )

    python_opcodes = {f"OP_{opcode.name}": int(opcode) for opcode in Opcode}
    if python_opcodes != EXPECTED_OPCODES:
        raise AssertionError(
            f"Python opcode map differs from proof model: {python_opcodes!r}"
        )
    python_dimensions = {
        "DATA_WIDTH": DATA_WIDTH,
        "COLUMN_COUNT": COLUMN_COUNT,
        "PREDICATE_COUNT": PREDICATE_COUNT,
    }
    if python_dimensions != EXPECTED_DIMENSIONS:
        raise AssertionError(
            f"Python dimensions differ from proof model: {python_dimensions!r}"
        )


def rtl_signed_lt(lhs: z3.BitVecRef, rhs: z3.BitVecRef) -> z3.BoolRef:
    lhs_sign = z3.Extract(31, 31, lhs) == z3.BitVecVal(1, 1)
    rhs_sign = z3.Extract(31, 31, rhs) == z3.BitVecVal(1, 1)
    return z3.If(lhs_sign != rhs_sign, lhs_sign, z3.ULT(lhs, rhs))


def mux_opcode(
    opcode: z3.BitVecRef,
    *,
    equal: z3.BoolRef,
    less: z3.BoolRef,
    greater: z3.BoolRef,
) -> z3.BoolRef:
    return z3.Or(
        z3.And(opcode == 0, equal),
        z3.And(opcode == 1, z3.Not(equal)),
        z3.And(opcode == 2, less),
        z3.And(opcode == 3, z3.Or(less, equal)),
        z3.And(opcode == 4, greater),
        z3.And(opcode == 5, z3.Or(greater, equal)),
    )


def rtl_compare(
    lhs: z3.BitVecRef,
    rhs: z3.BitVecRef,
    is_null: z3.BoolRef,
    opcode: z3.BitVecRef,
) -> z3.BoolRef:
    scalar = mux_opcode(
        opcode,
        equal=lhs == rhs,
        less=rtl_signed_lt(lhs, rhs),
        greater=rtl_signed_lt(rhs, lhs),
    )
    return z3.If(
        opcode == 6,
        is_null,
        z3.If(opcode == 7, z3.Not(is_null), z3.If(is_null, z3.BoolVal(False), scalar)),
    )


def sql_spec_compare(
    lhs: z3.BitVecRef,
    rhs: z3.BitVecRef,
    is_null: z3.BoolRef,
    opcode: z3.BitVecRef,
) -> z3.BoolRef:
    # Z3Py's <, <=, > and >= on BitVec values are signed comparisons.
    scalar = z3.Or(
        z3.And(opcode == 0, lhs == rhs),
        z3.And(opcode == 1, lhs != rhs),
        z3.And(opcode == 2, lhs < rhs),
        z3.And(opcode == 3, lhs <= rhs),
        z3.And(opcode == 4, lhs > rhs),
        z3.And(opcode == 5, lhs >= rhs),
    )
    return z3.If(
        opcode == 6,
        is_null,
        z3.If(opcode == 7, z3.Not(is_null), z3.If(is_null, z3.BoolVal(False), scalar)),
    )


def prove_unsat(name: str, counterexample: z3.BoolRef) -> None:
    solver = z3.Solver()
    solver.set(timeout=60_000)
    solver.add(counterexample)
    result = solver.check()
    if result != z3.unsat:
        detail = solver.model() if result == z3.sat else solver.reason_unknown()
        raise AssertionError(f"{name}: expected UNSAT, got {result}: {detail}")
    print(f"PASS  {name}: UNSAT (no counterexample)")


def proof_scalar_predicate() -> None:
    lhs = z3.BitVec("scalar_lhs", 32)
    rhs = z3.BitVec("scalar_rhs", 32)
    opcode = z3.BitVec("scalar_opcode", 3)
    is_null = z3.Bool("scalar_is_null")
    prove_unsat(
        "INT32 comparator + SQL NULL semantics",
        rtl_compare(lhs, rhs, is_null, opcode)
        != sql_spec_compare(lhs, rhs, is_null, opcode),
    )


def extract_lane(packed: z3.BitVecRef, index: int, width: int) -> z3.BitVecRef:
    return z3.Extract((index + 1) * width - 1, index * width, packed)


def select_lane(lanes: list[z3.BitVecRef], index: z3.BitVecRef) -> z3.BitVecRef:
    selected = lanes[-1]
    for lane_index in reversed(range(len(lanes) - 1)):
        selected = z3.If(index == lane_index, lanes[lane_index], selected)
    return selected


def proof_packed_four_predicate_datapath() -> None:
    rows = [z3.BitVec(f"row_{i}", 32) for i in range(4)]
    nulls = [z3.Bool(f"null_{i}") for i in range(4)]
    enables = [z3.Bool(f"enable_{i}") for i in range(4)]
    columns = [z3.BitVec(f"column_{i}", 2) for i in range(4)]
    opcodes = [z3.BitVec(f"opcode_{i}", 3) for i in range(4)]
    rhs = [z3.BitVec(f"rhs_{i}", 32) for i in range(4)]

    packed_row = z3.Concat(rows[3], rows[2], rows[1], rows[0])
    packed_null = z3.Concat(
        *[z3.If(nulls[i], z3.BitVecVal(1, 1), z3.BitVecVal(0, 1)) for i in (3, 2, 1, 0)]
    )
    packed_enable = z3.Concat(
        *[
            z3.If(enables[i], z3.BitVecVal(1, 1), z3.BitVecVal(0, 1))
            for i in (3, 2, 1, 0)
        ]
    )
    packed_column = z3.Concat(columns[3], columns[2], columns[1], columns[0])
    packed_opcode = z3.Concat(opcodes[3], opcodes[2], opcodes[1], opcodes[0])
    packed_rhs = z3.Concat(rhs[3], rhs[2], rhs[1], rhs[0])

    rtl_terms: list[z3.BoolRef] = []
    spec_terms: list[z3.BoolRef] = []
    for slot in range(4):
        enable_bit = extract_lane(packed_enable, slot, 1) == 1
        column_bits = extract_lane(packed_column, slot, 2)
        opcode_bits = extract_lane(packed_opcode, slot, 3)
        rhs_bits = extract_lane(packed_rhs, slot, 32)
        physical_lanes = [extract_lane(packed_row, lane, 32) for lane in range(4)]
        physical_nulls = [extract_lane(packed_null, lane, 1) == 1 for lane in range(4)]
        selected_value = select_lane(physical_lanes, column_bits)
        selected_null = (
            select_lane(
                [
                    z3.If(n, z3.BitVecVal(1, 1), z3.BitVecVal(0, 1))
                    for n in physical_nulls
                ],
                column_bits,
            )
            == 1
        )
        rtl_terms.append(
            z3.Or(
                z3.Not(enable_bit),
                rtl_compare(selected_value, rhs_bits, selected_null, opcode_bits),
            )
        )

        logical_value = select_lane(rows, columns[slot])
        logical_null = (
            select_lane(
                [z3.If(n, z3.BitVecVal(1, 1), z3.BitVecVal(0, 1)) for n in nulls],
                columns[slot],
            )
            == 1
        )
        spec_terms.append(
            z3.Or(
                z3.Not(enables[slot]),
                sql_spec_compare(logical_value, rhs[slot], logical_null, opcodes[slot]),
            )
        )

    prove_unsat(
        "packed four-lane/four-predicate AND datapath",
        z3.And(*rtl_terms) != z3.And(*spec_terms),
    )


def proof_stream_transition() -> None:
    valid_q = z3.Bool("valid_q")
    match_q = z3.Bool("match_q")
    in_valid = z3.Bool("in_valid")
    out_ready = z3.Bool("out_ready")
    reset = z3.Bool("reset")
    match_comb = z3.Bool("match_comb")

    in_ready = z3.Or(z3.Not(valid_q), out_ready)
    next_valid = z3.If(reset, z3.BoolVal(False), z3.If(in_ready, in_valid, valid_q))
    next_match = z3.If(
        reset,
        z3.BoolVal(False),
        z3.If(z3.And(in_ready, in_valid), match_comb, match_q),
    )

    claims: list[tuple[str, z3.BoolRef]] = [
        (
            "stream: reset clears output state",
            z3.And(reset, z3.Or(next_valid, next_match)),
        ),
        (
            "stream: backpressure preserves valid and payload",
            z3.And(
                z3.Not(reset),
                valid_q,
                z3.Not(out_ready),
                z3.Or(z3.Not(next_valid), next_match != match_q),
            ),
        ),
        (
            "stream: accepted row appears next cycle",
            z3.And(
                z3.Not(reset),
                in_valid,
                in_ready,
                z3.Or(z3.Not(next_valid), next_match != match_comb),
            ),
        ),
        (
            "stream: drain without replacement clears valid",
            z3.And(
                z3.Not(reset),
                valid_q,
                out_ready,
                z3.Not(in_valid),
                next_valid,
            ),
        ),
        (
            "stream: stalled input cannot be accepted/overwrite output",
            z3.And(valid_q, z3.Not(out_ready), in_ready),
        ),
    ]
    for name, counterexample in claims:
        prove_unsat(name, counterexample)


def main() -> int:
    check_rtl_integrity()
    print(
        f"RTL integrity: PASS ({len(json.loads(MANIFEST.read_text())['sha256'])} files)"
    )
    print(f"Z3 version: {z3.get_version_string()}")
    proof_scalar_predicate()
    proof_packed_four_predicate_datapath()
    proof_stream_transition()
    print("All contract proofs discharged.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print(f"FAIL  {exc}", file=sys.stderr)
        raise SystemExit(1)

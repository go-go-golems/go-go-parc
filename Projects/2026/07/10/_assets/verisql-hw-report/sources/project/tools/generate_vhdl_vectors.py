#!/usr/bin/env python3
"""Generate deterministic packed vectors for the VHDL datapath testbench."""

from __future__ import annotations

import argparse
from pathlib import Path
import random

from verisql.accelerator import (
    Opcode,
    PredicateConfig,
    VhdlPredicateModel,
    pack_config,
    pack_row,
)


EDGE_VALUES = (-(2**31), -(2**31) + 1, -1, 0, 1, 2**31 - 2, 2**31 - 1)


def random_int32(rng: random.Random) -> int:
    if rng.random() < 0.35:
        return rng.choice(EDGE_VALUES)
    return rng.randint(-(2**31), 2**31 - 1)


def generate(path: Path, count: int, seed: int) -> None:
    if count <= 0:
        raise ValueError("count must be positive")

    rng = random.Random(seed)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="ascii", newline="\n") as handle:
        for _ in range(count):
            row = tuple(
                None if rng.random() < 0.2 else random_int32(rng) for _ in range(4)
            )
            config = tuple(
                PredicateConfig(
                    enabled=rng.random() < 0.8,
                    column=rng.randrange(4),
                    opcode=rng.choice(tuple(Opcode)),
                    rhs=random_int32(rng),
                )
                for _ in range(4)
            )
            packed_row, packed_null = pack_row(row)
            packed_config = pack_config(config)
            expected = VhdlPredicateModel.evaluate(row, config)
            handle.write(
                f"{packed_config.enable:01X} "
                f"{packed_config.columns:02X} "
                f"{packed_config.opcodes:03X} "
                f"{packed_config.rhs:032X} "
                f"{packed_row:032X} "
                f"{packed_null:01X} "
                f"{int(expected)}\n"
            )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=Path)
    parser.add_argument("--count", type=int, default=1000)
    parser.add_argument("--seed", type=lambda value: int(value, 0), default=0x51A7E)
    args = parser.parse_args()
    generate(args.output, args.count, args.seed)
    print(f"generated {args.count} vectors in {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

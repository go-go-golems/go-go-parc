from collections import deque
import random

from verisql.accelerator import (
    Opcode,
    PredicateConfig,
    StreamAcceleratorModel,
    VhdlPredicateModel,
    pack_config,
    pack_row,
    rtl_compare,
)


def reference(value: int | None, opcode: Opcode, rhs: int) -> bool:
    if opcode == Opcode.IS_NULL:
        return value is None
    if opcode == Opcode.IS_NOT_NULL:
        return value is not None
    if value is None:
        return False
    return {
        Opcode.EQ: value == rhs,
        Opcode.NE: value != rhs,
        Opcode.LT: value < rhs,
        Opcode.LE: value <= rhs,
        Opcode.GT: value > rhs,
        Opcode.GE: value >= rhs,
    }[opcode]


def test_comparator_edges_and_random_values() -> None:
    edge = [-(2**31), -(2**31) + 1, -1, 0, 1, 2**31 - 2, 2**31 - 1]
    rng = random.Random(0x5EED)
    values = edge + [rng.randint(-(2**31), 2**31 - 1) for _ in range(1000)]
    for value in [None, *values]:
        for rhs in values[:100]:
            for opcode in Opcode:
                assert rtl_compare(value, opcode, rhs) == reference(value, opcode, rhs)


def test_four_predicate_and_null_semantics() -> None:
    config = (
        PredicateConfig(True, 0, Opcode.GE, 10),
        PredicateConfig(True, 1, Opcode.LT, 20),
        PredicateConfig(True, 2, Opcode.IS_NOT_NULL, 0),
        PredicateConfig(False, 3, Opcode.EQ, 99),
    )
    assert VhdlPredicateModel.evaluate((10, 19, 7, 0), config)
    assert not VhdlPredicateModel.evaluate((9, 19, 7, 0), config)
    assert not VhdlPredicateModel.evaluate((10, 20, 7, 0), config)
    assert not VhdlPredicateModel.evaluate((10, 19, None, 0), config)


def test_stream_holds_payload_under_backpressure_and_never_drops() -> None:
    config = (
        PredicateConfig(True, 0, Opcode.GE, 0),
        PredicateConfig(),
        PredicateConfig(),
        PredicateConfig(),
    )
    rows = [(-3,), (0,), (7,), (None,), (9,), (-1,)]
    model = StreamAcceleratorModel()
    model.step(reset=True, config=config, in_valid=False, row=None, out_ready=True)

    next_input = 0
    accepted: deque[tuple[int | None, ...]] = deque()
    completed: list[tuple[tuple[int | None, ...], bool]] = []
    held: tuple[bool, bool] | None = None

    for cycle in range(100):
        out_ready = cycle % 4 not in {1, 2}
        in_valid = next_input < len(rows)
        input_row = rows[next_input] if in_valid else None
        observation = model.step(
            reset=False,
            config=config,
            in_valid=in_valid,
            row=input_row,
            out_ready=out_ready,
        )

        if held is not None:
            assert (observation.out_valid, observation.out_match) == held
            held = None
        if observation.out_valid and not out_ready:
            held = (observation.out_valid, observation.out_match)

        if observation.emitted:
            completed.append((accepted.popleft(), observation.out_match))
        if observation.accepted:
            assert input_row is not None
            accepted.append(tuple(input_row))
            next_input += 1

        if next_input == len(rows) and not accepted and not model.out_valid:
            break
    else:
        raise AssertionError("stream did not drain")

    assert completed == [
        (tuple(row), VhdlPredicateModel.evaluate(row, config)) for row in rows
    ]


def test_bus_packing_lane_zero_is_least_significant() -> None:
    data, nulls = pack_row((1, -1, None, -(2**31)))
    assert data & 0xFFFFFFFF == 1
    assert (data >> 32) & 0xFFFFFFFF == 0xFFFFFFFF
    assert (data >> 64) & 0xFFFFFFFF == 0
    assert (data >> 96) & 0xFFFFFFFF == 0x80000000
    assert nulls == 0b0100

    packed = pack_config(
        (
            PredicateConfig(True, 3, Opcode.GE, -1),
            PredicateConfig(True, 2, Opcode.IS_NULL, 0),
            PredicateConfig(),
            PredicateConfig(),
        )
    )
    assert packed.enable & 0b11 == 0b11
    assert packed.columns & 0b11 == 0b11
    assert (packed.columns >> 2) & 0b11 == 0b10
    assert packed.opcodes & 0b111 == int(Opcode.GE)


def test_vhdl_vector_generator_is_deterministic(tmp_path) -> None:
    from tools.generate_vhdl_vectors import generate

    first = tmp_path / "first.txt"
    second = tmp_path / "second.txt"
    generate(first, count=32, seed=0x12345)
    generate(second, count=32, seed=0x12345)
    assert first.read_bytes() == second.read_bytes()

    lines = first.read_text(encoding="ascii").splitlines()
    assert len(lines) == 32
    widths = (1, 2, 3, 32, 32, 1, 1)
    for line in lines:
        fields = line.split()
        assert tuple(map(len, fields)) == widths
        assert fields[-1] in {"0", "1"}
        for field in fields[:-1]:
            int(field, 16)

"""Software contract and cycle model for the VHDL predicate accelerator."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from enum import IntEnum
from typing import Iterable, Sequence

from .ast import Predicate, PredicateOp
from .storage import INT32_MAX, INT32_MIN, SchemaError, TableSchema


DATA_WIDTH = 32
COLUMN_COUNT = 4
PREDICATE_COUNT = 4
WORD_MASK = (1 << DATA_WIDTH) - 1
SIGN_MASK = 1 << (DATA_WIDTH - 1)


class Opcode(IntEnum):
    EQ = 0b000
    NE = 0b001
    LT = 0b010
    LE = 0b011
    GT = 0b100
    GE = 0b101
    IS_NULL = 0b110
    IS_NOT_NULL = 0b111


_OP_FROM_AST = {
    PredicateOp.EQ: Opcode.EQ,
    PredicateOp.NE: Opcode.NE,
    PredicateOp.LT: Opcode.LT,
    PredicateOp.LE: Opcode.LE,
    PredicateOp.GT: Opcode.GT,
    PredicateOp.GE: Opcode.GE,
    PredicateOp.IS_NULL: Opcode.IS_NULL,
    PredicateOp.IS_NOT_NULL: Opcode.IS_NOT_NULL,
}


@dataclass(frozen=True, slots=True)
class PredicateConfig:
    enabled: bool = False
    column: int = 0
    opcode: Opcode = Opcode.EQ
    rhs: int = 0


@dataclass(frozen=True, slots=True)
class PackedConfig:
    enable: int
    columns: int
    opcodes: int
    rhs: int


@dataclass(frozen=True, slots=True)
class CycleObservation:
    """Signals and transfer events observed immediately before a rising edge."""

    in_ready: bool
    out_valid: bool
    out_match: bool
    accepted: bool
    emitted: bool


class AcceleratorContractError(ValueError):
    pass


def _check_int32(value: int, label: str = "value") -> None:
    if isinstance(value, bool) or not isinstance(value, int):
        raise AcceleratorContractError(f"{label} must be an integer")
    if not INT32_MIN <= value <= INT32_MAX:
        raise AcceleratorContractError(f"{label} {value} is outside signed INT32")


def to_u32(value: int) -> int:
    _check_int32(value)
    return value & WORD_MASK


def signed_lt_bits(lhs: int, rhs: int) -> bool:
    """RTL implementation of signed less-than using only signs and unsigned LT."""

    lhs_u = to_u32(lhs)
    rhs_u = to_u32(rhs)
    lhs_sign = bool(lhs_u & SIGN_MASK)
    rhs_sign = bool(rhs_u & SIGN_MASK)
    if lhs_sign != rhs_sign:
        return lhs_sign
    return lhs_u < rhs_u


def rtl_compare(value: int | None, opcode: Opcode, rhs: int = 0) -> bool:
    """Exact scalar semantics implemented by ``rtl/sql_cmp32.vhd``."""

    if opcode == Opcode.IS_NULL:
        return value is None
    if opcode == Opcode.IS_NOT_NULL:
        return value is not None
    if value is None:
        return False  # SQL UNKNOWN is rejected by WHERE.

    _check_int32(value, "left operand")
    _check_int32(rhs, "right operand")
    equal = to_u32(value) == to_u32(rhs)
    less = signed_lt_bits(value, rhs)
    greater = signed_lt_bits(rhs, value)

    if opcode == Opcode.EQ:
        return equal
    if opcode == Opcode.NE:
        return not equal
    if opcode == Opcode.LT:
        return less
    if opcode == Opcode.LE:
        return less or equal
    if opcode == Opcode.GT:
        return greater
    if opcode == Opcode.GE:
        return greater or equal
    raise AcceleratorContractError(f"unknown opcode {opcode!r}")


def software_compare(value: int | None, op: PredicateOp, rhs: int | None) -> bool:
    """Reference WHERE semantics for the supported SQL subset."""

    if op == PredicateOp.IS_NULL:
        return value is None
    if op == PredicateOp.IS_NOT_NULL:
        return value is not None
    if value is None or rhs is None:
        return False
    if op == PredicateOp.EQ:
        return value == rhs
    if op == PredicateOp.NE:
        return value != rhs
    if op == PredicateOp.LT:
        return value < rhs
    if op == PredicateOp.LE:
        return value <= rhs
    if op == PredicateOp.GT:
        return value > rhs
    if op == PredicateOp.GE:
        return value >= rhs
    raise AcceleratorContractError(f"unsupported predicate operator {op!r}")


def compile_predicates(
    schema: TableSchema, predicates: Sequence[Predicate]
) -> tuple[PredicateConfig, ...] | None:
    """Compile a conjunction into four hardware slots, or return ``None``.

    Returning ``None`` is an explicit software-fallback decision, not an error.
    """

    if len(predicates) > PREDICATE_COUNT:
        return None

    slots: list[PredicateConfig] = []
    for predicate in predicates:
        column = schema.column_index(predicate.column)
        if not 0 <= column < COLUMN_COUNT:
            return None
        opcode = _OP_FROM_AST[predicate.op]
        rhs = predicate.rhs if predicate.rhs is not None else 0
        if opcode not in {Opcode.IS_NULL, Opcode.IS_NOT_NULL}:
            if predicate.rhs is None:
                return None
            if not INT32_MIN <= predicate.rhs <= INT32_MAX:
                raise SchemaError(
                    f"predicate constant {predicate.rhs} is outside signed INT32"
                )
        slots.append(PredicateConfig(True, column, opcode, rhs))

    while len(slots) < PREDICATE_COUNT:
        slots.append(PredicateConfig())
    return tuple(slots)


def evaluate_software(
    row: Sequence[int | None], schema: TableSchema, predicates: Sequence[Predicate]
) -> bool:
    for predicate in predicates:
        value = row[schema.column_index(predicate.column)]
        if not software_compare(value, predicate.op, predicate.rhs):
            return False
    return True


class VhdlPredicateModel:
    """Bit-accurate combinational model of the four-predicate accelerator."""

    @staticmethod
    def evaluate(row: Sequence[int | None], config: Sequence[PredicateConfig]) -> bool:
        if len(row) > COLUMN_COUNT:
            raise AcceleratorContractError(
                f"hardware accepts at most {COLUMN_COUNT} columns"
            )
        if len(config) != PREDICATE_COUNT:
            raise AcceleratorContractError(
                f"hardware requires exactly {PREDICATE_COUNT} predicate slots"
            )
        padded = tuple(row) + (None,) * (COLUMN_COUNT - len(row))
        for slot in config:
            if not slot.enabled:
                continue
            if not 0 <= slot.column < COLUMN_COUNT:
                return False
            if not rtl_compare(padded[slot.column], slot.opcode, slot.rhs):
                return False
        return True

    @staticmethod
    def filter_rows(
        rows: Iterable[Sequence[int | None]], config: Sequence[PredicateConfig]
    ) -> list[tuple[int | None, ...]]:
        return [tuple(row) for row in rows if VhdlPredicateModel.evaluate(row, config)]


class StreamAcceleratorModel:
    """Cycle-accurate model of the one-entry valid/ready output buffer."""

    def __init__(self) -> None:
        self._valid_q = False
        self._match_q = False

    @property
    def out_valid(self) -> bool:
        return self._valid_q

    @property
    def out_match(self) -> bool:
        return self._match_q

    def step(
        self,
        *,
        reset: bool,
        config: Sequence[PredicateConfig],
        in_valid: bool,
        row: Sequence[int | None] | None,
        out_ready: bool,
    ) -> CycleObservation:
        """Advance one rising edge and return pre-edge interface observations."""

        in_ready = (not self._valid_q) or out_ready
        out_valid = self._valid_q
        out_match = self._match_q
        accepted = bool(in_valid and in_ready and not reset)
        emitted = bool(out_valid and out_ready and not reset)

        if reset:
            self._valid_q = False
            self._match_q = False
        elif in_ready:
            self._valid_q = bool(in_valid)
            if in_valid:
                if row is None:
                    raise AcceleratorContractError("in_valid requires a row")
                self._match_q = VhdlPredicateModel.evaluate(row, config)

        return CycleObservation(
            in_ready=in_ready,
            out_valid=out_valid,
            out_match=out_match,
            accepted=accepted,
            emitted=emitted,
        )

    def filter_rows(
        self,
        rows: Iterable[Sequence[int | None]],
        config: Sequence[PredicateConfig],
    ) -> list[tuple[int | None, ...]]:
        """Drive a no-stall stream through the cycle model."""

        pending: deque[tuple[int | None, ...]] = deque()
        selected: list[tuple[int | None, ...]] = []
        self.step(
            reset=True,
            config=config,
            in_valid=False,
            row=None,
            out_ready=True,
        )
        for input_row in rows:
            row_tuple = tuple(input_row)
            observation = self.step(
                reset=False,
                config=config,
                in_valid=True,
                row=row_tuple,
                out_ready=True,
            )
            if observation.emitted:
                completed = pending.popleft()
                if observation.out_match:
                    selected.append(completed)
            if observation.accepted:
                pending.append(row_tuple)

        while self.out_valid:
            observation = self.step(
                reset=False,
                config=config,
                in_valid=False,
                row=None,
                out_ready=True,
            )
            if observation.emitted:
                completed = pending.popleft()
                if observation.out_match:
                    selected.append(completed)
        if pending:
            raise AssertionError("stream model lost accepted rows")
        return selected


def pack_row(row: Sequence[int | None]) -> tuple[int, int]:
    """Pack a database row into ``in_row`` and ``in_null`` integer bitfields."""

    if len(row) > COLUMN_COUNT:
        raise AcceleratorContractError("too many columns for hardware row")
    data = 0
    nulls = 0
    for index in range(COLUMN_COUNT):
        value = row[index] if index < len(row) else None
        if value is None:
            nulls |= 1 << index
            word = 0
        else:
            word = to_u32(value)
        data |= word << (index * DATA_WIDTH)
    return data, nulls


def pack_config(config: Sequence[PredicateConfig]) -> PackedConfig:
    if len(config) != PREDICATE_COUNT:
        raise AcceleratorContractError("configuration must contain four slots")
    enable = columns = opcodes = rhs = 0
    for index, slot in enumerate(config):
        if slot.enabled:
            enable |= 1 << index
        if not 0 <= slot.column < COLUMN_COUNT:
            raise AcceleratorContractError("column index cannot be represented")
        columns |= slot.column << (index * 2)
        opcodes |= int(slot.opcode) << (index * 3)
        rhs |= to_u32(slot.rhs) << (index * DATA_WIDTH)
    return PackedConfig(enable, columns, opcodes, rhs)

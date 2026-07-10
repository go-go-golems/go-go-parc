"""Abstract syntax tree nodes for the supported SQL subset."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import TypeAlias


SqlValue: TypeAlias = int | None


class PredicateOp(str, Enum):
    EQ = "="
    NE = "!="
    LT = "<"
    LE = "<="
    GT = ">"
    GE = ">="
    IS_NULL = "IS NULL"
    IS_NOT_NULL = "IS NOT NULL"


@dataclass(frozen=True, slots=True)
class ColumnDef:
    name: str
    nullable: bool = True


@dataclass(frozen=True, slots=True)
class Predicate:
    column: str
    op: PredicateOp
    rhs: int | None = None


@dataclass(frozen=True, slots=True)
class CreateTable:
    name: str
    columns: tuple[ColumnDef, ...]


@dataclass(frozen=True, slots=True)
class Insert:
    table: str
    rows: tuple[tuple[SqlValue, ...], ...]


@dataclass(frozen=True, slots=True)
class Select:
    table: str
    columns: tuple[str, ...] | None = None
    count_star: bool = False
    predicates: tuple[Predicate, ...] = ()
    limit: int | None = None


@dataclass(frozen=True, slots=True)
class Explain:
    query: Select


Statement: TypeAlias = CreateTable | Insert | Select | Explain

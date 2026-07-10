"""SQL execution engine and hardware-offload planner."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from .accelerator import (
    StreamAcceleratorModel,
    compile_predicates,
    evaluate_software,
)
from .ast import CreateTable, Explain, Insert, Select, Statement
from .parser import parse
from .storage import Column, SchemaError, Storage, TableSchema


class ExecutionError(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class ResultSet:
    columns: tuple[str, ...] = ()
    rows: tuple[tuple[object, ...], ...] = ()
    message: str | None = None


@dataclass(frozen=True, slots=True)
class QueryPlan:
    operator: str
    details: str


class Database:
    """Persistent SQL database with an optional VHDL-contract predicate backend.

    ``backend='vhdl'`` executes eligible predicate conjunctions through the
    cycle-accurate RTL model. ``backend='software'`` is the reference path.
    """

    def __init__(
        self,
        path: str | Path,
        *,
        backend: str = "vhdl",
    ):
        if backend not in {"vhdl", "software"}:
            raise ValueError("backend must be 'vhdl' or 'software'")
        self.storage = Storage(path)
        self.backend = backend

    def execute(self, sql: str) -> list[ResultSet]:
        return [self.execute_statement(statement) for statement in parse(sql)]

    def execute_statement(self, statement: Statement) -> ResultSet:
        if isinstance(statement, CreateTable):
            return self._create_table(statement)
        if isinstance(statement, Insert):
            return self._insert(statement)
        if isinstance(statement, Select):
            return self._select(statement)
        if isinstance(statement, Explain):
            schema = self.storage.schema(statement.query.table)
            plan = self._plan(statement.query, schema)
            return ResultSet(
                columns=("operator", "details"),
                rows=((plan.operator, plan.details),),
            )
        raise ExecutionError(f"unsupported AST node {type(statement).__name__}")

    def _create_table(self, statement: CreateTable) -> ResultSet:
        schema = TableSchema(
            statement.name,
            tuple(Column(column.name, column.nullable) for column in statement.columns),
        )
        self.storage.create_table(schema)
        return ResultSet(message=f"created table {statement.name}")

    def _insert(self, statement: Insert) -> ResultSet:
        inserted = self.storage.append_rows(statement.table, statement.rows)
        noun = "row" if inserted == 1 else "rows"
        return ResultSet(message=f"inserted {inserted} {noun}")

    def _validate_query(self, query: Select, schema: TableSchema) -> tuple[int, ...]:
        for predicate in query.predicates:
            schema.column_index(predicate.column)
        if query.count_star:
            return ()
        if query.columns is None:
            return tuple(range(len(schema.columns)))
        indexes = tuple(schema.column_index(name) for name in query.columns)
        if len(set(indexes)) != len(indexes):
            raise SchemaError("duplicate columns in SELECT list are not supported")
        return indexes

    def _plan(self, query: Select, schema: TableSchema) -> QueryPlan:
        self._validate_query(query, schema)
        if not query.predicates:
            return QueryPlan(
                "TABLE_SCAN",
                f"append-only scan of {schema.name}; no WHERE predicate",
            )
        compiled = compile_predicates(schema, query.predicates)
        if self.backend == "vhdl" and compiled is not None:
            enabled = sum(slot.enabled for slot in compiled)
            return QueryPlan(
                "VHDL_PREDICATE_SCAN",
                f"{enabled} conjunctive predicate(s), four-lane INT32/NULL contract",
            )
        reason = (
            "software backend requested"
            if self.backend == "software"
            else "predicate count exceeds four hardware slots"
        )
        return QueryPlan(
            "SOFTWARE_FILTER_SCAN",
            f"reference SQL predicate evaluator; {reason}",
        )

    def _filtered_rows(
        self, query: Select, schema: TableSchema
    ) -> tuple[list[tuple[int | None, ...]], QueryPlan]:
        plan = self._plan(query, schema)
        source: Iterable[tuple[int | None, ...]] = self.storage.iter_rows(schema.name)

        if not query.predicates:
            rows = list(source)
        elif plan.operator == "VHDL_PREDICATE_SCAN":
            config = compile_predicates(schema, query.predicates)
            assert config is not None
            rows = StreamAcceleratorModel().filter_rows(source, config)
        else:
            rows = [
                row
                for row in source
                if evaluate_software(row, schema, query.predicates)
            ]
        return rows, plan

    def _select(self, query: Select) -> ResultSet:
        schema = self.storage.schema(query.table)
        projection = self._validate_query(query, schema)
        rows, _plan = self._filtered_rows(query, schema)

        if query.count_star:
            if query.limit == 0:
                return ResultSet(columns=("count",), rows=())
            return ResultSet(columns=("count",), rows=((len(rows),),))

        if query.limit is not None:
            rows = rows[: query.limit]

        if query.columns is None:
            names = tuple(column.name for column in schema.columns)
        else:
            names = query.columns
        projected = tuple(tuple(row[index] for index in projection) for row in rows)
        return ResultSet(columns=names, rows=projected)

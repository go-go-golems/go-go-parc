"""Command-line interface for VeriSQL-HW."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys
from typing import Iterable

from .engine import Database, ResultSet


def _format_cell(value: object) -> str:
    return "NULL" if value is None else str(value)


def format_result(result: ResultSet) -> str:
    if result.message is not None:
        return result.message
    if not result.columns:
        return ""
    matrix = [list(result.columns)] + [
        [_format_cell(value) for value in row] for row in result.rows
    ]
    widths = [
        max(len(str(row[index])) for row in matrix) for index in range(len(matrix[0]))
    ]
    header = " | ".join(
        str(cell).ljust(width) for cell, width in zip(matrix[0], widths)
    )
    separator = "-+-".join("-" * width for width in widths)
    body = [
        " | ".join(str(cell).ljust(width) for cell, width in zip(row, widths))
        for row in matrix[1:]
    ]
    return "\n".join([header, separator, *body, f"({len(result.rows)} row(s))"])


def _run_sql(database: Database, sql: str) -> int:
    try:
        results = database.execute(sql)
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    for index, result in enumerate(results):
        if index:
            print()
        rendered = format_result(result)
        if rendered:
            print(rendered)
    return 0


def _interactive(database: Database) -> int:
    print("VeriSQL-HW 0.1 — terminate statements with ';', Ctrl-D to exit")
    buffer: list[str] = []
    while True:
        try:
            line = input("vsql> " if not buffer else "   ... ")
        except EOFError:
            print()
            return 0
        buffer.append(line)
        if ";" not in line:
            continue
        sql = "\n".join(buffer)
        buffer.clear()
        _run_sql(database, sql)


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="verisql",
        description="Small SQL database with a verified VHDL predicate contract",
    )
    parser.add_argument(
        "--db",
        type=Path,
        default=Path("./verisql.db"),
        help="database directory (default: ./verisql.db)",
    )
    parser.add_argument(
        "--backend",
        choices=("vhdl", "software"),
        default="vhdl",
        help="predicate execution backend",
    )
    source = parser.add_mutually_exclusive_group()
    source.add_argument("-c", "--command", help="execute SQL text")
    source.add_argument("-f", "--file", type=Path, help="execute a SQL file")
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    args = build_argument_parser().parse_args(list(argv) if argv is not None else None)
    database = Database(args.db, backend=args.backend)
    if args.command is not None:
        return _run_sql(database, args.command)
    if args.file is not None:
        try:
            sql = args.file.read_text(encoding="utf-8")
        except OSError as exc:
            print(f"error: cannot read {args.file}: {exc}", file=sys.stderr)
            return 1
        return _run_sql(database, sql)
    if not sys.stdin.isatty():
        return _run_sql(database, sys.stdin.read())
    return _interactive(database)


if __name__ == "__main__":
    raise SystemExit(main())

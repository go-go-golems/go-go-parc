"""Append-only fixed-width storage aligned with the RTL row format.

Each table has one to four signed INT32 columns. A record consists of a one-byte
NULL bitmap followed by one little-endian signed 32-bit word per column. NULL
words are physically stored as zero; the bitmap carries their meaning.
"""

from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import re
import struct
import threading
from typing import Final, Iterator, Sequence

try:  # POSIX advisory locking; the engine remains usable without it.
    import fcntl
except ImportError:  # pragma: no cover - Windows fallback
    fcntl = None  # type: ignore[assignment]


INT32_MIN: Final[int] = -(2**31)
INT32_MAX: Final[int] = 2**31 - 1
MAX_COLUMNS: Final[int] = 4
CATALOG_VERSION: Final[int] = 1
TABLE_MAGIC: Final[bytes] = b"VSQLTB01"
_HEADER: Final[struct.Struct] = struct.Struct("<8sB3x32s")
_IDENTIFIER_RE: Final[re.Pattern[str]] = re.compile(r"^[a-z_][a-z0-9_]*$")


class StorageError(RuntimeError):
    pass


class TableNotFound(StorageError):
    pass


class TableAlreadyExists(StorageError):
    pass


class SchemaError(StorageError):
    pass


class CorruptTable(StorageError):
    pass


@dataclass(frozen=True, slots=True)
class Column:
    name: str
    nullable: bool = True


@dataclass(frozen=True, slots=True)
class TableSchema:
    name: str
    columns: tuple[Column, ...]

    def column_index(self, name: str) -> int:
        for index, column in enumerate(self.columns):
            if column.name == name:
                return index
        raise SchemaError(f"unknown column {name!r} in table {self.name!r}")

    @property
    def record_struct(self) -> struct.Struct:
        return struct.Struct("<B" + "i" * len(self.columns))

    @property
    def digest(self) -> bytes:
        canonical = json.dumps(
            {
                "name": self.name,
                "columns": [
                    {"name": column.name, "nullable": column.nullable}
                    for column in self.columns
                ],
            },
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        return hashlib.sha256(canonical).digest()


class Storage:
    """Persistent catalog and append-only table files."""

    def __init__(self, root: str | os.PathLike[str]):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self._catalog_path = self.root / "catalog.json"
        self._mutex = threading.RLock()
        if not self._catalog_path.exists():
            self._write_catalog({"format_version": CATALOG_VERSION, "tables": {}})
        self._catalog = self._load_catalog()

    def _load_catalog(self) -> dict[str, object]:
        try:
            raw = json.loads(self._catalog_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise StorageError(
                f"cannot read catalog {self._catalog_path}: {exc}"
            ) from exc
        if raw.get("format_version") != CATALOG_VERSION:
            raise StorageError(
                f"unsupported catalog version {raw.get('format_version')!r}; "
                f"expected {CATALOG_VERSION}"
            )
        if not isinstance(raw.get("tables"), dict):
            raise StorageError("catalog field 'tables' is not an object")
        return raw

    def _write_catalog(self, catalog: dict[str, object]) -> None:
        payload = json.dumps(catalog, indent=2, sort_keys=True) + "\n"
        temp = self.root / f".catalog.{os.getpid()}.{threading.get_ident()}.tmp"
        try:
            with temp.open("w", encoding="utf-8") as handle:
                handle.write(payload)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temp, self._catalog_path)
            # Persist the rename on POSIX filesystems where directory fsync is available.
            try:
                directory_fd = os.open(self.root, os.O_RDONLY)
            except OSError:
                directory_fd = -1
            if directory_fd >= 0:
                try:
                    os.fsync(directory_fd)
                finally:
                    os.close(directory_fd)
        finally:
            temp.unlink(missing_ok=True)

    @staticmethod
    def _validate_identifier(name: str, what: str) -> None:
        if not _IDENTIFIER_RE.fullmatch(name):
            raise SchemaError(f"invalid {what} identifier {name!r}")

    def _table_path(self, table: str) -> Path:
        self._validate_identifier(table, "table")
        return self.root / f"{table}.vsql"

    @contextmanager
    def _locked_file(self, path: Path, mode: str, exclusive: bool):
        with path.open(mode) as handle:
            if fcntl is not None:
                fcntl.flock(
                    handle.fileno(), fcntl.LOCK_EX if exclusive else fcntl.LOCK_SH
                )
            try:
                yield handle
            finally:
                if fcntl is not None:
                    fcntl.flock(handle.fileno(), fcntl.LOCK_UN)

    def list_tables(self) -> tuple[str, ...]:
        with self._mutex:
            tables = self._catalog["tables"]
            assert isinstance(tables, dict)
            return tuple(sorted(tables))

    def schema(self, table: str) -> TableSchema:
        with self._mutex:
            tables = self._catalog["tables"]
            assert isinstance(tables, dict)
            entry = tables.get(table)
            if entry is None:
                raise TableNotFound(f"table {table!r} does not exist")
            if not isinstance(entry, dict) or not isinstance(
                entry.get("columns"), list
            ):
                raise StorageError(f"malformed catalog entry for table {table!r}")
            columns: list[Column] = []
            for raw_column in entry["columns"]:
                if not isinstance(raw_column, dict):
                    raise StorageError(f"malformed column entry in table {table!r}")
                name = raw_column.get("name")
                nullable = raw_column.get("nullable")
                if not isinstance(name, str) or not isinstance(nullable, bool):
                    raise StorageError(f"malformed column entry in table {table!r}")
                columns.append(Column(name, nullable))
            schema = TableSchema(table, tuple(columns))
            self._validate_schema(schema)
            return schema

    def _validate_schema(self, schema: TableSchema) -> None:
        self._validate_identifier(schema.name, "table")
        if not 1 <= len(schema.columns) <= MAX_COLUMNS:
            raise SchemaError(
                f"table {schema.name!r} must have between 1 and {MAX_COLUMNS} columns"
            )
        names: set[str] = set()
        for column in schema.columns:
            self._validate_identifier(column.name, "column")
            if column.name in names:
                raise SchemaError(f"duplicate column {column.name!r}")
            names.add(column.name)

    def create_table(self, schema: TableSchema) -> None:
        self._validate_schema(schema)
        with self._mutex:
            tables = self._catalog["tables"]
            assert isinstance(tables, dict)
            if schema.name in tables:
                raise TableAlreadyExists(f"table {schema.name!r} already exists")
            path = self._table_path(schema.name)
            try:
                with path.open("xb") as handle:
                    handle.write(
                        _HEADER.pack(TABLE_MAGIC, len(schema.columns), schema.digest)
                    )
                    handle.flush()
                    os.fsync(handle.fileno())
            except FileExistsError as exc:
                raise TableAlreadyExists(
                    f"table file for {schema.name!r} already exists"
                ) from exc

            updated = json.loads(json.dumps(self._catalog))
            updated_tables = updated["tables"]
            assert isinstance(updated_tables, dict)
            updated_tables[schema.name] = {
                "columns": [
                    {"name": column.name, "nullable": column.nullable}
                    for column in schema.columns
                ]
            }
            try:
                self._write_catalog(updated)
            except Exception:
                path.unlink(missing_ok=True)
                raise
            self._catalog = updated

    @staticmethod
    def _validate_value(value: int | None, column: Column) -> None:
        if value is None:
            if not column.nullable:
                raise SchemaError(f"column {column.name!r} is NOT NULL")
            return
        if isinstance(value, bool) or not isinstance(value, int):
            raise SchemaError(f"column {column.name!r} requires an integer or NULL")
        if not INT32_MIN <= value <= INT32_MAX:
            raise SchemaError(
                f"value {value} for column {column.name!r} is outside INT32 range"
            )

    def _validate_header(self, handle, schema: TableSchema) -> None:
        handle.seek(0)
        header = handle.read(_HEADER.size)
        if len(header) != _HEADER.size:
            raise CorruptTable(f"table {schema.name!r} has a truncated header")
        magic, column_count, digest = _HEADER.unpack(header)
        if magic != TABLE_MAGIC:
            raise CorruptTable(f"table {schema.name!r} has invalid magic")
        if column_count != len(schema.columns):
            raise CorruptTable(
                f"table {schema.name!r} column count disagrees with catalog"
            )
        if digest != schema.digest:
            raise CorruptTable(
                f"table {schema.name!r} schema digest disagrees with catalog"
            )

    def append_rows(self, table: str, rows: Sequence[Sequence[int | None]]) -> int:
        schema = self.schema(table)
        record = schema.record_struct
        encoded = bytearray()
        for row_number, row in enumerate(rows, start=1):
            if len(row) != len(schema.columns):
                raise SchemaError(
                    f"row {row_number} has {len(row)} values; "
                    f"table {table!r} requires {len(schema.columns)}"
                )
            null_mask = 0
            words: list[int] = []
            for index, (value, column) in enumerate(zip(row, schema.columns)):
                self._validate_value(value, column)
                if value is None:
                    null_mask |= 1 << index
                    words.append(0)
                else:
                    words.append(value)
            encoded.extend(record.pack(null_mask, *words))

        if not encoded:
            return 0

        path = self._table_path(table)
        with self._mutex, self._locked_file(path, "r+b", exclusive=True) as handle:
            self._validate_header(handle, schema)
            handle.seek(0, os.SEEK_END)
            data_bytes = handle.tell() - _HEADER.size
            if data_bytes % record.size:
                raise CorruptTable(f"table {table!r} has a partial trailing record")
            handle.write(encoded)
            handle.flush()
            os.fsync(handle.fileno())
        return len(rows)

    def iter_rows(self, table: str) -> Iterator[tuple[int | None, ...]]:
        schema = self.schema(table)
        path = self._table_path(table)
        record = schema.record_struct

        def generator() -> Iterator[tuple[int | None, ...]]:
            with self._locked_file(path, "rb", exclusive=False) as handle:
                self._validate_header(handle, schema)
                while True:
                    raw = handle.read(record.size)
                    if raw == b"":
                        return
                    if len(raw) != record.size:
                        raise CorruptTable(
                            f"table {table!r} has a partial trailing record"
                        )
                    unpacked = record.unpack(raw)
                    null_mask, words = unpacked[0], unpacked[1:]
                    yield tuple(
                        None if null_mask & (1 << index) else word
                        for index, word in enumerate(words)
                    )

        return generator()

    def row_count(self, table: str) -> int:
        schema = self.schema(table)
        path = self._table_path(table)
        record = schema.record_struct
        with self._locked_file(path, "rb", exclusive=False) as handle:
            self._validate_header(handle, schema)
            handle.seek(0, os.SEEK_END)
            data_bytes = handle.tell() - _HEADER.size
            if data_bytes % record.size:
                raise CorruptTable(f"table {table!r} has a partial trailing record")
            return data_bytes // record.size

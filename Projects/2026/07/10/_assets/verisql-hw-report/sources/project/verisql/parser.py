"""A deliberately small, dependency-free SQL parser.

Supported statements:

* CREATE TABLE name (column INT [NULL|NOT NULL], ...)
* INSERT INTO name VALUES (...), (...)
* SELECT *, columns, or COUNT(*) FROM name [WHERE p AND p ...] [LIMIT n]
* EXPLAIN SELECT ...

Identifiers are unquoted and normalized to lower case. Values are signed decimal
32-bit integers or NULL. WHERE is a conjunction of scalar predicates.
"""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Final, Iterable

from .ast import (
    ColumnDef,
    CreateTable,
    Explain,
    Insert,
    Predicate,
    PredicateOp,
    Select,
    SqlValue,
    Statement,
)


class SqlSyntaxError(ValueError):
    """Raised when input is outside the accepted SQL grammar."""


@dataclass(frozen=True, slots=True)
class Token:
    kind: str
    text: str
    offset: int


_TOKEN_RE: Final[re.Pattern[str]] = re.compile(
    r"""
    (?P<SPACE>\s+)
  | (?P<COMMENT>--[^\n]*(?:\n|$))
  | (?P<OP><=|>=|<>|!=|=|<|>)
  | (?P<NUMBER>[+-]?\d+)
  | (?P<IDENT>[A-Za-z_][A-Za-z0-9_]*)
  | (?P<PUNCT>[(),;*])
  | (?P<MISMATCH>.)
    """,
    re.VERBOSE,
)

_KEYWORDS: Final[frozenset[str]] = frozenset(
    {
        "AND",
        "AS",
        "COUNT",
        "CREATE",
        "EXPLAIN",
        "FROM",
        "INSERT",
        "INT",
        "INTEGER",
        "INTO",
        "IS",
        "LIMIT",
        "NOT",
        "NULL",
        "SELECT",
        "TABLE",
        "VALUES",
        "WHERE",
    }
)


def tokenize(sql: str) -> list[Token]:
    tokens: list[Token] = []
    for match in _TOKEN_RE.finditer(sql):
        kind = match.lastgroup
        assert kind is not None
        text = match.group(0)
        if kind in {"SPACE", "COMMENT"}:
            continue
        if kind == "MISMATCH":
            raise SqlSyntaxError(
                f"unexpected character {text!r} at byte offset {match.start()}"
            )
        if kind == "IDENT":
            upper = text.upper()
            if upper in _KEYWORDS:
                tokens.append(Token(upper, upper, match.start()))
            else:
                tokens.append(Token("IDENT", text.lower(), match.start()))
        elif kind == "PUNCT":
            tokens.append(Token(text, text, match.start()))
        else:
            tokens.append(Token(kind, text, match.start()))
    tokens.append(Token("EOF", "", len(sql)))
    return tokens


class Parser:
    def __init__(self, tokens: Iterable[Token]):
        self._tokens = list(tokens)
        self._pos = 0

    @property
    def current(self) -> Token:
        return self._tokens[self._pos]

    def _advance(self) -> Token:
        token = self.current
        self._pos += 1
        return token

    def _accept(self, kind: str) -> Token | None:
        if self.current.kind == kind:
            return self._advance()
        return None

    def _expect(self, kind: str, expectation: str | None = None) -> Token:
        token = self.current
        if token.kind != kind:
            wanted = expectation or kind
            found = token.text or "end of input"
            raise SqlSyntaxError(
                f"expected {wanted}, found {found!r} at byte offset {token.offset}"
            )
        return self._advance()

    def parse_all(self) -> list[Statement]:
        statements: list[Statement] = []
        while self.current.kind != "EOF":
            while self._accept(";") is not None:
                pass
            if self.current.kind == "EOF":
                break
            statements.append(self._parse_statement())
            if self.current.kind not in {";", "EOF"}:
                token = self.current
                raise SqlSyntaxError(
                    f"expected ';' or end of input, found {token.text!r} "
                    f"at byte offset {token.offset}"
                )
            self._accept(";")
        return statements

    def _parse_statement(self) -> Statement:
        kind = self.current.kind
        if kind == "CREATE":
            return self._parse_create()
        if kind == "INSERT":
            return self._parse_insert()
        if kind == "SELECT":
            return self._parse_select()
        if kind == "EXPLAIN":
            self._advance()
            return Explain(self._parse_select())
        token = self.current
        raise SqlSyntaxError(
            f"unsupported statement starting with {token.text!r} "
            f"at byte offset {token.offset}"
        )

    def _parse_create(self) -> CreateTable:
        self._expect("CREATE")
        self._expect("TABLE")
        name = self._expect("IDENT", "table name").text
        self._expect("(")
        columns = [self._parse_column_def()]
        while self._accept(",") is not None:
            columns.append(self._parse_column_def())
        self._expect(")")
        return CreateTable(name, tuple(columns))

    def _parse_column_def(self) -> ColumnDef:
        name = self._expect("IDENT", "column name").text
        if self.current.kind not in {"INT", "INTEGER"}:
            self._expect("INT", "INT or INTEGER")
        else:
            self._advance()
        nullable = True
        if self._accept("NOT") is not None:
            self._expect("NULL")
            nullable = False
        else:
            self._accept("NULL")
        return ColumnDef(name, nullable)

    def _parse_insert(self) -> Insert:
        self._expect("INSERT")
        self._expect("INTO")
        table = self._expect("IDENT", "table name").text
        self._expect("VALUES")
        rows = [self._parse_value_tuple()]
        while self._accept(",") is not None:
            rows.append(self._parse_value_tuple())
        return Insert(table, tuple(rows))

    def _parse_value_tuple(self) -> tuple[SqlValue, ...]:
        self._expect("(")
        values = [self._parse_value()]
        while self._accept(",") is not None:
            values.append(self._parse_value())
        self._expect(")")
        return tuple(values)

    def _parse_value(self) -> SqlValue:
        if self._accept("NULL") is not None:
            return None
        token = self._expect("NUMBER", "integer or NULL")
        try:
            return int(token.text, 10)
        except ValueError as exc:  # defensive; token regex already restricts shape
            raise SqlSyntaxError(f"invalid integer {token.text!r}") from exc

    def _parse_select(self) -> Select:
        self._expect("SELECT")
        columns: tuple[str, ...] | None
        count_star = False
        if self._accept("*") is not None:
            columns = None
        elif self._accept("COUNT") is not None:
            self._expect("(")
            self._expect("*")
            self._expect(")")
            # Optional alias is accepted but intentionally not retained.
            if self._accept("AS") is not None:
                self._expect("IDENT", "alias")
            count_star = True
            columns = ()
        else:
            selected = [self._expect("IDENT", "column name").text]
            while self._accept(",") is not None:
                selected.append(self._expect("IDENT", "column name").text)
            columns = tuple(selected)

        self._expect("FROM")
        table = self._expect("IDENT", "table name").text

        predicates: list[Predicate] = []
        if self._accept("WHERE") is not None:
            predicates.append(self._parse_predicate())
            while self._accept("AND") is not None:
                predicates.append(self._parse_predicate())

        limit: int | None = None
        if self._accept("LIMIT") is not None:
            token = self._expect("NUMBER", "non-negative LIMIT")
            limit = int(token.text, 10)
            if limit < 0:
                raise SqlSyntaxError(
                    f"LIMIT must be non-negative at byte offset {token.offset}"
                )

        return Select(
            table=table,
            columns=columns,
            count_star=count_star,
            predicates=tuple(predicates),
            limit=limit,
        )

    def _parse_predicate(self) -> Predicate:
        column = self._expect("IDENT", "column name").text
        if self._accept("IS") is not None:
            if self._accept("NOT") is not None:
                self._expect("NULL")
                return Predicate(column, PredicateOp.IS_NOT_NULL)
            self._expect("NULL")
            return Predicate(column, PredicateOp.IS_NULL)

        token = self._expect("OP", "comparison operator or IS NULL")
        op_text = "!=" if token.text == "<>" else token.text
        try:
            op = PredicateOp(op_text)
        except ValueError as exc:
            raise SqlSyntaxError(
                f"unsupported comparison operator {token.text!r}"
            ) from exc
        rhs_token = self._expect("NUMBER", "integer constant")
        return Predicate(column, op, int(rhs_token.text, 10))


def parse(sql: str) -> list[Statement]:
    """Parse one or more semicolon-separated statements."""

    return Parser(tokenize(sql)).parse_all()

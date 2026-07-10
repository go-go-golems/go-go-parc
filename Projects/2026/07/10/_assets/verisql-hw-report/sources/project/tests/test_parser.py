from verisql.ast import CreateTable, Explain, Insert, PredicateOp, Select
from verisql.parser import SqlSyntaxError, parse


def test_parse_supported_sql_subset() -> None:
    statements = parse(
        """
        -- schema
        CREATE TABLE sensor (id INT NOT NULL, temp INTEGER, status INT NULL);
        INSERT INTO sensor VALUES (1, 20, NULL), (2, -5, 7);
        EXPLAIN SELECT id, temp FROM sensor
          WHERE temp >= -10 AND status IS NOT NULL LIMIT 5;
        """
    )
    assert isinstance(statements[0], CreateTable)
    assert statements[0].name == "sensor"
    assert statements[0].columns[0].nullable is False
    assert isinstance(statements[1], Insert)
    assert statements[1].rows == ((1, 20, None), (2, -5, 7))
    assert isinstance(statements[2], Explain)
    query = statements[2].query
    assert query.columns == ("id", "temp")
    assert query.predicates[0].op == PredicateOp.GE
    assert query.predicates[1].op == PredicateOp.IS_NOT_NULL
    assert query.limit == 5


def test_count_and_not_equal_spelling() -> None:
    statement = parse("SELECT COUNT(*) AS n FROM t WHERE a <> 3;")[0]
    assert isinstance(statement, Select)
    assert statement.count_star
    assert statement.predicates[0].op == PredicateOp.NE


def test_rejects_or_and_strings() -> None:
    try:
        parse("SELECT * FROM t WHERE a = 1 OR a = 2")
    except SqlSyntaxError as exc:
        assert "expected ';'" in str(exc)
    else:
        raise AssertionError("OR should be outside the grammar")

from pathlib import Path

import pytest

from verisql.engine import Database
from verisql.storage import SchemaError


SCHEMA_AND_DATA = """
CREATE TABLE readings (
  id INT NOT NULL,
  temp INT,
  pressure INT,
  quality INT NOT NULL
);
INSERT INTO readings VALUES
  (1, 18, 1000, 90),
  (2, 25, 990, 70),
  (3, NULL, 1010, 95),
  (4, -5, NULL, 99),
  (5, 25, 1005, 88);
"""


def rows(result):
    return result.rows


def test_end_to_end_accelerated_query_and_persistence(tmp_path: Path) -> None:
    db_path = tmp_path / "db"
    db = Database(db_path, backend="vhdl")
    db.execute(SCHEMA_AND_DATA)

    result = db.execute(
        "SELECT id, temp FROM readings "
        "WHERE temp >= 20 AND pressure IS NOT NULL AND quality > 80;"
    )[0]
    assert result.columns == ("id", "temp")
    assert rows(result) == ((5, 25),)

    plan = db.execute(
        "EXPLAIN SELECT * FROM readings WHERE temp >= 20 AND quality > 80;"
    )[0]
    assert plan.rows[0][0] == "VHDL_PREDICATE_SCAN"

    reopened = Database(db_path, backend="vhdl")
    count = reopened.execute("SELECT COUNT(*) FROM readings;")[0]
    assert count.rows == ((5,),)


def test_vhdl_and_software_backends_are_observationally_equal(tmp_path: Path) -> None:
    db_path = tmp_path / "db"
    Database(db_path).execute(SCHEMA_AND_DATA)
    hardware = Database(db_path, backend="vhdl")
    software = Database(db_path, backend="software")

    queries = [
        "SELECT * FROM readings WHERE temp < 25;",
        "SELECT id FROM readings WHERE pressure IS NULL;",
        "SELECT id, quality FROM readings WHERE temp != -5 AND quality >= 88;",
        "SELECT COUNT(*) FROM readings WHERE temp IS NOT NULL AND pressure > 995;",
    ]
    for query in queries:
        assert hardware.execute(query)[0] == software.execute(query)[0]


def test_fifth_predicate_falls_back_to_software(tmp_path: Path) -> None:
    db = Database(tmp_path / "db", backend="vhdl")
    db.execute(SCHEMA_AND_DATA)
    query = (
        "SELECT * FROM readings WHERE id >= 0 AND temp IS NOT NULL "
        "AND pressure IS NOT NULL AND quality >= 0 AND id < 100"
    )
    plan = db.execute("EXPLAIN " + query)[0]
    assert plan.rows[0][0] == "SOFTWARE_FILTER_SCAN"
    assert len(db.execute(query)[0].rows) == 3


def test_not_null_and_int32_validation(tmp_path: Path) -> None:
    db = Database(tmp_path / "db")
    db.execute("CREATE TABLE t (a INT NOT NULL);")
    with pytest.raises(SchemaError, match="NOT NULL"):
        db.execute("INSERT INTO t VALUES (NULL);")
    with pytest.raises(SchemaError, match="INT32"):
        db.execute("INSERT INTO t VALUES (2147483648);")
    with pytest.raises(SchemaError, match="INT32"):
        db.execute("SELECT * FROM t WHERE a = 2147483648;")


def test_limit_zero_and_projection(tmp_path: Path) -> None:
    db = Database(tmp_path / "db")
    db.execute("CREATE TABLE t (a INT, b INT); INSERT INTO t VALUES (1, 2), (3, 4);")
    assert db.execute("SELECT b FROM t LIMIT 1;")[0].rows == ((2,),)
    assert db.execute("SELECT COUNT(*) FROM t LIMIT 0;")[0].rows == ()


def test_randomized_accelerated_queries_match_software(tmp_path: Path) -> None:
    import random

    rng = random.Random(0xC0FFEE)
    db_path = tmp_path / "db"
    hardware = Database(db_path, backend="vhdl")

    edge_values = [-(2**31), -1000, -1, 0, 1, 1000, 2**31 - 1]
    generated_rows: list[tuple[int | None, ...]] = []
    for _ in range(200):
        row: list[int | None] = []
        for _column in range(4):
            if rng.random() < 0.18:
                row.append(None)
            elif rng.random() < 0.25:
                row.append(rng.choice(edge_values))
            else:
                row.append(rng.randint(-5000, 5000))
        generated_rows.append(tuple(row))

    def sql_value(value: int | None) -> str:
        return "NULL" if value is None else str(value)

    values_sql = ",\n".join(
        "(" + ", ".join(sql_value(value) for value in row) + ")"
        for row in generated_rows
    )
    hardware.execute(
        "CREATE TABLE t (a INT, b INT, c INT, d INT);\n"
        f"INSERT INTO t VALUES {values_sql};"
    )
    software = Database(db_path, backend="software")

    columns = ("a", "b", "c", "d")
    scalar_ops = ("=", "!=", "<>", "<", "<=", ">", ">=")
    constants = edge_values + [-4096, -17, 17, 4096]

    for _ in range(100):
        predicates: list[str] = []
        for _slot in range(rng.randint(1, 4)):
            column = rng.choice(columns)
            if rng.random() < 0.22:
                predicates.append(
                    f"{column} IS {'NOT ' if rng.random() < 0.5 else ''}NULL"
                )
            else:
                predicates.append(
                    f"{column} {rng.choice(scalar_ops)} {rng.choice(constants)}"
                )

        projection_choice = rng.randrange(3)
        if projection_choice == 0:
            projection = "*"
        elif projection_choice == 1:
            projection = "a, c"
        else:
            projection = "COUNT(*)"
        limit = ""
        if projection != "COUNT(*)" and rng.random() < 0.35:
            limit = f" LIMIT {rng.randint(0, 25)}"

        query = (
            f"SELECT {projection} FROM t WHERE "
            + " AND ".join(predicates)
            + limit
            + ";"
        )
        assert hardware.execute(query)[0] == software.execute(query)[0], query


def test_partial_record_is_detected_as_corruption(tmp_path: Path) -> None:
    from verisql.storage import CorruptTable

    db_path = tmp_path / "db"
    db = Database(db_path)
    db.execute("CREATE TABLE t (a INT, b INT); INSERT INTO t VALUES (1, 2);")
    with (db_path / "t.vsql").open("ab") as handle:
        handle.write(b"\\x00")

    with pytest.raises(CorruptTable, match="partial trailing record"):
        db.execute("SELECT * FROM t;")

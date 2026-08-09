# DAG Task Network Sync

- URL: https://chatgpt.com/c/6a7374ee-1050-83ea-9b76-1b7a30ffc719
- Created: 2026-08-05T17:38:04.491Z

---

> create a hierarchical DAG task network to synchronize multiple coding agents, with a CLI and sqlite.

I’ll build this as a self-contained Python package: SQLite schema, transactional task leasing, hierarchical/DAG validation, CLI commands, tests, and usage documentation.

<details><summary>💭 Thinking</summary>

**Designing task orchestration**

I’m outlining a SQLite-backed task system with groups, dependencies, leases, retries, cancellation, and status propagation. I’m also refining readiness rules so ancestor dependencies block every descendant and dependency cycles are rejected.

**Designed task orchestration**

</details>

```unknown
bash -lc mkdir -p /mnt/data/dag-agent-sync/src/dag_agent_sync /mnt/data/dag-agent-sync/tests && cat > /mnt/data/dag-agent-sync/pyproject.toml <<'EOF'
[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"

[project]
name = "dag-agent-sync"
version = "0.1.0"
description = "A transactional hierarchical DAG task coordinator for multiple coding agents"
readme = "README.md"
requires-python = ">=3.10"
license = {text = "MIT"}
authors = [{name = "OpenAI"}]
dependencies = []

[project.scripts]
dag-sync = "dag_agent_sync.cli:main"

[tool.setuptools.packages.find]
where = ["src"]

[tool.pytest.ini_options]
pythonpath = ["src"]
testpaths = ["tests"]
EOF

cat > /mnt/data/dag-agent-sync/src/dag_agent_sync/__init__.py <<'EOF'
"""Hierarchical DAG coordination for multiple coding agents."""

from .store import Coordinator, DagError, LeaseConflict, NotFound, ValidationError

__all__ = [
    "Coordinator",
    "DagError",
    "LeaseConflict",
    "NotFound",
    "ValidationError",
]
EOF

cat > /mnt/data/dag-agent-sync/src/dag_agent_sync/schema.sql <<'EOF'
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS meta (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

INSERT OR IGNORE INTO meta(key, value) VALUES ('schema_version', '1');

CREATE TABLE IF NOT EXISTS tasks (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    kind TEXT NOT NULL DEFAULT 'task' CHECK (kind IN ('task', 'group')),
    parent_id TEXT REFERENCES tasks(id) ON DELETE RESTRICT,
    status TEXT NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending', 'leased', 'running', 'completed', 'failed', 'cancelled')),
    priority INTEGER NOT NULL DEFAULT 0,
    created_at REAL NOT NULL,
    updated_at REAL NOT NULL,
    completed_at REAL,
    agent_id TEXT,
    lease_until REAL,
    heartbeat_at REAL,
    attempts INTEGER NOT NULL DEFAULT 0,
    max_attempts INTEGER NOT NULL DEFAULT 3 CHECK (max_attempts >= 1),
    result TEXT,
    error TEXT,
    CHECK (
        (status IN ('leased', 'running') AND agent_id IS NOT NULL AND lease_until IS NOT NULL)
        OR status NOT IN ('leased', 'running')
    )
);

CREATE INDEX IF NOT EXISTS idx_tasks_parent ON tasks(parent_id);
CREATE INDEX IF NOT EXISTS idx_tasks_status_priority ON tasks(status, priority DESC, created_at);
CREATE INDEX IF NOT EXISTS idx_tasks_lease ON tasks(lease_until);

CREATE TABLE IF NOT EXISTS dependencies (
    task_id TEXT NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    depends_on_id TEXT NOT NULL REFERENCES tasks(id) ON DELETE RESTRICT,
    created_at REAL NOT NULL,
    PRIMARY KEY (task_id, depends_on_id),
    CHECK (task_id <> depends_on_id)
);

CREATE INDEX IF NOT EXISTS idx_dependencies_depends_on ON dependencies(depends_on_id);

CREATE TABLE IF NOT EXISTS agents (
    id TEXT PRIMARY KEY,
    first_seen_at REAL NOT NULL,
    last_seen_at REAL NOT NULL,
    metadata TEXT NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS events (
    seq INTEGER PRIMARY KEY AUTOINCREMENT,
    at REAL NOT NULL,
    task_id TEXT REFERENCES tasks(id) ON DELETE SET NULL,
    agent_id TEXT,
    event_type TEXT NOT NULL,
    payload TEXT NOT NULL DEFAULT '{}'
);

CREATE INDEX IF NOT EXISTS idx_events_task_seq ON events(task_id, seq);
EOF

cat > /mnt/data/dag-agent-sync/src/dag_agent_sync/store.py <<'EOF'
from __future__ import annotations

import json
import sqlite3
import time
import uuid
from contextlib import contextmanager
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterator, Mapping, Sequence


class DagError(RuntimeError):
    """Base coordinator error."""


class NotFound(DagError):
    """Requested task does not exist."""


class ValidationError(DagError):
    """The requested graph or state mutation is invalid."""


class LeaseConflict(DagError):
    """An agent attempted to mutate a task leased by another agent."""


@dataclass(frozen=True)
class Task:
    id: str
    title: str
    description: str
    kind: str
    parent_id: str | None
    status: str
    priority: int
    created_at: float
    updated_at: float
    completed_at: float | None
    agent_id: str | None
    lease_until: float | None
    heartbeat_at: float | None
    attempts: int
    max_attempts: int
    result: str | None
    error: str | None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class Coordinator:
    """SQLite-backed coordinator for hierarchical DAG tasks.

    Each state-changing operation uses a fresh connection and a transaction.
    Claims use ``BEGIN IMMEDIATE`` so separate agent processes cannot claim the
    same task concurrently.
    """

    def __init__(self, db_path: str | Path, *, timeout: float = 10.0) -> None:
        self.db_path = str(db_path)
        self.timeout = timeout

    def initialize(self) -> None:
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        schema = Path(__file__).with_name("schema.sql").read_text(encoding="utf-8")
        with self._connect() as conn:
            conn.executescript(schema)
            conn.execute("PRAGMA journal_mode=WAL")

    @contextmanager
    def _connect(self) -> Iterator[sqlite3.Connection]:
        conn = sqlite3.connect(
            self.db_path,
            timeout=self.timeout,
            isolation_level=None,
        )
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys=ON")
        conn.execute(f"PRAGMA busy_timeout={int(self.timeout * 1000)}")
        try:
            yield conn
        finally:
            conn.close()

    @contextmanager
    def _tx(self, *, immediate: bool = False) -> Iterator[sqlite3.Connection]:
        with self._connect() as conn:
            conn.execute("BEGIN IMMEDIATE" if immediate else "BEGIN")
            try:
                yield conn
            except Exception:
                conn.rollback()
                raise
            else:
                conn.commit()

    @staticmethod
    def _now() -> float:
        return time.time()

    @staticmethod
    def _row_to_task(row: sqlite3.Row) -> Task:
        return Task(**dict(row))

    @staticmethod
    def _json(value: Mapping[str, Any] | Sequence[Any] | str | None) -> str:
        if value is None:
            return "{}"
        if isinstance(value, str):
            return value
        return json.dumps(value, sort_keys=True, separators=(",", ":"))

    def _event(
        self,
        conn: sqlite3.Connection,
        event_type: str,
        *,
        task_id: str | None = None,
        agent_id: str | None = None,
        payload: Mapping[str, Any] | None = None,
        at: float | None = None,
    ) -> None:
        conn.execute(
            "INSERT INTO events(at, task_id, agent_id, event_type, payload) VALUES (?, ?, ?, ?, ?)",
            (at or self._now(), task_id, agent_id, event_type, self._json(payload)),
        )

    def _touch_agent(
        self,
        conn: sqlite3.Connection,
        agent_id: str,
        *,
        metadata: Mapping[str, Any] | None = None,
        at: float | None = None,
    ) -> None:
        now = at or self._now()
        conn.execute(
            """
            INSERT INTO agents(id, first_seen_at, last_seen_at, metadata)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                last_seen_at=excluded.last_seen_at,
                metadata=CASE
                    WHEN excluded.metadata = '{}' THEN agents.metadata
                    ELSE excluded.metadata
                END
            """,
            (agent_id, now, now, self._json(metadata)),
        )

    def _require_task(self, conn: sqlite3.Connection, task_id: str) -> sqlite3.Row:
        row = conn.execute("SELECT * FROM tasks WHERE id=?", (task_id,)).fetchone()
        if row is None:
            raise NotFound(f"task not found: {task_id}")
        return row

    def add_task(
        self,
        title: str,
        *,
        description: str = "",
        kind: str = "task",
        parent_id: str | None = None,
        priority: int = 0,
        max_attempts: int = 3,
        task_id: str | None = None,
    ) -> Task:
        if not title.strip():
            raise ValidationError("title cannot be empty")
        if kind not in {"task", "group"}:
            raise ValidationError("kind must be 'task' or 'group'")
        if max_attempts < 1:
            raise ValidationError("max_attempts must be at least 1")
        task_id = task_id or str(uuid.uuid4())
        now = self._now()
        with self._tx(immediate=True) as conn:
            if parent_id:
                parent = self._require_task(conn, parent_id)
                if parent["kind"] != "group":
                    raise ValidationError("parent must be a group")
                if parent["status"] in {"completed", "failed", "cancelled"}:
                    raise ValidationError("cannot add a child to a terminal group")
            try:
                conn.execute(
                    """
                    INSERT INTO tasks(
                        id, title, description, kind, parent_id, status, priority,
                        created_at, updated_at, max_attempts
                    ) VALUES (?, ?, ?, ?, ?, 'pending', ?, ?, ?, ?)
                    """,
                    (
                        task_id,
                        title.strip(),
                        description,
                        kind,
                        parent_id,
                        priority,
                        now,
                        now,
                        max_attempts,
                    ),
                )
            except sqlite3.IntegrityError as exc:
                raise ValidationError(str(exc)) from exc
            self._event(
                conn,
                "task_created",
                task_id=task_id,
                payload={"kind": kind, "parent_id": parent_id, "priority": priority},
                at=now,
            )
            if parent_id:
                self._recompute_ancestors(conn, parent_id, now=now)
            row = self._require_task(conn, task_id)
            return self._row_to_task(row)

    def add_dependency(self, task_id: str, depends_on_id: str) -> None:
        if task_id == depends_on_id:
            raise ValidationError("a task cannot depend on itself")
        now = self._now()
        with self._tx(immediate=True) as conn:
            task = self._require_task(conn, task_id)
            self._require_task(conn, depends_on_id)
            if task["status"] not in {"pending"}:
                raise ValidationError("dependencies can only be changed while task is pending")
            cycle = conn.execute(
                """
                WITH RECURSIVE reachable(id) AS (
                    SELECT depends_on_id FROM dependencies WHERE task_id = ?
                    UNION
                    SELECT d.depends_on_id
                    FROM dependencies d
                    JOIN reachable r ON d.task_id = r.id
                )
                SELECT 1 FROM reachable WHERE id = ? LIMIT 1
                """,
                (depends_on_id, task_id),
            ).fetchone()
            if cycle:
                raise ValidationError("dependency would create a cycle")
            try:
                conn.execute(
                    "INSERT INTO dependencies(task_id, depends_on_id, created_at) VALUES (?, ?, ?)",
                    (task_id, depends_on_id, now),
                )
            except sqlite3.IntegrityError as exc:
                raise ValidationError(str(exc)) from exc
            self._event(
                conn,
                "dependency_added",
                task_id=task_id,
                payload={"depends_on_id": depends_on_id},
                at=now,
            )

    def remove_dependency(self, task_id: str, depends_on_id: str) -> None:
        now = self._now()
        with self._tx(immediate=True) as conn:
            task = self._require_task(conn, task_id)
            if task["status"] != "pending":
                raise ValidationError("dependencies can only be changed while task is pending")
            changed = conn.execute(
                "DELETE FROM dependencies WHERE task_id=? AND depends_on_id=?",
                (task_id, depends_on_id),
            ).rowcount
            if not changed:
                raise NotFound(f"dependency not found: {task_id} -> {depends_on_id}")
            self._event(
                conn,
                "dependency_removed",
                task_id=task_id,
                payload={"depends_on_id": depends_on_id},
                at=now,
            )

    def get_task(self, task_id: str) -> Task:
        with self._connect() as conn:
            return self._row_to_task(self._require_task(conn, task_id))

    def get_dependencies(self, task_id: str) -> list[Task]:
        with self._connect() as conn:
            self._require_task(conn, task_id)
            rows = conn.execute(
                """
                SELECT t.* FROM tasks t
                JOIN dependencies d ON d.depends_on_id=t.id
                WHERE d.task_id=? ORDER BY t.created_at, t.id
                """,
                (task_id,),
            ).fetchall()
            return [self._row_to_task(r) for r in rows]

    def list_tasks(
        self,
        *,
        status: str | None = None,
        parent_id: str | None = None,
        agent_id: str | None = None,
    ) -> list[Task]:
        clauses: list[str] = []
        params: list[Any] = []
        if status:
            clauses.append("status=?")
            params.append(status)
        if parent_id is not None:
            clauses.append("parent_id=?")
            params.append(parent_id)
        if agent_id:
            clauses.append("agent_id=?")
            params.append(agent_id)
        where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        with self._connect() as conn:
            rows = conn.execute(
                f"SELECT * FROM tasks {where} ORDER BY priority DESC, created_at, id",
                params,
            ).fetchall()
            return [self._row_to_task(r) for r in rows]

    def _ready_sql(self, *, include_expired: bool = True, scope_id: str | None = None) -> tuple[str, list[Any]]:
        now = self._now()
        params: list[Any] = [now]
        state_clause = "(t.status='pending' OR (t.status IN ('leased','running') AND t.lease_until <= ?))"
        if not include_expired:
            state_clause = "t.status='pending'"
            params = []

        scope_clause = ""
        if scope_id:
            scope_clause = """
            AND EXISTS (
                WITH RECURSIVE lineage(id) AS (
                    SELECT t.id
                    UNION ALL
                    SELECT x.parent_id FROM tasks x JOIN lineage l ON x.id=l.id
                    WHERE x.parent_id IS NOT NULL
                )
                SELECT 1 FROM lineage WHERE id=?
            )
            """
            params.append(scope_id)

        sql = f"""
            SELECT t.*
            FROM tasks t
            WHERE t.kind='task'
              AND {state_clause}
              AND t.attempts < t.max_attempts
              {scope_clause}
              AND NOT EXISTS (
                  WITH RECURSIVE lineage(id) AS (
                      SELECT t.id
                      UNION ALL
                      SELECT x.parent_id
                      FROM tasks x JOIN lineage l ON x.id=l.id
                      WHERE x.parent_id IS NOT NULL
                  )
                  SELECT 1
                  FROM lineage l
                  JOIN dependencies d ON d.task_id=l.id
                  JOIN tasks dep ON dep.id=d.depends_on_id
                  WHERE dep.status <> 'completed'
              )
              AND NOT EXISTS (
                  WITH RECURSIVE ancestors(id) AS (
                      SELECT t.parent_id WHERE t.parent_id IS NOT NULL
                      UNION ALL
                      SELECT x.parent_id
                      FROM tasks x JOIN ancestors a ON x.id=a.id
                      WHERE x.parent_id IS NOT NULL
                  )
                  SELECT 1 FROM ancestors a
                  JOIN tasks g ON g.id=a.id
                  WHERE g.status IN ('failed','cancelled')
              )
            ORDER BY t.priority DESC, t.created_at, t.id
        """
        return sql, params

    def ready_tasks(self, *, scope_id: str | None = None, limit: int | None = None) -> list[Task]:
        sql, params = self._ready_sql(scope_id=scope_id)
        if limit is not None:
            sql += " LIMIT ?"
            params.append(limit)
        with self._connect() as conn:
            if scope_id:
                self._require_task(conn, scope_id)
            rows = conn.execute(sql, params).fetchall()
            return [self._row_to_task(r) for r in rows]

    def claim(
        self,
        agent_id: str,
        *,
        lease_seconds: int = 900,
        scope_id: str | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> Task | None:
        if not agent_id.strip():
            raise ValidationError("agent_id cannot be empty")
        if lease_seconds < 1:
            raise ValidationError("lease_seconds must be positive")
        now = self._now()
        with self._tx(immediate=True) as conn:
            if scope_id:
                self._require_task(conn, scope_id)
            self._touch_agent(conn, agent_id, metadata=metadata, at=now)
            sql, params = self._ready_sql(scope_id=scope_id)
            row = conn.execute(sql + " LIMIT 1", params).fetchone()
            if row is None:
                return None
            reclaimed = row["status"] in {"leased", "running"}
            updated = conn.execute(
                """
                UPDATE tasks SET
                    status='leased', agent_id=?, lease_until=?, heartbeat_at=?,
                    attempts=attempts+1, updated_at=?, error=NULL
                WHERE id=?
                  AND (
                    status='pending'
                    OR (status IN ('leased','running') AND lease_until <= ?)
                  )
                """,
                (agent_id, now + lease_seconds, now, now, row["id"], now),
            ).rowcount
            if updated != 1:
                return None
            self._event(
                conn,
                "task_reclaimed" if reclaimed else "task_claimed",
                task_id=row["id"],
                agent_id=agent_id,
                payload={"lease_seconds": lease_seconds, "previous_agent": row["agent_id"]},
                at=now,
            )
            if row["parent_id"]:
                self._recompute_ancestors(conn, row["parent_id"], now=now)
            return self._row_to_task(self._require_task(conn, row["id"]))

    def start(self, task_id: str, agent_id: str) -> Task:
        now = self._now()
        with self._tx(immediate=True) as conn:
            row = self._assert_lease(conn, task_id, agent_id, now)
            if row["status"] != "leased":
                raise ValidationError("only a leased task can be started")
            conn.execute(
                "UPDATE tasks SET status='running', updated_at=? WHERE id=?",
                (now, task_id),
            )
            self._touch_agent(conn, agent_id, at=now)
            self._event(conn, "task_started", task_id=task_id, agent_id=agent_id, at=now)
            if row["parent_id"]:
                self._recompute_ancestors(conn, row["parent_id"], now=now)
            return self._row_to_task(self._require_task(conn, task_id))

    def heartbeat(self, task_id: str, agent_id: str, *, lease_seconds: int = 900) -> Task:
        if lease_seconds < 1:
            raise ValidationError("lease_seconds must be positive")
        now = self._now()
        with self._tx(immediate=True) as conn:
            self._assert_lease(conn, task_id, agent_id, now)
            conn.execute(
                "UPDATE tasks SET lease_until=?, heartbeat_at=?, updated_at=? WHERE id=?",
                (now + lease_seconds, now, now, task_id),
            )
            self._touch_agent(conn, agent_id, at=now)
            self._event(
                conn,
                "heartbeat",
                task_id=task_id,
                agent_id=agent_id,
                payload={"lease_seconds": lease_seconds},
                at=now,
            )
            return self._row_to_task(self._require_task(conn, task_id))

    def complete(self, task_id: str, agent_id: str, *, result: str | None = None) -> Task:
        now = self._now()
        with self._tx(immediate=True) as conn:
            row = self._assert_lease(conn, task_id, agent_id, now)
            conn.execute(
                """
                UPDATE tasks SET status='completed', result=?, error=NULL,
                    completed_at=?, updated_at=?, agent_id=NULL, lease_until=NULL, heartbeat_at=NULL
                WHERE id=?
                """,
                (result, now, now, task_id),
            )
            self._touch_agent(conn, agent_id, at=now)
            self._event(
                conn,
                "task_completed",
                task_id=task_id,
                agent_id=agent_id,
                payload={"result": result},
                at=now,
            )
            if row["parent_id"]:
                self._recompute_ancestors(conn, row["parent_id"], now=now)
            return self._row_to_task(self._require_task(conn, task_id))

    def fail(
        self,
        task_id: str,
        agent_id: str,
        *,
        error: str,
        retry: bool = False,
    ) -> Task:
        now = self._now()
        with self._tx(immediate=True) as conn:
            row = self._assert_lease(conn, task_id, agent_id, now)
            retry_allowed = retry and row["attempts"] < row["max_attempts"]
            status = "pending" if retry_allowed else "failed"
            conn.execute(
                """
                UPDATE tasks SET status=?, error=?, updated_at=?, completed_at=?,
                    agent_id=NULL, lease_until=NULL, heartbeat_at=NULL
                WHERE id=?
                """,
                (status, error, now, None if retry_allowed else now, task_id),
            )
            self._touch_agent(conn, agent_id, at=now)
            self._event(
                conn,
                "task_requeued" if retry_allowed else "task_failed",
                task_id=task_id,
                agent_id=agent_id,
                payload={"error": error, "retry_requested": retry},
                at=now,
            )
            if row["parent_id"]:
                self._recompute_ancestors(conn, row["parent_id"], now=now)
            return self._row_to_task(self._require_task(conn, task_id))

    def release(self, task_id: str, agent_id: str) -> Task:
        now = self._now()
        with self._tx(immediate=True) as conn:
            row = self._assert_lease(conn, task_id, agent_id, now, allow_expired=True)
            conn.execute(
                """
                UPDATE tasks SET status='pending', agent_id=NULL, lease_until=NULL,
                    heartbeat_at=NULL, updated_at=? WHERE id=?
                """,
                (now, task_id),
            )
            self._touch_agent(conn, agent_id, at=now)
            self._event(conn, "task_released", task_id=task_id, agent_id=agent_id, at=now)
            if row["parent_id"]:
                self._recompute_ancestors(conn, row["parent_id"], now=now)
            return self._row_to_task(self._require_task(conn, task_id))

    def cancel(self, task_id: str, *, reason: str | None = None) -> Task:
        now = self._now()
        with self._tx(immediate=True) as conn:
            row = self._require_task(conn, task_id)
            if row["status"] == "completed":
                raise ValidationError("a completed task cannot be cancelled")
            if row["kind"] == "group":
                active = conn.execute(
                    """
                    WITH RECURSIVE descendants(id) AS (
                        SELECT id FROM tasks WHERE parent_id=?
                        UNION ALL
                        SELECT t.id FROM tasks t JOIN descendants d ON t.parent_id=d.id
                    )
                    SELECT 1 FROM tasks t JOIN descendants d ON t.id=d.id
                    WHERE t.status IN ('leased','running') LIMIT 1
                    """,
                    (task_id,),
                ).fetchone()
                if active:
                    raise ValidationError("cannot cancel a group with leased or running descendants")
            conn.execute(
                """
                UPDATE tasks SET status='cancelled', error=?, completed_at=?, updated_at=?,
                    agent_id=NULL, lease_until=NULL, heartbeat_at=NULL WHERE id=?
                """,
                (reason, now, now, task_id),
            )
            self._event(
                conn,
                "task_cancelled",
                task_id=task_id,
                payload={"reason": reason},
                at=now,
            )
            if row["parent_id"]:
                self._recompute_ancestors(conn, row["parent_id"], now=now)
            return self._row_to_task(self._require_task(conn, task_id))

    def _assert_lease(
        self,
        conn: sqlite3.Connection,
        task_id: str,
        agent_id: str,
        now: float,
        *,
        allow_expired: bool = False,
    ) -> sqlite3.Row:
        row = self._require_task(conn, task_id)
        if row["kind"] != "task":
            raise ValidationError("groups cannot be leased")
        if row["status"] not in {"leased", "running"}:
            raise LeaseConflict(f"task is not leased: {task_id}")
        if row["agent_id"] != agent_id:
            raise LeaseConflict(f"task is leased by {row['agent_id']!r}, not {agent_id!r}")
        if not allow_expired and row["lease_until"] <= now:
            raise LeaseConflict("lease has expired")
        return row

    def _recompute_ancestors(
        self,
        conn: sqlite3.Connection,
        group_id: str,
        *,
        now: float,
    ) -> None:
        current: str | None = group_id
        while current:
            group = self._require_task(conn, current)
            if group["kind"] != "group":
                raise ValidationError("hierarchy contains a non-group parent")
            children = conn.execute(
                "SELECT status FROM tasks WHERE parent_id=?",
                (current,),
            ).fetchall()
            statuses = [r["status"] for r in children]
            old = group["status"]
            if not statuses:
                new = "pending"
            elif any(s == "failed" for s in statuses):
                new = "failed"
            elif all(s == "cancelled" for s in statuses):
                new = "cancelled"
            elif all(s in {"completed", "cancelled"} for s in statuses):
                new = "completed"
            elif any(s in {"leased", "running", "completed"} for s in statuses):
                new = "running"
            else:
                new = "pending"
            completed_at = now if new in {"completed", "failed", "cancelled"} else None
            if old != new or group["completed_at"] != completed_at:
                conn.execute(
                    "UPDATE tasks SET status=?, completed_at=?, updated_at=? WHERE id=?",
                    (new, completed_at, now, current),
                )
                if old != new:
                    self._event(
                        conn,
                        "group_status_changed",
                        task_id=current,
                        payload={"from": old, "to": new},
                        at=now,
                    )
            current = group["parent_id"]

    def events(self, *, task_id: str | None = None, limit: int = 100) -> list[dict[str, Any]]:
        with self._connect() as conn:
            if task_id:
                self._require_task(conn, task_id)
                rows = conn.execute(
                    "SELECT * FROM events WHERE task_id=? ORDER BY seq DESC LIMIT ?",
                    (task_id, limit),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM events ORDER BY seq DESC LIMIT ?",
                    (limit,),
                ).fetchall()
            output = []
            for row in reversed(rows):
                item = dict(row)
                try:
                    item["payload"] = json.loads(item["payload"])
                except json.JSONDecodeError:
                    pass
                output.append(item)
            return output

    def agents(self) -> list[dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute("SELECT * FROM agents ORDER BY last_seen_at DESC").fetchall()
            output = []
            for row in rows:
                item = dict(row)
                try:
                    item["metadata"] = json.loads(item["metadata"])
                except json.JSONDecodeError:
                    pass
                output.append(item)
            return output

    def validate(self) -> list[str]:
        """Return invariant violations; an empty list means the database is valid."""
        problems: list[str] = []
        with self._connect() as conn:
            fk = conn.execute("PRAGMA foreign_key_check").fetchall()
            problems.extend(f"foreign key violation: {tuple(r)}" for r in fk)

            dep_cycle = conn.execute(
                """
                WITH RECURSIVE walk(start, node, path, cycle) AS (
                    SELECT task_id, depends_on_id, task_id || ',' || depends_on_id, 0
                    FROM dependencies
                    UNION ALL
                    SELECT w.start, d.depends_on_id,
                           w.path || ',' || d.depends_on_id,
                           instr(',' || w.path || ',', ',' || d.depends_on_id || ',') > 0
                    FROM walk w JOIN dependencies d ON d.task_id=w.node
                    WHERE w.cycle=0
                )
                SELECT start, node, path FROM walk WHERE cycle=1 LIMIT 20
                """
            ).fetchall()
            problems.extend(f"dependency cycle: {r['path']}" for r in dep_cycle)

            hierarchy_cycle = conn.execute(
                """
                WITH RECURSIVE walk(start, node, path, cycle) AS (
                    SELECT id, parent_id, id || ',' || parent_id, 0
                    FROM tasks WHERE parent_id IS NOT NULL
                    UNION ALL
                    SELECT w.start, t.parent_id,
                           w.path || ',' || t.parent_id,
                           instr(',' || w.path || ',', ',' || t.parent_id || ',') > 0
                    FROM walk w JOIN tasks t ON t.id=w.node
                    WHERE t.parent_id IS NOT NULL AND w.cycle=0
                )
                SELECT start, node, path FROM walk WHERE cycle=1 LIMIT 20
                """
            ).fetchall()
            problems.extend(f"hierarchy cycle: {r['path']}" for r in hierarchy_cycle)

            bad_parents = conn.execute(
                """
                SELECT child.id, child.parent_id
                FROM tasks child JOIN tasks parent ON parent.id=child.parent_id
                WHERE parent.kind <> 'group'
                """
            ).fetchall()
            problems.extend(
                f"task {r['id']} has non-group parent {r['parent_id']}" for r in bad_parents
            )
        return problems

    def tree_rows(self, root_id: str | None = None) -> list[dict[str, Any]]:
        with self._connect() as conn:
            if root_id:
                self._require_task(conn, root_id)
                rows = conn.execute(
                    """
                    WITH RECURSIVE tree(id, depth, path) AS (
                        SELECT id, 0, printf('%08d:%s', 99999999-priority, id)
                        FROM tasks WHERE id=?
                        UNION ALL
                        SELECT t.id, tree.depth+1,
                               tree.path || '/' || printf('%08d:%s', 99999999-t.priority, t.id)
                        FROM tasks t JOIN tree ON t.parent_id=tree.id
                    )
                    SELECT tasks.*, tree.depth FROM tree JOIN tasks ON tasks.id=tree.id
                    ORDER BY tree.path
                    """,
                    (root_id,),
                ).fetchall()
            else:
                rows = conn.execute(
                    """
                    WITH RECURSIVE tree(id, depth, path) AS (
                        SELECT id, 0, printf('%08d:%s', 99999999-priority, id)
                        FROM tasks WHERE parent_id IS NULL
                        UNION ALL
                        SELECT t.id, tree.depth+1,
                               tree.path || '/' || printf('%08d:%s', 99999999-t.priority, t.id)
                        FROM tasks t JOIN tree ON t.parent_id=tree.id
                    )
                    SELECT tasks.*, tree.depth FROM tree JOIN tasks ON tasks.id=tree.id
                    ORDER BY tree.path
                    """
                ).fetchall()
            return [dict(r) for r in rows]

    def dot(self) -> str:
        with self._connect() as conn:
            tasks = conn.execute("SELECT * FROM tasks ORDER BY created_at, id").fetchall()
            deps = conn.execute("SELECT * FROM dependencies ORDER BY task_id, depends_on_id").fetchall()
        lines = ["digraph task_network {", "  rankdir=LR;", "  node [shape=box];"]
        for task in tasks:
            label = f"{task['title']}\\n{task['status']}"
            shape = "folder" if task["kind"] == "group" else "box"
            lines.append(f'  "{task["id"]}" [label={json.dumps(label)}, shape={shape}];')
        for task in tasks:
            if task["parent_id"]:
                lines.append(
                    f'  "{task["parent_id"]}" -> "{task["id"]}" '
                    '[style=dotted, arrowhead=none, label="contains"];'
                )
        for dep in deps:
            lines.append(
                f'  "{dep["depends_on_id"]}" -> "{dep["task_id"]}" [label="unblocks"];'
            )
        lines.append("}")
        return "\n".join(lines) + "\n"
EOF

cat > /mnt/data/dag-agent-sync/src/dag_agent_sync/cli.py <<'EOF'
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .store import Coordinator, DagError, Task


def iso(ts: float | None) -> str:
    if ts is None:
        return "-"
    return datetime.fromtimestamp(ts, timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def short(task_id: str | None) -> str:
    return "-" if task_id is None else task_id[:8]


def task_json(task: Task) -> dict[str, Any]:
    data = task.to_dict()
    for key in ("created_at", "updated_at", "completed_at", "lease_until", "heartbeat_at"):
        data[key + "_iso"] = iso(data[key])
    return data


def print_tasks(tasks: list[Task]) -> None:
    if not tasks:
        print("No tasks.")
        return
    headers = ("ID", "KIND", "STATUS", "PRI", "ATT", "AGENT", "LEASE", "TITLE")
    rows = []
    for t in tasks:
        rows.append(
            (
                short(t.id),
                t.kind,
                t.status,
                str(t.priority),
                f"{t.attempts}/{t.max_attempts}",
                t.agent_id or "-",
                iso(t.lease_until),
                t.title,
            )
        )
    widths = [max(len(headers[i]), *(len(r[i]) for r in rows)) for i in range(len(headers))]
    fmt = "  ".join(f"{{:<{w}}}" for w in widths)
    print(fmt.format(*headers))
    print(fmt.format(*("-" * w for w in widths)))
    for row in rows:
        print(fmt.format(*row))


def json_dump(value: Any) -> None:
    print(json.dumps(value, indent=2, sort_keys=True))


def add_common_output(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--json", action="store_true", help="emit JSON")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="dag-sync",
        description="Synchronize multiple coding agents over a hierarchical DAG in SQLite.",
    )
    parser.add_argument(
        "--db",
        default=".dag-sync.sqlite3",
        help="SQLite database path (default: .dag-sync.sqlite3)",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("init", help="initialize the database")

    p = sub.add_parser("add", help="add a task or group")
    p.add_argument("title")
    p.add_argument("--description", default="")
    p.add_argument("--kind", choices=("task", "group"), default="task")
    p.add_argument("--parent")
    p.add_argument("--priority", type=int, default=0)
    p.add_argument("--max-attempts", type=int, default=3)
    p.add_argument("--id", dest="task_id")
    add_common_output(p)

    p = sub.add_parser("depend", help="make TASK depend on PREREQUISITE")
    p.add_argument("task")
    p.add_argument("prerequisite")

    p = sub.add_parser("undepend", help="remove a dependency")
    p.add_argument("task")
    p.add_argument("prerequisite")

    p = sub.add_parser("list", help="list tasks")
    p.add_argument("--status")
    p.add_argument("--parent")
    p.add_argument("--agent")
    add_common_output(p)

    p = sub.add_parser("ready", help="list claimable leaf tasks")
    p.add_argument("--scope", help="restrict to a group/task subtree")
    p.add_argument("--limit", type=int)
    add_common_output(p)

    p = sub.add_parser("claim", help="atomically claim one ready task")
    p.add_argument("--agent", required=True)
    p.add_argument("--lease", type=int, default=900, help="lease seconds")
    p.add_argument("--scope")
    p.add_argument("--metadata", help="JSON object describing the agent")
    add_common_output(p)

    for name, help_text in (
        ("start", "mark a leased task running"),
        ("heartbeat", "extend a task lease"),
        ("complete", "complete a leased task"),
        ("release", "release a lease back to pending"),
    ):
        p = sub.add_parser(name, help=help_text)
        p.add_argument("task")
        p.add_argument("--agent", required=True)
        if name == "heartbeat":
            p.add_argument("--lease", type=int, default=900)
        if name == "complete":
            p.add_argument("--result")
        add_common_output(p)

    p = sub.add_parser("fail", help="fail or requeue a leased task")
    p.add_argument("task")
    p.add_argument("--agent", required=True)
    p.add_argument("--error", required=True)
    p.add_argument("--retry", action="store_true")
    add_common_output(p)

    p = sub.add_parser("cancel", help="cancel a task")
    p.add_argument("task")
    p.add_argument("--reason")
    add_common_output(p)

    p = sub.add_parser("show", help="show one task and its prerequisites")
    p.add_argument("task")
    add_common_output(p)

    p = sub.add_parser("tree", help="render the hierarchy")
    p.add_argument("--root")
    add_common_output(p)

    p = sub.add_parser("events", help="show audit events")
    p.add_argument("--task")
    p.add_argument("--limit", type=int, default=100)
    add_common_output(p)

    p = sub.add_parser("agents", help="show registered agents")
    add_common_output(p)

    p = sub.add_parser("dot", help="emit Graphviz DOT")
    p.add_argument("--output", "-o")

    p = sub.add_parser("validate", help="validate graph and database invariants")
    add_common_output(p)

    return parser


def ensure_initialized(coord: Coordinator, command: str) -> None:
    if command == "init":
        return
    if not Path(coord.db_path).exists():
        raise DagError(f"database does not exist: {coord.db_path}; run 'dag-sync --db {coord.db_path} init'")


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    coord = Coordinator(args.db)
    try:
        if args.command == "init":
            coord.initialize()
            print(f"Initialized {args.db}")
            return 0
        ensure_initialized(coord, args.command)

        if args.command == "add":
            task = coord.add_task(
                args.title,
                description=args.description,
                kind=args.kind,
                parent_id=args.parent,
                priority=args.priority,
                max_attempts=args.max_attempts,
                task_id=args.task_id,
            )
            json_dump(task_json(task)) if args.json else print(task.id)
        elif args.command == "depend":
            coord.add_dependency(args.task, args.prerequisite)
            print(f"{args.task} depends on {args.prerequisite}")
        elif args.command == "undepend":
            coord.remove_dependency(args.task, args.prerequisite)
            print(f"removed dependency {args.task} -> {args.prerequisite}")
        elif args.command == "list":
            tasks = coord.list_tasks(status=args.status, parent_id=args.parent, agent_id=args.agent)
            json_dump([task_json(t) for t in tasks]) if args.json else print_tasks(tasks)
        elif args.command == "ready":
            tasks = coord.ready_tasks(scope_id=args.scope, limit=args.limit)
            json_dump([task_json(t) for t in tasks]) if args.json else print_tasks(tasks)
        elif args.command == "claim":
            metadata = json.loads(args.metadata) if args.metadata else None
            if metadata is not None and not isinstance(metadata, dict):
                raise DagError("--metadata must be a JSON object")
            task = coord.claim(args.agent, lease_seconds=args.lease, scope_id=args.scope, metadata=metadata)
            if task is None:
                if args.json:
                    json_dump(None)
                else:
                    print("No ready task.")
                return 3
            json_dump(task_json(task)) if args.json else print(task.id)
        elif args.command == "start":
            task = coord.start(args.task, args.agent)
            json_dump(task_json(task)) if args.json else print(f"started {task.id}")
        elif args.command == "heartbeat":
            task = coord.heartbeat(args.task, args.agent, lease_seconds=args.lease)
            json_dump(task_json(task)) if args.json else print(f"lease extended to {iso(task.lease_until)}")
        elif args.command == "complete":
            task = coord.complete(args.task, args.agent, result=args.result)
            json_dump(task_json(task)) if args.json else print(f"completed {task.id}")
        elif args.command == "fail":
            task = coord.fail(args.task, args.agent, error=args.error, retry=args.retry)
            json_dump(task_json(task)) if args.json else print(f"{task.status} {task.id}")
        elif args.command == "release":
            task = coord.release(args.task, args.agent)
            json_dump(task_json(task)) if args.json else print(f"released {task.id}")
        elif args.command == "cancel":
            task = coord.cancel(args.task, reason=args.reason)
            json_dump(task_json(task)) if args.json else print(f"cancelled {task.id}")
        elif args.command == "show":
            task = coord.get_task(args.task)
            deps = coord.get_dependencies(args.task)
            data = task_json(task)
            data["dependencies"] = [task_json(t) for t in deps]
            if args.json:
                json_dump(data)
            else:
                print_tasks([task])
                print("\nPrerequisites:")
                print_tasks(deps)
        elif args.command == "tree":
            rows = coord.tree_rows(args.root)
            if args.json:
                json_dump(rows)
            elif not rows:
                print("No tasks.")
            else:
                for row in rows:
                    connector = "  " * row["depth"] + ("└─ " if row["depth"] else "")
                    print(
                        f"{connector}{short(row['id'])} [{row['kind']}/{row['status']}] "
                        f"p={row['priority']} {row['title']}"
                    )
        elif args.command == "events":
            rows = coord.events(task_id=args.task, limit=args.limit)
            if args.json:
                json_dump(rows)
            else:
                for row in rows:
                    print(
                        f"{row['seq']:>5} {iso(row['at'])} {row['event_type']:<22} "
                        f"task={short(row['task_id'])} agent={row['agent_id'] or '-'} "
                        f"{json.dumps(row['payload'], sort_keys=True)}"
                    )
        elif args.command == "agents":
            rows = coord.agents()
            if args.json:
                json_dump(rows)
            else:
                for row in rows:
                    print(
                        f"{row['id']}  last_seen={iso(row['last_seen_at'])}  "
                        f"metadata={json.dumps(row['metadata'], sort_keys=True)}"
                    )
        elif args.command == "dot":
            text = coord.dot()
            if args.output:
                Path(args.output).write_text(text, encoding="utf-8")
            else:
                print(text, end="")
        elif args.command == "validate":
            problems = coord.validate()
            if args.json:
                json_dump(problems)
            elif problems:
                for problem in problems:
                    print(problem)
            else:
                print("OK")
            return 1 if problems else 0
        return 0
    except (DagError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
EOF

cat > /mnt/data/dag-agent-sync/src/dag_agent_sync/__main__.py <<'EOF'
from .cli import main

raise SystemExit(main())
EOF

cat > /mnt/data/dag-agent-sync/tests/test_coordinator.py <<'EOF'
from __future__ import annotations

import threading
import time
from pathlib import Path

import pytest

from dag_agent_sync import Coordinator, LeaseConflict, ValidationError


@pytest.fixture
def coord(tmp_path: Path) -> Coordinator:
    c = Coordinator(tmp_path / "tasks.sqlite3")
    c.initialize()
    return c


def test_dependency_readiness_and_group_rollup(coord: Coordinator) -> None:
    group = coord.add_task("Feature", kind="group")
    design = coord.add_task("Design", parent_id=group.id)
    build = coord.add_task("Build", parent_id=group.id)
    coord.add_dependency(build.id, design.id)

    assert [t.id for t in coord.ready_tasks()] == [design.id]
    claimed = coord.claim("agent-a", lease_seconds=30)
    assert claimed and claimed.id == design.id
    coord.start(design.id, "agent-a")
    coord.complete(design.id, "agent-a", result="done")

    assert [t.id for t in coord.ready_tasks()] == [build.id]
    coord.claim("agent-b", lease_seconds=30)
    coord.complete(build.id, "agent-b")
    assert coord.get_task(group.id).status == "completed"


def test_group_dependency_blocks_entire_subtree(coord: Coordinator) -> None:
    prep = coord.add_task("Prepare")
    group = coord.add_task("Implementation", kind="group")
    child = coord.add_task("Code", parent_id=group.id)
    coord.add_dependency(group.id, prep.id)

    assert [t.id for t in coord.ready_tasks()] == [prep.id]
    coord.claim("agent", lease_seconds=30)
    coord.complete(prep.id, "agent")
    assert [t.id for t in coord.ready_tasks()] == [child.id]


def test_cycle_rejected(coord: Coordinator) -> None:
    a = coord.add_task("A")
    b = coord.add_task("B")
    c = coord.add_task("C")
    coord.add_dependency(a.id, b.id)
    coord.add_dependency(b.id, c.id)
    with pytest.raises(ValidationError):
        coord.add_dependency(c.id, a.id)


def test_concurrent_claim_is_unique(coord: Coordinator) -> None:
    task = coord.add_task("Only once")
    barrier = threading.Barrier(3)
    claimed: list[str | None] = []
    lock = threading.Lock()

    def worker(agent: str) -> None:
        local = Coordinator(coord.db_path)
        barrier.wait()
        result = local.claim(agent, lease_seconds=30)
        with lock:
            claimed.append(result.id if result else None)

    threads = [threading.Thread(target=worker, args=(f"agent-{i}",)) for i in range(2)]
    for thread in threads:
        thread.start()
    barrier.wait()
    for thread in threads:
        thread.join()

    assert claimed.count(task.id) == 1
    assert claimed.count(None) == 1


def test_expired_lease_can_be_reclaimed(coord: Coordinator) -> None:
    task = coord.add_task("Recover")
    first = coord.claim("agent-a", lease_seconds=1)
    assert first and first.id == task.id
    time.sleep(1.05)
    second = coord.claim("agent-b", lease_seconds=30)
    assert second and second.id == task.id
    assert second.agent_id == "agent-b"
    assert second.attempts == 2
    with pytest.raises(LeaseConflict):
        coord.complete(task.id, "agent-a")


def test_retry_respects_max_attempts(coord: Coordinator) -> None:
    task = coord.add_task("Flaky", max_attempts=2)
    coord.claim("a", lease_seconds=30)
    first = coord.fail(task.id, "a", error="x", retry=True)
    assert first.status == "pending"
    coord.claim("a", lease_seconds=30)
    second = coord.fail(task.id, "a", error="y", retry=True)
    assert second.status == "failed"
    assert coord.ready_tasks() == []


def test_validation_is_clean(coord: Coordinator) -> None:
    group = coord.add_task("G", kind="group")
    a = coord.add_task("A", parent_id=group.id)
    b = coord.add_task("B", parent_id=group.id)
    coord.add_dependency(b.id, a.id)
    assert coord.validate() == []
EOF

cat > /mnt/data/dag-agent-sync/README.md <<'EOF'
# dag-agent-sync

A dependency-free Python CLI and library for coordinating multiple coding agents over a **hierarchical DAG** stored in SQLite.

It provides:

- nested groups for epics, features, workstreams, or repositories;
- dependency edges with cycle prevention;
- atomic task claims across concurrent processes;
- expiring leases and heartbeats for crashed-agent recovery;
- retries with attempt limits;
- group-level dependencies inherited by every descendant;
- automatic group status rollups;
- audit events, agent registry, JSON output, and Graphviz export.

## Install

```bash
python -m venv .venv
. .venv/bin/activate
pip install -e .
```

Python 3.10+ is required. Runtime dependencies: none.

## Create a task network

```bash
dag-sync --db work.sqlite3 init

EPIC=$(dag-sync --db work.sqlite3 add "Authentication" --kind group)
SPEC=$(dag-sync --db work.sqlite3 add "Write API contract" --parent "$EPIC" --priority 100)
API=$(dag-sync --db work.sqlite3 add "Implement API" --parent "$EPIC" --priority 80)
UI=$(dag-sync --db work.sqlite3 add "Implement UI" --parent "$EPIC" --priority 70)
TEST=$(dag-sync --db work.sqlite3 add "Integration tests" --parent "$EPIC" --priority 60)

dag-sync --db work.sqlite3 depend "$API" "$SPEC"
dag-sync --db work.sqlite3 depend "$UI" "$SPEC"
dag-sync --db work.sqlite3 depend "$TEST" "$API"
dag-sync --db work.sqlite3 depend "$TEST" "$UI"

dag-sync --db work.sqlite3 tree
dag-sync --db work.sqlite3 ready
```

Dependency direction is: `TASK depends on PREREQUISITE`. The exported graph points from prerequisite to unblocked task.

## Agent loop

Each agent repeatedly claims one task. Claims are serialized with `BEGIN IMMEDIATE`, so only one process receives a given task.

```bash
AGENT="backend-agent-1"
TASK=$(dag-sync --db work.sqlite3 claim --agent "$AGENT" --lease 900)

# Exit code 3 means no task is currently ready.
[ -n "$TASK" ] || exit 0

dag-sync --db work.sqlite3 start "$TASK" --agent "$AGENT"

# While work is running, extend the lease periodically.
dag-sync --db work.sqlite3 heartbeat "$TASK" --agent "$AGENT" --lease 900

# On success:
dag-sync --db work.sqlite3 complete "$TASK" --agent "$AGENT" --result 'commit=abc123'

# On a retryable failure:
# dag-sync --db work.sqlite3 fail "$TASK" --agent "$AGENT" --error 'tests timed out' --retry
```

For automation, use `claim --json`, parse the returned task object, and treat exit status `3` as an idle queue.

## Hierarchy semantics

Only `kind=task` nodes can be claimed. `kind=group` nodes are containers whose status is rolled up from children:

- any failed child → group is failed;
- all children cancelled → group is cancelled;
- all children completed or cancelled → group is completed;
- any active or completed child while work remains → group is running;
- otherwise → group is pending.

A dependency attached to a group blocks every task below that group. This allows a whole workstream to wait for architecture approval, a merge, an environment, or another workstream.

Hierarchy does not itself create execution order between siblings; use dependency edges for that.

## Lease semantics

A claim changes a task to `leased`, records `agent_id`, increments `attempts`, and sets `lease_until`.

- `start` changes `leased` to `running`.
- `heartbeat` extends the current lease.
- `complete`, `fail`, and `release` require ownership of a live lease.
- an expired `leased` or `running` task is atomically reclaimable by another agent.
- a task is not claimable after `attempts == max_attempts`.

SQLite WAL mode allows readers to continue while claims and state transitions are committed. Keep the database on a local or correctly configured shared filesystem; SQLite locking semantics are not reliable on every network filesystem.

## Commands

```text
init                         Initialize the database
add                          Add a task or group
depend / undepend            Add or remove a dependency
list                         List tasks
ready                        List claimable leaf tasks
claim                        Atomically claim one ready task
start / heartbeat            Operate an active lease
complete / fail / release    Finish or relinquish a lease
cancel                       Cancel a task
show                         Show one task and prerequisites
tree                         Render hierarchy
events                       Show audit log
agents                       Show observed agents
dot                          Export Graphviz DOT
validate                     Check graph/database invariants
```

Use `dag-sync COMMAND --help` for flags. Most read and mutation commands support `--json`.

## Scope agents to a subtree

```bash
dag-sync --db work.sqlite3 claim --agent frontend-1 --scope "$UI_GROUP" --json
```

The scope may identify a group or task. Only tasks in that subtree are considered.

## Graph export

```bash
dag-sync --db work.sqlite3 dot -o graph.dot
dot -Tsvg graph.dot -o graph.svg
```

Dotted edges represent containment. Solid edges point from prerequisites to tasks they unblock.

## Python API

```python
from dag_agent_sync import Coordinator

q = Coordinator("work.sqlite3")
q.initialize()

epic = q.add_task("Search", kind="group")
index = q.add_task("Build index", parent_id=epic.id)
query = q.add_task("Query API", parent_id=epic.id)
q.add_dependency(query.id, index.id)

job = q.claim("agent-7", lease_seconds=600)
if job:
    q.start(job.id, "agent-7")
    q.complete(job.id, "agent-7", result="commit=deadbeef")
```

## Test

```bash
pip install pytest
pytest
```

The tests include dependency gating, hierarchy rollups, group-level barriers, cycle rejection, retries, expired-lease recovery, and a concurrent claim race.
EOF

cat > /mnt/data/dag-agent-sync/LICENSE <<'EOF'
MIT License

Copyright (c) 2026 OpenAI

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
EOF

```

<details><summary>💭 Thinking</summary>

**Implemented transactional DAG task coordination API**

</details>

The core implementation is in place. I’m validating the concurrency, dependency gating, lease recovery, and packaging behavior now.

```unknown
bash -lc python -m pytest -q
```

<details><summary>💭 Thinking</summary>

**Ran tests and fixed group lease packaging and schema inclusion**

</details>

Functional tests and a full CLI workflow pass. The remaining check is distribution packaging; the isolated build environment lacks access to its package index, so I’m verifying the wheel without isolation.

```unknown
bash -lc python - <<'PY'
import setuptools
print(setuptools.__version__)
PY
rm -rf /tmp/dag-agent-sync-wheel && mkdir -p /tmp/dag-agent-sync-wheel
python -m pip wheel . --no-deps --no-build-isolation -w /tmp/dag-agent-sync-wheel
unzip -l /tmp/dag-agent-sync-wheel/*.whl | grep -E 'schema.sql|dag_agent_sync/cli.py|METADATA'

```

<details><summary>💭 Thinking</summary>

**Checking DAG semantics**

I’m reviewing edge cases in the combined hierarchy-and-dependency model. Explicit dependency cycles are handled, but dependencies involving ancestors or descendants could create hidden completion deadlocks, so those relationships need validation too.

**Checked DAG semantics**

**Verified setuptools and built wheel**

</details>

```unknown
bash -lc python - <<'PY'
from pathlib import Path
p=Path('/mnt/data/dag-agent-sync/src/dag_agent_sync/store.py')
s=p.read_text()
old='''            cycle = conn.execute(
                """
                WITH RECURSIVE reachable(id) AS (
                    SELECT depends_on_id FROM dependencies WHERE task_id = ?
                    UNION
                    SELECT d.depends_on_id
                    FROM dependencies d
                    JOIN reachable r ON d.task_id = r.id
                )
                SELECT 1 FROM reachable WHERE id = ? LIMIT 1
                """,
                (depends_on_id, task_id),
            ).fetchone()
            if cycle:
                raise ValidationError("dependency would create a cycle")
'''
new='''            self._assert_dependency_preserves_dag(conn, task_id, depends_on_id)
'''
if old not in s:
    raise SystemExit('old dependency cycle block not found')
s=s.replace(old,new)

insert_after='''    def remove_dependency(self, task_id: str, depends_on_id: str) -> None:
'''
helper='''    def _effective_adjacency(
        self,
        conn: sqlite3.Connection,
        *,
        extra_dependency: tuple[str, str] | None = None,
    ) -> dict[str, set[str]]:
        """Build the effective execution graph.

        Edges point from a prerequisite to what it unblocks. A child points to
        its parent because a group cannot complete before its children. A
        dependency attached to a group points to the group and every
        descendant because group prerequisites are inherited by the subtree.
        """
        task_rows = conn.execute("SELECT id, parent_id FROM tasks").fetchall()
        adjacency: dict[str, set[str]] = {row["id"]: set() for row in task_rows}
        children: dict[str, list[str]] = {}
        for row in task_rows:
            parent_id = row["parent_id"]
            if parent_id:
                adjacency[row["id"]].add(parent_id)
                children.setdefault(parent_id, []).append(row["id"])

        descendant_cache: dict[str, set[str]] = {}

        def descendants(root: str) -> set[str]:
            cached = descendant_cache.get(root)
            if cached is not None:
                return cached
            found: set[str] = set()
            stack = [root]
            while stack:
                node = stack.pop()
                if node in found:
                    continue
                found.add(node)
                stack.extend(children.get(node, ()))
            descendant_cache[root] = found
            return found

        dependencies = [
            (row["task_id"], row["depends_on_id"])
            for row in conn.execute("SELECT task_id, depends_on_id FROM dependencies")
        ]
        if extra_dependency is not None:
            dependencies.append(extra_dependency)
        for task_id, depends_on_id in dependencies:
            adjacency.setdefault(depends_on_id, set()).update(descendants(task_id))
        return adjacency

    @staticmethod
    def _find_cycle(adjacency: Mapping[str, set[str]]) -> list[str] | None:
        state: dict[str, int] = {}
        stack: list[str] = []
        positions: dict[str, int] = {}

        def visit(node: str) -> list[str] | None:
            state[node] = 1
            positions[node] = len(stack)
            stack.append(node)
            for nxt in adjacency.get(node, ()):
                if state.get(nxt, 0) == 0:
                    cycle = visit(nxt)
                    if cycle:
                        return cycle
                elif state.get(nxt) == 1:
                    start = positions[nxt]
                    return stack[start:] + [nxt]
            stack.pop()
            positions.pop(node, None)
            state[node] = 2
            return None

        for node in adjacency:
            if state.get(node, 0) == 0:
                cycle = visit(node)
                if cycle:
                    return cycle
        return None

    def _assert_dependency_preserves_dag(
        self,
        conn: sqlite3.Connection,
        task_id: str,
        depends_on_id: str,
    ) -> None:
        adjacency = self._effective_adjacency(
            conn,
            extra_dependency=(task_id, depends_on_id),
        )
        cycle = self._find_cycle(adjacency)
        if cycle:
            raise ValidationError(
                "dependency would create an effective cycle: " + " -> ".join(cycle)
            )

'''
s=s.replace(insert_after, helper+insert_after)

# Add reaping before claim and a public method before claim.
marker='''    def claim(
        self,
        agent_id: str,
'''
reap='''    def _reap_expired_in_tx(self, conn: sqlite3.Connection, *, now: float) -> list[str]:
        rows = conn.execute(
            """
            SELECT * FROM tasks
            WHERE kind='task'
              AND status IN ('leased','running')
              AND lease_until <= ?
              AND attempts >= max_attempts
            ORDER BY id
            """,
            (now,),
        ).fetchall()
        reaped: list[str] = []
        parents: set[str] = set()
        for row in rows:
            error = row["error"] or "lease expired after maximum attempts"
            changed = conn.execute(
                """
                UPDATE tasks SET status='failed', error=?, completed_at=?, updated_at=?,
                    agent_id=NULL, lease_until=NULL, heartbeat_at=NULL
                WHERE id=? AND status IN ('leased','running') AND lease_until <= ?
                """,
                (error, now, now, row["id"], now),
            ).rowcount
            if not changed:
                continue
            reaped.append(row["id"])
            if row["parent_id"]:
                parents.add(row["parent_id"])
            self._event(
                conn,
                "task_lease_exhausted",
                task_id=row["id"],
                agent_id=row["agent_id"],
                payload={"attempts": row["attempts"], "max_attempts": row["max_attempts"]},
                at=now,
            )
        for parent_id in parents:
            self._recompute_ancestors(conn, parent_id, now=now)
        return reaped

    def reap_expired(self) -> list[str]:
        """Fail expired tasks whose attempt budget has been exhausted."""
        now = self._now()
        with self._tx(immediate=True) as conn:
            return self._reap_expired_in_tx(conn, now=now)

'''
if marker not in s:
    raise SystemExit('claim marker not found')
s=s.replace(marker,reap+marker)

old='''        with self._tx(immediate=True) as conn:
            if scope_id:
                self._require_task(conn, scope_id)
            self._touch_agent(conn, agent_id, metadata=metadata, at=now)
'''
new='''        with self._tx(immediate=True) as conn:
            if scope_id:
                self._require_task(conn, scope_id)
            self._reap_expired_in_tx(conn, now=now)
            self._touch_agent(conn, agent_id, metadata=metadata, at=now)
'''
if old not in s:
    raise SystemExit('claim tx block not found')
s=s.replace(old,new,1)

# Replace explicit dependency-cycle validation with effective graph validation.
start=s.index('''            dep_cycle = conn.execute(
''')
end=s.index('''            hierarchy_cycle = conn.execute(
''', start)
replacement='''            effective_cycle = self._find_cycle(self._effective_adjacency(conn))
            if effective_cycle:
                problems.append("effective graph cycle: " + " -> ".join(effective_cycle))

'''
s=s[:start]+replacement+s[end:]
p.write_text(s)
PY

python - <<'PY'
from pathlib import Path
p=Path('/mnt/data/dag-agent-sync/src/dag_agent_sync/cli.py')
s=p.read_text()
marker='''    p = sub.add_parser("agents", help="show registered agents")
    add_common_output(p)

'''
new='''    p = sub.add_parser("agents", help="show registered agents")
    add_common_output(p)

    p = sub.add_parser("reap", help="fail expired tasks with no attempts remaining")
    add_common_output(p)

'''
if marker not in s: raise SystemExit('agents parser marker missing')
s=s.replace(marker,new)
marker2='''        elif args.command == "agents":
            rows = coord.agents()
            if args.json:
                json_dump(rows)
            else:
                for row in rows:
                    print(
                        f"{row['id']}  last_seen={iso(row['last_seen_at'])}  "
                        f"metadata={json.dumps(row['metadata'], sort_keys=True)}"
                    )
        elif args.command == "dot":
'''
new2='''        elif args.command == "agents":
            rows = coord.agents()
            if args.json:
                json_dump(rows)
            else:
                for row in rows:
                    print(
                        f"{row['id']}  last_seen={iso(row['last_seen_at'])}  "
                        f"metadata={json.dumps(row['metadata'], sort_keys=True)}"
                    )
        elif args.command == "reap":
            task_ids = coord.reap_expired()
            if args.json:
                json_dump(task_ids)
            else:
                print(f"reaped {len(task_ids)} task(s)")
        elif args.command == "dot":
'''
if marker2 not in s: raise SystemExit('agents dispatch marker missing')
s=s.replace(marker2,new2)
p.write_text(s)
PY

cat >> /mnt/data/dag-agent-sync/tests/test_coordinator.py <<'EOF'


def test_dependency_on_ancestor_is_rejected(coord: Coordinator) -> None:
    group = coord.add_task("Group", kind="group")
    child = coord.add_task("Child", parent_id=group.id)
    with pytest.raises(ValidationError):
        coord.add_dependency(child.id, group.id)


def test_group_dependency_on_descendant_is_rejected(coord: Coordinator) -> None:
    group = coord.add_task("Group", kind="group")
    child = coord.add_task("Child", parent_id=group.id)
    with pytest.raises(ValidationError):
        coord.add_dependency(group.id, child.id)


def test_inherited_cross_group_cycle_is_rejected(coord: Coordinator) -> None:
    left = coord.add_task("Left", kind="group")
    left_task = coord.add_task("Left task", parent_id=left.id)
    right = coord.add_task("Right", kind="group")
    right_task = coord.add_task("Right task", parent_id=right.id)

    coord.add_dependency(left.id, right_task.id)
    with pytest.raises(ValidationError):
        coord.add_dependency(right_task.id, left_task.id)


def test_expired_final_attempt_is_reaped(coord: Coordinator) -> None:
    task = coord.add_task("One shot", max_attempts=1)
    coord.claim("agent-a", lease_seconds=1)
    time.sleep(1.05)
    assert coord.claim("agent-b", lease_seconds=30) is None
    failed = coord.get_task(task.id)
    assert failed.status == "failed"
    assert failed.error == "lease expired after maximum attempts"
EOF

python - <<'PY'
from pathlib import Path
p=Path('/mnt/data/dag-agent-sync/README.md')
s=p.read_text()
s=s.replace('- dependency edges with cycle prevention;', '- dependency edges with cycle prevention across explicit dependencies, inherited group barriers, and hierarchy rollups;')
s=s.replace('agents                       Show observed agents\ndot', 'agents                       Show observed agents\nreap                         Fail expired tasks with exhausted attempts\ndot')
s=s.replace('- a task is not claimable after `attempts == max_attempts`.', '- an expired task at `attempts == max_attempts` is marked failed by the next claim or by `reap`.')
p.write_text(s)
PY

python -m pytest -q
```

<details><summary>💭 Thinking</summary>

**Refactored dependency cycle validation and inspected files for syntax issues**

</details>

```unknown
bash -lc mkdir -p examples
cat > examples/worker.py <<'EOF'
#!/usr/bin/env python3
"""Claim one task, run an agent command, and maintain the SQLite lease.

The child process receives DAG_TASK_ID, DAG_TASK_TITLE, DAG_TASK_DESCRIPTION,
and DAG_TASK_JSON in its environment.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import threading
from pathlib import Path

from dag_agent_sync import Coordinator, DagError


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", required=True)
    parser.add_argument("--agent", required=True)
    parser.add_argument("--scope")
    parser.add_argument("--lease", type=int, default=900)
    parser.add_argument("--heartbeat", type=int, default=300)
    parser.add_argument(
        "--retry-on-failure",
        action="store_true",
        help="requeue a failed command while attempts remain",
    )
    parser.add_argument("command", nargs=argparse.REMAINDER)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if not args.command:
        print("error: an agent command is required after --", file=sys.stderr)
        return 2
    if args.command[0] == "--":
        args.command = args.command[1:]
    if not args.command:
        print("error: an agent command is required after --", file=sys.stderr)
        return 2
    if args.heartbeat < 1 or args.heartbeat >= args.lease:
        print("error: --heartbeat must be positive and less than --lease", file=sys.stderr)
        return 2

    coordinator = Coordinator(Path(args.db))
    try:
        task = coordinator.claim(
            args.agent,
            lease_seconds=args.lease,
            scope_id=args.scope,
            metadata={"pid": os.getpid(), "command": args.command},
        )
        if task is None:
            print("No ready task.")
            return 3
        coordinator.start(task.id, args.agent)

        task_data = task.to_dict()
        env = os.environ.copy()
        env.update(
            {
                "DAG_TASK_ID": task.id,
                "DAG_TASK_TITLE": task.title,
                "DAG_TASK_DESCRIPTION": task.description,
                "DAG_TASK_JSON": json.dumps(task_data, sort_keys=True),
            }
        )

        stop = threading.Event()
        heartbeat_error: list[Exception] = []

        def keep_alive() -> None:
            while not stop.wait(args.heartbeat):
                try:
                    coordinator.heartbeat(
                        task.id,
                        args.agent,
                        lease_seconds=args.lease,
                    )
                except Exception as exc:  # surfaced after the child exits
                    heartbeat_error.append(exc)
                    stop.set()

        thread = threading.Thread(target=keep_alive, daemon=True)
        thread.start()
        try:
            completed = subprocess.run(args.command, env=env, check=False)
        finally:
            stop.set()
            thread.join()

        if heartbeat_error:
            raise heartbeat_error[0]
        if completed.returncode == 0:
            coordinator.complete(
                task.id,
                args.agent,
                result=json.dumps({"exit_code": completed.returncode}),
            )
            return 0

        coordinator.fail(
            task.id,
            args.agent,
            error=f"agent command exited with code {completed.returncode}",
            retry=args.retry_on_failure,
        )
        return completed.returncode or 1
    except DagError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
EOF
chmod +x examples/worker.py

python - <<'PY'
from pathlib import Path
p=Path('README.md')
s=p.read_text()
needle='''For automation, use `claim --json`, parse the returned task object, and treat exit status `3` as an idle queue.
'''
replacement='''For automation, use `claim --json`, parse the returned task object, and treat exit status `3` as an idle queue.

A ready-to-use wrapper is included at `examples/worker.py`. It claims one task, exports the task as environment variables, runs an agent command, maintains heartbeats, and records success or failure:

```bash
python examples/worker.py \\
  --db work.sqlite3 \\
  --agent backend-agent-1 \\
  --lease 900 \\
  --heartbeat 300 \\
  --retry-on-failure \\
  -- your-coding-agent-command
```
'''
if needle not in s: raise SystemExit('readme insertion point missing')
s=s.replace(needle,replacement)
p.write_text(s)
PY

python -m pytest -q
python -m compileall -q src tests examples
```

<details><summary>💭 Thinking</summary>

**Built, tested, and packaged the task network and workers**

</details>

```unknown
bash -lc set -euo pipefail
cd /mnt/data/dag-agent-sync
rm -rf build .pytest_cache src/dag_agent_sync.egg-info
find . -type d -name __pycache__ -prune -exec rm -rf {} +

PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -p no:cacheprovider

rm -rf /tmp/dag-agent-sync-wheel && mkdir -p /tmp/dag-agent-sync-wheel
python -m pip wheel . --no-deps --no-build-isolation -w /tmp/dag-agent-sync-wheel >/tmp/dag-wheel-build.log
cp /tmp/dag-agent-sync-wheel/dag_agent_sync-0.1.0-py3-none-any.whl /mnt/data/

rm -rf build src/dag_agent_sync.egg-info
find . -type d -name __pycache__ -prune -exec rm -rf {} +

python - <<'PY'
from pathlib import Path
import zipfile

root = Path('/mnt/data/dag-agent-sync')
out = Path('/mnt/data/dag-agent-sync-0.1.0.zip')
include = [
    root / 'pyproject.toml',
    root / 'README.md',
    root / 'LICENSE',
    root / 'src' / 'dag_agent_sync' / '__init__.py',
    root / 'src' / 'dag_agent_sync' / '__main__.py',
    root / 'src' / 'dag_agent_sync' / 'cli.py',
    root / 'src' / 'dag_agent_sync' / 'schema.sql',
    root / 'src' / 'dag_agent_sync' / 'store.py',
    root / 'tests' / 'test_coordinator.py',
    root / 'examples' / 'worker.py',
]
with zipfile.ZipFile(out, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
    for path in include:
        zf.write(path, Path('dag-agent-sync') / path.relative_to(root))
with zipfile.ZipFile(out) as zf:
    bad = zf.testzip()
    if bad:
        raise SystemExit(f'corrupt archive member: {bad}')
print(out)
PY

rm -rf /tmp/dag-wheel-install /tmp/dag-wheel-test.sqlite3
python -m pip install --no-deps --target /tmp/dag-wheel-install /mnt/data/dag_agent_sync-0.1.0-py3-none-any.whl >/tmp/dag-wheel-install.log
cd /tmp
PYTHONPATH=/tmp/dag-wheel-install python - <<'PY'
from dag_agent_sync import Coordinator
c = Coordinator('/tmp/dag-wheel-test.sqlite3')
c.initialize()
a = c.add_task('A')
b = c.add_task('B')
c.add_dependency(b.id, a.id)
job = c.claim('wheel-agent', lease_seconds=30)
assert job and job.id == a.id
c.complete(a.id, 'wheel-agent')
assert c.ready_tasks()[0].id == b.id
assert c.validate() == []
print('wheel verification: OK')
PY

cd /mnt/data
sha256sum dag-agent-sync-0.1.0.zip dag_agent_sync-0.1.0-py3-none-any.whl
unzip -l dag-agent-sync-0.1.0.zip
unzip -l dag_agent_sync-0.1.0-py3-none-any.whl | grep -E 'dag_agent_sync/(store.py|cli.py|schema.sql)|dist-info/METADATA'

```

<details><summary>💭 Thinking</summary>

**Packaged and verified dag-agent-sync artifacts**

</details>

## Hierarchical DAG agent coordinator

Created a complete Python package with:

- SQLite persistence in WAL mode
- Hierarchical groups and executable leaf tasks
- Dependency DAG with effective cycle/deadlock detection
- Atomic task claims using `BEGIN IMMEDIATE`
- Agent leases, heartbeats, retries, and expired-worker recovery
- Group-level dependencies inherited by descendants
- Automatic parent status rollups
- Audit events and agent registry
- JSON output and Graphviz DOT export
- Worker wrapper for running coding-agent commands
- 11 passing tests, including concurrent-claim races

### Downloads

- [Source archive](sandbox:/mnt/data/dag-agent-sync-0.1.0.zip)
- [Installable Python wheel](sandbox:/mnt/data/dag_agent_sync-0.1.0-py3-none-any.whl)

### Install and start

```bash
pip install dag_agent_sync-0.1.0-py3-none-any.whl

dag-sync --db work.sqlite3 init
dag-sync --db work.sqlite3 add "Authentication" --kind group
dag-sync --db work.sqlite3 tree
```

Principal commands include `add`, `depend`, `ready`, `claim`, `start`, `heartbeat`, `complete`, `fail`, `release`, `reap`, `events`, `dot`, and `validate`. Python 3.10+ is required; there are no runtime dependencies.


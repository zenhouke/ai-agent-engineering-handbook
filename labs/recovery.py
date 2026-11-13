"""Crash after an external commit. Two databases model independent durability.

This is a narrow protocol simulation, not a production runtime. The external
service explicitly supports idempotency; local state alone cannot provide it.
"""

import sqlite3
import tempfile
from contextlib import closing
from pathlib import Path


class SimulatedCrash(RuntimeError):
    """The tool committed but the worker did not save its receipt."""


def prepare(local: sqlite3.Connection, external: sqlite3.Connection) -> None:
    local.execute(
        "CREATE TABLE IF NOT EXISTS tasks (id TEXT PRIMARY KEY, status TEXT, receipt TEXT)"
    )
    local.execute("INSERT OR IGNORE INTO tasks VALUES ('op-1', 'pending', NULL)")
    external.execute(
        "CREATE TABLE IF NOT EXISTS drafts (operation_id TEXT PRIMARY KEY, id TEXT)"
    )
    local.commit()
    external.commit()


def execute(
    local: sqlite3.Connection, external: sqlite3.Connection, crash: bool = False
) -> str:
    # Fixed operation key is persisted before calling the external service.
    operation_id = "op-1"
    local.execute("UPDATE tasks SET status='unknown' WHERE id=?", (operation_id,))
    local.commit()
    external.execute(
        "INSERT OR IGNORE INTO drafts VALUES (?, 'draft-1')", (operation_id,)
    )
    external.commit()
    if crash:
        raise SimulatedCrash("External commit happened; local receipt was not saved")
    row = external.execute(
        "SELECT id FROM drafts WHERE operation_id=?", (operation_id,)
    ).fetchone()
    if row is None:
        raise RuntimeError("External service did not return a durable result")
    receipt = str(row[0])
    local.execute(
        "UPDATE tasks SET status='completed', receipt=? WHERE id=?",
        (receipt, operation_id),
    )
    local.commit()
    return receipt


def demonstration(directory: Path) -> tuple[str, int]:
    local_path, external_path = directory / "tasks.db", directory / "external.db"
    # Connections really close across the crash boundary; state survives reopening.
    with (
        closing(sqlite3.connect(local_path)) as local,
        closing(sqlite3.connect(external_path)) as external,
    ):
        prepare(local, external)
        try:
            execute(local, external, crash=True)
        except SimulatedCrash:
            print("crash: local status=unknown; remote draft already exists")
    with (
        closing(sqlite3.connect(local_path)) as local,
        closing(sqlite3.connect(external_path)) as external,
    ):
        receipt = execute(local, external)
        count = external.execute("SELECT COUNT(*) FROM drafts").fetchone()[0]
        status = local.execute("SELECT status FROM tasks WHERE id='op-1'").fetchone()[0]
        print(f"recovered: status={status}, receipt={receipt}, external_drafts={count}")
    return receipt, count


if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as directory:
        demonstration(Path(directory))

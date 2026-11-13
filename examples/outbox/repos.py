"""SQLite persistence; services own transaction scope, repositories execute it."""

import sqlite3
from contextlib import contextmanager
from pathlib import Path

from .domain import Operation


class OutboxRepository:
    def __init__(self, connection: sqlite3.Connection):
        self.connection = connection
        self.connection.row_factory = sqlite3.Row

    def initialize(self) -> None:
        self.connection.execute("PRAGMA foreign_keys=ON")
        self.connection.executescript(
            Path(__file__).with_name("schema.sql").read_text()
        )

    @contextmanager
    def transaction(self):
        # Explicit begin also works with isolation_level=None; no network inside it.
        self.connection.execute("BEGIN IMMEDIATE")
        try:
            yield
            self.connection.commit()
        except BaseException:
            self.connection.rollback()
            raise

    def seed_approved(self, task_id, tenant, payload, fingerprint, expires_at) -> None:
        """Fixture only: real approval issuance must authenticate the approver."""
        with self.transaction():
            self.connection.execute(
                "INSERT INTO tasks VALUES (?, ?, ?, ?, ?, ?, ?, 1)",
                (
                    task_id,
                    tenant,
                    payload,
                    fingerprint,
                    fingerprint,
                    expires_at,
                    "approved",
                ),
            )

    def task(self, task_id: str, tenant: str) -> dict:
        row = self.connection.execute(
            "SELECT * FROM tasks WHERE task_id=? AND tenant=?", (task_id, tenant)
        ).fetchone()
        if row is None:
            raise LookupError("Task unavailable in tenant scope")
        return dict(row)

    def queue(self, task: dict, operation_id: str) -> None:
        changed = self.connection.execute(
            "UPDATE tasks SET state='queued',version=version+1 "
            "WHERE task_id=? AND tenant=? AND version=? AND state='approved'",
            (task["task_id"], task["tenant"], task["version"]),
        ).rowcount
        if changed != 1:
            raise RuntimeError("Stale task state/version")
        self.connection.execute(
            "INSERT INTO outbox VALUES (?, ?, ?, ?, ?, ?, NULL)",
            (
                operation_id,
                task["task_id"],
                task["tenant"],
                task["payload"],
                task["fingerprint"],
                "pending",
            ),
        )

    def operation(self, operation_id: str, tenant: str) -> Operation:
        row = self.connection.execute(
            "SELECT * FROM outbox WHERE operation_id=? AND tenant=?",
            (operation_id, tenant),
        ).fetchone()
        if row is None:
            raise LookupError("Operation unavailable in tenant scope")
        return Operation(**dict(row))

    def mark_unknown(self, operation: Operation) -> None:
        self.connection.execute(
            "UPDATE outbox SET state='unknown' WHERE operation_id=? AND state='pending'",
            (operation.operation_id,),
        )
        self.connection.execute(
            "UPDATE tasks SET state='executing',version=version+1 "
            "WHERE task_id=? AND state='queued'",
            (operation.task_id,),
        )

    def confirm(self, operation: Operation, receipt: str) -> None:
        # Repeated identical receipts are safe; contradictory receipts need investigation.
        old = self.operation(operation.operation_id, operation.tenant)
        if old.receipt is not None and old.receipt != receipt:
            raise RuntimeError("Conflicting remote receipts")
        self.connection.execute(
            "UPDATE outbox SET state='confirmed',receipt=? WHERE operation_id=?",
            (receipt, operation.operation_id),
        )
        self.connection.execute(
            "UPDATE tasks SET state='confirmed',version=version+1 "
            "WHERE task_id=? AND state!='confirmed'",
            (operation.task_id,),
        )

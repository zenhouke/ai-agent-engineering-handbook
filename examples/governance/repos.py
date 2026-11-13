"""Explicit transaction and narrow persistence operations; no network in transactions."""

import sqlite3
from contextlib import contextmanager
from pathlib import Path


class GovernanceRepository:
    def __init__(self, connection: sqlite3.Connection):
        self.connection = connection
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys=ON")

    def initialize(self) -> None:
        self.connection.executescript(
            Path(__file__).with_name("schema.sql").read_text()
        )

    @contextmanager
    def transaction(self):
        self.connection.execute("BEGIN IMMEDIATE")
        try:
            yield
            self.connection.commit()
        except BaseException:
            self.connection.rollback()
            raise

    def get(self, table: str, key: str, value: str) -> dict:
        # Identifiers are a closed internal set, never caller-supplied SQL fragments.
        if (table, key) not in {
            ("sessions", "session_id"),
            ("tasks", "task_id"),
            ("approvals", "approval_id"),
            ("operations", "operation_id"),
        }:
            raise ValueError("Unsupported lookup")
        row = self.connection.execute(
            f"SELECT * FROM {table} WHERE {key}=?", (value,)
        ).fetchone()
        if row is None:
            raise LookupError("Record not found")
        return dict(row)

    def member(self, subject: str, tenant: str) -> dict | None:
        row = self.connection.execute(
            "SELECT * FROM members WHERE subject=? AND tenant=?", (subject, tenant)
        ).fetchone()
        return dict(row) if row else None

    def policy_version(self) -> int:
        return self.connection.execute(
            "SELECT version FROM policy_epoch WHERE singleton=1"
        ).fetchone()[0]

    def set_member(self, subject: str, tenant: str, role: str, limit: int) -> None:
        with self.transaction():
            self.connection.execute(
                "INSERT INTO members VALUES(?,?,?,?) ON CONFLICT(subject,tenant) DO UPDATE SET role=excluded.role,limit_cents=excluded.limit_cents",
                (subject, tenant, role, limit),
            )
            self.connection.execute(
                "UPDATE policy_epoch SET version=version+1 WHERE singleton=1"
            )

    def create_session(
        self, session_id: str, subject: str, tenant: str, expires: int
    ) -> None:
        self.connection.execute(
            "INSERT INTO sessions(session_id,subject,tenant,expires_at) VALUES(?,?,?,?)",
            (session_id, subject, tenant, expires),
        )

    def revoke_session(self, session_id: str) -> None:
        self.connection.execute(
            "UPDATE sessions SET revoked=1 WHERE session_id=?", (session_id,)
        )

    def create_task(
        self, task_id: str, tenant: str, owner: str, conversation: str, resource: str
    ) -> None:
        self.connection.execute(
            "INSERT INTO tasks(task_id,tenant,owner,conversation_id,resource_id,state) VALUES(?,?,?,?,?,'paused')",
            (task_id, tenant, owner, conversation, resource),
        )

    def resume(
        self, task: dict, session_id: str, run_id: str, expected_version: int
    ) -> None:
        changed = self.connection.execute(
            "UPDATE tasks SET state='running',version=version+1 WHERE task_id=? AND version=? AND state='paused'",
            (task["task_id"], expected_version),
        ).rowcount
        if changed != 1:
            raise RuntimeError("Task already claimed or stale version")
        self.connection.execute(
            "INSERT INTO runs VALUES(?,?,?,?)",
            (run_id, task["task_id"], session_id, expected_version + 1),
        )

    def request_approval(
        self, approval_id: str, context, action, expires: int, epoch: int
    ) -> None:
        changed = self.connection.execute(
            "UPDATE tasks SET state='awaiting_approval',version=version+1 WHERE task_id=? AND state='paused'",
            (action.task_id,),
        ).rowcount
        if changed != 1:
            raise RuntimeError("Task not ready for approval")
        self.connection.execute(
            "INSERT INTO approvals VALUES(?,?,?,?,NULL,?,?,?,?,'pending')",
            (
                approval_id,
                action.task_id,
                context.tenant,
                context.subject,
                action.payload(),
                action.fingerprint(),
                epoch,
                expires,
            ),
        )

    def approve(self, approval_id: str, approver: str) -> None:
        changed = self.connection.execute(
            "UPDATE approvals SET status='approved',approver=? WHERE approval_id=? AND status='pending'",
            (approver, approval_id),
        ).rowcount
        if changed != 1:
            raise RuntimeError("Approval is no longer pending")

    def revoke_approval(self, approval_id: str) -> None:
        changed = self.connection.execute(
            "UPDATE approvals SET status='revoked' WHERE approval_id=? AND status IN ('pending','approved')",
            (approval_id,),
        ).rowcount
        if changed != 1:
            raise RuntimeError(
                "Approval already consumed or revoked; inspect operation"
            )
        self.connection.execute(
            "UPDATE tasks SET state='paused',version=version+1 WHERE task_id=(SELECT task_id FROM approvals WHERE approval_id=?) AND state='awaiting_approval'",
            (approval_id,),
        )

    def claim(self, approval: dict, action, operation_id: str) -> None:
        changed = self.connection.execute(
            "UPDATE approvals SET status='consumed' WHERE approval_id=? AND status='approved'",
            (approval["approval_id"],),
        ).rowcount
        if changed != 1:
            raise RuntimeError("Approval already consumed or not approved")
        self.connection.execute(
            "INSERT INTO operations(operation_id,approval_id,task_id,tenant,action_json,action_hash) VALUES(?,?,?,?,?,?)",
            (
                operation_id,
                approval["approval_id"],
                action.task_id,
                action.tenant,
                action.payload(),
                action.fingerprint(),
            ),
        )
        changed = self.connection.execute(
            "UPDATE tasks SET state='queued',version=version+1 WHERE task_id=? AND state='awaiting_approval'",
            (action.task_id,),
        ).rowcount
        if changed != 1:
            raise RuntimeError("Task state no longer permits execution")

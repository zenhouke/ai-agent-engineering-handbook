"""Application-session service; authentication and browser cookies are separate concerns."""

from uuid import uuid4

from .domain import Context, Principal
from .repos import GovernanceRepository


class SessionService:
    def __init__(self, repository: GovernanceRepository):
        self.repository = repository

    def open(
        self, identity: Principal, tenant: str, now: int, lifetime: int = 3600
    ) -> str:
        if lifetime <= 0:
            raise ValueError("Invalid lifetime")
        with self.repository.transaction():
            if self.repository.member(identity.subject, tenant) is None:
                raise PermissionError("No tenant membership")
            key = uuid4().hex
            self.repository.create_session(
                key, identity.subject, tenant, now + lifetime
            )
        return key

    def context(self, identity: Principal, session_id: str, now: int) -> Context:
        row = self.repository.get("sessions", "session_id", session_id)
        if (
            row["subject"] != identity.subject
            or row["revoked"]
            or row["expires_at"] <= now
        ):
            raise PermissionError("Session unavailable or expired")
        if self.repository.member(identity.subject, row["tenant"]) is None:
            raise PermissionError("Tenant membership revoked")
        return Context(identity.subject, row["tenant"], session_id)

    def close(self, identity: Principal, session_id: str, now: int) -> None:
        with self.repository.transaction():
            self.context(identity, session_id, now)
            self.repository.revoke_session(session_id)
        # Closing a session neither deletes task state nor proves an external action was cancelled.

    def task(self, context: Context, task_id: str) -> dict:
        row = self.repository.get("tasks", "task_id", task_id)
        if row["tenant"] != context.tenant or row["owner"] != context.subject:
            raise PermissionError("Task outside actor scope")
        return row

    def create_task(
        self,
        identity: Principal,
        session_id: str,
        task_id: str,
        conversation_id: str,
        resource: str,
        now: int,
    ) -> None:
        with self.repository.transaction():
            context = self.context(identity, session_id, now)
            self.repository.create_task(
                task_id, context.tenant, context.subject, conversation_id, resource
            )

    def resume(
        self,
        identity: Principal,
        session_id: str,
        task_id: str,
        run_id: str,
        expected_version: int,
        now: int,
    ) -> None:
        with self.repository.transaction():
            context = self.context(identity, session_id, now)
            task = self.task(context, task_id)
            member = self.repository.member(context.subject, context.tenant)
            if member["role"] not in {"operator", "lead"}:
                raise PermissionError("Current role cannot resume work")
            self.repository.resume(task, session_id, run_id, expected_version)

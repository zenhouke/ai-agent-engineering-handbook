"""Transactional queueing and a separate idempotent effect/reconciliation boundary."""

import hashlib

from .domain import IdempotentDraftBackend
from .repos import OutboxRepository


class DraftService:
    def __init__(self, repository: OutboxRepository):
        self.repository = repository

    @staticmethod
    def validate_approval(task: dict, now: int) -> None:
        # Stored payload is canonical JSON from the trusted approval service.
        actual_hash = hashlib.sha256(task["payload"].encode()).hexdigest()
        if (
            task["approved_until"] <= now
            or task["approved_hash"] != actual_hash
            or task["fingerprint"] != actual_hash
        ):
            raise PermissionError("Approval expired or payload changed")

    def enqueue(
        self,
        tenant: str,
        task_id: str,
        operation_id: str,
        now: int,
        allowed_tenants: frozenset[str],
    ) -> None:
        if tenant not in allowed_tenants:
            raise PermissionError("Tenant outside trusted identity scope")
        with self.repository.transaction():
            task = self.repository.task(task_id, tenant)
            if task["state"] != "approved":
                raise ValueError("Expected approved task; reconcile existing operation")
            self.validate_approval(task, now)
            # CAS + unique event insert share ONE transaction. Insert failure rolls back CAS.
            self.repository.queue(task, operation_id)

    def deliver(
        self, tenant: str, operation_id: str, backend: IdempotentDraftBackend, now: int
    ) -> str:
        # Worker identity/tenant selection is supplied by trusted dispatch infrastructure.
        # This is synchronous local polling, not a deployed broker/lease implementation.
        with self.repository.transaction():
            operation = self.repository.operation(operation_id, tenant)
            if operation.state == "confirmed":
                assert operation.receipt is not None
                return operation.receipt
            self.repository.mark_unknown(operation)
        # Persist uncertainty BEFORE network I/O. A crash after a successful remote write
        # leaves 'unknown', so recovery queries the same key instead of inventing a new one.
        receipt = backend.lookup(operation_id)
        if receipt is None:
            # An expired approval does not prevent looking up an earlier effect,
            # but it must prevent starting a fresh write attempt.
            with self.repository.transaction():
                task = self.repository.task(operation.task_id, tenant)
                self.validate_approval(task, now)
                if task["payload"] != operation.payload:
                    raise PermissionError("Queued payload changed")
            receipt = backend.create_or_get(operation_id, operation.payload)
        with self.repository.transaction():
            self.repository.confirm(operation, receipt)
        return receipt

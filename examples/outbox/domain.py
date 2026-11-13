from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class Operation:
    operation_id: str
    task_id: str
    tenant: str
    payload: str
    fingerprint: str
    state: str
    receipt: str | None


class IdempotentDraftBackend(Protocol):
    """Adapter MUST deduplicate key+payload and reject key reuse with changed payload."""

    def create_or_get(self, operation_id: str, payload: str) -> str: ...

    def lookup(self, operation_id: str) -> str | None: ...

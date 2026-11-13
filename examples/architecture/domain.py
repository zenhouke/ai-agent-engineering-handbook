from dataclasses import dataclass


@dataclass(frozen=True)
class Task:
    task_id: str
    tenant: str
    quantity: int
    unit_cents: int


@dataclass(frozen=True)
class Identity:
    user_id: str
    tenants: frozenset[str]

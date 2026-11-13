"""A task contract keeps predictions separate from external actions."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ResearchTask:
    quantity: int
    budget_cents: int
    evidence_ids: tuple[str, ...]
    may_create_draft: bool = False

    def validate(self) -> None:
        if self.quantity <= 0 or self.budget_cents <= 0:
            raise ValueError("Quantity and budget must be positive")
        if not self.evidence_ids:
            raise ValueError("Evidence is required before comparing quotations")


def affordable(unit_cents: int, shipping_cents: int, task: ResearchTask) -> bool:
    task.validate()
    if unit_cents < 0 or shipping_cents < 0:
        raise ValueError("Missing costs must not be silently replaced with zero")
    return unit_cents * task.quantity + shipping_cents <= task.budget_cents

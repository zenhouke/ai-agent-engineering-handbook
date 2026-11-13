"""Validate explicit work ownership and contracts before choosing a topology."""

from dataclasses import dataclass


@dataclass(frozen=True)
class WorkUnit:
    key: str
    owner: str
    input_contract: str
    output_contract: str
    depends_on: tuple[str, ...]
    budget: int


def validate_work(units: list[WorkUnit]) -> list[str]:
    by_key = {unit.key: unit for unit in units}
    if len(by_key) != len(units):
        raise ValueError("Duplicate work unit")
    for unit in units:
        if (
            not all((unit.key, unit.owner, unit.input_contract, unit.output_contract))
            or unit.budget <= 0
        ):
            raise ValueError("Missing ownership, contract or budget")
        if not set(unit.depends_on) <= by_key.keys():
            raise ValueError("Unknown dependency")
    pending, ordered = set(by_key), []
    while pending:
        ready = sorted(
            key for key in pending if set(by_key[key].depends_on) <= set(ordered)
        )
        if not ready:
            raise ValueError("Cyclic work graph")
        ordered.extend(ready)
        pending.difference_update(ready)
    return ordered


# One WorkUnit owner is accountable for an artifact; multiple reviewers do not erase ownership.
# A useful split needs independent evidence/work, not merely more role names in prompts.

"""Compose artifacts with explicit contracts; do not concatenate arbitrary skill bodies."""

from dataclasses import dataclass

from .skill_planning import Step, ready_steps


@dataclass(frozen=True)
class Artifact:
    contract: str
    skill_version: str
    source_ids: tuple[str, ...]
    complete: bool


def next_steps(
    plan: list[Step],
    completed: dict[str, Artifact],
    allowed: set[str],
    expected_contracts: dict[str, str],
) -> list[Step]:
    names = {step.name for step in plan}
    if not set(completed) <= names:
        raise ValueError("Artifact refers to an unknown plan node")
    for node, artifact in completed.items():
        if (
            not artifact.complete
            or artifact.contract != expected_contracts[node]
            or not artifact.source_ids
        ):
            raise ValueError("Artifact lacks acceptance, matching schema or provenance")
    return ready_steps(plan, set(completed), allowed)


# A new quote version invalidates its comparison and dependent approval artifacts.
# The caller must remove invalid descendants; the plan never treats a call as completion.

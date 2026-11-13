"""Skills are selected procedures; plans contain task-specific dependencies."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Step:
    name: str
    requires: tuple[str, ...]
    skill: str


def ready_steps(
    plan: list[Step], completed: set[str], allowed_skills: set[str]
) -> list[Step]:
    names = {step.name for step in plan}
    if len(names) != len(plan):
        raise ValueError("Step names must be unique")
    if any(not set(step.requires) <= names for step in plan):
        raise ValueError("Unknown dependency")
    ready = [
        step
        for step in plan
        if step.name not in completed
        and set(step.requires) <= completed
        and step.skill in allowed_skills
    ]
    if names - completed and not ready:
        raise ValueError("Plan is cyclic, blocked or requires a disallowed skill")
    return ready


# New evidence can invalidate the plan; it does not silently mark a step complete.

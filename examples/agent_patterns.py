"""A teaching comparison: Plan-and-Execute and bounded Reflection."""

from collections.abc import Callable


def plan_and_execute(
    question: str,
    planner: Callable[[str], list[str]],
    execute: Callable[[str], str],
    max_tasks: int = 5,
) -> list[str]:
    tasks = planner(question)
    if not tasks or len(tasks) > max_tasks:
        raise ValueError("Invalid or over-budget plan")
    return [execute(task) for task in tasks]


def reflect(
    draft: str,
    review: Callable[[str], tuple[bool, str]],
    revise: Callable[[str, str], str],
    rounds: int = 2,
) -> str:
    for _ in range(rounds):
        accepted, feedback = review(draft)
        if accepted:
            return draft
        draft = revise(draft, feedback)
    accepted, _ = review(draft)
    if not accepted:
        raise ValueError("Review budget exhausted")
    return draft


# Model-generated tasks still need authorization; a reviewer is not factual proof.

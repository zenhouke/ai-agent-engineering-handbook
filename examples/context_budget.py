"""Pack context using the target tokenizer's count, not a character estimate."""

from collections.abc import Callable
from dataclasses import dataclass


@dataclass(frozen=True)
class ContextPart:
    text: str
    priority: int
    required: bool = False


def pack(
    parts: list[ContextPart],
    window: int,
    output_reserve: int,
    count_tokens: Callable[[str], int],
) -> list[str]:
    budget = window - output_reserve
    if output_reserve < 0 or budget < 0:
        raise ValueError("Invalid context budget")
    selected = [part.text for part in parts if part.required]
    # The counter must include actual separators/chat-template overhead.
    if count_tokens("\n".join(selected)) > budget:
        raise ValueError(
            "Required instructions do not fit; stop instead of deleting them"
        )
    for part in sorted((p for p in parts if not p.required), key=lambda p: -p.priority):
        proposal = selected + [part.text]
        if count_tokens("\n".join(proposal)) <= budget:
            selected = proposal
    return selected

"""A bounded model/tool loop using an injected provider, never a live API on import."""

from collections.abc import Callable
from dataclasses import dataclass


@dataclass(frozen=True)
class Decision:
    tool: str | None
    argument: str
    answer: str = ""


def run(
    model: Callable[[list[dict]], Decision],
    tools: dict[str, Callable[[str], str]],
    question: str,
    max_steps: int = 5,
) -> tuple[str, list[dict]]:
    if max_steps < 1:
        raise ValueError("A positive step budget is required")
    messages = [{"role": "user", "content": question}]
    for _ in range(max_steps):
        decision = model(messages.copy())
        if decision.tool is None:
            if not decision.answer:
                raise ValueError("Empty final answer")
            return decision.answer, messages
        if decision.tool not in tools:
            raise PermissionError("Tool is outside this task's capability set")
        result = tools[decision.tool](decision.argument)
        messages.append(
            {"role": "assistant", "tool": decision.tool, "argument": decision.argument}
        )
        messages.append({"role": "tool", "content": result})
    raise TimeoutError("Step budget exhausted without a final answer")


# Tool implementations must enforce object authorization and result schemas.

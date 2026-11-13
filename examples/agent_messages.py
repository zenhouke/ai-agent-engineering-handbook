"""A typed envelope for Host-controlled collaboration, independent of MCP RPC IDs."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Envelope:
    schema: str
    task_id: str
    run_id: str
    message_id: str
    causation_id: str | None
    sender: str
    recipient: str
    artifact_id: str
    deadline: int


def validate_delivery(
    message: Envelope,
    task_id: str,
    run_id: str,
    receiver: str,
    edges: frozenset[tuple[str, str]],
    now: int,
) -> None:
    if (
        message.schema != "artifact-ready-v1"
        or not message.message_id
        or not message.artifact_id
    ):
        raise ValueError("Invalid envelope or artifact contract")
    if (
        message.task_id != task_id
        or message.run_id != run_id
        or message.recipient != receiver
    ):
        raise PermissionError("Message belongs to another task/run/recipient")
    if (message.sender, message.recipient) not in edges:
        raise PermissionError("Undeclared handoff edge")
    if message.deadline <= now:
        raise TimeoutError("Stale handoff")


# The transport injects authenticated sender identity; a model cannot self-assert it.
# A durable inbox must enforce message_id uniqueness together with its state transition.
# message_id, provider call_id, MCP RPC id and business operation_id have different purposes.

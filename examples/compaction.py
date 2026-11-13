"""Protected task facts survive a lossy history summary."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Continuation:
    goal: str
    constraints: tuple[str, ...]
    verified_sources: tuple[str, ...]
    pending_operations: tuple[str, ...]
    summary: str


def compact(previous: Continuation, candidate_summary: str) -> Continuation:
    # A summarizer can compress narrative, but cannot rewrite trusted fields.
    return Continuation(
        previous.goal,
        previous.constraints,
        previous.verified_sources,
        previous.pending_operations,
        candidate_summary,
    )


# Keep original artifacts elsewhere. This packet does not grant tool permission.

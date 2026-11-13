"""Compare matched task-level trials; operational violations are separate release gates."""

from dataclasses import dataclass
from math import ceil, isfinite


@dataclass(frozen=True)
class Trial:
    task_id: str
    success: bool
    cost: float
    latency: float
    unauthorized_actions: int


def compare(baseline: list[Trial], candidate: list[Trial]) -> dict:
    def index(rows):
        result = {x.task_id: x for x in rows}
        if not rows or len(result) != len(rows):
            raise ValueError("Missing/duplicate trials")
        if any(
            not isfinite(x.cost)
            or not isfinite(x.latency)
            or x.cost < 0
            or x.latency < 0
            or x.unauthorized_actions < 0
            for x in rows
        ):
            raise ValueError("Invalid metrics")
        return result

    old, new = index(baseline), index(candidate)
    if old.keys() != new.keys():
        raise ValueError("Compare identical tasks, not cherry-picked subsets")
    n = len(old)
    latencies = sorted(x.latency for x in candidate)
    return {
        "paired_success_delta": sum(
            int(new[k].success) - int(old[k].success) for k in old
        )
        / n,
        "added_cost": sum(new[k].cost - old[k].cost for k in old),
        "candidate_p95_latency": latencies[ceil(0.95 * n) - 1],
        "unauthorized_actions": sum(x.unauthorized_actions for x in candidate),
        "policy_gate_passed": all(x.unauthorized_actions == 0 for x in candidate),
    }


# Fix model/tool/evidence snapshots, track cost/latency per whole task and report sample size.
# This computes metrics on supplied records; no model experiment or production uplift is claimed.

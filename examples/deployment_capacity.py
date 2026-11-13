"""A capacity estimate from measured means, not a benchmark or deployment automation."""

from math import ceil, isfinite


def worker_estimate(
    task_rate: float,
    mean_calls_per_task: float,
    mean_call_seconds: float,
    slots_per_worker: int,
    target_utilization: float,
) -> dict:
    values = (task_rate, mean_calls_per_task, mean_call_seconds, target_utilization)
    if (
        any(not isfinite(x) for x in values)
        or min(values[:3]) <= 0
        or type(slots_per_worker) is not int
        or slots_per_worker <= 0
        or not 0 < target_utilization < 1
    ):
        raise ValueError("Invalid capacity inputs")
    mean_concurrency = task_rate * mean_calls_per_task * mean_call_seconds
    workers = ceil(mean_concurrency / (slots_per_worker * target_utilization))
    return {"mean_inflight_calls": mean_concurrency, "estimated_workers": workers}


# Use measured MEAN service time in Little's-law-style estimates, not p95 as if it were a mean.
# Include retries/fanout in calls_per_task; external quotas, burst backlog and memory can dominate.
# Select process/service boundaries from isolation, scaling and ownership requirements.

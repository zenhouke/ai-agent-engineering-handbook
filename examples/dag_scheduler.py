"""Bounded read-only DAG runner; first failure cancels and awaits all in-flight work."""

import asyncio
from collections.abc import Awaitable, Callable


async def schedule(
    jobs: dict[str, Callable[[], Awaitable[object]]],
    dependencies: dict[str, set[str]],
    concurrency: int,
    timeout: float,
) -> dict:
    if concurrency <= 0 or timeout <= 0 or set(jobs) != set(dependencies):
        raise ValueError("Invalid runner limits/keys")
    if any(not parents <= jobs.keys() for parents in dependencies.values()):
        raise ValueError("Unknown dependency")
    # Validate the whole DAG before any tool runs, including cycles beside a valid branch.
    visited = set()
    while len(visited) < len(jobs):
        ready = {
            key for key in jobs if key not in visited and dependencies[key] <= visited
        }
        if not ready:
            raise ValueError("Cyclic graph")
        visited.update(ready)
    pending, active, results = set(jobs), {}, {}
    try:
        async with asyncio.timeout(timeout):
            while pending or active:
                ready = sorted(
                    key for key in pending if dependencies[key] <= results.keys()
                )
                for key in ready[: concurrency - len(active)]:
                    task = asyncio.create_task(jobs[key]())
                    active[task] = key
                    pending.remove(key)
                done, _ = await asyncio.wait(
                    active, return_when=asyncio.FIRST_COMPLETED
                )
                for task in done:
                    key = active.pop(task)
                    results[key] = task.result()
    finally:
        # Read each completed exception too; cancellation must not leave orphan tasks.
        for task in active:
            task.cancel()
        await asyncio.gather(*active, return_exceptions=True)
    return results


# This process-local runner is not durable and uses fail-fast whole-task policy.
# Cancelling an await does not undo a remote write; mutating tools require operation reconciliation.

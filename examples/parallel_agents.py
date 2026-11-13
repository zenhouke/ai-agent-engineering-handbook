"""Bounded fork/join with cancellation cleanup; independent read-only tasks only."""

import asyncio
from collections.abc import Awaitable, Callable


async def gather_research(
    tasks: list[Callable[[], Awaitable[str]]], concurrency: int = 3, seconds: float = 10
) -> list[str]:
    if concurrency < 1 or seconds <= 0:
        raise ValueError("Positive limits required")
    semaphore = asyncio.Semaphore(concurrency)

    async def limited(task):
        async with semaphore:
            return await task()

    workers = [asyncio.create_task(limited(task)) for task in tasks]
    try:
        async with asyncio.timeout(seconds):
            return await asyncio.gather(*workers)
    finally:
        for worker in workers:
            if not worker.done():
                worker.cancel()
        await asyncio.gather(*workers, return_exceptions=True)


# Cancellation cannot undo an external action already committed by a worker.

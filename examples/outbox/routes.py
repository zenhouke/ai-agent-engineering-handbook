from .handlers import DraftHandler


def enqueue_entry(
    handler: DraftHandler, request: dict, trusted_tenants: frozenset[str], now: int
) -> dict:
    """Transport-neutral entry; real HTTP/RPC middleware injects authenticated scope."""
    return handler.enqueue(request, trusted_tenants, now)

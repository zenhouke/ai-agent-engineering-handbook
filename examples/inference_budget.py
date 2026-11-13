"""Estimate a conventional MHA/GQA KV cache, excluding other allocations."""


def kv_bytes(
    layers: int,
    batch: int,
    length: int,
    kv_heads: int,
    head_dim: int,
    element_bytes: int = 2,
) -> int:
    dimensions = (layers, batch, length, kv_heads, head_dim, element_bytes)
    if any(value <= 0 for value in dimensions):
        raise ValueError("All dimensions must be positive")
    return 2 * layers * batch * length * kv_heads * head_dim * element_bytes


def admits_request(used_bytes: int, request_bytes: int, capacity_bytes: int) -> bool:
    if min(used_bytes, request_bytes, capacity_bytes) < 0:
        raise ValueError("Budgets cannot be negative")
    return used_bytes + request_bytes <= capacity_bytes


# Different architectures and cache quantization change this estimate.

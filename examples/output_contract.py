"""Structure and evidence support are independent checks."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Quotation:
    unit_cents: int
    shipping_cents: int | None
    source_id: str


def total_or_unknown(
    quote: Quotation, quantity: int, allowed_sources: set[str]
) -> int | None:
    if quantity <= 0 or quote.unit_cents < 0:
        raise ValueError("Invalid amount or quantity")
    if quote.source_id not in allowed_sources:
        raise PermissionError("Unknown or unauthorized evidence")
    if quote.shipping_cents is None:
        return None
    if quote.shipping_cents < 0:
        raise ValueError("Shipping must be nonnegative")
    return quote.unit_cents * quantity + quote.shipping_cents


# A real application also verifies that the source supports the extracted fields.

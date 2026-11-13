from dataclasses import dataclass


@dataclass(frozen=True)
class Quote:
    quote_id: str
    unit_cents: int
    shipping_cents: int | None
    currency: str = "CNY"

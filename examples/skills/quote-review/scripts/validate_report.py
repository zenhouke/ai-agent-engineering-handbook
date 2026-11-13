"""Deterministic quote-review-v1 checks; importing this module has no side effects."""


def validate_report(quotes: list[dict], report: dict) -> None:
    if not quotes or set(report) != {
        "totals",
        "incomplete_quote_ids",
        "cheapest_quote_id",
    }:
        raise ValueError("Missing quotations or invalid report fields")
    currencies = {quote["currency"] for quote in quotes}
    if len(currencies) != 1:
        raise ValueError("Incompatible currencies")
    expected, incomplete = {}, []
    for quote in quotes:
        name, unit, shipping = (
            quote["quote_id"],
            quote["unit_cents"],
            quote["shipping_cents"],
        )
        if name in expected or type(unit) is not int or unit < 0:
            raise ValueError("Duplicate ID or invalid money")
        if shipping is not None and (type(shipping) is not int or shipping < 0):
            raise ValueError("Invalid shipping")
        expected[name] = None if shipping is None else unit + shipping
        if shipping is None:
            incomplete.append(name)
    totals = report["totals"]
    if not isinstance(totals, list) or len(totals) != len(expected):
        raise ValueError("Missing or duplicated result rows")
    actual = {}
    for row in totals:
        if (
            not isinstance(row, dict)
            or set(row) != {"quote_id", "total_cents"}
            or row["quote_id"] in actual
        ):
            raise ValueError("Invalid result row")
        value = row["total_cents"]
        if value is not None and type(value) is not int:
            raise ValueError("Totals must be integer cents or null")
        actual[row["quote_id"]] = value
    if actual != expected or report["incomplete_quote_ids"] != incomplete:
        raise ValueError("Unsupported total or missing-evidence declaration")
    cheapest = report["cheapest_quote_id"]
    if incomplete:
        if cheapest is not None:
            raise ValueError("Incomplete comparison cannot declare cheapest under v1")
    elif cheapest not in expected or expected[cheapest] != min(expected.values()):
        raise ValueError("Cheapest quote contradicts complete totals")

"""Three disclosure stages; repeated activation is deduplicated per task session."""

from .skill_host import build_host


def disclosure_trace() -> dict:
    service, session = build_host()
    catalog = service.catalog(
        session.policy
    )  # Only name + description enter the catalog.
    first = service.activate("quote-review", session)
    again = service.activate("quote-review", session)
    assert first is again
    reference = service.resource("quote-review", "references/conditions.md", session)
    return {
        "catalog": catalog,
        "active_count": len(session.active),
        "requested_resource": reference,
        "context": service.context(session),
    }


# Integrity checks read bundle bytes without injecting all those bytes into model context.
# This uses a character limit for illustration; a real Host should budget with its tokenizer.

from .domain import Principal
from .handlers import ApprovalHandler


def claim_entry(
    handler: ApprovalHandler,
    request: dict,
    identity: Principal,
    session_id: str,
    now: int,
) -> dict:
    """Trusted middleware injects identity/session/time; a model supplies only proposal data."""
    return handler.claim(request, identity, session_id, now)

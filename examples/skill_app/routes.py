from .domain import Session
from .handlers import SkillHandler


def activate_entry(handler: SkillHandler, request: dict, session: Session) -> dict:
    """Transport-neutral entry: the Host injects the trusted task session."""
    return handler.activate(request, session)

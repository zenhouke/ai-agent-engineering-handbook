from dataclasses import asdict

from .domain import Session
from .services import SkillService


class SkillHandler:
    def __init__(self, service: SkillService):
        self.service = service

    def activate(self, request: dict, session: Session) -> dict:
        if set(request) != {"name"} or not isinstance(request["name"], str):
            raise ValueError("Expected one skill name")
        return asdict(self.service.activate(request["name"], session))

from .approvals import ApprovalService
from .domain import Action, Principal


class ApprovalHandler:
    def __init__(self, service: ApprovalService):
        self.service = service

    def claim(
        self, request: dict, identity: Principal, session_id: str, now: int
    ) -> dict:
        if set(request) != {"approval_id", "operation_id", "action"}:
            raise ValueError("Invalid claim envelope")
        if any(
            not isinstance(request[key], str) or not request[key]
            for key in ["approval_id", "operation_id"]
        ):
            raise ValueError("Expected nonempty identifiers")
        if not isinstance(request["action"], dict):
            raise TypeError("Expected an action object")
        action = Action(**request["action"])
        self.service.claim(
            identity,
            session_id,
            request["approval_id"],
            action,
            request["operation_id"],
            now,
        )
        return {"operation_id": request["operation_id"], "state": "pending"}

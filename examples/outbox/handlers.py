from .services import DraftService


class DraftHandler:
    def __init__(self, service: DraftService):
        self.service = service

    def enqueue(self, request: dict, trusted_tenants: frozenset[str], now: int) -> dict:
        fields = ("tenant", "task_id", "operation_id")
        if set(request) != set(fields) or any(
            not isinstance(request[field], str) or not request[field]
            for field in fields
        ):
            raise ValueError("Expected three nonempty string fields")
        self.service.enqueue(
            request["tenant"],
            request["task_id"],
            request["operation_id"],
            now,
            trusted_tenants,
        )
        return {"state": "queued", "operation_id": request["operation_id"]}

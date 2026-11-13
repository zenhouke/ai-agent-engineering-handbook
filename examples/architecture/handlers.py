from dataclasses import dataclass

from .domain import Identity
from .services import ReportService


@dataclass(frozen=True)
class Request:
    identity: Identity  # Injected by authentication, never trusted from request JSON.
    tenant: str
    task_id: str


class ReportHandler:
    def __init__(self, service: ReportService):
        self._service = service

    def handle(self, request: Request) -> dict:
        try:
            amount = self._service.subtotal(
                request.identity, request.tenant, request.task_id
            )
            return {"status": 200, "subtotal_cents": amount}
        except PermissionError:
            return {"status": 403, "error": "forbidden"}
        except LookupError:
            return {"status": 404, "error": "not_found"}
        except ValueError:
            return {"status": 400, "error": "invalid_input"}

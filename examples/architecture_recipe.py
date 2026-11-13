"""Compose one-way layers. No server is started; no purchase is performed."""

from .architecture.domain import Identity, Task
from .architecture.handlers import ReportHandler, Request
from .architecture.repos import TaskRepository
from .architecture.routes import dispatch
from .architecture.services import ReportService


def example_request(tenant: str = "A") -> dict:
    repository = TaskRepository([Task("task-1", "A", 1000, 180)])
    service = ReportService(repository)
    handler = ReportHandler(service)
    request = Request(Identity("user-1", frozenset({"A"})), tenant, "task-1")
    return dispatch("GET", "/reports/subtotal", request, handler)


# Protocol router only calls the handler. Handler maps errors; service owns
# authorization/calculation; repository owns scoped data access.
# The response is a subtotal, not a total including unknown tax or shipping.

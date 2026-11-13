from .domain import Identity
from .repos import TaskRepository


class ReportService:
    def __init__(self, repository: TaskRepository):
        self._repository = repository

    def subtotal(self, identity: Identity, tenant: str, task_id: str) -> int:
        if tenant not in identity.tenants:
            raise PermissionError("Identity is not authorized for this tenant")
        task = self._repository.get(tenant, task_id)
        if task.quantity <= 0 or task.unit_cents < 0:
            raise ValueError("Invalid quotation")
        return task.quantity * task.unit_cents

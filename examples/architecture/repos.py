from .domain import Task


class TaskRepository:
    def __init__(self, records: list[Task]):
        self._records = {(task.tenant, task.task_id): task for task in records}

    def get(self, tenant: str, task_id: str) -> Task:
        task = self._records.get((tenant, task_id))
        if task is None:
            raise LookupError("Task not found in tenant scope")
        return task

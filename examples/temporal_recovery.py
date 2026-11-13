"""Temporal reference: durable approval wait and retried activity.

Reference only; no worker is started. Boundary authorization belongs in the API.
The activity backend must enforce idempotency for a stable operation_id.
"""

from dataclasses import dataclass
from datetime import timedelta

from temporalio import activity, workflow
from temporalio.common import RetryPolicy


@dataclass(frozen=True)
class DraftRequest:
    operation_id: str
    action_hash: str
    proposal_json: str


class DraftActivities:
    def __init__(self, backend):
        self.backend = backend

    @activity.defn(name="create_draft")
    async def create_draft(self, request: DraftRequest) -> str:
        return await self.backend.create_or_get(
            request.operation_id, request.proposal_json
        )


@workflow.defn
class ApprovedDraftWorkflow:
    def __init__(self):
        self.approved_hash = ""

    @workflow.signal
    def approve(self, action_hash: str) -> None:
        # Only a trusted, authenticated application should send approval signals.
        self.approved_hash = action_hash

    @workflow.run
    async def run(self, request: DraftRequest) -> str:
        await workflow.wait_condition(
            lambda: self.approved_hash == request.action_hash, timeout=timedelta(days=1)
        )
        return await workflow.execute_activity(
            "create_draft",
            request,
            start_to_close_timeout=timedelta(seconds=30),
            schedule_to_close_timeout=timedelta(minutes=5),
            retry_policy=RetryPolicy(
                maximum_attempts=5,
                non_retryable_error_types=["PermissionError", "ValueError"],
            ),
        )


# Replayed workflow history is not a guarantee of exactly-once remote writes.
# Register ApprovedDraftWorkflow and DraftActivities(backend).create_draft on a Worker.

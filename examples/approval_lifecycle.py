"""Prepare an approved action through routes → handler → service → repository."""

from .governance.approvals import ApprovalService
from .governance.handlers import ApprovalHandler
from .governance.repos import GovernanceRepository
from .governance.routes import claim_entry


def claim_approved(
    connection, request: dict, identity, session_id: str, now: int
) -> dict:
    service = ApprovalService(GovernanceRepository(connection))
    return claim_entry(ApprovalHandler(service), request, identity, session_id, now)


# Never trust approved=true in a model message. Approval rows are server-side records.
# The action hash includes tenant/task, operation, object, amount, recipient and evidence version.
# Claiming prepares work; it does not prove a remote action occurred exactly once.

"""A repeated callback reads the existing operation; it does not mint a new write."""

from .governance.approvals import ApprovalService
from .governance.domain import Principal
from .governance.repos import GovernanceRepository


def inspect_operation(
    connection, actor: Principal, session_id: str, operation_id: str, now: int
) -> dict:
    return ApprovalService(GovernanceRepository(connection)).operation(
        actor, session_id, operation_id, now
    )


# pending means durable work was prepared, not that the remote effect happened.
# Resume adapters query uncertain remote outcomes by the SAME operation_id.
# Revocation after dispatch cannot retroactively undo a remote effect.

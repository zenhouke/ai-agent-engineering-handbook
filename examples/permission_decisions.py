"""Evaluate current facts, not a model-supplied role or cached allow flag."""

from .governance.domain import Action, Principal
from .governance.policies import PolicyService
from .governance.repos import GovernanceRepository
from .governance.sessions import SessionService


def decide_action(
    connection, actor: Principal, session_id: str, action: Action, now: int
):
    repository = GovernanceRepository(connection)
    with repository.transaction():
        context = SessionService(repository).context(actor, session_id, now)
        return PolicyService(repository).decide(context, action)


# allowed=true only answers the current policy check. needs_approval remains a separate gate.

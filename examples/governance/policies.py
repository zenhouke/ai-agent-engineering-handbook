"""A small RBAC+ABAC example, not a reimplementation of Cedar/OPA/OpenFGA."""

from .domain import Action, Context, Decision
from .repos import GovernanceRepository

ROLE_ACTIONS = {
    "viewer": {"read_quote"},
    "operator": {"read_quote", "create_draft"},
    "reviewer": {"read_quote", "approve_draft"},
    "lead": {"read_quote", "create_draft", "approve_draft"},
}


class PolicyService:
    def __init__(self, repository: GovernanceRepository):
        self.repository = repository

    def decide(self, context: Context, action: Action) -> Decision:
        action.validate()
        epoch = self.repository.policy_version()
        member = self.repository.member(context.subject, context.tenant)
        task = self.repository.get("tasks", "task_id", action.task_id)
        if member is None or action.operation not in ROLE_ACTIONS.get(
            member["role"], set()
        ):
            return Decision(False, False, "role_denied", epoch)
        if (
            action.tenant != context.tenant
            or task["tenant"] != context.tenant
            or task["owner"] != context.subject
        ):
            return Decision(False, False, "object_scope_denied", epoch)
        if (
            action.resource_id != task["resource_id"]
            or action.evidence_version != task["evidence_version"]
        ):
            return Decision(False, False, "resource_or_evidence_changed", epoch)
        if action.amount_cents > member["limit_cents"]:
            return Decision(False, False, "amount_limit_exceeded", epoch)
        return Decision(True, True, "write_requires_approval", epoch)

    @staticmethod
    def delegated_scope(
        parent: frozenset[tuple[str, str]], requested: frozenset[tuple[str, str]]
    ) -> frozenset[tuple[str, str]]:
        if not requested <= parent:
            raise PermissionError("Delegation cannot amplify authority")
        return requested


# Policy decisions expire with their policy/resource facts. Never cache by subject alone.

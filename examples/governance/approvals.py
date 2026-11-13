import json

from .domain import Action, Principal
from .policies import ROLE_ACTIONS, PolicyService
from .repos import GovernanceRepository
from .sessions import SessionService


class ApprovalService:
    def __init__(self, repository: GovernanceRepository):
        self.repository = repository
        self.sessions = SessionService(repository)
        self.policy = PolicyService(repository)

    def request(
        self,
        identity: Principal,
        session_id: str,
        action: Action,
        approval_id: str,
        now: int,
        lifetime: int = 300,
    ) -> None:
        if lifetime <= 0:
            raise ValueError("Invalid approval lifetime")
        with self.repository.transaction():
            context = self.sessions.context(identity, session_id, now)
            decision = self.policy.decide(context, action)
            if not decision.allowed:
                raise PermissionError(decision.reason)
            self.repository.request_approval(
                approval_id, context, action, now + lifetime, decision.policy_version
            )

    def current_approval(self, approval_id: str, tenant: str, now: int) -> dict:
        row = self.repository.get("approvals", "approval_id", approval_id)
        if (
            row["tenant"] != tenant
            or row["expires_at"] <= now
            or row["policy_version"] != self.repository.policy_version()
        ):
            raise PermissionError("Approval scope, expiry or policy version changed")
        action = Action(**json.loads(row["action_json"]))
        if action.fingerprint() != row["action_hash"]:
            raise PermissionError("Approval payload changed")
        return row

    def approve(
        self, identity: Principal, session_id: str, approval_id: str, now: int
    ) -> None:
        with self.repository.transaction():
            context = self.sessions.context(identity, session_id, now)
            member = self.repository.member(context.subject, context.tenant)
            if "approve_draft" not in ROLE_ACTIONS.get(member["role"], set()):
                raise PermissionError("No reviewer role")
            row = self.current_approval(approval_id, context.tenant, now)
            if row["requester"] == context.subject:
                raise PermissionError("Independent approver required")
            self.repository.approve(approval_id, context.subject)

    def claim(
        self,
        identity: Principal,
        session_id: str,
        approval_id: str,
        action: Action,
        operation_id: str,
        now: int,
    ) -> None:
        with self.repository.transaction():
            context = self.sessions.context(identity, session_id, now)
            row = self.current_approval(approval_id, context.tenant, now)
            decision = self.policy.decide(context, action)
            if (
                row["requester"] != context.subject
                or not decision.allowed
                or action.fingerprint() != row["action_hash"]
            ):
                raise PermissionError(
                    "Requester, current permission or exact action mismatch"
                )
            # Consumption and pending operation are atomic; uniqueness rejects replay.
            self.repository.claim(row, action, operation_id)
        # This only prepares a durable pending operation. Workers must check revocation/
        # execution policy again before a NEW remote effect; unknown effects need lookup.

    def revoke(
        self, identity: Principal, session_id: str, approval_id: str, now: int
    ) -> None:
        with self.repository.transaction():
            context = self.sessions.context(identity, session_id, now)
            row = self.repository.get("approvals", "approval_id", approval_id)
            if row["tenant"] != context.tenant or context.subject not in {
                row["requester"],
                row["approver"],
            }:
                raise PermissionError("Cannot revoke this approval")
            self.repository.revoke_approval(approval_id)

    def operation(
        self, identity: Principal, session_id: str, operation_id: str, now: int
    ) -> dict:
        with self.repository.transaction():
            context = self.sessions.context(identity, session_id, now)
            row = self.repository.get("operations", "operation_id", operation_id)
            self.sessions.task(context, row["task_id"])
            return {
                "operation_id": operation_id,
                "state": row["state"],
                "action_hash": row["action_hash"],
            }

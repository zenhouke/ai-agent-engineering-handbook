import hashlib
import json
from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class Principal:
    subject: (
        str  # Supplied by trusted authentication middleware, never by model arguments.
    )


@dataclass(frozen=True)
class Context:
    subject: str
    tenant: str
    session_id: str


@dataclass(frozen=True)
class Action:
    tenant: str
    task_id: str
    operation: str
    resource_id: str
    amount_cents: int
    recipient: str
    evidence_version: int
    currency: str = "CNY"

    def validate(self) -> None:
        if self.operation != "create_draft" or any(
            not isinstance(value, str) or not value
            for value in (self.tenant, self.task_id, self.resource_id, self.recipient)
        ):
            raise ValueError("Unsupported or incomplete action")
        if self.currency != "CNY":
            raise ValueError("This reference supports only canonical CNY amounts")
        if (
            type(self.amount_cents) is not int
            or self.amount_cents <= 0
            or type(self.evidence_version) is not int
            or self.evidence_version <= 0
        ):
            raise ValueError("Invalid amount or evidence version")

    def payload(self) -> str:
        self.validate()
        return json.dumps(
            asdict(self), sort_keys=True, separators=(",", ":"), allow_nan=False
        )

    def fingerprint(self) -> str:
        return hashlib.sha256(self.payload().encode()).hexdigest()


@dataclass(frozen=True)
class Decision:
    allowed: bool
    needs_approval: bool
    reason: str
    policy_version: int

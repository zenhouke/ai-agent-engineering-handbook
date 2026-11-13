"""Plan recovery from observed receipts; compensation is a NEW authorized action."""

from dataclasses import dataclass


@dataclass(frozen=True)
class StepReceipt:
    step: str
    operation_id: str
    outcome: str  # confirmed, failed or unknown
    compensation: str | None


def recovery_plan(receipts: list[StepReceipt]) -> dict:
    if len({x.operation_id for x in receipts}) != len(receipts):
        raise ValueError("Duplicate operation identity")
    if any(x.outcome not in {"confirmed", "failed", "unknown"} for x in receipts):
        raise ValueError("Invalid outcome")
    unknown = [x.operation_id for x in receipts if x.outcome == "unknown"]
    if unknown:
        return {
            "phase": "reconcile_first",
            "query_operations": unknown,
            "proposals": [],
        }
    proposals = []
    for receipt in reversed(receipts):
        if receipt.outcome != "confirmed":
            continue
        if receipt.compensation is None:
            return {
                "phase": "manual_review",
                "blocked_at": receipt.operation_id,
                "proposals": [],
            }
        proposals.append(
            {"compensates": receipt.operation_id, "action": receipt.compensation}
        )
    return {"phase": "authorize_compensation", "proposals": proposals}


# Proposals are not executed here. Recheck identity, scope and approval for each compensation.
# A Saga coordinates business recovery; it is not a rollback of arbitrary distributed history.

"""Approval binds to an exact action. This does not execute any purchase."""

import hashlib
import json
from dataclasses import dataclass

from .workflow import transition


@dataclass(frozen=True)
class Approval:
    tenant: str
    action_hash: str
    expires_at: int


def action_hash(action: dict) -> str:
    encoded = json.dumps(action, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return hashlib.sha256(encoded.encode()).hexdigest()


def approve_draft(
    state: str, tenant: str, action: dict, approval: Approval, now: int
) -> str:
    if approval.tenant != tenant or approval.expires_at <= now:
        raise PermissionError("Approval scope or expiry mismatch")
    if action_hash(action) != approval.action_hash:
        raise PermissionError("Action changed after approval")
    return transition(state, "approve")


# Hashing needs a canonical action schema with normalized currency, units and recipients.
# An unknown remote outcome goes to reconciliation; do not create a fresh operation ID.

# Retrieved text cannot grant action authority.

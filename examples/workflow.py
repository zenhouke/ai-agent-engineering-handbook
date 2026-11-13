"""Legal state transitions remain deterministic even when a model chooses a tool."""

TRANSITIONS = {
    "received": {"analyze": "analyzing", "cancel": "cancelled"},
    "analyzing": {
        "missing": "needs_input",
        "report": "report_ready",
        "fail": "failed",
        "cancel": "cancelled",
    },
    "needs_input": {"reply": "analyzing", "cancel": "cancelled"},
    "report_ready": {
        "request_draft": "awaiting_approval",
        "finish": "completed",
        "cancel": "cancelled",
    },
    "awaiting_approval": {
        "approve": "executing",
        "change": "analyzing",
        "cancel": "cancelled",
    },
    "executing": {"receipt": "completed", "uncertain": "unknown", "fail": "failed"},
    "unknown": {
        "receipt": "completed",
        "confirmed_failure": "failed",
        "unqueryable": "manual_review",
    },
    "manual_review": {"confirmed_success": "completed", "confirmed_failure": "failed"},
    "completed": {},
    "failed": {},
    "cancelled": {},
}


def transition(state: str, event: str) -> str:
    if state not in TRANSITIONS or event not in TRANSITIONS[state]:
        raise ValueError(f"Illegal transition: {state} + {event}")
    return TRANSITIONS[state][event]


# An executing operation cannot simply become 'cancelled': its remote outcome needs reconciliation.

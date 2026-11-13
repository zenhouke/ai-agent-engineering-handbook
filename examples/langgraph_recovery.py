"""LangGraph reference: separate proposal, approval and side-effect nodes.

Supply a durable checkpointer and an idempotent domain adapter in production.
This file is supplied as reference code; no model call or graph starts on import.
"""

from typing import TypedDict

from .approval import action_hash


class TaskState(TypedDict):
    operation_id: str
    proposal: dict
    approved: bool
    receipt: str


def build_graph(checkpointer, create_draft):
    from langgraph.graph import END, START, StateGraph
    from langgraph.types import interrupt

    def approval(state: TaskState) -> dict:
        fingerprint = action_hash(state["proposal"])
        reply = interrupt({"action_hash": fingerprint, "proposal": state["proposal"]})
        # A trusted API must authorize the approver before it issues Command(resume=...).
        if (
            not isinstance(reply, dict)
            or reply.get("action_hash") != fingerprint
            or not reply.get("approved")
        ):
            raise PermissionError("Approval is absent or applies to a different action")
        return {"approved": True}

    def execute(state: TaskState) -> dict:
        if not state.get("approved"):
            raise PermissionError("No approved action")
        receipt = create_draft(state["operation_id"], state["proposal"])
        # The external adapter must deduplicate/query this operation_id.
        # Do not wrap arbitrary side effects in the approval node: it may restart.
        return {"receipt": receipt}

    graph = StateGraph(TaskState)
    graph.add_node("approval", approval)
    graph.add_node("execute", execute)
    graph.add_edge(START, "approval")
    graph.add_edge("approval", "execute")
    graph.add_edge("execute", END)
    return graph.compile(checkpointer=checkpointer)


# Invoke using a stable thread_id; resume with Command(resume=...) on that thread.
# InMemorySaver is for process-local examples, not cross-process crash recovery.

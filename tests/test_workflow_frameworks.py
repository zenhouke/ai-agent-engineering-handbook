"""Optional framework semantics, without an LLM, Temporal server or model training."""

import importlib.util
import unittest


@unittest.skipUnless(
    importlib.util.find_spec("langgraph"), "Optional LangGraph dependency missing"
)
class LangGraphRecoveryTests(unittest.TestCase):
    def test_interrupt_creates_no_effect_and_resume_uses_stable_key(self):
        from langgraph.checkpoint.memory import InMemorySaver
        from langgraph.types import Command

        from examples.approval import action_hash
        from examples.langgraph_recovery import build_graph

        effects = {}
        calls = []

        def create_draft(key, proposal):
            calls.append(key)
            return effects.setdefault(key, "draft-1")

        graph = build_graph(InMemorySaver(), create_draft)
        proposal = {"currency": "CNY", "amount_cents": 25000}
        config = {"configurable": {"thread_id": "task-1"}}
        graph.invoke({"proposal": proposal, "operation_id": "op-1"}, config)
        self.assertEqual([], calls)
        self.assertEqual(("approval",), graph.get_state(config).next)
        result = graph.invoke(
            Command(resume={"approved": True, "action_hash": action_hash(proposal)}),
            config,
        )
        self.assertEqual("draft-1", result["receipt"])
        self.assertEqual(["op-1"], calls)
        self.assertEqual((), graph.get_state(config).next)

    def test_changed_approval_hash_cannot_execute(self):
        from langgraph.checkpoint.memory import InMemorySaver
        from langgraph.types import Command

        from examples.langgraph_recovery import build_graph

        calls = []
        graph = build_graph(InMemorySaver(), lambda *args: calls.append(args))
        config = {"configurable": {"thread_id": "task-denied"}}
        graph.invoke(
            {"proposal": {"amount_cents": 25000}, "operation_id": "op-denied"}, config
        )
        with self.assertRaises(PermissionError):
            graph.invoke(
                Command(resume={"approved": True, "action_hash": "different"}), config
            )
        self.assertEqual([], calls)


@unittest.skipUnless(
    importlib.util.find_spec("temporalio"), "Optional Temporal dependency missing"
)
class TemporalActivityContractTests(unittest.IsolatedAsyncioTestCase):
    async def test_activity_delegates_stable_operation_to_backend(self):
        from examples.temporal_recovery import DraftActivities, DraftRequest

        calls = []

        class Backend:
            async def create_or_get(self, key, payload):
                calls.append((key, payload))
                return "draft-1"

        activity = DraftActivities(Backend())
        request = DraftRequest("op-1", "hash-1", '{"amount_cents":25000}')
        self.assertEqual("draft-1", await activity.create_draft(request))
        self.assertEqual([("op-1", request.proposal_json)], calls)
        # Direct activity invocation checks adapter input only, not server replay/retries.

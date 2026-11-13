"""Exercise non-training contracts only; tensor/training functions are not called."""

import asyncio
import sqlite3
import unittest
from time import monotonic

from examples.approval import Approval, action_hash, approve_draft
from examples.architecture_recipe import example_request
from examples.checkpoints import initialize, save
from examples.compaction import Continuation, compact
from examples.context_budget import ContextPart, pack
from examples.evaluation import Result, evaluate
from examples.hybrid_retrieval import reciprocal_rank_fusion
from examples.language_model import transition_probabilities
from examples.memory_scope import Memory, recall
from examples.parallel_agents import gather_research
from examples.react_loop import Decision, run
from examples.runtime_budget import Budget
from examples.skill_planning import Step, ready_steps
from examples.workflow import TRANSITIONS, transition


class ReferenceContracts(unittest.TestCase):
    def test_rrf_uses_ranks_and_excludes_unauthorized_ids(self):
        result = dict(
            reciprocal_rank_fusion([["A", "B", "A"], ["B", "private", "A"]], {"A", "B"})
        )
        self.assertAlmostEqual(result["A"], 1 / 61 + 1 / 63)
        self.assertAlmostEqual(result["B"], 1 / 62 + 1 / 61)
        self.assertNotIn("private", result)

    def test_bigram_smoothing_normalizes_and_has_sentence_end(self):
        rows = transition_probabilities(["aba", "abb"])
        self.assertIn("<end>", rows["a"])
        for row in rows.values():
            self.assertAlmostEqual(sum(row.values()), 1)
        self.assertAlmostEqual(rows["a"]["b"], 0.5)

    def test_react_observation_reaches_next_decision(self):
        def model(messages):
            if len(messages) == 1:
                return Decision("read", "quote-A")
            self.assertEqual(messages[-1]["content"], "verified quote-A")
            return Decision(None, "", "supported report")

        answer, _ = run(model, {"read": lambda key: "verified " + key}, "compare")
        self.assertEqual(answer, "supported report")

    def test_react_denies_unknown_tool_and_bounds_loop(self):
        with self.assertRaises(PermissionError):
            run(lambda _: Decision("write", "order"), {}, "research")
        with self.assertRaises(TimeoutError):
            run(lambda _: Decision("read", "q"), {"read": lambda _: "q"}, "research", 2)

    def test_checkpoint_stale_write_cannot_replace_new_state(self):
        connection = sqlite3.connect(":memory:")
        self.addCleanup(connection.close)
        initialize(connection)
        save(connection, "A", "t", 0, {"state": "old"})
        save(connection, "A", "t", 1, {"state": "new"})
        with self.assertRaises(RuntimeError):
            save(connection, "A", "t", 1, {"state": "stale"})
        row = connection.execute("SELECT version,payload FROM checkpoints").fetchone()
        self.assertEqual(row[0], 2)
        self.assertIn('"new"', row[1])

    def test_state_table_has_no_undefined_targets(self):
        targets = {
            target for events in TRANSITIONS.values() for target in events.values()
        }
        self.assertLessEqual(targets, TRANSITIONS.keys())
        for terminal in ("completed", "failed", "cancelled"):
            self.assertEqual(TRANSITIONS[terminal], {})

    def test_inflight_cancel_requires_reconciliation(self):
        with self.assertRaises(ValueError):
            transition("executing", "cancel")
        self.assertEqual(transition("executing", "uncertain"), "unknown")
        self.assertEqual(transition("unknown", "unqueryable"), "manual_review")

    def test_changed_or_expired_approval_does_not_execute(self):
        action = {"quantity": 1000, "recipient": "supplier-A"}
        approval = Approval("A", action_hash(action), 100)
        self.assertEqual(
            approve_draft("awaiting_approval", "A", action, approval, 50), "executing"
        )
        for changed, now in [(dict(action, quantity=2000), 50), (action, 100)]:
            with self.assertRaises(PermissionError):
                approve_draft("awaiting_approval", "A", changed, approval, now)

    def test_context_protects_required_constraints(self):
        parts = [ContextPart("budget=100", 0, True), ContextPart("verbose history", 10)]
        self.assertEqual(pack(parts, 20, 5, len), ["budget=100"])
        with self.assertRaises(ValueError):
            pack(parts, 5, 0, len)

    def test_compaction_cannot_change_trusted_fields(self):
        old = Continuation(
            "research", ("no purchase",), ("source-A",), ("unknown-op",), "long"
        )
        new = compact(old, "a shorter, possibly inaccurate narrative")
        self.assertEqual(new.constraints, old.constraints)
        self.assertEqual(new.pending_operations, ("unknown-op",))

    def test_memory_scope_verification_and_expiry(self):
        good = Memory("A", "u", "pref", "source", True, 100)
        records = [
            good,
            Memory("B", "u", "private", "s", True, 100),
            Memory("A", "u", "guess", "s", False, 100),
        ]
        self.assertEqual(recall(records, "A", "u", 50), [good])
        self.assertEqual(recall(records, "A", "u", 100), [])

    def test_plan_rejects_cycles(self):
        with self.assertRaises(ValueError):
            ready_steps(
                [Step("a", ("b",), "read"), Step("b", ("a",), "read")], set(), {"read"}
            )

    def test_cost_reservation_cannot_overspend(self):
        budget = Budget(2, 10, monotonic() + 5)
        with self.assertRaises(ValueError):
            budget.reserve(11)
        self.assertEqual(budget.remaining_units, 10)
        budget.reserve(6)
        self.assertEqual(budget.remaining_units, 4)

    def test_safety_gate_is_independent_of_average_success(self):
        results = [Result("normal", True, True, False)] * 9 + [
            Result("attack", False, False, True)
        ]
        report = evaluate(results)
        self.assertEqual(report["task_success"], 0.9)
        self.assertFalse(report["safety_gate_passed"])

    def test_layered_route_keeps_tenant_authorization(self):
        self.assertEqual(
            example_request("A"), {"status": 200, "subtotal_cents": 180000}
        )
        self.assertEqual(example_request("B")["status"], 403)


class ParallelCleanup(unittest.IsolatedAsyncioTestCase):
    async def test_timeout_awaits_cancelled_workers(self):
        cleaned = []

        async def task():
            try:
                await asyncio.sleep(5)
                return "unused"
            finally:
                cleaned.append(True)

        with self.assertRaises(TimeoutError):
            await gather_research([task, task], concurrency=2, seconds=0.02)
        self.assertEqual(cleaned, [True, True])

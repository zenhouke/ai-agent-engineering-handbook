import asyncio
import unittest
from dataclasses import replace

from examples.agent_messages import Envelope, validate_delivery
from examples.collaboration_evaluation import Trial, compare
from examples.dag_scheduler import schedule
from examples.deployment_capacity import worker_estimate
from examples.failure_recovery import StepReceipt, recovery_plan
from examples.shared_artifacts import Observation, reconcile
from examples.task_decomposition import WorkUnit, validate_work


class DesignContracts(unittest.TestCase):
    def test_work_graph_requires_owner_contracts_and_no_cycles(self):
        a = WorkUnit("a", "researcher", "query-v1", "evidence-v1", (), 10)
        b = WorkUnit("b", "writer", "evidence-v1", "report-v1", ("a",), 5)
        self.assertEqual(["a", "b"], validate_work([b, a]))
        with self.assertRaises(ValueError):
            validate_work([replace(a, owner="")])
        with self.assertRaises(ValueError):
            validate_work([replace(a, depends_on=("b",)), b])

    def test_messages_bind_task_run_edge_and_deadline(self):
        m = Envelope(
            "artifact-ready-v1",
            "t",
            "r",
            "m1",
            None,
            "researcher",
            "writer",
            "artifact-1",
            10,
        )
        edges = frozenset({("researcher", "writer")})
        validate_delivery(m, "t", "r", "writer", edges, 1)
        with self.assertRaises(PermissionError):
            validate_delivery(m, "other", "r", "writer", edges, 1)
        with self.assertRaises(PermissionError):
            validate_delivery(
                replace(m, sender="unknown"), "t", "r", "writer", edges, 1
            )
        with self.assertRaises(TimeoutError):
            validate_delivery(m, "t", "r", "writer", edges, 10)

    def test_conflicting_majority_does_not_establish_fact(self):
        values = [
            Observation("shipping", "free", "ad-copy", 1, "w1"),
            Observation("shipping", "free", "ad-copy", 1, "w2"),
            Observation("shipping", "80", "contract", 2, "w3"),
        ]
        result = reconcile(values)
        self.assertFalse(result["complete"])
        self.assertNotIn("shipping", result["accepted"])
        self.assertEqual(3, len(result["conflicts"]["shipping"]))

    def test_unknown_effect_blocks_blind_compensation(self):
        items = [
            StepReceipt("reserve", "op1", "confirmed", "release"),
            StepReceipt("draft", "op2", "unknown", "delete_draft"),
        ]
        result = recovery_plan(items)
        self.assertEqual("reconcile_first", result["phase"])
        self.assertEqual([], result["proposals"])
        done = recovery_plan([items[0], replace(items[1], outcome="confirmed")])
        self.assertEqual(["op2", "op1"], [x["compensates"] for x in done["proposals"]])

    def test_task_metrics_require_matched_cases_and_separate_policy_gate(self):
        before = [Trial("t", False, 1.0, 2.0, 0)]
        after = [Trial("t", True, 3.0, 1.0, 1)]
        result = compare(before, after)
        self.assertEqual(1.0, result["paired_success_delta"])
        self.assertFalse(result["policy_gate_passed"])
        with self.assertRaises(ValueError):
            compare(before, [replace(after[0], task_id="other")])

    def test_capacity_includes_fanout_and_rejects_bad_limits(self):
        result = worker_estimate(2.0, 3.0, 0.5, 2, 0.5)
        self.assertEqual(3.0, result["mean_inflight_calls"])
        self.assertEqual(3, result["estimated_workers"])
        with self.assertRaises(ValueError):
            worker_estimate(1, 1, 1, 0, 0.5)


class SchedulerContracts(unittest.IsolatedAsyncioTestCase):
    async def test_only_ready_nodes_run_and_concurrency_is_bounded(self):
        running = peak = 0
        finished = set()

        def job(name, parents):
            async def call():
                nonlocal running, peak
                self.assertTrue(parents <= finished)
                running += 1
                peak = max(peak, running)
                try:
                    await asyncio.sleep(0.01)
                    finished.add(name)
                    return name
                finally:
                    running -= 1

            return call

        deps = {"a": set(), "b": set(), "c": {"a", "b"}}
        result = await schedule({k: job(k, v) for k, v in deps.items()}, deps, 2, 1)
        self.assertEqual({"a", "b", "c"}, set(result))
        self.assertEqual(2, peak)

    async def test_timeout_cancels_and_awaits_workers(self):
        cleaned = []

        async def slow():
            try:
                await asyncio.sleep(10)
            finally:
                cleaned.append(True)

        with self.assertRaises(TimeoutError):
            await schedule({"a": slow}, {"a": set()}, 1, 0.01)
        self.assertEqual([True], cleaned)

    async def test_cycle_rejected_before_independent_job_executes(self):
        called = []

        async def job():
            called.append(True)

        with self.assertRaises(ValueError):
            await schedule(
                {"a": job, "b": job, "c": job},
                {"a": set(), "b": {"c"}, "c": {"b"}},
                2,
                1,
            )
        self.assertFalse(called)

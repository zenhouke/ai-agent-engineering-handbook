"""Test session isolation, current policy, exact approval and transaction replay windows."""

import sqlite3
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from pathlib import Path

from examples.governance.approvals import ApprovalService
from examples.governance.domain import Action, Principal
from examples.governance.policies import PolicyService
from examples.governance.repos import GovernanceRepository
from examples.governance.sessions import SessionService


class GovernanceTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.database = Path(temp.name) / "state.db"
        self.connection = sqlite3.connect(self.database, isolation_level=None)
        self.addCleanup(self.connection.close)
        self.repo = GovernanceRepository(self.connection)
        self.repo.initialize()
        self.repo.set_member("alice", "tenant-a", "operator", 50000)
        self.repo.set_member("bob", "tenant-a", "reviewer", 50000)
        self.repo.set_member("mallory", "tenant-b", "operator", 50000)
        self.sessions = SessionService(self.repo)
        self.approvals = ApprovalService(self.repo)
        self.alice, self.bob, self.mallory = map(Principal, ["alice", "bob", "mallory"])
        self.sid = self.sessions.open(self.alice, "tenant-a", 0)
        self.bsid = self.sessions.open(self.bob, "tenant-a", 0)
        self.msid = self.sessions.open(self.mallory, "tenant-b", 0)
        self.sessions.create_task(
            self.alice, self.sid, "task-a", "conversation-a", "quote-a", 1
        )
        self.action = Action(
            "tenant-a", "task-a", "create_draft", "quote-a", 25000, "supplier-a", 1
        )

    def requested(self):
        self.approvals.request(self.alice, self.sid, self.action, "approval-a", 10)

    def approved(self):
        self.requested()
        self.approvals.approve(self.bob, self.bsid, "approval-a", 11)

    def test_session_is_locator_not_identity_proof(self):
        with self.assertRaises(PermissionError):
            self.sessions.context(self.bob, self.sid, 1)
        with self.assertRaises(PermissionError):
            self.sessions.open(self.alice, "tenant-b", 1)

    def test_close_session_preserves_task_and_new_session_can_resume(self):
        self.sessions.close(self.alice, self.sid, 2)
        with self.assertRaises(PermissionError):
            self.sessions.resume(self.alice, self.sid, "task-a", "run-1", 1, 3)
        fresh = self.sessions.open(self.alice, "tenant-a", 3)
        self.sessions.resume(self.alice, fresh, "task-a", "run-1", 1, 4)
        self.assertEqual(
            "running", self.repo.get("tasks", "task_id", "task-a")["state"]
        )

    def test_expired_session_cannot_resume(self):
        short = self.sessions.open(self.alice, "tenant-a", 0, lifetime=2)
        with self.assertRaises(PermissionError):
            self.sessions.resume(self.alice, short, "task-a", "run-1", 1, 2)

    def test_cross_tenant_task_and_stale_version_are_rejected(self):
        with self.assertRaises(PermissionError):
            self.sessions.resume(self.mallory, self.msid, "task-a", "run-1", 1, 3)
        self.sessions.resume(self.alice, self.sid, "task-a", "run-1", 1, 3)
        with self.assertRaises(RuntimeError):
            self.sessions.resume(self.alice, self.sid, "task-a", "run-2", 1, 4)

    def test_changed_role_is_not_frozen_in_old_session(self):
        self.repo.set_member("alice", "tenant-a", "viewer", 50000)
        with self.assertRaises(PermissionError):
            self.sessions.resume(self.alice, self.sid, "task-a", "run-1", 1, 3)

    def test_run_insert_failure_rolls_back_task_claim(self):
        self.sessions.create_task(
            self.alice, self.sid, "task-b", "conversation-b", "quote-b", 1
        )
        self.sessions.resume(self.alice, self.sid, "task-a", "run-1", 1, 3)
        with self.assertRaises(sqlite3.IntegrityError):
            self.sessions.resume(self.alice, self.sid, "task-b", "run-1", 1, 4)
        row = self.repo.get("tasks", "task_id", "task-b")
        self.assertEqual(("paused", 1), (row["state"], row["version"]))

    def test_permission_and_approval_are_separate_decisions(self):
        context = self.sessions.context(self.alice, self.sid, 1)
        decision = PolicyService(self.repo).decide(context, self.action)
        self.assertTrue(decision.allowed)
        self.assertTrue(decision.needs_approval)
        denied = PolicyService(self.repo).decide(
            context, replace(self.action, amount_cents=50001)
        )
        self.assertFalse(denied.allowed)

    def test_delegation_cannot_amplify_scope(self):
        parent = frozenset({("read_quote", "quote-a")})
        self.assertEqual(parent, PolicyService.delegated_scope(parent, parent))
        with self.assertRaises(PermissionError):
            PolicyService.delegated_scope(
                parent, frozenset({("create_draft", "quote-b")})
            )

    def test_pending_or_self_approval_cannot_claim(self):
        self.requested()
        with self.assertRaises(RuntimeError):
            self.approvals.claim(
                self.alice, self.sid, "approval-a", self.action, "op-a", 12
            )
        with self.assertRaises(PermissionError):
            self.approvals.approve(self.alice, self.sid, "approval-a", 12)
        self.repo.set_member("alice", "tenant-a", "lead", 50000)
        # Even a role with both powers cannot approve its own new request.
        self.sessions.create_task(
            self.alice, self.sid, "task-self", "conversation-a", "quote-a", 13
        )
        self.approvals.request(
            self.alice,
            self.sid,
            replace(self.action, task_id="task-self"),
            "approval-self",
            14,
        )
        with self.assertRaises(PermissionError):
            self.approvals.approve(self.alice, self.sid, "approval-self", 15)

    def test_exact_action_fields_cannot_change_after_approval(self):
        self.approved()
        for field, value in [
            ("amount_cents", 24000),
            ("recipient", "supplier-b"),
            ("resource_id", "quote-b"),
            ("evidence_version", 2),
        ]:
            with self.subTest(field=field), self.assertRaises(PermissionError):
                self.approvals.claim(
                    self.alice,
                    self.sid,
                    "approval-a",
                    replace(self.action, **{field: value}),
                    "op-a",
                    12,
                )
        self.assertEqual(
            "approved",
            self.repo.get("approvals", "approval_id", "approval-a")["status"],
        )

    def test_policy_change_or_expiry_invalidates_approval(self):
        self.approved()
        with self.assertRaises(PermissionError):
            self.approvals.claim(
                self.alice, self.sid, "approval-a", self.action, "op-a", 310
            )
        self.repo.set_member("alice", "tenant-a", "operator", 10000)
        with self.assertRaises(PermissionError):
            self.approvals.claim(
                self.alice, self.sid, "approval-a", self.action, "op-a", 12
            )

    def test_new_evidence_and_revocation_block_claim(self):
        self.approved()
        self.connection.execute(
            "UPDATE tasks SET evidence_version=2 WHERE task_id='task-a'"
        )
        with self.assertRaises(PermissionError):
            self.approvals.claim(
                self.alice, self.sid, "approval-a", self.action, "op-a", 12
            )
        self.approvals.revoke(self.alice, self.sid, "approval-a", 13)
        self.assertEqual("paused", self.repo.get("tasks", "task_id", "task-a")["state"])
        with self.assertRaises(PermissionError):
            self.approvals.claim(
                self.alice, self.sid, "approval-a", self.action, "op-a", 14
            )

    def test_approval_consumption_and_pending_operation_are_atomic(self):
        self.approved()
        self.approvals.claim(
            self.alice, self.sid, "approval-a", self.action, "op-a", 12
        )
        with self.assertRaises(RuntimeError):
            self.approvals.claim(
                self.alice, self.sid, "approval-a", self.action, "op-b", 13
            )
        self.assertEqual(
            "pending",
            self.approvals.operation(self.alice, self.sid, "op-a", 13)["state"],
        )
        with self.assertRaises(PermissionError):
            self.approvals.operation(self.mallory, self.msid, "op-a", 13)

    def test_unique_operation_failure_rolls_back_consumption(self):
        self.approved()
        self.approvals.claim(
            self.alice, self.sid, "approval-a", self.action, "op-a", 12
        )
        self.sessions.create_task(
            self.alice, self.sid, "task-b", "conversation-b", "quote-b", 13
        )
        second = replace(self.action, task_id="task-b", resource_id="quote-b")
        self.approvals.request(self.alice, self.sid, second, "approval-b", 14)
        self.approvals.approve(self.bob, self.bsid, "approval-b", 15)
        with self.assertRaises(sqlite3.IntegrityError):
            self.approvals.claim(self.alice, self.sid, "approval-b", second, "op-a", 16)
        self.assertEqual(
            "approved",
            self.repo.get("approvals", "approval_id", "approval-b")["status"],
        )
        self.assertEqual(
            "awaiting_approval", self.repo.get("tasks", "task_id", "task-b")["state"]
        )

    def test_two_connections_cannot_consume_same_approval_twice(self):
        self.approved()

        def claim(key):
            connection = sqlite3.connect(self.database, isolation_level=None)
            try:
                ApprovalService(GovernanceRepository(connection)).claim(
                    self.alice, self.sid, "approval-a", self.action, key, 12
                )
                return True
            except RuntimeError:
                return False
            finally:
                connection.close()

        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(claim, ["op-1", "op-2"]))
        self.assertEqual(1, sum(results))
        self.assertEqual(
            1, self.connection.execute("SELECT count(*) FROM operations").fetchone()[0]
        )

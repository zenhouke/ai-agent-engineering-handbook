"""Inject real SQLite transaction failures and a successful-but-lost remote reply."""

import hashlib
import sqlite3
import unittest

from examples.outbox.repos import OutboxRepository
from examples.outbox.services import DraftService


class DeduplicatingBackend:
    def __init__(self):
        self.records = {}
        self.lose_response = False
        self.creations = 0

    def lookup(self, key):
        item = self.records.get(key)
        return item[1] if item else None

    def create_or_get(self, key, payload):
        if key in self.records:
            if self.records[key][0] != payload:
                raise ValueError("Key reused with changed payload")
            return self.records[key][1]
        self.creations += 1
        receipt = f"draft-{self.creations}"
        self.records[key] = (payload, receipt)
        if self.lose_response:
            raise TimeoutError("Remote succeeded, response lost")
        return receipt


class OutboxRecoveryTests(unittest.TestCase):
    def setUp(self):
        self.connection = sqlite3.connect(":memory:", isolation_level=None)
        self.addCleanup(self.connection.close)
        self.repo = OutboxRepository(self.connection)
        self.repo.initialize()
        self.repo.seed_approved(
            "t1",
            "tenant-a",
            '{"amount_cents":25000}',
            hashlib.sha256(b'{"amount_cents":25000}').hexdigest(),
            100,
        )
        self.service = DraftService(self.repo)
        self.scope = frozenset({"tenant-a"})

    def enqueue(self, task="t1", operation="op1"):
        self.service.enqueue("tenant-a", task, operation, 10, self.scope)

    def test_state_and_outbox_commit_together(self):
        self.enqueue()
        self.assertEqual("queued", self.repo.task("t1", "tenant-a")["state"])
        self.assertEqual("pending", self.repo.operation("op1", "tenant-a").state)

    def test_insert_failure_rolls_back_state_transition(self):
        self.enqueue()
        self.repo.seed_approved(
            "t2", "tenant-a", "{}", hashlib.sha256(b"{}").hexdigest(), 100
        )
        with self.assertRaises(sqlite3.IntegrityError):
            self.enqueue(
                task="t2"
            )  # Unique operation key collision AFTER state update.
        self.assertEqual("approved", self.repo.task("t2", "tenant-a")["state"])
        self.assertEqual("t1", self.repo.operation("op1", "tenant-a").task_id)

    def test_lost_success_response_recovers_by_same_key(self):
        self.enqueue()
        remote = DeduplicatingBackend()
        remote.lose_response = True
        with self.assertRaises(TimeoutError):
            self.service.deliver("tenant-a", "op1", remote, now=10)
        self.assertEqual("unknown", self.repo.operation("op1", "tenant-a").state)
        # Fresh service instance knows no in-memory progress and uses only stored state.
        restored = DraftService(OutboxRepository(self.connection))
        self.assertEqual("draft-1", restored.deliver("tenant-a", "op1", remote, now=10))
        self.assertEqual(1, remote.creations)
        self.assertEqual("confirmed", self.repo.task("t1", "tenant-a")["state"])

    def test_redelivery_returns_recorded_receipt(self):
        self.enqueue()
        remote = DeduplicatingBackend()
        first = self.service.deliver("tenant-a", "op1", remote, now=10)
        self.assertEqual(first, self.service.deliver("tenant-a", "op1", remote, now=10))
        self.assertEqual(1, remote.creations)

    def test_scope_and_expiry_cannot_queue(self):
        with self.assertRaises(PermissionError):
            self.service.enqueue("tenant-a", "t1", "op1", 10, frozenset())
        with self.assertRaises(PermissionError):
            self.service.enqueue("tenant-a", "t1", "op1", 100, self.scope)
        self.assertEqual("approved", self.repo.task("t1", "tenant-a")["state"])

    def test_changed_action_invalidates_approval(self):
        self.connection.execute(
            "UPDATE tasks SET fingerprint='changed' WHERE task_id='t1'"
        )
        with self.assertRaises(PermissionError):
            self.enqueue()
        self.assertEqual("approved", self.repo.task("t1", "tenant-a")["state"])

    def test_conflicting_receipt_is_rejected(self):
        self.enqueue()
        self.service.deliver("tenant-a", "op1", DeduplicatingBackend(), now=10)
        with self.assertRaises(RuntimeError), self.repo.transaction():
            self.repo.confirm(self.repo.operation("op1", "tenant-a"), "different-draft")
        self.assertEqual("draft-1", self.repo.operation("op1", "tenant-a").receipt)

    def test_expired_approval_blocks_new_attempt_but_allows_receipt_lookup(self):
        self.enqueue()
        remote = DeduplicatingBackend()
        with self.assertRaises(PermissionError):
            self.service.deliver("tenant-a", "op1", remote, now=100)
        self.assertEqual(0, remote.creations)
        remote.records["op1"] = ('{"amount_cents":25000}', "previous-draft")
        self.assertEqual(
            "previous-draft", self.service.deliver("tenant-a", "op1", remote, now=101)
        )

    def test_mutated_payload_with_old_hash_is_rejected(self):
        self.connection.execute("UPDATE tasks SET payload='{}' WHERE task_id='t1'")
        with self.assertRaises(PermissionError):
            self.enqueue()

"""Commercial gates reject stale authority, changed work and unsupported funds."""

import unittest
from dataclasses import replace

from examples.studio_contracts import (
    ApprovalFact,
    ApprovalKind,
    CustomerConfirmation,
    GateError,
    Order,
    PaymentFact,
    require_delivery,
    require_start,
)


class StudioContractTests(unittest.TestCase):
    def setUp(self):
        self.order = Order("studio", "o1", 1, "c1", 1, "CNY", 100000, 30000)
        self.quote = ApprovalFact(ApprovalKind.QUOTE, self.order, 200, 7)
        self.run = ApprovalFact(ApprovalKind.RUN, self.order, 200, 7)
        self.confirmation = CustomerConfirmation(self.order, "message-1")
        self.payment = PaymentFact("studio", "o1", 1, "CNY", 30000, "bank-1", True)

    def start(self, **changes):
        facts = {
            "order": self.order,
            "quote_approval": self.quote,
            "run_approval": self.run,
            "confirmation": self.confirmation,
            "payment": self.payment,
            "now": 100,
            "authority_epoch": 7,
        }
        facts.update(changes)
        require_start(**facts)

    def test_start_with_matching_deposit(self):
        self.start()

    def test_run_approval_does_not_replace_commercial_approval(self):
        with self.assertRaises(GateError):
            self.start(quote_approval=self.run)

    def test_payment_claim_and_insufficient_funds_are_rejected(self):
        for payment in (
            replace(self.payment, verified=False),
            replace(self.payment, reference=""),
            replace(self.payment, cumulative_minor=29999),
            replace(self.payment, currency="USD"),
            replace(self.payment, workspace="other"),
            replace(self.payment, quote_revision=2),
        ):
            with self.subTest(payment=payment), self.assertRaises(GateError):
                self.start(payment=payment)

    def test_price_customer_and_scope_changes_invalidate_approval(self):
        for order in (
            replace(self.order, total_minor=110000),
            replace(self.order, customer="c2"),
            replace(self.order, revision=2),
            replace(self.order, quote_revision=2),
        ):
            with self.subTest(order=order), self.assertRaises(GateError):
                self.start(order=order)

    def test_confirmation_must_match_current_snapshot(self):
        with self.assertRaises(GateError):
            self.start(confirmation=replace(self.confirmation, native_message_id=""))

    def test_expired_and_revoked_authority_is_rejected(self):
        for changes in ({"now": 200}, {"authority_epoch": 8}):
            with self.subTest(changes=changes), self.assertRaises(GateError):
                self.start(**changes)

    def test_delivery_requires_full_settlement_and_exact_artifact(self):
        approval = ApprovalFact(ApprovalKind.DELIVERY, self.order, 200, 7, "sha256:a")
        full = replace(self.payment, cumulative_minor=100000)
        require_delivery(
            self.order, approval, full, "sha256:a", now=100, authority_epoch=7
        )
        for payment, artifact in ((self.payment, "sha256:a"), (full, "sha256:b")):
            with self.subTest(artifact=artifact), self.assertRaises(GateError):
                require_delivery(
                    self.order, approval, payment, artifact, now=100, authority_epoch=7
                )

    def test_amount_invariants(self):
        for changes in (
            {"deposit_minor": 100001},
            {"deposit_minor": 0},
            {"total_minor": True},
            {"total_minor": 1000.5},
            {"currency": "cny"},
        ):
            with self.subTest(changes=changes), self.assertRaises(GateError):
                replace(self.order, **changes)


if __name__ == "__main__":
    unittest.main()

"""Pure studio business gates; trusted facts come from an authorized service.

These checks do not authenticate a caller, consume an approval, send a message,
or commit a payment. The governance/outbox examples implement those boundaries.
Amounts use integer minor units. A customer chat message is never payment proof.
"""

from dataclasses import dataclass
from enum import Enum


class GateError(ValueError):
    """The proposed transition lacks matching, current business evidence."""


class ApprovalKind(str, Enum):
    RUN = "run"
    QUOTE = "quote"
    DELIVERY = "delivery"


@dataclass(frozen=True)
class Order:
    workspace: str
    order_id: str
    revision: int
    customer: str
    quote_revision: int
    currency: str
    total_minor: int
    deposit_minor: int

    def __post_init__(self) -> None:
        if not all((self.workspace, self.order_id, self.customer)):
            raise GateError("missing order identity")
        if self.revision < 1 or self.quote_revision < 1:
            raise GateError("invalid revision")
        if len(self.currency) != 3 or not self.currency.isascii():
            raise GateError("currency must be an uppercase three-letter code")
        if not self.currency.isalpha() or not self.currency.isupper():
            raise GateError("currency must be an uppercase three-letter code")
        if type(self.total_minor) is not int or type(self.deposit_minor) is not int:
            raise GateError("amounts must be integer minor units")
        if not 0 < self.deposit_minor <= self.total_minor:
            raise GateError("require 0 < deposit <= total")


@dataclass(frozen=True)
class ApprovalFact:
    """Server-loaded fact, never accepted directly as a client's assertion."""

    kind: ApprovalKind
    order: Order
    expires_at: int
    authority_epoch: int
    artifact_hash: str = ""


@dataclass(frozen=True)
class PaymentFact:
    workspace: str
    order_id: str
    quote_revision: int
    currency: str
    cumulative_minor: int
    reference: str
    verified: bool


@dataclass(frozen=True)
class CustomerConfirmation:
    order: Order
    native_message_id: str


def require_approval(
    approval: ApprovalFact,
    kind: ApprovalKind,
    order: Order,
    now: int,
    authority_epoch: int,
    artifact_hash: str = "",
) -> None:
    if approval.kind != kind or approval.order != order:
        raise GateError("approval kind or immutable snapshot mismatch")
    if approval.expires_at <= now or approval.authority_epoch != authority_epoch:
        raise GateError("expired approval or changed authority")
    if approval.artifact_hash != artifact_hash:
        raise GateError("reviewed artifact differs")


def require_payment(order: Order, payment: PaymentFact, required_minor: int) -> None:
    expected = (order.workspace, order.order_id, order.quote_revision, order.currency)
    actual = (
        payment.workspace,
        payment.order_id,
        payment.quote_revision,
        payment.currency,
    )
    if actual != expected or not payment.verified or not payment.reference:
        raise GateError("payment evidence is unverified or belongs to another quote")
    if type(payment.cumulative_minor) is not int:
        raise GateError("invalid payment amount")
    if payment.cumulative_minor < required_minor:
        raise GateError("insufficient verified funds")


def require_start(
    order: Order,
    quote_approval: ApprovalFact,
    run_approval: ApprovalFact,
    confirmation: CustomerConfirmation,
    payment: PaymentFact,
    *,
    now: int,
    authority_epoch: int,
) -> None:
    """A run approval cannot substitute for quote approval or verified funds."""
    require_approval(quote_approval, ApprovalKind.QUOTE, order, now, authority_epoch)
    require_approval(run_approval, ApprovalKind.RUN, order, now, authority_epoch)
    if confirmation.order != order or not confirmation.native_message_id:
        raise GateError("customer has not confirmed this exact order")
    require_payment(order, payment, order.deposit_minor)


def require_delivery(
    order: Order,
    approval: ApprovalFact,
    payment: PaymentFact,
    artifact_hash: str,
    *,
    now: int,
    authority_epoch: int,
) -> None:
    if not artifact_hash:
        raise GateError("missing immutable artifact hash")
    require_approval(
        approval, ApprovalKind.DELIVERY, order, now, authority_epoch, artifact_hash
    )
    require_payment(order, payment, order.total_minor)


if __name__ == "__main__":
    order = Order("studio", "order-42", 1, "customer-7", 1, "CNY", 100000, 30000)
    quote = ApprovalFact(ApprovalKind.QUOTE, order, 200, 1)
    run = ApprovalFact(ApprovalKind.RUN, order, 200, 1)
    confirmation = CustomerConfirmation(order, "native-message-9")
    deposit = PaymentFact("studio", "order-42", 1, "CNY", 30000, "receipt-8", True)
    require_start(order, quote, run, confirmation, deposit, now=100, authority_epoch=1)
    print("Start gate passed; no external action performed")

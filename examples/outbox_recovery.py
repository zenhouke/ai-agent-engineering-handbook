"""Read this assembly with the layered implementation and independent schema.

A local demonstration of atomic queueing and lost-response recovery; no queue
service, model, training, network call or real purchase is started by import.
"""

from .outbox.handlers import DraftHandler
from .outbox.repos import OutboxRepository
from .outbox.routes import enqueue_entry
from .outbox.services import DraftService


def enqueue_approved(
    connection, request: dict, trusted_tenants: frozenset[str], now: int
):
    service = DraftService(OutboxRepository(connection))
    return enqueue_entry(DraftHandler(service), request, trusted_tenants, now)


# Core transaction: validate approval → CAS approved/queued → INSERT unique Outbox → commit.
# Delivery: persist unknown → lookup/create_or_get same key → commit receipt.
# Never infer remote failure from timeout; require dedup/query or manual reconciliation.
# The full repository, service and schema are reproduced in the architecture appendix.

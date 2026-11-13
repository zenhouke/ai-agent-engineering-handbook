"""Application session, task and run are distinct identifiers and lifetimes."""

from .governance.repos import GovernanceRepository
from .governance.sessions import SessionService


def session_service(connection) -> SessionService:
    return SessionService(GovernanceRepository(connection))


# Identity comes from real authentication middleware in deployment; no login server is built.
# A conversation/thread ID locates context; it is never an access credential.
# resume() rechecks current session/membership and uses task-version CAS in one transaction.

"""Resume the same task from a new authorized session; use a fresh run ID."""

from .governance.domain import Principal
from .session_lifecycle import session_service


def resume_task(
    connection,
    actor: Principal,
    session_id: str,
    task_id: str,
    run_id: str,
    expected_version: int,
    now: int,
) -> None:
    session_service(connection).resume(
        actor, session_id, task_id, run_id, expected_version, now
    )


# The CAS and run insert are one transaction. Reusing an old task version is rejected.
# A new session is allowed only for the same authorized subject and tenant.

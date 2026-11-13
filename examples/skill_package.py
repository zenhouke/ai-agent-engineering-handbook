"""Inspect the real package format without executing any bundled scripts."""

from .skill_host import build_host


def describe_package() -> dict:
    service, session = build_host()
    descriptor = service.repository.metadata("quote-review")
    return {
        "name": descriptor.name,
        "version": descriptor.version,
        "catalog": service.catalog(session.policy),
        "declared_tools_grant_permission": False,
    }

"""Explicit scope and provenance before ranking any stored preference."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Memory:
    tenant: str
    user: str
    claim: str
    source: str
    verified: bool
    expires_at: int


def recall(records: list[Memory], tenant: str, user: str, now: int) -> list[Memory]:
    return [
        record
        for record in records
        if record.tenant == tenant
        and record.user == user
        and record.verified
        and record.expires_at > now
    ]


# A remembered fact remains evidence, not an instruction overriding the current user.

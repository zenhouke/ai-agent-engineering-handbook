"""Evidence conflicts are explicit; no last-writer-wins or agent-majority truth."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Observation:
    claim: str
    value: str
    source_id: str
    source_version: int
    worker: str


def reconcile(observations: list[Observation]) -> dict:
    claims = {}
    for item in observations:
        if not item.source_id or item.source_version <= 0:
            raise ValueError("Missing provenance")
        claims.setdefault(item.claim, []).append(item)
    accepted, conflicts = {}, {}
    for key, items in claims.items():
        values = {item.value for item in items}
        if len(values) == 1:
            accepted[key] = {
                "value": items[0].value,
                "sources": sorted({x.source_id for x in items}),
            }
        else:
            conflicts[key] = [
                {"value": x.value, "source": x.source_id, "version": x.source_version}
                for x in items
            ]
    return {"accepted": accepted, "conflicts": conflicts, "complete": not conflicts}


# Different versions are not automatically comparable; trusted freshness rules belong in the service.
# Persist worker artifacts separately, then commit the validated reducer result with CAS.

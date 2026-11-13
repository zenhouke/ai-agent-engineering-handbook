"""Assemble the example Host; no scanning of user-installed skills or execution."""

import json
from pathlib import Path

from .skill_app.domain import Policy, RegistryEntry, Session
from .skill_app.repos import SkillRepository
from .skill_app.services import SkillService


def build_host(root: Path | None = None) -> tuple[SkillService, Session]:
    base = root or Path(__file__).with_name("skills")
    manifest = json.loads((base / "registry.json").read_text())
    registry = {
        name: RegistryEntry(
            row["version"],
            row["sha256"],
            tuple(row["bindings"]),
            row["metadata_sha256"],
        )
        for name, row in manifest.items()
    }
    service = SkillService(SkillRepository(base), registry, frozenset({"read_quote"}))
    session = Session(
        Policy(frozenset({"quote-review"}), frozenset({"read_quote"}), frozenset({"A"}))
    )
    return service, session


# Registry hashes/bindings are trusted deployment configuration, not model-generated.
# Do not auto-register a changed bundle using its freshly computed digest at runtime.

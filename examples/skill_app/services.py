import json
from pathlib import PurePosixPath

from .domain import Activated, Policy, RegistryEntry, Session, ToolAdapter
from .repos import (
    SkillRepository,
    descriptor_digest,
    parse_frontmatter,
    snapshot_digest,
)


class SkillService:
    def __init__(
        self,
        repository: SkillRepository,
        registry: dict[str, RegistryEntry],
        available_tools: frozenset[str],
    ):
        self.repository, self.registry, self.available_tools = (
            repository,
            registry,
            available_tools,
        )

    def eligible(self, name: str, policy: Policy) -> RegistryEntry:
        entry = self.registry.get(name)
        if entry is None or name not in policy.allowed_skills:
            raise PermissionError("Skill unavailable to this task")
        if not set(entry.bindings) <= (policy.allowed_tools & self.available_tools):
            raise PermissionError("Required binding unavailable or unauthorized")
        return entry

    def catalog(self, policy: Policy) -> list[dict]:
        result = []
        for name in sorted(self.registry):
            try:
                entry = self.eligible(name, policy)
            except PermissionError:
                continue
            descriptor = self.repository.metadata(name)
            if descriptor_digest(descriptor) != entry.metadata_digest:
                raise PermissionError("Catalog metadata changed after registration")
            result.append({"name": name, "description": descriptor.description})
        return result

    def verified(
        self, name: str, policy: Policy
    ) -> tuple[RegistryEntry, dict[str, bytes]]:
        entry = self.eligible(name, policy)
        files = self.repository.snapshot(name)
        if snapshot_digest(files) != entry.digest:
            raise PermissionError("Bundle changed since trusted registration")
        descriptor, _ = parse_frontmatter(files["SKILL.md"].decode(), name)
        if descriptor.version != entry.version:
            raise PermissionError("Pinned version mismatch")
        return entry, files

    @staticmethod
    def fits(session: Session, content: str) -> None:
        used = sum(len(x.instructions) for x in session.active.values())
        used += sum(map(len, session.resources.values()))
        if used + len(content) > session.char_limit:
            raise ValueError("Skill context character budget exhausted")

    def activate(self, name: str, session: Session) -> Activated:
        entry, files = self.verified(name, session.policy)
        if name in session.active:
            return session.active[
                name
            ]  # No duplicate injection, but integrity was rechecked.
        _, body = parse_frontmatter(files["SKILL.md"].decode(), name)
        self.fits(session, body)
        loaded = Activated(name, entry.version, entry.digest, body)
        session.active[name] = loaded
        return loaded

    def resource(self, name: str, relative: str, session: Session) -> str:
        if name not in session.active:
            raise ValueError("Activate the skill first")
        path = PurePosixPath(relative)
        if (
            path.is_absolute()
            or ".." in path.parts
            or not path.parts
            or path.parts[0] not in {"references", "assets", "scripts"}
        ):
            raise PermissionError("Resource path outside bundle conventions")
        _, files = self.verified(name, session.policy)
        key = (name, path.as_posix())
        if key in session.resources:
            return session.resources[key]
        content = files[path.as_posix()].decode("utf-8")
        self.fits(session, content)
        session.resources[key] = (
            content  # Returning source never executes a bundled script.
        )
        return content

    async def invoke(
        self,
        name: str,
        tool: str,
        arguments: dict,
        session: Session,
        adapter: ToolAdapter,
    ) -> dict:
        if name not in session.active:
            raise ValueError("Activate the skill first")
        entry, _ = self.verified(name, session.policy)
        if tool not in entry.bindings:
            raise PermissionError("Tool is not a trusted binding for this skill")
        return await adapter(tool, arguments, session.policy)

    def context(self, session: Session) -> str:
        # Structured packaging aids provenance; it is not an authorization mechanism.
        return json.dumps(
            [
                {
                    "source": "approved-skill",
                    "name": x.name,
                    "version": x.version,
                    "digest": x.digest,
                    "instructions": x.instructions,
                }
                for x in session.active.values()
            ],
            ensure_ascii=False,
        )

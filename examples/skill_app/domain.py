from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Descriptor:
    name: str
    description: str
    version: str  # Custom metadata, not a required Agent Skills field.
    declared_tools: str = ""  # Experimental declaration; never grants authority here.


@dataclass(frozen=True)
class RegistryEntry:
    version: str
    digest: str
    bindings: tuple[str, ...]
    metadata_digest: str = ""


@dataclass(frozen=True)
class Policy:
    allowed_skills: frozenset[str]
    allowed_tools: frozenset[str]
    quote_ids: frozenset[str]


@dataclass(frozen=True)
class Activated:
    name: str
    version: str
    digest: str
    instructions: str


@dataclass
class Session:
    policy: Policy
    char_limit: int = 12000  # Demonstration character budget, NOT a token estimate.
    active: dict[str, Activated] = field(default_factory=dict)
    resources: dict[tuple[str, str], str] = field(default_factory=dict)


ToolAdapter = Callable[[str, dict, Policy], Awaitable[dict]]

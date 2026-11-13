"""Bounded reads of an explicitly supplied, trusted, read-only package root."""

import hashlib
import json
import re
from dataclasses import asdict
from pathlib import Path

from .domain import Descriptor


def parse_frontmatter(text: str, directory_name: str) -> tuple[Descriptor, str]:
    import yaml

    lines = text.splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        raise ValueError("Missing YAML frontmatter")
    end = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), None)
    if end is None:
        raise ValueError("Unclosed YAML frontmatter")
    metadata = yaml.safe_load("".join(lines[1:end]))
    if not isinstance(metadata, dict):
        raise TypeError("Frontmatter must be a mapping")
    name, description = metadata.get("name"), metadata.get("description")
    if (
        not isinstance(name, str)
        or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name)
        or len(name) > 64
        or name != directory_name
    ):
        raise ValueError("Invalid skill/directory name")
    if not isinstance(description, str) or not 1 <= len(description.strip()) <= 1024:
        raise ValueError("Invalid description")
    extra = metadata.get("metadata", {})
    if not isinstance(extra, dict) or any(
        not isinstance(k, str) or not isinstance(v, str) for k, v in extra.items()
    ):
        raise ValueError("metadata must map strings to strings")
    tools = metadata.get("allowed-tools", "")
    if not isinstance(tools, str):
        raise TypeError("allowed-tools must be a string")
    return Descriptor(name, description, extra.get("version", ""), tools), "".join(
        lines[end + 1 :]
    ).strip()


def descriptor_digest(descriptor: Descriptor) -> str:
    return hashlib.sha256(
        json.dumps(asdict(descriptor), sort_keys=True).encode()
    ).hexdigest()


def snapshot_digest(files: dict[str, bytes]) -> str:
    digest = hashlib.sha256()
    for path, content in sorted(files.items()):
        # Length prefixes avoid ambiguous concatenation of filenames and bytes.
        label = path.encode()
        digest.update(len(label).to_bytes(8, "big") + label)
        digest.update(len(content).to_bytes(8, "big") + content)
    return digest.hexdigest()


class SkillRepository:
    def __init__(self, root: Path):
        self.root = root.resolve(strict=True)
        self.reads: list[str] = []  # Observable demonstration of disclosure stages.

    def package(self, name: str) -> Path:
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name) or len(name) > 64:
            raise ValueError("Invalid skill name")
        path = self.root / name
        if path.is_symlink() or not path.resolve(strict=True).is_relative_to(self.root):
            raise PermissionError("Package escapes trusted root")
        return path

    def metadata(self, name: str) -> Descriptor:
        path = self.package(name) / "SKILL.md"
        if path.is_symlink():
            raise PermissionError("Symlinked entrypoint")
        self.reads.append(f"{name}:metadata")
        header = []
        # Read frontmatter without exposing the body or resources to the catalog.
        with path.open(encoding="utf-8") as source:
            for line in source:
                header.append(line)
                if sum(map(len, header)) > 16384:
                    raise ValueError("Oversized metadata")
                if len(header) > 1 and line.strip() == "---":
                    break
        descriptor, _ = parse_frontmatter("".join(header), name)
        return descriptor

    def snapshot(self, name: str) -> dict[str, bytes]:
        package = self.package(name)
        files, total = {}, 0
        for path in sorted(package.rglob("*")):
            if "__pycache__" in path.parts or path.suffix == ".pyc":
                continue  # Build artifacts are not part of this package manifest.
            if path.is_symlink():
                raise PermissionError("Symlinks are unsupported in this example")
            if not path.is_file():
                continue
            if path.stat().st_size > 65536:
                raise ValueError("Oversized resource")
            content = path.read_bytes()
            total += len(content)
            if total > 262144:
                raise ValueError("Oversized skill bundle")
            files[path.relative_to(package).as_posix()] = content
        self.reads.append(f"{name}:integrity-snapshot")
        return files


# Snapshot bytes are read for integrity; only requested content enters model context.
# Read-only trusted storage is assumed: this is not an OS sandbox or a TOCTOU defense.

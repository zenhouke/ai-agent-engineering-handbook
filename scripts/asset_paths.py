"""Derive diagram ownership from the same curriculum that owns navigation."""

from pathlib import Path

from curriculum import ROOT

DIAGRAMS = ROOT / "assets/diagrams"
VISUAL_MANIFEST = ROOT / "assets/manifest.json"
STAGES = {1: "foundations", 2: "intermediate", 3: "architecture", 4: "projects"}


def lesson_diagrams(item: dict, language: str) -> Path:
    """Group by stage, optional module, stable lesson ID, then language."""
    if language not in {"zh", "en"}:
        raise ValueError(f"Unsupported diagram language: {language}")
    path = DIAGRAMS / STAGES[item["group"]]
    if section := item.get("section"):
        path /= section
    return path / item["id"] / language


def prune_lesson_diagrams(expected: set[Path]) -> None:
    """Only generated stage directories are owned here; overview is authored."""
    for stage in STAGES.values():
        folder = DIAGRAMS / stage
        if not folder.exists():
            continue
        for path in (p for p in folder.rglob("*") if p.suffix in {".svg", ".png"}):
            if path not in expected:
                path.unlink()
        for path in sorted(folder.rglob("*"), reverse=True):
            if path.is_dir() and not any(path.iterdir()):
                path.rmdir()

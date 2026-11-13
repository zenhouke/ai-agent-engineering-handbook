"""The manifest order is the single source of all displayed course numbers."""

import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_curriculum() -> list[dict]:
    rows = json.loads((ROOT / "site/curriculum.json").read_text())
    counts, modules = defaultdict(int), {}
    for row in rows:
        group, section = row["group"], row.get("section")
        if section:
            key = (group, section)
            if key not in modules:
                modules[key] = sum(g == group for g, _ in modules) + 1
            counts[key] += 1
            number = f"{group}.{modules[key]}.{counts[key]}"
        elif group:
            counts[group] += 1
            number = f"{group}.{counts[group]}"
        else:
            number = ""
        row["number"] = number
        for field in ["title", "en_title"]:
            row["base_" + field] = row[field]
            row[field] = (number + " " if number else "") + row[field]
    return rows


def group_label(number: int, label: str) -> str:
    return f"{number} {label}" if number else label


def section_label(children: list[dict], label: str) -> str:
    return children[0]["number"].rsplit(".", 1)[0] + " " + label

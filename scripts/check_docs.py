"""Audit repository Markdown, embedded examples and paired authoring inputs.

Run after build_site.py. Partials are resolved in their destination article,
matching how the reading site includes notes and lesson appendices.
"""

from __future__ import annotations

import ast
import json
import os
import re
import shlex
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

import markdown
from curriculum import ROOT, load_curriculum

EXCLUDED = {
    ".git",
    "_site",
    ".venv",
    ".artifacts",
    ".ruff_cache",
    "node_modules",
    "__pycache__",
}
FENCES = re.compile(
    r"^```(?P<language>[\w+-]+)[^\n]*\n(?P<body>.*?)^```", re.MULTILINE | re.DOTALL
)


class References(HTMLParser):
    def __init__(self, source: str):
        super().__init__()
        self.links: list[str] = []
        self.ids: set[str] = set()
        self.feed(source)

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        fields = dict(attrs)
        if fields.get("id"):
            self.ids.add(fields["id"])
        for name in ("href", "src"):
            if fields.get(name):
                self.links.append(fields[name])


def parse(text: str) -> References:
    renderer = markdown.Markdown(extensions=["extra", "toc", "sane_lists"])
    return References(
        renderer.convert(text.replace("<details>", '<details markdown="1">'))
    )


def sources() -> list[Path]:
    result = []
    for folder, directories, files in os.walk(ROOT):
        directories[:] = [name for name in directories if name not in EXCLUDED]
        result += [Path(folder) / name for name in files if name.endswith(".md")]
    return sorted(result)


def contexts(manifest: list[dict]) -> dict[Path, Path]:
    result = {}
    for item in manifest:
        for language, field in [("zh", "source"), ("en", "en_source")]:
            target = ROOT / item[field]
            result[ROOT / f"docs/{language}/notes/{item['id']}.md"] = target
            result[ROOT / f"site/lessons/{language}/{item['id']}-details.md"] = target
    return result


def check_commands(text: str, source: Path) -> list[str]:
    errors = []
    for block in FENCES.finditer(text):
        language, body = block["language"], block["body"]
        if language in {"python", "json"}:
            try:
                if language == "python":
                    ast.parse(body)
                else:
                    json.loads(body)
            except (SyntaxError, json.JSONDecodeError) as error:
                errors.append(f"{source}: invalid {language} block: {error}")
        if language not in {"sh", "bash", "shell"}:
            continue
        for line in body.replace("\\\n", " ").splitlines():
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            try:
                args = shlex.split(line, comments=True)
            except ValueError as error:
                errors.append(f"{source}: malformed shell example: {error}")
                continue
            for index, token in enumerate(args[:-1]):
                if (
                    token == "-r"
                    and any(part in {"pip", "install"} for part in args)
                    and not (ROOT / args[index + 1]).is_file()
                ):
                    errors.append(
                        f"{source}: missing requirements file {args[index + 1]}"
                    )
            if not args or not re.fullmatch(
                r"python(?:3(?:\.\d+)?)?", Path(args[0]).name
            ):
                continue
            if "-m" in args:
                if args[-1] == "-m":
                    errors.append(f"{source}: missing Python module argument")
                    continue
                module = args[args.index("-m") + 1]
                if (
                    module.startswith(("examples.", "labs."))
                    and not (ROOT / (module.replace(".", "/") + ".py")).is_file()
                ):
                    errors.append(f"{source}: missing Python module {module}")
                if module == "unittest" and "-p" in args:
                    if args[-1] in {"-p", "-s"}:
                        errors.append(f"{source}: missing unittest discovery argument")
                        continue
                    pattern = args[args.index("-p") + 1]
                    directory = args[args.index("-s") + 1] if "-s" in args else "."
                    if not list((ROOT / directory).glob(pattern)):
                        errors.append(f"{source}: no tests match {pattern}")
            elif (
                len(args) > 1
                and args[1].endswith(".py")
                and not (ROOT / args[1]).is_file()
            ):
                errors.append(f"{source}: missing Python script {args[1]}")
    return errors


def check_lesson_text(data: dict, source: str) -> list[str]:
    """Keep code scope and image-only procedure content readable as text."""
    errors = []
    if not data.get("scope") or data["scope"] not in source:
        errors.append("Missing reference-code scope")
    for index, procedure in enumerate(data.get("procedures", []), start=1):
        values = procedure["steps"] + [
            procedure[field] for field in ("state", "failure", "measure", "case")
        ]
        if any(value not in source for value in values):
            errors.append(f"Missing text alternative for procedure {index}")
    return errors


def check() -> None:
    manifest = load_curriculum()
    aliases = contexts(manifest)
    paths = sources()
    parsed = {path: parse(path.read_text()) for path in paths}
    errors, external = [], set()
    chinese = {(ROOT / item["source"]).resolve() for item in manifest}
    for path, document in parsed.items():
        context = aliases.get(path, path)
        errors += check_commands(path.read_text(), path.relative_to(ROOT))
        for value in document.links:
            url = urlsplit(value)
            if url.scheme or url.netloc:
                if url.scheme in {"http", "https"}:
                    external.add(value)
                continue
            target = (
                (context.parent / unquote(url.path)).resolve() if url.path else context
            )
            if not target.is_relative_to(ROOT):
                errors.append(
                    f"{path.relative_to(ROOT)}: link escapes repository: {value}"
                )
                continue
            if not target.exists():
                errors.append(f"{path.relative_to(ROOT)}: missing local target {value}")
            elif (
                url.fragment
                and target.suffix == ".md"
                and target in parsed
                and unquote(url.fragment) not in parsed[target].ids
            ):
                errors.append(f"{path.relative_to(ROOT)}: missing anchor {value}")
            if context.is_relative_to(ROOT / "docs/en") and target in chinese:
                errors.append(
                    f"{path.relative_to(ROOT)}: English lesson links to Chinese page: {value}"
                )
    records = {"zh": {}, "en": {}}
    for language, items in records.items():
        for path in (ROOT / f"site/lessons/{language}").glob("*.json"):
            data = json.loads(path.read_text())
            items[data["id"]] = data
    if records["zh"].keys() != records["en"].keys():
        errors.append("Authored lesson locale sets differ")
    for key in records["zh"].keys() & records["en"].keys():
        left, right = records["zh"][key], records["en"][key]
        for field in ("example", "extra_examples", "extra_snippets"):
            a = left.get(field, [])
            b = right.get(field, [])
            if field != "example":
                a = [item.get("example", item.get("file")) for item in a]
                b = [item.get("example", item.get("file")) for item in b]
            if a != b:
                errors.append(
                    f"{key}: reference implementation differs across locales: {field}"
                )
    by_id = {item["id"]: item for item in manifest}
    for language, items in records.items():
        for key, data in items.items():
            source = ROOT / by_id[key]["source" if language == "zh" else "en_source"]
            errors += [
                f"{key} {language}: {error}"
                for error in check_lesson_text(data, source.read_text())
            ]
    if errors:
        raise SystemExit("\n".join(errors))
    print(
        f"Checked {len(paths)} Markdown sources, Python/JSON/shell examples, {len(records['zh'])} paired lesson inputs and {len(external)} distinct external references (no network check)"
    )


if __name__ == "__main__":
    check()

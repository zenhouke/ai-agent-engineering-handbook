"""Check the actual generated documents, their local links and course coverage."""

from __future__ import annotations

import ast
import json
import struct
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

from asset_paths import DIAGRAMS, VISUAL_MANIFEST, lesson_diagrams
from curriculum import load_curriculum

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "_site"


class Document(HTMLParser):
    def __init__(self, path: Path):
        super().__init__()
        self.links: list[tuple[str, str]] = []
        self.ids: set[str] = set()
        self.duplicates: set[str] = set()
        self.headings = 0
        self.heading_text: list[str] = []
        self.in_heading = False
        self.image_count = 0
        self.errors: list[str] = []
        self.details_context: list[tuple[str | None, str | None]] = []
        self.navigation: dict[str, tuple[str | None, str | None]] = {}
        self.feed(path.read_text())

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        data = dict(attrs)
        if tag == "details":
            group, section = (
                self.details_context[-1] if self.details_context else (None, None)
            )
            self.details_context.append(
                (data.get("data-group", group), data.get("data-section", section))
            )
        if "data-lesson" in data:
            self.navigation[data["data-lesson"]] = (
                self.details_context[-1] if self.details_context else (None, None)
            )
        if identifier := data.get("id"):
            if identifier in self.ids:
                self.duplicates.add(identifier)
            self.ids.add(identifier)
        if tag == "h1":
            self.headings += 1
            self.in_heading = True
        if tag == "img":
            self.image_count += 1
            if not data.get("alt"):
                self.errors.append("Image has no alt text")
        for attr in ("href", "src"):
            if data.get(attr):
                self.links.append((tag, data[attr]))

    def handle_endtag(self, tag: str) -> None:
        if tag == "h1":
            self.in_heading = False
        if tag == "details" and self.details_context:
            self.details_context.pop()

    def handle_data(self, data: str) -> None:
        if self.in_heading:
            self.heading_text.append(data)


def check() -> None:
    manifest = load_curriculum()
    files = list(OUT.rglob("*.html"))
    if not files:
        raise SystemExit("Build the site before checking")
    documents = {path.resolve(): Document(path) for path in files}
    errors = []
    for path, document in documents.items():
        errors.extend(f"{path.name}: {error}" for error in document.errors)
        if document.duplicates:
            errors.append(f"{path}: duplicate IDs {document.duplicates}")
        if document.navigation:
            if list(document.navigation) != [item["id"] for item in manifest]:
                errors.append(
                    f"{path.name}: navigation order differs from numbered manifest"
                )
            for item in manifest:
                expected = (str(item["group"]), item.get("section"))
                if document.navigation.get(item["id"]) != expected:
                    errors.append(
                        f"{path.name}: wrong navigation parent for {item['id']}"
                    )
        for tag, value in document.links:
            parsed = urlsplit(value)
            if parsed.scheme or parsed.netloc:
                continue
            target = (
                (path.parent / unquote(parsed.path)).resolve() if parsed.path else path
            )
            if not target.is_relative_to(OUT):
                errors.append(f"{path}: link escapes generated site: {value}")
                continue
            if not target.is_file():
                errors.append(f"{path}: missing {value}")
            if (
                parsed.fragment
                and target in documents
                and unquote(parsed.fragment) not in documents[target].ids
            ):
                errors.append(f"{path}: missing anchor {value}")
    core = [item for item in manifest if item.get("kind") == "core"]
    numbers = [
        tuple(map(int, item["number"].split(".")))
        for item in manifest
        if item["number"]
    ]
    if numbers != sorted(numbers) or len(numbers) != len(set(numbers)):
        errors.append("Course numbering is duplicated or out of navigation order")
    for item in manifest:
        for language in ("zh", "en"):
            path = (OUT / language / f"{item['id']}.html").resolve()
            if path not in documents:
                errors.append(f"Missing language pair: {path}")
                continue
            if documents[path].headings != 1:
                errors.append(f"{path}: must contain exactly one H1")
            expected_title = item["title" if language == "zh" else "en_title"]
            if "".join(documents[path].heading_text) != expected_title:
                errors.append(
                    f"{path.name}: displayed heading differs from numbered manifest"
                )
        if item in core:
            source = (ROOT / item["source"]).read_text()
            if "<details>" not in source or source.count("![") < 3:
                errors.append(
                    f"{item['source']}: missing worked lesson, figure or answer"
                )
            rendered = (OUT / "zh" / f"{item['id']}.html").read_text()
            if "```" in rendered or "```mermaid" in source:
                errors.append(f"{item['source']}: raw unrendered block")
    visual_index = json.loads(VISUAL_MANIFEST.read_text())
    protocols = [item for item in manifest if item.get("kind") == "protocol"]
    topics = [
        item
        for item in manifest
        if item.get("kind") in {"skill", "function", "architecture", "project"}
    ]
    for item in core + protocols + topics:
        for language in ("zh", "en"):
            entries = [
                entry
                for entry in visual_index
                if entry["lesson"] == item["id"] and entry["language"] == language
            ]
            if len(entries) != 1:
                errors.append(
                    f"Missing unique visual/code mapping: {item['id']} {language}"
                )
                continue
            entry = entries[0]
            code_path = ROOT / entry["example"]
            ast.parse(code_path.read_text(), filename=str(code_path))
            source = (
                ROOT / item["source" if language == "zh" else "en_source"]
            ).read_text()
            if code_path.read_text().strip() not in source:
                errors.append(
                    f"Lesson code differs from reference file: {item['id']} {language}"
                )
            data = json.loads(
                (ROOT / f"site/lessons/{language}/{item['id']}.json").read_text()
            )
            if item in core + topics:
                procedures = data.get("procedures", [])
                if len(procedures) != 3 or any(
                    len(part.get("steps", [])) != 4
                    or not all(
                        part.get(field)
                        for field in ("state", "failure", "measure", "case")
                    )
                    for part in procedures
                ):
                    errors.append(
                        f"Missing implementation trace: {item['id']} {language}"
                    )
            references = [
                f"examples/{part['example']}.py"
                for part in data.get("extra_examples", [])
            ] + [part["file"] for part in data.get("extra_snippets", [])]
            for reference in references:
                if (ROOT / reference).read_text().strip() not in source:
                    errors.append(
                        f"Unsynchronized code appendix: {reference} {language}"
                    )
            rendered = (OUT / language / f"{item['id']}.html").read_text()
            required_header = "方案" if language == "zh" else "Approach"
            if f"<th>{required_header}</th>" not in rendered:
                errors.append(
                    f"Approach comparison did not render as a table: {item['id']} {language}"
                )
            if len(data["solutions"]) != 3 or any(
                len(row) != 4 or not all(row) for row in data["solutions"]
            ):
                errors.append(
                    f"Missing approach/mechanism/condition/tradeoff: {item['id']} {language}"
                )
            for asset in entry["images"]:
                if asset not in source or not (ROOT / asset).is_file():
                    errors.append(f"Missing lesson figure: {asset}")
                if asset.startswith("assets/diagrams/") and (
                    ROOT / asset
                ).parent != lesson_diagrams(item, language):
                    errors.append(f"Figure outside its curriculum folder: {asset}")
            media = data.get("media", []) + (
                [data["intro_image"]] if data.get("intro_image") else []
            )
            for image in media:
                if not image.get("alt") or not image.get("caption"):
                    errors.append(f"Missing image context: {item['id']} {language}")
                if image["file"] not in source or not (ROOT / image["file"]).is_file():
                    errors.append(
                        f"Missing photographic/illustrative media: {image['file']}"
                    )
            if item["group"] >= 3 and any(
                asset.endswith(".svg") for asset in entry["images"]
            ):
                errors.append(
                    f"Architecture lesson must publish PNG figures: {item['id']} {language}"
                )
    diagrams = [path for path in DIAGRAMS.rglob("*") if path.suffix in {".svg", ".png"}]
    declared = {
        ROOT / asset
        for entry in visual_index
        for asset in entry["images"]
        if asset.startswith("assets/diagrams/")
    }
    declared.add(DIAGRAMS / "overview/learning-map.svg")
    for path in set(diagrams) - declared:
        errors.append(f"Unowned diagram asset: {path.relative_to(ROOT)}")
    if list(ROOT.glob("*.svg")):
        errors.append("SVG files must not be scattered in the repository root")
    image_extensions = {".svg", ".png", ".jpg", ".jpeg", ".webp"}
    published = {
        p.relative_to(OUT)
        for p in (OUT / "assets").rglob("*")
        if p.suffix in image_extensions
    }
    originals = {
        p.relative_to(ROOT)
        for p in (ROOT / "assets").rglob("*")
        if p.suffix in image_extensions
    }
    if published != originals or list(OUT.glob("*.svg")):
        errors.append("Published image inventory differs from current source assets")
    referenced = set()
    for page, document in documents.items():
        for tag, value in document.links:
            parsed = urlsplit(value)
            if tag == "img" and not parsed.scheme and not parsed.netloc:
                target = (page.parent / unquote(parsed.path)).resolve()
                if target.is_relative_to(OUT):
                    referenced.add(target.relative_to(OUT))
    # The historical reference index is read directly in the repository.
    referenced.add(Path("assets/diagrams/overview/learning-map.svg"))
    for path in originals - referenced:
        errors.append(f"Unreferenced image: {path}")
    for path in diagrams:
        if path.suffix == ".svg":
            ET.parse(path)
        else:
            header = path.read_bytes()[:24]
            if header[:8] != b"\x89PNG\r\n\x1a\n" or struct.unpack(
                ">II", header[16:24]
            )[0] != (3600 if path.name == "system-architecture.png" else 2400):
                errors.append(
                    f"Architecture figure has an invalid PNG export size: {path}"
                )
    registry = json.loads((ROOT / "assets/media.json").read_text())
    for media in registry["assets"]:
        if not (ROOT / media["file"]).is_file() or not media.get("producer"):
            errors.append(f"Missing media or provenance: {media['file']}")
    if errors:
        raise SystemExit("\n".join(errors))
    print(
        f"Checked {len(manifest)} paired pages, {len(core)} core + {len(protocols)} MCP + {len(topics)} architecture/topic lessons, numbered navigation/headings, local links/anchors and {len(originals)} image assets (training not executed)"
    )


if __name__ == "__main__":
    check()

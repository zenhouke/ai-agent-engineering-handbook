"""Small diagram primitives with deterministic wrapping and accessible labels."""

import unicodedata
from html import escape
from pathlib import Path

INK, BLUE, MIST, PAPER = "#0B1F3A", "#1F4E9C", "#A6B7CC", "#F4F6FA"


def wrap(text: str, width: int) -> list[str]:
    lines, current, units = [], "", 0
    for char in text:
        cost = 2 if unicodedata.east_asian_width(char) in ("W", "F") else 1
        if char == "\n" or units + cost > width:
            lines.append(current)
            current, units = "", 0
            if char == "\n":
                continue
        current += char
        units += cost
    if current:
        lines.append(current)
    return lines or [""]


class Canvas:
    def __init__(
        self, title: str, description: str, height: int = 520, width: int = 1200
    ):
        self.height = height
        self.parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" role="img" aria-labelledby="title desc"><title id="title">{escape(title)}</title><desc id="desc">{escape(description)}</desc><defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0L10 5L0 10" fill="{BLUE}"/></marker></defs><rect width="{width}" height="{height}" rx="12" fill="{PAPER}"/><g font-family="Noto Sans CJK SC,Microsoft YaHei,system-ui,sans-serif" fill="{INK}">'
        ]
        self.text(32, 44, title, size=27, width=82)

    def text(self, x, y, text, size=22, width=38, fill=INK):
        for index, line in enumerate(wrap(str(text), width)):
            self.parts.append(
                f'<text x="{x}" y="{y + index * (size + 8)}" font-size="{size}" fill="{fill}">{escape(line)}</text>'
            )

    def rect(self, x, y, w, h, fill="white", stroke=MIST, radius=8):
        self.parts.append(
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" fill="{fill}" stroke="{stroke}"/>'
        )

    def box(self, x, y, w, h, label, note="", color="white"):
        self.rect(x, y, w, h, color)
        self.text(x + 16, y + 34, label, width=max(10, int((w - 32) / 12)))
        if note:
            self.text(
                x + 16, y + h - 22, note, size=17, width=max(10, int((w - 32) / 9))
            )

    def path(self, points, dashed=False, arrow=True):
        self.parts.append(
            f'<path d="{points}" fill="none" stroke="{BLUE}" stroke-width="2.5"'
            + (' stroke-dasharray="7 6"' if dashed else "")
            + (' marker-end="url(#arrow)"' if arrow else "")
            + "/>"
        )

    def line(self, x1, y1, x2, y2, **kwargs):
        self.path(f"M{x1} {y1}L{x2} {y2}", **kwargs)

    def circle(self, x, y, r=22):
        self.parts.append(
            f'<circle cx="{x}" cy="{y}" r="{r}" fill="white" stroke="{BLUE}" stroke-width="2.5"/>'
        )

    def save(self, path: Path):
        path.parent.mkdir(parents=True, exist_ok=True)
        content = "".join(self.parts) + "</g></svg>"
        if path.suffix == ".png":
            from .raster import save_png

            save_png(content, path)
            return
        if not path.exists() or path.read_text() != content:
            path.write_text(content)

    def chain(self, labels, y=170):
        for i, label in enumerate(labels):
            x = 32 + i * 295
            self.box(x, y, 250, 100, label)
            if i < len(labels) - 1:
                self.line(x + 254, y + 50, x + 289, y + 50)

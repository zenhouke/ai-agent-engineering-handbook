"""Build a self-contained reading site from the paired lesson manifest."""

from __future__ import annotations

import html
import json
import re
import shutil
from pathlib import Path
from urllib.parse import unquote, urlsplit

import markdown
from curriculum import group_label, load_curriculum, section_label
from curriculum_docs import render as render_curriculum_docs
from site_navigation import render_navigation
from visual_lessons import render_lessons

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "_site"


def load_manifest() -> list[dict]:
    return load_curriculum()


def rewrite_links(
    rendered: str, source: Path, language: str, manifest: list[dict]
) -> str:
    pages = {(ROOT / item["source"]).resolve(): item["id"] for item in manifest}
    pages.update(
        {(ROOT / item["en_source"]).resolve(): item["id"] for item in manifest}
    )
    redirects = json.loads((ROOT / "site/redirects.json").read_text())
    for alias in redirects.values():
        pages[(ROOT / alias["source"]).resolve()] = alias["target"]
        pages[(ROOT / alias["en_source"]).resolve()] = alias["target"]
    pages.update(
        {
            ROOT / "README.md": "index",
            ROOT / "READING-GUIDE.md": "index",
            ROOT / "SOURCES.md": "resources",
            ROOT / "HANDBOOK.md": "a01",
        }
    )

    def replace(match: re.Match) -> str:
        attr, raw = match.groups()
        value = html.unescape(raw)
        url = urlsplit(value)
        if url.scheme or url.netloc or value.startswith("#"):
            return match.group(0)
        target = (source.parent / unquote(url.path)).resolve()
        if target == ROOT / "site/demos/attention.html":
            destination = f"../demos/attention-{language}.html"
        elif target in pages:
            destination = f"{pages[target]}.html"
            if target.name == "HANDBOOK.md" and url.fragment.startswith("chapter-"):
                number = int(url.fragment.removeprefix("chapter-"))
                destination = (
                    "index.html"
                    if number == 0
                    else ("skill05.html" if number == 10 else f"a{number:02}.html")
                )
            elif url.fragment:
                destination += "#" + url.fragment
        else:
            try:
                relative = target.relative_to(ROOT)
            except ValueError as error:
                raise ValueError(f"Link escapes project: {source}: {value}") from error
            destination = "../" + relative.as_posix()
        return f'{attr}="{html.escape(destination, quote=True)}"'

    return re.sub(r'(href|src)="([^"]+)"', replace, rendered)


def render_page(item: dict, language: str, manifest: list[dict], ui: dict) -> str:
    english = language == "en"
    source = ROOT / item["en_source" if english else "source"]
    md = markdown.Markdown(
        extensions=["extra", "toc", "sane_lists"], output_format="html"
    )
    authored = source.read_text().replace("<details>", '<details markdown="1">')
    article = rewrite_links(md.convert(authored), source, language, manifest)

    def link_diagram(match: re.Match) -> str:
        image = match.group(0)
        target = re.search(r'src="([^"]+)"', image).group(1)
        label = html.escape(ui["open_diagram"], quote=True)
        return f'<a class="diagram-link" href="{target}" target="_blank" rel="noopener" aria-label="{label}" title="{label}">{image}</a>'

    article = re.sub(r'<img\b[^>]*\bsrc="[^"]+"[^>]*>', link_diagram, article)
    article = re.sub(
        r"(<table>.*?</table>)",
        r'<div class="table-scroll">\1</div>',
        article,
        flags=re.DOTALL,
    )
    title = item["en_title" if english else "title"]
    navigation = render_navigation(item, manifest, ui, english, md.toc_tokens)
    position = manifest.index(item)
    pager = []
    for offset, label in [(-1, "previous"), (1, "next")]:
        index = position + offset
        if 0 <= index < len(manifest):
            page = manifest[index]
            pager.append(
                f'<a href="{page["id"]}.html"><small>{ui[label]}</small>{html.escape(page["en_title" if english else "title"])}</a>'
            )
    breadcrumb = group_label(item["group"], ui["groups"][item["group"]])
    if item.get("section"):
        children = [
            p
            for p in manifest
            if p["group"] == item["group"] and p.get("section") == item["section"]
        ]
        breadcrumb += " / " + section_label(children, ui["sections"][item["section"]])
    other = "zh" if english else "en"
    return f'''<!doctype html>
<html lang="{"en" if english else "zh-CN"}"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)} | {ui["title"]}</title>
<meta name="description" content="{html.escape(ui["subtitle"])}">
<link rel="stylesheet" href="../styles/main.css"><script defer src="../app.js"></script></head>
<body><a class="skip" href="#content">{ui["skip"]}</a>
<header class="topbar"><a class="brand" href="index.html"><span class="brand-mark" aria-hidden="true">∑</span>{ui["brand"]}</a>
<span class="subtitle">{ui["subtitle"]}</span><button class="menu-button" aria-expanded="false" aria-controls="navigation">{ui["menu"]}</button>
<a class="language" href="../{other}/{item["id"]}.html" lang="{other}" hreflang="{other}">{ui["language"]}</a></header>
<nav class="sidebar" id="navigation" aria-label="{ui["nav"]}"><label for="lesson-search">{ui["search"]}</label>
<input id="lesson-search" type="search" autocomplete="off">{navigation}
<p id="empty-search" role="status" hidden>{ui["empty"]}</p><p class="nav-progress" data-progress="{ui["progress"]}"></p></nav>
<main id="content" tabindex="-1"><div class="breadcrumb">{html.escape(breadcrumb)}</div><article>{article}</article>
<footer class="lesson-footer"><button data-complete="{item["id"]}" data-pending="{ui["complete"]}" data-done="{ui["completed"]}" aria-pressed="false">{ui["complete"]}</button>
<nav class="pager" aria-label="{ui["nav"]}">{"".join(pager)}</nav><p class="site-note">{ui["notes"]}</p></footer></main></body></html>'''


def build() -> None:
    manifest = load_manifest()
    render_curriculum_docs(manifest)
    render_lessons()
    OUT.mkdir(exist_ok=True)
    for language in ("zh", "en"):
        ui = json.loads((ROOT / f"site/i18n/{language}.json").read_text())
        target = OUT / language
        target.mkdir(exist_ok=True)
        for item in manifest:
            result = render_page(item, language, manifest, ui)
            temporary = target / f"{item['id']}.html.tmp"
            temporary.write_text(result)
            temporary.replace(target / f"{item['id']}.html")
        for alias, redirect in json.loads(
            (ROOT / "site/redirects.json").read_text()
        ).items():
            destination = redirect["target"] + ".html"
            (target / f"{alias}.html").write_text(
                f'<!doctype html><html lang="{language}"><meta charset="utf-8"><meta http-equiv="refresh" content="0;url={destination}"><title>{ui["brand"]}</title><a href="{destination}">{ui["next"]}</a></html>'
            )
    for directory in ("styles",):
        shutil.copytree(ROOT / "site" / directory, OUT / directory, dirs_exist_ok=True)
    shutil.copy2(ROOT / "site/app.js", OUT / "app.js")
    shutil.copytree(ROOT / "assets", OUT / "assets", dirs_exist_ok=True)
    for image in ROOT.glob("*.svg"):
        shutil.copy2(image, OUT / image.name)
    template = (ROOT / "site/demos/attention.html").read_text()
    (OUT / "demos").mkdir(exist_ok=True)
    for language in ("zh", "en"):
        values = json.loads((ROOT / f"site/i18n/demo-{language}.json").read_text())
        demo = template
        for key, value in values.items():
            demo = demo.replace("{{" + key + "}}", html.escape(value, quote=True))
        (OUT / "demos" / f"attention-{language}.html").write_text(demo)
    (OUT / "index.html").write_text(
        '<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta http-equiv="refresh" content="0;url=zh/index.html"><title>AI 学习手册</title><a href="zh/index.html">开始学习</a></html>'
    )
    print(f"Built {len(manifest) * 2} lesson pages in _site")


if __name__ == "__main__":
    build()

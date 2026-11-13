"""Render category → architecture module → lesson → section navigation."""

import html

from curriculum import group_label, section_label


def lesson_link(
    page: dict, current: dict, ui: dict, english: bool, tokens: list
) -> str:
    active = page["id"] == current["id"]
    title = page["en_title" if english else "title"]
    toc = []
    if active:
        for token in tokens:
            for section in token.get("children", []):
                toc.append(
                    f'<li><a href="#{section["id"]}">{html.escape(section["name"])}</a></li>'
                )
                children = "".join(
                    f'<li><a href="#{part["id"]}">{html.escape(part["name"])}</a></li>'
                    for part in section.get("children", [])
                )
                if children:
                    toc.append(f"<li><ul>{children}</ul></li>")
    nested = (
        f'<ul class="toc" aria-label="{ui["toc"]}">{"".join(toc)}</ul>' if toc else ""
    )
    selected = ' aria-current="page"' if active else ""
    return f'<li data-lesson="{page["id"]}" data-title="{html.escape(title, quote=True)}"><a href="{page["id"]}.html"{selected}>{html.escape(title)}</a>{nested}</li>'


def render_navigation(
    current: dict, manifest: list, ui: dict, english: bool, tokens: list
) -> str:
    groups = []
    for number, title in enumerate(ui["groups"]):
        title = group_label(number, title)
        pages = [p for p in manifest if p["group"] == number]
        parts = [
            lesson_link(p, current, ui, english, tokens)
            for p in pages
            if not p.get("section")
        ]
        for key, label in ui.get("sections", {}).items():
            children = [p for p in pages if p.get("section") == key]
            if not children:
                continue
            label = section_label(children, label)
            opened = " open" if current.get("section") == key else ""
            links = "".join(
                lesson_link(p, current, ui, english, tokens) for p in children
            )
            parts.append(
                f'<li><details data-section="{key}"{opened}><summary>{html.escape(label)}</summary><ul>{links}</ul></details></li>'
            )
        opened = " open" if current["group"] == number or number == 0 else ""
        groups.append(
            f'<details data-group="{number}"{opened}><summary>{html.escape(title)}</summary><ul>{"".join(parts)}</ul></details>'
        )
    return "".join(groups)

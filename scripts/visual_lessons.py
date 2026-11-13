"""Render authored visual lessons and localized mechanism/decision diagrams."""

from __future__ import annotations

import json
from pathlib import Path

from agent_scenes import draw as draw_agent
from architecture_scenes import architecture
from curriculum import load_curriculum
from deep_scenes import scenes
from foundation_scenes import draw as draw_foundation
from governance_scenes import draw as draw_governance
from mcp_scenes import draw as draw_mcp
from multi_agent_scenes import draw as draw_multi
from skill_scenes import draw as draw_skills
from solution_scenes import draw_procedure
from studio_scenes import draw as draw_studio
from studio_scenes import scenes as studio_scenes
from svg_canvas import Canvas

ROOT = Path(__file__).resolve().parents[1]


def write_changed(path: Path, text: str) -> None:
    if not path.exists() or path.read_text() != text:
        path.write_text(text)


def render_diagrams(data: dict, ui: dict, language: str) -> list[Path]:
    target = ROOT / "assets/lessons" / language
    target.mkdir(parents=True, exist_ok=True)
    key = data["id"]
    paths = [
        target / f"{key}-{kind}.svg" for kind in ("problem", "mechanism", "selection")
    ]
    c = Canvas(ui["problem_figure"], data["problem"], 490)
    for row, (labels, heading) in enumerate(
        [(data["before"], ui["before"]), (data["after"], ui["after"])]
    ):
        y = 140 + row * 180
        c.text(30, y + 42, heading, size=20, width=12)
        for i, label in enumerate(labels):
            x = 190 + i * 330
            c.box(x, y, 285, 95, label)
            if i < 2:
                c.line(x + 290, y + 47, x + 324, y + 47)
    c.save(paths[0])
    c = Canvas(data["diagram_title"], data["principle"], 520)
    if not (
        draw_foundation(key, c, data, ui)
        or draw_agent(key, c, data, ui)
        or draw_mcp(key, c, data, ui)
        or draw_skills(key, c, data, ui)
        or draw_governance(key, c, data, ui)
        or draw_multi(key, c, data, ui)
        or draw_studio(key, c, data, ui)
    ):
        raise ValueError(f"No mechanism scene: {key}")
    c.save(paths[1])
    c = Canvas(ui["selection_figure"], data["principle"], 570)
    c.box(30, 220, 280, 100, ui["diagnose"])
    for i, row in enumerate(data["solutions"]):
        y = 95 + i * 150
        c.box(440, y, 690, 115, row[0], row[2])
        c.path(f"M315 270H370V{y + 57}H435")
    c.text(30, 525, ui["selection_note"], size=19, width=110)
    c.save(paths[2])
    if key == "f07":
        extra = target / f"{key}-architecture.svg"
        architecture(key, ui, data["principle"]).save(extra)
        paths.append(extra)
    for index, procedure in enumerate(data.get("procedures", [])):
        extra = target / f"{key}-solution-{index + 1}.svg"
        draw_procedure(data["solutions"][index][0], procedure, ui).save(extra)
        paths.append(extra)
    for slug, canvas in scenes(key, language):
        extra = target / f"{key}-{slug}.svg"
        canvas.save(extra)
        paths.append(extra)
    if key == "studio":
        for slug, canvas in studio_scenes(language):
            extra = target / f"studio-{slug}.svg"
            canvas.save(extra)
            paths.append(extra)
    return paths


def render_lessons() -> None:
    manifest = load_curriculum()
    visual_index = []
    for language in ("zh", "en"):
        ui = json.loads((ROOT / f"site/i18n/visual-{language}.json").read_text())
        for record in sorted((ROOT / f"site/lessons/{language}").glob("*.json")):
            data = json.loads(record.read_text())
            key = data["id"]
            item = next(item for item in manifest if item["id"] == key)
            destination = ROOT / item["source" if language == "zh" else "en_source"]
            title = item["title" if language == "zh" else "en_title"]
            images = render_diagrams(data, ui, language)
            visual_index.append(
                {
                    "lesson": key,
                    "language": language,
                    "images": [p.relative_to(ROOT).as_posix() for p in images],
                    "example": f"examples/{data['example']}.py",
                }
            )
            prefix = "../../../" if language == "zh" else "../../"
            lines = [
                f"# {title}",
                f"> {ui['mode']}",
                f"## {ui['problem']}",
                data["problem"],
                f"![{ui['problem_figure']}]({prefix}{images[0].relative_to(ROOT)})",
                f"## {ui['mechanism']}",
                data["principle"],
                f"![{ui['mechanism_figure']}]({prefix}{images[1].relative_to(ROOT)})",
                f"## {ui['solutions']}",
                f"![{ui['selection_figure']}]({prefix}{images[2].relative_to(ROOT)})",
            ]
            if data.get("scope"):
                lines.insert(2, data["scope"])
            table = ["| " + " | ".join(ui["table"]) + " |", "|---|---|---|---|"]
            table += ["| " + " | ".join(row) + " |" for row in data["solutions"]]
            lines.append("\n".join(table))
            if data.get("procedures"):
                lines += [f"## {ui['inside_solutions']}"]
                for index, procedure in enumerate(data["procedures"]):
                    name = data["solutions"][index][0]
                    image = f"assets/lessons/{language}/{key}-solution-{index + 1}.svg"
                    lines += [
                        f"### {index + 1} · {name}",
                        f"![{name}]({prefix}{image})",
                        f"**{ui['walkthrough']}** {procedure['case']}",
                    ]
            if key == "f07":
                lines += [
                    f"## {ui['architecture']}",
                    f"![{ui['architecture_figure']}]({prefix}{images[3].relative_to(ROOT)})",
                ]
            for slug, _ in scenes(key, language):
                image = f"assets/lessons/{language}/{key}-{slug}.svg"
                lines += [
                    f"## {ui['failure_trace']}",
                    f"![{ui['failure_trace']}]({prefix}{image})",
                ]
            code = (ROOT / f"examples/{data['example']}.py").read_text()
            lines += [
                f"## {ui['code']}",
                ui["code_note"],
                f"[{ui['code_guide']}]({prefix}docs/zh/projects/03-code-guide.md)",
                f"<details><summary>{ui['expand_code']}</summary>",
                "```python\n" + code.rstrip() + "\n```",
                "</details>",
            ]
            if key == "f07":
                lines += [f"[{ui['interactive']}]({prefix}site/demos/attention.html)"]
            appendix = ROOT / f"site/lessons/{language}/{key}-details.md"
            if appendix.exists():
                lines += [appendix.read_text()]
            for reference in data.get("extra_examples", []):
                extra_code = (ROOT / f"examples/{reference['example']}.py").read_text()
                lines += [
                    f"### {reference['title']}",
                    reference["scope"],
                    f"<details><summary>{ui['expand_code']}</summary>",
                    "```python\n" + extra_code.rstrip() + "\n```",
                    "</details>",
                ]
            for reference in data.get("extra_snippets", []):
                snippet = (ROOT / reference["file"]).read_text()
                lines += [
                    f"### {reference['title']}",
                    f"<details><summary>{ui['expand_code']}</summary>",
                    f"```{reference['language']}\n" + snippet.rstrip() + "\n```",
                    "</details>",
                ]
            lines += [
                f"## {ui['check']}",
                data["check"],
                f"<details><summary>{ui['answer']}</summary>",
                data["answer"],
                "</details>",
            ]
            notes = ROOT / f"docs/{language}/notes/{key}.md"
            if notes.exists():
                lines += [
                    f"<details><summary>{ui['more']}</summary>",
                    notes.read_text(),
                    "</details>",
                ]
            lines += [f"[{ui['sources']}]({prefix}docs/zh/resources.md)"]
            write_changed(destination, "\n\n".join(lines) + "\n")
    write_changed(
        ROOT / "assets/visual-manifest.json",
        json.dumps(visual_index, ensure_ascii=False, indent=2) + "\n",
    )
    print(
        f"Rendered {len(visual_index)} visual lesson pages and "
        f"{sum(len(entry['images']) for entry in visual_index)} SVGs; no training executed"
    )


if __name__ == "__main__":
    render_lessons()

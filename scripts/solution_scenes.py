"""Draw authored implementation steps, persisted state and failure boundaries."""

from svg_canvas import Canvas, wrap


def draw_procedure(name: str, procedure: dict, ui: dict) -> Canvas:
    step_height = max(
        112, 44 + max(len(wrap(step, 22)) for step in procedure["steps"]) * 28
    )
    y = 110 + step_height + 36
    rows = []
    for field in ("state", "failure", "measure"):
        height = max(90, 38 + len(wrap(procedure[field], 80)) * 29)
        rows.append((field, y, height))
        y += height + 12
    c = Canvas(name, procedure["case"], y + 20)
    for i, step in enumerate(procedure["steps"]):
        x = 32 + i * 293
        c.rect(x, 110, 258, step_height)
        c.text(x + 15, 139, f"{i + 1}", size=18)
        c.text(x + 15, 172, step, size=20, width=22)
        if i < 3:
            c.line(x + 262, 110 + step_height / 2, x + 286, 110 + step_height / 2)
    for field, top, height in rows:
        c.rect(32, top, 1136, height)
        c.text(48, top + 32, ui[field], size=20, width=14)
        c.text(236, top + 32, procedure[field], size=21, width=80)
    return c

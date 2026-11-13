"""Extra full-block and full-system diagrams for the two architecture milestones."""

from .svg_canvas import Canvas


def architecture(key: str, ui: dict, principle: str) -> Canvas:
    c = Canvas(ui["architecture_figure"], principle, 680)
    if key == "f07":
        labels = [
            "Token + position embeddings",
            "LayerNorm → causal MHA",
            "Residual: X + attention",
            "LayerNorm → FFN",
            "Residual: X + FFN",
            "Final norm → vocabulary logits",
        ]
        for index, label in enumerate(labels):
            y = 90 + index * 88
            c.box(330, y, 640, 66, label)
            if index < 5:
                c.line(650, y + 69, 650, y + 84)
        c.path("M325 120H200V298H325", dashed=True)
        c.path("M325 298H245V474H325", dashed=True)
        c.text(
            35,
            650,
            "X[B,T,D] → blocks → logits[B,T,V]; future positions masked",
            size=21,
            width=112,
        )
    else:
        c.box(35, 110, 290, 90, "User / API", "identity + request")
        c.box(455, 110, 290, 90, "Business service", "authorize + transition")
        c.box(875, 110, 290, 90, "Task / operation DB", "version + outbox")
        c.line(330, 155, 450, 155)
        c.line(750, 155, 870, 155)
        c.box(455, 300, 290, 90, "Runtime / workers", "budget + recovery")
        c.line(600, 205, 600, 295)
        c.path("M1020 205V345H750", dashed=True)
        for x, label, note in [
            (35, "Model gateway", "proposal + output schema"),
            (455, "Retrieval", "scope + version + evidence"),
            (875, "Tool gateway", "approval + operation key"),
        ]:
            c.box(x, 490, 290, 105, label, note)
        c.path("M450 345H180V485")
        c.line(600, 395, 600, 485)
        c.path("M750 365H1020V485")
        c.text(35, 650, ui["architecture_note"], size=19, width=110)
    return c

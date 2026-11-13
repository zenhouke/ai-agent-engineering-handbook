"""Multi-Agent design mechanisms: ownership, contracts, state, scheduling and recovery."""

from svg_canvas import Canvas


def draw(key: str, c: Canvas, data: dict, ui: dict) -> bool:
    if key not in ui["multi_design"]:
        return False
    t = ui["multi_design"][key]
    if key == "ma01":
        c.box(32, 110, 300, 100, t["goal"])
        c.box(465, 110, 300, 100, t["a"])
        c.box(465, 295, 300, 100, t["b"])
        c.box(890, 200, 275, 110, t["merge"])
        c.path("M338 160H395V160H459")
        c.path("M395 160V345H459")
        c.path("M771 160H820V235H884")
        c.path("M771 345H820V275H884")
        c.text(40, 445, t["ownership"], size=20, width=108)
    elif key == "ma02":
        c.box(32, 110, 280, 80, t["sender"])
        c.box(880, 110, 285, 80, t["receiver"])
        c.rect(385, 100, 425, 330)
        for i, line in enumerate(t["fields"]):
            c.text(405, 145 + i * 44, line, size=20, width=36)
        c.line(318, 150, 379, 150)
        c.line(816, 150, 874, 150)
        c.text(35, 300, t["artifact"], size=21, width=28)
        c.text(870, 300, t["accept"], size=21, width=29)
    elif key == "ma03":
        for i, label in enumerate(t["claims"]):
            c.box(32, 100 + i * 110, 430, 85, label)
            c.path(f"M468 {142 + i * 110}H530V252H594")
        c.box(600, 200, 565, 120, t["conflict"])
        c.text(600, 390, t["no_vote"], size=22, width=47)
    elif key == "ma04":
        c.box(32, 110, 285, 220, t["pending"])
        c.box(450, 110, 300, 220, t["slots"])
        c.box(885, 110, 280, 220, t["done"])
        for i, label in enumerate(t["jobs"]):
            c.text(50, 190 + i * 46, label, size=20, width=24)
        c.box(470, 180, 260, 55, "worker slot 1")
        c.box(470, 252, 260, 55, "worker slot 2")
        c.line(323, 220, 444, 220)
        c.line(756, 220, 879, 220)
        c.path("M1025 335V385H175V335")
        c.text(370, 415, t["release"], size=20, width=75)
    elif key == "ma05":
        c.box(32, 190, 260, 100, t["failure"])
        c.box(450, 110, 315, 95, t["unknown"])
        c.box(450, 310, 315, 95, t["confirmed"])
        c.box(890, 110, 275, 95, t["query"])
        c.box(890, 310, 275, 95, t["compensate"])
        c.path("M298 240H360V157H444")
        c.path("M360 240V357H444")
        c.line(771, 157, 884, 157)
        c.line(771, 357, 884, 357)
        c.path("M1027 211V275H608V304", dashed=True)
    elif key == "ma06":
        for i, label in enumerate(t["cases"]):
            c.box(32, 110 + i * 105, 325, 80, label)
        c.box(470, 110, 300, 280, t["single"])
        c.box(870, 110, 295, 280, t["multi"])
        c.line(363, 255, 464, 255)
        c.line(776, 255, 864, 255, arrow=False)
        c.text(490, 210, t["metrics"], size=20, width=22)
        c.text(890, 210, t["metrics"], size=20, width=22)
        c.text(40, 445, t["gate"], size=21, width=108)
    elif key == "ma07":
        c.box(32, 110, 335, 105, t["traffic"])
        for i in range(3):
            c.box(495, 100 + i * 110, 230, 75, f"worker {i + 1}")
        c.box(885, 170, 280, 180, t["quota"])
        for i in range(3):
            c.path(f"M373 162H430V{137 + i * 110}H489")
            c.path(f"M731 {137 + i * 110}H805V260H879")
        c.text(35, 430, t["formula"], size=22, width=108)
    c.text(32, 490, t["footer"], size=18, width=118)
    return True

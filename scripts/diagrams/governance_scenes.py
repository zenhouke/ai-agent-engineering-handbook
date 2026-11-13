"""Show identity/session lifetimes, authorization gates and approval transaction boundaries."""

from .svg_canvas import Canvas


def draw(key: str, c: Canvas, data: dict, ui: dict) -> bool:
    if key not in ui["governance_scenes"]:
        return False
    text = ui["governance_scenes"][key]
    if key == "session01":
        c.box(32, 195, 220, 110, text["actor"])
        c.box(380, 110, 275, 90, text["old"])
        c.box(380, 300, 275, 90, text["new"])
        c.box(805, 200, 360, 110, text["task"])
        c.path("M258 250H315V155H374")
        c.path("M315 250V345H374")
        c.path("M661 155H730V230H799", dashed=True)
        c.path("M661 345H730V280H799")
        c.text(785, 365, text["run"], size=20, width=35)
    elif key == "session02":
        c.box(32, 110, 400, 90, text["expired"])
        c.box(32, 290, 400, 90, text["fresh"])
        c.box(580, 175, 585, 135, text["claim"])
        c.path("M438 155H495", dashed=True, arrow=False)
        c.text(467, 136, "×", size=30)
        c.path("M438 335H510V242H574")
        c.box(580, 365, 585, 75, text["atomic"])
        c.line(872, 315, 872, 359)
    elif key == "auth01":
        for i, label in enumerate(text["gates"]):
            c.box(32 + i * 395, 130, 350, 125, label)
            if i < 2:
                c.line(388 + i * 395, 192, 421 + i * 395, 192)
            c.path(f"M{207 + i * 395} 260V285H600V290", dashed=True)
        c.circle(600, 315, 20)
        c.text(584, 321, "AND", size=16, width=5)
        c.path("M578 315H282V334")
        c.path("M622 315H915V334")
        c.box(32, 340, 500, 85, text["deny"])
        c.box(665, 340, 500, 85, text["allow"])
    elif key == "auth02":
        c.box(32, 110, 300, 100, text["pep"])
        c.box(450, 110, 300, 100, text["pdp"])
        c.box(865, 110, 300, 100, text["facts"])
        c.line(338, 150, 444, 150)
        c.line(756, 150, 859, 150)
        c.path("M600 215V265H182V216")
        c.text(335, 248, text["decision"], size=18, width=42)
        c.box(32, 335, 510, 95, text["worker"])
        c.box(655, 335, 510, 95, text["service"])
        c.line(548, 382, 649, 382)
    elif key == "approval01":
        c.box(32, 110, 570, 285, text["action"])
        for i, field in enumerate(text["fields"]):
            c.text(50, 190 + i * 43, field, size=20, width=47)
        c.box(760, 110, 405, 100, text["approver"])
        c.box(760, 295, 405, 100, text["record"])
        c.line(608, 250, 690, 250)
        c.path("M690 250V160H754")
        c.line(962, 215, 962, 289)
        c.text(40, 445, text["recheck"], size=21, width=100)
    elif key == "approval02":
        c.rect(32, 110, 1135, 190)
        c.text(50, 145, text["transaction"], size=21, width=95)
        for i, label in enumerate(text["writes"]):
            c.box(50 + i * 375, 175, 340, 90, label)
            if i < 2:
                c.line(396 + i * 375, 220, 419 + i * 375, 220)
        c.box(32, 340, 500, 95, text["rollback"])
        c.box(655, 340, 510, 95, text["dispatch"])
        c.path("M600 305V320H282V334", dashed=True)
        c.path("M1168 220H1180V387H1170")
    c.text(32, 490, text["footer"], size=18, width=118)
    return True

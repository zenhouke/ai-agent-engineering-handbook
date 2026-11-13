"""State, budget, protocol and coordination diagrams for agent lessons."""

from svg_canvas import BLUE, MIST, PAPER, Canvas


def draw(key: str, c: Canvas, d: dict, ui: dict) -> bool:
    s = d["steps"]
    if key == "a01":
        for x, y, w, h, t in [
            (50, 170, 230, 100, s[0]),
            (390, 170, 260, 100, s[1]),
            (800, 170, 310, 100, s[2]),
        ]:
            c.box(x, y, w, h, t)
        c.line(285, 220, 385, 220)
        c.line(655, 220, 795, 220)
        c.path("M950 275V370H160V275")
        c.text(380, 410, ui["observation"], size=20, width=65)
        c.box(390, 65, 260, 65, s[3])
        c.path("M160 165V100H385")
        c.text(50, 470, ui["loop_limit"], size=20, width=105)
    elif key == "a02":
        for i, (name, path) in enumerate(
            [
                ("Sequence", "Input → A → B → Verify"),
                ("Router", "Type? → specialist A / B"),
                ("Plan-and-Execute", "Goal → plan → steps → replan"),
                ("Reflection", "Draft → review → revise / stop"),
            ]
        ):
            y = 95 + i * 95
            c.box(35, y, 280, 75, name)
            c.text(370, y + 43, path, size=24, width=65)
            c.line(320, y + 37, 355, y + 37)
    elif key == "a03":
        values = [
            ("Instructions", 15),
            ("Task", 20),
            ("Evidence", 35),
            ("Tool/output reserve", 30),
        ]
        x = 50
        for i, (label, value) in enumerate(values):
            w = value * 11
            c.rect(x, 175, w, 120, BLUE if i % 2 == 0 else MIST)
            c.text(x + 12, 223, str(value) + "%", fill="white", width=13)
            c.text(x + 12, 265, label, size=16, width=max(12, int(w / 9)), fill="white")
            x += w
        for i, t in enumerate(s):
            c.text(45 + i * 295, 365, t, size=22, width=23)
        c.text(45, 460, ui["budget"], size=20, width=108)
    elif key == "a04":
        c.box(40, 110, 430, 285, ui["original"], ui["artifact"])
        for i in range(6):
            c.rect(65, 165 + i * 27, 370, 15, MIST)
        c.line(480, 250, 620, 250)
        for i, t in enumerate(s):
            c.box(650, 95 + i * 85, 500, 68, t, color="white" if i != 1 else PAPER)
        c.text(45, 465, ui["protected"], size=20, width=108)
    elif key == "a05":
        participants = [(130, "Worker A"), (535, "Checkpoint DB"), (980, "Worker B")]
        for x, t in participants:
            c.text(x - 65, 115, t, width=22)
            c.path(f"M{x} 140V440", dashed=True, arrow=False)
        for y, x1, x2, t in [
            (180, 535, 130, "snapshot v=7"),
            (225, 535, 980, "snapshot v=7"),
            (270, 980, 535, "CAS expected=7"),
            (315, 535, 980, "commit v=8"),
            (360, 130, 535, "CAS expected=7"),
            (410, 535, 130, "conflict; current v=8"),
        ]:
            c.line(x1, y, x2, y)
            c.text(min(x1, x2) + 12, y - 15, t, size=20, width=55)
        c.text(40, 485, ui["cas"], size=19, width=112)
    elif key == "a06":
        for i, t in enumerate(
            ["tenant=A, user=U", "tenant=B, user=U", "tenant=A, user=V"]
        ):
            c.box(35, 95 + i * 110, 350, 80, t)
        c.box(490, 165, 250, 140, s[0])
        c.path("M390 135H440V205H485")
        c.path("M390 245H430", dashed=True, arrow=False)
        c.path("M390 355H430", dashed=True, arrow=False)
        c.text(430, 265, "×", size=34)
        c.text(430, 370, "×", size=34)
        c.box(845, 155, 315, 170, s[3], ui["provenance"])
        c.line(745, 235, 840, 235)
        c.text(40, 460, ui["memory"], size=20, width=108)
    elif key == "a07":
        for x, t in [(35, "Host"), (430, "MCP client"), (825, "MCP server")]:
            c.box(x, 130, 330, 110, t)
        c.line(370, 185, 425, 185)
        c.line(765, 185, 820, 185)
        c.box(430, 330, 730, 100, s[3], ui["business_boundary"])
        c.path("M990 245V325")
        c.text(35, 290, "tools / resources / prompts", size=23, width=78)
        c.text(35, 485, ui["protocol"], size=19, width=112)
    elif key == "a08":
        c.box(30, 210, 230, 100, s[0])
        c.box(940, 210, 230, 100, s[2])
        for i, t in enumerate(["Research A", "Research B", "Research C"]):
            y = 90 + i * 135
            c.box(425, y, 300, 85, t)
            c.path(f"M265 260H340V{y + 42}H420")
            c.path(f"M730 {y + 42}H840V260H935")
        c.text(40, 480, ui["parallel"], size=20, width=108)
    elif key == "a09":
        c.chain(s, 120)
        c.box(430, 320, 340, 95, "STOP / WAIT / UNKNOWN")
        c.path("M155 225V365H425", dashed=True)
        c.path("M1040 225V285H600V315", dashed=True)
        c.text(35, 465, ui["runtime"], size=20, width=108)
    elif key == "a10":
        c.box(35, 110, 260, 120, s[0])
        c.box(35, 310, 260, 120, s[1])
        c.path("M165 235V305")
        for i, (name, status) in enumerate(
            [("Extract", "done"), ("Verify", "ready"), ("Report", "waiting")]
        ):
            c.box(440 + i * 245, 210, 210, 115, name, status)
            if i < 2:
                c.line(655 + i * 245, 267, 680 + i * 245, 267)
        c.path("M300 370H380V267H435")
        c.text(350, 460, ui["plan"], size=20, width=79)
    elif key == "a11":
        rows = [
            ("Normal", 9, 10),
            ("Missing evidence", 7, 10),
            ("Conflicting facts", 6, 10),
            ("Unauthorized action", 0, 10),
        ]
        for i, (label, value, total) in enumerate(rows):
            y = 120 + i * 83
            c.text(40, y + 28, label, size=22, width=28)
            for j in range(total):
                c.rect(380 + j * 58, y, 45, 38, BLUE if j < value else "white")
            c.text(1000, y + 29, f"{value}/{total}", size=24, width=12)
        c.text(40, 480, ui["synthetic_scores"], size=19, width=110)
    elif key == "a12":
        c.chain(s, 100)
        for i, t in enumerate(
            ["routes → handlers", "services → ports", "repos → storage"]
        ):
            c.box(175 + i * 330, 300, 300, 90, t)
        c.text(40, 470, ui["layers"], size=20, width=110)
    else:
        return False
    return True

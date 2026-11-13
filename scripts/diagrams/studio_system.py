"""One integrated reference architecture, with explicit trust and execution edges."""

import json
from pathlib import Path

from .svg_canvas import BLUE, MIST, PAPER, Canvas, wrap

ROOT = Path(__file__).resolve().parents[2]


def architecture(language: str) -> Canvas:
    ui = json.loads((ROOT / f"site/i18n/studio-system-{language}.json").read_text())
    c = Canvas(ui["title"], ui["description"], 1590, width=1800)
    c.text(32, 83, ui["subtitle"], size=20, width=166)

    def boundary(x, y, w, h, label):
        c.rect(x, y, w, h, fill=PAPER, stroke=MIST)
        c.text(x + 16, y + 29, label, size=20, width=int((w - 32) / 10))

    def card(key, x, y, w, h, emphasis=False):
        item = ui["nodes"][key]
        c.rect(x, y, w, h, stroke=BLUE if emphasis else MIST)
        c.rect(x, y, 5, h, fill=BLUE, stroke=BLUE, radius=0)
        title = wrap(item["title"], int((w - 30) / 10))
        for i, line in enumerate(title):
            c.text(x + 16, y + 30 + i * 28, line, size=20, width=200)
        top = y + 38 + len(title) * 28
        for line in item["lines"]:
            for part in wrap(line, int((w - 30) / 8)):
                c.text(x + 16, top, part, size=16, width=200)
                top += 23
        if top - 18 > y + h - 4:
            raise ValueError(f"Architecture card overflows: {language}/{key}")

    boundary(350, 300, 1060, 260, ui["regions"]["control"])
    boundary(350, 595, 1060, 225, ui["regions"]["agents"])
    boundary(350, 890, 1060, 245, ui["regions"]["capabilities"])
    boundary(24, 330, 290, 460, ui["regions"]["context"])
    boundary(24, 1205, 1386, 220, ui["regions"]["data"])
    boundary(1460, 1205, 315, 220, ui["regions"]["operations"])

    # Draw connectors before opaque cards. Gutter routes never cross a card.
    # Solid paths carry commands/reads; dashed paths carry receipts/events.
    edges = [
        ("M314 195H370", False),
        ("M850 195H895", False),
        ("M610 250V285H515V355", False),
        ("M1135 250V285H1220V355", False),
        ("M655 425H700", False),
        ("M1020 425H1060", False),
        ("M290 435H328V420H375", False),
        ("M290 570H328V420", False),
        ("M290 705H328V570", False),
        ("M860 500V575H515V645", False),
        ("M860 575V645", False),
        ("M860 575H1205V645", False),
        ("M515 785V855H860", False),
        ("M860 785V855", False),
        ("M1205 785V855H860", False),
        ("M860 855H515V945", False),
        ("M860 855V945", False),
        ("M375 1010H314", False),
        ("M1000 985H1035V985H1065", False),
        ("M1000 1040H1035V1085H1065", False),
        ("M1065 1008H1000", True),
        ("M720 1075H680V1195H1250V1265", True),
        ("M1345 985H1435V465H1460", False),
        ("M860 1095V1160H1425V990H1460", False),
        ("M1460 210H1448V940H1345", False),
        ("M800 500V535H338V1175H210V1265", False),
        ("M1205 1125V1188H560V1265", False),
        ("M45 735H14V1180H895V1265", False),
        ("M1250 1265V1180H1390V425H1380", True),
        ("M1020 455H1040V585H1440V1305H1480", True),
        ("M1385 1340H1480", True),
        ("M1755 1330H1788V120H1140V140", True),
    ]
    for path, dashed in edges:
        c.path(path, dashed=dashed)

    cards = [
        ("operator", 24, 140, 290, 110),
        ("entry", 370, 140, 480, 110),
        ("policy", 895, 140, 490, 110),
        ("secrets", 1460, 140, 315, 155),
        ("lead", 375, 355, 280, 145),
        ("runtime", 700, 355, 320, 145),
        ("contracts", 1060, 355, 320, 145),
        ("context", 45, 385, 245, 100),
        ("skills", 45, 520, 245, 100),
        ("retrieval", 45, 655, 245, 110),
        ("research", 375, 645, 280, 140),
        ("execution", 720, 645, 280, 140),
        ("review", 1065, 645, 280, 140),
        ("platforms", 1460, 365, 315, 200),
        ("model", 375, 945, 280, 150),
        ("host", 720, 945, 280, 150),
        ("browser", 1065, 940, 280, 85),
        ("sandbox", 1065, 1045, 280, 80),
        ("providers", 24, 945, 290, 150),
        ("mcp", 1460, 900, 315, 195),
        ("database", 45, 1265, 330, 130),
        ("artifacts", 410, 1265, 300, 130),
        ("knowledge", 745, 1265, 300, 130),
        ("outbox", 1080, 1265, 305, 130),
        ("operations", 1480, 1265, 275, 130),
    ]
    for key, x, y, w, h in cards:
        card(key, x, y, w, h, key in {"policy", "runtime", "host"})

    c.text(460, 278, ui["labels"]["authenticated"], size=16, width=50)
    c.text(1045, 278, ui["labels"]["gates"], size=16, width=42)
    c.text(890, 555, ui["labels"]["dispatch"], size=16, width=48)
    c.text(600, 848, ui["labels"]["proposals"], size=16, width=55)
    c.text(1460, 630, ui["labels"]["receipt"], size=18, width=31)
    c.text(1460, 770, ui["labels"]["boundary"], size=18, width=31)
    c.text(40, 840, ui["labels"]["method"], size=17, width=30)
    c.text(1460, 1150, ui["labels"]["telemetry"], size=16, width=36)
    c.text(1260, 112, ui["labels"]["feedback"], size=16, width=50)
    c.text(35, 1470, ui["journey"], size=21, width=160)
    c.text(35, 1540, ui["legend"], size=18, width=176)
    return c

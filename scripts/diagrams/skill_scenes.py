"""Skill disclosure, composition and model/protocol interface diagrams."""

from .svg_canvas import Canvas


def draw(key: str, c: Canvas, data: dict, ui: dict) -> bool:
    if key not in ui["skill_scenes"]:
        return False
    labels = ui["skill_scenes"][key]
    if key == "skill01":
        for i, label in enumerate(labels["layers"]):
            c.box(32, 110 + i * 85, 570, 65, label)
        c.box(760, 110, 400, 120, labels["plan"])
        c.box(760, 310, 400, 120, labels["state"])
        c.path("M754 170H680V300H608")
        c.path("M754 370H710V325H608")
    elif key == "skill02":
        for i, (file, role) in enumerate(zip(labels["files"], labels["roles"])):
            y = 110 + i * 69
            c.box(32, y, 430, 60, file)
            c.box(600, y, 560, 60, role)
            c.line(468, y + 30, 594, y + 30)
    elif key == "skill03":
        for i, title in enumerate(labels["tiers"]):
            c.box(32 + i * 395, 110, 350, 250, title)
        for i in range(6):
            c.rect(58, 175 + i * 25, 285, 16)
        c.rect(58, 225, 285, 16, fill="#A6B7CC")
        c.box(445, 180, 300, 110, labels["one_body"])
        c.box(840, 180, 300, 70, labels["resource"])
        c.text(845, 292, labels["no_exec"], size=18, width=30)
        c.line(388, 230, 420, 230)
        c.line(783, 230, 815, 230)
        c.box(32, 395, 1136, 65, labels["dedupe"])
    elif key == "skill04":
        for i, title in enumerate(labels["sets"]):
            c.box(32 + i * 395, 110, 350, 85, title)
            c.path(f"M{207 + i * 395} 199V235H600V265")
        c.box(360, 270, 480, 80, labels["intersection"])
        c.box(32, 390, 500, 65, labels["allow"])
        c.box(665, 390, 500, 65, labels["deny"])
        c.path("M480 354V375H282V384")
        c.path("M720 354V375H915V384", dashed=True)
    elif key == "skill05":
        c.box(32, 110, 320, 95, labels["a"])
        c.box(32, 280, 320, 95, labels["b"])
        c.box(465, 190, 300, 120, labels["join"])
        c.box(875, 190, 290, 120, labels["next"])
        c.path("M358 158H410V250H459")
        c.path("M358 328H410V250")
        c.line(771, 250, 869, 250)
        c.text(372, 353, labels["contract"], size=19, width=55)
        c.box(465, 405, 700, 60, labels["invalidate"])
        c.path("M615 399V317", dashed=True)
    elif key == "skill06":
        c.text(35, 120, labels["selection"], width=50)
        for i, value in enumerate(labels["cells"]):
            c.box(32 + (i % 2) * 260, 150 + (i // 2) * 110, 245, 95, value)
        c.box(650, 150, 515, 90, labels["baseline"])
        c.box(650, 280, 515, 90, labels["candidate"])
        c.path("M907 245V275")
        c.box(32, 410, 1135, 55, labels["gate"])
    elif key == "fc01":
        c.box(32, 140, 260, 100, labels["model"])
        c.box(440, 140, 320, 100, labels["host"])
        c.box(890, 140, 275, 100, labels["function"])
        c.line(298, 190, 434, 190)
        c.line(766, 190, 884, 190)
        c.text(318, 165, "function_call", size=16, width=14)
        c.text(790, 165, labels["authorize"], size=16, width=13)
        c.path("M1027 246V365H162V246")
        c.text(300, 345, labels["result"], size=21, width=75)
        c.box(32, 415, 1135, 55, labels["strict"])
    elif key == "fc02":
        c.box(32, 195, 250, 105, labels["proposal"])
        c.box(385, 195, 250, 105, labels["host"])
        c.line(288, 247, 379, 247)
        c.box(730, 110, 435, 95, labels["direct"])
        c.box(730, 315, 200, 95, "MCP Client")
        c.box(980, 315, 185, 95, "MCP Server")
        c.path("M641 247H680V158H724")
        c.path("M680 247V362H724")
        c.line(936, 362, 974, 362)
        c.text(760, 260, labels["alternatives"], size=19, width=40)
        # Both backends return to the Host before the observation reaches the model.
        c.path("M1170 158H1178V427H510V306")
        c.path("M1072 416V427", arrow=False)
        c.path("M379 275H340V365H157V306")
        c.text(335, 455, labels["return"], size=19, width=75)
    c.text(32, 495, labels["footer"], size=18, width=118)
    return True

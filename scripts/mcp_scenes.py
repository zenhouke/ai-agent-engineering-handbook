"""MCP-specific diagrams, scoped to the 2026-07-28 protocol revision."""

from svg_canvas import Canvas


def draw(key: str, c: Canvas, data: dict, ui: dict) -> bool:
    if key == "mcp01":
        c.rect(30, 100, 640, 340)
        c.text(50, 135, ui["mcp_labels"]["host"], width=48)
        c.box(70, 190, 235, 95, ui["mcp_labels"]["model"])
        c.box(370, 170, 250, 80, "MCP Client A")
        c.box(370, 300, 250, 80, "MCP Client B")
        c.path("M310 235H335V210H365")
        c.path("M335 235V340H365")
        c.box(
            800,
            170,
            350,
            80,
            ui["mcp_labels"]["quote_server"],
            "services → repos / API",
        )
        c.box(
            800, 300, 350, 80, ui["mcp_labels"]["doc_server"], "services → repos / API"
        )
        c.line(625, 210, 795, 210)
        c.line(625, 340, 795, 340)
        c.text(40, 485, data["principle"], size=18, width=116)
    elif key == "mcp02":
        for y, name, method, result in [
            (
                100,
                ui["mcp_labels"]["tools"],
                "tools/list → tools/call",
                ui["mcp_labels"]["tool_result"],
            ),
            (
                230,
                ui["mcp_labels"]["resources"],
                "resources/read",
                ui["mcp_labels"]["resource_result"],
            ),
            (
                360,
                ui["mcp_labels"]["prompts"],
                "prompts/get",
                ui["mcp_labels"]["prompt_result"],
            ),
        ]:
            c.box(35, y, 225, 90, name)
            c.box(355, y, 425, 90, method)
            c.box(870, y, 295, 90, result)
            c.line(265, y + 45, 350, y + 45)
            c.line(785, y + 45, 865, y + 45)
    elif key == "mcp03":
        c.box(35, 95, 530, 340, "2026-07-28")
        c.box(640, 95, 525, 340, ui["mcp_labels"]["old"])
        for i, text in enumerate(
            [
                ui["mcp_labels"]["discover"],
                ui["mcp_labels"]["list_meta"],
                ui["mcp_labels"]["call_meta"],
            ]
        ):
            c.text(55, 180 + i * 80, text, size=20, width=47)
        for i, text in enumerate(
            [
                ui["mcp_labels"]["initialize"],
                "notifications/initialized",
                "tools/list → tools/call",
            ]
        ):
            c.text(660, 180 + i * 80, text, size=20, width=46)
        c.text(
            35,
            490,
            ui["mcp_labels"]["ids"],
            size=20,
            width=114,
        )
    elif key == "mcp04":
        c.box(35, 100, 400, 110, "stdio", ui["mcp_labels"]["process"])
        c.box(735, 100, 430, 110, "Streamable HTTP", ui["mcp_labels"]["http_response"])
        c.text(470, 140, ui["mcp_labels"]["same_rpc"], size=20, width=22)
        for i, (title, detail) in enumerate(
            [
                (ui["mcp_labels"]["authentication"], ui["mcp_labels"]["verify"]),
                (ui["mcp_labels"]["authorization"], ui["mcp_labels"]["scope"]),
                (ui["mcp_labels"]["domain"], ui["mcp_labels"]["receipt"]),
            ]
        ):
            x = 35 + i * 395
            c.box(x, 330, 350, 100, title, detail)
            if i < 2:
                c.line(x + 355, 380, x + 390, 380)
        c.text(
            35,
            490,
            ui["mcp_labels"]["transport_boundary"],
            size=20,
            width=114,
        )
    elif key == "mcp05":
        for i, label in enumerate(
            [
                "Client(server)",
                ui["mcp_labels"]["registration"],
                "handlers → services\n→ repos",
            ]
        ):
            c.box(35 + i * 395, 145, 350, 110, label)
            if i < 2:
                c.line(390 + i * 395, 200, 425 + i * 395, 200)
        c.box(
            245,
            330,
            710,
            100,
            "read_quote(A) → unit_cents=180",
            ui["mcp_labels"]["readonly"],
        )
        c.path("M1010 265V300H600V325")
        c.text(
            35,
            490,
            ui["mcp_labels"]["memory_scope"],
            size=20,
            width=114,
        )
    elif key == "mcp06":
        for i, label in enumerate(
            [
                ui["mcp_labels"]["catalog"],
                ui["mcp_labels"]["provider"],
                ui["mcp_labels"]["proposal"],
                ui["mcp_labels"]["gateway"],
                ui["mcp_labels"]["client_server"],
            ]
        ):
            c.box(32 + i * 235, 125, 200, 110, label)
            if i < 4:
                c.line(236 + i * 235, 180, 262 + i * 235, 180)
        c.path("M1070 240V365H600V240")
        c.text(
            315,
            310,
            ui["mcp_labels"]["observation"],
            size=21,
            width=70,
        )
        c.text(
            35,
            470,
            ui["mcp_labels"]["unknown"],
            size=20,
            width=114,
        )
    else:
        return False
    return True

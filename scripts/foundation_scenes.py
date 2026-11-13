"""Mechanism scenes for foundations and LLM application lessons."""

from svg_canvas import BLUE, MIST, PAPER, Canvas


def draw(key: str, c: Canvas, d: dict, ui: dict) -> bool:
    labels = d["steps"]
    if key == "f01":
        for i, (x, y, w, h, label) in enumerate(
            [
                (40, 95, 720, 340, "AI"),
                (100, 150, 620, 245, "Machine learning"),
                (160, 220, 510, 135, "Deep learning"),
            ]
        ):
            c.rect(x, y, w, h, "white" if i % 2 == 0 else PAPER)
            c.text(x + 20, y + 36, label)
        c.box(815, 150, 345, 175, "Agent", labels[3])
        c.path("M765 270H808")
        c.text(55, 470, ui["orthogonal"], size=19, width=108)
    elif key == "f02":
        c.chain(labels, 110)
        for x, a, b in [
            (45, "x=2; y=4; w=1", "ŷ=2; L=4"),
            (340, "dL/dw=2(wx−y)x", "gradient = −8"),
            (635, "w ← w − η∇L", "η=0.1 → w=1.8"),
            (930, "ŷ=3.6", "L=0.16"),
        ]:
            c.text(x, 295, a, size=21, width=23)
            c.text(x, 350, b, size=21, width=23)
        c.text(40, 460, "η=0.3 → w=3.4 → L=7.84", size=25, width=70)
    elif key == "f03":
        c.text(60, 110, ui["confusion"], width=40)
        cells = [
            (80, 155, "TP 15", BLUE),
            (290, 155, "FP 10", MIST),
            (80, 265, "FN 5", MIST),
            (290, 265, "TN 70", BLUE),
        ]
        for x, y, t, color in cells:
            c.rect(x, y, 190, 90, color)
            c.text(x + 28, y + 52, t, fill="white")
        c.box(590, 130, 550, 90, "Precision = 15/25 = 0.60")
        c.box(590, 245, 550, 90, "Recall = 15/20 = 0.75")
        c.text(75, 430, "Accuracy=0.85; F1≈0.667", width=45)
        c.text(590, 415, ui["threshold"], size=20, width=48)
    elif key == "f04":
        positions = [(120, [170, 285]), (450, [170, 285]), (790, [225])]
        for x, ys in positions:
            for y in ys:
                c.circle(x, y, 27)
        for y1 in [170, 285]:
            for y2 in [170, 285]:
                c.line(151, y1, 416, y2)
        for y in [170, 285]:
            c.line(481, y, 756, 225)
        c.box(930, 180, 220, 90, labels[3])
        c.line(820, 225, 925, 225)
        for x, t in [(55, "X: [B,2]"), (360, "ReLU(XW₁+b₁)"), (710, "logit: [B,1]")]:
            c.text(x, 375, t, width=25)
        c.path("M1040 280V435H460V320", dashed=True)
        c.text(560, 470, ui["backprop"], size=20, width=55)
    elif key == "f05":
        for offset, values in [(50, [[1, 2], [3, 4]]), (400, [[1, 0], [0, -1]])]:
            for r, row in enumerate(values):
                for col, value in enumerate(row):
                    c.rect(offset + col * 100, 145 + r * 95, 90, 85)
                    c.text(offset + col * 100 + 33, 195 + r * 95, str(value), size=28)
        c.text(300, 245, "⊙", size=40)
        c.line(630, 235, 760, 235)
        c.box(800, 185, 310, 110, "Σ = 1 − 4 = −3")
        c.text(55, 390, labels[0] + " → " + labels[1] + " → " + labels[2], width=94)
        c.text(55, 455, ui["conv"], size=19, width=108)
    elif key == "f06":
        for i, (a, b) in enumerate([("a", "ID 0"), ("b", "ID 1"), ("<end>", "ID 2")]):
            c.box(45, 115 + i * 100, 170, 75, a)
            c.line(220, 153 + i * 100, 330, 153 + i * 100)
            c.box(340, 115 + i * 100, 170, 75, b)
            for j in range(4):
                c.rect(
                    630 + j * 65, 130 + i * 100, 55, 45, BLUE if (i + j) % 2 else MIST
                )
            c.line(515, 153 + i * 100, 620, 153 + i * 100)
        c.text(45, 460, ui["encoding"], size=19, width=110)
        c.box(960, 160, 205, 155, "LM head", "P(next | prefix)")
        c.path("M900 153H930V210H955")
        c.path("M900 353H930V265H955")
    elif key == "f07":
        for r in range(4):
            for col in range(4):
                x = 50 + col * 67
                y = 140 + r * 67
                visible = col <= r
                c.rect(x, y, 59, 59, BLUE if visible else "white")
                c.text(
                    x + 18,
                    y + 38,
                    "1" if visible else "0",
                    fill="white" if visible else MIST,
                )
        c.text(50, 110, "mask: past + self", width=30)
        c.box(405, 110, 745, 85, "S = QKᵀ/√dₖ + mask")
        c.box(405, 215, 745, 85, "A = softmax(S); O = AV")
        c.box(
            405,
            320,
            745,
            115,
            "q=[1]; K=[1,0]; V=[[2,0],[0,2]]",
            "A≈[0.7311,0.2689]; O≈[1.4621,0.5379]",
        )
        c.text(
            50,
            480,
            "X[B,T,D] → Q/K/V → heads → mix → residual → FFN",
            size=20,
            width=110,
        )
    elif key == "f08":
        c.rect(45, 115, 350, 220, BLUE)
        c.text(75, 165, "W: [4096,4096]", fill="white", width=30)
        c.text(75, 225, "frozen base", fill="white", width=28)
        c.text(435, 245, "+", size=42)
        c.rect(510, 115, 72, 220, MIST)
        c.text(490, 380, "B [4096,8]", size=18, width=20)
        c.text(615, 245, "×", size=36)
        c.rect(680, 190, 290, 72, MIST)
        c.text(700, 300, "A [8,4096]", size=20, width=25)
        c.line(995, 225, 1070, 225)
        c.text(1080, 205, "W′", size=30, width=6)
        c.text(
            45,
            455,
            "16,777,216 base parameters; 65,536 trainable (r=8)",
            size=23,
            width=98,
        )
    elif key == "l01":
        c.chain(labels, 135)
        for i, t in enumerate(
            ["goal + sources", "fields / types", "support + units", "object / approval"]
        ):
            c.text(45 + i * 295, 290, t, size=20, width=24)
        c.path("M1030 245V365H420V245", dashed=True)
        c.text(45, 435, ui["not_equivalent"], size=20, width=110)
    elif key == "l02":
        c.box(30, 205, 230, 95, labels[0])
        c.box(345, 105, 260, 90, "BM25 / keyword")
        c.box(345, 310, 260, 90, "Embedding / vector")
        c.path("M265 250H300V150H340")
        c.path("M300 250V355H340")
        c.box(705, 205, 225, 95, "RRF + reranker")
        c.path("M610 150H655V250H700")
        c.path("M610 355H655V265H700")
        c.box(980, 190, 185, 125, labels[3])
        c.line(935, 250, 975, 250)
        c.text(40, 465, ui["retrieval"], size=20, width=110)
    elif key == "l03":
        c.box(45, 125, 315, 100, "Prefill", labels[0])
        c.line(365, 175, 435, 175)
        for i in range(4):
            c.box(445 + i * 175, 125, 150, 100, f"t{i + 1}", "Decode")
            if i < 3:
                c.line(600 + i * 175, 175, 615 + i * 175, 175)
        for i in range(6):
            c.rect(445 + i * 105, 310, 90, 55, BLUE if i < 3 else MIST)
        c.text(45, 345, "KV cache", width=24)
        c.path("M465 305V260H530V230")
        c.line(445, 285, 1100, 285, arrow=False)
        c.text(
            45,
            440,
            "KV ≈ 2 × layers × batch × tokens × KV_heads × head_dim × bytes",
            size=21,
            width=112,
        )
    else:
        return False
    return True

from html import escape
from pathlib import Path

P = Path(__file__).resolve().parents[1] / "assets/diagrams"
NAVY = "#0B1F3A"
BLUE = "#1F4E9C"
MIST = "#A6B7CC"
PAPER = "#F4F6FA"


class Figure:
    def __init__(self, name, title, sub, h=440):
        self.name = name
        self.h = h
        self.parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="960" height="{h}" viewBox="0 0 960 {h}" role="img" aria-labelledby="title desc"><title id="title">{escape(title)}</title><desc id="desc">{escape(sub)}</desc><defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0L10 5L0 10" fill="{BLUE}"/></marker></defs><rect width="960" height="{h}" rx="12" fill="{PAPER}"/><g font-family="Noto Sans CJK SC,Microsoft YaHei,sans-serif" fill="{NAVY}">'
        ]
        self.text(32, 44, title, 25)
        self.text(32, 76, sub, 15)

    def text(self, x, y, s, size=17, fill=NAVY, anchor="start"):
        self.parts.append(
            f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" text-anchor="{anchor}">{escape(s)}</text>'
        )

    def box(self, x, y, w, title, sub="", h=74):
        self.parts.append(
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="white" stroke="{MIST}"/>'
        )
        self.text(x + 14, y + 29, title, 18)
        for i, t in enumerate(sub.split("|")):
            self.text(x + 14, y + 53 + i * 21, t, 14)

    def path(self, d, dash=False):
        self.parts.append(
            f'<path d="{d}" fill="none" stroke="{BLUE}" stroke-width="2" marker-end="url(#arrow)"'
            + (' stroke-dasharray="6 5"' if dash else "")
            + "/>"
        )

    def line(self, x1, y1, x2, y2, dash=False):
        self.path(f"M{x1} {y1}L{x2} {y2}", dash)

    def save(self):
        self.parts.append("</g></svg>")
        (P / (self.name + ".svg")).write_text("".join(self.parts))


def chain(name, title, sub, labels, foot):
    f = Figure(name, title, sub, 330)
    n = len(labels)
    w = 864 / n - 24
    for i, (a, b) in enumerate(labels):
        x = 32 + i * (w + 24)
        f.box(x, 125, w, a, b, h=100)
        if i < n - 1:
            f.line(x + w + 3, 175, x + w + 21, 175)
    f.text(32, 280, foot, 16)
    f.save()


chain(
    "learning-map",
    "从数据学习到系统行动",
    "先理解模型，再理解应用，最后设计可靠的执行系统",
    [
        ("数据与数学", "特征 · 概率|训练与验证"),
        ("模型机制", "神经网络|Token · 注意力"),
        ("LLM 应用", "契约 · 检索|推理与评价"),
        ("Agent 架构", "状态 · 工具|审批与恢复"),
    ],
    "箭头表示课程先修关系；每一阶段都需要例子、检验与失败分析。",
)
chain(
    "gradient",
    "一次梯度下降：把误差变成参数更新",
    "单样本 x=2，y=4；模型 ŷ=wx；损失 L=(ŷ-y)²",
    [
        ("前向计算", "w=1，ŷ=2|L=4"),
        ("链式法则", "dL/dw|=2×(2−4)×2=−8"),
        ("更新参数", "学习率 η=0.1|w ← 1−0.1×(−8)"),
        ("重新检查", "w=1.8，ŷ=3.6|新损失 L=0.16"),
    ],
    "梯度给出局部变化方向；步长过大仍可能使损失上升。",
)
f = Figure(
    "ml-cycle",
    "数据边界决定实验是否可信",
    "预处理只拟合训练集；测试集不参与选择模型",
    440,
)
f.box(32, 120, 175, "原始历史订单", "去重 · 按时间切分", h=85)
f.box(270, 110, 200, "训练集", "拟合预处理与模型", h=80)
f.box(270, 230, 200, "验证集", "选择阈值与超参数", h=80)
f.box(675, 170, 245, "独立测试集", "最终比较 · 分组评价", h=90)
f.path("M207 150H245V145H270")
f.path("M207 175H235V265H270")
f.path("M470 150H575V210H675")
f.path("M470 270H575V240H675")
f.path("M370 230V190", True)
f.text(32, 385, "先定义预测时刻，再选择特征。测试信息不能倒流回训练或调参。", 17)
f.save()
f = Figure(
    "neural-network",
    "前向表示与反向梯度",
    "线性层 + 非线性激活 + 损失；优化器执行参数更新",
    440,
)
for x, n in [(115, 2), (360, 3), (610, 2)]:
    ys = [160 + i * 62 for i in range(n)]
    for y in ys:
        f.parts.append(
            f'<circle cx="{x}" cy="{y}" r="19" fill="white" stroke="{BLUE}" stroke-width="2"/>'
        )
for x1, ys1, x2, ys2 in [
    (135, [160, 222], 340, [160, 222, 284]),
    (380, [160, 222, 284], 590, [160, 222]),
]:
    for y1 in ys1:
        for y2 in ys2:
            f.line(x1, y1, x2, y2)
f.box(740, 170, 170, "损失函数", "预测与标签比较", h=85)
f.line(630, 195, 740, 195)
f.text(74, 335, "输入 X", 18)
f.text(290, 335, "隐藏层 + ReLU", 18)
f.text(565, 335, "预测 logits", 18)
f.path("M815 265V370H360V310", True)
f.text(430, 400, "反向传播：沿计算图应用链式法则", 16)
f.save()
f = Figure(
    "modalities",
    "不同数据结构，需要不同的机制",
    "归纳偏置：在模型中利用数据的局部性、顺序或噪声结构",
    460,
)
for y, a, b, c in [
    (120, "图像局部区域", "卷积核共享参数", "特征图 → 分类 / 检测"),
    (225, "有顺序的序列", "RNN 状态 / 注意力", "上下文表示 → 预测"),
    (330, "噪声 + 条件", "多步去噪模型", "图像 / 潜在表示"),
]:
    f.box(32, y, 230, a)
    f.box(345, y, 245, b)
    f.box(680, y, 245, c)
    f.line(265, y + 37, 342, y + 37)
    f.line(592, y + 37, 677, y + 37)
f.save()
f = Figure(
    "token-loop",
    "语言模型的自回归循环",
    "Tokenizer 固定编码规则；模型输出下一 Token 的概率分布",
    420,
)
f.box(32, 125, 170, "文本前缀", "例如：交货期")
f.box(260, 125, 180, "Token IDs", "整数序列 → 向量")
f.box(495, 125, 190, "模型计算", "上下文 → logits")
f.box(740, 125, 185, "选择下个 Token", "采样 / greedy")
for a, b in [(202, 260), (440, 495), (685, 740)]:
    f.line(a + 2, 162, b - 3, 162)
f.path("M835 200V290H350V200")
f.text(380, 278, "追加到前缀，再预测下一步", 18)
f.text(32, 365, "直到结束 Token、长度上限或外部取消。推理通常不更新权重。", 17)
f.save()
f = Figure(
    "attention",
    "因果注意力：先屏蔽未来，再做加权和",
    "A = softmax(QKᵀ / √dₖ + mask)，O = AV",
    490,
)
f.text(45, 120, "每行只读取自己与过去的位置", 17)
for r in range(4):
    f.text(40, 171 + 47 * r, str(r + 1), 15)
    for c in range(4):
        x = 65 + c * 55
        y = 140 + r * 47
        ok = c <= r
        f.parts.append(
            f'<rect x="{x}" y="{y}" width="49" height="40" rx="4" fill="{BLUE if ok else MIST}" opacity="{1 if ok else 0.22}"/>'
        )
        f.text(
            x + 24,
            y + 26,
            "可见" if ok else "屏蔽",
            12,
            "white" if ok else NAVY,
            "middle",
        )
f.box(390, 125, 520, "一个 Query 的数值例子", "q=[1]；k₁=[1]，k₂=[0]；dₖ=1", h=80)
f.box(390, 230, 520, "softmax([1,0]) ≈ [0.731,0.269]", "v₁=[2,0]；v₂=[0,2]", h=80)
f.box(
    390,
    335,
    520,
    "输出 = [1.462, 0.538]",
    "若第二位置被 mask：权重 [1,0]，输出 [2,0]",
    h=80,
)
f.line(650, 207, 650, 227)
f.line(650, 312, 650, 332)
f.text(32, 455, "这张图展示计算机制，注意力权重不是完整的因果解释或思维日志。", 16)
f.save()
chain(
    "adaptation",
    "模型适配的不同阶段",
    "先用留出集定义问题，再判断是否值得改变参数",
    [
        ("预训练", "通用数据|预测学习"),
        ("SFT", "指令与示范|任务行为"),
        ("偏好优化", "回答比较|行为倾向"),
        ("独立评价", "事实与格式|回退与成本"),
    ],
    "LoRA 是参数更新方式，可用于适配阶段；它不是一个与 SFT 并列的任务目标。",
)
f = Figure(
    "output-contract",
    "输出正确，需要三道独立检查",
    "格式通过不等于事实成立；模型调用不等于获得授权",
    420,
)
for x, t, s in [
    (32, "任务与证据", "目标 · 来源 · 未知处理"),
    (340, "模型候选输出", "JSON / 工具调用建议"),
    (650, "执行前检查", "结构 → 事实 → 权限"),
]:
    f.box(x, 125, 275, t, s, h=90)
f.line(310, 170, 337, 170)
f.line(617, 170, 647, 170)
f.box(650, 270, 275, "允许执行 / 交付", "参数、对象与审批绑定", h=90)
f.line(790, 218, 790, 267)
f.path("M650 310H477V218", True)
f.text(35, 327, "失败：修复结构 / 请求证据 / 拒绝越权", 17)
f.save()
f = Figure(
    "rag",
    "两条链路：入库与检索增强问答",
    "文档 ID、版本、权限、原文位置与向量一起维护",
    475,
)
for y, labels in [
    (
        125,
        [
            ("文档解析", "清洗 · 表格 · 版本"),
            ("语义切块", "片段 + 原文定位"),
            ("索引更新", "关键词 + 向量"),
        ],
    ),
    (
        285,
        [
            ("问题与可信身份", "租户 · 对象权限"),
            ("授权检索与排序", "混合召回 → rerank"),
            ("证据生成与核验", "引用支持 / 缺失拒答"),
        ],
    ),
]:
    for i, (t, s) in enumerate(labels):
        x = 32 + 310 * i
        f.box(x, y, 275, t, s, h=85)
        if i < 2:
            f.line(x + 278, y + 42, x + 307, y + 42)
f.path("M790 212V250H480V282")
f.text(32, 433, "禁止未授权内容进入模型或共享缓存；相似度不是事实正确概率。", 17)
f.save()
f = Figure(
    "inference",
    "Prefill 与逐步 Decode",
    "缓存历史 Key / Value；不把缓存当成永久记忆",
    420,
)
f.box(32, 125, 230, "已知输入前缀", "一次处理多个位置", h=90)
f.box(350, 125, 235, "Prefill", "建立每层 KV cache", h=90)
f.box(675, 125, 250, "Decode 第 t 步", "读取缓存 → 生成 Token", h=90)
f.line(265, 170, 347, 170)
f.line(588, 170, 672, 170)
f.box(350, 280, 235, "KV cache", "追加第 t 步的 K/V", h=80)
f.path("M800 217V320H588")
f.path("M470 280V250H800V217")
f.text(32, 390, "前缀长度影响处理成本；输出长度影响串行生成；并发影响排队和显存。", 16)
f.save()
f = Figure(
    "agent-architecture",
    "采购调研 Agent 的能力与状态边界",
    "实线表示调用或数据流；虚线表示执行事件，所有动作经过业务授权",
    650,
)
f.box(32, 115, 230, "用户 / 客户端", "任务 · 补充输入 · 审批", h=90)
f.box(350, 115, 250, "Handler 与 Service", "身份 → 授权 → 状态转换", h=90)
f.box(685, 115, 240, "任务库与操作流水", "版本 · Checkpoint · Outbox", h=90)
f.line(265, 160, 347, 160)
f.line(603, 160, 682, 160)
f.box(350, 285, 250, "Runtime / Worker", "预算 · 租约 · 恢复 · 取消", h=90)
f.path("M475 208V282")
f.path("M805 208V330H603", True)
for x, t, s in [
    (32, "模型网关", "提示 · 模型版本 · 输出验证"),
    (350, "检索能力", "权限 · 文档版本 · 证据"),
    (685, "工具网关", "参数 · 审批 · 幂等"),
]:
    f.box(x, 460, 240, t, s, h=90)
f.path("M350 330H150V457")
f.line(475, 378, 475, 457)
f.path("M600 355H805V457")
f.text(32, 605, "日志与评测贯穿全链路；长期偏好、任务状态和模型上下文独立管理。", 17)
f.save()
f = Figure(
    "recovery",
    "外部动作未知时，先查询再推进",
    "工具成功 + 回执丢失 ≠ 操作未发生；无幂等能力则人工对账",
    590,
)
for x, t in [(125, "Service / Worker"), (480, "外部工具"), (820, "持久化任务库")]:
    f.text(x, 120, t, 18, anchor="middle")
    f.parts.append(f'<path d="M{x} 140V510" stroke="{MIST}" stroke-dasharray="5 6"/>')
for y, a, b, t in [
    (180, 125, 820, "记录待执行操作 + Outbox"),
    (250, 125, 480, "同一 operation_id 发起调用"),
    (320, 480, 125, "回执丢失：结果 UNKNOWN"),
    (390, 125, 480, "查询 / 幂等重放，获取原结果"),
    (465, 125, 820, "保存回执，推进 COMPLETED"),
]:
    f.line(a, y, b, y, y == 320)
    f.text(min(a, b) + 12, y - 13, t, 15)
f.text(32, 555, "不能查询且不能幂等 → 停止自动重试，进入人工核查。", 17)
f.save()
print("Generated", len(list(P.glob("*.svg"))), "SVG diagrams")

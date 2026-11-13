"""Concrete rank arithmetic and crash windows, rather than generic phase boxes."""

from .svg_canvas import BLUE, Canvas


def scenes(key: str, language: str) -> list[tuple[str, Canvas]]:
    zh = language == "zh"

    def t(a, b):
        return a if zh else b

    if key == "l02":
        c = Canvas(
            t(
                "RRF 如何融合：只加排名倒数，不相加原始分数",
                "RRF fusion: add reciprocal ranks, not raw scores",
            ),
            t(
                "虚构排名，k=60；重排结果为机制示例，不是模型实测。",
                "Synthetic ranks, k=60; reranking is illustrative, not a model benchmark.",
            ),
            720,
        )
        c.box(
            32,
            110,
            1136,
            85,
            t(
                "查询：比较含运费的总价 → 先限定当前租户、版本与访问范围",
                "Query: compare delivered totals → filter tenant, version and access first",
            ),
        )
        columns = [
            (32, "BM25"),
            (410, t("向量召回", "Dense retrieval")),
            (788, t("RRF 融合", "RRF fusion")),
        ]
        values = [
            ["1 · A", "2 · B"],
            ["1 · B", "2 · D", "3 · A"],
            [
                "B: 1/62 + 1/61 = .032522",
                "A: 1/61 + 1/63 = .032266",
                "D: 0 + 1/62 = .016129",
            ],
        ]
        for i, (x, label) in enumerate(columns):
            c.rect(x, 230, 350, 190)
            c.text(x + 16, 263, label, width=27)
            for n, value in enumerate(values[i]):
                c.text(x + 16, 310 + n * 35, value, size=19, width=34)
        # Both retrievers receive the scoped query independently; BM25 is not
        # an input to dense retrieval. Their ranked lists meet only at fusion.
        c.path("M207 198V224")
        c.path("M585 198V224")
        c.path("M207 423V435H963V424")
        c.path("M760 320H781")
        c.path("M1110 423V473H300V484")
        c.text(
            45,
            457,
            t(
                "没有入榜的文档贡献 0；同一文档跨召回器累加。",
                "Absent documents contribute zero; merge by document ID.",
            ),
            width=96,
            size=21,
        )
        c.box(
            32,
            490,
            530,
            120,
            t(
                "Cross-encoder：query + 候选正文",
                "Cross-encoder: query + candidate text",
            ),
            t(
                "逐对评分 → 去重 → 取有限 Top-N",
                "Score pairs → deduplicate → bounded Top-N",
            ),
        )
        c.line(568, 550, 600, 550)
        c.box(
            608,
            490,
            560,
            120,
            t(
                "回答只引用证据；未知运费仍未知",
                "Answer from evidence; missing shipping stays unknown",
            ),
            t("排序靠前 ≠ 条款已完整", "High rank does not imply complete terms"),
        )
        c.text(
            32,
            663,
            t(
                "分开验收：Recall@K → 重排 nDCG/MRR → 引用支撑与回答完整性",
                "Evaluate separately: Recall@K → rerank nDCG/MRR → support and coverage",
            ),
            size=20,
            width=108,
        )
        return [("rank-trace", c)]
    if key == "a09":
        c = Canvas(
            t("重启之后，哪些代码会再运行？", "What runs again after recovery?"),
            t(
                "图状态恢复与历史重放不同；两者都不能替远端保证写入幂等。",
                "Graph checkpoints and history replay differ; remote effects still need deduplication.",
            ),
            740,
        )
        for x, label in [(32, "LangGraph"), (620, "Temporal")]:
            c.rect(x, 110, 550, 520)
            c.text(x + 16, 147, label, fill=BLUE)
        left = [
            t("State → approval 节点 → interrupt", "State → approval node → interrupt"),
            t("Checkpoint：State + pending node", "Checkpoint: State + pending node"),
            t("同 thread_id + Command(resume)", "Same thread_id + Command(resume)"),
            t("重新进入 approval 节点并核验", "Re-enter approval node and validate"),
            t("execute 节点：同 operation_id", "execute node: same operation_id"),
        ]
        right = [
            t("Workflow 等待批准 signal", "Workflow waits for approval signal"),
            t("历史记录：signal / timer / 结果", "History: signals / timers / results"),
            t("worker 重启 → 确定性重放", "Worker restarts → deterministic replay"),
            t(
                "已记录结果复用；未决活动调度",
                "Reuse recorded results; schedule pending Activity",
            ),
            t(
                "Activity 可重试：同 operation_id",
                "Activity may retry: same operation_id",
            ),
        ]
        for x, labels in [(48, left), (636, right)]:
            for i, label in enumerate(labels):
                y = 174 + i * 87
                c.box(x, y, 518, 66, label)
                if i < 4:
                    c.line(x + 259, y + 69, x + 259, y + 83)
        c.text(
            32,
            681,
            t(
                "外部动作成功但结果未记入：先查回执 / 同键去重；不可查询则人工核查。",
                "Remote success without a recorded result: query/deduplicate; otherwise reconcile manually.",
            ),
            size=21,
            width=106,
        )
        return [("replay-boundary", c)]
    return []

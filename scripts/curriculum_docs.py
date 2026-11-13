"""Keep public outlines, entry maps and manual-page H1s aligned with the manifest."""

import json
import re
from pathlib import Path

from curriculum import ROOT, group_label, section_label


def write(path: Path, text: str) -> None:
    if not path.exists() or path.read_text() != text:
        path.write_text(text)


def render(manifest: list[dict]) -> None:
    by_id = {p["id"]: p for p in manifest}
    chinese = json.loads((ROOT / "site/i18n/zh.json").read_text())
    outline = [
        "# 完整课程目录",
        "入门理解模型，进阶掌握Agent机制，高级按具体设计问题构建多Agent系统。编号与导航同源；Skills旧总览已合并到专题。",
    ]
    for group, title in enumerate(chinese["groups"]):
        outline.append("## " + group_label(group, title))
        pages = [p for p in manifest if p["group"] == group]
        for item in [p for p in pages if not p.get("section")]:
            outline.append(f"- [{item['title']}]({item['source']})")
        for section, label in chinese["sections"].items():
            children = [p for p in pages if p.get("section") == section]
            if not children:
                continue
            outline.append("### " + section_label(children, label))
            for item in children:
                if re.fullmatch(r"a\d{2}", item["id"]):
                    outline.append(f'<a id="chapter-{int(item["id"][1:]):02}"></a>')
                if item["id"] == "skill05":
                    outline.append('<a id="chapter-10"></a>')
                outline.append(f"- [{item['title']}]({item['source']})")
    write(ROOT / "HANDBOOK.md", "\n\n".join(outline) + "\n")
    for lang in ["zh", "en"]:
        zh = lang == "zh"
        ui = json.loads((ROOT / f"site/i18n/{lang}.json").read_text())

        def link(key, zh=zh, lang=lang):
            p = by_id[key]
            source = Path(p["source" if zh else "en_source"])
            relative = source.relative_to(Path("docs") / lang).as_posix()
            return f"[{p['title' if zh else 'en_title']}]({relative})"

        home = [
            "# " + by_id["index"]["title" if zh else "en_title"],
            "先理解机制，再按任务边界、协作契约、状态、权限和恢复等具体问题完成架构设计。训练仅提供代码，不实际训练。"
            if zh
            else "Learn mechanisms, then design around task boundaries, contracts, state, authority and recovery. Training code is supplied without running training.",
            "![学习路径](../../assets/illustrations/learning-journey.jpg)"
            if zh
            else "![Learning journey](../../assets/illustrations/learning-journey.jpg)",
            "## 学习阶段" if zh else "## Learning stages",
        ]
        for group, key in [(1, "f01"), (2, "l01"), (3, "ma01"), (4, "studio")]:
            home.append(
                f"- **{group_label(group, ui['groups'][group])}** · {link(key)}"
            )
        home += [
            "## 从哪些方面设计多 Agent"
            if zh
            else "## Dimensions of multi-Agent design",
            "| 模块 | 该做出的设计 |" if zh else "| Module | Design decision |",
            "|---|---|",
        ]
        outputs = {
            "task-design": (
                "任务验收、拆分理由、唯一责任者和产物契约",
                "Acceptance, split rationale, owners and artifact contracts",
            ),
            "collaboration": (
                "控制拓扑、路由、消息信封、因果与交接条件",
                "Control topology, routing, envelopes, causation and handoff",
            ),
            "sessions": (
                "身份/会话/任务/run的生命周期与续接",
                "Identity/session/task/run lifetimes and resumption",
            ),
            "state-consistency": (
                "产物版本、状态所有权、CAS和冲突处理",
                "Artifact versions, ownership, CAS and conflict handling",
            ),
            "permissions": (
                "主体、动作、对象、策略事实和受限委派",
                "Principal, action, object, policy facts and scoped delegation",
            ),
            "approvals": (
                "具体动作审批、失效、单次消费和回执",
                "Exact-action approval, invalidation, consumption and receipts",
            ),
            "execution-design": (
                "DAG、并发/预算、背压、失败恢复与补偿",
                "DAGs, concurrency/budget, backpressure, recovery and compensation",
            ),
            "assurance": (
                "完整任务对照、轨迹、告警、安全与发布门槛",
                "Whole-task comparisons, tracing, alerts, safety and release gates",
            ),
            "deployment": (
                "进程/服务隔离、容量、伸缩及完整装配",
                "Isolation boundaries, capacity, scaling and assembly",
            ),
        }
        for section, pair in outputs.items():
            page = next(
                p for p in manifest if p["group"] == 3 and p.get("section") == section
            )
            home.append(f"| {link(page['id'])} | {pair[0 if zh else 1]} |")
        home += [
            "## 进阶机制与高级设计怎样衔接"
            if zh
            else "## Intermediate concepts versus advanced design",
            "Agent基础、上下文、函数调用、MCP、Skills、状态记忆都属于进阶；高级设计复用这些能力来回答系统组合问题。Function Calling表达模型提议，MCP连接能力，Skills复用方法，三者可以在同一条链中组合。"
            if zh
            else "Agent foundations, context, Function Calling, MCP, Skills and memory belong to the intermediate stage. Advanced design combines them. Function Calling expresses proposals, MCP connects capabilities and Skills package methods.",
            link("fc02") + " · " + link("skill01") + " · " + link("code-guide"),
            "## 怎样检验理解" if zh else "## Check understanding",
            "改变租户、金额、证据版本或故障时点，说明哪一层拒绝、哪些状态保留、怎样恢复；提交具体产物与取舍，不以框架名字和漂亮总图代替设计。"
            if zh
            else "Change tenant, amount, evidence version or failure timing; identify the rejecting boundary, retained state and recovery path. Produce concrete contracts and tradeoffs, not framework names alone.",
        ]
        write(ROOT / f"docs/{lang}/index.md", "\n\n".join(home) + "\n")
        for item in manifest:
            if item.get("kind"):
                continue
            path = ROOT / item["source" if zh else "en_source"]
            if item["id"] == "index":
                continue
            text = path.read_text()
            text = re.sub(
                r"^# .*", "# " + item["title" if zh else "en_title"], text, count=1
            )
            write(path, text)

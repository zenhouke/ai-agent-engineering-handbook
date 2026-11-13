"""Personal studio diagrams: business gates and independently scoped runtimes."""

from .studio_system import architecture as system_architecture
from .svg_canvas import Canvas


def draw(key: str, c: Canvas, data: dict, ui: dict) -> bool:
    if key != "studio":
        return False
    labels = data["steps"]
    c.chain(labels, y=125)
    zh = data["language"] == "zh"
    c.box(
        35,
        325,
        520,
        110,
        "Host / Services",
        "权限、审批、资金、状态" if zh else "Authority, approvals, funds, state",
    )
    c.box(
        645,
        325,
        520,
        110,
        "Worker / Adapters",
        "精确动作、原生回执" if zh else "Exact actions, native receipts",
    )
    c.line(295, 230, 295, 319)
    c.line(561, 380, 639, 380)
    c.path("M905 319V270H1035V230")
    return True


def scenes(language: str) -> list[tuple[str, Canvas]]:
    def t(zh: str, en: str) -> str:
        return zh if language == "zh" else en

    result = [("system-architecture", system_architecture(language))]
    c = Canvas(
        t(
            "运行部署：谁持有状态，谁持有凭据",
            "Deployment: state and credential owners",
        ),
        "Studio runtime boundaries",
        760,
    )
    rows = [
        (
            "Web / Telegram / QQ",
            t("操作者与客户消息入口", "Operator and customer messages"),
        ),
        (
            "Node Gateway / Broker",
            t("可信身份、配置、协议适配", "Trusted identity, config, codecs"),
        ),
        (
            "Rust Studio Worker",
            t(
                "冻结流程、调度、审批、owner fencing",
                "Frozen flow, scheduling, approval, fencing",
            ),
        ),
        (
            "PostgreSQL",
            t(
                "订单、run、审批、产物、动作账本",
                "Orders, runs, approvals, artifacts, ledger",
            ),
        ),
    ]
    for i, (label, note) in enumerate(rows):
        y = 90 + i * 145
        c.box(35, y, 610, 100, label, note)
        if i < 3:
            c.line(340, y + 105, 340, y + 138)
    c.box(
        745,
        235,
        420,
        115,
        "Browser Worker",
        t("每账号独立 profile / 平台凭据", "Account profiles / platform credentials"),
    )
    c.box(
        745,
        425,
        420,
        115,
        "Task Execution Container",
        t(
            "任务文件、受限运行时、无平台凭据",
            "Task files, bounded runtime, no platform keys",
        ),
    )
    c.path("M651 418H700V292H739")
    c.path("M700 418V482H739")
    c.text(
        35,
        715,
        t(
            "关闭网页不终止后台任务；执行 Agent 不直接控制平台账号。",
            "Closing the UI does not end jobs; execution agents do not own platform accounts.",
        ),
        size=21,
        width=104,
    )
    result.append(("deployment", c))

    c = Canvas(
        t("商业闭环：四个独立门禁", "Commercial lifecycle: four independent gates"),
        "Business approvals cannot be bypassed by run approval",
        810,
    )
    stages = [
        (
            t("发现与身份去重", "Discover / deduplicate"),
            t("平台 + 账号 + 原生订单 ID", "Platform + account + native order ID"),
        ),
        (
            t("需求与报价冻结", "Freeze scope / quote"),
            t("G1 人工确认报价与对外动作", "G1 Approve quote and external action"),
        ),
        (
            t("开工条件校验", "Validate start conditions"),
            t(
                "G2 客户确认 + 已核验启动金",
                "G2 Customer confirmation + verified deposit",
            ),
        ),
        (
            t("隔离执行与产物审查", "Execute / review artifacts"),
            t(
                "G3 运行授权；产物绑定内容哈希",
                "G3 Run authority; artifact content hash",
            ),
        ),
        (
            t("结算与精确交付", "Settle / deliver exact output"),
            t(
                "G4 足额结算 + 对具体产物批准",
                "G4 Full settlement + exact artifact approval",
            ),
        ),
    ]
    for i, (label, note) in enumerate(stages):
        y = 90 + i * 130
        c.box(35, y, 400, 90, label)
        c.box(525, y, 640, 90, note)
        c.line(441, y + 45, 519, y + 45)
        if i < 4:
            c.line(235, y + 95, 235, y + 123)
    c.text(
        35,
        775,
        t(
            "任何报价、客户或产物变更，都重新校验相应门禁；消息“已付款”不是收款证据。",
            "Changed scope/customer/artifact reopens gates; a payment claim is not verified funds.",
        ),
        size=20,
        width=108,
    )
    result.append(("gates", c))

    c = Canvas(
        t(
            "会话、任务与账号：独立生命周期",
            "Sessions, tasks and accounts: separate lifetimes",
        ),
        "Identifiers are locators, not permissions",
        660,
    )
    labels = [
        (
            t("应用登录会话", "Application session"),
            t(
                "主体 / 工作区 / 过期 / 撤销",
                "Principal / workspace / expiry / revocation",
            ),
        ),
        (
            t("Agent 对话线程", "Agent conversation"),
            t("上下文 / 摘要 / 消息因果", "Context / summary / message causation"),
        ),
        (
            t("平台浏览器会话", "Platform browser session"),
            t("账号 / profile / 加密凭据", "Account / profile / encrypted credentials"),
        ),
        (
            t("任务执行环境", "Task execution environment"),
            t(
                "订单 / run / 文件版本 / checkpoint",
                "Order / run / file versions / checkpoint",
            ),
        ),
    ]
    for i, (label, note) in enumerate(labels):
        x, y = 35 + i % 2 * 600, 100 + i // 2 * 225
        c.box(x, y, 530, 150, label, note)
    c.text(
        35,
        595,
        t(
            "交接信封显式关联 workspace / order / run / actor / artifact；每次使用重新授权。",
            "Handoff links workspace / order / run / actor / artifact; authorize each use.",
        ),
        size=21,
        width=102,
    )
    result.append(("sessions", c))

    c = Canvas(
        t(
            "失败恢复：执行权与外部结果分别处理",
            "Recovery: ownership and external outcomes",
        ),
        "Fencing does not prove the remote effect did not happen",
        690,
    )
    c.box(
        35,
        100,
        350,
        115,
        t("Worker 丢失", "Worker lost"),
        "run / journal / owner token",
    )
    c.box(
        510,
        100,
        655,
        115,
        t("校验租约与 fencing token", "Validate lease and fencing token"),
        t("旧 owner 不得继续提交", "Reject writes from obsolete owners"),
    )
    c.line(391, 158, 504, 158)
    c.box(
        35,
        340,
        510,
        145,
        t("安全 checkpoint", "Safe checkpoint"),
        t("恢复同一 run 与冻结配置", "Resume same run and frozen config"),
    )
    c.box(
        655,
        340,
        510,
        145,
        "UNKNOWN / RecoveryRequired",
        t("对账原生回执；禁止盲重发", "Reconcile native receipt; no blind resend"),
    )
    c.path("M820 221V270H290V334")
    c.path("M820 270H910V334")
    c.text(
        35,
        565,
        t(
            "接单、联系、交付：唯一 operation + payload hash；重复事件可重放，未知商业动作须核对。",
            "Accept/contact/deliver: unique operation + payload hash; replay events, reconcile unknown effects.",
        ),
        size=21,
        width=102,
    )
    c.text(
        35,
        635,
        t(
            "Outbox 解决本地状态与事件一致性，不能单独保证远端恰好一次。",
            "Outbox couples local state and events; it cannot guarantee remote exactly-once.",
        ),
        size=21,
        width=102,
    )
    result.append(("recovery", c))
    return result

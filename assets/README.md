# 视觉资产目录与格式选择

| 用途 | 格式 | 维护方式 |
|---|---|---|
| 架构总览、部署拓扑、多 Agent 协作与治理设计 | 高清PNG，宽2400像素 | 绘图源码确定性输出，保留准确的节点、连线与文字 |
| 场景、图像输入示例与概念插画 | PNG / JPEG | 选用实际图片或生成图片，检查后记录来源和用途 |
| 实际操作或界面效果 | PNG截图 | 从可运行页面真实操作后截图，明确数值与状态 |
| 公式、矩阵、计算机制与交互原理 | SVG | 保留矢量清晰度，交互演示使用网页内联图形 |

不统一把所有内容画成SVG，也不把需要精确表达的架构交给图片模型随意补字或改连线。AI生成的场景不是实际产品截图，也不是训练/评测数据；正文有对应说明。

```text
assets/
├── illustrations/                  # 场景图片与概念插画
│   ├── learning-journey.jpg
│   ├── f05/visual-input.png
│   ├── l02/evidence-desk.png
│   └── studio/solo-studio.png
├── screenshots/f07/{zh,en}/        # 中英文注意力互动页面真实截图
├── diagrams/
│   ├── overview/                   # 手工维护的全局图
│   ├── foundations/f01/zh/         # 入门：课程 → 语言，主要使用SVG
│   ├── intermediate/mcp/mcp01/en/  # 进阶：专题 → 课程 → 语言
│   ├── architecture/permissions/auth01/zh/ # 高级架构：PNG
│   └── projects/studio/en/         # 项目架构：PNG
├── manifest.json                   # 自动生成的课程、语言、图与代码映射
└── media.json                      # 图片来源、生成提示词与截图条件
```

每课目录使用 `problem`、`mechanism`、`selection`、`solution-1` 等局部文件名；专题推演使用 `deployment` 等有具体含义的名称。同一课的中文和英文并列，不再把所有课程铺在一个语言目录。目录从课程清单推导。

绘图源集中在 `scripts/diagrams/`，文字与场景图引用维护在 `site/lessons/`。运行 `python3 scripts/build_site.py` 同步图、Markdown和站点。不要只修改生成图；PNG从同一绘图源输出，无需另外保存一套中间SVG。

PNG导出调用 `resvg_py` 语言库，不启动外部渲染CLI。字体使用Noto Sans CJK；Docker与CI自动安装。独立构建时安装 `fonts-noto-cjk`，或用 `HANDBOOK_FONT_FILE` 指向已安装的字体文件。临时哈希缓存位于 `.artifacts/`，不纳入版本管理；字体、绘图源或渲染版本改变时重新生成。

生成图保留在仓库，使Markdown直接显示图片。构建会清理已移除课程/旧格式的生成图和 `_site/` 过期产物；检查会拒绝根目录散图、无归属图、错误课程目录、架构SVG、低分辨率架构PNG及源站资产不一致。

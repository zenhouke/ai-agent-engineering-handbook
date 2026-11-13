## 在架构中找准职责

| 部件 | 保存什么 | 决定什么 |
|---|---|---|
| Prompt | 本次任务指令与输入 | 当前轮要做什么 |
| Skill | 可复用方法、条件、资源 | 怎样完成某类专业任务 |
| Function Calling | 模型工具定义及调用提议 | 模型建议调用哪项能力、参数是什么 |
| MCP | Client/Server 能力与消息契约 | 能力怎样发现和交换 |
| 工作流 / Runtime | 任务状态、依赖、预算、回执 | 当前允许执行哪一步、失败怎样继续 |

这不是五种互斥产品。报价审查可以加载一个 Skill，再由模型提出 read_quote，Host 校验后使用 MCP 或直接 SDK；最后由确定性校验器验收报告。对一个很短的临时要求，普通 Prompt 已足够；对固定计算，直接函数比多一轮模型选择更合适。

**贯穿案例：** A 单价180分、运费未知，B 单价170分、运费80分。技能教会保留未知，工具提供证据，程序计算总价；本报告契约在所有总价已知前不宣布最便宜。技能不会让基础模型参数发生变化。


依据：[Agent Skills Specification](https://agentskills.io/specification), [Agent Skills Host Integration](https://agentskills.io/client-implementation/adding-skills-support)。

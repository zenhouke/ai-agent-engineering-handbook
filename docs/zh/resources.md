# 4.4 参考课程：带着问题阅读

本课程参考其他教材的教学组织方式，重新编写讲解、数值例子和图。下表说明借鉴什么，以及阅读之后应该产出什么；只看目录不等于完成项目实践。

## 基础主线

| 资料 | 适合什么时候读 | 本课程借鉴的组织方式 | 阅读产物 |
|---|---|---|---|
| [Dive into Deep Learning](https://d2l.ai/chapter_preface/index.html) | 数学到深度学习阶段 | 将数学预备知识、模型机制与例子顺序衔接 | 手算线性层和梯度，解释验证集作用 |
| [Neural Networks: Zero to Hero](https://github.com/karpathy/nn-zero-to-hero) | 神经网络与语言模型阶段 | 从小计算图和小语言模型逐步扩大复杂度 | 跟踪一个数值从前向到反向的变化 |
| [LLM Cookbook](https://github.com/datawhalechina/llm-cookbook) | 进入应用开发时 | 区分基础必修和按问题选择的专题 | 为提示、RAG、微调分别写适用条件 |
| [Hello-Agents](https://github.com/datawhalechina/hello-agents) | 已理解模型与工具之后 | 从智能体原理推进到框架和系统构建 | 对比固定工作流与自主工具选择 |

以上入口和课程组织在 2026-11-13 阅读核对；不代表已执行其全部 Notebook 或审核全部内容。原有 Agent 资料索引中的历史核验另见仓库保留记录，不将历史日期伪装为本次重新核验。

## 技术机制的原始资料

| 资料 | 解决什么问题 | 本课对应问题 |
|---|---|---|
| [Attention Is All You Need](https://arxiv.org/abs/1706.03762) | 注意力与 Transformer 的原始架构 | Q/K/V、掩码、多头、位置和 Encoder–Decoder |
| [LoRA 原论文](https://arxiv.org/abs/2106.09685) | 低秩参数适配 | 固定基座与低秩更新为何能减少训练参数 |
| [D2L：Self-Attention and Positional Encoding](https://d2l.ai/chapter_attention-mechanisms-and-transformers/self-attention-and-positional-encoding.html) | 自注意力与位置关系 | 不提供位置时为什么难以表达顺序 |
| [Building Effective Agents](https://www.anthropic.com/research/building-effective-agents) | 工作流、动态编排与取舍 | 何时需要自主决策，何时保持固定路径 |

这些资料用于技术背景和教学方法参考。本文里的采购情节、计算例子、状态表与教学图为独立编写。文章年代、模型环境与当前工程实现可能不同，机制解释不等于框架版本使用保证。

## 用主流机制解决具体问题

| 问题 | 本课程采用的方案 | 官方资料 |
|---|---|---|
| 不知道参数怎样影响损失 | 自动求导与计算图 | [PyTorch autograd](https://docs.pytorch.org/tutorials/beginner/basics/autogradqs_tutorial.html) |
| 工具任务需要依据观察继续行动 | ReAct 式交错决策与外部动作 | [ReAct 原论文](https://arxiv.org/abs/2210.03629) |
| 关键词与向量排名分数不在同一尺度 | RRF 排名融合 | [Elasticsearch RRF 说明](https://www.elastic.co/docs/reference/elasticsearch/rest-apis/reciprocal-rank-fusion) |
| 表格预测先选什么基线 | 逻辑回归、树与集成，独立验证 | [scikit-learn 监督学习](https://scikit-learn.org/stable/supervised_learning.html) |
| 微调参数和内存开销大 | LoRA 低秩适配；与 SFT、量化区分 | [PEFT LoRA 概念](https://huggingface.co/docs/peft/main/en/conceptual_guides/lora) |
| 不知道用固定流程还是自主循环 | 路由、并行、规划执行、反馈改进 | [LangGraph 工作流与 Agent](https://docs.langchain.com/oss/python/langgraph/workflows-agents) |
| 长任务需要暂停与恢复 | Checkpointer、线程状态与持久化 | [LangGraph Persistence](https://docs.langchain.com/oss/python/langgraph/persistence) |
| 长期记忆与当前任务混用 | 分别管理短期状态和长期记录 | [Memory 概念](https://docs.langchain.com/oss/python/concepts/memory) |
| 工具接入方式各不相同 | MCP 的能力发现与调用边界 | [MCP 架构](https://modelcontextprotocol.io/docs/2026-07-28/learn/architecture) |
| 推理缓存占用高、并发受限 | KV cache 管理与分页注意力机制 | [vLLM Paged Attention](https://docs.vllm.ai/en/latest/design/paged_attention/) |
| 跨进程长流程需要持久执行 | 工作流执行、事件与 Worker 的分工 | [Temporal Workflow Execution](https://docs.temporal.io/workflow-execution) |

这些是机制和实现入口，不是要求同时安装的技术栈。PEFT 链接指向 main 文档，框架页面可能随版本变化；具体已安装和执行的 SDK/框架范围见配套代码说明，未执行模型训练。

## 阅读方法

先提出一个窄问题，例如“为什么 checkpoint 不能单独防止外部重复执行”。阅读一段机制说明，画一条正常路径与失败路径，再写出你会采用和拒绝的设计。每次只推进一个问题，避免同时安装多个解决同一问题的框架。

上游内容、代码、图片和权重有各自许可。这里提供阅读入口，不转存第三方课程全文或图片，也不替仓库所有者决定本仓库的原创许可。

## MCP 版本与可靠执行专题依据（2026-11-13）

- [MCP 当前版本与兼容](https://modelcontextprotocol.io/docs/2026-07-28/learn/versioning)：逐请求声明版本、可选预先发现，与旧初始化握手区分。
- [官方 Python SDK 入门](https://py.sdk.modelcontextprotocol.io/get-started/)：MCPServer、Client 与无网络内存协议测试；本课程固定 mcp==2.3.0。
- [LangGraph 中断](https://docs.langchain.com/oss/python/langgraph/interrupts)：节点重入、thread_id 与 Command(resume=...)，不能把中断前副作用当作只执行一次。
- [Temporal Python 错误处理](https://docs.temporal.io/develop/python/best-practices/error-handling)：Activity 幂等、重试边界与超时。
- [AWS Transactional Outbox](https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/transactional-outbox.html)：同事务保存状态/待发事件，重复投递仍需幂等。

上述参考中的协议与 SDK 版本分开记录；本地验证范围以配套代码说明为准，不把内存测试或直接 Activity 调用当作部署验收。

## Skills 与模型工具接口依据（2026-11-13）

[Agent Skills 格式](https://agentskills.io/specification)用于包结构和字段；[Host 集成](https://agentskills.io/client-implementation/adding-skills-support)用于三层披露与激活；[技能产物评测](https://agentskills.io/skill-creation/evaluating-skills)用于成对对照。[Function Calling](https://developers.openai.com/api/docs/guides/function-calling)及[客户端工具调用](https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview)用于区分模型提议、应用执行和不同提供方的结果格式。Host 示例的绑定、哈希注册表和版本策略由本课程自行定义，不冒称跨产品统一标准。

## 架构设计维度与治理依据

- [OWASP 会话管理](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html)：身份、失效与撤销边界；本例应用会话不是浏览器登录实现。
- [Cedar 授权概念](https://docs.cedarpolicy.com/auth/authorization.html)、[OPA 策略](https://www.openpolicyagent.org/docs/policy-language)、[OpenFGA 授权模型](https://openfga.dev/docs/authorization-concepts)：区分策略求值、角色属性和关系模型。
- [OWASP 事务授权](https://cheatsheetseries.owasp.org/cheatsheets/Transaction_Authorization_Cheat_Sheet.html)：明确交易数据、服务端校验、时效和单次授权。
- [多Agent研究系统实践](https://www.anthropic.com/research/multi-agent-research-system)：任务分解、协调、评测和可靠性经验，不能把上游效果套用成本例收益。
- [OpenTelemetry Traces](https://opentelemetry.io/docs/concepts/signals/traces/)、[Saga 编排](https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/saga-orchestration.html)：链路关联与补偿机制。

## 个人工作室的多仓库对照（2026-11-13）

参考 ForgePilot 本地版本 `13d673c` 的订单、资金、审批与执行边界，再对照上游：

| 仓库 | 用来解决的问题 | 本课程的选择与限制 |
|---|---|---|
| [LangGraph](https://github.com/langchain-ai/langgraph) | 状态持久化与人工中断 | 显式续接；节点重入需要独立副作用幂等 |
| [Temporal Python SDK](https://github.com/temporalio/sdk-python) | 长业务流程、确定性与外部活动 | 持久执行候选；不与自建调度器同时持有执行历史 |
| [CrewAI](https://github.com/crewAIInc/crewAI) | 专职角色与受控流程组合 | 协作放在业务门禁内；角色名称不授予权限 |
| [Microsoft Agent Framework](https://github.com/microsoft/agent-framework) | 顺序、并发、交接与多语言编排 | 候选方案；[AutoGen](https://github.com/microsoft/autogen)已归档，只作历史参考 |
| [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk) | 能力发现与调用 | 固定SDK版本；订单授权由业务服务负责 |
| [Agent Skills](https://github.com/agentskills/agentskills) | 可复用方法与按需披露 | 冻结方法版本；不能替代当前计划和审批 |

核对上游 README、LangGraph interrupt 实现和 Temporal 确定性说明；没有把这些仓库全部安装或部署。工作室项目正文给出具体取舍与故障验收。参考阅读不等于复制第三方实现，也不代表 ForgePilot 依赖上述框架。

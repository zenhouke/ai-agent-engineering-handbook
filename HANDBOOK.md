# 完整课程目录

入门理解模型，进阶掌握Agent机制，高级按具体设计问题构建多Agent系统。编号与导航同源；Skills旧总览已合并到专题。

## 开始学习

- [学习地图：从入门到多 Agent 架构设计](docs/zh/index.md)

## 1 入门 · 模型原理

- [1.1 从一个预测问题认识 AI](docs/zh/foundations/01-map.md)

- [1.2 只学现在用得上的数学](docs/zh/foundations/02-math.md)

- [1.3 从数据到可信的机器学习实验](docs/zh/foundations/03-machine-learning.md)

- [1.4 神经网络为什么能学习非线性规则](docs/zh/foundations/04-neural-networks.md)

- [1.5 图像、序列与生成模型：选择合适的归纳偏置](docs/zh/foundations/05-modalities.md)

- [1.6 从字符计数走到语言模型](docs/zh/foundations/06-language-models.md)

- [1.7 手算注意力，再看 Transformer](docs/zh/foundations/07-transformer.md)

- [1.8 预训练、SFT、偏好优化与 LoRA](docs/zh/foundations/08-training.md)

## 2 进阶 · Agent 原理与应用

### 2.1 大模型应用

- [2.1.1 提示、结构化输出与工具契约](docs/zh/llm/01-prompting.md)

- [2.1.2 RAG：把检索与回答分别做对](docs/zh/llm/02-rag.md)

- [2.1.3 推理部署：延迟、吞吐、显存与评价](docs/zh/llm/03-inference.md)

### 2.2 Agent 基础控制流

<a id="chapter-01"></a>

- [2.2.1 LLM 与 Agent 基础：从“会回答”到“会办事”](docs/zh/agent/01.md)

<a id="chapter-02"></a>

- [2.2.2 Agent控制流：固定工作流与动态循环](docs/zh/agent/02.md)

### 2.3 上下文工程

<a id="chapter-03"></a>

- [2.3.1 Context Engineering：给研究员准备一张干净的办公桌](docs/zh/agent/03.md)

<a id="chapter-04"></a>

- [2.3.2 Context Compaction：不是删聊天，而是打包行李](docs/zh/agent/04.md)

### 2.4 函数调用

<a id="chapter-07"></a>

- [2.4.1 工具网关：从模型提议到受控执行](docs/zh/agent/07.md)

- [2.4.2 模型提议怎样变成实际函数调用？](docs/zh/tools/fc01.md)

- [2.4.3 与 MCP 的区别及完整衔接](docs/zh/tools/fc02.md)

### 2.5 MCP 能力接入

- [2.5.1 为什么需要协议，Host / Client / Server 各做什么？](docs/zh/mcp/mcp01.md)

- [2.5.2 Tools、Resources、Prompts 怎么配合？](docs/zh/mcp/mcp02.md)

- [2.5.3 发现、JSON-RPC 与一次完整工具调用](docs/zh/mcp/mcp03.md)

- [2.5.4 stdio、Streamable HTTP 与授权怎么选？](docs/zh/mcp/mcp04.md)

- [2.5.5 用官方 SDK 构建真实 Server 与 Client](docs/zh/mcp/mcp05.md)

- [2.5.6 接入 Agent：工具膨胀、错误恢复与版本迁移](docs/zh/mcp/mcp06.md)

### 2.6 Skills 方法与资源

- [2.6.1 方法、Prompt、工具与工作流各管什么？](docs/zh/skills/skill01.md)

- [2.6.2 把专业方法写成可维护的技能包](docs/zh/skills/skill02.md)

- [2.6.3 发现、激活、按需加载与上下文生命周期](docs/zh/skills/skill03.md)

- [2.6.4 工具绑定、MCP 接入与权限交集](docs/zh/skills/skill04.md)

<a id="chapter-10"></a>

- [2.6.5 多技能组合、产物契约与重规划](docs/zh/skills/skill05.md)

- [2.6.6 触发评测、消融对照与版本回归](docs/zh/skills/skill06.md)

### 2.7 状态与记忆

<a id="chapter-05"></a>

- [2.7.1 短期记忆：断电以后，订单不能失忆](docs/zh/agent/05.md)

<a id="chapter-06"></a>

- [2.7.2 长期记忆：记住客户，不要替客户编历史](docs/zh/agent/06.md)

## 3 高级 · Agent 架构设计

### 3.1 任务与职责设计

- [3.1.1 任务分解、Agent 职责与产物所有权](docs/zh/architecture/ma01.md)

### 3.2 协作拓扑与通信

<a id="chapter-08"></a>

- [3.2.1 协作拓扑：顺序、Supervisor 与 DAG](docs/zh/agent/08.md)

- [3.2.2 Agent 间通信、交接与消息契约](docs/zh/architecture/ma02.md)

### 3.3 会话、任务与运行实例

- [3.3.1 会话、对话、任务和运行实例的区别](docs/zh/governance/session01.md)

- [3.3.2 会话切换、并发续接与撤销](docs/zh/governance/session02.md)

### 3.4 共享状态与冲突裁决

- [3.4.1 共享状态、产物版本与冲突裁决](docs/zh/architecture/ma03.md)

### 3.5 权限策略与委派

- [3.5.1 RBAC、ABAC、ReBAC 怎样约束 Agent](docs/zh/governance/auth01.md)

- [3.5.2 策略执行点、缓存与多 Agent 委派](docs/zh/governance/auth02.md)

### 3.6 审批与受控执行

- [3.6.1 审批绑定什么：动作、证据、时效与审批人](docs/zh/governance/approval01.md)

- [3.6.2 审批撤销、单次消费与恢复边界](docs/zh/governance/approval02.md)

### 3.7 执行调度与故障恢复

<a id="chapter-09"></a>

- [3.7.1 Runtime 与 Harness：模型负责建议，系统负责兑现](docs/zh/agent/09.md)

- [3.7.2 DAG 调度、背压、预算与取消](docs/zh/architecture/ma04.md)

- [3.7.3 失败传播、重试、补偿与人工核查](docs/zh/architecture/ma05.md)

### 3.8 评测、监控与安全

<a id="chapter-11"></a>

- [3.8.1 评测、监控与安全：漂亮答案不等于可靠系统](docs/zh/agent/11.md)

- [3.8.2 怎样证明多 Agent 比单 Agent 更合适](docs/zh/architecture/ma06.md)

### 3.9 部署与完整装配

- [3.9.1 部署边界、容量、隔离与技术选型](docs/zh/architecture/ma07.md)

<a id="chapter-12"></a>

- [3.9.2 架构分层装配与集成验收](docs/zh/agent/12.md)

## 4 综合实践与资料

- [4.1 个人工作室：AI 接单到交付的多 Agent 架构](docs/zh/projects/personal-studio.md)

- [4.2 四个可选实验：把原理变成可观察结果](docs/zh/projects/02-labs.md)

- [4.3 配套代码与验证边界](docs/zh/projects/03-code-guide.md)

- [4.4 参考课程：带着问题阅读](docs/zh/resources.md)

- [4.5 新手随手词典](GLOSSARY.md)

# 4.3 配套代码与验证边界

训练相关内容提供参考实现，不要求实际训练模型。每课的“参考代码”可展开阅读，保持图、张量形状、函数与解决方案对应。

## 从原理到代码

| 阶段 | 已提供的实现 | 阅读时重点检查 |
|---|---|---|
| 初级原理 | 任务契约、自动求导、分类 Pipeline、MLP、CNN、Bigram | 输入输出、训练/推理区别、数据边界 |
| 大模型机制 | 因果 Decoder Block、LoRA 层、KV 容量估算 | mask 方向、维度、冻结参数、内存口径 |
| 应用方案 | 输出校验、未知运费处理、RRF 融合 | 结构不等于事实、授权候选、排名分数 |
| Agent 范式 | ReAct、Plan-and-Execute、有限 Reflection | 工具契约、停止条件、计划校验 |
| 高级架构 | 上下文预算、Compaction、版本化 Checkpoint、记忆范围、并发、审批与分层装配 | 谁决策、谁授权、谁存状态、失败由谁接管 |

## 哪些代码需要依赖

自动求导、MLP、CNN、Decoder 和 LoRA 使用 PyTorch；分类 Pipeline 使用 scikit-learn。它们是训练或模型结构的参考代码，不在文档构建和测试中调用训练函数。可选依赖采用范围声明，实际使用时应按设备和 Python 环境锁定兼容版本；这里未验证所有依赖版本组合。

其他机制示例以 Python 标准库为主。模型与工具通过可注入函数表示，测试可使用确定性替身，不需要真实模型请求、模型权重或付费服务。

另附完整分类训练参考：读取独立训练/验证 CSV → 仅训练集拟合标准化 → 2→2→1 MLP → 批次前向与反向 → 验证模式计算指标 → 保存最佳权重与预处理参数。它只提供代码，没有训练结果或效果承诺。

## 验证分成三层

| 层次 | 可以证明 | 不能证明 |
|---|---|---|
| 语法与静态检查 | 文件可解析、基本代码规范通过 | PyTorch/scikit-learn 在具体环境运行正确 |
| 非训练机制测试 | 方案中的预算、授权、状态、排名融合等指定性质 | 模型质量、真实工具性能与生产可靠性 |
| 学习者自行运行模型代码 | 在所选环境观察张量与训练过程 | 自动代表其他硬件、数据或配置 |

文档中的分数、矩阵与轨迹均为教学例子。代码是对应机制的参考实现，不能把单层 LoRA、一个 Decoder Block 或有界工具循环称为完整训练平台或生产 Agent。

## MCP、框架恢复与事务示例

MCP 使用 **协议 2026-07-28、官方 Python SDK 2.3.0**。这与 SDK v1 的 FastMCP 导入及旧 initialize 握手不同；六讲分别标注迁移边界。依赖与非训练检查可独立安装/执行：

```sh
python3 -m pip install -r requirements-mcp.txt -r examples/requirements-architecture.txt
python3 -m unittest discover -s tests -p 'test_mcp_sdk.py' -v
python3 -m unittest discover -s tests -p 'test_workflow_frameworks.py' -v
python3 -m unittest discover -s tests -p 'test_outbox_recovery.py' -v
```

| 示例 | 实际验证 | 保留边界 |
|---|---|---|
| MCP Client/Server | 真实 SDK 内存及 stdio 发现、三类原语、作用域拒绝、Host 校验 | 已验证内存与 stdio；未验证公网 HTTP、OAuth 或真实模型 |
| LangGraph | 审批前不执行；同 thread_id resume；错误审批被拒绝 | InMemorySaver 不是跨进程持久化恢复 |
| Temporal | SDK 装饰器/模块导入、Activity 向适配器传稳定操作键 | 未启动服务/Worker，未验证事件重放、实际重试与部署 |
| SQLite Outbox | 状态与事件同事务；唯一键冲突回滚；丢失成功响应后核查；重复投递取同一回执 | 远端是可注入幂等替身；未实现 broker、租约调度或真实采购 |

高级 Runtime 课分别解释 LangGraph、Temporal、数据库加队列保存什么、重跑什么、谁负责并发和外部幂等；个人工作室项目组合业务门禁、治理事务与 UNKNOWN 对账机制。它们是可审查的机制实现，各自有明确验证范围。

## Skills 与 Function Calling 专题

实际技能包遵循 Agent Skills 的元数据/正文/资源结构；Host 的版本摘要、绑定与任务权限为示例应用约定，不是通用格式授权。可选依赖为 PyYAML 6.0.3；MCP 集成沿用官方 SDK 2.3.0。格式、辅助函数、按需披露、去重、路径拒绝、摘要变更、任务隔离与参数/权限契约有独立测试。

```sh
python3 -m pip install -r requirements-skills.txt -r requirements-mcp.txt
python3 -m unittest discover -s tests -p 'test_skill_host.py' -v
python3 -m unittest discover -s tests -p 'test_function_calling.py' -v
```

Function Calling 示例使用固定模型提议，真实 MCP Client/Server 负责只读能力调用；未发送付费模型请求，没有模型选择增益数据，不执行训练。Host 仅在任务会话内保存激活状态，不声称完成OS沙箱、跨进程持久恢复或技能发布平台。

## 会话、权限、审批与多 Agent 设计验证

新增局部代码覆盖应用会话/任务/run分离、当前角色与对象策略、委派范围、精确动作审批、原子消费，以及多Agent职责、消息信封、共享事实冲突、DAG调度、失败补偿提议、成对任务指标和容量估算。运行：

```sh
python3 -m unittest discover -s tests -p 'test_governance.py' -v
python3 -m unittest discover -s tests -p 'test_multi_agent_design.py' -v
```

SQLite测试包含两个独立连接竞争消费同一审批与唯一键失败回滚。新网络副作用没有执行，未部署OIDC、浏览器登录、消息broker、策略引擎或生产worker。代码按明确条件展示机制，不将局部测试当作多Agent协作收益。

页面、导航、目录的编号来自同一清单；分类和数字序列及H1一致性纳入站点检查。旧Skills总览从清单移除，旧URL跳转到组合与规划章节；源内容已归并。

## 个人工作室项目验证

工作室代码验证报价/运行审批分别校验、可信付款证据、报价与客户变更失效、有效期与权限版本、足额结算及精确产物交付。它是纯业务门禁契约，没有身份认证、审批消费或外部写入；这些职责由治理与 Outbox 示例分别展示。

```sh
python3 -m unittest discover -s tests -p 'test_studio_contracts.py' -v
```

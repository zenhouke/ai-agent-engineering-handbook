# 学习范围与验证方法

## 范围

课程从问题定义、必要数学和机器学习，推进到神经网络、语言模型、Transformer、适配、RAG、推理及 Agent 架构。中英文提供问题、图解、方案对照和参考代码；中文另有完整推导，英文补充笔记为精简版。入门、进阶和高级设计按当前目录组织，课号由目录层级统一生成。

图与例子用于解释机制；个人工作室案例是参考设计，四个离线实验是局部机制演示。这里不声称完成了大模型预训练、真实硬件推理基准或生产接单平台。小规模教学评测不能证明生产可靠性。

训练相关模块仅提供参考代码，进行语法与静态检查，不执行实际训练，也不声明张量库在所有设备和版本上的运行结果。非训练机制可用确定性模型/工具替身测试；其成功不等于真实模型或外部服务可靠。

## 检查的边界

构建检查确认内容可以生成网页。静态检查确认本地图片、链接、锚点、课程配对与图像结构。实验测试确认列明的数值和恢复性质。HTTP 检查确认运行态能返回产物。浏览器验收进一步检查真实布局、交互和图片显示。它们是不同层次的证据。

来源阅读核对不代表已运行上游所有项目。旧 sources.json 保存历史文件核验记录，本次参考课程页面另有核对日期。外部内容和软件接口可能更新，使用时需重新确认版本。

## 协议与恢复的独立验证

可选环境固定 MCP SDK 2.3.0、LangGraph 1.2.21、Temporal Python 1.36.0。MCP 使用真实内存及 stdio Client/Server；LangGraph 验证 interrupt/resume 与审批拒绝；Temporal 仅验证定义导入和直接 Activity 适配契约，未运行服务端重放或重试。Outbox 使用真实 SQLite 事务与确定性幂等远端替身，注入唯一键失败、成功响应丢失、重复投递、审批过期与载荷变更。

构建继续仅依赖 Markdown。未安装可选 SDK 时，对应测试显式跳过；独立 CI 作业安装固定依赖运行协议/框架测试。不能把跳过计为已验证，也不能把示例事务测试当作生产消息队列部署验收。

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

个人工作室项目参考 ForgePilot 本地 `13d673c` 的已核验实现及多个一手 GitHub 仓库；教学门禁包含报价/运行审批分离、付款凭据、版本失效、足额结算与产物绑定检查。未修改或重新部署 ForgePilot，未接真实平台商业操作，也未声称已实现完整工作室后端。

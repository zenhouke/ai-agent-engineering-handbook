## 同一个崩溃问题，三种恢复机制

**场景：** 调研已完成，审批要等一天；审批后远端创建草稿成功，响应在网络中丢失。重启后既要续接，也不能重复创建。

| 维度 | LangGraph + 持久化 Checkpointer | Temporal Workflow + Activity | 数据库 + Outbox + 队列 |
|---|---|---|---|
| 持久化什么 | 图状态、检查点、待执行节点/任务 | Workflow 事件历史与 Activity 结果/重试信息 | 自定义任务、审批、操作记录、Outbox、租约 |
| 怎样恢复 | 同一 thread_id 加载检查点，继续待执行工作 | SDK 重放历史重建 Workflow，再调度未完成工作 | worker 读取待处理记录，按版本领取并执行 |
| 会重跑什么 | 未完成节点；interrupt 所在节点恢复时会重新进入 | Workflow 代码会确定性重放；未确认 Activity 可重试 | 未确认消息会重复投递；领取/执行逻辑可能重跑 |
| 审批等待 | interrupt 保存位置，由可信入口发起 resume | signal/update 由可信入口发送，等待条件持久化 | approved 状态及事件由数据库事务维护 |
| 谁管外部幂等 | 业务适配器与远端；检查点不替它完成 | 业务适配器与远端；Activity 可执行多次 | 业务适配器与远端；消费去重不能替代远端去重 |
| 并发所有权 | 按选定存储/部署的并发契约设计，不能假设 thread_id 是锁 | 服务调度 Workflow/Activity 任务；外部系统仍须防重复效果 | 自建 CAS、租约、fencing；租约过期不等于旧 worker 停止 |
| 更适合 | 图式 Agent、模型/工具循环、人工中断 | 跨日流程、可靠活动调度、明确重试/超时 | 已有队列/数据库体系且愿意自行维护状态机 |

### 关键故障窗口：远端成功，本地还没记回执

1. 本地先持久化 `operation_id=op-42` 与请求指纹，再发请求。
2. 远端创建 `draft-42`，但网络响应丢失。本地只能记为 **UNKNOWN**，不能判断为“未创建”。
3. 恢复时按 `op-42` 查远端；查到后回填回执。支持幂等的远端也可用**同键、同载荷**取回同一结果。
4. 远端既不支持幂等也不可查询时，进入人工核查。重新分配 `op-43` 盲重试可能创建第二份。

`request_id` 只关联一次 RPC 的请求与响应；`operation_id` 标识一次业务动作，跨重启保持稳定。工作流引擎解决“编排怎么恢复”，不能凭空获得远端的恰好一次写入能力。

### LangGraph 中断为什么要分开节点

`interrupt()` 不是把 Python 调用栈永久冻结。恢复时节点会重新进入，因此中断之前的代码可能再执行。审批节点只计算/核验动作摘要；创建草稿放在独立节点，并使用稳定操作键。`InMemorySaver` 只适合测试，不能演示跨进程持久恢复。真实部署还需选定持久化 Checkpointer、状态迁移和并发写入策略。

### Temporal 为什么分 Workflow 与 Activity

Workflow 的条件、计时器、活动结果通过历史恢复；Workflow 代码须满足确定性重放要求。网络请求、数据库写入和随机外部结果放到 Activity。`start_to_close_timeout` 限制单次尝试，`schedule_to_close_timeout` 限制整个调度/重试窗口；重试策略不能把权限错误当瞬时网络错误。长活动还应设计 heartbeat 与取消响应；下方短调用参考没有实现长活动。

框架依据：[LangGraph 持久化](https://docs.langchain.com/oss/python/langgraph/persistence)、[中断恢复](https://docs.langchain.com/oss/python/langgraph/interrupts)、[Temporal Python 错误与重试](https://docs.temporal.io/develop/python/best-practices/error-handling)。

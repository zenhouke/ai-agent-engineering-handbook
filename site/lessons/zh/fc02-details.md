## 两个接口，处于不同层

| 维度 | Function Calling（本例客户端工具） | MCP |
|---|---|---|
| 两端 | 模型提供方接口 ↔ Host 应用 | MCP Client ↔ MCP Server |
| 主要内容 | 工具 schema、调用提议、模型工具观察 | 能力发现、工具/资源/模板、RPC 与传输 |
| 谁执行 | Host 分发到函数/SDK，也可转交 MCP | Server 调领域服务；Client 接结果 |
| 没有另一方能用吗 | 能，直接分发本地函数 | 能，普通程序可直接调用 SDK Client |
| 授权 | Host 与领域服务落实 | 认证/对象授权仍要落实 |

**共同出现的时序：** MCP list_tools → Host筛选工具并适配模型 schema → 模型 function_call → Host参数/对象检查 → Client tools/call → Server service → Host映射结果 → 原call_id的 function_call_output。MCP Server 不必知道这个调用原来来自哪个模型。

**不要混淆三个 ID：** provider call_id 关联模型观察；JSON-RPC id 关联一次 MCP 请求；operation_id 在业务层标识跨重试的同一写动作。前两者不会自动保证业务幂等。

本例复用真实 MCP SDK，但模型提议是固定测试输入。另一条直接 SDK 路径无需 MCP；固定工作流用 MCP 时也无需生成 Function Calling。Function Calling 与 MCP 的 schema 约束、错误层次及版本各自不同，必须在 Host 边界适配。


依据：[OpenAI Function Calling](https://developers.openai.com/api/docs/guides/function-calling), [MCP Architecture](https://modelcontextprotocol.io/docs/2026-07-28/learn/architecture)。

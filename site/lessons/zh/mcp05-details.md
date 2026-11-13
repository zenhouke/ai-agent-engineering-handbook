## 注册不是全部业务逻辑

示例暴露一个只读工具、一个资源、一个模板。MCP 注册层只绑定协议能力，handler 负责解析/错误映射，service 决定可读对象，repo 管虚构数据。

| 检查点 | 预期观察 |
|---|---|
| 发现工具 | 有 `read_quote`，`quote_id` 是必填字符串 |
| 调用 A | `unit_cents=180`，`shipping_cents=null`，不得伪造总价 |
| 调用范围外 B | 工具执行失败，不能读出其报价 |
| 读取 Resource | 返回 A 的文字上下文 |
| 获取 Prompt | 返回模板消息，不发送订单、不调用模型 |

本示例固定官方 `mcp==2.3.0`。v1 的 `from mcp.server.fastmcp import FastMCP` 不用于这份代码；v2 使用 `from mcp.server import MCPServer` 和 `from mcp import Client`。独立的 `fastmcp` 项目也不是这份依赖，不要混装教程 API。

内存连接使用真实 SDK 发现、参数验证与调用路径，不会启动子进程或开放端口。它不证明远程网络、OAuth、代理和其他 MCP Host 的兼容性；这些需要另做对应验收。

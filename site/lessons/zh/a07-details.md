## MCP 六讲：从协议到真实接入

[MCP 专题](../mcp/mcp01.md)：架构 → 三类原语 → 请求与版本 → 传输认证 → 真实服务端/客户端 → Host 适配。示例使用官方 SDK 2.3.0，通过内存 Client/Server 验证真实协议能力，不调用模型。


## 先区分模型侧与工具服务侧

[函数调用机制](../tools/fc01.md) · [Function Calling / MCP](../tools/fc02.md)：先看模型提议与Host执行，再看两层契约怎样衔接。MCP并不要求模型使用Function Calling，Function Calling也可直接分发本地函数。

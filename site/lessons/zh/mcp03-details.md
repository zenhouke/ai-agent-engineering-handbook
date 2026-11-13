## 看一条真实形状的当前请求

```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "method": "tools/call",
  "params": {
    "name": "read_quote",
    "arguments": {"quote_id": "A"},
    "_meta": {"io.modelcontextprotocol/protocolVersion": "2026-07-28"}
  }
}
```

SDK 负责完整元数据和序列化；这里突出与模型生成的 `{quote_id:A}` 参数之间的区别。`server/discover` 是服务端必须实现、客户端可选择先调用的方法；发现结果可缓存，但不能缓存成永久权限。

| 层次 | 例子 | 处理 |
|---|---|---|
| HTTP/传输 | 401、403、连接中断、响应格式错误 | 检查认证、代理、超时与版本头；写结果不明时先对账 |
| JSON-RPC | 未知方法、非法参数、版本不兼容 | 根据错误修正请求或选择兼容版本，不无限重试 |
| 工具执行 | `result.isError=true` | 把失败作为观察，修正参数或停止；不伪装成成功事实 |
| 业务验收 | 返回合法报价但缺少交期证据 | 继续查证、追问或交付部分结果 |

**旧版单独看：**`2025-11-25` 及以前先 `initialize` 协商，再发不含 `id` 的 `notifications/initialized`，然后进入 operation。当前版不需要这套连接握手；不能只替换日期字符串来迁移。一般 JSON-RPC notification 不携带请求 `id`，也不期待对应响应。

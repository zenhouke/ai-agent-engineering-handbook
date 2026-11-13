## 同一份报价怎样分别暴露

| 需要 | 原语与消息 | 返回后发生什么 |
|---|---|---|
| 根据参数查询 A | `tools/list` → `tools/call` | 执行 `read_quote`，得到结构化字段与可能的执行错误 |
| 读取已批准报价正文 | `resources/list` 或模板发现 → `resources/read` | 返回 URI 内容；Host 决定是否选入上下文 |
| 选用比较方法模板 | `prompts/list` → `prompts/get` | 渲染消息，不自动调用模型，也不自动执行工具 |

`resources/list` 用于固定资源，`resources/templates/list` 描述可参数化 URI；不能假定模板的每个实例都在资源列表里。URI 是标识，不必是能用浏览器打开的网页地址。

`inputSchema` 描述输入，`outputSchema` 可描述结构化输出；展示文本在 `content`，程序可用字段在 `structuredContent`。当前 Python SDK 使用 `input_schema`、`structured_content` 等蛇形属性，SDK 负责线缆字段转换。一个只读 tool 仍可以执行查询；Resource 与 Tool 的区别不只是“有没有写权限”。

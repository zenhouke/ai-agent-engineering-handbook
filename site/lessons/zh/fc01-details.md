## 一次客户端工具回合

先区分普通函数调用与模型 Function Calling：前者是程序已经进入函数执行；后者在本例中是模型产生调用提议，直到 Host 执行才发生实际调用。

1. 应用向模型提供函数描述与参数 schema。
2. 模型可返回普通文本、拒答、一个或多个工具调用；没有调用时不能硬执行默认工具。
3. Host 对每个提议验证工具名、参数、资源范围和当前业务状态，再调用受控函数。
4. 将真实结果按原 call_id 回传，模型据此继续回答。失败也要分类返回，不能编造成功回执。

本例采用 Responses 的 function_call / function_call_output 形状；Chat Completions 的工具消息、其他提供方的 tool_use/tool_result 并不相同。适配器只支持明确的 read_quote 参数契约，不冒充通用 schema 转换器；不演示完整流式聚合、并发调度或付费模型调用。

strict=true 有助于约束参数结构，不能证明对象可访问、价格有证据或业务动作已发生。流式参数要等该调用完整结束并校验后再执行；不能边收到一段 JSON 边触发写入。


依据：[Official 1](https://developers.openai.com/api/docs/guides/function-calling), [Official 2](https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview)。

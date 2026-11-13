## 从方法到真实调用，必须经过 Host

可用绑定来自可信部署配置，并与本次任务权限和当前可用工具取交集。本例只绑定 read_quote；用户、模型或技能正文不能把 create_order 填进来。绑定的语义名可由适配器映射到某个 MCP Server 工具，或直接 SDK；不把 Host 专用绑定字段写成通用规范。

调用仍经两次边界检查：Host 校验提议的工具名/参数/报价范围，MCP Server 的 service 再校验可读对象。激活方法只是准备上下文，既不执行脚本，也不自动调用工具。

真实内存 SDK 例子返回 A 的 unit_cents=180、shipping_cents=null。请求 B 在任务范围检查被拒绝；发现 B 的能力、合法工具 schema、成功认证都不能替代对象授权。后续写动作还需单独审批、操作键和未知结果核查。

**测试范围：** 没有模型请求、网络采购或训练。SDK 测试证明所列契约与拒绝路径，不证明任意第三方技能安全。摘要固定用于检测变更，不能把恶意包变成可信包。


依据：[Official 1](https://agentskills.io/client-implementation/adding-skills-support), [Official 2](https://modelcontextprotocol.io/docs/2026-07-28/learn/architecture)。

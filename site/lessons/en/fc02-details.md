## Two interfaces at different layers

| Dimension | Client Function Calling | MCP |
|---|---|---|
| Endpoints | Model provider interface ↔ Host | MCP Client ↔ Server |
| Content | Tool schemas, proposals, model observations | Capability discovery, RPC, tools/resources/prompts |
| Execution | Host dispatches direct SDK or MCP | Server invokes domain services |
| Requires the other? | No; direct local functions work | No; an ordinary program can call MCP |
| Authority | Host/domain authorization | Authentication plus object authorization |

Combined sequence: MCP list_tools → filtered/adapted model schema → function_call → Host policy → tools/call → domain service → provider observation under the original call_id. The Server need not know the originating model.

Provider call_id correlates model observations; JSON-RPC id correlates one MCP request; operation_id identifies one business effect across retries. The first two do not establish idempotency.

Real MCP is used with a fixed synthetic model proposal. Direct SDK execution needs no MCP, and fixed workflows can use MCP without model Function Calling. Schema constraints, errors and versions require explicit adaptation at the Host.


References: [Official 1](https://developers.openai.com/api/docs/guides/function-calling), [Official 2](https://modelcontextprotocol.io/docs/2026-07-28/learn/architecture)。

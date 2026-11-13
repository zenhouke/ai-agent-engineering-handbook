## MCP: six lessons from protocol to integration

[MCP deep dive](mcp01.md): architecture → primitives → requests/versioning → transport/auth → real server/client → Host adapter. The official SDK 2.3.0 is checked using an in-memory Client/Server without an LLM.


## Distinguish model-side and capability-side interfaces

[Function Calling mechanics](fc01.md) · [Function Calling / MCP](fc02.md): model proposals and Host execution first, then explicit adaptation between the two contracts. Each can operate without the other.

## What the SDK example verifies

Expect discovery of `read_quote` with a required string argument. A returns 180 cents and unknown shipping. B, outside the configured scope, produces a tool error. The resource returns A as text; the prompt returns template messages without invoking a model.

The code pins official `mcp==2.3.0`, using `MCPServer` and `Client`. Old v1 `FastMCP` imports and the separate `fastmcp` project are not interchangeable APIs.

Registration binds protocol capabilities. Handlers map errors, services authorize and repositories read fictional data. The in-memory connection exercises the real SDK without a subprocess or port, but does not verify network/OAuth/proxy or other-host compatibility.

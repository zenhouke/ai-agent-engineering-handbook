"""MCP SDK 2.3.0 transport references. No connection starts on import."""


async def list_local_tools() -> list[str]:
    import sys

    from mcp import Client, StdioServerParameters

    # Command and module are trusted Host configuration, never model-generated.
    # The official SDK owns subprocess startup, stream handling and shutdown.
    parameters = StdioServerParameters(
        command=sys.executable, args=["-m", "examples.mcp_server_example"]
    )
    async with Client(parameters) as client:
        result = await client.list_tools()
        return [tool.name for tool in result.tools]


async def list_remote_tools(endpoint: str, access_token: str) -> list[str]:
    import httpx2
    from mcp import Client
    from mcp.client.streamable_http import streamable_http_client

    if not endpoint.startswith("https://"):
        raise ValueError("Use TLS for a remote authenticated endpoint")
    async with httpx2.AsyncClient(
        headers={"Authorization": f"Bearer {access_token}"},
        timeout=httpx2.Timeout(30.0, read=300.0),
    ) as http_client:
        transport = streamable_http_client(endpoint, http_client=http_client)
        async with Client(transport) as client:
            result = await client.list_tools()
            return [tool.name for tool in result.tools]


# Obtain the token via your authorization flow; do not pass an upstream service token through.
# The HTTP server must validate audience/scope and resolve object access from trusted identity.

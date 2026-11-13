"""Discover real SDK tool schemas in memory, without a model or a subprocess."""


async def discover_capabilities() -> dict:
    from mcp import Client

    from .mcp_server_example import build_server

    async with Client(build_server()) as client:
        tools = await client.list_tools()
        return {
            "protocol": client.protocol_version,
            "tools": [
                {"name": tool.name, "input_schema": tool.input_schema}
                for tool in tools.tools
            ],
        }


# Host owns the model and policy. Client carries MCP messages. Server exposes capabilities.

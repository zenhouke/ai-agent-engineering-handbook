"""Both interfaces in one chain: provider function proposal → Host → MCP → observation."""

from .function_calling import handle_proposal, parse_proposal
from .mcp_host_bridge import call_authorized, check_quote_access
from .mcp_server_example import build_server


async def resolve_via_mcp(item: dict) -> dict:
    from mcp import Client

    _, arguments = parse_proposal(item)
    check_quote_access(
        "read_quote", arguments, frozenset({"read_quote"}), frozenset({"A"})
    )
    async with Client(build_server()) as client:

        async def execute(name, arguments):
            # Trusted task scope is injected by the application, never taken from item.
            return await call_authorized(
                client, name, arguments, frozenset({"read_quote"}), frozenset({"A"})
            )

        return await handle_proposal(item, execute)


# Provider call_id correlates model tool output; MCP request id correlates one RPC.
# Neither is the operation_id required to deduplicate an external business write.

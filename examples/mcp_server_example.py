"""Official Python SDK 2.3.0; protocol 2026-07-28. No external model required."""

from .mcp_app.domain import Quote
from .mcp_app.handlers import QuoteHandlers
from .mcp_app.repos import QuoteRepository
from .mcp_app.routes import register_capabilities
from .mcp_app.services import QuoteService


def build_server(allowed_ids: frozenset[str] = frozenset({"A"})):
    from mcp.server import MCPServer  # v2; not the v1 FastMCP import path.

    repository = QuoteRepository((Quote("A", 180, None), Quote("B", 170, 80)))
    handlers = QuoteHandlers(QuoteService(repository, allowed_ids))
    server = MCPServer("Quotation teaching server")
    register_capabilities(server, handlers)
    return server


if __name__ == "__main__":
    # stdio is a protocol-defined subprocess transport. stdout is reserved for MCP.
    # SDK clients own start/close/wait/kill; diagnostics belong on stderr.
    build_server().run(transport="stdio")

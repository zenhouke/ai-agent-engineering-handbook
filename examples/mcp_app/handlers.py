from dataclasses import asdict

from .services import QuoteService


class QuoteHandlers:
    def __init__(self, service: QuoteService):
        self._service = service

    def read_quote(self, quote_id: str) -> dict[str, str | int | None]:
        """Read one authorized fictional quotation. No write or order action."""
        from mcp.server.mcpserver.exceptions import ToolError

        try:
            return asdict(self._service.read(quote_id))
        except (PermissionError, LookupError) as error:
            raise ToolError("Quotation unavailable in current scope") from error

    def quote_resource(self) -> str:
        """Read the approved quotation as textual context."""
        from mcp.server.mcpserver.exceptions import ResourceError

        try:
            quote = self._service.read("A")
        except (PermissionError, LookupError) as error:
            raise ResourceError("Quotation context unavailable") from error
        return f"Quote A: {quote.unit_cents} cents per unit; shipping unknown."

    def compare_prompt(self, quote_id: str) -> str:
        """Return a user-selectable template; this does not run a model."""
        return (
            f"Compare quotation {quote_id!r} using authorized sources. "
            "Keep missing shipping and unsupported facts unknown. Do not place an order."
        )

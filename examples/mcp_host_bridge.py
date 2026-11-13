"""Host-side validation before an MCP call; the server enforces object scope too."""


def check_quote_access(
    name: str,
    arguments: dict,
    allowed_tools: frozenset[str],
    allowed_quote_ids: frozenset[str],
):
    if name not in allowed_tools:
        raise PermissionError("Tool not exposed to this task")
    if name != "read_quote" or set(arguments) != {"quote_id"}:
        raise ValueError("Unexpected tool contract")
    if not isinstance(arguments["quote_id"], str):
        raise TypeError("quote_id must be a string")
    if arguments["quote_id"] not in allowed_quote_ids:
        raise PermissionError("Quotation outside task scope")


async def call_authorized(
    client,
    name: str,
    arguments: dict,
    allowed_tools: frozenset[str],
    allowed_quote_ids: frozenset[str],
):
    check_quote_access(name, arguments, allowed_tools, allowed_quote_ids)
    result = await client.call_tool(name, arguments)
    if result.is_error:
        raise RuntimeError("Tool execution failed; do not claim task completion")
    return result.structured_content


# A model-provider adapter must map MCP input_schema to the provider's tool format,
# correlate call IDs and return the observation in that provider's expected structure.
# MCP content remains untrusted evidence, not a new system instruction.

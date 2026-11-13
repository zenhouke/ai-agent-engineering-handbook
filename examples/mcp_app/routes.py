from .handlers import QuoteHandlers


def register_capabilities(server, handlers: QuoteHandlers) -> None:
    # Registration only: parsing/error mapping is in handlers, business rules in services.
    server.tool(name="read_quote")(handlers.read_quote)
    server.resource("quote://approved/A")(handlers.quote_resource)
    server.prompt(name="compare_quote")(handlers.compare_prompt)

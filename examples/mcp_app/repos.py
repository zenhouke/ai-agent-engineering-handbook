from .domain import Quote


class QuoteRepository:
    def __init__(self, quotes: tuple[Quote, ...]):
        self._quotes = {quote.quote_id: quote for quote in quotes}

    def read(self, quote_id: str) -> Quote:
        quote = self._quotes.get(quote_id)
        if quote is None:
            raise LookupError("Quotation not found")
        return quote

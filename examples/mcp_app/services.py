from .domain import Quote
from .repos import QuoteRepository


class QuoteService:
    def __init__(self, repository: QuoteRepository, allowed_ids: frozenset[str]):
        self._repository = repository
        self._allowed_ids = allowed_ids  # Trusted configuration, not model arguments.

    def read(self, quote_id: str) -> Quote:
        if quote_id not in self._allowed_ids:
            raise PermissionError("Quotation is outside the permitted scope")
        return self._repository.read(quote_id)

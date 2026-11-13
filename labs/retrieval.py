"""Keyword tags isolate authorization and metric definitions, not NLP quality."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Chunk:
    chunk_id: str
    tenant: str
    tags: frozenset[str]
    text: str


CHUNKS = (
    Chunk(
        "quote",
        "A",
        frozenset({"delivery", "price"}),
        "Price 1.8; standard delivery 7 days",
    ),
    Chunk(
        "condition",
        "A",
        frozenset({"delivery"}),
        "Orders over 500 units need confirmation",
    ),
    Chunk(
        "private",
        "B",
        frozenset({"delivery", "price", "quantity"}),
        "Private B quotation",
    ),
)


def retrieve(tenant: str, query: set[str], k: int) -> list[Chunk]:
    if k < 1:
        raise ValueError("k must be positive")
    # Filter before scoring: unauthorized text never enters candidates.
    allowed = [chunk for chunk in CHUNKS if chunk.tenant == tenant]
    scored = [(len(query & chunk.tags), chunk) for chunk in allowed]
    scored.sort(key=lambda item: (-item[0], item[1].chunk_id))
    return [chunk for score, chunk in scored if score > 0][:k]


def evaluate(found: set[str], required: set[str]) -> tuple[float, bool]:
    if not required:
        raise ValueError("An answerable example needs at least one required chunk")
    return len(found & required) / len(required), required <= found


if __name__ == "__main__":
    for k in (1, 2):
        candidates = retrieve("A", {"delivery", "price", "quantity"}, k)
        ids = {chunk.chunk_id for chunk in candidates}
        recall, complete = evaluate(ids, {"quote", "condition"})
        print(
            f"k={k}, candidates={sorted(ids)}, recall={recall}, evidence_complete={complete}"
        )

"""RRF combines rankings, not incompatible raw similarity scales."""

from collections import defaultdict
from collections.abc import Sequence


def reciprocal_rank_fusion(
    rankings: Sequence[Sequence[str]], allowed_ids: set[str], k: int = 60
) -> list[tuple[str, float]]:
    if k <= 0:
        raise ValueError("k must be positive")
    scores = defaultdict(float)
    for ranking in rankings:
        seen = set()
        for rank, document_id in enumerate(ranking, 1):
            if document_id not in allowed_ids or document_id in seen:
                continue
            scores[document_id] += 1 / (k + rank)
            seen.add(document_id)
    return sorted(scores.items(), key=lambda item: (-item[1], item[0]))


# Inputs should come from authorized BM25/vector retrieval. No embedding model is hidden here.

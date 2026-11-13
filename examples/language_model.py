"""Count a character bigram with explicit sentence boundaries and smoothing."""

from collections import Counter, defaultdict
from itertools import pairwise


def transition_probabilities(words: list[str], alpha: float = 1.0):
    if alpha <= 0:
        raise ValueError("Positive smoothing required")
    counts = defaultdict(Counter)
    for word in words:
        sequence = ["<start>", *word, "<end>"]
        for left, right in pairwise(sequence):
            counts[left][right] += 1
    vocabulary = sorted({token for row in counts.values() for token in row})
    return {
        left: {
            right: (row[right] + alpha) / (sum(row.values()) + alpha * len(vocabulary))
            for right in vocabulary
        }
        for left, row in counts.items()
    }

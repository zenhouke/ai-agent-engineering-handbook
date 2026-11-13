"""Stable softmax with an explicit mask and a tiny attention example."""

import math
from collections.abc import Sequence


def softmax(scores: Sequence[float], visible: Sequence[bool]) -> list[float]:
    if len(scores) != len(visible) or not any(visible):
        raise ValueError("Matching lengths and at least one visible position required")
    if not all(math.isfinite(score) for score in scores):
        raise ValueError("Scores must be finite")
    maximum = max(score for score, keep in zip(scores, visible) if keep)
    values = [
        math.exp(score - maximum) if keep else 0.0
        for score, keep in zip(scores, visible)
    ]
    total = sum(values)
    return [value / total for value in values]


def example(mask_future: bool) -> tuple[list[float], list[float]]:
    weights = softmax([1, 0], [True, not mask_future])
    values = [[2, 0], [0, 2]]
    output = [
        sum(weight * value[dimension] for weight, value in zip(weights, values))
        for dimension in range(2)
    ]
    return weights, output


if __name__ == "__main__":
    for masked in (False, True):
        weights, output = example(masked)
        print(f"mask_future={masked}, weights={weights}, output={output}")

"""One sample makes every intermediate quantity inspectable."""


def update(weight: float, learning_rate: float) -> tuple[float, float]:
    prediction = weight * 2
    gradient = 2 * (prediction - 4) * 2
    new_weight = weight - learning_rate * gradient
    return new_weight, (new_weight * 2 - 4) ** 2


if __name__ == "__main__":
    for rate in (0.1, 0.3):
        weight, loss = update(1, rate)
        print(f"learning_rate={rate}, weight={weight:.4f}, loss={loss:.4f}")

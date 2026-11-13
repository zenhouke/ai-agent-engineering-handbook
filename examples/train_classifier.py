"""Optional complete training reference. Supplied as code, not executed in validation.

CSV format: feature_1,feature_2,label (numeric features; label is 0 or 1).
Use separate train/validation data; reserve a third period for final testing.
This file never downloads a dataset or model. Running main is an explicit opt-in.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


def read_rows(path: Path) -> tuple[list[list[float]], list[float]]:
    import math

    inputs, labels = [], []
    with path.open(newline="") as stream:
        for row in csv.DictReader(stream):
            features = [float(row["feature_1"]), float(row["feature_2"])]
            label = float(row["label"])
            if not all(math.isfinite(value) for value in features) or label not in (
                0,
                1,
            ):
                raise ValueError("Finite features and binary labels required")
            inputs.append(features)
            labels.append(label)
    if not inputs:
        raise ValueError("Dataset is empty")
    return inputs, labels


def train(
    train_csv: Path,
    validation_csv: Path,
    output: Path,
    epochs: int = 20,
    learning_rate: float = 0.001,
    seed: int = 42,
) -> None:
    import torch
    from torch import nn
    from torch.utils.data import DataLoader, TensorDataset

    if epochs <= 0 or learning_rate <= 0:
        raise ValueError("Positive epochs and learning rate required")
    if train_csv.resolve() == validation_csv.resolve():
        raise ValueError("Training and validation inputs must be separate")
    torch.manual_seed(seed)
    train_x, train_y = read_rows(train_csv)
    val_x, val_y = read_rows(validation_csv)
    x = torch.tensor(train_x, dtype=torch.float32)
    y = torch.tensor(train_y, dtype=torch.float32)
    vx = torch.tensor(val_x, dtype=torch.float32)
    vy = torch.tensor(val_y, dtype=torch.float32)
    # Fit preprocessing only on the training partition.
    mean, scale = x.mean(0), x.std(0, unbiased=False).clamp_min(1e-6)
    x, vx = (x - mean) / scale, (vx - mean) / scale
    batches = DataLoader(TensorDataset(x, y), batch_size=32, shuffle=True)
    model = nn.Sequential(nn.Linear(2, 2), nn.ReLU(), nn.Linear(2, 1))
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
    criterion = nn.BCEWithLogitsLoss()
    best_loss = float("inf")
    output.parent.mkdir(parents=True, exist_ok=True)
    for epoch in range(epochs):
        model.train()
        for batch_x, batch_y in batches:
            optimizer.zero_grad(set_to_none=True)
            loss = criterion(model(batch_x).squeeze(-1), batch_y)
            loss.backward()
            optimizer.step()
        model.eval()
        with torch.inference_mode():
            logits = model(vx).squeeze(-1)
            validation_loss = criterion(logits, vy).item()
            accuracy = ((logits >= 0) == vy.bool()).float().mean().item()
        if validation_loss < best_loss:
            best_loss = validation_loss
            torch.save(
                {
                    "state_dict": model.state_dict(),
                    "mean": mean,
                    "scale": scale,
                    "epoch": epoch,
                    "seed": seed,
                },
                output,
            )
        print(
            f"epoch={epoch + 1} val_loss={validation_loss:.4f} val_accuracy={accuracy:.3f}"
        )
    # Accuracy is illustrative; include recall/precision and group metrics for real risk tasks.


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--train-csv", type=Path, required=True)
    parser.add_argument("--validation-csv", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--epochs", type=int, default=20)
    arguments = parser.parse_args()
    train(
        arguments.train_csv,
        arguments.validation_csv,
        arguments.output,
        arguments.epochs,
    )


if __name__ == "__main__":
    main()

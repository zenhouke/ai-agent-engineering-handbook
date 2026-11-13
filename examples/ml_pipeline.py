"""Time-ordered model selection. Reference only: no training on import."""


def fit_time_split(features, labels, split: int):
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import precision_score, recall_score
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler

    if not 0 < split < len(features):
        raise ValueError("Nonempty past and future partitions required")
    # features and labels must already be ordered by prediction time.
    model = make_pipeline(StandardScaler(), LogisticRegression(max_iter=500))
    model.fit(features[:split], labels[:split])
    predictions = model.predict(features[split:])
    return model, {
        "precision": precision_score(labels[split:], predictions, zero_division=0),
        "recall": recall_score(labels[split:], predictions, zero_division=0),
    }


# The future partition is validation here. Reserve a third, untouched test period.

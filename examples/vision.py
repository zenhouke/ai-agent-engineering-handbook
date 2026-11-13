"""A CNN inference block. No datasets, training or downloads are started."""


def build_classifier():
    from torch import nn

    return nn.Sequential(
        nn.Conv2d(1, 8, kernel_size=3, padding=1),
        nn.ReLU(),
        nn.AdaptiveAvgPool2d(1),
        nn.Flatten(),
        nn.Linear(8, 2),
    )


# Input [batch,1,height,width] -> feature map -> [batch,8] -> two logits.
# Randomly initialized weights demonstrate shapes, not useful predictions.

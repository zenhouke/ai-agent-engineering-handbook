"""2 -> 2 -> 1 MLP: this shape also appears in the lesson diagram."""


def build_model():
    from torch import nn

    return nn.Sequential(nn.Linear(2, 2), nn.ReLU(), nn.Linear(2, 1))


def train_batch(model, optimizer, inputs, labels):
    from torch.nn import functional as F

    model.train()
    optimizer.zero_grad(set_to_none=True)
    logits = model(inputs).squeeze(-1)
    loss = F.binary_cross_entropy_with_logits(logits, labels.float())
    loss.backward()
    optimizer.step()
    return loss.detach()


# Supply inputs [batch,2], labels [batch]. This function is reference code only.

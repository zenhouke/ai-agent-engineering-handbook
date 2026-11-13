"""Reference training step; not executed during documentation checks."""


def gradient_step() -> dict[str, float]:
    import torch

    weight = torch.tensor(1.0, requires_grad=True)
    prediction = weight * 2
    loss = (prediction - 4).square()
    loss.backward()  # derivative: -8
    with torch.no_grad():
        weight -= 0.1 * weight.grad  # reference result: 1.8
        updated_loss = (weight * 2 - 4).square()
    weight.grad = None  # do not carry a stale gradient
    return {
        "weight": weight.detach().item(),
        "loss_before": loss.detach().item(),
        "loss_after": updated_loss.item(),
    }

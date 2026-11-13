"""LoRA reference layer with the base frozen. No weights are downloaded."""


def attach_lora(base, rank: int = 8, alpha: float = 16):
    import torch
    from torch import nn

    if rank < 1:
        raise ValueError("rank must be positive")

    class LoRALinear(nn.Module):
        def __init__(self):
            super().__init__()
            self.base = base.requires_grad_(False)
            self.a = nn.Parameter(
                torch.empty(
                    rank,
                    base.in_features,
                    device=base.weight.device,
                    dtype=base.weight.dtype,
                )
            )
            self.b = nn.Parameter(
                torch.zeros(
                    base.out_features,
                    rank,
                    device=base.weight.device,
                    dtype=base.weight.dtype,
                )
            )
            nn.init.kaiming_uniform_(self.a, a=5**0.5)
            self.scale = alpha / rank

        def forward(self, x):
            return self.base(x) + (x @ self.a.T @ self.b.T) * self.scale

    return LoRALinear()


# B starts at zero, so the initial adapted output equals the base output.

"""Complete causal block; forward reference, no training on import."""


def build_decoder_block(width: int = 64, heads: int = 4):
    import torch
    from torch import nn

    if width % heads:
        raise ValueError("width must be divisible by heads")

    class DecoderBlock(nn.Module):
        def __init__(self):
            super().__init__()
            self.norm1 = nn.LayerNorm(width)
            self.attention = nn.MultiheadAttention(
                width, heads, dropout=0, batch_first=True
            )
            self.norm2 = nn.LayerNorm(width)
            self.ffn = nn.Sequential(
                nn.Linear(width, 4 * width), nn.GELU(), nn.Linear(4 * width, width)
            )

        def forward(self, x):
            length = x.shape[1]  # x: [batch,time,width]
            mask = torch.ones(length, length, device=x.device, dtype=torch.bool).triu(1)
            normalized = self.norm1(x)
            mixed, _ = self.attention(
                normalized, normalized, normalized, attn_mask=mask, need_weights=False
            )
            x = x + mixed
            return x + self.ffn(self.norm2(x))

    return DecoderBlock()


# Add token+position embeddings before this block and a vocabulary head after it.
# This is a block, not a pretrained language model or a KV-cached decoder.

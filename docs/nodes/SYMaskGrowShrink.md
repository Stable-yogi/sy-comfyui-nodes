# MaskGrowShrink SY (`SYMaskGrowShrink`)

Source: `nodes/sy_mask_grow_shrink.py`

**What it does:** Makes the white area of a mask bigger (positive pixels) or smaller (negative pixels). The info output says how much white there was before and after, and warns when the mask became empty or full.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| mask | MASK | yes | The mask to change. | mask [B,H,W] |
| pixels | INT | yes | Positive grows the white area, negative shrinks it. | -512 to 512, step 1, default 8 |
| shape | COMBO | yes | Round keeps corners smooth. Square grows corners out. | one of: round, square |

Outputs: `MASK`, `STRING`

## How to use

1. Connect your mask.
2. Set pixels. A positive number makes the white area bigger, a negative number makes it smaller.
3. Choose shape: round keeps corners smooth, square grows corners outward.
The info output shows how much white there was before and after, and warns if the mask became empty or full.

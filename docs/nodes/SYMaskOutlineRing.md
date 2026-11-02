# Mask Outline Ring SY (`SYMaskOutlineRing`)

Source: `nodes/sy_mask_outline_ring.py`

**What it does:** Makes an outline: a band of the chosen width around the edge of a mask, outside it, inside it, or centred on the edge. The band is round. Soft feathers its edges. Edges of the picture itself never get a band.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| mask | MASK | yes | The mask to draw an outline around. | mask [B,H,W] |
| width | INT | yes | Thickness of the outline in pixels. | 1 to 200, step 1, default 6 |
| position | COMBO | yes | Where the band sits: outside the mask, inside it, or half and half on the edge. | one of: outside, inside, centred |
| soft | FLOAT | yes | How much the band edges are feathered. 0 gives hard edges. | 0.0 to 1.0, step 0.01, default 0.0 |
| threshold | FLOAT | yes | Mask values above this count as white, the rest as black. | 0.0 to 1.0, step 0.01, default 0.5 |

Outputs: `MASK`

## How to use

1. Connect the mask to **mask**.
2. Set **width** to the outline thickness in pixels.
3. Pick **position**: outside grows away from the shape, inside stays within it, centred straddles the edge.
4. Raise **soft** to feather the band; 0 keeps it hard.
5. The output **MASK** is the outline band only. Use it to draw a border or glow.

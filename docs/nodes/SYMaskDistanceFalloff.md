# Mask Distance Falloff SY (`SYMaskDistanceFalloff`)

Source: `nodes/sy_mask_distance_falloff.py`

**What it does:** Makes a soft edge that depends on how far each pixel is from the mask shape. Distance is counted up to the distance setting, so far pixels stay 0 outside and 1 inside.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| mask | MASK | yes | The mask whose shape the soft edge follows. Pixels above 0.5 count as the shape. | mask [B,H,W] |
| distance | INT | yes | How many pixels wide the soft edge is. Longer distances are slower. | 1 to 256, default 24 |
| side | COMBO | yes | Outside: shape stays solid, edge fades away from it. Inside: fades inward. Both: centred on the edge. | one of: outside, inside, both |
| curve | COMBO | yes | Shape of the fade. Smooth is soft at both ends, sharp drops fast near the shape. | one of: linear, smooth, sharp |

Outputs: `MASK`

## How to use

1. Connect a mask to **mask**.
2. Set **distance** to the width of the soft edge in pixels.
3. Pick **side**: outside grows a soft halo, inside softens the shape from within, both is centred on the old edge.
4. Pick **curve** for how the fade looks.
5. Use the output **MASK** wherever you need a soft, shape-following edge.

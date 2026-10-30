# MaskFeather SY (`SYMaskFeather`)

Source: `nodes/sy_mask_feather.py`

**What it does:** Softens the edge of a mask with a smooth blur so it blends in. Radius 0 changes nothing.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| mask | MASK | yes | The mask to soften. | mask [B,H,W] |
| radius | INT | yes | How many pixels wide the soft edge is. 0 keeps the mask as it is. | 0 to 512, step 1, default 16 |

Outputs: `MASK`

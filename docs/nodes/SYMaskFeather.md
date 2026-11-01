# MaskFeather SY (`SYMaskFeather`)

Source: `nodes/sy_mask_feather.py`

**What it does:** Softens the edge of a mask with a smooth blur so it blends in. Radius 0 changes nothing. Can grow first and then feather (the right order), and keep the soft edge inside the old edge so no halo appears outside the subject.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| mask | MASK | yes | The mask to soften. | mask [B,H,W] |
| radius | INT | yes | How many pixels wide the soft edge is. 0 keeps the mask as it is. | 0 to 512, step 1, default 16 |
| grow | INT | no | Grow the white area by this many pixels BEFORE feathering (negative shrinks). 0 is off. | -512 to 512, step 1, default 0 |
| edge | COMBO | no | centred: soft edge on both sides. inside only: no halo outside. outside only: no shrinking. | one of: centred, inside only, outside only |

Outputs: `MASK`, `STRING`

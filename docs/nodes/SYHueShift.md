# Hue Shift SY (`SYHueShift`)

Source: `nodes/sy_hue_shift.py`

**What it does:** Rotates all colours around the colour wheel. Greys stay grey.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image | IMAGE | yes | The picture or batch of pictures to recolour. | picture batch [B,H,W,3] |
| degrees | FLOAT | yes | How far to turn the colours. 180 swaps each colour for roughly its opposite. | -180.0 to 180.0, step 1.0, default 0.0 |
| strength | FLOAT | yes | How much of the shifted colour to use. 0 keeps the original. | 0.0 to 1.0, step 0.01, default 1.0 |

Outputs: `IMAGE`

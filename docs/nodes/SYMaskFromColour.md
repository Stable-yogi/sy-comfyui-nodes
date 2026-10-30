# MaskFromColour SY (`SYMaskFromColour`)

Source: `nodes/sy_mask_from_colour.py`

**What it does:** Makes a mask from every pixel that is close to a chosen colour. Tolerance sets how close.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image | IMAGE | yes | The picture to pick the colour from. | picture batch [B,H,W,3] |
| red | INT | yes | Red part of the wanted colour, 0 to 255. | 0 to 255, step 1, default 0 |
| green | INT | yes | Green part of the wanted colour, 0 to 255. | 0 to 255, step 1, default 255 |
| blue | INT | yes | Blue part of the wanted colour, 0 to 255. | 0 to 255, step 1, default 0 |
| tolerance | INT | yes | How far each colour part may differ and still count. 0 is an exact match. | 0 to 255, step 1, default 20 |

Outputs: `MASK`

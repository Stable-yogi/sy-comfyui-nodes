# MaskOverlayPreview SY (`SYMaskOverlayPreview`)

Source: `nodes/sy_mask_overlay_preview.py`

**What it does:** Shows a mask on top of a picture as a coloured tint, so you can check what it covers.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image | IMAGE | yes | The picture to show the mask on. | picture batch [B,H,W,3] |
| mask | MASK | yes | The mask to show. It is stretched to the picture size if needed. | mask [B,H,W] |
| red | INT | yes | Red part of the tint colour, 0 to 255. | 0 to 255, step 1, default 255 |
| green | INT | yes | Green part of the tint colour, 0 to 255. | 0 to 255, step 1, default 0 |
| blue | INT | yes | Blue part of the tint colour, 0 to 255. | 0 to 255, step 1, default 0 |
| opacity | FLOAT | yes | How strong the tint is. 0 shows no tint, 1 covers the picture. | 0.0 to 1.0, step 0.01, default 0.5 |

Outputs: `IMAGE`

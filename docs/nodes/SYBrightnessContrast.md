# Brightness Contrast SY (`SYBrightnessContrast`)

Source: `nodes/sy_brightness_contrast.py`

**What it does:** Makes a picture lighter or darker, and flatter or punchier. Adds a mask (change only the white part), a mix slider to blend with the original, an on/off switch and an info line, and keeps transparency. Both at 0 leaves the picture as it is.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image | IMAGE | yes | The picture or batch of pictures to change. | picture batch [B,H,W,3] |
| brightness | FLOAT | yes | Below 0 darkens, above 0 lightens. | -100.0 to 100.0, step 1.0, default 0.0 |
| contrast | FLOAT | yes | Below 0 flattens the picture, above 0 pushes lights and darks apart. | -100.0 to 100.0, step 1.0, default 0.0 |
| mask | MASK | no | Optional. White = apply the effect, black = keep the original. A different size is stretched to fit. | mask [B,H,W] |
| mix | FLOAT | no | How much of the effect to use. 1 = full effect, 0.5 = half, 0 = original picture. | 0.0 to 1.0, step 0.01, default 1.0 |
| enabled | BOOLEAN | no | Turn off to pass the picture through untouched (handy to compare before and after). | default True |

Outputs: `IMAGE`, `STRING`

## How to use

1. Connect your picture to image.
2. Set brightness (below 0 darkens, above 0 lightens) and contrast (below 0 flattens, above 0 pushes lights and darks apart). Both at 0 changes nothing.
3. Optional: connect a mask (white = change, black = keep), lower mix to blend with the original, or turn enabled off.
4. The result comes out as image. Transparency is kept.

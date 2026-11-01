# Auto Contrast SY (`SYAutoContrast`)

Source: `nodes/sy_auto_contrast.py`

**What it does:** Stretches the darkest and brightest parts of each picture to fill the full range. Fixes dull, flat pictures. Adds per-colour stretching (removes colour casts), a mask, a mix slider, an on/off switch and an info line.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image | IMAGE | yes | The picture or batch of pictures to change. Each picture is handled on its own. | picture batch [B,H,W,3] |
| clip_percent | FLOAT | yes | Percent of the darkest and brightest pixels to ignore when finding the range. | 0.0 to 20.0, step 0.1, default 1.0 |
| mask | MASK | no | Optional. White = apply the effect, black = keep the original. A different size is stretched to fit. | mask [B,H,W] |
| mix | FLOAT | no | How much of the effect to use. 1 = full effect, 0.5 = half, 0 = original picture. | 0.0 to 1.0, step 0.01, default 1.0 |
| enabled | BOOLEAN | no | Turn off to pass the picture through untouched (handy to compare before and after). | default True |
| per_colour | BOOLEAN | no | On: stretch red, green and blue on their own. Also removes a colour cast. | default False |

Outputs: `IMAGE`, `STRING`

## How to use

1. Connect your picture to image.
2. Set clip_percent: the share of darkest and brightest pixels to ignore when finding the range.
3. Turn on per_colour to stretch red, green and blue on their own, which also removes a colour cast.
4. Optional: connect a mask (white = apply), lower mix to blend with the original, or turn enabled off to pass the picture through.

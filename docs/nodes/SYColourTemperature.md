# Colour Temperature SY (`SYColourTemperature`)

Source: `nodes/sy_colour_temperature.py`

**What it does:** Makes a picture warmer (orange) or cooler (blue), and can push it towards magenta or green. Adds a mask, a mix slider to blend with the original, an on/off switch and an info line, and keeps transparency.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image | IMAGE | yes | The picture or batch of pictures to adjust. | picture batch [B,H,W,3] |
| warmth | FLOAT | yes | Above 0 is warmer (more red, less blue). Below 0 is cooler. | -100.0 to 100.0, step 1.0, default 0.0 |
| tint | FLOAT | yes | Above 0 pushes towards magenta. Below 0 pushes towards green. | -100.0 to 100.0, step 1.0, default 0.0 |
| mask | MASK | no | Optional. White = apply the effect, black = keep the original. A different size is stretched to fit. | mask [B,H,W] |
| mix | FLOAT | no | How much of the effect to use. 1 = full effect, 0.5 = half, 0 = original picture. | 0.0 to 1.0, step 0.01, default 1.0 |
| enabled | BOOLEAN | no | Turn off to pass the picture through untouched (handy to compare before and after). | default True |

Outputs: `IMAGE`, `STRING`

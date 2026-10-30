# Colour Temperature SY (`SYColourTemperature`)

Source: `nodes/sy_colour_temperature.py`

**What it does:** Makes a picture warmer (orange) or cooler (blue), and can push it towards magenta or green.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image | IMAGE | yes | The picture or batch of pictures to adjust. | picture batch [B,H,W,3] |
| warmth | FLOAT | yes | Above 0 is warmer (more red, less blue). Below 0 is cooler. | -100.0 to 100.0, step 1.0, default 0.0 |
| tint | FLOAT | yes | Above 0 pushes towards magenta. Below 0 pushes towards green. | -100.0 to 100.0, step 1.0, default 0.0 |

Outputs: `IMAGE`

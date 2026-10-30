# Brightness Contrast SY (`SYBrightnessContrast`)

Source: `nodes/sy_brightness_contrast.py`

**What it does:** Makes a picture lighter or darker, and flatter or punchier. Both at 0 leaves the picture as it is.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image | IMAGE | yes | The picture or batch of pictures to change. | picture batch [B,H,W,3] |
| brightness | FLOAT | yes | Below 0 darkens, above 0 lightens. | -100.0 to 100.0, step 1.0, default 0.0 |
| contrast | FLOAT | yes | Below 0 flattens the picture, above 0 pushes lights and darks apart. | -100.0 to 100.0, step 1.0, default 0.0 |

Outputs: `IMAGE`

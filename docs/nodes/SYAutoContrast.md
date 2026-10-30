# Auto Contrast SY (`SYAutoContrast`)

Source: `nodes/sy_auto_contrast.py`

**What it does:** Stretches the darkest and brightest parts of each picture to fill the full range. Fixes dull, flat pictures.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image | IMAGE | yes | The picture or batch of pictures to change. Each picture is handled on its own. | picture batch [B,H,W,3] |
| clip_percent | FLOAT | yes | Percent of the darkest and brightest pixels to ignore when finding the range. | 0.0 to 20.0, step 0.1, default 1.0 |

Outputs: `IMAGE`

# Image Stats SY (`SYImageStats`)

Source: `nodes/sy_image_stats.py`

**What it does:** Measures a picture: average brightness, contrast, and how many pixels are very dark or very bright.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image | IMAGE | yes | The picture or batch of pictures to measure. A batch is measured as one. | picture batch [B,H,W,3] |
| dark_level | FLOAT | yes | Pixels darker than this count as dark. Must be lower than bright_level. | 0.0 to 1.0, step 0.01, default 0.1 |
| bright_level | FLOAT | yes | Pixels brighter than this count as bright. Must be higher than dark_level. | 0.0 to 1.0, step 0.01, default 0.9 |

Outputs: `FLOAT`, `FLOAT`, `FLOAT`, `FLOAT`, `STRING`

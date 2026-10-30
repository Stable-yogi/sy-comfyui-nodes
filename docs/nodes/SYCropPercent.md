# Crop Percent SY (`SYCropPercent`)

Source: `nodes/sy_crop_percent.py`

**What it does:** Cuts a percentage off each edge of a picture. Gives the cropped picture and its new size.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image | IMAGE | yes | The picture or batch of pictures to crop. | picture batch [B,H,W,3] |
| left | FLOAT | yes | Percent of the width to remove from this edge. | 0.0 to 49.9, step 0.1, default 0.0 |
| right | FLOAT | yes | Percent of the width to remove from this edge. | 0.0 to 49.9, step 0.1, default 0.0 |
| top | FLOAT | yes | Percent of the height to remove from this edge. | 0.0 to 49.9, step 0.1, default 0.0 |
| bottom | FLOAT | yes | Percent of the height to remove from this edge. | 0.0 to 49.9, step 0.1, default 0.0 |

Outputs: `IMAGE`, `INT`, `INT`

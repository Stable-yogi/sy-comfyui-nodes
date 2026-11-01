# Crop Percent SY (`SYCropPercent`)

Source: `nodes/sy_crop_percent.py`

**What it does:** Cuts a percentage off each edge of a picture. Gives the cropped picture, its new size and an info line. The optional snap_multiple trims the result to a multiple of 8 or 64 so the next model node accepts it.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image | IMAGE | yes | The picture or batch of pictures to crop. | picture batch [B,H,W,3] |
| left | FLOAT | yes | Percent of the width to remove from this edge. | 0.0 to 49.9, step 0.1, default 0.0 |
| right | FLOAT | yes | Percent of the width to remove from this edge. | 0.0 to 49.9, step 0.1, default 0.0 |
| top | FLOAT | yes | Percent of the height to remove from this edge. | 0.0 to 49.9, step 0.1, default 0.0 |
| bottom | FLOAT | yes | Percent of the height to remove from this edge. | 0.0 to 49.9, step 0.1, default 0.0 |
| snap_multiple | INT | no | 1 is off. 8 trims the result so width and height are multiples of 8 (many models need it). | 1 to 256, default 1 |

Outputs: `IMAGE`, `INT`, `INT`, `STRING`

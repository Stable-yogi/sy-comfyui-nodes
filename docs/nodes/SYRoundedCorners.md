# Rounded Corners SY (`SYRoundedCorners`)

Source: `nodes/sy_rounded_corners.py`

**What it does:** Rounds the corners of a picture. The cut-off corners are painted with a background colour and also given as a mask.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image | IMAGE | yes | The picture or batch of pictures to round the corners of. | picture batch [B,H,W,3] |
| radius_percent | FLOAT | yes | Corner size as a percent of the shorter side. 50 makes a circle or pill. | 0.0 to 50.0, step 0.5, default 10.0 |
| background | STRING | yes | Colour painted in the cut-off corners, as 3 or 6 hex digits. | default '#000000' |

Outputs: `IMAGE`, `MASK`

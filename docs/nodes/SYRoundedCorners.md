# Rounded Corners SY (`SYRoundedCorners`)

Source: `nodes/sy_rounded_corners.py`

**What it does:** Rounds the corners of a picture. The cut-off corners are painted with a background colour and also given as a mask. Switch on transparent_corners to get an alpha channel instead of a painted corner.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image | IMAGE | yes | The picture or batch of pictures to round the corners of. | picture batch [B,H,W,3] |
| radius_percent | FLOAT | yes | Corner size as a percent of the shorter side. 50 makes a circle or pill. | 0.0 to 50.0, step 0.5, default 10.0 |
| background | STRING | yes | Colour painted in the cut-off corners, as 3 or 6 hex digits. | default '#000000' |
| transparent_corners | BOOLEAN | no | On: keep the corners see-through (adds an alpha channel) instead of painting the background colour. | default False |

Outputs: `IMAGE`, `MASK`, `STRING`

## How to use

1. Connect your picture to image.
2. Set radius_percent, the corner size as a percent of the shorter side. 50 makes a circle or pill.
3. The cut-off corners are painted with background (3 or 6 hex digits) and also given as a mask.
4. Turn transparent_corners on to get an alpha channel instead of painted corners.
Outputs: image, mask and an info line.

# Orientation SY (`SYOrientation`)

Source: `nodes/sy_orientation.py`

**What it does:** Tells if an image is landscape, portrait or square, and gives its width and height, its width/height ratio, and a plain info sentence (ratio like 16:9, megapixels).

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image | IMAGE | yes | The picture to measure. For a batch the first size is used. | picture batch [B,H,W,3] |
| tolerance_percent | FLOAT | yes | Sides this close (in percent of the longer side) count as square. | 0.0 to 100.0, step 0.5, default 0.0 |

Outputs: `STRING`, `BOOLEAN`, `INT`, `INT`, `FLOAT`, `STRING`

## How to use

1. Connect your picture to image. For a batch, the first size is used.
2. Optional: set tolerance_percent. Sides this close, in percent of the longer side, count as square.
3. Outputs: landscape, portrait or square as text, an is_landscape switch, width, height, the width/height ratio and a sentence such as the ratio (16:9) and megapixels.

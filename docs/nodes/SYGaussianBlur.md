# Gaussian Blur SY (`SYGaussianBlur`)

Source: `nodes/sy_gaussian_blur.py`

**What it does:** Blurs a picture softly. Radius 0 leaves it as it is. Add a mask to blur only that area (the edge of a soft mask blends smoothly), and read the info line for what was done.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image | IMAGE | yes | The picture or batch of pictures to blur. | picture batch [B,H,W,3] |
| radius | FLOAT | yes | How far the blur reaches, in pixels. 0 does nothing. | 0.0 to 64.0, step 0.1, default 4.0 |
| mask | MASK | no | Optional. Blur only where this mask is white. A different size is stretched to fit. | mask [B,H,W] |

Outputs: `IMAGE`, `STRING`

## How to use

1. Connect a picture or batch to image.
2. Set radius in pixels. 0 leaves the picture as it is.
3. Optional: connect a mask to blur only the white area. A mask of another size is stretched to fit.
4. The blurred picture comes out, plus an info line that says what was done.

# Gaussian Blur SY (`SYGaussianBlur`)

Source: `nodes/sy_gaussian_blur.py`

**What it does:** Blurs a picture softly. A bigger radius gives a stronger blur. Radius 0 leaves the picture as it is.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image | IMAGE | yes | The picture or batch of pictures to blur. | picture batch [B,H,W,3] |
| radius | FLOAT | yes | How far the blur reaches, in pixels. 0 does nothing. | 0.0 to 64.0, step 0.1, default 4.0 |

Outputs: `IMAGE`

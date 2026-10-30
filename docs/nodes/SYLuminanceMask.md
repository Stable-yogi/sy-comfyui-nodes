# Luminance Mask SY (`SYLuminanceMask`)

Source: `nodes/sy_luminance_mask.py`

**What it does:** Builds a mask from brightness. Pixels between low and high are white in the mask, the rest are black, with an optional soft fade.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image | IMAGE | yes | The picture or batch of pictures to measure the brightness of. | picture batch [B,H,W,3] |
| low | FLOAT | yes | Darkest brightness that still counts. 0 is black. | 0.0 to 1.0, step 0.01, default 0.0 |
| high | FLOAT | yes | Brightest brightness that still counts. 1 is white. | 0.0 to 1.0, step 0.01, default 1.0 |
| softness | FLOAT | yes | Width of the fade outside the band. 0 gives hard black and white. | 0.0 to 0.5, step 0.01, default 0.0 |
| invert | BOOLEAN | yes | Swap the mask so the chosen band becomes black. | default False |

Outputs: `MASK`

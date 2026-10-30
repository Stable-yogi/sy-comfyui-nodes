# Threshold SY (`SYThreshold`)

Source: `nodes/sy_threshold.py`

**What it does:** Makes a black and white picture: brighter than the level becomes white, darker becomes black. Also gives a mask.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image | IMAGE | yes | The picture or batch of pictures to turn black and white. | picture batch [B,H,W,3] |
| level | FLOAT | yes | Brightness where black turns to white. Higher means more of the picture goes black. | 0.0 to 1.0, step 0.01, default 0.5 |
| softness | FLOAT | yes | Width of a smooth grey ramp around the level. 0 gives a hard edge. | 0.0 to 0.5, step 0.01, default 0.0 |
| invert | BOOLEAN | yes | Swap black and white. | default False |

Outputs: `IMAGE`, `MASK`

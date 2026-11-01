# Threshold SY (`SYThreshold`)

Source: `nodes/sy_threshold.py`

**What it does:** Makes a black and white picture: brighter than the level becomes white, darker becomes black. Also gives a mask. Can cut on one colour channel instead of brightness, and the info output says how much turned white.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image | IMAGE | yes | The picture or batch of pictures to turn black and white. | picture batch [B,H,W,3] |
| level | FLOAT | yes | Brightness where black turns to white. Higher means more of the picture goes black. | 0.0 to 1.0, step 0.01, default 0.5 |
| softness | FLOAT | yes | Width of a smooth grey ramp around the level. 0 gives a hard edge. | 0.0 to 0.5, step 0.01, default 0.0 |
| invert | BOOLEAN | yes | Swap black and white. | default False |
| channel | COMBO | no | What to cut on: normal brightness, one colour channel, or the highest of red, green and blue. | one of: brightness, red, green, blue, highest |

Outputs: `IMAGE`, `MASK`, `STRING`

## How to use

1. Connect a picture or a batch to image.
2. Set level. Brighter than the level becomes white, darker becomes black.
3. Set softness for a smooth grey ramp (0 is a hard edge), turn on invert to swap black and white, and pick channel to cut on one colour instead of brightness.
4. Outputs: the black and white picture, a mask and an info line.

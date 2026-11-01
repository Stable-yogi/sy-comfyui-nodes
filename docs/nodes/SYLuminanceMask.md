# Luminance Mask SY (`SYLuminanceMask`)

Source: `nodes/sy_luminance_mask.py`

**What it does:** Builds a mask from brightness (or from one colour channel). Pixels between low and high are white in the mask, the rest are black, with an optional soft fade and feather. The info line tells how much of the picture is selected.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image | IMAGE | yes | The picture or batch of pictures to measure the brightness of. | picture batch [B,H,W,3] |
| low | FLOAT | yes | Darkest brightness that still counts. 0 is black. | 0.0 to 1.0, step 0.01, default 0.0 |
| high | FLOAT | yes | Brightest brightness that still counts. 1 is white. | 0.0 to 1.0, step 0.01, default 1.0 |
| softness | FLOAT | yes | Width of the fade outside the band. 0 gives hard black and white. | 0.0 to 0.5, step 0.01, default 0.0 |
| invert | BOOLEAN | yes | Swap the mask so the chosen band becomes black. | default False |
| source | COMBO | no | What to measure: overall brightness, or one colour channel (red is good for skin, blue for sky). | one of: luminance, red, green, blue, brightest channel |
| feather | INT | no | Soften the finished mask by this many pixels, so it blends without a hard edge. 0 is off. | 0 to 512, step 1, default 0 |

Outputs: `MASK`, `STRING`

## How to use

1. Connect your picture to image.
2. Set low and high. Pixels with a brightness between the two turn white in the mask, the rest turn black.
3. Use softness for a fade at the band edges and feather to soften the finished mask. Turn invert on to swap the result.
4. In source, choose luminance or one colour channel. Red suits skin and blue suits sky.
The info output says how much of the picture is selected.

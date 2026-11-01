# Levels Adjust SY (`SYLevelsAdjust`)

Source: `nodes/sy_levels_adjust.py`

**What it does:** Black point, white point, gamma, contrast, brightness and saturation in one node. Default values change nothing. Add a mask to adjust only one area. The info line lists what was changed.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image | IMAGE | yes | The picture or batch of pictures to adjust. | picture batch [B,H,W,3] |
| brightness | FLOAT | yes | Adds light. Below 0 darkens, above 0 brightens. | -1.0 to 1.0, step 0.01, default 0.0 |
| contrast | FLOAT | yes | Spread between dark and light. 1 is unchanged, 0 is flat grey. | 0.0 to 3.0, step 0.01, default 1.0 |
| saturation | FLOAT | yes | Colour strength. 1 is unchanged, 0 is black and white. | 0.0 to 3.0, step 0.01, default 1.0 |
| gamma | FLOAT | yes | Middle tones. Above 1 brightens the shadows, below 1 darkens them. | 0.1 to 5.0, step 0.01, default 1.0 |
| black_point | FLOAT | no | Brightness that becomes pure black, for example 0.05. Fixes washed-out shadows. | 0.0 to 0.99, step 0.01, default 0.0 |
| white_point | FLOAT | no | Brightness that becomes pure white, for example 0.95. Fixes dull highlights. | 0.01 to 1.0, step 0.01, default 1.0 |
| mask | MASK | no | Optional. Adjust only where this mask is white. A different size is stretched to fit. | mask [B,H,W] |

Outputs: `IMAGE`, `STRING`

## How to use

1. Connect a picture or batch to image. The default values change nothing.
2. Set black_point and white_point to fix washed-out shadows and dull highlights, for example 0.05 and 0.95.
3. Then use gamma, contrast, brightness and saturation as needed.
4. Optional: connect a mask to adjust only the white area. The picture and an info line that lists what was changed come out.

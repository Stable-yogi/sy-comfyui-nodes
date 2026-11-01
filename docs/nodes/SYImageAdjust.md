# Image Adjust SY (`SYImageAdjust`)

Source: `nodes/sy_image_adjust.py`

**What it does:** One finishing node instead of five: tone (brightness, contrast, gamma), colour (saturation, hue, warmth, tint), sharpen, vignette and film grain. Each group has its own switch, plus a mask, a mix slider and an overall on/off. Every setting starts neutral, so nothing changes until you move one. The info line lists what was applied.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image | IMAGE | yes | The picture or batch of pictures to finish. | picture batch [B,H,W,3] |
| brightness | FLOAT | no | Adds light. Below 0 darkens, above 0 brightens. Try 0.05. | -1.0 to 1.0, step 0.01, default 0.0 |
| contrast | FLOAT | no | Spread between dark and light. 1 is unchanged, 1.15 is a gentle boost. | 0.0 to 3.0, step 0.01, default 1.0 |
| gamma | FLOAT | no | Middle tones. Above 1 lifts the shadows, below 1 deepens them. | 0.1 to 5.0, step 0.01, default 1.0 |
| saturation | FLOAT | no | Colour strength. 1 is unchanged, 0 is black and white. | 0.0 to 3.0, step 0.01, default 1.0 |
| hue | FLOAT | no | Turns all colours round the colour wheel, in degrees. Brightness stays. | -180.0 to 180.0, step 1.0, default 0.0 |
| warmth | FLOAT | no | Above 0 makes the picture warmer (orange), below 0 cooler (blue). Try 0.1. | -1.0 to 1.0, step 0.01, default 0.0 |
| tint | FLOAT | no | Above 0 adds magenta, below 0 adds green. Fixes a colour cast. | -1.0 to 1.0, step 0.01, default 0.0 |
| sharpen | FLOAT | no | Edge sharpening amount. 0 is off, 0.5 is gentle, 1.5 is strong. | 0.0 to 3.0, step 0.05, default 0.0 |
| sharpen_radius | FLOAT | no | Size of the detail to sharpen, in pixels. Small = fine detail. | 0.3 to 10.0, step 0.1, default 1.5 |
| vignette | FLOAT | no | Darkens the corners. 0 is off, 0.3 is subtle, 1 is black corners. | 0.0 to 1.0, step 0.01, default 0.0 |
| vignette_size | FLOAT | no | How far the light reaches. Bigger = the dark edge moves outward. | 0.1 to 2.0, step 0.05, default 1.0 |
| grain | FLOAT | no | Film grain amount. 0 is off, 0.2 is subtle. | 0.0 to 1.0, step 0.01, default 0.0 |
| grain_size | INT | no | Grain clump size in pixels. 1 is fine, 3 is coarse. | 1 to 8, default 1 |
| grain_seed | INT | no | Same seed = the same grain pattern. Change it for a different pattern. | 0 to 4294967295, default 0 |
| use_tone | BOOLEAN | no | Switch the tone group (brightness, contrast, gamma) on or off. | default True |
| use_colour | BOOLEAN | no | Switch the colour group (saturation, hue, warmth, tint) on or off. | default True |
| use_sharpen | BOOLEAN | no | Switch the sharpen step on or off. | default True |
| use_vignette | BOOLEAN | no | Switch the vignette on or off. | default True |
| use_grain | BOOLEAN | no | Switch the film grain on or off. | default True |
| mix | FLOAT | no | How much of the effect to use. 1 = full effect, 0.5 = half, 0 = original picture. | 0.0 to 1.0, step 0.01, default 1.0 |
| mask | MASK | no | Optional. White = apply the effect, black = keep the original. A different size is stretched to fit. | mask [B,H,W] |
| enabled | BOOLEAN | no | Turn off to pass the picture through untouched (handy to compare before and after). | default True |

Outputs: `IMAGE`, `STRING`

## How to use

1. Connect a picture or batch to image. Every setting starts neutral, so nothing changes until you move one.
2. Change the groups you want: tone (brightness, contrast, gamma), colour (saturation, hue, warmth, tint), sharpen, vignette, grain. Each group has its own use_ switch.
3. mix sets how much of the effect is used (0 is the original). Optional: connect a mask, where white means apply. enabled off passes the picture through untouched.
4. The finished picture and an info line that lists what was changed come out.

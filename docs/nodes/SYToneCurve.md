# Tone Curve SY (`SYToneCurve`)

Source: `nodes/sy_tone_curve.py`

**What it does:** Levels, curves, auto contrast and a histogram in one node. Auto levels stretch a flat picture (per picture or for the whole batch, optionally per colour channel to remove a colour cast), black point, white point and midtone fine-tune it, and a tone curve (type points or pick a preset) shapes the contrast. Every setting starts neutral. Outputs the picture, a histogram picture (before in grey, after in colour) and an info line.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image | IMAGE | yes | The picture or batch of pictures to adjust. | picture batch [B,H,W,3] |
| auto_levels | COMBO | no | Stretch dark and bright ends to fill the range. Per picture or one setting for the batch. | one of: off, per picture, whole batch |
| clip_percent | FLOAT | no | Percent of the darkest and brightest pixels ignored when auto levelling. | 0.0 to 10.0, step 0.1, default 0.5 |
| black_point | FLOAT | no | This brightness becomes pure black. 0 is unchanged. | 0.0 to 0.95, step 0.01, default 0.0 |
| white_point | FLOAT | no | This brightness becomes pure white. 1 is unchanged. | 0.05 to 1.0, step 0.01, default 1.0 |
| midtone | FLOAT | no | Middle tones. Above 1 brightens them, below 1 darkens them. 1 is unchanged. | 0.1 to 5.0, step 0.01, default 1.0 |
| curve_points | STRING | no | Tone curve as x,y pairs from 0 to 1, e.g. 0,0 0.25,0.2 0.75,0.85 1,1. Empty = no curve. | default '', multiline |
| curve_preset | COMBO | no | Ready-made curve. Used only when the curve points box is empty. | one of: none, soft contrast, strong contrast, lift shadows, fade blacks, invert |
| per_channel | BOOLEAN | no | Auto levels on red, green and blue separately. Also removes a colour cast. | default False |
| mix | FLOAT | no | How much of the effect to use. 1 = full effect, 0.5 = half, 0 = original picture. | 0.0 to 1.0, step 0.01, default 1.0 |
| mask | MASK | no | Optional. White = apply the effect, black = keep the original. A different size is stretched to fit. | mask [B,H,W] |
| enabled | BOOLEAN | no | Turn off to pass the picture through untouched (handy to compare before and after). | default True |
| histogram_size | INT | no | Width of the histogram picture in pixels (height is half). | 64 to 512, step 1, default 256 |

Outputs: `IMAGE`, `IMAGE`, `STRING`

# Split Toning SY (`SYSplitToning`)

Source: `nodes/sy_split_toning.py`

**What it does:** Tints the dark parts of the picture one colour and the bright parts another, the classic film look. The picture keeps its own brightness, only the colour shifts. Strength 0 does nothing.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image | IMAGE | yes | The picture or pictures to tint. | picture batch [B,H,W,3] |
| shadow_hue | FLOAT | yes | Colour of the dark parts as a colour-wheel angle. 210 is blue. | 0.0 to 360.0, step 1.0, default 210.0 |
| shadow_saturation | FLOAT | yes | How strong the dark-part tint is. 0 means no tint. | 0.0 to 1.0, step 0.01, default 0.25 |
| highlight_hue | FLOAT | yes | Colour of the bright parts as a colour-wheel angle. 40 is warm orange. | 0.0 to 360.0, step 1.0, default 40.0 |
| highlight_saturation | FLOAT | yes | How strong the bright-part tint is. 0 means no tint. | 0.0 to 1.0, step 0.01, default 0.25 |
| balance | FLOAT | yes | Moves the split: below 0 towards the shadows, above 0 towards the highlights. | -1.0 to 1.0, step 0.01, default 0.0 |
| strength | FLOAT | yes | Overall mix of the effect. 0 returns the original picture. | 0.0 to 1.0, step 0.01, default 1.0 |

Outputs: `IMAGE`

## How to use

1. Connect a picture or batch to **image**.
2. Choose a cool hue for **shadow_hue** and a warm hue for **highlight_hue** (or any pair you like).
3. Raise the two saturations until the tint is visible but gentle.
4. Use **balance** to decide where the split sits: a positive value moves the split point towards the highlights, so more of the picture gets the shadow tint.
5. The output **IMAGE** has the same size; an alpha channel is passed through.

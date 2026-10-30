# Grayscale SY (`SYGrayscale`)

Source: `nodes/sy_grayscale.py`

**What it does:** Turns a picture into shades of grey. Pick how brightness is measured and how strong the effect is.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image | IMAGE | yes | The picture or batch of pictures to turn grey. | picture batch [B,H,W,3] |
| method | COMBO | yes | How brightness is measured. rec709 matches how the eye sees modern screens; lightness keeps contrast flat. | one of: rec709, rec601, average, lightness |
| strength | FLOAT | yes | 0 keeps the colours, 1 is fully grey. | 0.0 to 1.0, step 0.01, default 1.0 |

Outputs: `IMAGE`

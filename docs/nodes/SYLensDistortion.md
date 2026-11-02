# Lens Distortion SY (`SYLensDistortion`)

Source: `nodes/sy_lens_distortion.py`

**What it does:** Bends the picture like a camera lens. Positive amounts bulge the middle outwards (barrel), negative amounts pinch it inwards (pincushion). 0 leaves the picture exactly as it is.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image | IMAGE | yes | The picture or pictures to bend. | picture batch [B,H,W,3] |
| amount | FLOAT | yes | Above 0 bulges the middle (barrel). Below 0 pinches it (pincushion). 0 does nothing. | -1.0 to 1.0, step 0.01, default 0.2 |
| edge | COMBO | yes | What fills the border when the bend pulls in space: stretch the edge, black, or mirror the picture. | one of: stretch, black, mirror |

Outputs: `IMAGE`

## How to use

1. Connect a picture or batch to **image**.
2. Set **amount**: positive for barrel, negative for pincushion.
3. Pick **edge**: stretch repeats the border pixels, black leaves black, mirror reflects the picture.
4. The output **IMAGE** has the same size as the input.

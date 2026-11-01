# Emboss SY (`SYEmboss`)

Source: `nodes/sy_emboss.py`

**What it does:** Turns a picture into a grey relief, as if pressed into metal. The angle sets where the light comes from. Adds a mix slider (blend the relief into the original), a mask, an on/off switch and an info line, and keeps transparency.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image | IMAGE | yes | The picture or batch of pictures to change. | picture batch [B,H,W,3] |
| strength | FLOAT | yes | How deep the relief looks. 0 gives flat grey. | 0.0 to 10.0, step 0.1, default 1.0 |
| angle | COMBO | yes | The side the light comes from. | one of: top_left, top, top_right, left, right, bottom_left, bottom, bottom_right |
| mask | MASK | no | Optional. White = apply the effect, black = keep the original. A different size is stretched to fit. | mask [B,H,W] |
| mix | FLOAT | no | How much of the effect to use. 1 = full effect, 0.5 = half, 0 = original picture. | 0.0 to 1.0, step 0.01, default 1.0 |
| enabled | BOOLEAN | no | Turn off to pass the picture through untouched (handy to compare before and after). | default True |

Outputs: `IMAGE`, `STRING`

## How to use

1. Connect your picture to image.
2. Set strength and angle (where the light comes from).
3. Lower mix to blend the relief into the original. Optional: connect a mask or turn enabled off.
4. The result comes out as image. Transparency is kept.

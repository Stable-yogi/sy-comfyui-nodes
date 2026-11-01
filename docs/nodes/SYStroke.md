# Stroke SY (`SYStroke`)

Source: `nodes/sy_layer_styles.py`

**What it does:** Draws an outline along the edge of the shape: outside it, inside it, or centred on the edge. The shape is the mask, or the transparent background of the picture if no mask is given. With a mask, everything outside the mask becomes transparent. The result is a picture with transparency, plus the effect as a mask.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image | IMAGE | yes | The picture (RGB or with transparency). | picture batch [B,H,W,3] |
| width | INT | yes | Thickness of the outline, in pixels. | 1 to 128, default 6 |
| position | COMBO | yes | Where the outline sits: outside the shape, inside it, or centred on the edge. | one of: outside, inside, centre |
| opacity | FLOAT | yes | How strong the outline is. 0 is invisible. | 0.0 to 1.0, step 0.01, default 1.0 |
| color | COMBO | yes | Colour of the effect. Choose 'custom' to use the three numbers below. | one of: black, white, gold, red, blue, green, grey, custom |
| mask | MASK | no | The shape. Empty: the transparent background of the picture is used. | mask [B,H,W] |
| custom_r | INT | no | Red part of the custom colour, 0 to 255. | 0 to 255, default 0 |
| custom_g | INT | no | Green part of the custom colour, 0 to 255. | 0 to 255, default 0 |
| custom_b | INT | no | Blue part of the custom colour, 0 to 255. | 0 to 255, default 0 |

Outputs: `IMAGE`, `MASK`

## How to use

1. Connect the picture to image. Optionally connect a mask as the shape. Without a mask, the transparent background of the picture is the shape.
2. Set width, position (outside, inside or centre) and opacity.
3. Pick a colour, or choose custom and set custom_r, custom_g and custom_b.
4. Outputs: the picture with the outline and the effect_mask.

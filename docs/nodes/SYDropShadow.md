# Drop Shadow SY (`SYDropShadow`)

Source: `nodes/sy_layer_styles.py`

**What it does:** Adds a soft shadow behind the shape, moved by offset_x and offset_y. The shape is the mask, or the transparent background of the picture if no mask is given. With a mask, everything outside the mask becomes transparent. The result is a picture with transparency, plus the effect as a mask.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image | IMAGE | yes | The picture (RGB or with transparency). | picture batch [B,H,W,3] |
| offset_x | INT | yes | Move the shadow right (plus) or left (minus), in pixels. | -512 to 512, default 12 |
| offset_y | INT | yes | Move the shadow down (plus) or up (minus), in pixels. | -512 to 512, default 12 |
| blur | INT | yes | How soft the shadow edge is, in pixels. 0 is hard. | 0 to 256, default 16 |
| spread | INT | yes | Make the shadow bigger (plus) or smaller (minus) before it is blurred. | -64 to 64, default 0 |
| opacity | FLOAT | yes | How strong the shadow is. 0 is invisible. | 0.0 to 1.0, step 0.01, default 0.6 |
| color | COMBO | yes | Colour of the effect. Choose 'custom' to use the three numbers below. | one of: black, white, gold, red, blue, green, grey, custom |
| mask | MASK | no | The shape. Empty: the transparent background of the picture is used. | mask [B,H,W] |
| custom_r | INT | no | Red part of the custom colour, 0 to 255. | 0 to 255, default 0 |
| custom_g | INT | no | Green part of the custom colour, 0 to 255. | 0 to 255, default 0 |
| custom_b | INT | no | Blue part of the custom colour, 0 to 255. | 0 to 255, default 0 |

Outputs: `IMAGE`, `MASK`

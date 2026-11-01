# Outer Glow SY (`SYOuterGlow`)

Source: `nodes/sy_layer_styles.py`

**What it does:** Adds a soft glow around the outside of the shape. The shape is the mask, or the transparent background of the picture if no mask is given. With a mask, everything outside the mask becomes transparent. The result is a picture with transparency, plus the effect as a mask.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image | IMAGE | yes | The picture (RGB or with transparency). | picture batch [B,H,W,3] |
| size | INT | yes | How far the glow reaches, in pixels. | 1 to 256, default 24 |
| spread | FLOAT | yes | How much of the glow is solid near the shape. 0 is all soft. | 0.0 to 1.0, step 0.01, default 0.3 |
| opacity | FLOAT | yes | How strong the glow is. 0 is invisible. | 0.0 to 1.0, step 0.01, default 0.75 |
| color | COMBO | yes | Colour of the effect. Choose 'custom' to use the three numbers below. | one of: black, white, gold, red, blue, green, grey, custom |
| mask | MASK | no | The shape. Empty: the transparent background of the picture is used. | mask [B,H,W] |
| custom_r | INT | no | Red part of the custom colour, 0 to 255. | 0 to 255, default 0 |
| custom_g | INT | no | Green part of the custom colour, 0 to 255. | 0 to 255, default 0 |
| custom_b | INT | no | Blue part of the custom colour, 0 to 255. | 0 to 255, default 0 |

Outputs: `IMAGE`, `MASK`

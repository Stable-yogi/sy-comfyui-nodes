# Mask Tools SY (`SYMaskTools`)

Source: `nodes/sy_mask_tools.py`

**What it does:** Cleans up a mask in one node: make it hard (threshold), grow or shrink it, feather the edge, invert it, in the right order. Connect the picture to see the mask tinted on it. The info line says what was done and how much of the picture the mask covers before and after. All settings start neutral.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| mask | MASK | yes | The mask to clean up. | mask [B,H,W] |
| threshold | FLOAT | no | Makes the mask hard black and white at this level. 0 = off, 0.5 is typical. | 0.0 to 1.0, step 0.01, default 0.0 |
| grow | INT | no | Pixels to grow (above 0) or shrink (below 0) the white area. Try 8. | -512 to 512, default 0 |
| feather | INT | no | Soft edge in pixels, applied after grow. Try 12. | 0 to 512, default 0 |
| edge | COMBO | no | centred = soft edge straddles the old edge. inside only = no halo outside the subject. | one of: centred, inside only, outside only |
| invert | BOOLEAN | no | Flip white and black after all other steps. | default False |
| invert_first | BOOLEAN | no | Flip white and black before the other steps instead of after. | default False |
| image | IMAGE | no | Optional. The preview shows the mask tinted on this picture, and the mask is stretched to its size. | picture batch [B,H,W,3] |
| overlay_colour | COMBO | no | Tint colour for the preview. | one of: red, green, blue, yellow, magenta, cyan |
| overlay_opacity | FLOAT | no | How strong the tint is in the preview. 0.5 is half. | 0.0 to 1.0, step 0.05, default 0.5 |

Outputs: `MASK`, `IMAGE`, `STRING`

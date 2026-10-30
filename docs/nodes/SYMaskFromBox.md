# MaskFromBox SY (`SYMaskFromBox`)

Source: `nodes/sy_mask_from_box.py`

**What it does:** Makes a mask that is white inside a rectangle and black elsewhere. Parts outside the canvas are cut off.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| x | INT | yes | Left edge of the box in pixels. | -16384 to 16384, step 1, default 0 |
| y | INT | yes | Top edge of the box in pixels. | -16384 to 16384, step 1, default 0 |
| box_width | INT | yes | Width of the box in pixels. | 0 to 16384, step 1, default 256 |
| box_height | INT | yes | Height of the box in pixels. | 0 to 16384, step 1, default 256 |
| canvas_width | INT | yes | Width of the mask in pixels. | 1 to 16384, step 1, default 1024 |
| canvas_height | INT | yes | Height of the mask in pixels. | 1 to 16384, step 1, default 1024 |

Outputs: `MASK`

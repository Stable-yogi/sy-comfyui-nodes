# MaskToBox SY (`SYMaskToBox`)

Source: `nodes/sy_mask_to_box.py`

**What it does:** Finds the rectangle around the white part of a mask and returns x, y, width, height, with optional padding and an option to make the size a multiple of 8, 16 or 64 for samplers. The info output explains the box and warns when the mask is empty.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| mask | MASK | yes | The mask to measure. A batch gives one box around all of them. | mask [B,H,W] |
| padding | INT | yes | Extra pixels added around the box. The box stays inside the image. | 0 to 4096, step 1, default 0 |
| threshold | FLOAT | yes | Mask values at or above this count as white. | 0.01 to 1.0, step 0.01, default 0.5 |
| on_empty | COMBO | yes | When nothing is white: use the whole image, or stop with an error. | one of: whole_image, error |
| multiple_of | INT | no | Grow the box so width and height are multiples of this, for example 8 or 64. 1 keeps the exact box. | 1 to 512, step 1, default 1 |

Outputs: `INT`, `INT`, `INT`, `INT`, `STRING`

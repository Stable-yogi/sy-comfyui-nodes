# Pixel Count Info SY (`SYPixelCountInfo`)

Source: `nodes/sy_pixel_count_info.py`

**What it does:** Shows how big a picture size is: megapixels, total pixels and shape. Also gives a text line you can show or save. Adds an optional fit: scale to a target number of megapixels and/or snap to a multiple of 8, 16, 32 or 64, with the new width and height as outputs and a plain note about size problems.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| width | INT | yes | Width in pixels. | 0 to 1000000, default 1024 |
| height | INT | yes | Height in pixels. | 0 to 1000000, default 1024 |
| snap_to | COMBO | no | Round the size to a multiple of this (8, 16, 32, 64). off leaves it alone. | one of: off, 8, 16, 32, 64 |
| snap_direction | COMBO | no | How snap_to rounds: nearest multiple, always down, or always up. | one of: nearest, down, up |
| target_mp | FLOAT | no | 0 = off. 1.0 scales the size to about 1 megapixel, same shape. | 0.0 to 1000.0, step 0.05, default 0.0 |

Outputs: `FLOAT`, `INT`, `STRING`, `INT`, `INT`, `STRING`

## How to use

1. Enter width and height.
2. Read the megapixels, the total pixels and the report text.
3. Optional fit: set target_mp to scale to about that many megapixels (0 is off), and snap_to with snap_direction to round to a multiple of 8, 16, 32 or 64.
4. Use out_width and out_height for the new size. fit_note explains size problems in plain words.

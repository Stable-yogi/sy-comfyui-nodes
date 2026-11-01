# MaskFromBox SY (`SYMaskFromBox`)

Source: `nodes/sy_mask_from_box.py`

**What it does:** Makes a mask that is white inside a rectangle and black elsewhere. Parts outside the canvas are cut off. Connect a picture to copy its size, place the box by its centre, feather it or invert it. The info line tells if the box was cut off or missed the canvas.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| x | INT | yes | Left edge of the box in pixels. | -16384 to 16384, step 1, default 0 |
| y | INT | yes | Top edge of the box in pixels. | -16384 to 16384, step 1, default 0 |
| box_width | INT | yes | Width of the box in pixels. | 0 to 16384, step 1, default 256 |
| box_height | INT | yes | Height of the box in pixels. | 0 to 16384, step 1, default 256 |
| canvas_width | INT | yes | Width of the mask in pixels. | 1 to 16384, step 1, default 1024 |
| canvas_height | INT | yes | Height of the mask in pixels. | 1 to 16384, step 1, default 1024 |
| size_from | IMAGE | no | Optional picture whose width and height are used as the canvas. Stops size mismatches. | picture batch [B,H,W,3] |
| anchor | COMBO | no | top-left: x and y are the box corner. centre: x and y are the middle of the box. | one of: top-left, centre |
| feather | INT | no | Soften the box edge by this many pixels. 0 is a hard edge. | 0 to 512, step 1, default 0 |
| invert | BOOLEAN | no | Swap white and black: everything except the box is selected. | default False |

Outputs: `MASK`, `STRING`

## How to use

1. Set x, y, box_width and box_height for the rectangle. The inside is white, the rest is black.
2. Set canvas_width and canvas_height, or connect a picture to size_from to copy its size.
3. Set anchor to centre if x and y mean the middle of the box instead of its top-left corner.
4. Optional: feather softens the edge, invert swaps white and black.
The info output says if the box was cut off or missed the canvas.

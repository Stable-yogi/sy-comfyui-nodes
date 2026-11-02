# Mask Shape Draw SY (`SYMaskShapeDraw`)

Source: `nodes/sy_mask_shape_draw.py`

**What it does:** Draws a mask from numbers: rectangle, ellipse, rounded rectangle, or a linear or radial gradient. Set the size and place, soften the edge, rotate it, or flip it.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| width | INT | yes | Width of the mask in pixels. | 8 to 8192, default 1024 |
| height | INT | yes | Height of the mask in pixels. | 8 to 8192, default 1024 |
| shape | COMBO | yes | What to draw. Gradients fade from 0 to 1 instead of drawing a solid shape. | one of: rectangle, ellipse, rounded rectangle, linear gradient, radial gradient |
| centre_x | FLOAT | yes | Horizontal middle of the shape. 0 is the left edge, 1 the right. | 0.0 to 1.0, step 0.01, default 0.5 |
| centre_y | FLOAT | yes | Vertical middle of the shape. 0 is the top edge, 1 the bottom. | 0.0 to 1.0, step 0.01, default 0.5 |
| size_x | FLOAT | yes | Width of the shape as a share of the picture width. For a linear gradient: length of the fade. | 0.0 to 1.0, step 0.01, default 0.5 |
| size_y | FLOAT | yes | Height of the shape as a share of the picture height. A linear gradient ignores it. | 0.0 to 1.0, step 0.01, default 0.5 |
| feather | FLOAT | yes | Soft edge width as a share of the shorter side. 0 gives a crisp edge. | 0.0 to 0.5, step 0.01, default 0.0 |
| angle | FLOAT | yes | Turns the shape or the gradient direction, in degrees. | 0.0 to 360.0, step 1.0, default 0.0 |
| invert | BOOLEAN | yes | On: swap black and white in the finished mask. | default False |

Outputs: `MASK`

## How to use

1. Set **width** and **height** to the size you need, for example the size of your picture.
2. Pick the **shape**.
3. Set **centre_x** and **centre_y** for where it sits, and **size_x** and **size_y** for how big it is.
4. Raise **feather** for a soft edge, and use **angle** to turn the shape or the gradient.
5. Turn **invert** on to swap black and white.
6. Use the output **MASK** like any other mask.

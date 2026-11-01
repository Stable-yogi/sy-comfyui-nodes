# Gradient Image SY (`SYGradientImage`)

Source: `nodes/sy_gradient_image.py`

**What it does:** Makes a new picture that fades from one colour to another, in a straight line or from the centre outward. Connect a picture to copy its size, and pick smooth for a softer start and end. The mask shows the fade position.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| width | INT | yes | Width of the new picture in pixels. | 1 to 8192, step 1, default 1024 |
| height | INT | yes | Height of the new picture in pixels. | 1 to 8192, step 1, default 1024 |
| shape | COMBO | yes | linear fades along a line; radial fades from the centre to the corners. | one of: linear, radial |
| colour_a | STRING | yes | Starting colour, as 3 or 6 hex digits like a web colour. | default '#1b1b2f' |
| colour_b | STRING | yes | Ending colour, as 3 or 6 hex digits like a web colour. | default '#f5d58a' |
| angle | FLOAT | yes | Linear only. 0 goes left to right, 90 goes top to bottom. | -360.0 to 360.0, step 1.0, default 0.0 |
| batch_size | INT | yes | How many identical pictures to make. | 1 to 64, step 1, default 1 |
| size_from | IMAGE | no | Optional picture whose width and height are copied. The width and height above are then ignored. | picture batch [B,H,W,3] |
| ease | COMBO | no | linear: even fade. smooth: slow start and end, which hides the line where the fade begins. | one of: linear, smooth |

Outputs: `IMAGE`, `MASK`, `STRING`

## How to use

1. Pick shape: linear (a straight fade) or radial (from the centre out). Set colour_a and colour_b as hex colours.
2. Set width and height, or connect a picture to size_from to copy its size (width and height are then ignored).
3. For linear, angle sets the direction. 0 goes left to right, 90 goes top to bottom. Choose smooth in ease for a softer start and end.
4. The new picture comes out, plus a mask that shows the fade position. batch_size makes identical copies.

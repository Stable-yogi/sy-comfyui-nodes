# Layout Box SY (`SYLayoutBox`)

Source: `nodes/sy_layout_box.py`

**What it does:** Makes one named box for a picture layout. Join several with Layout Boxes Merge, then check or preview them.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| x | INT | yes | Distance of the box left edge from the left of the picture, in pixels. | 0 to 16384, default 0 |
| y | INT | yes | Distance of the box top edge from the top of the picture, in pixels. | 0 to 16384, default 0 |
| w | INT | yes | Width of the box in pixels. | 1 to 16384, default 256 |
| h | INT | yes | Height of the box in pixels. | 1 to 16384, default 256 |
| label | STRING | yes | Short name shown on the box, up to 80 characters. | default 'box' |
| colour | COMBO | yes | Colour the preview uses to draw this box. | one of: red, orange, yellow, green, cyan, blue, purple, pink, white, black |

Outputs: `STRING`

# Layout Box Draw SY (`SYLayoutBoxDraw`)

Source: `nodes/sy_layout_box_draw.py`

**What it does:** Draw layout boxes with the mouse on a small canvas inside the node. The boxes come out as box text for Layout Boxes Merge, Preview and Check, and for a MOSS layout prompt.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| canvas_width | INT | yes | Width of the picture the boxes are for, in pixels. The canvas keeps this shape. | 1 to 16384, default 1024 |
| canvas_height | INT | yes | Height of the picture the boxes are for, in pixels. | 1 to 16384, default 1024 |
| boxes | STRING | yes | The boxes as a JSON list. The canvas writes this for you; you can also paste a list here. | default '[]', multiline |
| snap_to | INT | no | Round every box to a multiple of this, for example 8 or 64. 1 keeps your numbers. | 1 to 512, default 1 |

Outputs: `STRING`, `STRING`, `INT`

## How to use

1. Set canvas_width and canvas_height to the size of the picture you plan to make. The canvas shows that shape.
2. Drag on the canvas to draw a box. Drag inside a box to move it. Drag a gold corner square to resize it.
3. Double-click a box (or press Name) to give it a label. The Colour button picks the colour; with a box selected it changes that box. Press Delete, the Delete button, or right-click a box to remove it. Clear removes all.
4. Optional: set snap_to to 8 or 64 so every box lands on a grid.
5. Connect layout_boxes to Layout Boxes Merge, Preview or Check. A box that leaves the picture, a bad colour or more than 64 boxes is refused with a plain message.

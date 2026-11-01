# Layout Boxes Preview SY (`SYLayoutBoxesPreview`)

Source: `nodes/sy_layout_boxes_preview.py`

**What it does:** Draws layout boxes and their labels over a picture, or over a blank canvas when no picture is connected. Can number the boxes, tint them, and tells you which boxes fell outside the picture.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| layout_boxes | STRING | yes | The box list as JSON text. Connect a Layout Box or Merge node, or paste it. | default '', multiline |
| line_width | INT | yes | Thickness of the box outline in pixels. | 1 to 32, default 3 |
| show_labels | BOOLEAN | yes | Write each box label above its top left corner. | default True |
| blank_width | INT | yes | Width of the blank canvas. Used only when no picture is connected. | 8 to 16384, default 1024 |
| blank_height | INT | yes | Height of the blank canvas. Used only when no picture is connected. | 8 to 16384, default 1024 |
| image | IMAGE | no | Optional picture to draw on. Leave it out to use a blank canvas. | picture batch [B,H,W,3] |
| fill_opacity | FLOAT | no | Tint inside each box. 0 is outline only, 0.3 is a light tint, 1 is solid. | 0.0 to 1.0, step 0.05, default 0.0 |
| show_numbers | BOOLEAN | no | Put the box number (1, 2, 3 ...) before its label, to match the numbers in check reports. | default False |

Outputs: `IMAGE`, `STRING`

## How to use

1. Connect the box list to layout_boxes, or paste it as JSON text.
2. Connect a picture to image to draw on it. Without one, a blank canvas of blank_width and blank_height is used.
3. Set line_width and show_labels. Optional: fill_opacity tints the inside of each box, and show_numbers adds the box number to match the check reports.
4. The picture with the boxes comes out, plus an info line that lists boxes that fell outside the picture.

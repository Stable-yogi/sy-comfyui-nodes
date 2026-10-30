# Layout Boxes Preview SY (`SYLayoutBoxesPreview`)

Source: `nodes/sy_layout_boxes_preview.py`

**What it does:** Draws layout boxes and their labels over a picture, or over a blank canvas when no picture is connected.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| layout_boxes | STRING | yes | The box list as JSON text. Connect a Layout Box or Merge node, or paste it. | default '', multiline |
| line_width | INT | yes | Thickness of the box outline in pixels. | 1 to 32, default 3 |
| show_labels | BOOLEAN | yes | Write each box label above its top left corner. | default True |
| blank_width | INT | yes | Width of the blank canvas. Used only when no picture is connected. | 8 to 16384, default 1024 |
| blank_height | INT | yes | Height of the blank canvas. Used only when no picture is connected. | 8 to 16384, default 1024 |
| image | IMAGE | no | Optional picture to draw on. Leave it out to use a blank canvas. | picture batch [B,H,W,3] |

Outputs: `IMAGE`

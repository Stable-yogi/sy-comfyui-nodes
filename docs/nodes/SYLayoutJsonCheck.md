# Layout JSON Check SY (`SYLayoutJsonCheck`)

Source: `nodes/sy_layout_json_check.py`

**What it does:** Checks a list of layout boxes: valid JSON, numbers, inside the picture, real size, short labels. Gives true or false and a report. Also hands back a fixed list (cut to fit the picture) and can warn when numbers are not a multiple of 8 or 64.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| layout_boxes | STRING | yes | The box list as JSON text. Connect a Layout Box or Merge node, or paste it. | default '', multiline |
| canvas_width | INT | yes | Width of the picture the boxes must fit in, in pixels. | 1 to 16384, default 1024 |
| canvas_height | INT | yes | Height of the picture the boxes must fit in, in pixels. | 1 to 16384, default 1024 |
| warn_overlap | BOOLEAN | yes | Add a warning when two boxes cover the same area. A warning does not make it invalid. | default True |
| warn_multiple_of | INT | no | Warn for numbers that are not a multiple of this, for example 8 or 64. 1 turns it off. | 1 to 512, default 1 |

Outputs: `BOOLEAN`, `STRING`, `STRING`, `STRING`

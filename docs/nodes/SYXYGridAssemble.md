# XY Grid Assemble SY (`SYXYGridAssemble`)

Source: `nodes/sy_xy_grid_assemble.py`

**What it does:** Builds one grid picture from a batch, with the X values across the top and the Y values down the side.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| images | IMAGE | yes | The pictures, row by row: X changes fastest. The count must be X count times Y count. | picture batch [B,H,W,3] |
| x_labels | STRING | yes | Labels across the top, one per line. Empty means one column and no header. | default '', multiline |
| y_labels | STRING | yes | Labels down the side, one per line. Empty means one row and no side labels. | default '', multiline |
| gap | INT | yes | Space in pixels between pictures. | 0 to 256, default 8 |
| padding | INT | yes | Space in pixels around the whole grid. | 0 to 256, default 12 |
| background | STRING | yes | Grid colour: black, white, gray, dark_gray, red, green, blue, gold or six hex digits. | default 'dark_gray' |
| label_size | INT | yes | Label text height in pixels. | 8 to 96, default 24 |

Outputs: `IMAGE`

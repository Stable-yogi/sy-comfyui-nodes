# XY Label Strip SY (`SYXYLabelStrip`)

Source: `nodes/sy_xy_label_strip.py`

**What it does:** Writes the XY grid as a Markdown table. Each cell shows its picture number, so you can match it to the batch.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| x_values | STRING | yes | The X list, one value per line. | default '', multiline |
| y_values | STRING | yes | The Y list, one value per line. Empty means a single row. | default '', multiline |
| x_name | STRING | yes | Name of the X axis, shown in the table corner. | default 'X' |
| y_name | STRING | yes | Name of the Y axis, shown in the table corner. | default 'Y' |

Outputs: `STRING`

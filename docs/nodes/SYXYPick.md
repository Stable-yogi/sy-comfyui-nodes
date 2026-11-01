# XY Pick SY (`SYXYPick`)

Source: `nodes/sy_xy_pick.py`

**What it does:** Picks one cell of an XY grid from a running index. Feed it a counter and auto-queue to render the whole grid. Also gives a plain label such as 'cell 2 of 6: X=b, Y=p' and a flag for the last cell. Optionally stays on the last cell instead of stopping with an error.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| x_values | STRING | yes | The X list, one value per line. Empty means a single column. | default '', multiline |
| y_values | STRING | yes | The Y list, one value per line. Empty means a single row. | default '', multiline |
| index | INT | yes | Cell number from 0, going across each row first. | 0 to 2147483647, default 0 |
| wrap | BOOLEAN | yes | On: an index past the end starts again at 0. Off: it stops with an error. | default False |
| clamp_to_last | BOOLEAN | no | On: an index past the end stays on the last cell. Ignored when wrap is on. | default False |

Outputs: `STRING`, `STRING`, `INT`, `INT`, `INT`, `STRING`, `BOOLEAN`

## How to use

1. Type x_values and y_values, one per line.
2. Feed index from a counter and use auto-queue to render the whole grid. Index counts across each row first.
3. Turn on wrap to start again after the end, or clamp_to_last to stay on the last cell. Otherwise it stops with an error.
4. Outputs: x_value, y_value, both indexes, the total, a label and is_last.

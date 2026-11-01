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

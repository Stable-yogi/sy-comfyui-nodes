# LinePick SY (`SYLinePick`)

Source: `nodes/sy_line_pick.py`

**What it does:** Takes one line from a text. Count from the top with 0, 1, 2 or from the bottom with -1, -2.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| text | STRING | yes | The text with several lines. | default '', multiline |
| index | INT | yes | Line to take, counting from 0. Negative counts from the end. | -100000 to 100000, default 0 |
| skip_blank | BOOLEAN | yes | Ignore empty lines when counting. | default True |

Outputs: `STRING`, `INT`

# CyclePick SY (`SYCyclePick`)

Source: `nodes/sy_cycle_pick.py`

**What it does:** Picks one line from a list using a counter. When the counter passes the end it starts again from the first line.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| items | STRING | yes | One item per line. Blank lines are skipped. | default '', multiline |
| counter | INT | yes | Which item to take, counting from 0. It goes round when too big. | -2147483648 to 2147483647, default 0 |

Outputs: `STRING`, `INT`, `INT`

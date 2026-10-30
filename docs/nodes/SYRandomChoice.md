# Random Choice SY (`SYRandomChoice`)

Source: `nodes/sy_random_choice.py`

**What it does:** Picks one line out of your list of lines. The same seed always picks the same line.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| lines | STRING | yes | One choice per line. Empty lines are skipped. | default '', multiline |
| seed | INT | yes | Decides the pick. Change it to get another line. | 0 to 18446744073709551615, default 0 |

Outputs: `STRING`, `INT`

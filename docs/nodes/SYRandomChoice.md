# Random Choice SY (`SYRandomChoice`)

Source: `nodes/sy_random_choice.py`

**What it does:** Picks one line out of your list of lines. The same seed always picks the same line. Can instead walk the list in order (seed 0, 1, 2 ...), skips # comment lines, and the info line says which line was picked.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| lines | STRING | yes | One choice per line. Empty lines are skipped. | default '', multiline |
| seed | INT | yes | Decides the pick. Change it to get another line. | 0 to 18446744073709551615, default 0 |
| mode | COMBO | no | In order: seed 0 gives line 1, seed 1 gives line 2, and so on, then it starts over. | one of: random from seed, in order (seed 0 = first line) |
| skip_comments | BOOLEAN | no | On: lines that start with # are ignored. | default False |

Outputs: `STRING`, `INT`, `STRING`

# Select By Index Text SY (`SYSelectByIndexText`)

Source: `nodes/sy_select_by_index_text.py`

**What it does:** Picks one of up to 8 connected texts by number. 0 is the first connected text. Too big a number wraps to the start.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| index | INT | yes | Which connected text to send, from 0. Past the last one wraps to the first. | -2147483648 to 2147483647, default 0 |
| text_1 | STRING | no | Text number 1. Leave it unconnected to skip it. | default '' |
| text_2 | STRING | no | Text number 2. Leave it unconnected to skip it. | default '' |
| text_3 | STRING | no | Text number 3. Leave it unconnected to skip it. | default '' |
| text_4 | STRING | no | Text number 4. Leave it unconnected to skip it. | default '' |
| text_5 | STRING | no | Text number 5. Leave it unconnected to skip it. | default '' |
| text_6 | STRING | no | Text number 6. Leave it unconnected to skip it. | default '' |
| text_7 | STRING | no | Text number 7. Leave it unconnected to skip it. | default '' |
| text_8 | STRING | no | Text number 8. Leave it unconnected to skip it. | default '' |

Outputs: `STRING`, `INT`

# Select By Index Text SY (`SYSelectByIndexText`)

Source: `nodes/sy_select_by_index_text.py`

**What it does:** Picks one of up to 8 connected texts by number. 0 is the first connected text. Too big a number wraps to the start, stays on the last, or stops with a message. Empty texts can be skipped.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| index | INT | yes | Which connected text to send, from 0. Past the last one wraps to the first. | -2147483648 to 2147483647, default 0 |
| out_of_range | COMBO | no | wrap: go round. clamp: stay on the first or last. error: stop with a message. | one of: wrap, clamp, error |
| skip_empty | BOOLEAN | no | On ignores texts that are empty or only spaces, so an unused slot does not get picked. | default False |
| text_1 | STRING | no | Text number 1. Leave it unconnected to skip it. | default '' |
| text_2 | STRING | no | Text number 2. Leave it unconnected to skip it. | default '' |
| text_3 | STRING | no | Text number 3. Leave it unconnected to skip it. | default '' |
| text_4 | STRING | no | Text number 4. Leave it unconnected to skip it. | default '' |
| text_5 | STRING | no | Text number 5. Leave it unconnected to skip it. | default '' |
| text_6 | STRING | no | Text number 6. Leave it unconnected to skip it. | default '' |
| text_7 | STRING | no | Text number 7. Leave it unconnected to skip it. | default '' |
| text_8 | STRING | no | Text number 8. Leave it unconnected to skip it. | default '' |

Outputs: `STRING`, `INT`, `INT`, `STRING`

## How to use

1. Connect up to 8 texts to text_1 to text_8. Unconnected slots are skipped.
2. Set index. 0 is the first connected text.
3. Set out_of_range: wrap goes round, clamp stays on the first or last, error stops with a message.
4. Turn on skip_empty to ignore empty texts. Outputs: the picked text, its slot, the count and an info line.

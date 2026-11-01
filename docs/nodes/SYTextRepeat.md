# TextRepeat SY (`SYTextRepeat`)

Source: `nodes/sy_text_repeat.py`

**What it does:** Repeats a text a number of times. It can put a separator between copies and number each copy, starting at any number. Refuses results over 200000 characters, and the info line shows the size.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| text | STRING | yes | The text to repeat. | default '', multiline |
| count | INT | yes | How many copies to make. | 1 to 200, default 2 |
| separator | STRING | yes | Put between copies. Use a comma, a space or a new line. | default '\n' |
| numbered | BOOLEAN | yes | Start each copy with its number, like 1. text. | default False |
| start_at | INT | no | First number when numbered is on. Use 0 to count from zero. | 0 to 1000000, default 1 |

Outputs: `STRING`, `STRING`

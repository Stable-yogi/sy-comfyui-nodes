# TextRepeat SY (`SYTextRepeat`)

Source: `nodes/sy_text_repeat.py`

**What it does:** Repeats a text a number of times. It can put a separator between copies and number each copy.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| text | STRING | yes | The text to repeat. | default '', multiline |
| count | INT | yes | How many copies to make. | 1 to 200, default 2 |
| separator | STRING | yes | Put between copies. Use a comma, a space or a new line. | default '\n' |
| numbered | BOOLEAN | yes | Start each copy with its number, like 1. text. | default False |

Outputs: `STRING`

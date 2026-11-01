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

## How to use

1. Connect the text and set count (1 to 200).
2. Set separator between copies. The default is a new line.
3. Turn on numbered to start each copy with its number, and set start_at.
4. Results over 200000 characters are refused. The info line shows the result size.

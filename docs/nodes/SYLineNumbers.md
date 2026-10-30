# Line Numbers SY (`SYLineNumbers`)

Source: `nodes/sy_line_numbers.py`

**What it does:** Puts a number in front of every line of a text. Can skip empty lines and pad the numbers with zeros.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| text | STRING | yes | The text to number, one number per line. | default '', multiline |
| start | INT | yes | The number given to the first line. | -1000000 to 1000000, default 1 |
| separator | STRING | yes | Text placed between the number and the line. | default '. ' |
| pad_zeros | BOOLEAN | yes | On: fill numbers with leading zeros so they all have the same width. | default False |
| skip_empty | BOOLEAN | yes | On: empty lines get no number and are not counted. | default False |

Outputs: `STRING`, `INT`

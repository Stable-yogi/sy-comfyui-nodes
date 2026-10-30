# Text SY (`SYText`)

Source: `nodes/sy_text.py`

**What it does:** A multiline text box. The text goes out as it is. Turn on strip_lines to remove spaces at the end of each line.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| text | STRING | yes | The text to pass on, such as your prompt. | default '', multiline |
| strip_lines | BOOLEAN | yes | On: trim spaces at the start and end of every line. | default False |

Outputs: `STRING`

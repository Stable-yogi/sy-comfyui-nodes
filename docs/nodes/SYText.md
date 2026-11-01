# Text SY (`SYText`)

Source: `nodes/sy_text.py`

**What it does:** A multiline text box. The text goes out as it is. Optional clean-up: spaces at line ends, empty lines at the start and end, and hidden characters that sneak in when you paste from a web page. The info line shows the size.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| text | STRING | yes | The text to pass on, such as your prompt. | default '', multiline |
| strip_lines | BOOLEAN | yes | On: trim spaces at the start and end of every line. | default False |
| clean_invisible | BOOLEAN | no | On: remove zero-width characters and turn non-breaking spaces into normal spaces. | default False |
| strip_ends | BOOLEAN | no | On: remove empty lines and spaces at the very start and end of the text. | default False |

Outputs: `STRING`, `STRING`

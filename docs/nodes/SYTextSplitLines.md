# Text Split Lines SY (`SYTextSplitLines`)

Source: `nodes/sy_text_split_lines.py`

**What it does:** Splits text into lines. Gives the full list, one line picked by number (wraps around), and the line count. Can trim spaces and skip # comment lines, and the info line says which line was picked.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| text | STRING | yes | The text to split. One line becomes one item. | default '', multiline |
| index | INT | yes | Which line to pick, counting from 0. Too big a number wraps to the start. | -2147483648 to 2147483647, default 0 |
| skip_empty | BOOLEAN | yes | Leave out empty lines and lines with only spaces. | default True |
| trim_lines | BOOLEAN | no | On: remove spaces at the start and end of every line. | default False |
| skip_comments | BOOLEAN | no | On: lines that start with # are left out. | default False |

Outputs: `STRING`, `STRING`, `INT`, `STRING`

# Text Case Trim SY (`SYTextCaseTrim`)

Source: `nodes/sy_text_case_trim.py`

**What it does:** Changes upper and lower case and cleans up text: trims each line, collapses double spaces, removes empty lines.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| text | STRING | yes | The text to clean up. | default '', multiline |
| case | COMBO | yes | Letter case: keep as is, UPPER, lower, Title Case or Sentence case. | one of: keep, upper, lower, title, sentence |
| trim | BOOLEAN | yes | Remove spaces at the start and end of the text and of every line. | default True |
| collapse_spaces | BOOLEAN | yes | Turn several spaces in a row into one space. | default False |
| strip_empty_lines | BOOLEAN | yes | Remove lines that are empty or hold only spaces. | default False |

Outputs: `STRING`

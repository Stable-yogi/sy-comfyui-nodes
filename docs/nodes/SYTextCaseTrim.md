# Text Case Trim SY (`SYTextCaseTrim`)

Source: `nodes/sy_text_case_trim.py`

**What it does:** Changes upper and lower case and cleans up text: trims each line, collapses double spaces, removes empty lines. tidy_commas also fixes stray commas in a tag list ('a ,b,, c,' becomes 'a, b, c'). The info line says what changed.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| text | STRING | yes | The text to clean up. | default '', multiline |
| case | COMBO | yes | Letter case: keep as is, UPPER, lower, Title Case or Sentence case. | one of: keep, upper, lower, title, sentence |
| trim | BOOLEAN | yes | Remove spaces at the start and end of the text and of every line. | default True |
| collapse_spaces | BOOLEAN | yes | Turn several spaces in a row into one space. | default False |
| strip_empty_lines | BOOLEAN | yes | Remove lines that are empty or hold only spaces. | default False |
| tidy_commas | BOOLEAN | no | On: fix stray commas and spaces in a tag list, like 'a ,b,, c,' to 'a, b, c'. | default False |

Outputs: `STRING`, `STRING`

## How to use

1. Connect the text.
2. Pick case: keep, upper, lower, title or sentence.
3. Switch trim, collapse_spaces and strip_empty_lines as needed.
4. Turn on tidy_commas to fix a tag list like "a ,b,, c," into "a, b, c". The info line says what changed.

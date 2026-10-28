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

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | PASS | STRING=str '' |
| 2 | text = '' (empty) | PASS | STRING=str '' |
| 3 | case = 'upper' | PASS | STRING=str '' |
| 4 | case = 'lower' | PASS | STRING=str '' |
| 5 | case = 'title' | PASS | STRING=str '' |
| 6 | case = 'sentence' | PASS | STRING=str '' |
| 7 | trim = False | PASS | STRING=str '' |
| 8 | collapse_spaces = True | PASS | STRING=str '' |
| 9 | strip_empty_lines = True | PASS | STRING=str '' |

## Verdict

All 9 cases behaved as expected (9 passed, 0 rejected with a clear message).

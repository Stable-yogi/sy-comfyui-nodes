# Text Join SY (`SYTextJoin`)

Source: `nodes/sy_text_join.py`

**What it does:** Joins up to four texts into one, with a separator between them. Empty texts can be skipped.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| separator | STRING | yes | What goes between the texts. A comma and space is common. | default ', ' |
| skip_empty | BOOLEAN | yes | On: empty texts are left out so you get no double separators. | default True |
| text_a | STRING | no | The first text to join. Leave empty to skip it. | default '', multiline |
| text_b | STRING | no | The second text to join. Leave empty to skip it. | default '', multiline |
| text_c | STRING | no | The third text to join. Leave empty to skip it. | default '', multiline |
| text_d | STRING | no | The fourth text to join. Leave empty to skip it. | default '', multiline |

Outputs: `STRING`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | PASS | STRING=str '' |
| 2 | separator = '' (empty) | PASS | STRING=str '' |
| 3 | skip_empty = False | PASS | STRING=str ', , ,' |
| 4 | text_a = '' (empty) | PASS | STRING=str '' |
| 5 | text_b = '' (empty) | PASS | STRING=str '' |
| 6 | text_c = '' (empty) | PASS | STRING=str '' |
| 7 | text_d = '' (empty) | PASS | STRING=str '' |

## Verdict

All 7 cases behaved as expected (7 passed, 0 rejected with a clear message).

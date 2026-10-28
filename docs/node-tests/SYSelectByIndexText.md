# Select By Index Text SY (`SYSelectByIndexText`)

Source: `nodes/sy_select_by_index_text.py`

**What it does:** Picks one of up to 8 connected texts by number. 0 is the first connected text. Too big a number wraps to the start.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| index | INT | yes | Which connected text to send, from 0. Past the last one wraps to the first. | -2147483648 to 2147483647, default 0 |
| text_1 | STRING | no | Text number 1. Leave it unconnected to skip it. | default '' |
| text_2 | STRING | no | Text number 2. Leave it unconnected to skip it. | default '' |
| text_3 | STRING | no | Text number 3. Leave it unconnected to skip it. | default '' |
| text_4 | STRING | no | Text number 4. Leave it unconnected to skip it. | default '' |
| text_5 | STRING | no | Text number 5. Leave it unconnected to skip it. | default '' |
| text_6 | STRING | no | Text number 6. Leave it unconnected to skip it. | default '' |
| text_7 | STRING | no | Text number 7. Leave it unconnected to skip it. | default '' |
| text_8 | STRING | no | Text number 8. Leave it unconnected to skip it. | default '' |

Outputs: `STRING`, `INT`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | PASS | STRING=str 'test'; INT=int 0 |
| 2 | index = -2147483648 (min) | PASS | STRING=str 'test'; INT=int 0 |
| 3 | index = 2147483647 (max) | PASS | STRING=str 'test'; INT=int 7 |
| 4 | index = -1 (mid) | PASS | STRING=str 'test'; INT=int 7 |
| 5 | text_1 = '' (empty) | PASS | STRING=str ''; INT=int 0 |
| 6 | text_2 = '' (empty) | PASS | STRING=str 'test'; INT=int 0 |
| 7 | text_3 = '' (empty) | PASS | STRING=str 'test'; INT=int 0 |
| 8 | text_4 = '' (empty) | PASS | STRING=str 'test'; INT=int 0 |
| 9 | text_5 = '' (empty) | PASS | STRING=str 'test'; INT=int 0 |
| 10 | text_6 = '' (empty) | PASS | STRING=str 'test'; INT=int 0 |
| 11 | text_7 = '' (empty) | PASS | STRING=str 'test'; INT=int 0 |
| 12 | text_8 = '' (empty) | PASS | STRING=str 'test'; INT=int 0 |

## Verdict

All 12 cases behaved as expected (12 passed, 0 rejected with a clear message).

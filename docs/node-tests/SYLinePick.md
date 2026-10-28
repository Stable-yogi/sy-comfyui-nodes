# LinePick SY (`SYLinePick`)

Source: `nodes/sy_line_pick.py`

**What it does:** Takes one line from a text. Count from the top with 0, 1, 2 or from the bottom with -1, -2.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| text | STRING | yes | The text with several lines. | default '', multiline |
| index | INT | yes | Line to take, counting from 0. Negative counts from the end. | -100000 to 100000, default 0 |
| skip_blank | BOOLEAN | yes | Ignore empty lines when counting. | default True |

Outputs: `STRING`, `INT`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | PASS | STRING=str 'test'; INT=int 1 |
| 2 | text = '' (empty) | REJECTED | ValueError: text has no lines to pick from |
| 3 | index = -100000 (min) | REJECTED | ValueError: index -100000 is out of range: the text has 1 lines (use -1 to 0) |
| 4 | index = 100000 (max) | REJECTED | ValueError: index 100000 is out of range: the text has 1 lines (use -1 to 0) |
| 5 | skip_blank = False | PASS | STRING=str 'test'; INT=int 1 |

Note: Empty text boxes were filled with sample text in the starting inputs, because the node refuses empty text.


## Verdict

All 5 cases behaved as expected (2 passed, 3 rejected with a clear message).

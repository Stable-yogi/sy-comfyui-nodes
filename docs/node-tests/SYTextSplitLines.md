# Text Split Lines SY (`SYTextSplitLines`)

Source: `nodes/sy_text_split_lines.py`

**What it does:** Splits text into lines. Gives the full list, one line picked by number (wraps around), and the line count.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| text | STRING | yes | The text to split. One line becomes one item. | default '', multiline |
| index | INT | yes | Which line to pick, counting from 0. Too big a number wraps to the start. | -2147483648 to 2147483647, default 0 |
| skip_empty | BOOLEAN | yes | Leave out empty lines and lines with only spaces. | default True |

Outputs: `STRING`, `STRING`, `INT`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | REJECTED | ValueError: there are no lines to pick from: add some text or turn off skip_empty |
| 2 | text = '' (empty) | REJECTED | ValueError: there are no lines to pick from: add some text or turn off skip_empty |
| 3 | index = -2147483648 (min) | REJECTED | ValueError: there are no lines to pick from: add some text or turn off skip_empty |
| 4 | index = 2147483647 (max) | REJECTED | ValueError: there are no lines to pick from: add some text or turn off skip_empty |
| 5 | index = -1 (mid) | REJECTED | ValueError: there are no lines to pick from: add some text or turn off skip_empty |
| 6 | skip_empty = False | REJECTED | ValueError: there are no lines to pick from: add some text or turn off skip_empty |

## Verdict

All 6 cases behaved as expected (0 passed, 6 rejected with a clear message).

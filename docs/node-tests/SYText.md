# Text SY (`SYText`)

Source: `nodes/sy_text.py`

**What it does:** A multiline text box. The text goes out as it is. Turn on strip_lines to remove spaces at the end of each line.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| text | STRING | yes | The text to pass on, such as your prompt. | default '', multiline |
| strip_lines | BOOLEAN | yes | On: trim spaces at the start and end of every line. | default False |

Outputs: `STRING`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | PASS | STRING=str '' |
| 2 | text = '' (empty) | PASS | STRING=str '' |
| 3 | strip_lines = True | PASS | STRING=str '' |

## Verdict

All 3 cases behaved as expected (3 passed, 0 rejected with a clear message).

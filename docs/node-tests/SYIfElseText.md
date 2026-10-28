# If Else Text SY (`SYIfElseText`)

Source: `nodes/sy_if_else_text.py`

**What it does:** Picks one of two texts. Yes sends if_true. No sends if_false.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| condition | BOOLEAN | yes | Yes sends if_true. No sends if_false. | default True |
| if_true | STRING | yes | The text sent when the condition is yes. | default '', multiline |
| if_false | STRING | yes | The text sent when the condition is no. | default '', multiline |

Outputs: `STRING`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | PASS | STRING=str '' |
| 2 | condition = False | PASS | STRING=str '' |
| 3 | if_true = '' (empty) | PASS | STRING=str '' |
| 4 | if_false = '' (empty) | PASS | STRING=str '' |

## Verdict

All 4 cases behaved as expected (4 passed, 0 rejected with a clear message).

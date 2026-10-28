# TextRepeat SY (`SYTextRepeat`)

Source: `nodes/sy_text_repeat.py`

**What it does:** Repeats a text a number of times. It can put a separator between copies and number each copy.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| text | STRING | yes | The text to repeat. | default '', multiline |
| count | INT | yes | How many copies to make. | 1 to 200, default 2 |
| separator | STRING | yes | Put between copies. Use a comma, a space or a new line. | default '\n' |
| numbered | BOOLEAN | yes | Start each copy with its number, like 1. text. | default False |

Outputs: `STRING`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | PASS | STRING=str '' |
| 2 | text = '' (empty) | PASS | STRING=str '' |
| 3 | count = 1 (min) | PASS | STRING=str '' |
| 4 | count = 200 (max) | PASS | STRING=str '' |
| 5 | count = 100 (mid) | PASS | STRING=str '' |
| 6 | separator = '' (empty) | PASS | STRING=str '' |
| 7 | numbered = True | PASS | STRING=str '1. 2.' |

## Verdict

All 7 cases behaved as expected (7 passed, 0 rejected with a clear message).

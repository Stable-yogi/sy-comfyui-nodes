# Note SY (`SYNote`)

Source: `nodes/sy_note.py`

**What it does:** A note card for your workflow. Pick a style and the card gets a colour. The text can also go out as a prompt.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| text | STRING | yes | Write your note here. Plain text. | default '', multiline |
| style | COMBO | yes | Info is blue, tip is green, warning is red, step is gold, model is purple. | one of: info, tip, warning, step, model |

Outputs: `STRING`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | PASS | STRING=str '' |
| 2 | text = '' (empty) | PASS | STRING=str '' |
| 3 | style = 'tip' | PASS | STRING=str '' |
| 4 | style = 'warning' | PASS | STRING=str '' |
| 5 | style = 'step' | PASS | STRING=str '' |
| 6 | style = 'model' | PASS | STRING=str '' |

## Verdict

All 6 cases behaved as expected (6 passed, 0 rejected with a clear message).

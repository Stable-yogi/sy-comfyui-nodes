# Multiline Text SY (`SYMultilineText`)

Source: `nodes/sy_multiline_text.py`

**What it does:** A big text box. Lines starting with # are notes to yourself and are left out. Start a line with \# to keep a #.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| text | STRING | yes | Your text. Lines that start with # are ignored. | default '', multiline |
| keep_empty_lines | BOOLEAN | yes | Off: also remove empty lines from the result. | default True |

Outputs: `STRING`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | PASS | STRING=str '' |
| 2 | text = '' (empty) | PASS | STRING=str '' |
| 3 | keep_empty_lines = False | PASS | STRING=str '' |

## Verdict

All 3 cases behaved as expected (3 passed, 0 rejected with a clear message).

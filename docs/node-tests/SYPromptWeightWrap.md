# Prompt Weight Wrap SY (`SYPromptWeightWrap`)

Source: `nodes/sy_prompt_weight_wrap.py`

**What it does:** Wraps a prompt as (text:1.2) with a weight, or in round, square or curly brackets. Empty text stays empty.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| text | STRING | yes | The prompt part to wrap. | default '', multiline |
| style | COMBO | yes | How to wrap: with a weight number or with a bracket type. | one of: weight (text:1.2), round ( ), double round (( )), square [ ], curly { } |
| weight | FLOAT | yes | Strength for the weight style. 1 means no change. | 0.0 to 10.0, step 0.05, default 1.2 |

Outputs: `STRING`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | PASS | STRING=str '' |
| 2 | text = '' (empty) | PASS | STRING=str '' |
| 3 | style = 'round ( )' | PASS | STRING=str '' |
| 4 | style = 'double round (( ))' | PASS | STRING=str '' |
| 5 | style = 'square [ ]' | PASS | STRING=str '' |
| 6 | style = 'curly { }' | PASS | STRING=str '' |
| 7 | weight = 0.0 (min) | PASS | STRING=str '' |
| 8 | weight = 10.0 (max) | PASS | STRING=str '' |
| 9 | weight = 5.0 (mid) | PASS | STRING=str '' |

## Verdict

All 9 cases behaved as expected (9 passed, 0 rejected with a clear message).

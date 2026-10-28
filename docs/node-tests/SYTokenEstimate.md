# Token Estimate SY (`SYTokenEstimate`)

Source: `nodes/sy_token_estimate.py`

**What it does:** Gives a rough word, character and token count. The token number is only an estimate, not what a real tokenizer would say.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| text | STRING | yes | The text to measure. | default '', multiline |

Outputs: `INT`, `INT`, `INT`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | PASS | INT=int 0; INT=int 0; INT=int 0 |
| 2 | text = '' (empty) | PASS | INT=int 0; INT=int 0; INT=int 0 |

## Verdict

All 2 cases behaved as expected (2 passed, 0 rejected with a clear message).

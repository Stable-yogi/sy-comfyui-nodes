# Prompt Choice SY (`SYPromptChoice`)

Source: `nodes/sy_prompt_wildcards.py`

**What it does:** Picks one option from each {red|green|blue} group in the text. The same seed gives the same result in the browser and in an API run. Use a backslash before a brace to keep it literal.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| text | STRING | yes | Your prompt. Write {red\|blue} to pick one option at random. | default '', multiline |
| seed | INT | yes | Same number gives the same picks every time. Change it to get other picks. | 0 to 18446744073709551615, default 0 |

Outputs: `STRING`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | PASS | STRING=str '' |
| 2 | text = '' (empty) | PASS | STRING=str '' |
| 3 | seed = 18446744073709551615 (max) | PASS | STRING=str '' |
| 4 | seed = 9223372036854775807 (mid) | PASS | STRING=str '' |

## Verdict

All 4 cases behaved as expected (4 passed, 0 rejected with a clear message).

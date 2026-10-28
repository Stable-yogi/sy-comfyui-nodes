# Bool Logic SY (`SYBoolLogic`)

Source: `nodes/sy_bool_logic.py`

**What it does:** Combines two yes/no values with and, or, xor. The not choice flips a and ignores b.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| a | BOOLEAN | yes | The first yes/no value. | default False |
| b | BOOLEAN | yes | The second yes/no value. Not used by not. | default False |
| operation | COMBO | yes | and: both yes. or: at least one yes. xor: exactly one yes. not: flip a. | one of: and, or, xor, not |

Outputs: `BOOLEAN`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | PASS | BOOLEAN=bool False |
| 2 | a = True | PASS | BOOLEAN=bool False |
| 3 | b = True | PASS | BOOLEAN=bool False |
| 4 | operation = 'or' | PASS | BOOLEAN=bool False |
| 5 | operation = 'xor' | PASS | BOOLEAN=bool False |
| 6 | operation = 'not' | PASS | BOOLEAN=bool True |

## Verdict

All 6 cases behaved as expected (6 passed, 0 rejected with a clear message).

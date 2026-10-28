# Text Number Format SY (`SYTextNumberFormat`)

Source: `nodes/sy_text_number_format.py`

**What it does:** Turns a number into text. Set decimals, zero padding (7 becomes 007), thousands commas, and a prefix and suffix.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| number | FLOAT | yes | The number to turn into text. | -1000000000000.0 to 1000000000000.0, step 0.01, default 0.0 |
| decimals | INT | yes | How many digits after the decimal point. | 0 to 10, default 0 |
| pad_width | INT | yes | Fill the whole-number part with leading zeros up to this width. | 0 to 32, default 0 |
| thousands | BOOLEAN | yes | Put commas between groups of three digits. | default False |
| prefix | STRING | yes | Text added before the number. | default '' |
| suffix | STRING | yes | Text added after the number. | default '' |
| number_in | * | no | Connect an INT or FLOAT here to use it instead of the number box. |  |

Outputs: `STRING`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | PASS | STRING=str '12345' |
| 2 | number = -1000000000000.0 (min) | PASS | STRING=str '12345' |
| 3 | number = 1000000000000.0 (max) | PASS | STRING=str '12345' |
| 4 | decimals = 10 (max) | PASS | STRING=str '12345.0000000000' |
| 5 | decimals = 5 (mid) | PASS | STRING=str '12345.00000' |
| 6 | pad_width = 32 (max) | PASS | STRING=str '00000000000000000000000000012345' |
| 7 | pad_width = 16 (mid) | PASS | STRING=str '0000000000012345' |
| 8 | thousands = True | PASS | STRING=str '12,345' |
| 9 | prefix = '' (empty) | PASS | STRING=str '12345' |
| 10 | suffix = '' (empty) | PASS | STRING=str '12345' |

Note: The any-type input was given the number 12345 because text was refused.


## Verdict

All 10 cases behaved as expected (10 passed, 0 rejected with a clear message).

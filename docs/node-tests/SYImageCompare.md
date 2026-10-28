# Image Compare SY (`SYImageCompare`)

Source: `nodes/sy_image_compare.py`

**What it does:** Compares two pictures: side by side, difference, blend, checker or wipe. B is resized to match A.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image_a | IMAGE | yes | The first picture. Its size sets the result size. | picture batch [B,H,W,3] |
| image_b | IMAGE | yes | The second picture. It is resized to fit the first if needed. | picture batch [B,H,W,3] |
| mode | COMBO | yes | How to put the two pictures together. | one of: side_by_side, difference, blend, checker, wipe |
| amount | FLOAT | yes | Blend mix, or wipe position. 0 shows A, 1 shows B. | 0.0 to 1.0, step 0.01, default 0.5 |

Outputs: `IMAGE`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | PASS | IMAGE=tensor[1, 64, 192, 3] |
| 2 | mode = 'difference' | PASS | IMAGE=tensor[1, 64, 96, 3] |
| 3 | mode = 'blend' | PASS | IMAGE=tensor[1, 64, 96, 3] |
| 4 | mode = 'checker' | PASS | IMAGE=tensor[1, 64, 96, 3] |
| 5 | mode = 'wipe' | PASS | IMAGE=tensor[1, 64, 96, 3] |
| 6 | amount = 0.0 (min) | PASS | IMAGE=tensor[1, 64, 192, 3] |
| 7 | amount = 1.0 (max) | PASS | IMAGE=tensor[1, 64, 192, 3] |

## Verdict

All 7 cases behaved as expected (7 passed, 0 rejected with a clear message).

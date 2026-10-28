# Compare Metrics SY (`SYCompareMetrics`)

Source: `nodes/sy_compare_metrics.py`

**What it does:** Compares two images of the same size. diff_score is the mean absolute difference (0 = identical, 1 = opposite). diff_image shows the difference, brightened by gain.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image_a | IMAGE | yes | The first picture to compare, for example the original. | picture batch [B,H,W,3] |
| image_b | IMAGE | yes | The second picture to compare. It must be the same size as the first. | picture batch [B,H,W,3] |
| gain | FLOAT | yes | Makes small differences easier to see in the output. 1 = true size, 4 = four times brighter. | 0.0 to 1000.0, step 0.1, default 4.0 |

Outputs: `FLOAT`, `IMAGE`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | PASS | FLOAT=float 0; IMAGE=tensor[1, 64, 96, 3] |
| 2 | gain = 0.0 (min) | PASS | FLOAT=float 0; IMAGE=tensor[1, 64, 96, 3] |
| 3 | gain = 1000.0 (max) | PASS | FLOAT=float 0; IMAGE=tensor[1, 64, 96, 3] |
| 4 | gain = 500.0 (mid) | PASS | FLOAT=float 0; IMAGE=tensor[1, 64, 96, 3] |

## Verdict

All 4 cases behaved as expected (4 passed, 0 rejected with a clear message).

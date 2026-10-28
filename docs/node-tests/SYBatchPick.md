# Batch Pick SY (`SYBatchPick`)

Source: `nodes/sy_batch_pick.py`

**What it does:** Picks a slice of pictures from a batch. Starts at the index and wraps around to the first one.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| images | IMAGE | yes | The batch of pictures to pick from. | picture batch [B,H,W,3] |
| index | INT | yes | First picture to take, counting from 0. Too big a number wraps around. | 0 to 2147483647, default 0 |
| count | INT | yes | How many pictures to take. It wraps to the start when the batch ends. | 1 to 64, default 1 |

Outputs: `IMAGE`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | PASS | IMAGE=tensor[1, 64, 96, 3] |
| 2 | index = 2147483647 (max) | PASS | IMAGE=tensor[1, 64, 96, 3] |
| 3 | index = 1073741823 (mid) | PASS | IMAGE=tensor[1, 64, 96, 3] |
| 4 | count = 64 (max) | PASS | IMAGE=tensor[64, 64, 96, 3] |
| 5 | count = 32 (mid) | PASS | IMAGE=tensor[32, 64, 96, 3] |

## Verdict

All 5 cases behaved as expected (5 passed, 0 rejected with a clear message).

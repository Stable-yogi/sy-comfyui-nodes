# Batch Repeat SY (`SYBatchRepeat`)

Source: `nodes/sy_batch_repeat.py`

**What it does:** Repeats each picture N times in a row, or repeats the whole batch N times.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| images | IMAGE | yes | The batch of pictures to repeat. | picture batch [B,H,W,3] |
| times | INT | yes | How many copies of each picture, or of the whole batch. | 1 to 256, default 2 |
| mode | COMBO | yes | each_picture gives 1,1,2,2. whole_batch gives 1,2,1,2. | one of: each_picture, whole_batch |

Outputs: `IMAGE`, `INT`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | PASS | IMAGE=tensor[2, 64, 96, 3]; INT=int 2 |
| 2 | times = 1 (min) | PASS | IMAGE=tensor[1, 64, 96, 3]; INT=int 1 |
| 3 | times = 256 (max) | PASS | IMAGE=tensor[256, 64, 96, 3]; INT=int 256 |
| 4 | times = 128 (mid) | PASS | IMAGE=tensor[128, 64, 96, 3]; INT=int 128 |
| 5 | mode = 'whole_batch' | PASS | IMAGE=tensor[2, 64, 96, 3]; INT=int 2 |

## Verdict

All 5 cases behaved as expected (5 passed, 0 rejected with a clear message).

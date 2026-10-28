# Batch Concat SY (`SYBatchConcat`)

Source: `nodes/sy_batch_concat.py`

**What it does:** Joins two to four picture batches into one batch, in order. Other sizes can be resized to match the first.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image_1 | IMAGE | yes | First batch. Its size and channels set the size of the result. | picture batch [B,H,W,3] |
| image_2 | IMAGE | yes | Second batch, added after the first. | picture batch [B,H,W,3] |
| resize_to_first | BOOLEAN | yes | On: resize other batches to the first one's size. Off: stop with an error when sizes differ. | default True |
| image_3 | IMAGE | no | Optional third batch. | picture batch [B,H,W,3] |
| image_4 | IMAGE | no | Optional fourth batch. | picture batch [B,H,W,3] |

Outputs: `IMAGE`, `INT`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | PASS | IMAGE=tensor[4, 64, 96, 3]; INT=int 4 |
| 2 | resize_to_first = False | PASS | IMAGE=tensor[4, 64, 96, 3]; INT=int 4 |

## Verdict

All 2 cases behaved as expected (2 passed, 0 rejected with a clear message).

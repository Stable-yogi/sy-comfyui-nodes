# Reverse Batch SY (`SYReverseBatch`)

Source: `nodes/sy_reverse_batch.py`

**What it does:** Turns a batch of pictures around so the last one comes first. Handy for playing a video backwards.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| images | IMAGE | yes | The batch of pictures or video frames to reverse. | picture batch [B,H,W,3] |

Outputs: `IMAGE`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | PASS | IMAGE=tensor[1, 64, 96, 3] |

## Verdict

All 1 cases behaved as expected (1 passed, 0 rejected with a clear message).

# Batch Info SY (`SYBatchInfo`)

Source: `nodes/sy_batch_info.py`

**What it does:** Reports the number of pictures in a batch and their width, height and channels. The pictures pass through unchanged.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| images | IMAGE | yes | The batch to measure. It is passed on unchanged. | picture batch [B,H,W,3] |

Outputs: `IMAGE`, `INT`, `INT`, `INT`, `INT`, `STRING`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | PASS | IMAGE=tensor[1, 64, 96, 3]; INT=int 1; INT=int 96; INT=int 64; INT=int 3; STRING=str '1 picture, 96x64, 3 channels' |

## Verdict

All 1 cases behaved as expected (1 passed, 0 rejected with a clear message).

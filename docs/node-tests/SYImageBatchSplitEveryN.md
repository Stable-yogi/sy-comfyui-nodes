# Image Batch Split Every N SY (`SYImageBatchSplitEveryN`)

Source: `nodes/sy_image_batch_split_every_n.py`

**What it does:** Cuts a batch into slices of N pictures and gives you slice number K. The last slice may be shorter.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| images | IMAGE | yes | The batch of pictures to cut. | picture batch [B,H,W,3] |
| part_size | INT | yes | How many pictures go in each slice. | 1 to 100000, default 16 |
| part | INT | yes | Which slice to output, counting from 0. | 0 to 100000, default 0 |

Outputs: `IMAGE`, `INT`, `INT`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | PASS | IMAGE=tensor[1, 64, 96, 3]; INT=int 1; INT=int 1 |
| 2 | part_size = 1 (min) | PASS | IMAGE=tensor[1, 64, 96, 3]; INT=int 1; INT=int 1 |
| 3 | part_size = 100000 (max) | PASS | IMAGE=tensor[1, 64, 96, 3]; INT=int 1; INT=int 1 |
| 4 | part_size = 50000 (mid) | PASS | IMAGE=tensor[1, 64, 96, 3]; INT=int 1; INT=int 1 |
| 5 | part = 100000 (max) | REJECTED | ValueError: part 100000 does not exist: 1 frames in slices of 16 make 1 parts (0 to 0) |
| 6 | part = 50000 (mid) | REJECTED | ValueError: part 50000 does not exist: 1 frames in slices of 16 make 1 parts (0 to 0) |

## Verdict

All 6 cases behaved as expected (4 passed, 2 rejected with a clear message).

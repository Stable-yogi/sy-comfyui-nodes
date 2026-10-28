# Frame Select SY (`SYFrameSelect`)

Source: `nodes/sy_frame_select.py`

**What it does:** Takes some frames from a batch: from start to end (both included), every step frames. Negative numbers count from the end.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| images | IMAGE | yes | The batch of frames to take from. | picture batch [B,H,W,3] |
| start | INT | yes | First frame to keep, counting from 0. -1 means the last frame. | -100000 to 100000, default 0 |
| end | INT | yes | Last frame to keep, included. -1 means the last frame. | -100000 to 100000, default -1 |
| step | INT | yes | Keep every this many frames. 2 keeps every second frame. | 1 to 1000, default 1 |

Outputs: `IMAGE`, `INT`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | PASS | IMAGE=tensor[1, 64, 96, 3]; INT=int 1 |
| 2 | start = -100000 (min) | REJECTED | ValueError: start -100000 is outside the batch of 1 frames (allowed: -1 to 0) |
| 3 | start = 100000 (max) | REJECTED | ValueError: start 100000 is outside the batch of 1 frames (allowed: -1 to 0) |
| 4 | end = -100000 (min) | REJECTED | ValueError: end -100000 is outside the batch of 1 frames (allowed: -1 to 0) |
| 5 | end = 100000 (max) | REJECTED | ValueError: end 100000 is outside the batch of 1 frames (allowed: -1 to 0) |
| 6 | end = 0 (mid) | PASS | IMAGE=tensor[1, 64, 96, 3]; INT=int 1 |
| 7 | step = 1000 (max) | PASS | IMAGE=tensor[1, 64, 96, 3]; INT=int 1 |
| 8 | step = 500 (mid) | PASS | IMAGE=tensor[1, 64, 96, 3]; INT=int 1 |

## Verdict

All 8 cases behaved as expected (4 passed, 4 rejected with a clear message).

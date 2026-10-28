# Video Loop Frames SY (`SYVideoLoopFrames`)

Source: `nodes/sy_video_loop_frames.py`

**What it does:** Fills a target frame count by repeating the frames from the start, or by playing them forward and back.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| images | IMAGE | yes | The frames to loop. | picture batch [B,H,W,3] |
| target_frames | INT | yes | How many frames the result should have. | 1 to 100000, default 81 |
| mode | COMBO | yes | repeat starts over at the end. ping_pong plays back and forth. | one of: repeat, ping_pong |

Outputs: `IMAGE`, `INT`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | PASS | IMAGE=tensor[81, 64, 96, 3]; INT=int 81 |
| 2 | target_frames = 1 (min) | PASS | IMAGE=tensor[1, 64, 96, 3]; INT=int 1 |
| 3 | target_frames = 100000 (max) | PASS | IMAGE=tensor[100000, 64, 96, 3]; INT=int 100000 |
| 4 | target_frames = 50000 (mid) | PASS | IMAGE=tensor[50000, 64, 96, 3]; INT=int 50000 |
| 5 | mode = 'ping_pong' | PASS | IMAGE=tensor[81, 64, 96, 3]; INT=int 81 |

## Verdict

All 5 cases behaved as expected (5 passed, 0 rejected with a clear message).

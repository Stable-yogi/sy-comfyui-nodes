# Frame Rate Convert SY (`SYFrameRateConvert`)

Source: `nodes/sy_frame_rate_convert.py`

**What it does:** Changes the frame rate of a clip, keeping its length. It drops or repeats the nearest frames, no blending.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| images | IMAGE | yes | The frames of the clip. | picture batch [B,H,W,3] |
| source_fps | FLOAT | yes | The frame rate the clip has now. | 0.1 to 1000.0, step 1.0, default 24.0 |
| target_fps | FLOAT | yes | The frame rate you want. | 0.1 to 1000.0, step 1.0, default 16.0 |

Outputs: `IMAGE`, `INT`, `FLOAT`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | PASS | IMAGE=tensor[1, 64, 96, 3]; INT=int 1; FLOAT=float 16 |
| 2 | source_fps = 0.1 (min) | PASS | IMAGE=tensor[160, 64, 96, 3]; INT=int 160; FLOAT=float 16 |
| 3 | source_fps = 1000.0 (max) | PASS | IMAGE=tensor[1, 64, 96, 3]; INT=int 1; FLOAT=float 16 |
| 4 | source_fps = 500.05 (mid) | PASS | IMAGE=tensor[1, 64, 96, 3]; INT=int 1; FLOAT=float 16 |
| 5 | target_fps = 0.1 (min) | PASS | IMAGE=tensor[1, 64, 96, 3]; INT=int 1; FLOAT=float 0.1 |
| 6 | target_fps = 1000.0 (max) | PASS | IMAGE=tensor[42, 64, 96, 3]; INT=int 42; FLOAT=float 1000 |
| 7 | target_fps = 500.05 (mid) | PASS | IMAGE=tensor[21, 64, 96, 3]; INT=int 21; FLOAT=float 500.05 |

## Verdict

All 7 cases behaved as expected (7 passed, 0 rejected with a clear message).

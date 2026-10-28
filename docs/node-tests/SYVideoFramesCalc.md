# Video Frames Calc SY (`SYVideoFramesCalc`)

Source: `nodes/sy_video_frames_calc.py`

**What it does:** Turns seconds and frames per second into a frame count. Switch on 4n+1 to land on 1, 5, 9, 13 ... frames, which many video models need.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| seconds | FLOAT | yes | How long the clip should be, in seconds. | 0.01 to 100000.0, step 0.1, default 5.0 |
| fps | FLOAT | yes | Frames per second of the clip. | 0.1 to 1000.0, step 1.0, default 16.0 |
| four_n_plus_one | BOOLEAN | yes | On makes the frame count 4n+1 (like 81). Off keeps the plain count. | default True |

Outputs: `INT`, `FLOAT`, `FLOAT`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | PASS | INT=int 81; FLOAT=float 16; FLOAT=float 5.0625 |
| 2 | seconds = 0.01 (min) | PASS | INT=int 1; FLOAT=float 16; FLOAT=float 0.0625 |
| 3 | seconds = 100000.0 (max) | REJECTED | ValueError: that is 1600001 frames, more than the limit of 1000000. Lower seconds or fps |
| 4 | seconds = 50000.005 (mid) | PASS | INT=int 800001; FLOAT=float 16; FLOAT=float 50000.1 |
| 5 | fps = 0.1 (min) | PASS | INT=int 1; FLOAT=float 0.1; FLOAT=float 10 |
| 6 | fps = 1000.0 (max) | PASS | INT=int 5001; FLOAT=float 1000; FLOAT=float 5.001 |
| 7 | fps = 500.05 (mid) | PASS | INT=int 2501; FLOAT=float 500.05; FLOAT=float 5.0015 |
| 8 | four_n_plus_one = False | PASS | INT=int 80; FLOAT=float 16; FLOAT=float 5 |

## Verdict

All 8 cases behaved as expected (7 passed, 1 rejected with a clear message).

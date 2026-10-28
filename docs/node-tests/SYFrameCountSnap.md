# Frame Count Snap SY (`SYFrameCountSnap`)

Source: `nodes/sy_frame_count_snap.py`

**What it does:** Rounds a wanted frame count to a multiple of a step, then can add one frame. Example: 80 with step 4 gives 81.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| wanted_frames | INT | yes | The number of frames you would like. | 1 to 100000, default 80 |
| step | INT | yes | The result is a multiple of this number. | 1 to 1024, default 4 |
| mode | COMBO | yes | nearest picks the closest multiple, down rounds lower, up rounds higher. | one of: nearest, down, up |
| plus_one | BOOLEAN | yes | Add one extra frame after snapping (for example 80 becomes 81). | default True |

Outputs: `INT`, `STRING`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | PASS | INT=int 81; STRING=str 'wanted 80, step 4, nearest -> 80 +1 = 81 frames' |
| 2 | wanted_frames = 1 (min) | PASS | INT=int 5; STRING=str 'wanted 1, step 4, nearest -> 4 +1 = 5 frames' |
| 3 | wanted_frames = 100000 (max) | PASS | INT=int 100001; STRING=str 'wanted 100000, step 4, nearest -> 100000 +1 = 100001 frames' |
| 4 | wanted_frames = 50000 (mid) | PASS | INT=int 50001; STRING=str 'wanted 50000, step 4, nearest -> 50000 +1 = 50001 frames' |
| 5 | step = 1 (min) | PASS | INT=int 81; STRING=str 'wanted 80, step 1, nearest -> 80 +1 = 81 frames' |
| 6 | step = 1024 (max) | PASS | INT=int 1025; STRING=str 'wanted 80, step 1024, nearest -> 1024 +1 = 1025 frames' |
| 7 | step = 512 (mid) | PASS | INT=int 513; STRING=str 'wanted 80, step 512, nearest -> 512 +1 = 513 frames' |
| 8 | mode = 'down' | PASS | INT=int 81; STRING=str 'wanted 80, step 4, down -> 80 +1 = 81 frames' |
| 9 | mode = 'up' | PASS | INT=int 81; STRING=str 'wanted 80, step 4, up -> 80 +1 = 81 frames' |
| 10 | plus_one = False | PASS | INT=int 80; STRING=str 'wanted 80, step 4, nearest -> 80 = 80 frames' |

## Verdict

All 10 cases behaved as expected (10 passed, 0 rejected with a clear message).

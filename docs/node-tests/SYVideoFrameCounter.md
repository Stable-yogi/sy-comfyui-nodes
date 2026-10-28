# Video Frame Counter SY (`SYVideoFrameCounter`)

Source: `nodes/sy_video_frame_counter.py`

**What it does:** Works out the missing one of frames, seconds and frames per second. Gives the numbers and a text line.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| mode | COMBO | yes | Which value to work out. The other two are used. | one of: frames_to_seconds, seconds_to_frames, fps_from_frames_and_seconds |
| frames | INT | yes | Number of frames. Used unless the mode works out the frames. | 1 to 1000000, default 81 |
| seconds | FLOAT | yes | Length in seconds. Used unless the mode works out the seconds. | 0.01 to 100000.0, step 0.1, default 5.0 |
| fps | FLOAT | yes | Frames per second. Used unless the mode works out the fps. | 0.1 to 1000.0, step 1.0, default 16.0 |

Outputs: `INT`, `FLOAT`, `FLOAT`, `STRING`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | PASS | INT=int 81; FLOAT=float 5.0625; FLOAT=float 16; STRING=str '81 frames, 5.062 seconds, 16.000 fps' |
| 2 | mode = 'seconds_to_frames' | PASS | INT=int 80; FLOAT=float 5; FLOAT=float 16; STRING=str '80 frames, 5.000 seconds, 16.000 fps' |
| 3 | mode = 'fps_from_frames_and_seconds' | PASS | INT=int 81; FLOAT=float 5; FLOAT=float 16.2; STRING=str '81 frames, 5.000 seconds, 16.200 fps' |
| 4 | frames = 1 (min) | PASS | INT=int 1; FLOAT=float 0.0625; FLOAT=float 16; STRING=str '1 frames, 0.062 seconds, 16.000 fps' |
| 5 | frames = 1000000 (max) | PASS | INT=int 1000000; FLOAT=float 62500; FLOAT=float 16; STRING=str '1000000 frames, 62500.000 seconds, 16.000 fps' |
| 6 | frames = 500000 (mid) | PASS | INT=int 500000; FLOAT=float 31250; FLOAT=float 16; STRING=str '500000 frames, 31250.000 seconds, 16.000 fps' |
| 7 | seconds = 0.01 (min) | PASS | INT=int 81; FLOAT=float 5.0625; FLOAT=float 16; STRING=str '81 frames, 5.062 seconds, 16.000 fps' |
| 8 | seconds = 100000.0 (max) | PASS | INT=int 81; FLOAT=float 5.0625; FLOAT=float 16; STRING=str '81 frames, 5.062 seconds, 16.000 fps' |
| 9 | seconds = 50000.005 (mid) | PASS | INT=int 81; FLOAT=float 5.0625; FLOAT=float 16; STRING=str '81 frames, 5.062 seconds, 16.000 fps' |
| 10 | fps = 0.1 (min) | PASS | INT=int 81; FLOAT=float 810; FLOAT=float 0.1; STRING=str '81 frames, 810.000 seconds, 0.100 fps' |
| 11 | fps = 1000.0 (max) | PASS | INT=int 81; FLOAT=float 0.081; FLOAT=float 1000; STRING=str '81 frames, 0.081 seconds, 1000.000 fps' |
| 12 | fps = 500.05 (mid) | PASS | INT=int 81; FLOAT=float 0.161984; FLOAT=float 500.05; STRING=str '81 frames, 0.162 seconds, 500.050 fps' |

## Verdict

All 12 cases behaved as expected (12 passed, 0 rejected with a clear message).

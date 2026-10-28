# Duration Frames SY (`SYDurationFrames`)

Source: `nodes/sy_duration_frames.py`

**What it does:** Turns seconds into a frame count, or a frame count into seconds, using the frame rate you give.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| mode | COMBO | yes | Which way to convert. | one of: seconds_to_frames, frames_to_seconds |
| seconds | FLOAT | yes | Length in seconds. Used when mode is seconds_to_frames. | 0.0 to 100000.0, step 0.01, default 5.0 |
| frames | INT | yes | Frame count. Used when mode is frames_to_seconds. | 0 to 10000000, default 120 |
| fps | FLOAT | yes | Frames per second. | 0.01 to 1000.0, step 0.01, default 24.0 |

Outputs: `INT`, `FLOAT`, `STRING`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | PASS | INT=int 120; FLOAT=float 5; STRING=str '120 frames = 5.000 seconds at 24.0 fps' |
| 2 | mode = 'frames_to_seconds' | PASS | INT=int 120; FLOAT=float 5; STRING=str '120 frames = 5.000 seconds at 24.0 fps' |
| 3 | seconds = 0.0 (min) | PASS | INT=int 0; FLOAT=float 0; STRING=str '0 frames = 0.000 seconds at 24.0 fps' |
| 4 | seconds = 100000.0 (max) | PASS | INT=int 2400000; FLOAT=float 100000; STRING=str '2400000 frames = 100000.000 seconds at 24.0 fps' |
| 5 | seconds = 50000.0 (mid) | PASS | INT=int 1200000; FLOAT=float 50000; STRING=str '1200000 frames = 50000.000 seconds at 24.0 fps' |
| 6 | frames = 0 (min) | PASS | INT=int 120; FLOAT=float 5; STRING=str '120 frames = 5.000 seconds at 24.0 fps' |
| 7 | frames = 10000000 (max) | PASS | INT=int 120; FLOAT=float 5; STRING=str '120 frames = 5.000 seconds at 24.0 fps' |
| 8 | frames = 5000000 (mid) | PASS | INT=int 120; FLOAT=float 5; STRING=str '120 frames = 5.000 seconds at 24.0 fps' |
| 9 | fps = 0.01 (min) | PASS | INT=int 0; FLOAT=float 5; STRING=str '0 frames = 5.000 seconds at 0.01 fps' |
| 10 | fps = 1000.0 (max) | PASS | INT=int 5000; FLOAT=float 5; STRING=str '5000 frames = 5.000 seconds at 1000.0 fps' |
| 11 | fps = 500.005 (mid) | PASS | INT=int 2500; FLOAT=float 5; STRING=str '2500 frames = 5.000 seconds at 500.005 fps' |

## Verdict

All 11 cases behaved as expected (11 passed, 0 rejected with a clear message).

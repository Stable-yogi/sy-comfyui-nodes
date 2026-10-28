# Time Code SY (`SYTimeCode`)

Source: `nodes/sy_time_code.py`

**What it does:** Turns a frame number into a time code like 00:00:03:12, or reads a time code back into a frame number.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| mode | COMBO | yes | Which way to convert. | one of: frame_to_timecode, timecode_to_frame |
| frame | INT | yes | Frame number. Used when mode is frame_to_timecode. | 0 to 100000000, default 0 |
| fps | FLOAT | yes | Frames per second. | 1.0 to 1000.0, step 0.01, default 24.0 |
| timecode | STRING | yes | Time code as HH:MM:SS:FF. Used when mode is timecode_to_frame. | default '00:00:00:00' |

Outputs: `STRING`, `FLOAT`, `INT`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | PASS | STRING=str '00:00:00:00'; FLOAT=float 0; INT=int 0 |
| 2 | mode = 'timecode_to_frame' | PASS | STRING=str '00:00:00:00'; FLOAT=float 0; INT=int 0 |
| 3 | frame = 100000000 (max) | PASS | STRING=str '1157:24:26:16'; FLOAT=float 4.16667e+06; INT=int 100000000 |
| 4 | frame = 50000000 (mid) | PASS | STRING=str '578:42:13:08'; FLOAT=float 2.08333e+06; INT=int 50000000 |
| 5 | fps = 1.0 (min) | PASS | STRING=str '00:00:00:00'; FLOAT=float 0; INT=int 0 |
| 6 | fps = 1000.0 (max) | PASS | STRING=str '00:00:00:00'; FLOAT=float 0; INT=int 0 |
| 7 | fps = 500.5 (mid) | PASS | STRING=str '00:00:00:00'; FLOAT=float 0; INT=int 0 |
| 8 | timecode = '' (empty) | PASS | STRING=str '00:00:00:00'; FLOAT=float 0; INT=int 0 |

## Verdict

All 8 cases behaved as expected (8 passed, 0 rejected with a clear message).

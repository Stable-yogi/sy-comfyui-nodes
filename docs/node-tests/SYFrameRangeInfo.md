# Frame Range Info SY (`SYFrameRangeInfo`)

Source: `nodes/sy_frame_range_info.py`

**What it does:** Shows which frame numbers a start, end and step pick, and how many. The end counts when a step lands on it.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| start | INT | yes | First frame number. | 0 to 1000000, default 0 |
| end | INT | yes | Last frame number. A smaller number than start counts down. | 0 to 1000000, default 80 |
| step | INT | yes | Gap between frame numbers. 2 takes every second frame. | 1 to 1000000, default 1 |

Outputs: `STRING`, `INT`, `INT`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | PASS | STRING=str '0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21,...'; INT=int 81; INT=int 80 |
| 2 | start = 1000000 (max) | REJECTED | ValueError: that range has 999921 frames, more than the limit of 100000. Raise step |
| 3 | start = 500000 (mid) | REJECTED | ValueError: that range has 499921 frames, more than the limit of 100000. Raise step |
| 4 | end = 0 (min) | PASS | STRING=str '0'; INT=int 1; INT=int 0 |
| 5 | end = 1000000 (max) | REJECTED | ValueError: that range has 1000001 frames, more than the limit of 100000. Raise step |
| 6 | end = 500000 (mid) | REJECTED | ValueError: that range has 500001 frames, more than the limit of 100000. Raise step |
| 7 | step = 1000000 (max) | PASS | STRING=str '0'; INT=int 1; INT=int 0 |
| 8 | step = 500000 (mid) | PASS | STRING=str '0'; INT=int 1; INT=int 0 |

## Verdict

All 8 cases behaved as expected (4 passed, 4 rejected with a clear message).

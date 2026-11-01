# Frame Range Info SY (`SYFrameRangeInfo`)

Source: `nodes/sy_frame_range_info.py`

**What it does:** Shows which frame numbers a start, end and step pick, and how many. The end counts when a step lands on it. Optional fps gives the length in seconds. Optional frame_rule fits the end so the count is 4n+1 (81 frames and so on) for Wan and LTX style video models. An info line says it all in words.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| start | INT | yes | First frame number. | 0 to 1000000, default 0 |
| end | INT | yes | Last frame number. A smaller number than start counts down. | 0 to 1000000, default 80 |
| step | INT | yes | Gap between frame numbers. 2 takes every second frame. | 1 to 1000000, default 1 |
| fps | FLOAT | no | 0 = off. The frame rate, to also give the length in seconds. | 0.0 to 1000.0, step 1.0, default 0.0 |
| frame_rule | COMBO | no | off keeps the end. 4n+1 trim/extend moves the end so the count is 4n+1. | one of: off, 4n+1 trim, 4n+1 extend |

Outputs: `STRING`, `INT`, `INT`, `FLOAT`, `STRING`

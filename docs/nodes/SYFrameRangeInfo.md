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

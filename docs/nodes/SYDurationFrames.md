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

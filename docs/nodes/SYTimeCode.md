# Time Code SY (`SYTimeCode`)

Source: `nodes/sy_time_code.py`

**What it does:** Turns a frame number into a time code like 00:00:03:12, or reads a time code back into a frame number. The info line says both in one plain sentence. No drop frame: every second has the whole number of frames.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| mode | COMBO | yes | Which way to convert. | one of: frame_to_timecode, timecode_to_frame |
| frame | INT | yes | Frame number. Used when mode is frame_to_timecode. | 0 to 100000000, default 0 |
| fps | FLOAT | yes | Frames per second. | 1.0 to 1000.0, step 0.01, default 24.0 |
| timecode | STRING | yes | Time code as HH:MM:SS:FF. Used when mode is timecode_to_frame. | default '00:00:00:00' |

Outputs: `STRING`, `FLOAT`, `INT`, `STRING`

## How to use

1. Pick mode: frame_to_timecode or timecode_to_frame.
2. Set fps. For the first mode set frame, for the second type the timecode as HH:MM:SS:FF.
3. Outputs: timecode, seconds, frame and an info sentence. There is no drop frame: every second has the same number of frames.

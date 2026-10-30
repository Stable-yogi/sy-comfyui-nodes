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

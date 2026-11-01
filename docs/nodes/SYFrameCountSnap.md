# Frame Count Snap SY (`SYFrameCountSnap`)

Source: `nodes/sy_frame_count_snap.py`

**What it does:** Rounds a wanted frame count to a multiple of a step, then can add one frame. Example: 80 with step 4 gives 81. A max_frames cap keeps the clip small enough for your memory, and the seconds output shows the real length.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| wanted_frames | INT | yes | The number of frames you would like. | 1 to 100000, default 80 |
| step | INT | yes | The result is a multiple of this number. | 1 to 1024, default 4 |
| mode | COMBO | yes | nearest picks the closest multiple, down rounds lower, up rounds higher. | one of: nearest, down, up |
| plus_one | BOOLEAN | yes | Add one extra frame after snapping (for example 80 becomes 81). | default True |
| max_frames | INT | no | Safety cap against running out of memory. 0 is off. Example: 121. | 0 to 100000, default 0 |
| fps | FLOAT | no | Only used for the seconds output: frames divided by fps. | 0.01 to 1000.0, step 0.01, default 24.0 |

Outputs: `INT`, `STRING`, `FLOAT`

## How to use

1. Set wanted_frames and step, for example 80 and 4.
2. Pick mode: nearest, down or up. plus_one adds one frame (80 with step 4 gives 81).
3. max_frames caps the clip (0 = no cap). Set fps to see the real length.
4. Outputs: frames, info and seconds.

# Frame Count Snap SY (`SYFrameCountSnap`)

Source: `nodes/sy_frame_count_snap.py`

**What it does:** Rounds a wanted frame count to a multiple of a step, then can add one frame. Example: 80 with step 4 gives 81.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| wanted_frames | INT | yes | The number of frames you would like. | 1 to 100000, default 80 |
| step | INT | yes | The result is a multiple of this number. | 1 to 1024, default 4 |
| mode | COMBO | yes | nearest picks the closest multiple, down rounds lower, up rounds higher. | one of: nearest, down, up |
| plus_one | BOOLEAN | yes | Add one extra frame after snapping (for example 80 becomes 81). | default True |

Outputs: `INT`, `STRING`

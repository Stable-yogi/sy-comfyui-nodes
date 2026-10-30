# Video Frames Calc SY (`SYVideoFramesCalc`)

Source: `nodes/sy_video_frames_calc.py`

**What it does:** Turns seconds and frames per second into a frame count. Switch on 4n+1 to land on 1, 5, 9, 13 ... frames, which many video models need.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| seconds | FLOAT | yes | How long the clip should be, in seconds. | 0.01 to 100000.0, step 0.1, default 5.0 |
| fps | FLOAT | yes | Frames per second of the clip. | 0.1 to 1000.0, step 1.0, default 16.0 |
| four_n_plus_one | BOOLEAN | yes | On makes the frame count 4n+1 (like 81). Off keeps the plain count. | default True |

Outputs: `INT`, `FLOAT`, `FLOAT`

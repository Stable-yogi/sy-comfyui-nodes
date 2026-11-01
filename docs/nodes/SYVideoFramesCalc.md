# Video Frames Calc SY (`SYVideoFramesCalc`)

Source: `nodes/sy_video_frames_calc.py`

**What it does:** Turns seconds and frames per second into a frame count. Switch on 4n+1 to land on 1, 5, 9, 13 ... frames, which many video models need. Pick the step (8 for LTX) and whether to round to the nearest, round up so the clip is never shorter, or round down. The info output shows what was asked and the real length.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| seconds | FLOAT | yes | How long the clip should be, in seconds. | 0.01 to 100000.0, step 0.1, default 5.0 |
| fps | FLOAT | yes | Frames per second of the clip. | 0.1 to 1000.0, step 1.0, default 16.0 |
| four_n_plus_one | BOOLEAN | yes | On makes the frame count 4n+1 (like 81). Off keeps the plain count. | default True |
| frame_step | INT | no | The n in the Kn+1 rule: 4 for Wan and most models, 8 for LTX. Only used when the switch is on. | 1 to 64, default 4 |
| rounding | COMBO | no | nearest: closest valid count. up: never shorter than asked. down: never longer. | one of: nearest, up, down |

Outputs: `INT`, `FLOAT`, `FLOAT`, `STRING`

## How to use

1. Set seconds and fps.
2. Leave four_n_plus_one on to get a count such as 81. Set frame_step (4 for most models, 8 for LTX).
3. Pick rounding: nearest, up (never shorter) or down (never longer).
4. Outputs: frames, fps, seconds and an info line.

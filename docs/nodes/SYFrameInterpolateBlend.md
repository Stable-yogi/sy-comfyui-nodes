# Frame Interpolate Blend SY (`SYFrameInterpolateBlend`)

Source: `nodes/sy_frame_interpolate_blend.py`

**What it does:** Inserts cross-fade frames between neighbouring frames. This is a plain blend, not motion interpolation, so fast motion looks ghosted. Enter your fps to get the new frame rate that keeps the same speed.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| images | IMAGE | yes | The frames to add blend frames to. Needs at least 2. | picture batch [B,H,W,3] |
| between | INT | yes | How many blend frames to insert between each pair of frames. | 1 to 32, default 1 |
| loop | BOOLEAN | yes | Also blend from the last frame back to the first, for a looping clip. | default False |
| fps | FLOAT | no | Frame rate of the original clip, for example 16. 0 means unknown. | 0.0 to 1000.0, step 0.1, default 0.0 |

Outputs: `IMAGE`, `INT`, `FLOAT`, `STRING`

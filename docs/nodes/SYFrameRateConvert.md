# Frame Rate Convert SY (`SYFrameRateConvert`)

Source: `nodes/sy_frame_rate_convert.py`

**What it does:** Changes the frame rate of a clip, keeping its length. It drops or repeats the nearest frames, no blending.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| images | IMAGE | yes | The frames of the clip. | picture batch [B,H,W,3] |
| source_fps | FLOAT | yes | The frame rate the clip has now. | 0.1 to 1000.0, step 1.0, default 24.0 |
| target_fps | FLOAT | yes | The frame rate you want. | 0.1 to 1000.0, step 1.0, default 16.0 |

Outputs: `IMAGE`, `INT`, `FLOAT`

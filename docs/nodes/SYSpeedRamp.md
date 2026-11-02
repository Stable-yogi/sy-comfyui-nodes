# Speed Ramp SY (`SYSpeedRamp`)

Source: `nodes/sy_speed_ramp.py`

**What it does:** Changes how fast a clip plays over time, for example slow motion that speeds up. It picks frames along a speed curve and can mix the two nearest frames for smooth motion.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| images | IMAGE | yes | The clip as a batch of frames. It needs at least 2 frames. | picture batch [B,H,W,3] |
| start_speed | FLOAT | yes | Playback speed at the start. 1 is normal, 0.5 is half speed. | 0.1 to 8.0, step 0.05, default 1.0 |
| end_speed | FLOAT | yes | Playback speed at the end. 2 is twice as fast. | 0.1 to 8.0, step 0.05, default 2.0 |
| curve | COMBO | yes | How the speed moves from the start value to the end value. | one of: linear, ease in, ease out, ease in out |
| blend | BOOLEAN | yes | On: mix the two nearest frames. Off: take the nearest single frame. | default True |

Outputs: `IMAGE`, `STRING`

## How to use

1. Connect a clip (at least 2 frames) to **images**.
2. Set **start_speed** and **end_speed**, for example 0.5 and 2.0 for slow motion that speeds up. 1 is normal speed.
3. Pick **curve** for how the speed moves: linear, ease in, ease out or ease in out.
4. Leave **blend** on to mix the two nearest frames for smooth motion, or turn it off to take single frames.
5. The second output **info** is a short text report.

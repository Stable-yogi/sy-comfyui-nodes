# Deflicker SY (`SYDeflicker`)

Source: `nodes/sy_deflicker.py`

**What it does:** Evens out brightness jumps between frames. Each frame is pulled toward the smoothed average brightness of its neighbours.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| images | IMAGE | yes | The clip as a batch of frames. | picture batch [B,H,W,3] |
| window | INT | yes | Frames on each side used for the smooth average. 1 changes nothing. | 1 to 31, default 5 |
| strength | FLOAT | yes | How far to move toward the smooth value. 0 changes nothing. | 0.0 to 1.0, step 0.05, default 1.0 |
| keep_colour | BOOLEAN | yes | On: all colours change by the same factor. Off: each colour is evened out alone. | default True |

Outputs: `IMAGE`, `STRING`

## How to use

1. Connect a clip (a batch of frames) to **images**.
2. Set **window** to how many frames on each side are averaged, for example 5. A value of 1 changes nothing.
3. Set **strength** to how far each frame moves toward the smooth value. 1.0 is full, 0.5 is half.
4. Leave **keep_colour** on to change all colours by the same factor, or turn it off to even out each colour alone.
5. The second output **info** is a short text report.

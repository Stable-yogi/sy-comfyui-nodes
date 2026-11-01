# H3 Length SY (`SYH3Length`)

Source: `nodes/sy_h3_length.py`

**What it does:** Turns seconds into a frame count the video model accepts. The model only takes 5, 22, 39, 56 ... frames (17 times a whole number, plus 5). 124 frames is about 5 seconds at 24 per second.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| seconds | FLOAT | yes | How long the clip should be. | 0.1 to 150.0, step 0.1, default 5.0 |
| fps | INT | yes | Frames per second. The video model makes 24. | 1 to 120, default 24 |
| rounding | COMBO | yes | up keeps the whole time you asked for. nearest and down can make the clip a little shorter. | one of: up, nearest, down |

Outputs: `INT`, `FLOAT`, `STRING`

## How to use

1. Set seconds and fps (the video model makes 24).
2. Pick rounding. up keeps the whole time you asked for; nearest and down can make the clip a little shorter.
3. The node gives a frame count the model accepts (5, 22, 39, 56 and so on), plus a decimal value and an info line.
4. Example: 5 seconds at 24 fps gives 124 frames.

# Zoom Punch SY (`SYZoomPunch`)

Source: `nodes/sy_zoom_punch.py`

**What it does:** A quick pulse zoom on the frames you choose, for beats and hits. The zoom jumps in on the chosen frame and eases back out. Frames without a hit stay as they are.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| images | IMAGE | yes | The frames of the clip, in order. | picture batch [B,H,W,3] |
| frames | STRING | yes | Frame numbers to punch on, counted from 0, like 12, 30, 48. Empty means none. | default '' |
| strength | FLOAT | yes | Extra zoom at the peak. 0.15 means 15 percent bigger on the hit frame. | 0.0 to 1.0, step 0.01, default 0.15 |
| length | INT | yes | How many frames the zoom takes to ease back to normal. | 2 to 60, default 8 |
| centre_x | FLOAT | yes | Horizontal point the zoom grows from. 0 is the left edge, 1 the right. | 0.0 to 1.0, step 0.01, default 0.5 |
| centre_y | FLOAT | yes | Vertical point the zoom grows from. 0 is the top edge, 1 the bottom. | 0.0 to 1.0, step 0.01, default 0.5 |

Outputs: `IMAGE`

## How to use

1. Connect the clip frames, in order, to **images**.
2. Type the beat or hit frame numbers into **frames**, separated by commas. A number outside the clip stops the node with a message.
3. Set **strength** for how hard the punch is and **length** for how long it takes to settle.
4. Move **centre_x** and **centre_y** to punch toward a point other than the middle.
5. Use the output **IMAGE** as the finished clip.
